# -*- coding: utf-8 -*-
"""T531 敌人攻击频率 → docs/design/attack_rate.md

每只敌人：攻击回合占比 = 攻击意图数/意图总数；平均单发伤害 = 攻击意图值均值；
每回合期望承伤 = 占比 × 均值（defend/buff 回合按 0 伤害，保守口径）。
按层聚合：普通/精英/boss 分列。复算：python data/audit/gen_t531.py

用法：python data/audit/gen_t531.py
"""
import io, sys, json, statistics
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_common import GAME

OUT = GAME / 'docs' / 'design' / 'attack_rate.md'
RAW = json.load(open(GAME / 'data' / 'audit' / 'raw_all.json', encoding='utf-8'))
POOL = [('enemies', '通用'), ('anminEnemies', '维护者'), ('cngEnemies', '疯先知')]
CN_TIER = {'normal': '普通', 'elite': '精英', 'boss': 'boss'}

def collect(e):
    its = list(e.get('intent_pattern') or [])
    for ph in e.get('phases') or []:
        its.extend(ph.get('intent_pattern') or [])
    return its

def metrics(e):
    its = collect(e)
    if not its:
        return 0, 0, 0
    atks = [i.get('value') or 0 for i in its if i.get('type') == 'attack']
    freq = len(atks) / len(its)
    avg = statistics.mean(atks) if atks else 0
    return freq, avg, freq * avg

by_layer = defaultdict(lambda: defaultdict(list))
buf = io.StringIO()
buf.write('# T531 · 敌人攻击频率（每回合期望承伤）\n\n')
buf.write('> 口径：攻击回合占比 = 攻击意图数 / 意图总数（含 phases 并集）；defend/buff 回合按 0 伤害摊入（保守）。')
buf.write('复算：`python data/audit/gen_t531.py`。\n\n')
buf.write('## 按层聚合\n\n')
buf.write('| 层 | 档 | 只数 | 攻击回合占比均值 | 平均单发 | 期望承伤/回合 |\n|---|---|---|---|---|---|\n')
for L in range(1, 9):
    for tier in ['normal', 'elite', 'boss']:
        ms = [metrics(e) for pk, pn in POOL for e in RAW[pk] if e['layer'] == L and e['tier'] == tier]
        if not ms:
            continue
        f = statistics.mean(m[0] for m in ms)
        a = statistics.mean(m[1] for m in ms)
        d = statistics.mean(m[2] for m in ms)
        buf.write('| %d | %s | %d | %.0f%% | %.1f | %.1f |\n' % (L, CN_TIER[tier], len(ms), f * 100, a, d))

buf.write('\n## 极值（哪只敌人最凶）\n\n')
rows = [(e, metrics(e)) for pk, _ in POOL for e in RAW[pk]]
rows.sort(key=lambda x: -x[1][2])
buf.write('| id | 名字 | 层 | 档 | 攻击占比 | 平均单发 | 期望承伤 |\n|---|---|---|---|---|---|---|\n')
for e, (f, a, d) in rows[:12]:
    buf.write('| %s | %s | %s | %s | %.0f%% | %.1f | %.1f |\n' % (
        e['id'], e['name'], e['layer'], CN_TIER[e['tier']], f * 100, a, d))

buf.write('\n## 全体分布\n\n')
allf = [m[0] for _, m in rows]
buf.write('- 145 只敌人攻击回合占比：中位 %.0f%%，最高 %.0f%%（%s），最低 %.0f%%。\n' % (
    statistics.median(allf) * 100, max(f for _, (f, a, d) in rows) * 100,
    max(rows, key=lambda x: x[1][0])[0]['name'], min(f for _, (f, a, d) in rows) * 100))
buf.write('- 只攻击不防御的敌人（占比 100%%）：%s。\n' % '、'.join(
    '`%s` %s' % (e['id'], e['name']) for e, (f, a, d) in rows if f >= 0.999) or '—')

buf.write('\n### 复算\n\n`python data/audit/gen_t531.py`；数据源 `data/audit/raw_all.json`。\n')

OUT.write_text(buf.getvalue(), encoding='utf-8')
print('written', OUT)
