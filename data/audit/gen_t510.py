# -*- coding: utf-8 -*-
"""T510 敌人里的「必躲」→ docs/design/enemy_avoid.md

性价比模型（写死可复算）：
  收益侧：普通/精英/boss 的奖励差异见 web 引擎（普通=金 20~40+拿牌；精英=拿牌+遗物三选一；
          boss=必给遗物+金 50~80）。同一档内收益与敌人强弱无关——所以「血厚攻高」的普通敌人=亏。
  成本侧：期望承伤 = 平均每回合攻击 × 期望回合数；
          期望回合数 = ceil(平均血量 / 玩家 DPS)，玩家 DPS=15/回合（4 能量、平均费 1.09 的粗估，与队列其他任务同一口径）；
          平均每回合攻击 = 攻击意图均值（含全部 phases，忽略 defend/buff 回合的零伤害——保守）。
  必躲线：期望承伤 ≥ 20 且档位=普通（拿同样的奖励却要多挨 20+ 血）。
  精英/boss 不参加必躲（收益不同不可比），但给「值得打」参考线：期望承伤 ≤ 遗物期望价值。

用法：python data/audit/gen_t510.py
"""
import io, sys, json, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_common import GAME

OUT = GAME / 'docs' / 'design' / 'enemy_avoid.md'
RAW = json.load(open(GAME / 'data' / 'audit' / 'raw_all.json', encoding='utf-8'))
DPS = 15
POOL = [('enemies', '通用'), ('anminEnemies', '维护者'), ('cngEnemies', '疯先知')]
CN_TIER = {'normal': '普通', 'elite': '精英', 'boss': 'boss'}

def parse_hp(s):
    s = str(s)
    if '-' in s:
        a, b = s.split('-')
        return (float(a) + float(b)) / 2
    return float(s)

def collect(e):
    its = list(e.get('intent_pattern') or [])
    for ph in e.get('phases') or []:
        its.extend(ph.get('intent_pattern') or [])
    return its

def metrics(e):
    its = collect(e)
    atks = [i.get('value') or 0 for i in its if i.get('type') == 'attack']
    avg_atk = sum(atks) / len(atks) if atks else 0
    hp = parse_hp(e['hp'])
    rounds = math.ceil(hp / DPS)
    return hp, avg_atk, rounds, avg_atk * rounds

rows = []
for pk, pn in POOL:
    for e in RAW[pk]:
        hp, avg_atk, rounds, dmg = metrics(e)
        rows.append((e, pn, hp, avg_atk, rounds, dmg))

avoid = [r for r in rows if r[0]['tier'] == 'normal' and r[5] >= 20]
avoid.sort(key=lambda r: -r[5])

buf = io.StringIO()
buf.write('# T510 · 敌人里的「必躲」\n\n')
buf.write('> 模型：期望承伤 = 平均攻击 × ceil(平均血 / 玩家 DPS 15)。普通敌人奖励固定（金 20~40 + 拿牌三选一，与强弱无关），')
buf.write('所以「多挨的血」全是净亏。**必躲线 = 期望承伤 ≥ 20 的普通敌**。复算：`python data/audit/gen_t510.py`。\n\n')

buf.write('## 必躲清单（%d 只普通敌）\n\n' % len(avoid))
buf.write('| id | 名字 | 层 | 池 | 血量 | 平均攻击 | 期望回合 | 期望承伤 | 为什么躲 |\n|---|---|---|---|---|---|---|---|---|\n')
for e, pn, hp, avg_atk, rounds, dmg in avoid:
    why = '同样的奖励（20~40 金+拿牌），比同层普通敌多挨 %d 点' % round(dmg)
    buf.write('| %s | %s | %s | %s | %s | %.1f | %d | %d | %s |\n' % (
        e['id'], e['name'], e['layer'], pn, e['hp'], avg_atk, rounds, round(dmg), why))

buf.write('\n## 对照：全普通敌期望承伤分布\n\n')
normals = [r for r in rows if r[0]['tier'] == 'normal']
vals = sorted(r[5] for r in normals)
import statistics
buf.write('- 普通敌共 %d 只；期望承伤中位数 %.0f、P75 %.0f、最高 %.0f。\n' % (
    len(vals), statistics.median(vals), vals[int(len(vals)*0.75)], vals[-1]))
buf.write('- 必躲线 20 = P75 上方。躲掉必躲清单里的 %d 只 ≈ 每层少挨一次大额损耗。\n\n' % len(avoid))

buf.write('## 精英/boss 的「值得打」参考\n\n')
buf.write('精英/普通收益结构不同（精英=拿牌+遗物），不进必躲表；只提醒：')
eli = sorted([r for r in rows if r[0]['tier'] == 'elite'], key=lambda r: -r[5])
buf.write('期望承伤最高的三只精英是 %s——打它们之前先把血线抬起来。\n\n' % '、'.join(
    '`%s` %s（%d 承伤）' % (e['id'], e['name'], round(d)) for e, pn, hp, a, rd, d in eli[:3]))

buf.write('\n## 模型说明（复算用）\n\n')
buf.write('1. 玩家 DPS=15/回合：4 能量 × 平均费 1.09 ≈ 3.7 张 × 平均 4~5 伤/张 的粗估，与队列内其他任务同口径。\n')
buf.write('2. 平均攻击只取 attack 意图（defend/buff 回合按 0 伤害摊进均值，偏保守——实际承伤更高）。\n')
buf.write('3. 收益侧数据来自 `web/index.html` finishCombat/nextReward（普通 20~40 金+拿牌；精英+遗物；boss 必给遗物+50~80 金）。\n')
buf.write('4. 必躲线 20 = 承伤分布 P75 上方的整数线；非实测结论，是模型口径。\n')

OUT.write_text(buf.getvalue(), encoding='utf-8')
print('written', OUT, '| avoid', len(avoid), 'of', len(normals), 'normals; median', statistics.median(vals))
