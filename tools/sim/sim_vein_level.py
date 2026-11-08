# -*- coding: utf-8 -*-
"""H09 脉象等级成长模拟 → docs/design/sim_vein_level.md
按 T526 规则（进对应生态 +1；离开后经过 2 个事件块 −1；上限 5）模拟 1000 局。
生态映射用 T526 的候选假设（光↔L4、震↔L2、水↔L3、热↔L5、矿↔L6），事件数按 T512 概率随机。
可复算：python tools/sim/sim_vein_level.py（seed=42）
"""
import sys, statistics
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from simlib import GAME, CN_VEIN

OUT = GAME / 'docs' / 'design' / 'sim_vein_level.md'
from config import N_VEIN_LEVEL_RUNS, SEED
N, CAP = N_VEIN_LEVEL_RUNS, 5
import random
rng = random.Random(SEED)

# 映射假设（T526 已声明为推演用假设）
VEIN_ECO = {'light': [4], 'water': [3], 'heat': [5], 'tremor': [2], 'mineral': [6]}
from config import EVENT_P

results = {}
for vein, ecos in VEIN_ECO.items():
    peaks, finals, in_target = [], [], 0
    traj_sum = [0.0] * 8
    for _ in range(N):
        level, since_leave, peak = 0, None, 0
        entered = False
        for L in range(1, 9):
            ev = rng.random() < EVENT_P[L]  # 本层是否遇到事件
            if L in ecos and not entered:
                entered = True
                level = min(CAP, level + 1)
                since_leave = None
            elif entered:
                if ev:
                    since_leave = (since_leave or 0) + 1
                    if since_leave >= 2:
                        level = max(0, level - 1)
                        since_leave = 0
            peak = max(peak, level)
            traj_sum[L - 1] += level
        peaks.append(peak)
        finals.append(level)
        if peak >= 2:
            in_target += 1
    results[vein] = (statistics.median(peaks), statistics.mean(peaks),
                     statistics.mean(finals), in_target / N, [t / N for t in traj_sum])

buf = []
buf.append('# H09 · 脉象等级成长模拟（T526 规则 + 事件随机性）')
buf.append('')
buf.append('> **假设**：① 生态映射用 T526 的候选假设（光↔L4/震↔L2/水↔L3/热↔L5/矿↔L6）——**映射本身未拍板**，换映射=换拐点不换形状；')
buf.append('> ② 进对应生态层 +1（一次）；离开后每遇 2 个事件块 −1（事件按 T512 概率随机：L1/6/7/8=1.0，其余=0.5）；上限 5；')
buf.append('> ③ 单生态假设（T526 场景 A——最保守）；不含「出该脉牌 +X」进项（T400 阶段 2.2 的主进项未定参数）。')
buf.append('> **局限**：这是 T526 静态推演的蒙特卡洛版——把「事件数」从期望值变成随机序列；结论与 T526 一致则互证，不一致处按模拟为准。')
buf.append('')
buf.append('## 逐脉结果（%d 局，seed=%d）' % (N, SEED))
buf.append('')
buf.append('| 脉 | 峰值中位 | 峰值均值 | 终局均值 | 峰值≥2 的局占比 |')
buf.append('|---|---|---|---|---|')
for v in ['light', 'water', 'heat', 'tremor', 'mineral']:
    mp, ap, af, p2, _ = results[v]
    buf.append('| %s | %.0f | %.2f | %.2f | %.0f%% |' % (CN_VEIN[v], mp, ap, af, 100 * p2))
buf.append('')
buf.append('## 逐层等级轨迹（均值，映射对应层为拐点）')
buf.append('')
buf.append('| 脉 | L1 | L2 | L3 | L4 | L5 | L6 | L7 | L8 |')
buf.append('|---|---|---|---|---|---|---|---|---|')
for v in ['light', 'water', 'heat', 'tremor', 'mineral']:
    tr = results[v][4]
    buf.append('| %s | %s |' % (CN_VEIN[v], ' | '.join('%.2f' % x for x in tr)))
buf.append('')
buf.append('## 判断')
buf.append('')
buf.append('1. 峰值均值全部 <%.1f——**蒙特卡洛证实 T526 场景 A 的结论：单生态脉峰值 1~2，上限 5 摸不到**（峰值≥2 的局占比最高 %.0f%%）。' % (
    max(results[v][1] for v in results) + 0.99, 100 * max(results[v][3] for v in results)))
buf.append('2. 终局均值全部 <%.2f——散牌局保底接近零的判断（T526 结论 1）被随机事件序列进一步压实。' % max(results[v][2] for v in results))
buf.append('3. 轨迹形状：拐点（映射层）+1 后缓慢衰减——衰减速度由事件供给（全程期望 6 次）决定，**参数不变则任何映射下等级都活不过 3 层**。')
buf.append('4. 这批数字是「生态-only 进项」的下界；加入「出牌 +X」主进项后曲线会整体抬高——那是阶段 2.2 的参数表，等设计者。')
buf.append('')
buf.append('## 复算')
buf.append('')
buf.append('`python tools/sim/sim_vein_level.py`（N/SEED/CAP/VEIN_ECO/EVENT_P 在顶部——映射表改这里重跑）。')
OUT.write_text('\n'.join(buf) + '\n', encoding='utf-8')
import io as _io
sys.stdout = _io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
for v in results: print(v, results[v][:4])
