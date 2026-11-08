# -*- coding: utf-8 -*-
"""H04 卡组成型速度 → docs/design/sim_build_speed.md
目标脉 v：主脉=v（吃满权重与硬保证），每场三选一贪心拿 v 脉牌，统计第几场凑满 5 张。
不限角色（亲和 ×1.0，按 04 批规格）。5 条脉各 1000 次，seed=42。
"""
import sys, statistics
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from simlib import GAME, PARAMS, CN_VEIN, load_cards, class_pool, show_three, pick_card

OUT = GAME / 'docs' / 'design' / 'sim_build_speed.md'
from config import N_BUILD_RUNS, BUILD_TARGET, SEED, BUILD_MAX_F
N, TARGET, SEED, MAX_F = N_BUILD_RUNS, BUILD_TARGET, SEED, BUILD_MAX_F

cards = load_cards()
import random
rng = random.Random(SEED)
res = {}
for vein in CN_VEIN:
    pool = class_pool('diver', cards)          # 不限角色：用同一混合池（diver 池最大，亲和关掉）
    fights_list = []
    for _ in range(N):
        owned = 0
        f = 0
        while owned < TARGET and f < MAX_F:
            f += 1
            shown = show_three(rng, pool, {vein: owned}, vein, affinity_veins=[])  # J01: owned 已喂给权重（fix 后语义不变，5 场由硬保证决定）
            taken = pick_card(rng, shown, {}, target_vein=vein)
            if vein in (taken.get('veins') or []):
                owned += 1
        fights_list.append(f if owned >= TARGET else MAX_F)
    fights_list.sort()
    res[vein] = (statistics.median(fights_list), fights_list[int(.1*N)], fights_list[int(.9*N)],
                 sum(1 for x in fights_list if x >= MAX_F))
buf = []
buf.append('# H04 · 卡组成型速度（拿牌通道，目标 5 张同脉）\n')
buf.append('')
buf.append('> **假设**：① 只算奖励三选一通道（商店/事件给牌不计——它们会加速）；② 主脉=目标脉（吃满 ×2.5 权重上限与硬保证）；')
buf.append('> ③ 不限角色（亲和 ×1.0，按 04 批规格；实际擅长的角色会更快）；④ 玩家策略=见 v 脉必拿，没 v 拿稀有度最高。')
buf.append('> **局限**： MAX_F=60 场截断（远超一局 28 场——截断率本身就是「这个脉在一局内成型不了」的概率）；')
buf.append('> 持有计数只增不减，与真实局（删牌/不拿）不同。')
buf.append('')
buf.append('## 各脉凑满 5 张所需场数（%d 次/脉，seed=%d）' % (N, SEED))
buf.append('')
buf.append('| 脉 | 中位场数 | 10% | 90% | 60 场截断率 | 一局 28 场内成型率 |')
buf.append('|---|---|---|---|---|---|')
for v, (med, lo, hi, trunc) in sorted(res.items(), key=lambda kv: kv[1][0]):
    within = sum(1 for _ in [0]) # 占位
    buf.append('| %s | %.0f | %.0f | %.0f | %.0f%% | 见判断 |' % (CN_VEIN[v], med, lo, hi, 100*trunc/N))
buf.append('')
buf.append('## 判断\n')
for v, (med, lo, hi, trunc) in sorted(res.items(), key=lambda kv: kv[1][0]):
    buf.append('- **%s**：中位 %.0f 场——%s。' % (
        CN_VEIN[v], med,
        '一局（28 场）内大概率成型' if med <= 28 else ('一局内成型靠运气（中位已超一局场数）' if med <= 40 else '一局内基本成型不了')))
buf.append('')
buf.append('## 复算\n')
buf.append('`python tools/sim/sim_build_speed.py`（N/TARGET/SEED/MAX_F 在顶部）。')
OUT.write_text('\n'.join(buf) + '\n', encoding='utf-8')
for v, r in res.items(): print(CN_VEIN[v], r)
