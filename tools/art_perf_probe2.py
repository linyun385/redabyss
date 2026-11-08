# -*- coding: utf-8 -*-
"""T80 第二阶梯：真凶是显存溢出（8.88GB > 8GB 物理 → 共享内存爬行）。
方案：encode_prompt 缓存后【释放文本编码器】（省 ~1.4GB）+ VAE 保持 fp32（fp16 全黑已证伪）+
     不开 tiling/slicing + expandable_segments。目标：常驻 < 8GB → UNet 不再爬行。
同时用 pynvml 记录 GPU 温度/频率（笔记本持续负载降频会污染计时）。
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
W, H, SEED, CFG, STEPS = 640, 936, 7, 6.0, 20

results = []
try:
    import pynvml
    pynvml.nvmlInit()
    HND = pynvml.nvmlDeviceGetHandleByIndex(0)
    def gpu_state():
        t = pynvml.nvmlDeviceGetTemperature(HND, pynvml.NVML_TEMPERATURE_GPU)
        sm = pynvml.nvmlDeviceGetClockInfo(pynvml.NVML_CLOCK_SM)
        return {'temp_c': t, 'sm_mhz': sm}
except Exception:
    def gpu_state():
        return {}

def gen(pipe, tag, times=1, size=(W, H), embeds=None):
    gen = torch.Generator(device='cpu').manual_seed(SEED)
    w, h = size
    for i in range(times):
        torch.cuda.synchronize()
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
        vram = torch.cuda.max_memory_allocated() / 1024 ** 3
        p = OUT / ('t80r2_%s_%d.png' % (tag, i + 1))
        img.save(p)
        results.append({'tag': tag, 'i': i + 1, 'size': '%dx%d' % (w, h), 'gen_s': round(dt, 1),
                        'vram_gb': round(vram, 2), **gpu_state()})
        print('%-26s #%d gen %6.1fs  vram %.2fGB  %s' % (tag, i + 1, dt, vram, gpu_state()), flush=True)

def main():
    t0 = time.time()
    pipe = StableDiffusionXLPipeline.from_single_file(CKPT, torch_dtype=torch.float16, use_safetensors=True,
                                                      add_watermarker=False)
    pipe = pipe.to('cuda')
    print('model load %.1fs' % (time.time() - t0), flush=True)
    torch.backends.cuda.matmul.allow_tf32 = True

    # 1) 先编码（缓存 embeds），然后释放两个文本编码器（省 ~1.4GB）
    embeds = pipe.encode_prompt(prompt=PROMPT, negative_prompt=NEG, device='cuda',
                                num_images_per_prompt=1, do_classifier_free_guidance=True)
    import gc
    pipe.text_encoder = None; pipe.text_encoder_2 = None; pipe.tokenizer = None; pipe.tokenizer_2 = None
    gc.collect(); torch.cuda.empty_cache()
    free_gb = torch.cuda.mem_get_info()[0] / 1024 ** 3
    print('text encoders freed; free vram %.2fGB' % free_gb, flush=True)

    # 2) VAE：保持 fp32（fp16 全黑已证伪），关 tiling/slicing
    pipe.vae.disable_slicing(); pipe.vae.disable_tiling()

    torch.cuda.empty_cache(); torch.cuda.reset_peak_memory_stats()
    gen(pipe, 'R2_freed_encoders_fp32vae', times=3, embeds=embeds)

    # 3) 512×752 档
    torch.cuda.empty_cache(); torch.cuda.reset_peak_memory_stats()
    gen(pipe, 'R2_512x752', times=2, size=(512, 752), embeds=embeds)

    (OUT / 'art_perf_r2.json').write_text(json.dumps({
        'meta': {'task': 'T80', 'steps': STEPS, 'seed': SEED, 'cfg': CFG,
                 'gpu': torch.cuda.get_device_name(0),
                 'config': 'embeds cached + text encoders freed + VAE fp32 no-tiling + expandable_segments + tf32 matmul'},
        'steps': results}, indent=1) + '\n')
    print('saved', OUT / 'art_perf_r2.json', flush=True)

if __name__ == '__main__':
    main()
