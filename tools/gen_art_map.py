# -*- coding: utf-8 -*-
"""生成素材映射表：每张图 ↔ 当前被哪些卡牌 / 敌人 / 职业 / 结局使用。

规则与 web/index.html 完全一致（改那边就要改这里）：
  卡面  face_<eco>_<1..6>      eco = 首脉映射（light→eco_sea / water→eco_arid / heat→eco_vent
                                     / tremor→eco_cold / mineral→eco_rad），无脉时
                                     diver|anmin→eco_surface，其它→eco_nexus
                               序号 = 1 + sum(charCode(card.id)) % 6
  敌人  foe_<layerEco>_<1..3>   序号 = 1 + sum(charCode(enemy.id)) % 3
  职业  class_<classId>
  结局  end_ending_<endingId>

输出：
  docs/ART_MAP.md   人读（按类别分组，图 → 使用者列表）
  docs/ART_MAP.csv  机读（id,kind,eco,users,file,prompt）
"""
import csv
import glob
import json
import sys
from pathlib import Path

GAME = Path(__file__).resolve().parents[1]
OUT_MD = GAME / 'docs' / 'ART_MAP.md'
OUT_CSV = GAME / 'docs' / 'ART_MAP.csv'

VEIN_ECO = {'light': 'eco_sea', 'water': 'eco_arid', 'heat': 'eco_vent',
            'tremor': 'eco_cold', 'mineral': 'eco_rad'}
LAYER_ECO = {1: 'eco_surface', 2: 'eco_cold', 3: 'eco_arid', 4: 'eco_sea',
             5: 'eco_vent', 6: 'eco_rad', 7: 'eco_core', 8: 'eco_nexus'}


def jhash(text):
    """和 JS 的 str.split('').reduce((a,ch)=>a+ch.charCodeAt(0),0) 等价。"""
    return sum(ord(c) for c in text)


def load_cards():
    out = []
    for f in sorted(glob.glob(str(GAME / 'cards' / '*.json'))):
        d = json.loads(Path(f).read_text(encoding='utf-8'))
        items = d if isinstance(d, list) else (d.get('cards') or list(d.values())[0])
        if not isinstance(items, list):
            continue
        for c in items:
            if isinstance(c, dict) and c.get('id'):
                out.append(c)
    return out


def load_enemies():
    out = []
    for f in sorted(glob.glob(str(GAME / 'enemies' / '*.json'))):
        d = json.loads(Path(f).read_text(encoding='utf-8'))
        items = d if isinstance(d, list) else (d.get('enemies') or list(d.values())[0])
        if not isinstance(items, list):
            continue
        for e in items:
            if isinstance(e, dict) and e.get('id'):
                out.append(e)
    return out


def card_art_id(card):
    veins = card.get('veins') or []
    eco = VEIN_ECO.get(veins[0]) if veins else None
    if not eco:
        eco = 'eco_surface' if card.get('class') in ('diver', 'anmin') else 'eco_nexus'
    return 'face_%s_%d' % (eco, 1 + jhash(str(card.get('id', ''))) % 6)


def foe_art_id(enemy):
    try:
        layer = int(enemy.get('layer') or 1)
    except (TypeError, ValueError):
        layer = 1
    eco = LAYER_ECO.get(layer, 'eco_nexus')
    return 'foe_%s_%d' % (eco, 1 + jhash(str(enemy.get('id', ''))) % 3)


def main():
    manifest = json.loads((GAME / 'tools' / 'art_manifest.json').read_text(encoding='utf-8'))
    entries = {e['id']: e for e in manifest['entries']}
    art_dir = GAME / 'web' / 'assets' / 'art'

    users = {}

    def add(aid, kind, label):
        users.setdefault(aid, {'kind': kind, 'users': []})['users'].append(label)

    for c in load_cards():
        add(card_art_id(c), 'card', '%s（%s）' % (c.get('name', '?'), c.get('id')))
    for e in load_enemies():
        add(foe_art_id(e), 'enemy', '%s（%s）' % (e.get('name', '?'), e.get('id')))
    for cid, cname in [('diver', '下潜者'), ('tremor', '震语者'), ('cangmin', '疯先知'), ('anmin', '维护者')]:
        add('class_' + cid, 'class', cname)
    for eid in ('ending_watched', 'ending_averted', 'ending_walked'):
        add('end_' + eid, 'ending', eid)

    rows = []
    for aid, meta in sorted(users.items()):
        e = entries.get(aid, {})
        p = e.get('prompt')
        if isinstance(p, dict):
            p = ' '.join(x for x in (p.get('prefix'), p.get('obj'), p.get('suffix')) if x)
        f = art_dir / (aid + '.webp')
        rows.append({
            'id': aid,
            'kind': meta['kind'],
            'eco': e.get('eco', ''),
            'obj': e.get('obj', ''),
            'users': ' / '.join(meta['users']),
            'user_count': len(meta['users']),
            'file': 'web/assets/art/%s.webp' % aid,
            'exists': f.exists(),
            'kb': round(f.stat().st_size / 1024, 1) if f.exists() else 0,
            'prompt': (p or '')[:300],
        })

    # 没被任何卡/怪引用的图也列出来（孤儿图）
    for aid, e in entries.items():
        if aid not in users:
            f = art_dir / (aid + '.webp')
            rows.append({'id': aid, 'kind': 'unused', 'eco': e.get('eco', ''),
                         'obj': e.get('obj', ''), 'users': '', 'user_count': 0,
                         'file': 'web/assets/art/%s.webp' % aid,
                         'exists': f.exists(),
                         'kb': round(f.stat().st_size / 1024, 1) if f.exists() else 0,
                         'prompt': ''})

    with OUT_CSV.open('w', encoding='utf-8-sig', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    lines = ['# 素材映射表（哪张图被谁用）', '',
             '> 自动生成：`python tools/gen_art_map.py`。规则以 `web/index.html` 里的 '
             '`cardArtId()` / 敌人查表为准，改代码要同步改脚本。', '',
             '## 一页速查', '',
             '| 类别 | 图 id 规则 | 数量 |', '|---|---|---|',
             '| 卡面 | `face_<生态>_<1..6>`（按卡牌首脉取生态，id 哈希取序号）| %d |'
             % len([r for r in rows if r['kind'] == 'card']),
             '| 敌人 | `foe_<层对应生态>_<1..3>`（按敌人 layer + id 哈希）| %d |'
             % len([r for r in rows if r['kind'] == 'enemy']),
             '| 职业立绘 | `class_<职业id>` | %d |' % len([r for r in rows if r['kind'] == 'class']),
             '| 结局 | `end_ending_<结局id>` | %d |' % len([r for r in rows if r['kind'] == 'ending']),
             '']

    for kind, title in (('card', '卡面（face_*）'), ('enemy', '敌人（foe_*）'),
                        ('class', '职业立绘（class_*）'), ('ending', '结局（end_*）')):
        sub = [r for r in rows if r['kind'] == kind]
        if not sub:
            continue
        lines += ['## ' + title, '', '| 图 id | 生态 | 被谁用（%d 处）| 文件 |' % 0, '|---|---|---|---|']
        lines[-2] = '| 图 id | 生态 | 使用者 | 文件 |'
        for r in sub:
            lines.append('| `%s` | %s | %s | %s |' % (
                r['id'], r['eco'] or '-', r['users'].replace('|', '/') or '（未被引用）', r['file']))
        lines.append('')

    OUT_MD.write_text('\n'.join(lines), encoding='utf-8')
    print('写出', OUT_MD, OUT_CSV)
    print('条目 %d（卡面 %d / 敌人 %d / 职业 %d / 结局 %d / 孤儿 %d）' % (
        len(rows),
        sum(1 for r in rows if r['kind'] == 'card'),
        sum(1 for r in rows if r['kind'] == 'enemy'),
        sum(1 for r in rows if r['kind'] == 'class'),
        sum(1 for r in rows if r['kind'] == 'ending'),
        sum(1 for r in rows if r['kind'] == 'unused')))


if __name__ == '__main__':
    sys.exit(main())
