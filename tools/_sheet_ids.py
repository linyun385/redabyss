# -*- coding: utf-8 -*-
"""按 id 列表拼审图表。
用法：python tools/_sheet_ids.py bad|all|first:N   [cell]
  bad      = foe_check.json 里可疑的那些（不红/太暗/太亮）
  all      = 全部敌人
  first:N  = 前 N 张
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.stdout.reconfigure(encoding='utf-8')
GAME = Path(__file__).resolve().parents[1]
ART = GAME / 'web' / 'assets' / 'art'
OUT = GAME / 'art' / '_review20'
CAT = json.loads((GAME / 'data' / 'art_catalog.json').read_text(encoding='utf-8'))
NAMES = {r['id']: r['name'] for r in CAT}
CHK = json.loads((GAME / 'data' / 'foe_check.json').read_text(encoding='utf-8'))


def pick(mode):
    if mode == 'bad':
        return [c['id'] for c in CHK if c['red'] < 15 or c['lum'] < 22 or c['lum'] > 165]
    if mode == 'all':
        return [c['id'] for c in CHK]
    n = int(mode.split(':')[1])
    return [c['id'] for c in CHK[:n]]


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'bad'
    cell = int(sys.argv[2]) if len(sys.argv) > 2 else 250
    ids = pick(mode)
    cols = 6 if len(ids) > 20 else 4
    rows = (len(ids) + cols - 1) // cols
    LAB = 18
    img = Image.new('RGB', (cols * cell, rows * (cell + LAB)), (16, 14, 12))
    d = ImageDraw.Draw(img)
    stat = {c['id']: c for c in CHK}
    for i, rid in enumerate(ids):
        p = ART / (rid + '.webp')
        if not p.exists():
            continue
        im = Image.open(p).convert('RGB')
        im.thumbnail((cell, cell), Image.LANCZOS)
        x, y = (i % cols) * cell, (i // cols) * (cell + LAB)
        img.paste(im, (x + (cell - im.width) // 2, y + LAB))
        c = stat[rid]
        d.text((x + 4, y + 3), '%s %s r%.0f l%.0f'
               % (rid.replace('enemy_', ''), NAMES.get(rid, '')[:6], c['red'], c['lum']),
               fill=(235, 225, 205))
    OUT.mkdir(parents=True, exist_ok=True)
    f = OUT / ('sheet_%s.png' % mode.replace(':', ''))
    img.save(f)
    print('saved', f, img.size, len(ids), '张')
    return 0


if __name__ == '__main__':
    sys.exit(main())
