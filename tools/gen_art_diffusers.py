# -*- coding: utf-8 -*-
"""本地生图（diffusers 路线）——绕开 ComfyUI。

为什么不用 ComfyUI（2026-10-30 复盘）：
  D:\\ComfyUI 是 2026-10-29 的 master（commit fd7639f），它的新依赖 comfy-kitchen
  在 torch 2.6 上直接崩：torch.fx 的 infer_schema 不认 C++ 算子的 `list[int]` 参数
  （ValueError: Parameter stride has unsupported type list[int]）。
  要么升级 torch（2.7/2.8，2.5GB+ 下载，且 comfy-kitchen 对版本很挑），
  要么干脆不用 ComfyUI。SDXL 底模已经在盘上（6.46GB），diffusers 单文件就能加载。

用法：
  python tools/gen_art_diffusers.py --prompt "..." --out out.png --width 832 --height 1216
  python tools/gen_art_diffusers.py --prompt "..." --out out.png --seed 7 --steps 25
"""
import argparse
import os
import sys
import time
from pathlib import Path

# 显存够紧的，先开这几个省显存开关（能在 8GB 上跑 832x1216）
os.environ.setdefault('PYTORCH_CUDA_ALLOC_CONF', 'expandable_segments:True')

import torch
from diffusers import StableDiffusionXLPipeline, AutoencoderKL


CKPT_CANDIDATES = [
    r'D:\ComfyUI\models\checkpoints\sd_xl_base_1.0.safetensors',
    r'D:\ComfyUI\models\checkpoints\sdXL_v10.safetensors',
]

STYLE_PREFIX = ('woodcut engraving, medieval occult manuscript illustration, '
                'sepia ink and dark crimson on aged parchment, '
                'heavy cross-hatching, rough hand-carved lines, ')
STYLE_SUFFIX = (', centered symmetrical composition, dark vignette edges, '
                'no text, no letters, no watermark')
STYLE_NEG = ('photograph, 3d render, cgi, smooth gradient, airbrush, anime, manga, '
             'cartoon, colorful, saturated, neon, modern design, flat vector, '
             'ui element, text, watermark, signature, blurry, lowres, jpeg artifacts')


def pick_ckpt(explicit=None):
    if explicit:
        return explicit
    for p in CKPT_CANDIDATES:
        if Path(p).exists():
            return p
    raise SystemExit('找不到 SDXL 底模，检查 D:\\ComfyUI\\models\\checkpoints')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--prompt', required=True, help='对象描述（会自动套 STYLE_ART 的前缀/后缀）')
    ap.add_argument('--out', required=True)
    ap.add_argument('--width', type=int, default=512)
    ap.add_argument('--height', type=int, default=752)
    ap.add_argument('--vae', default=None,
                    help='可选：fp16 安全的 VAE（如 madebyollin/sdxl-vae-fp16-fix 的 safetensors）。'
                         '默认用底模自带 VAE 且保持 fp32——VAE 转 fp16 会输出全黑图（2026-11-01 实测）')
    ap.add_argument('--steps', type=int, default=25)
    ap.add_argument('--cfg', type=float, default=6.0)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--raw', action='store_true', help='不套风格前缀（调试用）')
    ap.add_argument('--ckpt', default=None)
    ap.add_argument('--neg', default=None)
    ap.add_argument('--lora', default=None, help='可选 LoRA（如 SDXL-Lightning 4step），能大幅提速')
    ap.add_argument('--lora-scale', type=float, default=0.7, help='LoRA 强度（风格 LoRA 建议 0.5–0.8，太高会过拟合）')
    ap.add_argument('--vae-tiling', action='store_true',
                    help='给 fp16 VAE 开 tiling/slicing（实测会让 decode 慢 50 倍，非必要别开）')
    ap.add_argument('--attn-slice', action='store_true', help='显存实在不够时才开（会慢很多）')
    a = ap.parse_args()

    ckpt = pick_ckpt(a.ckpt)
    prompt = a.prompt if a.raw else (STYLE_PREFIX + a.prompt + STYLE_SUFFIX)
    neg = a.neg or STYLE_NEG
    gen = torch.Generator(device='cpu').manual_seed(a.seed) if a.seed else None

    t0 = time.time()
    pipe = StableDiffusionXLPipeline.from_single_file(
        ckpt, torch_dtype=torch.float16, use_safetensors=True,
        add_watermarker=False,
    )
    # diffusers 0.42 起 VAE 的省显存开关挪到了 pipe.vae 上（旧版是 pipe.enable_vae_slicing）
    if hasattr(pipe, 'vae') and hasattr(pipe.vae, 'enable_slicing'):
        pipe.vae.enable_slicing()
        pipe.vae.enable_tiling()
    else:
        for fn in ('enable_vae_slicing', 'enable_vae_tiling'):
            if hasattr(pipe, fn):
                getattr(pipe, fn)()
    # 换 fp16 安全的 VAE（可选）：VAE 保持 fp16 才不会黑图
    if a.vae:
        try:
            from diffusers import AutoencoderKL
            pipe.vae = AutoencoderKL.from_single_file(a.vae, torch_dtype=torch.float16)
            pipe.vae.config.force_upcast = False
            # 关键：换进来的 VAE 默认在 CPU 上，必须显式搬到 CUDA，否则解码在 CPU 上跑（实测 500 秒）
            pipe.vae = pipe.vae.to('cuda')
            # 注意：fp16 VAE **不要**开 tiling/slicing —— 实测 512×752 的 decode 会从 ~15s 变成 ~870s
            if a.vae_tiling:
                pipe.vae.enable_slicing()
                pipe.vae.enable_tiling()
            print('vae swapped ->', a.vae)
        except Exception as e:
            print('!! 换 VAE 失败，继续用底模 VAE：', e)
    torch.backends.cudnn.benchmark = True
    torch.backends.cuda.matmul.allow_tf32 = True
    if hasattr(pipe, 'enable_attention_slicing') and a.attn_slice:
        pipe.enable_attention_slicing()
    if a.lora:
        name = pipe.load_lora_weights(a.lora)
        try:
            pipe.set_adapters([name] if isinstance(name, str) else list(name.keys()),
                              adapter_weights=[a.lora_scale])
            print('lora %s scale=%.2f' % (a.lora, a.lora_scale))
        except Exception as e:
            print('lora loaded but scale failed:', e)
    pipe = pipe.to('cuda')
    t_load = time.time() - t0

    t1 = time.time()
    img = pipe(prompt=prompt, negative_prompt=neg, width=a.width, height=a.height,
               num_inference_steps=a.steps, guidance_scale=a.cfg,
               generator=gen).images[0]
    t_gen = time.time() - t1

    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)

    vram = torch.cuda.max_memory_allocated() / 1024 ** 3
    # 黑图自检：VAE 精度不对（或 latent 溢出）时出图会是纯黑/纯色，必须拦住
    try:
        import numpy as _np
        _a = _np.asarray(img.convert('L'), dtype='float32')
        _std = float(_a.std())
        if _std < 3:
            print('!! 警告：出图像素标准差 %.1f，疑似黑图/坏图（检查 VAE 精度）' % _std)
    except Exception:
        pass
    print('ok model_load %.1fs gen %.1fs  vram_peak %.2fGB  %dx%d steps=%d seed=%d'
          % (t_load, t_gen, vram, a.width, a.height, a.steps, a.seed))
    print('out', out)
    print('prompt', prompt)


if __name__ == '__main__':
    main()
