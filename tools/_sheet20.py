# -*- coding: utf-8 -*-
"""把 20 族批次拼成一张 5x4 总览图，便于一次看完（省上下文）。"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.stdout.reconfigure(encoding='utf-8')
GAME = Path(__file__).resolve().parents[1]
SRC = GAME / 'web' / 'assets' / 'art'
OUT = GAME / 'art' / '_review20'

IDS = [
    'foe_zh3_thermophile', 'foe_zh3_saprophyte', 'foe_zh3_gap_mite', 'foe_zh3_moss_mat',
    'foe_zh3_salt_formation', 'foe_zh3_eyeless_eel', 'foe_zh3_jumping_spider',
    'foe_zh3_waste_crab', 'foe_zh3_cave_amphibian', 'foe_zh3_lungfish',
    'card_zh3_inspection_board', 'card_zh3_battery_lamp', 'card_zh3_energy_gun',
    'card_zh3_oxygen_rig', 'card_zh3_tremor_meter', 'card_zh3_noose_rope',
    'evt_zh3_body_in_suit', 'evt_zh3_self_switch_lamp', 'evt_zh3_rubble', 'evt_zh3_red_fern',
]
CELL = 300
COLS = 5
LABEL = 22


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = (len(IDS) + COLS - 1) // COLS
    sheet = Image.new('RGB', (COLS * CELL, rows * (CELL + LABEL)), (18, 16, 14))
    d = ImageDraw.Draw(sheet)
    missing = []
    for i, name in enumerate(IDS):
        p = SRC / (name + '.webp')
        if not p.exists():
            missing.append(name)
            continue
        im = Image.open(p).convert('RGB')
        im.thumbnail((CELL, CELL), Image.LANCZOS)
        x = (i % COLS) * CELL
        y = (i // COLS) * (CELL + LABEL)
        sheet.paste(im, (x + (CELL - im.width) // 2, y + LABEL))
        d.text((x + 4, y + 5), '%d %s' % (i + 1, name.replace('_zh3', '')), fill=(230, 220, 200))
    out = OUT / 'sheet20.png'
    sheet.save(out)
    print('saved', out, sheet.size, 'missing:', missing)
    return 0


if __name__ == '__main__':
    sys.exit(main())
