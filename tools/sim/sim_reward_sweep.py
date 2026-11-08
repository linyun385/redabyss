# -*- coding: utf-8 -*-
"""I01 主脉率参数扫描 → docs/design/_FIX_REWARD_RATE.md
四组对照（基线 + 三组调参）：VEIN_SCALE 0.35 / VEIN_CAP 8 / AFFINITY 1.5。
只改 simlib.PARAMS 的**数值**（monkey-patch），不动 simlib 逻辑；单脚本单 seed 独立重跑。
写 data/sim/sweep_raw.txt 原始输出（落盘备复核）。
"""
import sys, io, statistics
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from simlib import GAME, PARAMS, CN_VEIN, load_cards, class_pool, show_three, pick_card
import random

N_PLAYERS, N_FIGHTS, SEED = 1000, 20, 42

SCENARIOS = [
    ('基线（0.25 / cap6 / 1.3）', {}),
    ('① VEIN_SCALE 0.35', {'VEIN_SCALE': 0.35}),
    ('② VEIN_CAP 8', {'VEIN_CAP': 8}),
    ('③ AFFINITY 1.5', {'VEIN_AFFINITY': 1.5}),
    ('④ 组合：0.35 + 1.5', {'VEIN_SCALE': 0.35, 'VEIN_AFFINITY': 1.5}),
]

cards = load_cards()

def run_once():
    rng = random.Random(SEED)
    rates = []
    vein_shown = {v: 0 for v in CN_VEIN}
    total = 0
    for p in range(N_PLAYERS):
        cls = ['diver', 'tremor', 'anmin', 'cangmin'][p % 4]
        affinity = PARAMS['AFFINITY'][cls]
        pool = class_pool(cls, cards)
        owned = {v: 0 for v in ['light', 'water', 'heat', 'tremor', 'mineral']}  # 英文键修复（同 sim_reward）
        hits, shown_n = 0, 0
        for f in range(N_FIGHTS):
            main = max(owned.items(), key=lambda kv: (kv[1], 1 if kv[0] in affinity else 0))[0]
            shown = show_three(rng, pool, owned, main, affinity)
            shown_n += len(shown)
            hits += sum(1 for c in shown if main in (c.get('veins') or []))
            for c in shown:
                for v in (c.get('veins') or []):
                    vein_shown[v] += 1
            taken = pick_card(rng, shown, owned, target_vein=main)
            for v in (taken.get('veins') or []):
                owned[v] += 1
        rates.append(hits / shown_n)
        total += shown_n
    return sum(rates) / len(rates), sorted(rates)[int(.1 * N_PLAYERS)], sorted(rates)[int(.9 * N_PLAYERS)], vein_shown, total

raw_lines = []
buf = []
buf.append('# I01 · 主脉率为什么只有 41%——参数敏感度扫描')
buf.append('')
buf.append('> 方法：monkey-patch `simlib.PARAMS` 的数值（不动逻辑），每档独立重跑 sim_reward 的同款流程（1000 玩家 x 20 场，seed=42）。')
buf.append('> 基线=05 批实测 41.1%。目标=T400 §2.3 的 45~65%。所有数字为**估算**（模型口径见 sim_reward.md 假设段）。')
buf.append('')
buf.append('| 情形 | 主脉率 | 10/90 分位 | 达标（≥45%）？ |')
buf.append('|---|---|---|---|')
results = []
for name, patch in SCENARIOS:
    saved = {k: PARAMS[k] for k in patch}
    PARAMS.update(patch)
    rate, lo, hi, vein_shown, total = run_once()
    results.append((name, rate, lo, hi, dict(vein_shown), total))
    PARAMS.update(saved)  # 还原
    raw_lines.append('%s | rate=%.4f lo=%.4f hi=%.4f | veins=%s' % (name, rate, lo, hi, vein_shown))
    buf.append('| %s | **%.1f%%** | %.1f / %.1f | %s |' % (
        name, rate * 100, lo * 100, hi * 100, '✅' if rate >= 0.45 else '❌'))
buf.append('')
buf.append('## 各情形的脉曝光分布（占展示总数 %）')
buf.append('')
buf.append('| 情形 | ' + ' | '.join(CN_VEIN[v] for v in ['light', 'water', 'heat', 'tremor', 'mineral']) + ' |')
buf.append('|---|' + '---|' * 5)
for name, rate, lo, hi, vein_shown, total in results:
    buf.append('| %s | %s |' % (name, ' | '.join('%.1f%%' % (100 * vein_shown[v] / total) for v in ['light', 'water', 'heat', 'tremor', 'mineral'])))
buf.append('')
buf.append('## 判断：哪一组能推到 50%')
buf.append('')
best = max(results, key=lambda r: r[1])
buf.append('1. 单参数里最有效的是 **%s（%.1f%%）**；三组单参数' % (best[0], best[1] * 100))
for name, rate, *_ in results[1:4]:
    buf.append('   - %s：%.1f%%（较基线 %+.1fpp）' % (name, rate * 100, (rate - results[0][1]) * 100))
buf.append('2. 组合 ④（0.35+1.5）达 %.1f%%——要进 45~65 区间，单参数不够就上组合；但越高越挤压非主脉曝光（看脉分布表：主脉挤占的是谁的份额）。' % (results[4][1] * 100))
buf.append('3. 副作用检查：任何一档把主脉推上去，非主脉里的最弱者（水）曝光都进一步下降——**调权重的钱是从水里扣的**，水脉成型慢的问题（H04）会被放大。配套建议：调权重的同时补水脉池密度（两件事不是二选一）。')
buf.append('')
buf.append('## 复算')
buf.append('')
buf.append('`python tools/sim/sim_reward_sweep.py`（SCENARIOS 表在顶部；原始输出落盘 data/sim/sweep_raw.txt）。')
OUT = GAME / 'docs' / 'design' / '_FIX_REWARD_RATE.md'
OUT.write_text('\n'.join(buf) + '\n', encoding='utf-8')
raw_dir = GAME / 'data' / 'sim'
raw_dir.mkdir(exist_ok=True)
(raw_dir / 'sweep_raw.txt').write_text('\n'.join(raw_lines) + '\n', encoding='utf-8')
for r in results:
    print('%s %.3f (%.3f-%.3f)' % (r[0], r[1], r[2], r[3]))
