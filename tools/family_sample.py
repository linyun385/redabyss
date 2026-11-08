# -*- coding: utf-8 -*-
"""从 data/art_families.json 里挑几族出样张（验证「具象优先」方向）。

用法：python tools/family_sample.py [--only foe_family_cave_amphibian,card_family_energy_gun]
输出：art/_samples_families/<族id>.png
"""
import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

GAME = Path(__file__).resolve().parents[1]
FAM = GAME / 'data' / 'art_families.json'
OUT = GAME / 'art' / '_samples_families'
GEN = GAME / 'tools' / 'gen_art_diffusers.py'
VAE = GAME / 'models' / 'sdxl-vae-fp16-fix.safetensors'
STYLE_A = ('ink line drawing on aged off-white paper, dense fine hatching, plate from an old '
           'naturalist volume, single small red accent, no border')
NEG = ('text, letters, glyphs, caption, fake writing, border, frame, photograph, 3d render, '
       'color photo, bright saturated colors, gradient, glow, extra limbs, deformed')

DEFAULT = ['foe_family_cave_amphibian', 'foe_family_jumping_spider',
           'card_family_energy_gun', 'event_d3_1', 'evt_event_d3_1']


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--only', default='')
    ap.add_argument('--width', type=int, default=512)
    ap.add_argument('--height', type=int, default=752)
    a = ap.parse_args()
    os.environ.setdefault('HF_ENDPOINT', 'https://hf-mirror.com')
    fam = json.loads(FAM.read_text(encoding='utf-8'))
    flat = {}
    for kind in ('foe', 'card', 'event'):
        for fid, meta in (fam.get(kind) or {}).items():
            flat[fid] = meta
    picks = [x for x in a.only.split(',') if x] or DEFAULT
    picks = [p for p in picks if p in flat] or DEFAULT
    OUT.mkdir(parents=True, exist_ok=True)
    for fid in picks:
        meta = flat[fid]
        prompt = meta['prompt']
        if 'ink line drawing' not in prompt:
            prompt += ', ' + STYLE_A
        out = OUT / (fid + '.png')
        cmd = [sys.executable, str(GEN), '--raw', '--prompt', prompt, '--neg', NEG,
               '--out', str(out), '--width', str(a.width), '--height', str(a.height),
               '--steps', '20', '--seed', str(abs(hash(fid)) % 2147483647)]
        if VAE.exists():
            cmd += ['--vae', str(VAE)]
        t0 = time.time()
        r = subprocess.run(cmd, cwd=str(GAME), capture_output=True, text=True,
                           encoding='utf-8', errors='replace')
        ok = r.returncode == 0 and out.exists() and '疑似黑图' not in (r.stdout or '')
        print('%-30s %s %5.0fs' % (fid, 'ok' if ok else 'FAIL', time.time() - t0), flush=True)
        if not ok:
            print((r.stdout or '')[-200:], (r.stderr or '')[-200:])


if __name__ == '__main__':
    sys.exit(main())
