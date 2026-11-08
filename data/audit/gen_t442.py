# -*- coding: utf-8 -*-
"""T442 遗物全表 → docs/design/relic_table.md

每件一行：id/名字/稀有度/来源/效果一句话/偏向(脉+池)。
来源口径（数据只显式标 event；其余按引擎逻辑推）：
  source=='event' → 事件；rarity=='boss' → boss 奖励；其余 → 奖励池（精英三选一/商店/拆解随机）。
偏向 = 遗物自带 veins 标签（中文）+ 所属池（anrelic→维护者、cngrelic→疯先知、relic→通用）。
末尾统计：按来源、按稀有度。复算：python data/audit/gen_t442.py

用法：python data/audit/gen_t442.py
"""
import io, sys, json
from pathlib import Path
from collections import Counter, defaultdict
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_common import GAME, CN_VEIN

OUT = GAME / 'docs' / 'design' / 'relic_table.md'
RAW = json.load(open(GAME / 'data' / 'audit' / 'raw_all.json', encoding='utf-8'))
POOLS = [('relics', '通用'), ('anminRelics', '维护者'), ('cngRelics', '疯先知')]
CN_R = {'common': '普通', 'uncommon': '精良', 'rare': '稀有', 'boss': 'boss'}
CN_ACT = {'draw': '抽牌', 'heal': '回血', 'block': '格挡', 'maxhp': '生命上限',
          'resonance': '共振', 'gaze': '凝视'}

def effect_line(r):
    t = r.get('effect_text') or ''
    if t:
        return t
    ecs = r.get('effect_code') or []
    parts = []
    for ec in ecs:
        trig = {'combat_start': '开战时', 'turn_start': '每回合', 'run_start': '整局',
                'on_kill': '击杀时'}.get(ec.get('trigger'), ec.get('trigger'))
        act = CN_ACT.get(ec.get('action'), ec.get('action'))
        v = ec.get('value')
        s = '%s%s%s' % (trig, act, ('%+d' % v) if isinstance(v, (int, float)) else '')
        parts.append(s)
    return '；'.join(parts) or '—'

def source(r):
    if r.get('source') == 'event':
        return '事件'
    if r.get('rarity') == 'boss':
        return 'boss'
    return '奖励池'

def lean(r, pool):
    vs = ['%s脉' % CN_VEIN[v] for v in (r.get('veins') or [])]
    pool_cn = {'relics': '通用', 'anminRelics': '维护者', 'cngRelics': '疯先知'}[pool]
    return '、'.join(vs) if vs else '无脉标签', pool_cn

buf = io.StringIO()
buf.write('# T442 · 遗物全表\n\n')
buf.write('> 数据源：`data/audit/raw_all.json` relics(77)+anminRelics(15)+cngRelics(15) = **107 件**。\n')
buf.write('> 来源口径：数据显式标 `source=event` 的算「事件」（4 件）；`rarity=boss` 算「boss」（3 件）；')
buf.write('其余走引擎 `pickRelics` 奖励池（精英三选一/商店/拆解随机）。「偏向」= 自带 veins 标签 + 所属池。')
buf.write('复算：`python data/audit/gen_t442.py`。\n\n')

src_c = Counter(); rar_c = Counter(); vein_c = Counter()
for pk, pn in POOLS:
    buf.write('## %s池（%d 件）\n\n' % (pn, len(RAW[pk])))
    buf.write('| id | 名字 | 稀有度 | 来源 | 效果 | 偏向 |\n|---|---|---|---|---|---|\n')
    for r in RAW[pk]:
        vs, _ = lean(r, pk)
        vein_c['、'.join(vs)] += 1
        src_c[source(r)] += 1
        rar_c[r.get('rarity')] += 1
        buf.write('| %s | %s | %s | %s | %s | %s（%s） |\n' % (
            r['id'], r['name'], CN_R.get(r.get('rarity'), r.get('rarity')),
            source(r), effect_line(r), vs or '无脉', _))
    buf.write('\n')

buf.write('## 统计\n\n')
buf.write('### 按来源\n\n| 来源 | 件数 |\n|---|---|\n')
for k, n in src_c.most_common():
    buf.write('| %s | %d |\n' % (k, n))
buf.write('\n### 按稀有度\n\n| 稀有度 | 件数 |\n|---|---|\n')
for k in ['common', 'uncommon', 'rare', 'boss']:
    buf.write('| %s | %d |\n' % (CN_R[k], rar_c[k]))
buf.write('\n### 偏向分布（按 veins 标签）\n\n| 标签 | 件数 |\n|---|---|\n')
for k, n in vein_c.most_common():
    buf.write('| %s | %d |\n' % (k or '无脉', n))

buf.write('\n### 复算\n\n`python data/audit/gen_t442.py`。效果一句话优先取 `effect_text`（数据自带人话），缺失时从 `effect_code` 逐条翻译。\n')

OUT.write_text(buf.getvalue(), encoding='utf-8')
print('written', OUT, '| src', dict(src_c), '| rar', dict(rar_c))
