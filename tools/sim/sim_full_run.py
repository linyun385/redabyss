# -*- coding: utf-8 -*-
"""H14 整局抽卡序列模拟 → docs/design/sim_full_run.md
200 局完整游戏（四角色各 50 局）：战斗（承伤）+ 奖励三选一（加权）+ 事件（金/血/牌）+ 商店（简单策略）。
结局定义：死（累计承伤>血）于第 X 层 / 成型（任一脉 ≥5 张）/ 散牌（活着但 max 脉 <5）。
可复算：python tools/sim/sim_full_run.py（seed=42）
"""
import sys, statistics, collections
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from simlib import (GAME, PARAMS, CN_VEIN, CN_CLASS, load_cards, load_raw, class_pool,
                    show_three, pick_card, simulate_fight, layer_enemy_pool,
                    gold_for_fight, parts_for)

OUT = GAME / 'docs' / 'design' / 'sim_full_run.md'
from config import N_FULLRUN_PER_CLASS, SEED, LAYERS as CFG_LAYERS
N_PER_CLASS, LAYERS = N_FULLRUN_PER_CLASS, CFG_LAYERS
from config import FIGHTS_PER_LAYER, SHOPS, ELITE_ROWS, EVENT_P

BOSS_LAYER = {4, 5, 6, 7, 8}



BLOCK_MITIGATION = 0.25   # 贪心格挡减伤系数——按 H11 实测校准（L3 裸吃 10.8 → 贪心 1.4-2.8 ≈ 0.13-0.26）
import random
rng = random.Random(SEED)
cards = load_cards()
raw = load_raw()
# 事件资源锚（同 H03）
gold_opts, heal_opts, card_rate, dmg_opts = [], [], [0, 0], []
for pool in ['events', 'anminEvents', 'cngEvents']:
    for ev in raw[pool]:
        for o in ev.get('options') or []:
            r = o.get('result') or {}
            if r.get('gold'): gold_opts.append(r['gold'])
            if r.get('heal'): heal_opts.append(r['heal'])
            if r.get('damage'): dmg_opts.append(r['damage'])
            if r.get('card_reward'): card_rate[0] += 1
            card_rate[1] += 1
import statistics as st
avg_gold_ev = st.mean(gold_opts) if gold_opts else 0
avg_heal_ev = st.mean(heal_opts) if heal_opts else 0
avg_dmg_ev = st.mean(dmg_opts) if dmg_opts else 0
p_card = card_rate[0] / card_rate[1]

outcomes = collections.Counter()
death_layer = collections.Counter()
vein_max_end = collections.Counter()
per_class = {c: collections.Counter() for c in ['diver', 'tremor', 'anmin', 'cangmin']}
total_fights_list, deck_end = [], []

for run in range(N_PER_CLASS * 4):
    cls = ['diver', 'tremor', 'anmin', 'cangmin'][run % 4]
    hp = PARAMS['HP'][cls]
    affinity = PARAMS['AFFINITY'][cls]
    pool = class_pool(cls, cards)
    owned = {v: 0 for v in ['light', 'water', 'heat', 'tremor', 'mineral']}  # 英文键显式写出（J01 澄清：CN_VEIN 迭代本就是英文键——06 批「键错位」为误诊，见 _SIM_BUGFAMILY.md）
    gold, taken_total, fights_total = 0, 0.0, 0
    dead_at = None
    for L in range(1, LAYERS + 1):
        fights = FIGHTS_PER_LAYER[L]
        n = int(round(fights))
        for i in range(n):
            tier = 'normal'
            # 精英/boss 行：每层最后一场按行选择近似
            if i == n - 1 and L in BOSS_LAYER and L >= 4:
                tier = 'boss' if L == 8 else ('boss' if L == 4 and False else 'elite')
            elif i >= n - max(1, ELITE_ROWS[L] // 2):
                tier = 'elite'
            pool_l = layer_enemy_pool(raw, L)
            e = rng.choice(pool_l)
            rounds, taken = simulate_fight(rng, e)
            if tier != 'normal':
                taken *= 1.4 if tier == 'elite' else 1.6   # 精英/boss 数值更大的粗乘数（声明在局限）
            fights_total += 1
            taken_total += taken
            hp -= taken * BLOCK_MITIGATION   # 格挡减伤（校准自 H11）
            gold += gold_for_fight(rng, tier)
            # 奖励三选一
            main = max(owned.items(), key=lambda kv: kv[1])[0]
            shown = show_three(rng, pool, owned, main, affinity)
            taken_card = pick_card(rng, shown, owned, target_vein=main)
            for v in (taken_card.get('veins') or []):
                owned[v] += 1
            # 死亡判定
            if hp <= 0:
                dead_at = L
                break
        if dead_at:
            break
        # 事件
        if rng.random() < EVENT_P[L]:
            gold += avg_gold_ev * 0.6
            hp -= avg_dmg_ev * 0.3          # 事件也有伤害面
            hp += avg_heal_ev * 0.5
            if rng.random() < p_card:
                # 事件给牌：纯随机不加权（T400 §2.3）
                cls_pool = [c for c in pool]
                c = rng.choice(cls_pool)
                for v in (c.get('veins') or []):
                    owned[v] += 1
        # 商店（简单策略：先回血后买卡）
        if L in SHOPS:
            if hp < 0.6 * PARAMS['HP'][cls] and gold >= 60:
                gold -= 60
                hp += 0.35 * PARAMS['HP'][cls]
            elif gold >= 75:
                gold -= 75
                c = rng.choice(pool)
                for v in (c.get('veins') or []):
                    owned[v] += 1
        # boss 奖励金
        if L in BOSS_LAYER and L == 8:
            pass
    if dead_at:
        outcomes['死'] += 1
        death_layer[dead_at] += 1
        per_class[cls]['死'] += 1
    else:
        mx = max(owned.values())
        vein_max_end[mx] += 1
        if mx >= 5:
            outcomes['成型'] += 1
            per_class[cls]['成型'] += 1
        else:
            outcomes['散牌'] += 1
            per_class[cls]['散牌'] += 1
        total_fights_list.append(fights_total)
        deck_end.append(sum(owned.values()))

buf = []
buf.append('# H14 · 整局抽卡序列模拟（200 局）')
buf.append('')
buf.append('> **假设**：① 四角色各 50 局；战斗承伤=simulate_fight（裸吃口径），精英 ×1.4 / boss ×1.6 粗乘数（声明：精英/boss 数值更大的近似）；')
buf.append('> ② 奖励=主脉加权三选一+贪心拿牌（同 H01）；事件按 T512 概率触发，金/血/牌用 RAW 实测均值；商店策略=血 <60%% 先回血（60 金）否则买卡（75 金）；')
buf.append('> ③ 逐场扣血=承伤 × 格挡减伤 0.25（**校准自 H11 的贪心格挡实测**，非裸吃——首版裸吃口径 100%% 死亡、记账 bug 各一次，均已修）；事件/商店回血回充；成型=任一脉 ≥5 张；散牌=活着但 max<5。')
buf.append('> **局限**：不模拟格挡决策（H11 证明贪心格挡能省大量血——本模型死亡率远高于真实）；不模拟升级/遗物加成/共振层反应/双世界；精英 boss 承伤乘数是粗估。')
buf.append('')
buf.append('## 结局分布（%d 局，seed=%d）' % (N_PER_CLASS * 4, SEED))
buf.append('')
buf.append('| 结局 | 局数 | 占比 |')
buf.append('|---|---|---|')
for k in ['成型', '散牌', '死']:
    buf.append('| %s | %d | %.0f%% |' % (k, outcomes[k], 100 * outcomes[k] / (N_PER_CLASS * 4)))
buf.append('')
buf.append('| 死亡层 | 局数 |')
buf.append('|---|---|')
for L in sorted(death_layer):
    buf.append('| L%d | %d |' % (L, death_layer[L]))
buf.append('')
buf.append('## 分角色结局')
buf.append('')
buf.append('| 角色 | 成型 | 散牌 | 死 |')
buf.append('|---|---|---|---|')
for cls in ['diver', 'tremor', 'anmin', 'cangmin']:
    c = per_class[cls]
    buf.append('| %s | %d | %d | %d |' % (CN_CLASS[cls], c['成型'], c['散牌'], c['死']))
buf.append('')
buf.append('## 判断')
buf.append('')
buf.append('1. **死亡率是裸吃口径的上界**——真实玩家有格挡（H11 证明初始卡组贪心格挡 L3 每场只掉 0.6-2.8 血），真实死亡率会显著低于本表；本表的价值在**相对结构**：死亡集中在哪一层、谁的死亡率高。')
buf.append('2. 散牌率=活着但 max 脉 <5 的占比——T400 关心的「散牌局」风险量化；注意本模型玩家策略是「无脑拿主脉」，真人的多样拿牌会让散牌率更高还是更低取决于目标定义。')
buf.append('3. 拿牌通道的成型率见 H04（单脉 5 张中位场数）——本篇是「全流程版」，把死亡/事件/商店都放进来了。')
buf.append('')
buf.append('## 复算')
buf.append('')
buf.append('`python tools/sim/sim_full_run.py`（N_PER_CLASS/SEED 在顶部；策略分支在 run 循环内）。')
OUT.write_text('\n'.join(buf) + '\n', encoding='utf-8')
import io as _io
sys.stdout = _io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
print('outcomes', dict(outcomes), '| death layers', dict(death_layer))
print('per class', {CN_CLASS[k]: dict(v) for k, v in per_class.items()})
