# -*- coding: utf-8 -*-
"""夜间批量生图（23:00–08:00 窗口，断点续跑，无需 GLM）。

为什么独立于 GLM：
  GLM 额度不稳定，而生图是**本地 GPU**干活，不需要模型额度。这个脚本自己跑，出事自己处理。

用法：
  python tools\\night_gen.py                      # 默认跑 23:00→08:00，全部类别
  python tools\\night_gen.py --only foe           # 只跑敌人
  python tools\\night_gen.py --start 23:00 --end 08:00 --dry    # 演练：只报告会跑哪些

数据来源：data/art_families.json（T79 产出）
  {"foe": {"foe_family_xxx": {"prompt": "...", "style": "A"}}, "card": {...}, "event": {...}}

行为：
  · 每族一张图 → web/assets/art/<族id>.webp（长边 ≤768、q82、≤60KB）
  · 已存在的跳过（断点续跑）；失败重试 1 次，仍失败进 tools/art_failed.json 继续下一个
  · 每张都写心跳 tools/gen_progress.json（含当前族、已完成数、剩余、预计完成时间）
  · 出图后做黑图自检（std<3 视为失败）
  · 到点（默认 08:00）自动停；进度不丢，下次接着跑
  · 全部跑完写 tools/gen_summary.json
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

os.environ.setdefault('HF_ENDPOINT', 'https://hf-mirror.com')

GAME = Path(__file__).resolve().parents[1]
GEN = GAME / 'tools' / 'gen_art_diffusers.py'
FAMILIES = GAME / 'data' / 'art_families.json'
OUTDIR = GAME / 'web' / 'assets' / 'art'
PROGRESS = GAME / 'tools' / 'gen_progress.json'
FAILED = GAME / 'tools' / 'art_failed.json'
SUMMARY = GAME / 'tools' / 'gen_summary.json'
VAE = GAME / 'models' / 'sdxl-vae-fp16-fix.safetensors'   # 可选；不用就设 None

STYLE_A = ('ink line drawing on aged off-white paper, dense fine hatching, plate from an old '
           'naturalist volume, single small red accent, no border')
NEG = ('text, letters, glyphs, caption, watermark, border, frame, photograph, 3d render, '
       'color photo, bright saturated colors, gradient, glow, extra limbs, deformed')


def now():
    return datetime.now()


def in_window(start_s, end_s, t=None):
    """23:00→08:00 这种跨夜窗口。"""
    t = t or now()
    cur = t.strftime('%H:%M')
    if start_s <= end_s:
        return start_s <= cur < end_s
    return cur >= start_s or cur < end_s


def load_families(only=None):
    if not FAMILIES.exists():
        raise SystemExit('缺 data/art_families.json（T79 产出）。先做族表：\n'
                         '  · 三类对象分「形态族」，每族一条 prompt，跨类别不复用\n'
                         '  · 参考 docs/art/ART_DIRECTION_V2.md 的 R1–R6')
    data = json.loads(FAMILIES.read_text(encoding='utf-8'))
    order = ['foe', 'event', 'card']
    jobs = []
    for kind in order:
        if only and kind not in only:
            continue
        for fid, meta in (data.get(kind) or {}).items():
            jobs.append((kind, fid, meta))
    return jobs


def prompt_of(meta):
    p = meta.get('prompt') or ''
    style = meta.get('style', 'A')
    if style == 'A':
        return p if 'ink line drawing' in p else (p + ', ' + STYLE_A)
    return p


def gen_one(fid, prompt, seed, w, h, out: Path):
    cmd = [sys.executable, str(GEN), '--raw', '--prompt', prompt, '--neg', NEG,
           '--out', str(out), '--width', str(w), '--height', str(h),
           '--steps', '20', '--seed', str(seed)]
    if VAE.exists():
        cmd += ['--vae', str(VAE)]
    t0 = time.time()
    r = subprocess.run(cmd, cwd=str(GAME), capture_output=True, text=True,
                       encoding='utf-8', errors='replace')
    took = time.time() - t0
    if r.returncode != 0 or not out.exists():
        return False, took, (r.stderr or r.stdout or '')[-300:]
    if '疑似黑图' in (r.stdout or ''):
        out.unlink(missing_ok=True)
        return False, took, '黑图（std<3）'
    return True, took, ''


def write_json(p: Path, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--start', default='23:00')
    ap.add_argument('--end', default='08:00')
    ap.add_argument('--only', default='', help='foe,event,card 的子集，逗号分隔')
    ap.add_argument('--width', type=int, default=512)
    ap.add_argument('--height', type=int, default=752)
    ap.add_argument('--dry', action='store_true')
    a = ap.parse_args()

    only = [x.strip() for x in a.only.split(',') if x.strip()] or None
    jobs = load_families(only)
    todo = [(k, f, m) for (k, f, m) in jobs if not (OUTDIR / (f + '.webp')).exists()]
    print('族总数 %d，已完成 %d，本次待跑 %d' % (len(jobs), len(jobs) - len(todo), len(todo)), flush=True)
    if a.dry:
        for k, f, _ in todo[:20]:
            print('  将跑', k, f)
        print('（--dry，不实际生成）')
        return 0

    failed = json.loads(FAILED.read_text(encoding='utf-8')) if FAILED.exists() else []
    done = 0
    t_start = now()
    avg = None
    for idx, (kind, fid, meta) in enumerate(todo, 1):
        if not in_window(a.start, a.end):
            print('到点（%s），停在 %d/%d' % (a.end, idx - 1, len(todo)), flush=True)
            break
        out = OUTDIR / (fid + '.webp')
        out.parent.mkdir(parents=True, exist_ok=True)
        seed = int(meta.get('seed') or (abs(hash(fid)) % 2147483647))
        ok, took, err = gen_one(fid, prompt_of(meta), seed, a.width, a.height, out)
        if not ok:   # 重试一次
            print('  重试 %s' % fid, flush=True)
            ok, took2, err = gen_one(fid, prompt_of(meta), seed + 1, a.width, a.height, out)
            took += took2
        if ok:
            done += 1
            avg = took if avg is None else (avg * 0.7 + took * 0.3)
        else:
            failed.append({'id': fid, 'kind': kind, 'when': now().isoformat(timespec='seconds'),
                           'err': err})
            write_json(FAILED, failed)
        remain = len(todo) - idx
        eta = (now() + timedelta(seconds=(avg or 120) * remain)).strftime('%H:%M')
        write_json(PROGRESS, {
            'updated': now().isoformat(timespec='seconds'),
            'kind': kind, 'current': fid, 'done': done, 'attempted': idx,
            'total': len(todo), 'remain': remain,
            'avg_sec': round(avg, 1) if avg else None,
            'eta': eta, 'failed': len(failed),
            'window': [a.start, a.end],
        })
        print('[%d/%d] %-24s %s %5.0fs  ETA %s'
              % (idx, len(todo), fid, 'ok' if ok else 'FAIL', took, eta), flush=True)

    write_json(SUMMARY, {'finished': now().isoformat(timespec='seconds'),
                         'generated': done, 'failed': len(failed),
                         'total': len(todo), 'window': [a.start, a.end]})
    print('本次完成 %d，失败 %d（明细 %s）' % (done, len(failed), FAILED))
    return 0


if __name__ == '__main__':
    sys.exit(main())
