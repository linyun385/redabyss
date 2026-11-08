# -*- coding: utf-8 -*-
"""T80 终测（修正版）：VAE 必须留 fp32。

结论先说：
  · VAE 转 fp16 会**输出全黑图**（实测 640_fp16vae.png / fast_2_512x752.png 都是 mean=0 std=0），
    所以 fp16 VAE 这条路**不可用**，GLM 之前测到的"fp16 更快"是黑图换来的假速度。
  · 正确的省显存方式是：**文本编码器算完即释放** + **VAE tiling/slicing**，VAE 保持 fp32。
本脚本只测这条正确路径：512×752 ×2、640×936 ×1，并检查图像非黑（std>3）。
"""
import json
import os
import sys
import time
from pathlib import Path

os.environ.setdefault('HF_ENDPOINT', 'https://hf-mirror.com')

import numpy as np
import torch
from diffusers import StableDiffusionXLPipeline
from PIL import Image

GAME = Path(__file__).resolve().parents[1]
CKPT = r'D:\ComfyUI\models\checkpoints\sd_xl_base_1.0.safetensors'
OUT = GAME / 'art' / '_perf'
RES = GAME / 'tools' / 'art_perf_final.json'

PROMPT = ('a pale frog-like amphibian creature lying half-submerged in shallow seepage water, '
          'wet mottled skin, four legs, visible gills, one eye half open, low crouched posture, '
          'ink line drawing on aged off-white paper, dense fine hatching, plate from an old '
          'naturalist volume, single small red accent, no border')
NEG = ('text, letters, glyphs, caption, watermark, border, frame, photograph, 3d render, '
       'color photo, bright saturated colors, gradient, glow, extra limbs, deformed')
SEED, CFG, STEPS = 501, 6.0, 20


def gen(pipe, w, h, name, embeds, rows):
    torch.cuda.synchronize()
    torch.cuda.reset_peak_memory_stats()
    t0 = time.time()
    img = pipe(width=w, height=h, num_inference_steps=STEPS, guidance_scale=CFG,
               generator=torch.Generator(device='cpu').manual_seed(SEED),
               prompt_embeds=embeds[0], negative_prompt_embeds=embeds[1],
               pooled_prompt_embeds=embeds[2], negative_pooled_prompt_embeds=embeds[3]).images[0]
    torch.cuda.synchronize()
    dt = time.time() - t0
    peak = torch.cuda.max_memory_allocated() / 1024 ** 3
    p = OUT / name
    img.save(p)
    a = np.asarray(img.convert('L'), dtype='float32')
    ok = a.std() > 3
    rows.append({'file': name, 'size': '%dx%d' % (w, h), 'sec': round(dt, 1),
                 'peak_gb': round(peak, 2), 'std': round(float(a.std()), 1), 'ok': bool(ok)})
    print('%-22s %6.1fs  peak %.2fGB  std %5.1f  %s'
          % (name, dt, peak, a.std(), '正常' if ok else '!! 黑图'), flush=True)
    return dt


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    pipe = StableDiffusionXLPipeline.from_single_file(
        CKPT, torch_dtype=torch.float16, use_safetensors=True, add_watermarker=False).to('cuda')
    load_s = time.time() - t0
    torch.backends.cudnn.benchmark = True
    torch.backends.cuda.matmul.allow_tf32 = True
    # VAE 保持 fp32（fp16 会黑图）；用 tiling/slicing 控显存
    pipe.vae.config.force_upcast = True
    pipe.vae.to(torch.float32)
    pipe.vae.enable_tiling()
    pipe.vae.enable_slicing()

    embeds = pipe.encode_prompt(prompt=PROMPT, negative_prompt=NEG, device='cuda',
                                num_images_per_prompt=1, do_classifier_free_guidance=True)
    pipe.text_encoder = None
    pipe.text_encoder_2 = None
    pipe.tokenizer = None
    pipe.tokenizer_2 = None
    import gc
    gc.collect()
    torch.cuda.empty_cache()
    print('模型加载 %.1fs，编码器已释放，显存 %.2fGB' %
          (load_s, torch.cuda.memory_allocated() / 1024 ** 3), flush=True)

    rows = []
    gen(pipe, 512, 752, 'final_512_1.png', embeds, rows)   # 首张含预热
    d512 = gen(pipe, 512, 752, 'final_512_2.png', embeds, rows)
    d640 = gen(pipe, 640, 936, 'final_640_1.png', embeds, rows)

    data = {'meta': {'steps': STEPS, 'seed': SEED, 'cfg': CFG,
                     'gpu': torch.cuda.get_device_name(0), 'model_load_s': round(load_s, 1),
                     'config': 'fp16 UNet + fp32 VAE(force_upcast=True) + VAE tiling/slicing + '
                               '文本编码器释放 + cudnn.benchmark + tf32'},
            'summary': {'512x752_steady_s': round(d512, 1), '640x936_s': round(d640, 1),
                        'peak_gb': round(max(r['peak_gb'] for r in rows), 2),
                        'all_images_valid': all(r['ok'] for r in rows)},
            'runs': rows}
    RES.write_text(json.dumps(data, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print('\n512×752 稳态 %.1fs | 640×936 %.1fs | 峰值 %.2fGB | 全部图片有效: %s'
          % (d512, d640, data['summary']['peak_gb'], data['summary']['all_images_valid']))
    print('写出', RES)


if __name__ == '__main__':
    sys.exit(main())
