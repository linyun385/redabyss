# -*- coding: utf-8 -*-
"""方向验证样张：按「具象优先」的新语言出 3 张（怪物 / 卡牌工具 / 事件场景）。

用户 2026-10-31 的判断：
  · 现在太抽象 —— 怪物要有怪物的样子，工具要像工具，事件要有对应场面
  · BOSS / 结局可以抽象，那是特色
所以这里的语言是「旧博物志铜版图」：米白纸 + 墨线 + 一点朱红，画出可辨认的形体。
"""
import os
import subprocess
import sys
import time
from pathlib import Path

GAME = Path(__file__).resolve().parents[1]
GEN = GAME / 'tools' / 'gen_art_diffusers.py'
OUT = GAME / 'art' / '_samples_v2'
PY = sys.executable

NEG = ('text, letters, glyphs, caption, watermark, border, frame, photograph, 3d render, '
       'color photo, bright saturated colors, gradient, glow, extra limbs, deformed')

STYLE = ('ink line drawing on aged off-white paper, dense fine hatching, plate from an old '
         'naturalist volume, single small red accent, no border')

ITEMS = [
    # 1) 怪物：休眠两栖类（D2 普通）—— 必须像两栖动物
    ('foe_amphibian.png',
     'a pale frog-like amphibian creature lying half-submerged in shallow seepage water, '
     'wet mottled skin, four legs, visible gills, one eye half open, low crouched posture, '
     + STYLE, 640, 936, 501),
    # 2) 卡牌工具：例检条款（维护者的检查单）—— 必须像工具/物件
    ('card_checklist.png',
     'a worn metal clipboard holding an inspection checklist sheet, a mechanical stamp arm '
     'pressed on it, a hanging pencil, oil stains, object study centered, '
     + STYLE, 640, 936, 502),
    # 3) 事件场景：穿防护服的遗体 —— 必须有"发生了什么"
    ('event_body.png',
     'a body in an intact protective suit slumped sitting against a rock wall, round glass '
     'faceplate, inside the visor small handwriting, dust on the shoulders, an empty corridor '
     'behind, scene drawing, ' + STYLE, 640, 936, 503),
]


def main():
    os.environ.setdefault('HF_ENDPOINT', 'https://hf-mirror.com')
    OUT.mkdir(parents=True, exist_ok=True)
    for name, prompt, w, h, seed in ITEMS:
        out = OUT / name
        t0 = time.time()
        r = subprocess.run([PY, str(GEN), '--raw', '--prompt', prompt, '--neg', NEG,
                            '--out', str(out), '--width', str(w), '--height', str(h),
                            '--steps', '22', '--seed', str(seed)],
                           capture_output=True, text=True, encoding='utf-8', errors='replace')
        print('%-22s %s %4.0fs' % (name, 'ok' if r.returncode == 0 and out.exists() else 'FAIL',
                                   time.time() - t0), flush=True)
        if r.returncode != 0:
            print((r.stderr or '')[-250:])


if __name__ == '__main__':
    main()
