# -*- coding: utf-8 -*-
"""单张生成（终案配置），供外部 nvidia-smi 轮询采样。"""
import os
os.environ.setdefault('PYTORCH_CUDA_ALLOC_CONF', 'expandable_segments:True')
import time
import torch
from diffusers import StableDiffusionXLPipeline

CKPT = r'D:\ComfyUI\models\checkpoints\sd_xl_base_1.0.safetensors'
PROMPT = ('woodcut engraving, medieval occult manuscript illustration, sepia ink and dark crimson '
          'on aged parchment, heavy cross-hatching, rough hand-carved lines, '
          'a lone diver in a brass helmet descending into the abyss, lantern light, '
          'centered symmetrical composition, dark vignette edges, no text, no letters, no watermark')
NEG = ('photograph, 3d render, cgi, smooth gradient, airbrush, anime, manga, cartoon, colorful, '
       'saturated, neon, modern design, flat vector, ui element, text, watermark, signature, '
       'blurry, lowres, jpeg artifacts')

pipe = StableDiffusionXLPipeline.from_single_file(CKPT, torch_dtype=torch.float16,
                                                  use_safetensors=True, add_watermarker=False)
pipe = pipe.to('cuda')
embeds = pipe.encode_prompt(prompt=PROMPT, negative_prompt=NEG, device='cuda',
                            num_images_per_prompt=1, do_classifier_free_guidance=True)
pipe.text_encoder = None; pipe.text_encoder_2 = None; pipe.tokenizer = None; pipe.tokenizer_2 = None
import gc; gc.collect(); torch.cuda.empty_cache()
pipe.vae.enable_slicing(); pipe.vae.enable_tiling()
torch.cuda.empty_cache(); torch.cuda.reset_peak_memory_stats()
print('READY', flush=True)
t0 = time.time()
img = pipe(prompt_embeds=embeds[0], negative_prompt_embeds=embeds[1],
           pooled_prompt_embeds=embeds[2], negative_pooled_prompt_embeds=embeds[3],
           width=640, height=936, num_inference_steps=20, guidance_scale=6.0,
           generator=torch.Generator(device='cpu').manual_seed(7)).images[0]
print('GEN %.1fs  peak %.2fGB' % (time.time() - t0, torch.cuda.max_memory_allocated() / 1024 ** 3), flush=True)
img.save(r'C:\Users\Administrator\Desktop\杂七杂八\红渊\game\tools\art_test\t80_poll_sample.png')
print('DONE', flush=True)
