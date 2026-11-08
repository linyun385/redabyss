# -*- coding: utf-8 -*-
"""H08 常见组合期望伤害 → docs/design/sim_combo_damage.md
20 组两卡组合的单回合期望伤害（4 能量内同回合打出）。
模型：伤害=Σ(damage×hits)（力量 0 基线；多段按次数）；费用和 ≤4 才算同回合可打。
组合选自 T513 natural_combos 的伤害类 + 三组基准对照。
可复算：python tools/sim/sim_combo_damage.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from simlib import GAME, CN_VEIN, load_cards

OUT = GAME / 'docs' / 'design' / 'sim_combo_damage.md'
cards = load_cards()
C = {c['id']: c for pool in cards.values() for c in pool}

def dmg(c):
    e = c.get('effect') or {}
    return (e.get('damage') or 0) * (e.get('hits') or 1)

def cost(c):
    return c.get('energy', 0)

# 20 组（伤害向；标注来源）
PAIRS = [
 ('dive_0020', 'dive_0024', 'T513 #12 力量+钻探平台'),      # 力量2 与多段：力量×3 段生效（引擎：dmgEach 含 strength，每段都加）
 ('dive_0020', 'dive_0002', 'T513 #12 力量+聚能枪'),
 ('trem_0044', 'trem_0069', 'T513 #12 封忆+新碑'),
 ('dive_0022', 'trem_0034', 'T513(改) 双破防直伤'),          # 两个大直伤同回合
 ('dive_0012', 'dive_0002', '基准：轨道炮+聚能枪'),
 ('dive_0024', 'dive_0012', '基准：双斩杀位'),
 ('trem_0010', 'trem_0004', '基准：三震+回响'),
 ('cng_0038', 'cng_0040', '基准：震喉+墟语'),
 ('anm_0002', 'anm_0014', '基准：维护者双直伤'),
 ('dive_0033', 'dive_0034', 'T513 #6 圣火+焚烧（灼烧另计）'),
 ('trem_0023', 'trem_0080', 'T513 #6 沸息+长夜'),
 ('dive_0026', 'dive_0014', 'T513 #2 装药+探测器（共振循环）'),
 ('dive_0046', 'trem_0002', 'T513 #1 深部震源+听震'),
 ('dive_0011', 'dive_0046', 'T513(新7) 辐射弹共振回流+深部震源'),
 ('trem_0034', 'trem_0023', '断流+沸息（共振消耗组合）'),
 ('dive_0054', 'dive_0001', 'T513(超载) 聚能超载+透镜润滑'),
 ('u_0012', 'u_0008', '通用双输出'),
 ('u_0006', 'u_0003', '通用：风险合同+虹吸管'),
 ('anm_0007', 'anm_0028', '基准：维护者螺栓+注销'),
 ('cng_0037', 'cng_0034', '基准：影语+火母怀抱'),
]
rows = []
for a, b, src in PAIRS:
    ca, cb = C[a], C[b]
    total_cost = cost(ca) + cost(cb)
    same_turn = total_cost <= 4
    # 力量组合特殊：dive_0020/trem_0044 力量2 → 另一张多段/单段伤害 +2×段数
    d = dmg(ca) + dmg(cb)
    strength_bonus = 0
    for x, y in ((ca, cb), (cb, ca)):
        for s in (x.get('effect') or {}).get('special') or []:
            if isinstance(s, dict) and s.get('code') == 'strength' and (y.get('effect') or {}).get('damage'):
                strength_bonus += (s.get('value', 1)) * ((y['effect'].get('hits') or 1))
    if strength_bonus:
        d += strength_bonus
    burn = sum((s.get('value') or 0) for x in (ca, cb) for s in (x.get('effect') or {}).get('special') or []
               if isinstance(s, dict) and s.get('code') == 'burn')
    rows.append((d, a, b, src, total_cost, same_turn, burn))
rows.sort(reverse=True)

buf = []
buf.append('# H08 · 常见组合期望伤害（单回合，4 能量）')
buf.append('')
buf.append('> **假设**：① 力量 0 基线（不带成长）；伤害=Σ(damage×hits)；② 力量牌的组合按引擎语义给另一张的每段 +力量值（core.js:463 dmgEach 含 buffs.strength——每段都吃）；')
buf.append('> ③ 同回合=费用和 ≤4；④ 灼烧单列不进直伤（覆盖语义下按施加值列）。')
buf.append('> **局限**：不含格挡优先的机会成本（同回合打伤害=不挡）；不含凝视/共振门槛的达成成本；「期望」实为确定值——无随机段（本池无随机伤害）。')
buf.append('')
buf.append('| 排名 | 组合 | 来源 | 费用和 | 同回合？ | 单回合伤害 | 灼烧附加 |')
buf.append('|---|---|---|---|---|---|---|')
for i, (d, a, b, src, tc, st, burn) in enumerate(rows, 1):
    buf.append('| %d | %s + %s | %s | %d | %s | **%d** | %s |' % (
        i, C[a]['name'], C[b]['name'], src, tc, '✓' if st else '✗（%d 费，要两回合）' % tc, d, ('灼烧 %d' % burn) if burn else '—'))
buf.append('')
buf.append('## 结论')
buf.append('')
best, worst = rows[0], rows[-1]
buf.append('1. **效率最高**：%s + %s（%d 伤/%d 费=%.1f 伤/费）——力量对多段的加成是全池最强乘区（每段都吃）。' % (
    C[best[1]]['name'], C[best[2]]['name'], best[0], best[4], best[0] / max(1, best[4])))
buf.append('2. **效率最低**：%s + %s（%d 伤/%d 费=%.1f 伤/费）——高费组合的节奏代价明显。' % (
    C[worst[1]]['name'], C[worst[2]]['name'], worst[0], worst[4], worst[0] / max(1, worst[4])))
per_eff = [(d / max(1, tc), a, b, st) for d, a, b, src, tc, st, burn in rows]
per_eff.sort(reverse=True)
buf.append('3. 伤/费比 Top3：%s。' % '、'.join('%s+%s（%.1f）' % (C[a]['name'], C[b]['name'], r) for r, a, b, st in per_eff[:3]))
buf.append('4. 力量+多段（组合 #1）以 %.0f 伤领跑——**多段卡的价值 = 3 × 其他直伤卡**（力量乘区每段生效），这解释了钻探平台为什么被 T504 标「低稀强」。' % rows[0][0])
buf.append('')
buf.append('## 复算')
buf.append('')
buf.append('`python tools/sim/sim_combo_damage.py`（PAIRS 表在顶部，增删组合改那里）。')
OUT.write_text('\n'.join(buf) + '\n', encoding='utf-8')
import io as _io
sys.stdout = _io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
for d, a, b, src, tc, st, burn in rows[:5]:
    print(d, C[a]['name'], '+', C[b]['name'], 'cost', tc)
