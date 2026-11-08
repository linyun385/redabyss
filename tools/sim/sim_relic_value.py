# -*- coding: utf-8 -*-
"""H07 遗物长期收益 → docs/design/sim_relic_value.md
每件遗物在 20 场（每场 8 回合）的累计收益分，对比商店价格（普通 120-160 / 稀有-boss 250-320）。
金→分换算：静脉合剂 60 金 = 回 35pct×76 血 ≈ 26.6 分 → 1 金 ≈ 0.44 分。
可复算：python tools/sim/sim_relic_value.py（无随机性——确定模型）
"""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from simlib import GAME

OUT = GAME / 'docs' / 'design' / 'sim_relic_value.md'
from config import RELIC_FIGHTS, RELIC_TURNS_PER_FIGHT, RELIC_KILLS_PER_FIGHT
FIGHTS, TURNS_PER_FIGHT, KILLS_PER_FIGHT = RELIC_FIGHTS, RELIC_TURNS_PER_FIGHT, RELIC_KILLS_PER_FIGHT
TRIG = {'combat_start': FIGHTS, 'turn_start': FIGHTS * TURNS_PER_FIGHT,
        'run_start': 1, 'on_kill': FIGHTS * KILLS_PER_FIGHT}
ACT = {'draw': 3.0, 'block': 0.6, 'heal': 0.6, 'maxhp': 2.0, 'resonance': 0.5}
GOLD_PER_POINT = 60 / (0.35 * 76)   # ≈2.26 金/分 → 1 分 ≈ 0.44 金

raw = json.loads((GAME / 'data/audit/raw_all.json').read_text(encoding='utf-8'))
CN_R = {'common': '普通', 'uncommon': '精良', 'rare': '稀有', 'boss': 'boss'}
rows = []
for pk, pn in [('relics', '通用'), ('anminRelics', '维护者'), ('cngRelics', '疯先知')]:
    for r in raw[pk]:
        total, unknown = 0.0, 0
        for ec in r.get('effect_code') or []:
            a, v, t = ec.get('action'), ec.get('value'), ec.get('trigger')
            if not isinstance(v, (int, float)):
                continue
            w = ACT.get(a)
            if a == 'gaze':
                w = -1.0 if v > 0 else 1.0
                v = abs(v)
            if w is None:
                unknown += 1
                continue
            total += w * v * TRIG.get(t, 0)
        price = (250, 320) if r.get('rarity') in ('rare', 'boss') else (120, 160)
        price_mid = sum(price) / 2
        worth = total / GOLD_PER_POINT   # 这件遗物「值多少金」
        rows.append((worth / price_mid, r['id'], r['name'], pn, CN_R.get(r.get('rarity'), ''), total, worth, price_mid, unknown))
rows.sort(reverse=True)

buf = []
buf.append('# H07 · 遗物长期收益与性价比（20 场累计）')
buf.append('')
buf.append('> **假设**：① 20 场 × 每场 8 回合 × 每场 1.5 杀；动作价值=分（血=1）：抽 3/张、挡 0.6/点、回血 0.6/点、上限 2/点、共振 0.5/点、凝视 +1=−1 分 / −1=+1 分；')
buf.append('> ② 金→分换算锚=静脉合剂（60 金=35pct×76 血≈26.6 分 → 1 金≈%.2f 分）；③ 遗物按商店价中位（普通 140 / 稀-boss 285）算性价比。' % (1 / GOLD_PER_POINT))
buf.append('> **局限**：裸强度不含配合乘数（共振遗物对共振流价值远超此表）；「分」把抽牌/格挡/生命折成同一量纲是强假设；未知动作按 0 计（低估）。')
buf.append('')
buf.append('## 性价比总貌（%d 件）' % len(rows))
import collections
band = collections.Counter()
for ratio, *_ in rows:
    band['值（≥1.0，超过等价回血）' if ratio >= 1 else '平（0.5~1.0）' if ratio >= 0.5 else '亏（<0.5）'] += 1
buf.append('| 性价比（收益金当量/价格中位） | 件数 |')
buf.append('|---|---|')
for k in ['值（≥1.0，超过等价回血）', '平（0.5~1.0）', '亏（<0.5）']:
    buf.append('| %s | %d |' % (k, band[k]))
buf.append('')
buf.append('## 最值（Top 10）')
buf.append('')
buf.append('| id | 名字 | 池 | 稀有度 | 20 场收益分 | 值多少金 | 价中位 | 性价比 |')
buf.append('|---|---|---|---|---|---|---|---|')
for ratio, rid, name, pn, rar, total, worth, price, unk in rows[:10]:
    buf.append('| %s | %s | %s | %s | %.0f | %.0f | %.0f | **%.2f** |' % (rid, name, pn, rar, total, worth, price, ratio))
buf.append('')
buf.append('## 最亏（Bottom 10）')
buf.append('')
buf.append('| id | 名字 | 池 | 稀有度 | 20 场收益分 | 值多少金 | 价中位 | 性价比 |')
buf.append('|---|---|---|---|---|---|---|---|')
for ratio, rid, name, pn, rar, total, worth, price, unk in rows[-10:]:
    buf.append('| %s | %s | %s | %s | %.0f | %.0f | %.0f | **%.2f** |' % (rid, name, pn, rar, total, worth, price, ratio))
buf.append('')
unk_list = [r for r in rows if r[8] > 0]
buf.append('## 含未知动作的遗物（%d 件，本模型低估）' % len(unk_list))
buf.append('')
for ratio, rid, name, pn, rar, total, worth, price, unk in unk_list[:8]:
    buf.append('- `%s` %s（%d 个未知动作）' % (rid, name, unk))
buf.append('')
buf.append('## 判断')
buf.append('')
top_ratio = rows[0][0]
buf.append('1. 性价比 ≥1 的遗物 %d 件——**多数遗物（%d/%d）的 20 场裸收益买不回商店价**：商店定价锚（等价回血）比遗物实际收益高，这解释了为什么商店遗物槽是「奢侈品」。' % (
    band['值（≥1.0，超过等价回血）'], len(rows) - band['值（≥1.0，超过等价回血）'], len(rows)))
buf.append('2. 最值的是被动数值件（每回合挡/回/共振），最亏的是凝视正债件——与 relic_tier.md（T525）同向，本篇把「分」换算成了「金」可直接比价。')
buf.append('3. 全部为**裸强度口径**：配合流（共振流拿谐振垫层类）的真实价值高于此表——买遗物的决策不能只看本表。')
buf.append('')
buf.append('## 复算')
buf.append('')
buf.append('`python tools/sim/sim_relic_value.py`（FIGHTS/TURNS_PER_FIGHT/KILLS_PER_FIGHT/GOLD_PER_POINT 在顶部）。')
OUT.write_text('\n'.join(buf) + '\n', encoding='utf-8')
import io as _io
sys.stdout = _io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
print('rows', len(rows), 'bands', dict(band), 'top', rows[0][1], rows[0][0], 'bottom', rows[-1][1], rows[-1][0])
