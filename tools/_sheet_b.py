# -*- coding: utf-8 -*-
"""拼两张审图：
  sheet20b.png  第二抽 20 张总览
  cmp5.png      5 个改过的族，左=第一抽(a) 右=第二抽(b) 并排对比
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.stdout.reconfigure(encoding='utf-8')
GAME = Path(__file__).resolve().parents[1]
SRC = GAME / 'web' / 'assets' / 'art'
OUT = GAME / 'art' / '_review20'

ORDER = [
    'thermophile', 'saprophyte', 'gap_mite', 'moss_mat', 'salt_formation',
    'eyeless_eel', 'jumping_spider', 'waste_crab', 'cave_amphibian', 'lungfish',
    'card_inspection_board', 'card_battery_lamp', 'card_energy_gun',
    'card_oxygen_rig', 'card_tremor_meter', 'card_noose_rope',
    'evt_body_in_suit', 'evt_self_switch_lamp', 'evt_rubble', 'evt_red_fern',
]
FIXED = ['saprophyte', 'moss_mat', 'salt_formation', 'jumping_spider', 'lungfish']


def ensure(name):
    p = SRC / (name + '.webp')
    return Image.open(p).convert('RGB') if p.exists() else None


def sheet():
    CELL, COLS, LABEL = 300, 5, 22
    rows = (len(ORDER) + COLS - 1) // COLS
    img = Image.new('RGB', (COLS * CELL, rows * (CELL + LABEL)), (18, 16, 14))
    d = ImageDraw.Draw(img)
    miss = []
    for i, key in enumerate(ORDER):
        im = ensure('foe_zh3b_' + key if key in ('thermophile', 'saprophyte', 'gap_mite', 'moss_mat',
                                                'salt_formation', 'eyeless_eel', 'jumping_spider',
                                                'waste_crab', 'cave_amphibian', 'lungfish')
                    else ('card_zh3b_' + key[5:] if key.startswith('card_') else 'evt_zh3b_' + key[4:]))
        if im is None:
            miss.append(key)
            continue
        im.thumbnail((CELL, CELL), Image.LANCZOS)
        x, y = (i % COLS) * CELL, (i // COLS) * (CELL + LABEL)
        img.paste(im, (x + (CELL - im.width) // 2, y + LABEL))
        d.text((x + 4, y + 5), '%d %s (b)' % (i + 1, key), fill=(230, 220, 200))
    img.save(OUT / 'sheet20b.png')
    return miss


def cmp():
    CELL, LABEL = 420, 24
    img = Image.new('RGB', (CELL * 2, len(FIXED) * (CELL + LABEL)), (18, 16, 14))
    d = ImageDraw.Draw(img)
    for r, key in enumerate(FIXED):
        pre = 'foe_zh3_' + key
        for c, (suffix, tag) in enumerate([(pre, 'a 第一抽'), (pre.replace('_zh3_', '_zh3b_'), 'b 第二抽')]):
            im = ensure(suffix)
            if im is None:
                continue
            im.thumbnail((CELL, CELL), Image.LANCZOS)
            x, y = c * CELL, r * (CELL + LABEL)
            img.paste(im, (x + (CELL - im.width) // 2, y + LABEL))
            d.text((x + 4, y + 6), '%s · %s' % (key, tag), fill=(235, 225, 205))
    img.save(OUT / 'cmp5.png')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    miss = sheet()
    cmp()
    print('sheet20b.png + cmp5.png 生成完毕；缺失:', miss)
    return 0


if __name__ == '__main__':
    sys.exit(main())
