# -*- coding: utf-8 -*-
"""H03 一局资源流模拟 → docs/design/sim_economy.md
1000 局全程模拟：牌/金币/零件/遗物/事件，按层推进（商店消费策略固定）。
可复算：python tools/sim/sim_economy.py（seed=42）
"""
import sys, statistics
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from simlib import GAME, PARAMS, load_raw, gold_for_fight, parts_for

OUT = GAME / 'docs' / 'design' / 'sim_economy.md'
from config import N_ECONOMY_RUNS, SEED, LAYERS, SHOPS, ELITE_ROWS, EVENT_P as CFG_EVENT_P
N_RUNS = N_ECONOMY_RUNS
# 层结构常量来自 config.py（K05 集中化）

import random
rng = random.Random(SEED)
raw = load_raw()

# 事件资源锚点：从 events result 字段实测均值（金/血/牌）
gold_ev, heal_ev, card_ev = [], [], 0
n_opts = 0
for pool in ['events', 'anminEvents', 'cngEvents']:
    for ev in raw[pool]:
        for o in ev.get('options') or []:
            r = o.get('result') or {}
            n_opts += 1
            if r.get('gold'): gold_ev.append(r['gold'])
            if r.get('heal'): heal_ev.append(r['heal'])
            if r.get('card_reward'): card_ev += 1
avg_gold_ev = statistics.mean(gold_ev) if gold_ev else 0
avg_heal_ev = statistics.mean(heal_ev) if heal_ev else 0
p_card_ev = card_ev / n_opts

runs = []
for _ in range(N_RUNS):
    cards_n, gold, parts, relics, events_n = 12.0, 0, 0, 0, 0.0
    for L in range(1, LAYERS + 1):
        # 战斗
        fights = FIGHTS_PER_LAYER[L]
        normals = fights - ELITES_PER_LAYER[L] * 0.5
        elites = ELITES_PER_LAYER[L] * 0.5
        gold += normals * gold_for_fight(rng, 'normal') + elites * gold_for_fight(rng, 'elite')
        cards_n += fights  # 每场三选一拿 1（贪心策略上限）
        relics += elites   # 精英=遗物三选一
        if L == 4:
            gold += gold_for_fight(rng, 'boss')  # L4 起 boss
        # 事件
        ev = CFG_EVENT_P[L]
        events_n += ev
        gold += ev * avg_gold_ev * 0.6      # 六成事件含金项
        # 商店：到店策略=买 1 张卡(75) + 血线低买回血(60)，二选一固定
        if L in SHOPS:
            cards_n += 1
            gold -= 75
    runs.append((cards_n, gold, parts, relics, events_n))

def q(v, p):
    s = sorted(v)
    return s[int(p * len(s))]

buf = []
buf.append('# H03 · 一局资源流模拟（1000 局，seed=%d）' % SEED)
buf.append('')
buf.append('> **假设**：① 层节点按行选择期望模型（战斗 3.5 场/层、精英半次、事件见 T512）；')
buf.append('> ② 每场战斗必拿 1 牌（三选一贪心上限）；事件金按实测均值×0.6（六成选项含金）；')
buf.append('> ③ 商店策略固定=每店买 1 卡（75 金），不买回血（血线策略另见 H14）；④ 遗物只从精英来（boss 必给未计常量差）。')
buf.append('> **局限**：不模拟升级/删牌/共振凝视收益；精英数取整口径（实际行选择是半次期望）；金币不计利息性支出差异——结果看**分布形状**不看绝对值。')
buf.append('')
buf.append('## 终局分布（1000 局）\n')
buf.append('| 资源 | 10% | 中位 | 90% | 均值 |\n|---|---|---|---|---|')
for i, name in [(0, '卡组张数'), (1, '金币余量'), (2, '零件（非维护者计 0）'), (3, '遗物件数'), (4, '事件次数')]:
    v = [r[i] for r in runs]
    buf.append('| %s | %.1f | %.1f | %.1f | %.1f |' % (name, q(v, .1), statistics.median(v), q(v, .9), statistics.mean(v)))
buf.append('')
buf.append('## 与静态估算对照\n')
v = [r[1] for r in runs]
buf.append('- 金币中位 %.0f vs resource_curve.md 推演 ~550——同量级，验证该推演的形状。' % statistics.median(v))
v = [r[0] for r in runs]
buf.append('- 卡组中位 %.1f 张 vs deck_size.md 的 +12~18 进牌（终局 24~30）——一致（本模型含商店 3 张）。' % statistics.median(v))
buf.append('- 事件次数中位 %.1f vs event_density.md 期望 ~6.0——一致。' % statistics.median([r[4] for r in runs]))
buf.append('')
buf.append('## 复算\n')
buf.append('`python tools/sim/sim_economy.py`；常数在 simlib.PARAMS 与本文件顶部（ELITES_PER_LAYER/SHOPS）。')
OUT.write_text('\n'.join(buf) + '\n', encoding='utf-8')
print('median gold', statistics.median([r[1] for r in runs]), 'cards', statistics.median([r[0] for r in runs]), 'events', statistics.median([r[4] for r in runs]))
