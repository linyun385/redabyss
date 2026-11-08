# -*- coding: utf-8 -*-
"""把 266 张卡牌按顺序拼成若干张总览图（供人眼挑构图问题）。

一张图放 PER=70 张（10 列 × 7 行，格 200px），共 4 张。
标签只写 id（不带中文，避免字体缺字变方块）。

用法：python tools/_sheets_all.py
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.stdout.reconfigure(encoding='utf-8')
GAME = Path(__file__).resolve().parents[1]
ART = GAME / 'web' / 'assets' / 'art'
OUT = GAME / 'art' / '_review_all'
JOB = GAME / 'data' / 'jobs_card.json'
PER, COLS, CELL, LAB = 70, 10, 200, 18


def main():
    ids = [j['id'] for j in json.loads(JOB.read_text(encoding='utf-8'))]
    OUT.mkdir(parents=True, exist_ok=True)
    made = []
    for s in range(0, len(ids), PER):
        chunk = ids[s:s + PER]
        rows = (len(chunk) + COLS - 1) // COLS
        img = Image.new('RGB', (COLS * CELL, rows * (CELL + LAB)), (14, 12, 10))
        d = ImageDraw.Draw(img)
        for i, rid in enumerate(chunk):
            p = ART / (rid + '.webp')
            if not p.exists():
                continue
            im = Image.open(p).convert('RGB').resize((CELL, CELL), Image.LANCZOS)
            x, y = (i % COLS) * CELL, (i // COLS) * (CELL + LAB)
            img.paste(im, (x, y + LAB))
            d.text((x + 4, y + 3), rid, fill=(240, 230, 210))
        f = OUT / ('card_all_%d.png' % (s // PER + 1))
        img.save(f)
        made.append((f.name, len(chunk)))
    for n, c in made:
        print(n, c, '张')
    return 0


if __name__ == '__main__':
    sys.exit(main())
