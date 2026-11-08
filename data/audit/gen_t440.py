# -*- coding: utf-8 -*-
"""T440 敌人全表 → docs/design/enemy_table.md

每只敌人一行：id/名字/层/等级/血量(区间)/攻击数值(每次意图的值)/意图序列(按顺序)/垫底机制。
垫底机制 = 数据里的特殊机制字段：phases(多阶段)、pierce(穿透)、mirror(复刻)、
drain_discard(抽弃牌攻击)、debuff status(steal/gift/weak/burn/poison)、eco(生态副池标记)。
末尾按层统计：每层多少只、平均血量(取区间中值)、最高攻击。
复算：python data/audit/gen_t440.py

用法：python data/audit/gen_t440.py
"""
import io, sys, json, statistics
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_common import GAME

OUT = GAME / 'docs' / 'design' / 'enemy_table.md'
RAW = json.load(open(GAME / 'data' / 'audit' / 'raw_all.json', encoding='utf-8'))
POOL = [('enemies', '通用'), ('anminEnemies', '维护者'), ('cngEnemies', '疯先知')]
CN_TIER = {'normal': '普通', 'elite': '精英', 'boss': 'boss'}

def special_mechs(e):
    ms = []
    if e.get('phases'):
        ms.append('phases×%d' % len(e['phases']))
    its = list(e.get('intent_pattern') or [])
    for ph in e.get('phases') or []:
        its.extend(ph.get('intent_pattern') or [])
    if any(i.get('pierce') for i in its):
        ms.append('穿透')
    if any(i.get('mirror') for i in its):
        ms.append('复刻')
    if any(i.get('drain_discard') for i in its):
        ms.append('抽弃牌')
    sts = {i.get('status') for i in its if i.get('type') == 'debuff' and i.get('status')}
    ms += ['debuff:' + s for s in sorted(sts)]
    if e.get('eco'):
        ms.append('副池:' + e['eco'])
    if e.get('traits'):
        ms.append('traits:' + json.dumps(e['traits'], ensure_ascii=False))
    return '、'.join(ms) if ms else '—'

def seq(e):
    out = []
    for it in e.get('intent_pattern') or []:
        s = {'attack': '攻', 'defend': '防', 'buff': '增益', 'debuff': '减益'}.get(it.get('type'), it.get('type'))
        s += str(it.get('value', ''))
        if it.get('times'):
            s += '×%d' % it['times']
        out.append(s)
    return ' → '.join(out) if out else '—'

def hp_mid(s):
    s = str(s)
    if '-' in s:
        a, b = s.split('-')
        return (float(a) + float(b)) / 2
    return float(s)

def max_atk(e):
    its = list(e.get('intent_pattern') or [])
    for ph in e.get('phases') or []:
        its.extend(ph.get('intent_pattern') or [])
    return max([i.get('value') or 0 for i in its if i.get('type') == 'attack'] + [0])

allrows = []
for pk, pn in POOL:
    for e in RAW[pk]:
        allrows.append((e, pn))

buf = io.StringIO()
buf.write('# T440 · 敌人全表\n\n')
buf.write('> 数据源：`data/audit/raw_all.json`（node 抽自 `web/index.html` 行 6401 `const RAW`）——')
buf.write('enemies 113 + anminEnemies 16 + cngEnemies 16 = **145 只**。\n')
buf.write('> 「垫底机制」列 = 数据里的特殊机制字段（phases/穿透/复刻/抽弃牌/debuff status/eco 副池标记）。\n')
buf.write('> 复算：`python data/audit/gen_t440.py`。\n\n')

for L in range(1, 9):
    rows = [r for r in allrows if r[0]['layer'] == L]
    buf.write('## 第 %d 层（%d 只）\n\n' % (L, len(rows)))
    buf.write('| id | 名字 | 等级 | 池 | 血量 | 攻击值 | 意图序列 | 垫底机制 |\n|---|---|---|---|---|---|---|---|\n')
    for e, pn in sorted(rows, key=lambda r: {'normal': 0, 'elite': 1, 'boss': 2}[r[0]['tier']]):
        atk = '/'.join(str(i.get('value')) for i in e.get('intent_pattern') or [] if i.get('type') == 'attack') or '—'
        buf.write('| %s | %s | %s | %s | %s | %s | %s | %s |\n' % (
            e['id'], e['name'], CN_TIER[e['tier']], pn, e['hp'], atk, seq(e), special_mechs(e)))
        if e.get('phases'):
            for pi, ph in enumerate(e['phases'], 1):
                ps = []
                for it in ph.get('intent_pattern') or []:
                    s = {'attack': '攻', 'defend': '防', 'buff': '增益', 'debuff': '减益'}.get(it.get('type'), it.get('type'))
                    s += str(it.get('value', ''))
                    if it.get('times'):
                        s += '×%d' % it['times']
                    ps.append(s)
                buf.write('| ^ | └ 阶段 %d（hp≥%s%%） | | | | | %s | |\n' % (
                    pi, int(ph.get('hp_above', 0) * 100), ' → '.join(ps)))
    buf.write('\n')

buf.write('## 按层统计\n\n')
buf.write('| 层 | 只数 | 普通/精英/boss | 平均血量(区间中值) | 最高单发攻击 |\n|---|---|---|---|---|\n')
for L in range(1, 9):
    rows = [r for r in allrows if r[0]['layer'] == L]
    hps = [hp_mid(r[0]['hp']) for r in rows]
    mas = [max_atk(r[0]) for r in rows]
    tc = {'normal': 0, 'elite': 0, 'boss': 0}
    for r in rows:
        tc[r[0]['tier']] += 1
    buf.write('| %d | %d | %d/%d/%d | %.1f | %d |\n' % (
        L, len(rows), tc['normal'], tc['elite'], tc['boss'],
        statistics.mean(hps) if hps else 0, max(mas) if mas else 0))
buf.write('\n合计 %d 只。\n' % len(allrows))
buf.write('\n### 复算\n\n`python data/audit/gen_t440.py`；血量中值 = 区间两端平均（单值按单值）；最高攻击含 phases 意图。\n')

OUT.write_text(buf.getvalue(), encoding='utf-8')
print('written', OUT, len(allrows), 'enemies')
