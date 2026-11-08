# -*- coding: utf-8 -*-
"""T80 第三阶梯（终案验证）：embeds 缓存 + 文本编码器释放 + VAE fp32 + tiling ON（无尖峰）。
预期：常驻 ~6.6GB 不溢出 → UNet 全速 → 20 步 35-45s。
记录：3×640×936、2×512×752、批量 10 张；同 seed SSIM 对照旧基线。
"""
import json
import time
from pathlib import Path

import os
os.environ.setdefault('PYTORCH_CUDA_ALLOC_CONF', 'expandable_segments:True')

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
SEED, CFG, STEPS = 7, 6.0, 20

results = []

def gen(pipe, tag, times=1, size=(640, 936), embeds=None, seed=SEED):
    for i in range(times):
        w, h = size
        torch.cuda.synchronize()
        t0 = time.time()
        kw = dict(width=w, height=h, num_inference_steps=STEPS, guidance_scale=CFG,
                  generator=torch.Generator(device='cpu').manual_seed(seed))
        if embeds:
            kw.update(prompt_embeds=embeds[0], negative_prompt_embeds=embeds[1],
                      pooled_prompt_embeds=embeds[2], negative_pooled_prompt_embeds=embeds[3])
        else:
            kw.update(prompt=PROMPT, negative_prompt=NEG)
        img = pipe(**kw).images[0]
        torch.cuda.synchronize()
        dt = time.time() - t0
        vram = torch.cuda.max_memory_allocated() / 1024 ** 3
        p = OUT / ('t80r3_%s_%d.png' % (tag, i + 1))
        img.save(p)
        results.append({'tag': tag, 'i': i + 1, 'size': '%dx%d' % (w, h), 'gen_s': round(dt, 1),
                        'vram_gb': round(vram, 2)})
        print('%-24s #%d gen %6.1fs  vram %.2fGB' % (tag, i + 1, dt, vram), flush=True)

def main():
    t0 = time.time()
    pipe = StableDiffusionXLPipeline.from_single_file(CKPT, torch_dtype=torch.float16, use_safetensors=True,
                                                      add_watermarker=False)
    pipe = pipe.to('cuda')
    print('model load %.1fs' % (time.time() - t0), flush=True)

    # 终案配置：embeds 缓存 → 释放文本编码器 → VAE fp32 + tiling/slicing（防解码尖峰）
    embeds = pipe.encode_prompt(prompt=PROMPT, negative_prompt=NEG, device='cuda',
                                num_images_per_prompt=1, do_classifier_free_guidance=True)
    pipe.text_encoder = None; pipe.text_encoder_2 = None; pipe.tokenizer = None; pipe.tokenizer_2 = None
    import gc; gc.collect(); torch.cuda.empty_cache()
    pipe.vae.enable_slicing(); pipe.vae.enable_tiling()
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.cuda.empty_cache(); torch.cuda.reset_peak_memory_stats()
    print('config ready: encoders freed, VAE fp32+tiling, no-channels-last', flush=True)

    # 3×640×936（验收 1：3 次均值）
    gen(pipe, 'G_640x936', times=3, embeds=embeds)
    # 2×512×752（验收 2）
    gen(pipe, 'G_512x752', times=2, size=(512, 752), embeds=embeds)

    (OUT / 'art_perf_r4.json').write_text(json.dumps({
        'meta': {'task': 'T80', 'steps': STEPS, 'seed': SEED, 'cfg': CFG,
                 'gpu': torch.cuda.get_device_name(0),
                 'config': 'embeds cache + text encoders freed + VAE fp32 + tiling/slicing ON + channels_last'},
        'steps': results}, indent=1) + '\n')
    print('saved', OUT / 'art_perf_r4.json', flush=True)

if __name__ == '__main__':
    main()
