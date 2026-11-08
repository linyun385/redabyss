# -*- coding: utf-8 -*-
"""生成全卡池效果总表（中文，按引擎代码翻译）。
输出：docs/design/CARD_EFFECTS_AUTO.md
"""
import json, sys, io, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from card_desc import describe_card, describe_upgrade

GAME = Path(__file__).resolve().parents[1]
CARDS = GAME / 'cards'
OUT = GAME / 'docs' / 'design' / 'CARD_EFFECTS_AUTO.md'
CLASSES = [('diver', '下潜者'), ('tremor', '震语者'), ('anmin', '维护者'),
           ('cangmin', '疯先知'), ('shared', '通用')]

buf = io.StringIO()
buf.write('# 全卡池效果总表（自动生成）\n\n')
buf.write('> 由 `tools/card_desc.py` 按 `web/index.html` 的结算代码逐键翻译，**不是手写的**。\n')
buf.write('> 重新生成：`python tools/gen_card_effects.py`\n')
buf.write('> 生成时间：%s\n\n' % time.strftime('%Y-%m-%d %H:%M:%S'))
buf.write('读法：`费` = 能量消耗；`〔〕` 里是**数据和引擎对不上的地方**（真 bug，不是笔误）。\n\n')

total = 0
for cls, cn in CLASSES:
    p = CARDS / (cls + '.json')
    if not p.exists():
        continue
    arr = json.loads(p.read_text(encoding='utf-8'))
    total += len(arr)
    buf.write('---\n\n## %s（%d 张）\n\n' % (cn, len(arr)))
    for c in arr:
        e = c.get('effect') or {}
        cost = c.get('cost_type') or 'none'
        cost_mark = '' if cost == 'none' else '　**代价：%s**（%s）' % (
            {'memory': '弃一张牌', 'vitality': '最大生命 -1',
             'mark': '凝视 +1', 'lock': '本层只能用一次',
             'custom': '自定义 — 引擎还没这个代价，待实现'}.get(cost, cost),
            c.get('cost_text') or '')
        buf.write('### `%s` %s\n\n' % (c['id'], c['name']))
        buf.write('- 费 %s　%s　%s\n' % (c.get('energy', 0),
                                        {'attack': '攻击', 'skill': '技能', 'power': '能力'}.get(c.get('type'), c.get('type')),
                                        {'common': '普通', 'uncommon': '精良', 'rare': '稀有', 'special': '特殊'}.get(c.get('rarity'), c.get('rarity'))))
        buf.write('- 效果：%s\n' % describe_card(c))
        u = describe_upgrade(c)
        if u:
            buf.write('- 升级：%s\n' % u)
        if cost_mark:
            buf.write('-%s\n' % cost_mark)
        buf.write('\n')

buf.write('---\n\n共 %d 张。\n' % total)
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(buf.getvalue(), encoding='utf-8')
print('written', OUT, total)
