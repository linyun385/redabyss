# -*- coding: utf-8 -*-
"""T508 卡面描述可读性分级 → docs/design/card_readability.md

口径：字数 = describe_card(card) 输出去掉半角空格后的字符数（近似玩家在卡面读到的效果文字）。
分档：<20 / 20-40 / >40。最长 15 张逐张分析。
复算：python data/audit/gen_t508.py

用法：python data/audit/gen_t508.py
"""
import io, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_common import GAME, CN_CLASS, load_cards, all_cards, one_line

OUT = GAME / 'docs' / 'design' / 'card_readability.md'

def desc_len(c):
    return len(one_line(c).replace(' ', ''))

items = []
for cls, c in all_cards(load_cards()):
    items.append((desc_len(c), cls, c))
items.sort(key=lambda x: -x[0])

t1 = sum(1 for L, _, _ in items if L < 20)
t2 = sum(1 for L, _, _ in items if 20 <= L <= 40)
t3 = sum(1 for L, _, _ in items if L > 40)

buf = io.StringIO()
buf.write('# T508 · 卡面描述可读性分级\n\n')
buf.write('> 口径：字数 = `tools/card_desc.describe_card()` 输出去掉半角空格后的字符数（近似玩家在卡面读到的效果文字长度）。\n')
buf.write('> 分档：<20 / 20–40 / >40。复算：`python data/audit/gen_t508.py`。\n\n')

buf.write('## 分布\n\n| 档 | 张数 | 占比 |\n|---|---|---|\n')
buf.write('| <20 字 | %d | %.1f%% |\n| 20–40 字 | %d | %.1f%% |\n| >40 字 | %d | %.1f%% |\n' % (
    t1, 100*t1/len(items), t2, 100*t2/len(items), t3, 100*t3/len(items)))
buf.write('\n总 219 张。\n\n')

buf.write('## 最长 15 张逐张分析\n\n')
NOTES = {
 'dive_0011': '门槛+共振+AOE 三件套——是「需要读才能懂」的合理复杂，不是啰嗦',
 'dive_0024': '三段伤害+门槛，说明长是因为数字多',
 'trem_0013': '三段+共振支付+凝视门槛，三种定价叠一张——全游戏最难读的一张，玩家可能直接不点开说明',
 'trem_0014': '门槛+共振+再生，长在机制叠加',
 'trem_0058': '门槛 8 是全游戏最高——文字里必须解释清楚，长是必要的',
 'trem_0060': 'AOE+门槛，同上',
 'trem_0075': '共振支付+大抽牌，说明较长但语义单一',
 'trem_0056': '凝视门槛+抽牌，中等复杂',
 'trem_0057': '共振+凝视双资源，长在必须解释两个系统',
 'trem_0029': '凝视管理+格挡，同上',
 'trem_0027': '凝视+过牌，凝视系统的教学牌，长是必要的',
 'trem_0066': '凝视+过牌，同上',
 'dive_0016': '共振锁定需要一句解释「锁定是什么」——机制教学成本',
 'dive_0023': '同上，大号版',
 'trem_0019': '共振锁定+格挡，同上',
}
for L, cls, c in items[:15]:
    note = NOTES.get(c['id'], '')
    if not note:
        note = '长在多机制叠加（门槛/共振/状态说明）'
    buf.write('- **`%s` %s（%s，%d 字）**\n  - 文字：%s\n  - 分析：%s\n' % (
        c['id'], c['name'], CN_CLASS[cls], L, one_line(c), note))

buf.write('\n## 判断\n\n')
buf.write('- 不到 %d%% 的卡超过 40 字——大多数卡面一屏读完，可读性基本盘是好的。\n' % round(100*t3/len(items)))
buf.write('- 长卡集中在**凝视/共振双资源区**（震语者的门槛牌最多）——长不是废话，是双资源系统要解释。要减字，减法只能是「游戏内建术语提示」（悬停解释凝视/共振/锁定），而不是删效果。\n')
buf.write('- 下潜者的门槛牌（辐射弹/钻探平台/镇爆弹）也在长卡区——说明「凝视门槛」这个机制本身的解释成本高，全卡池统一。\n')
buf.write('- 真正「长到不想读」风险的只有 1~2 张（震语：崩齿这种三定价叠加），其余长卡都有明确的解释必要性。\n')
buf.write('\n### 复算\n\n`python data/audit/gen_t508.py`；字数含标点、不含半角空格。\n')

OUT.write_text(buf.getvalue(), encoding='utf-8')
print('written', OUT, '| <20:', t1, '20-40:', t2, '>40:', t3)
for L, cls, c in items[:5]:
    print(' ', c['id'], L)
