# -*- coding: utf-8 -*-
"""H01 抽卡加权蒙特卡洛 → docs/design/sim_reward.md
按 T400 §2.3 公式模拟 1000 名玩家 × 20 场奖励三选一，统计主脉出现率（展示牌口径）。
可复算：python tools/sim/sim_reward.py（参数在 config.py）
"""
import sys, statistics
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from simlib import GAME, PARAMS, CN_VEIN, load_cards, class_pool, show_three, pick_card
from config import N_REWARD_PLAYERS as N_PLAYERS, N_REWARD_FIGHTS as N_FIGHTS, SEED

OUT = GAME / 'docs' / 'design' / 'sim_reward.md'

cards = load_cards()
import random
rng = random.Random(SEED)

VEINS_EN = ['light', 'water', 'heat', 'tremor', 'mineral']

main_rate_per_player = []
vein_shown = {v: 0 for v in VEINS_EN}
total_shown = 0
streak_info = {'would_trigger': 0}  # 核心卡保底：做不了（见报告），只统计「连续 3 次无主脉」的理论触发率

for p in range(N_PLAYERS):
    cls = ['diver', 'tremor', 'anmin', 'cangmin'][p % 4]
    affinity = PARAMS['AFFINITY'][cls]
    pool = class_pool(cls, cards)
    owned = {v: 0 for v in VEINS_EN}  # 英文键=卡牌 veins 键（键语言口径见 _SIM_BUGFAMILY.md P1）
    main_hits, shown_n = 0, 0
    no_main_streak = 0
    for f in range(N_FIGHTS):
        # 主脉=当前持有最多（平局取 affinity 第一条）
        main = max(owned.items(), key=lambda kv: (kv[1], 1 if kv[0] in affinity else 0))[0]
        shown = show_three(rng, pool, owned, main, affinity)
        shown_n += len(shown)
        hits = sum(1 for c in shown if main in (c.get('veins') or []))
        main_hits += hits
        for c in shown:
            for v in (c.get('veins') or []):
                vein_shown[v] += 1
        no_main_streak = no_main_streak + 1 if hits == 0 else 0
        if no_main_streak >= 3:
            streak_info['would_trigger'] += 1
            no_main_streak = 0
        taken = pick_card(rng, shown, owned, target_vein=main)
        for v in (taken.get('veins') or []):
            owned[v] += 1
    main_rate_per_player.append(main_hits / shown_n)
    total_shown += shown_n

rate = sum(main_rate_per_player) / len(main_rate_per_player)
lo = sorted(main_rate_per_player)[int(0.1 * len(main_rate_per_player))]
hi = sorted(main_rate_per_player)[int(0.9 * len(main_rate_per_player))]
ok = 0.45 <= rate <= 0.65
buf = []
buf.append('# H01 · 抽卡加权蒙特卡洛（奖励三选一）\n')
buf.append('')
buf.append('> **假设**：①「主脉出现率」= 三张展示牌中属于玩家主脉的占比（T400 §2.3 的验收口径）；主脉=当前持有最多的脉。')
buf.append('> ② 玩家拿牌策略=优先拿主脉（贪心）；③ 稀有度权重 6/3/1（special 按精良）；④ 擅长脉 ×1.3（四个角色轮转，每人 20 场）。')
buf.append('> **局限**：不模拟升级/核心卡/事件给牌（T400 规定事件不加权）；「持有该脉张数」按展示后玩家的实际拿牌更新，不含商店/事件来源。')
buf.append('> **做不了**：核心卡保底触发次数——**卡数据没有任何 core:true 字段**（T400 阶段 2.9 未实装），保底只能统计「连续 3 次奖励无主脉」的理论触发率，不能统计真核心卡触发。')
buf.append('')
buf.append('## 结果（seed=%d，%d 玩家 × %d 场，展示牌共 %d 张）' % (SEED, N_PLAYERS, N_FIGHTS, total_shown))
buf.append('')
buf.append('| 指标 | 值 | T400 目标 | 判定 |')
buf.append('|---|---|---|---|')
buf.append('| 主脉出现率（全体均值） | **%.1f%%** | 45~65%% | %s |' % (
    rate * 100, '落在区间内' if ok else '出界（实际值如上，不调参）'))
buf.append('| 玩家级 10%%/90%% 分位 | %.1f%% / %.1f%% | — | 个体差异带 |' % (lo * 100, hi * 100))
buf.append('| 「连续 3 次无主脉」理论触发 | %d 次 | — | 真核心卡保底的代理下界 |' % streak_info['would_trigger'])
buf.append('')
buf.append('## 各脉展示次数\n')
buf.append('| 脉 | 展示次数 | 占比 |\n|---|---|---|')
for v in VEINS_EN:
    buf.append('| %s | %d | %.1f%% |' % (CN_VEIN[v], vein_shown[v], 100 * vein_shown[v] / total_shown))
buf.append('')
buf.append('## 复算\n')
buf.append('`python tools/sim/sim_reward.py`（参数在 config.py：N_REWARD_PLAYERS/N_REWARD_FIGHTS/SEED）。模型=simlib.show_three（权重公式与硬保证逐条实现，I01 修复后接入加权采样）。')
OUT.write_text('\n'.join(buf) + '\n', encoding='utf-8')
import io as _io
sys.stdout = _io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
print('rate %.3f [%0.3f-%0.3f] streak-proxy %d' % (rate, lo, hi, streak_info['would_trigger']))
print('veins', {CN_VEIN[k]: v for k, v in vein_shown.items()})
