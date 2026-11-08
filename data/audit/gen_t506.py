# -*- coding: utf-8 -*-
"""T506 每回合决策点数量 → docs/design/decision_points.md

模型（写死，可复算）：
  手牌 = 每回合抽 5 张。抽牌用游戏的稀有度权重 {common:6, uncommon:3, rare:1}
        从「角色池 + 通用池」里抽（special 也按 uncommon 处理——引擎 weightedCards 只列三档）。
  1000 回合模拟（seed=42）。
  每回合计算：
    A. 手牌类别数 = 手牌中出现的 effect 类别数（伤害/格挡/资源/减益/增益，audit_common.effect_types）
    B. 可打张数 = 4 能量下能打出的最大张数（按费用升序贪心）
    C. 资源决策数 = 手牌中带 resonance_cost / gaze_cost 的张数（打不打=决策）
    D. 决策广度 = A + C（有意义的分支数近似）
  判断「选择太少」= D < 2.5。

用法：python data/audit/gen_t506.py
"""
import io, sys, random
from pathlib import Path
from collections import Counter
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_common import (GAME, CN_CLASS, load_cards, all_cards, effect_types)

OUT = GAME / 'docs' / 'design' / 'decision_points.md'
rng = random.Random(42)
WEIGHT = {'common': 6, 'uncommon': 3, 'rare': 1, 'special': 3}
cards = load_cards()
ALL = [(cls, c) for cls, c in all_cards(cards)]

buf = io.StringIO()
buf.write('# T506 · 每回合决策点数量（4 能量 / 抽 5 张粗估）\n\n')
buf.write('> 模型：手牌=抽 5 张，按游戏稀有度权重 {普通6,精良3,稀有1}（特殊按精良处理）从「本角色池+通用池」抽；')
buf.write('1000 回合模拟，seed=42。复算：`python data/audit/gen_t506.py`。\n\n')
buf.write('| 角色 | 手牌类别数 A | 可打张数 B | 资源决策数 C | 决策广度 D=A+C | 判定 |\n|---|---|---|---|---|---|\n')

judgement = {}
for cls in ['diver', 'tremor', 'anmin', 'cangmin']:
    pool = [c for _, c in ALL if _ in (cls, 'shared')]
    pop_w = [WEIGHT[c.get('rarity', 'common')] for c in pool]
    A = B = C = D = 0
    for _ in range(1000):
        hand = rng.choices(pool, weights=pop_w, k=5)
        cats = set()
        for c in hand:
            cats.update(effect_types(c))
        resd = sum(1 for c in hand if (c.get('effect') or {}).get('resonance_cost')
                   or (c.get('effect') or {}).get('gaze_cost'))
        energy, playable = 4, 0
        for c in sorted(hand, key=lambda x: x.get('energy', 0)):
            if c.get('energy', 0) <= energy:
                energy -= c.get('energy', 0)
                playable += 1
        a = len(cats)
        A += a; B += playable; C += resd; D += a + resd
    A /= 1000; B /= 1000; C /= 1000; D /= 1000
    verdict = '偏少（基本二选一）' if D < 2.5 else ('中等' if D < 3.2 else '充足')
    judgement[cls] = (A, B, C, D, verdict)
    buf.write('| %s | %.2f | %.2f | %.2f | %.2f | %s |\n' % (
        CN_CLASS[cls], A, B, C, D, verdict))

buf.write('\n### 解读\n\n')
order = sorted(judgement.items(), key=lambda kv: kv[1][3])
buf.write('决策广度最低的角色是 **%s**（D=%.2f）——手牌里同时出现的用途类别最少。' % (
    CN_CLASS[order[0][0]], order[0][1][3]))
buf.write('决策广度最高的是 **%s**（D=%.2f）。' % (CN_CLASS[order[-1][0]], order[-1][1][3]))
buf.write('\n\n注意：这个模型只算「手牌内的分支数」，不含跨回合规划（留牌、共振积攒路线选择）——')
buf.write('后者对疯先知/震语者这类资源系角色的实际决策量贡献更大，模型里只体现为资源决策数 C。\n')
buf.write('\n### 模型细节（复算用）\n\n')
buf.write('1. 权重抽牌与 `web/index.html` 的 `weightedCards` 同款稀有度权重；special 稀有度权重按 3（=精良档）处理。\n')
buf.write('2. 类别判定 = `audit_common.effect_types`（伤害/格挡/资源/减益/增益，一卡多类）。\n')
buf.write('3. 可打张数 = 4 能量下按费用升序贪心可打出的张数（不算共振/凝视支付牌的额外打开能力——它们计入 C 而不是 B）。\n')
buf.write('4. D = A + C；阈值：<2.5 偏少，<3.2 中等，否则充足——阈值是粗估口径，不是实测结论。\n')

OUT.write_text(buf.getvalue(), encoding='utf-8')
print('written', OUT)
for k, v in judgement.items():
    print(k, ['%.2f' % x for x in v[:4]], v[4])
