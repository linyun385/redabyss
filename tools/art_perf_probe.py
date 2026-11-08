# -*- coding: utf-8 -*-
"""T80 提速阶梯探针：加载一次 SDXL，按优先级逐个套改动，记录每步 gen 耗时/显存/图。
输出 tools/art_perf_steps.json（每种改法的单独耗时对比）+ 每步一张图（供 SSIM 对照）。
用法：python tools/art_perf_probe.py [--steps 20]
"""
import argparse
import json
import time
from pathlib import Path

import torch
from diffusers import StableDiffusionXLPipeline

CKPT = r'D:\ComfyUI\models\checkpoints\sd_xl_base_1.0.safetensors'
OUT = Path(__file__).parent
STYLE_PREFIX = ('woodcut engraving, medieval occult manuscript illustration, '
                'sepia ink and dark crimson on aged parchment, '
                'heavy cross-hatching, rough hand-carved lines, ')
STYLE_SUFFIX = (', centered symmetrical composition, dark vignette edges, '
                'no text, no letters, no watermark')
STYLE_NEG = ('photograph, 3d render, cgi, smooth gradient, airbrush, anime, manga, '
             'cartoon, colorful, saturated, neon, modern design, flat vector, '
             'ui element, text, watermark, signature, blurry, lowres, jpeg artifacts')
PROMPT = STYLE_PREFIX + 'a lone diver in a brass helmet descending into the abyss, lantern light' + STYLE_SUFFIX
NEG = STYLE_NEG
W, H, SEED, CFG = 640, 936, 7, 6.0

ap = argparse.ArgumentParser()
ap.add_argument('--steps', type=int, default=20)
a = ap.parse_args()
STEPS = a.steps

results = []

def gen(pipe, tag, embeds=None):
    gen = torch.Generator(device='cpu').manual_seed(SEED)
    torch.cuda.synchronize()
    t0 = time.time()
    kw = dict(prompt=PROMPT, negative_prompt=NEG, width=W, height=H,
              num_inference_steps=STEPS, guidance_scale=CFG, generator=gen)
    if embeds:
        kw['prompt_embeds'] = embeds[0]
        kw['negative_prompt_embeds'] = embeds[1]
        kw['pooled_prompt_embeds'] = embeds[2]
        kw['negative_pooled_prompt_embeds'] = embeds[3]
        del kw['prompt'], kw['negative_prompt']
    img = pipe(**kw).images[0]
    torch.cuda.synchronize()
    dt = time.time() - t0
    vram = torch.cuda.max_memory_allocated() / 1024 ** 3
    p = OUT / ('t80_step_%s.png' % tag)
    img.save(p)
    results.append({'tag': tag, 'gen_s': round(dt, 1), 'vram_gb': round(vram, 2)})
    print('%-28s gen %6.1fs  vram %.2fGB' % (tag, dt, vram), flush=True)
    return img

def main():
    t0 = time.time()
    pipe = StableDiffusionXLPipeline.from_single_file(CKPT, torch_dtype=torch.float16, use_safetensors=True,
                                                      add_watermarker=False)
    pipe = pipe.to('cuda')
    print('model load %.1fs' % (time.time() - t0), flush=True)

    st = pipe.vae.config.force_upcast
    print('vae force_upcast =', st, '| slicing =', pipe.vae.use_slicing, '| tiling =', pipe.vae.use_tiling, flush=True)

    # C0 现状基线：fp32 upcast VAE + slicing + tiling（与 gen_art_diffusers.py 旧配置一致）
    pipe.vae.enable_slicing(); pipe.vae.enable_tiling()
    torch.cuda.reset_peak_memory_stats()
    gen(pipe, 'C0_baseline_fp32vae_tiling')

    # C1 只关 tiling/slicing（VAE 仍 fp32）——隔离「瓦片解码」的代价
    pipe.vae.disable_slicing(); pipe.vae.disable_tiling()
    torch.cuda.empty_cache(); torch.cuda.reset_peak_memory_stats()
    gen(pipe, 'C1_no_tiling')

    # C2 VAE fp16 + force_upcast=False（任务优先级 1；警惕原版 VAE fp16 NaN → SSIM 检查兜底）
    pipe.vae.config.force_upcast = False
    pipe.vae = pipe.vae.to(torch.float16)
    torch.cuda.empty_cache(); torch.cuda.reset_peak_memory_stats()
    img_c2 = gen(pipe, 'C2_vae_fp16')

    # C3 cudnn.benchmark + float32_matmul_precision('high')
    torch.backends.cudnn.benchmark = True
    torch.set_float32_matmul_precision('high')
    torch.cuda.empty_cache(); torch.cuda.reset_peak_memory_stats()
    gen(pipe, 'C3_cudnn_matmul')

    # C4 prompt_embeds 缓存（同 prompt 第二次起直接吃缓存）
    torch.cuda.empty_cache(); torch.cuda.reset_peak_memory_stats()
    te = time.time()
    embeds = pipe.encode_prompt(prompt=PROMPT, negative_prompt=NEG, device='cuda',
                                num_images_per_prompt=1, do_classifier_free_guidance=True)
    te_s = time.time() - te
    print('  encode_prompt %.2fs（批量缓存后每张省这笔）' % te_s, flush=True)
    gen(pipe, 'C4_cached_embeds', embeds=embeds)
    results[-1]['encode_s'] = round(te_s, 2)

    (OUT / 'art_perf_steps.json').write_text(json.dumps({
        'meta': {'task': 'T80', 'steps': STEPS, 'size': '%dx%d' % (W, H), 'seed': SEED, 'cfg': CFG,
                 'gpu': torch.cuda.get_device_name(0), 'torch': torch.__version__,
                 'diffusers': __import__('diffusers').__version__},
        'steps': results}, indent=1) + '\n')
    print('saved', OUT / 'art_perf_steps.json', flush=True)

if __name__ == '__main__':
    main()
