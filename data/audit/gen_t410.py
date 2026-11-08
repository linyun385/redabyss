# -*- coding: utf-8 -*-
"""T410 按脉重组效果全集 → docs/design/vein_effects_by_vein.md

把 219 张按脉分组（光/水/热/震/矿/无脉/多脉），每张带效果一句话（describe_card，与
CARD_EFFECTS_AUTO.md 同源）。多脉卡在「多脉」节集中列（不复制进单脉，避免重复计数）。
复算：python data/audit/gen_t410.py

用法：python data/audit/gen_t410.py
"""
import io, sys
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_common import GAME, CN_CLASS, CN_TYPE, CN_RARITY, load_cards, all_cards, one_line, card_veins

OUT = GAME / 'docs' / 'design' / 'vein_effects_by_vein.md'

groups = defaultdict(list)
for cls, c in all_cards(load_cards()):
    vs = card_veins(c)
    key = vs[0] if len(vs) == 1 else '多脉'
    groups[key].append((cls, c))

ORDER = ['光', '水', '热', '震', '矿', '无', '多脉']
INTRO = {
 '光': '注意看：多少张是纯过牌/平 buff（T406 已判它们不像光）',
 '水': '只有 24 张，全池最薄——注意「流转是主体」的有几张',
 '热': '注意「只改自己」的热牌（T406 V1）混在里面',
 '震': '注意 2/3 费大动作和共振支付的占比',
 '矿': '最大脉之一——注意纯过牌/共振位混在里面（T406）',
 '无': '11 张无脉牌，归属建议见 vein_no_vein_advice.md',
 '多脉': '5 张桥牌——通用池缝合用的',
}

buf = io.StringIO()
buf.write('# T410 · 每脉效果全集\n\n')
buf.write('> 数据源：`cards/*.json`；效果一句话 = `tools/card_desc.describe_card()`（与 `CARD_EFFECTS_AUTO.md` 同源）。\n')
buf.write('> 分组：单脉卡进各脉节；多脉卡集中列在「多脉」节（不复制进单脉，避免重复计数）。')
buf.write('复算：`python data/audit/gen_t410.py`。\n\n')

total = 0
for v in ORDER:
    members = groups.get(v, [])
    total += len(members)
    buf.write('---\n\n## %s（%d 张）\n\n%s\n\n' % (v, len(members), INTRO[v]))
    buf.write('| id | 角色 | 名字 | 类型 | 费 | 稀有度 | 效果一句话 |\n|---|---|---|---|---|---|---|\n')
    for cls, c in members:
        buf.write('| %s | %s | %s | %s | %s | %s | %s |\n' % (
            c['id'], CN_CLASS[cls], c['name'], CN_TYPE.get(c.get('type'), ''),
            c.get('energy', 0), CN_RARITY.get(c.get('rarity'), ''), one_line(c)))
buf.write('\n合计（含多脉节）：%d —— 应等于 219。\n' % total)

OUT.write_text(buf.getvalue(), encoding='utf-8')
print('written', OUT, {k: len(v) for k, v in groups.items()}, 'total', total)
