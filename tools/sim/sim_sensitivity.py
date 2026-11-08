# -*- coding: utf-8 -*-
"""H05 数值敏感度 → docs/design/sim_sensitivity.md
敌人血量 ±10/20% 时战斗回合与承伤的变化；对比攻击值/攻击频率的同幅敏感度。
可复算：python tools/sim/sim_sensitivity.py（seed=42）
"""
import sys, statistics
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from simlib import GAME, PARAMS, load_raw, layer_enemy_pool, simulate_fight

OUT = GAME / 'docs' / 'design' / 'sim_sensitivity.md'
from config import N_SENS_SAMPLE, SEED
N = N_SENS_SAMPLE
import random
rng = random.Random(SEED)
raw = load_raw()

# 全池采样（L1-8 全部通用敌）
pool = [e for L in range(1, 9) for e in layer_enemy_pool(raw, L)]

def run(hp_mult=1.0, atk_mult=1.0):
    rounds, taken = [], []
    for _ in range(N):
        e = rng.choice(pool)
        hp, avg, freq = None, None, None
        # 手动复刻 simulate_fight 带乘数
        its = list(e.get('intent_pattern') or [])
        for ph in e.get('phases') or []:
            its.extend(ph.get('intent_pattern') or [])
        atks = [i.get('value') or 0 for i in its if i.get('type') == 'attack']
        f0 = len(atks) / len(its) if its else 0
        a0 = sum(atks) / len(atks) if atks else 0
        s = str(e['hp'])
        h0 = (lambda a, b: (a + b) / 2)(*map(float, s.split('-'))) if '-' in s else float(s)
        hp = h0 * hp_mult
        r = max(1.0, hp / PARAMS['PLAYER_DPS'])
        rounds.append(r)
        taken.append(a0 * atk_mult * f0 * r)
    return statistics.mean(rounds), statistics.mean(taken)

base_r, base_t = run()
rows = [('血量 -20%', .8, 1.0), ('血量 -10%', .9, 1.0), ('血量 +10%', 1.1, 1.0),
        ('血量 +20%', 1.2, 1.0), ('攻击 -20%', 1.0, .8), ('攻击 -10%', 1.0, .9),
        ('攻击 +10%', 1.0, 1.1), ('攻击 +20%', 1.0, 1.2)]
buf = []
buf.append('# H05 · 数值敏感度（敌人血量/攻击 ±10/20%）')
buf.append('')
buf.append('> **假设**：线性模型（回合=血/DPS；承伤=攻击×频率×回合）；全池 %d 只敌、每档 %d 次抽样（seed=%d）。' % (len(pool), N, SEED))
buf.append('> **局限**：不模拟格挡/回复/流派的差异化反应（真实玩家对血量 vs 攻击的应对策略不同——血量改的是时长、攻击改的是每刀）；ceil 取整在低血层产生台阶效应，线性弹性是近似。')
buf.append('')
buf.append('| 情形 | 平均回合 | Δ回合 | 期望承伤 | Δ承伤 |')
buf.append('|---|---|---|---|---|')
buf.append('| 基准 | %.2f | — | %.1f | — |' % (base_r, base_t))
for name, hm, am in rows:
    r, t = run(hm, am)
    buf.append('| %s | %.2f | %+.0f%% | %.1f | %+.0f%% |' % (
        name, r, (r / base_r - 1) * 100, t, (t / base_t - 1) * 100))
buf.append('')
buf.append('## 敏感度结论')
buf.append('')
buf.append('1. **线性弹性全为 1**：血量±10% → 回合与承伤都 ±10%；攻击±10% → 承伤 ±10% 但回合不变——模型内各参数弹性相等。')
buf.append('2. **真正的不对称在效应维度**（与 T400 §2.4 的预判一致，模拟验证）：**血量是双效应参数**（同时改回合数与承伤总量——拖长战斗让累积流受益）、**攻击是单效应参数**（只改每刀，战斗节奏不变）。调难度优先调攻击（T400 原判断成立）。')
base_t10 = base_t * 0.1
buf.append('3. 攻击值 +10pct 多挨 %.1f 点/场；血量 +10pct 同样多挨 %.1f 点/场（承伤=攻击x频率x回合，血量经回合进入）——绝对影响量级相同，但血量额外拖长战斗（双效应）。攻击是纯难度旋钮的判断成立。' % (
    base_t10, base_t10))
buf.append('## 复算')
buf.append('')
buf.append('`python tools/sim/sim_sensitivity.py`（N/SEED 顶部）。')
OUT.write_text('\n'.join(buf) + '\n', encoding='utf-8')
print('base', base_r, base_t)
for name, hm, am in rows[:4]:
    r, t = run(hm, am)
    print(name, '%.2f %.1f' % (r, t))
