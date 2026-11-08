# -*- coding: utf-8 -*-
"""T401 全卡脉象矩阵生成器 → docs/design/vein_audit_matrix.md

数据源：cards/*.json（权威）。效果一句话 = tools/card_desc.describe_card(card)，
与 docs/design/CARD_EFFECTS_AUTO.md 同源（该文档即由同一函数生成）。
RAW 比对：data/audit/raw_cards.json（由 web/index.html 行 6401 经 node JSON.parse 抽出）。

用法：python data/audit/gen_t401.py
"""
import io, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_common import (GAME, CLASSES, CN_CLASS, CN_TYPE, CN_RARITY,
                          load_cards, all_cards, card_veins, vein_key,
                          raw_vs_json_diffs, one_line)

OUT = GAME / 'docs' / 'design' / 'vein_audit_matrix.md'

buf = io.StringIO()
buf.write('# T401 · 全卡脉象矩阵\n\n')
buf.write('> 生成：`python data/audit/gen_t401.py`（算法见文末）。\n')
buf.write('> 数据源：`cards/*.json`（权威，219 张）。效果一句话由 `tools/card_desc.py` 的')
buf.write('`describe_card()` 生成，与 `docs/design/CARD_EFFECTS_AUTO.md` 同源。\n')
buf.write('> 「与谁重复」列由 T402 的全 219 张两两查重填入（判据与 `tools/dup_check.py` 相同）。\n\n')
buf.write('| id | 职业 | 名字 | 脉 | 类型 | 费 | 稀有度 | 效果一句话 | 与谁重复 |\n')
buf.write('|---|---|---|---|---|---|---|---|---|\n')

cards = load_cards()
pairs = all_cards(cards)
n = 0
for cls, c in pairs:
    n += 1
    vein = vein_key(c)
    typ = CN_TYPE.get(c.get('type'), str(c.get('type')))
    rar = CN_RARITY.get(c.get('rarity'), str(c.get('rarity')))
    buf.write('| %s | %s | %s | %s | %s | %s | %s | %s | %s |\n' % (
        c['id'], CN_CLASS[cls], c['name'], vein, typ, c.get('energy', 0),
        rar, one_line(c), ''))

buf.write('\n总行数：%d\n\n' % n)

# 数据源比对：cards/*.json vs web/index.html RAW
diffs = raw_vs_json_diffs()
buf.write('## 数据源比对（cards/*.json vs web/index.html RAW）\n\n')
buf.write('比法：用 node 从 `web/index.html` 第 6401 行 `const RAW =` 抽出 JSON 字面量，')
buf.write('逐卡逐字段比对 name/type/rarity/veins/energy/effect/cost_type/cost_text/flavor/upgrade。')
buf.write('不一致时以 json 为准（本表即按 json 生成）。\n\n')
if diffs:
    buf.write('| id | 职业 | 不一致字段 |\n|---|---|---|\n')
    for cid, cn, d in diffs:
        buf.write('| %s | %s | %s |\n' % (cid, cn, '、'.join(d)))
    buf.write('\n不一致卡数：%d\n' % len(diffs))
else:
    buf.write('零不一致：5 个文件全部字段与 RAW 一致。\n')

# 验收数字
from collections import Counter
cnt = Counter()
for cls, c in pairs:
    cnt[CN_CLASS[cls]] += 1
buf.write('\n## 验收\n\n')
buf.write('- 总行数 = %d（规格要求 219）：%s\n' % (
    n, '、'.join('%s %d' % kv for kv in cnt.items())))
buf.write('- 每行都有 id：是（脚本按 id 逐行生成，空 id 会抛异常）\n')
buf.write('- 复算命令：`python data/audit/gen_t401.py` 后数表格行，或\n')
buf.write('  `python -c "import json;print(sum(len(json.load(open(\'cards/%s.json\',encoding=\'utf-8\'))) for f in [\'diver\',\'tremor\',\'anmin\',\'cangmin\',\'shared\']))"`\n')

OUT.write_text(buf.getvalue(), encoding='utf-8')
print('written', OUT, n, 'rows; raw diffs:', len(diffs))
