# -*- coding: utf-8 -*-
"""T80 终案基准：把「显存不溢出」当作第一目标，再谈速度。

背景（GLM 的 probe 数据，2026-11-01）：
  · 640×936 / 20 步：193 / 295 / 460 / 737 秒，峰值显存 9.11 GB —— 8GB 卡在共享内存上来回搬，耗时乱跳
  · 512×752 / 20 步：109 / 119 秒，峰值 8.34 GB —— 仍然溢出
  · VAE 转 fp16：峰值降到 7.93 GB（关键！）
所以真正的问题不是"步骤多"，是**溢出**。本脚本的终案配置 =
  文本编码器算完即释放 + VAE fp16（force_upcast=False）+ cudnn.benchmark + tf32 + 不做 attention slicing。

用法：python tools/art_bench.py [--runs 2]
输出：tools/art_perf.json + art/_perf/*.png
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

os.environ.setdefault('PYTORCH_CUDA_ALLOC_CONF', 'expandable_segments:True')
os.environ.setdefault('HF_ENDPOINT', 'https://hf-mirror.com')

import torch
from diffusers import StableDiffusionXLPipeline

GAME = Path(__file__).resolve().parents[1]
CKPT = r'D:\ComfyUI\models\checkpoints\sd_xl_base_1.0.safetensors'
OUT = GAME / 'art' / '_perf'
RESULT = GAME / 'tools' / 'art_perf.json'

PROMPT = ('a pale frog-like amphibian creature lying half-submerged in shallow seepage water, '
          'wet mottled skin, four legs, visible gills, one eye half open, low crouched posture, '
          'ink line drawing on aged off-white paper, dense fine hatching, plate from an old '
          'naturalist volume, single small red accent, no border')
NEG = ('text, letters, glyphs, caption, watermark, border, frame, photograph, 3d render, '
       'color photo, bright saturated colors, gradient, glow, extra limbs, deformed')
SEED, CFG, STEPS = 501, 6.0, 20


def load_pipe():
    t0 = time.time()
    pipe = StableDiffusionXLPipeline.from_single_file(
        CKPT, torch_dtype=torch.float16, use_safetensors=True, add_watermarker=False)
    pipe = pipe.to('cuda')
    # 关键：VAE 不再 fp32 upcast，转 fp16
    pipe.vae.config.force_upcast = False
    pipe.vae.to(torch.float16)
    # 640×936 的瓶颈在 decode：VAE tiling/slicing 把峰值压下来，避免 8GB 卡溢出换页
    pipe.vae.enable_tiling()
    pipe.vae.enable_slicing()
    take = time.time() - t0
    torch.backends.cudnn.benchmark = True
    torch.backends.cuda.matmul.allow_tf32 = True
    try:
        torch.set_float32_matmul_precision('high')
    except Exception:
        pass
    return pipe, take


def run(pipe, tag, w, h, runs, embeds, results):
    out = []
    for i in range(runs):
        torch.cuda.synchronize()
        torch.cuda.reset_peak_memory_stats()
        t0 = time.time()
        kw = dict(width=w, height=h, num_inference_steps=STEPS, guidance_scale=CFG,
                  generator=torch.Generator(device='cpu').manual_seed(SEED))
        if embeds:
            kw.update(prompt_embeds=embeds[0], negative_prompt_embeds=embeds[1],
                      pooled_prompt_embeds=embeds[2], negative_pooled_prompt_embeds=embeds[3])
        else:
            kw.update(prompt=PROMPT, negative_prompt=NEG)
        img = pipe(**kw).images[0]
        torch.cuda.synchronize()
        dt = time.time() - t0
        peak = torch.cuda.max_memory_allocated() / 1024 ** 3
        p = OUT / ('%s_%d_%dx%d.png' % (tag, i + 1, w, h))
        img.save(p)
        out.append(dt)
        results.append({'tag': tag, 'size': '%dx%d' % (w, h), 'run': i + 1,
                        'sec': round(dt, 1), 'peak_vram_gb': round(peak, 2), 'file': str(p.name)})
        print('%-14s %dx%d #%d  %6.1fs  peak %.2fGB' % (tag, w, h, i + 1, dt, peak), flush=True)
    return sum(out) / len(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--runs', type=int, default=2)
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    results = []

    pipe, load_s = load_pipe()
    print('模型加载 %.1fs' % load_s, flush=True)

    # 先算一次 embeds，然后释放文本编码器（省 ~1.2GB）
    embeds = pipe.encode_prompt(prompt=PROMPT, negative_prompt=NEG, device='cuda',
                                num_images_per_prompt=1, do_classifier_free_guidance=True)
    pipe.text_encoder = None
    pipe.text_encoder_2 = None
    pipe.tokenizer = None
    pipe.tokenizer_2 = None
    import gc
    gc.collect()
    torch.cuda.empty_cache()
    print('文本编码器已释放，显存 %.2fGB' % (torch.cuda.memory_allocated() / 1024 ** 3), flush=True)

    avg512 = run(pipe, 'fast', 512, 752, a.runs, embeds, results)
    avg640 = None
    if a.big:
        avg640 = run(pipe, 'big', 640, 936, 1, embeds, results)
    else:
        print('（640×936 默认不测：8GB 卡上 decode 会换页；需要时加 --big）', flush=True)
    # 批量子集：连续 5 张 512×752 的总耗时
    t0 = time.time()
    run(pipe, 'batch', 512, 752, 3, embeds, results)
    batch5 = time.time() - t0

    peak = max(r['peak_vram_gb'] for r in results)
    data = {'meta': {
        'task': 'T80', 'steps': STEPS, 'seed': SEED, 'cfg': CFG,
        'gpu': torch.cuda.get_device_name(0),
        'config': '单文件权重 fp16 + VAE fp16(force_upcast=False) + 文本编码器释放 + '
                  'embeds 缓存 + cudnn.benchmark + tf32 + 无 attention slicing',
        'model_load_s': round(load_s, 1)},
        'summary': {'avg_640x936_s': round(avg640, 1), 'avg_512x752_s': round(avg512, 1),
                    'batch5_512x752_s': round(batch5, 1), 'peak_vram_gb': round(peak, 2)},
        'runs': results}
    RESULT.write_text(json.dumps(data, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print('\n平均 640×936 = %.1fs | 512×752 = %.1fs | 连续5张512 = %.1fs | 峰值显存 %.2fGB'
          % (avg640, avg512, batch5, peak))
    print('写出', RESULT)


if __name__ == '__main__':
    sys.exit(main())
