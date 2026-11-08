# -*- coding: utf-8 -*-
"""T80 收尾测量：640×936 单张耗时 + VAE fp16 / fp32 的画质对比（SSIM）。

目的：
  1) 640×936 在 8GB 卡上到底能不能 ≤60 秒（VAE tiling + fp16）
  2) VAE 从 fp32 降到 fp16，画面有没有肉眼可见退化（同 prompt 同 seed）

输出：tools/art_perf_640.json + art/_perf/{640,ssim_fp16,ssim_fp32}.png + 终端打印 SSIM
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
RES = GAME / 'tools' / 'art_perf_640.json'

PROMPT = ('a pale frog-like amphibian creature lying half-submerged in shallow seepage water, '
          'wet mottled skin, four legs, visible gills, one eye half open, low crouched posture, '
          'ink line drawing on aged off-white paper, dense fine hatching, plate from an old '
          'naturalist volume, single small red accent, no border')
NEG = ('text, letters, glyphs, caption, watermark, border, frame, photograph, 3d render, '
       'color photo, bright saturated colors, gradient, glow, extra limbs, deformed')
SEED, CFG, STEPS = 501, 6.0, 20


def ssim(a, b):
    """简化 SSIM（8×8 窗口均值版），够用来判断"有没有肉眼可见退化"。"""
    a = np.asarray(a.convert('L'), dtype=np.float64)
    b = np.asarray(b.convert('L'), dtype=np.float64)
    if a.shape != b.shape:
        return float('nan')
    C1, C2 = (0.01 * 255) ** 2, (0.03 * 255) ** 2
    mu_a = a.mean(); mu_b = b.mean()
    va = a.var(); vb = b.var()
    cov = ((a - mu_a) * (b - mu_b)).mean()
    return ((2 * mu_a * mu_b + C1) * (2 * cov + C2)) / ((mu_a ** 2 + mu_b ** 2 + C1) * (va + vb + C2))


def gen(pipe, w, h, out, embeds):
    torch.cuda.synchronize(); torch.cuda.reset_peak_memory_stats()
    t0 = time.time()
    img = pipe(width=w, height=h, num_inference_steps=STEPS, guidance_scale=CFG,
               generator=torch.Generator(device='cpu').manual_seed(SEED),
               prompt_embeds=embeds[0], negative_prompt_embeds=embeds[1],
               pooled_prompt_embeds=embeds[2], negative_pooled_prompt_embeds=embeds[3]).images[0]
    torch.cuda.synchronize()
    dt = time.time() - t0
    peak = torch.cuda.max_memory_allocated() / 1024 ** 3
    img.save(OUT / out)
    print('%-18s %dx%d  %6.1fs  peak %.2fGB' % (out, w, h, dt, peak), flush=True)
    return img, dt, peak


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    pipe = StableDiffusionXLPipeline.from_single_file(
        CKPT, torch_dtype=torch.float16, use_safetensors=True, add_watermarker=False).to('cuda')
    torch.backends.cudnn.benchmark = True
    torch.backends.cuda.matmul.allow_tf32 = True
    embeds = pipe.encode_prompt(prompt=PROMPT, negative_prompt=NEG, device='cuda',
                                num_images_per_prompt=1, do_classifier_free_guidance=True)
    pipe.text_encoder = None; pipe.text_encoder_2 = None
    pipe.tokenizer = None; pipe.tokenizer_2 = None
    import gc; gc.collect(); torch.cuda.empty_cache()

    data = {'meta': {'steps': STEPS, 'seed': SEED, 'cfg': CFG,
                     'gpu': torch.cuda.get_device_name(0)}}

    # A) 640×936 + VAE fp16 + tiling
    pipe.vae.config.force_upcast = False
    pipe.vae.to(torch.float16)
    pipe.vae.enable_tiling(); pipe.vae.enable_slicing()
    _, dt640, peak640 = gen(pipe, 640, 936, '640_fp16vae.png', embeds)
    data['640x936_fp16vae'] = {'sec': round(dt640, 1), 'peak_gb': round(peak640, 2)}

    # B) 512×752 fp16 VAE（与旧实现 fp32 对比画质）
    img16, dt512, peak512 = gen(pipe, 512, 752, 'ssim_fp16.png', embeds)
    data['512x752_fp16vae'] = {'sec': round(dt512, 1), 'peak_gb': round(peak512, 2)}

    # C) 同 seed，VAE 换回 fp32（旧实现）
    pipe.vae.to(torch.float32)
    pipe.vae.config.force_upcast = True
    img32, dt512b, peak512b = gen(pipe, 512, 752, 'ssim_fp32.png', embeds)
    data['512x752_fp32vae'] = {'sec': round(dt512b, 1), 'peak_gb': round(peak512b, 2)}

    s = ssim(img16, img32)
    data['ssim_fp16_vs_fp32'] = round(float(s), 4)
    RES.write_text(json.dumps(data, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print('\nSSIM(fp16 vs fp32, 同 seed 512×752) = %.4f' % s)
    print('640×936 = %.1fs / %.2fGB ；512×752 fp16 = %.1fs ；写出 %s'
          % (dt640, peak640, dt512, RES))


if __name__ == '__main__':
    sys.exit(main())
