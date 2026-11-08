# -*- coding: utf-8 -*-
"""卡牌试点审图：把 jobs_card.json 里的 id 拼一张表，并统计"构图雷同度"。
雷同度 = 各图的平均色/亮度分布间的标准差；越低说明越像同一张图。
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.stdout.reconfigure(encoding='utf-8')
GAME = Path(__file__).resolve().parents[1]
ART = GAME / 'web' / 'assets' / 'art'
OUT = GAME / 'art' / '_review20'
JOBS = GAME / 'data' / 'jobs_card.json'
NAMES = {r['id']: r.get('name', '') for r in
         json.loads((GAME / 'data' / 'art_catalog.json').read_text(encoding='utf-8'))}


def main():
    ids = [j['id'] for j in json.loads(JOBS.read_text(encoding='utf-8'))]
    CELL, COLS, LAB = 250, 6, 18
    rows = (len(ids) + COLS - 1) // COLS
    img = Image.new('RGB', (COLS * CELL, rows * (CELL + LAB)), (16, 14, 12))
    d = ImageDraw.Draw(img)
    miss = []
    feats = []
    for i, rid in enumerate(ids):
        p = ART / (rid + '.webp')
        if not p.exists():
            miss.append(rid)
            continue
        im = Image.open(p).convert('RGB')
        small = im.copy()
        small.thumbnail((64, 64))
        px = list(small.getdata())
        feats.append([sum(c[k] for c in px) / len(px) for k in range(3)])
        im.thumbnail((CELL, CELL), Image.LANCZOS)
        x, y = (i % COLS) * CELL, (i // COLS) * (CELL + LAB)
        img.paste(im, (x + (CELL - im.width) // 2, y + LAB))
        d.text((x + 4, y + 3), '%s %s' % (rid, NAMES.get(rid, '')[:6]), fill=(235, 225, 205))
    OUT.mkdir(parents=True, exist_ok=True)
    f = OUT / 'sheet_card30.png'
    img.save(f)
    if feats:
        import statistics as st
        spread = [st.pstdev([t[k] for t in feats]) for k in range(3)]
        print('生成 %s  张数 %d  缺失 %d' % (f.name, len(feats), len(miss)))
        print('三通道均值标准差 R%.1f G%.1f B%.1f（越大越多样）' % tuple(spread))
    return 0


if __name__ == '__main__':
    sys.exit(main())
