# -*- coding: utf-8 -*-
"""定位瓶颈：把「采样」和「VAE 解码」分开计时。

之前整张 512×752 要 560–655 秒，但 20 步采样本身只要 ~55 秒，
差的那 500 秒到底花在哪，必须量出来，不能再靠猜。
"""
import os
import sys
import time

os.environ.setdefault('HF_ENDPOINT', 'https://hf-mirror.com')
import torch
from diffusers import StableDiffusionXLPipeline, AutoencoderKL

CKPT = r'D:\ComfyUI\models\checkpoints\sd_xl_base_1.0.safetensors'
VAE = r'C:\Users\Administrator\Desktop\杂七杂八\红渊\game\models\sdxl-vae-fp16-fix.safetensors'
PROMPT = ('a pale frog-like amphibian creature, wet mottled skin, four legs, visible gills, '
          'ink line drawing on aged off-white paper, dense fine hatching, single small red accent')

pipe = StableDiffusionXLPipeline.from_single_file(
    CKPT, torch_dtype=torch.float16, use_safetensors=True, add_watermarker=False).to('cuda')

# A) 原装 VAE（fp32 upcast）
pipe.vae.config.force_upcast = True
torch.cuda.synchronize(); t = time.time()
lat = pipe(prompt=PROMPT, width=512, height=752, num_inference_steps=20,
           guidance_scale=6.0, output_type='latent',
           generator=torch.Generator(device='cpu').manual_seed(501)).images
torch.cuda.synchronize(); t_s1 = time.time() - t

t = time.time()
img1 = pipe.vae.decode(lat / pipe.vae.config.scaling_factor, return_dict=False)[0]
torch.cuda.synchronize(); t_d1 = time.time() - t

# B) 换 fp16-fix VAE（fp16，搬到 cuda）
vae = AutoencoderKL.from_single_file(VAE, torch_dtype=torch.float16).to('cuda')
vae.config.force_upcast = False
pipe.vae = vae
t = time.time()
img2 = pipe.vae.decode(lat / pipe.vae.config.scaling_factor, return_dict=False)[0]
torch.cuda.synchronize(); t_d2 = time.time() - t

print('\n采样(20步) %.1fs | 原装VAE解码 %.1fs | fp16-fix VAE解码 %.1fs' % (t_s1, t_d1, t_d2))
print('显存峰值 %.2fGB' % (torch.cuda.max_memory_allocated() / 1024 ** 3))
