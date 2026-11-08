# -*- coding: utf-8 -*-
"""T66 批量生图：读 tools/art_manifest.json，逐张走 diffusers（SDXL 底模在盘）。

- 断点续跑：out 文件已存在 → 跳过
- 失败重试 1 次，仍失败记 tools/art_failed.json，继续下一张
- 每张耗时与显存峰值记 tools/art_run.json
- --only id1,id2 只跑子集（样张用）；--limit N 限张数
- HF_ENDPOINT 默认 https://hf-mirror.com（直连 HF 超时）
- 遵守 T66 实测口径：768×1152 / 20 步（832×1216 会爆显存到 10 分钟/张，只给结局 A 用 832×1216/20）

用法：
  python tools/gen_art_batch.py --only face_eco_cold_1,class_diver
  python tools/gen_art_batch.py                # 全量（断点续跑）
"""
import argparse
import io
import json
import os
import time
from io import BytesIO

from PIL import Image
from pathlib import Path

os.environ.setdefault('HF_ENDPOINT', 'https://hf-mirror.com')
os.environ.setdefault('PYTORCH_CUDA_ALLOC_CONF', 'expandable_segments:True')

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / 'tools' / 'art_manifest.json'
RUN_LOG = ROOT / 'tools' / 'art_run.json'
FAIL_LOG = ROOT / 'tools' / 'art_failed.json'

CKPT_CANDIDATES = [
    r'D:\ComfyUI\models\checkpoints\sd_xl_base_1.0.safetensors',
    r'D:\ComfyUI\models\checkpoints\sdXL_v10.safetensors',
]


def pick_ckpt():
    for p in CKPT_CANDIDATES:
        if Path(p).exists():
            return p
    raise SystemExit('找不到 SDXL 底模，检查 D:\\ComfyUI\\models\\checkpoints')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--only', default='', help='逗号分隔的 manifest id 子集')
    ap.add_argument('--limit', type=int, default=0)
    ap.add_argument('--steps', type=int, default=20)
    args = ap.parse_args()
    only = set(x for x in args.only.split(',') if x)

    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    todo = [e for e in manifest['entries'] if (not only or e['id'] in only)]
    if args.limit:
        todo = todo[:args.limit]

    import torch
    from diffusers import StableDiffusionXLPipeline

    ckpt = pick_ckpt()
    print(f'[load] {ckpt}')
    pipe = StableDiffusionXLPipeline.from_single_file(
        ckpt, torch_dtype=torch.float16, use_safetensors=True)
    pipe = pipe.to('cuda')
    pipe.set_progress_bar_config(disable=True)

    run_log = json.loads(RUN_LOG.read_text(encoding='utf-8')) if RUN_LOG.exists() else {'runs': {}}
    failed = json.loads(FAIL_LOG.read_text(encoding='utf-8')) if FAIL_LOG.exists() else {}

    for e in todo:
        out = ROOT / e['out']
        out.parent.mkdir(parents=True, exist_ok=True)
        if out.exists():
            print(f'[skip] {e["id"]} 已存在')
            continue
        prompt = e['prompt']['prefix'] + ' ' + e['prompt']['obj'] + e['prompt']['suffix']
        w, h = e['size']
        attempt_ok = False
        for attempt in (1, 2):
            try:
                t0 = time.time()
                torch.cuda.reset_peak_memory_stats()
                img = pipe(prompt=prompt, negative_prompt=e['negative'],
                           width=w, height=h, num_inference_steps=args.steps,
                           guidance_scale=6.0, generator=None or torch.Generator('cuda').manual_seed(e['seed'])).images[0]
                ms = int((time.time() - t0) * 1000)
                vram = int(torch.cuda.max_memory_allocated() / 1024 / 1024)
                # T69 体积帽：≤30KB（webp）。先 q 降档（82→78），仍超则缩边 0.85×（最多 3 轮）
                qv = 82
                blob = io.BytesIO()
                img.save(blob, 'WEBP', quality=qv, method=6)
                tmp = img
                rounds = 0
                while blob.getbuffer().nbytes > 30 * 1024 and rounds < 3:
                    if qv > 78:
                        qv = 78
                    else:
                        tmp = tmp.resize((max(1, int(tmp.width * 0.85)), max(1, int(tmp.height * 0.85))), Image.LANCZOS)
                    blob = io.BytesIO()
                    tmp.save(blob, 'WEBP', quality=qv, method=6)
                    rounds += 1
                out.write_bytes(blob.getvalue())
                run_log['runs'][e['id']] = {'ms': ms, 'vram_mb': vram, 'attempt': attempt,
                                            'out': e['out'], 'steps': args.steps, 'size': [w, h]}
                failed.pop(e['id'], None)
                print(f'[ok] {e["id"]} {ms}ms {vram}MB → {e["out"]}')
                attempt_ok = True
                break
            except Exception as ex:  # 重试 1 次
                print(f'[err] {e["id"]} attempt {attempt}: {ex}')
                failed[e['id']] = str(ex)[:300]
        RUN_LOG.write_text(json.dumps(run_log, ensure_ascii=False, indent=1), encoding='utf-8')
        FAIL_LOG.write_text(json.dumps(failed, ensure_ascii=False, indent=1), encoding='utf-8')
        if not attempt_ok:
            print(f'[fail-final] {e["id"]}，已记录，继续')

    done = len(run_log['runs'])
    print(f'[done] 累计成功 {done} 张')


if __name__ == '__main__':
    main()
