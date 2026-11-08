# -*- coding: utf-8 -*-
"""拉取 fp16 安全的 SDXL VAE（madebyollin/sdxl-vae-fp16-fix）。

先后端：hf-mirror（国内快） → 失败再试 huggingface.co（用户开了 VPN）。
下载到 game/models/sdxl-vae-fp16-fix.safetensors，带进度与总体超时。
"""
import os
import sys
import time
from pathlib import Path

GAME = Path(__file__).resolve().parents[1]
DEST = GAME / 'models' / 'sdxl-vae-fp16-fix.safetensors'
REPO = 'madebyollin/sdxl-vae-fp16-fix'
FILE = 'diffusion_pytorch_model.safetensors'
TARGET_MB = 335


def try_endpoint(endpoint, timeout_s=420):
    os.environ['HF_ENDPOINT'] = endpoint
    for k in list(os.environ):
        if k.startswith('HF_'):
            pass
    print('== 尝试 %s（超时 %ds）==' % (endpoint, timeout_s), flush=True)
    t0 = time.time()
    try:
        from huggingface_hub import hf_hub_download
        p = hf_hub_download(repo_id=REPO, filename=FILE, local_dir=str(DEST.parent / 'hf'),
                            resume_download=True, force_download=False)
        mb = os.path.getsize(p) / 1024 / 1024
        print('成功：%s（%.1f MB，用时 %.0fs）' % (p, mb, time.time() - t0), flush=True)
        DEST.parent.mkdir(parents=True, exist_ok=True)
        if Path(p).resolve() != DEST.resolve():
            Path(p).replace(DEST)
        return True
    except Exception as e:
        print('失败：%s: %s（用时 %.0fs）'
              % (type(e).__name__, str(e)[:200], time.time() - t0), flush=True)
        return False


def main():
    DEST.parent.mkdir(parents=True, exist_ok=True)
    if DEST.exists() and DEST.stat().st_size > 100 * 1024 * 1024:
        print('已存在：%s（%.1f MB）' % (DEST, DEST.stat().st_size / 1024 / 1024))
        return 0
    for ep in ('https://hf-mirror.com', 'https://huggingface.co'):
        if try_endpoint(ep):
            size = DEST.stat().st_size / 1024 / 1024
            print('最终文件 %.1f MB（预期约 %d MB）' % (size, TARGET_MB))
            return 0 if size > 200 else 2
    return 1


if __name__ == '__main__':
    sys.exit(main())
