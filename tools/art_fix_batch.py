# -*- coding: utf-8 -*-
"""重出 4 张不达标的样张（结局×3 + 苍民立绘），按我定的三条修正规则：

1. 结局（A 语言）：**画面里不要边框、不要罗马数字、不要标题栏**——框和数字由 CSS 画；
   否则尺寸一缩就是一堆假字形（第一版就中了）。
2. 立绘（C 语言）：米白纸底 + 单一墨线，禁彩色/渐变；苍民那张要去掉现代军帽感。
3. 全部：禁画面内文字（negative 里明确 glyph/lettering/numeral）。

用法：python tools/art_fix_batch.py
"""
import os
import subprocess
import sys
import time
from pathlib import Path

GAME = Path(__file__).resolve().parents[1]
PY = sys.executable
GEN = GAME / 'tools' / 'gen_art_diffusers.py'

NEG_A = ('text, lettering, glyphs, roman numeral, number, border, frame, title bar, '
         'caption, watermark, photograph, 3d render, bright saturated colors, '
         'modern clothing, lowres, jpeg artifacts')
NEG_C = ('color, vivid colors, gradient shading, smooth airbrush, photograph, 3d render, '
         'text, lettering, watermark, modern military hat, cap with visor, sunglasses')

ITEMS = [
    ('art/ending/ending_watched.webp',
     'tarot style illustration, dark scene with one glowing area: a lone diver kneeling before '
     'a vast humming machine, one red light watching, muted palette with a single hot red accent, '
     'grainy print texture, no border, no text', NEG_A, 640, 936, 41),
    ('art/ending/ending_averted.webp',
     'tarot style illustration, dark scene with one glowing area: the same corridor seen from '
     'behind, the diver walking away, red light fading into black, muted palette with a single '
     'hot red accent, grainy print texture, no border, no text', NEG_A, 640, 936, 42),
    ('art/ending/ending_walked.webp',
     'tarot style illustration, dark scene with one glowing area: diver and a vague silhouette '
     'walking side by side into the red dark, muted palette with a single hot red accent, '
     'grainy print texture, no border, no text', NEG_A, 640, 936, 43),
    ('art/portraits/cangmin.webp',
     'antique plate portrait of a sleepless prophet, long dark hair, closed eyes, plain cloth '
     'headwrap without any brim, ink lines on aged paper, faint red mark on the forehead, '
     'no background, frontal bust', NEG_C, 640, 960, 44),
]


def main():
    os.environ.setdefault('HF_ENDPOINT', 'https://hf-mirror.com')
    ok = 0
    for out, prompt, neg, w, h, seed in ITEMS:
        dst = GAME / out
        dst.parent.mkdir(parents=True, exist_ok=True)
        t0 = time.time()
        r = subprocess.run([PY, str(GEN), '--raw', '--prompt', prompt, '--neg', neg,
                            '--out', str(dst.with_suffix('.png')), '--width', str(w),
                            '--height', str(h), '--steps', '22', '--seed', str(seed)],
                           capture_output=True, text=True, encoding='utf-8', errors='replace')
        took = time.time() - t0
        good = r.returncode == 0 and dst.with_suffix('.png').exists()
        print('%-34s %s %5.0fs' % (out.split('/')[-1], 'ok' if good else 'FAIL', took))
        if not good:
            print((r.stderr or '')[-300:])
        else:
            ok += 1
    print('done %d/%d' % (ok, len(ITEMS)))


if __name__ == '__main__':
    main()
