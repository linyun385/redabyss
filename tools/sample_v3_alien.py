# -*- coding: utf-8 -*-
"""验证「红渊化 + 非素描」方向的两张样张。

用户 2026-11-01 19:17 的判定：
  · 这四张「完全能看出来具体的形象」→ 具象方向是对的
  · 但「太素、太现实」—— 青蛙就是一个人类世界的青蛙；我们的世界里这些东西应该有完全不一样的形态
  · 而且「不应该是素描的形式」

所以这一版改动：
  1) 形态异化：给每种生物/物件加 1–2 个「不属于地球」的形态标记
     （器官被别的材料替代 / 多出环形眼 / 对称破缺 / 长出工艺结构）
  2) 风格换掉素描：铜版实色印刷（赭黄 + 烟灰 + 一点朱红），不是铅笔/排线素描
"""
import os
import subprocess
import sys
import time
from pathlib import Path

GAME = Path(__file__).resolve().parents[1]
GEN = GAME / 'tools' / 'gen_art_diffusers.py'
OUT = GAME / 'art' / '_samples_v3'
VAE = GAME / 'models' / 'sdxl-vae-fp16-fix.safetensors'

STYLE = ('antique lithograph print, flat blocks of ochre yellow and soot grey, fine stipple '
         'shading, deep ink contours, aged yellowed paper, single vermilion accent, '
         'no pencil sketch, no graphite, no hatching-only look')

NEG = ('pencil sketch, graphite, charcoal, monochrome sketch, cross-hatching only, '
       'photograph, realistic wildlife photo, earth animal, dog, cat, horse, butterfly, '
       'cartoon, anime, 3d render, text, letters, glyphs, labels, diagram, callouts, '
       'multiple views, inset, border, frame, watermark, bright saturated colors')

ITEMS = [
    ('foe_cave_amphibian_v3', 640, 936, 601,
     'a cave amphibian whose back has split into overlapping salt-crystal plates, '
     'six small eyes set in a ring around a wide flat head, forelimbs fused into one broad '
     'pad with too many thin fingers, translucent belly showing a second smaller skeleton '
     'curled inside, sitting half-submerged in seepage water, black water reflecting its plates, '
     + STYLE),
    ('card_energy_gun_v3', 640, 936, 602,
     'an energy weapon grown rather than manufactured: the barrel is a fused length of pale '
     'bone and copper pipe, a glass organ along its side pulses red, the grip is wrapped in '
     'dried sinew and stitched leather, pressure gauge replaced by a single small eye, '
     'resting on a scratched metal table, ' + STYLE),
]


def main():
    os.environ.setdefault('HF_ENDPOINT', 'https://hf-mirror.com')
    OUT.mkdir(parents=True, exist_ok=True)
    for name, w, h, seed, prompt in ITEMS:
        out = OUT / (name + '.png')
        cmd = [sys.executable, str(GEN), '--raw', '--prompt', prompt, '--neg', NEG,
               '--out', str(out), '--width', str(w), '--height', str(h),
               '--steps', '22', '--seed', str(seed)]
        if VAE.exists():
            cmd += ['--vae', str(VAE)]
        t0 = time.time()
        r = subprocess.run(cmd, cwd=str(GAME), capture_output=True, text=True,
                           encoding='utf-8', errors='replace')
        ok = r.returncode == 0 and out.exists() and '疑似黑图' not in (r.stdout or '')
        print('%-28s %s %5.0fs' % (name, 'ok' if ok else 'FAIL', time.time() - t0), flush=True)
        if not ok:
            print((r.stdout or '')[-200:], (r.stderr or '')[-200:])


if __name__ == '__main__':
    sys.exit(main())
