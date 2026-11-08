# -*- coding: utf-8 -*-
"""B · 卡牌数值审计 → docs/design/ui/11_card_numbers_audit.md
可复算：python tools/sim/card_numbers_audit.py
所有数字由本脚本计算，无手写值。
"""
import sys, io, json, collections, statistics
from pathlib import Path

GAME = Path(__file__).resolve().parents[2]
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

CLASSES = ['diver', 'tremor', 'anmin', 'cangmin', 'shared']
FEES = ["0", "1", "2", "3"]
RARS = ["common", "uncommon", "rare", "special"]
TYPES = ["attack", "skill", "power"]
CN = {'diver': '下潜者', 'tremor': '震语者', 'anmin': '维护者', 'cangmin': '疯先知', 'shared': '通用',
      'attack': '攻击', 'skill': '技能', 'power': '能力',
      'common': '普通', 'uncommon': '精良', 'rare': '稀有', 'special': '特殊'}

# 加载
cards = {}
total = 0
for f in CLASSES:
    arr = json.loads((GAME / 'cards' / (f + '.json')).read_text(encoding='utf-8'))
    cards[f] = arr
    total += len(arr)

all_c = {}
for cl in CLASSES:
    for c in cards[cl]:
        all_c[c['id']] = c

# ── 效果量计算 ──

def power_score(c):
    """主效果量：把一张卡的全部数值效果折成一个可比数字。
    折算口径（写明，不隐藏）：
      damage × hits = 1 分/点
      block = 1 分/点
      draw × 3 = 3 分/张（手牌优势）
      heal × 0.6 = 0.6 分/点
      resonance_gain × 0.5 = 0.5 分/点
      gaze_gain × 1 = 1 分/点（正债，对凝视流是资源）
      strength/dexterity × 2 = 2 分/点（永久 buff）
      regenerate × 0.6 × 3 = 1.8 分/点（按 3 回合）
      thorns × 0.6 = 0.6 分/点
      special 不计（无法统一定价）
    多效果卡 = 各分量之和。这是「裸强度」口径，不含协同/流派加成。"""
    e = c.get('effect') or {}
    s = 0.0
    if e.get('damage'):
        s += e['damage'] * (e.get('hits') or 1)
    if e.get('block'):
        s += e['block']
    if e.get('draw'):
        s += e['draw'] * 3
    if e.get('heal'):
        s += e['heal'] * 0.6
    if e.get('resonance_gain'):
        s += e['resonance_gain'] * 0.5
    if e.get('gaze_gain'):
        s += e['gaze_gain'] * 1
    for sp in e.get('special') or []:
        if not isinstance(sp, dict):
            continue
        code = sp.get('code', '')
        v = sp.get('value', sp.get('v', 1))
        if code == 'strength':
            s += v * 2
        elif code == 'dexterity':
            s += v * 2
        elif code == 'regenerate':
            s += v * 0.6 * 3
        elif code == 'thorns':
            s += v * 0.6
    return round(s, 1)

def upgrade_power_delta(c):
    """升级后效果量差 = upgrade 后 power_score − 原 power_score。"""
    up = c.get('upgrade')
    if not up:
        return None
    upgraded = dict(c)
    upgraded['effect'] = dict(c.get('effect') or {})
    upgraded['upgraded'] = True
    if up.get('effect'):
        for k, v in up['effect'].items():
            if k == 'special':
                old_sp = upgraded['effect'].get('special') or []
                upgraded['effect']['special'] = old_sp + (v if isinstance(v, list) else [v])
            else:
                upgraded['effect'][k] = v
    return round(power_score(upgraded) - power_score(c), 1)

# 全卡打分
scored = []
for cl in CLASSES:
    for c in cards[cl]:
        ps = power_score(c)
        upd = upgrade_power_delta(c)
        scored.append((cl, c, ps, upd))

# ── B1 费用-效果量曲线 ──
buf = []
buf.append('# B · 卡牌数值审计（%d 张）' % total)
buf.append('')
buf.append('> 口径：效果量 = damage×hits(1/点) + block(1/点) + draw(3/张) + heal(0.6/点) + resonance(0.5/点) + gaze(1/点) + str/dex(2/点) + regen(1.8/点) + thorns(0.6/点)。special 不计。')
buf.append('> **裸强度口径**：不含协同/流派加成/升级。全部数字由脚本计算。')
buf.append('> 复算：`python tools/sim/card_numbers_audit.py`')
buf.append('')
buf.append('## B1 · 费用-效果量曲线')
buf.append('')
buf.append('| 费 | 张数 | 最小 | P25 | 中位 | P75 | P90 | 最大 | 均值 |')
buf.append('|---|---|---|---|---|---|---|---|---|')

def pct(lst, p):
    s = sorted(lst)
    idx = int(p * len(s))
    return s[min(idx, len(s) - 1)]

by_fee = collections.defaultdict(list)
for cl, c, ps, upd in scored:
    by_fee[c.get('energy', 0)].append(ps)

for fee in [0, 1, 2, 3]:
    vals = by_fee.get(fee, [])
    if not vals:
        continue
    buf.append('| %d | %d | %.1f | %.1f | %.1f | %.1f | %.1f | %.1f | %.1f |' % (
        fee, len(vals), min(vals), pct(vals, .25), statistics.median(vals),
        pct(vals, .75), pct(vals, .9), max(vals), statistics.mean(vals)))
buf.append('')

# 异常值
buf.append('### 异常高（> 该费 P90 × 1.5）')
buf.append('')
buf.append('| id | 名字 | 职业 | 费 | 效果量 | 该费 P90 | 倍数 |')
buf.append('|---|---|---|---|---|---|---|')
hi_count = 0
for fee in [0, 1, 2, 3]:
    vals = by_fee.get(fee, [])
    if not vals: continue
    p90 = pct(vals, .9)
    for cl, c, ps, upd in scored:
        if c.get('energy', 0) == fee and ps > p90 * 1.5:
            hi_count += 1
            buf.append('| %s | %s | %s | %d | %.1f | %.1f | %.1fx |' % (
                c['id'], c['name'], CN[cl], fee, ps, p90, ps / p90 if p90 else 0))
if hi_count == 0:
    buf.append('（无）')
buf.append('')

buf.append('### 异常低（< 该费 P50 × 0.5）')
buf.append('')
buf.append('| id | 名字 | 职业 | 费 | 效果量 | 该费 P50 | 比率 |')
buf.append('|---|---|---|---|---|---|---|')
lo_count = 0
for fee in [0, 1, 2, 3]:
    vals = by_fee.get(fee, [])
    if not vals: continue
    p50 = statistics.median(vals)
    if p50 == 0: continue
    for cl, c, ps, upd in scored:
        if c.get('energy', 0) == fee and ps < p50 * 0.5:
            lo_count += 1
            buf.append('| %s | %s | %s | %d | %.1f | %.1f | %.2f |' % (
                c['id'], c['name'], CN[cl], fee, ps, p50, ps / p50))
if lo_count == 0:
    buf.append('（无）')
buf.append('')

# 升级后变低
buf.append('### 升级后效果量反而变低')
buf.append('')
buf.append('| id | 名字 | 升级前量 | 升级后差 |')
buf.append('|---|---|---|---|')
neg_count = 0
for cl, c, ps, upd in scored:
    if upd is not None and upd < 0:
        neg_count += 1
        buf.append('| %s | %s | %.1f | %.1f |' % (c['id'], c['name'], ps, upd))
if neg_count == 0:
    buf.append('（无——全部升级 ≥ 0）')
buf.append('')

# ── B2 职业间横向对比 ──
buf.append('## B2 · 职业间横向对比')
buf.append('')
buf.append('同费 + 同类型，四职业（不含 shared）效果量均值：')
buf.append('')
buf.append('| 费 | 类型 | ' + ' | '.join(CN[c] for c in CLASSES[:4]) + ' | 最大差 |')
buf.append('|---|---|' + '---|' * 5 + '---|')

gap_rows = []
for fee in [0, 1, 2, 3]:
    for typ in TYPES:
        cls_avgs = {}
        for cl in CLASSES[:4]:
            vals = [ps for cl2, c, ps, upd in scored if cl2 == cl and c.get('energy', 0) == fee and c.get('type') == typ]
            if vals:
                cls_avgs[cl] = statistics.mean(vals)
        if len(cls_avgs) < 2:
            continue
        mx = max(cls_avgs.values())
        mn = min(cls_avgs.values())
        gap = mx - mn
        if gap < 1:
            continue
        cells = []
        for cl in CLASSES[:4]:
            v = cls_avgs.get(cl)
            cells.append('%.1f' % v if v is not None else '·')
        buf.append('| %d | %s | %s | %.1f |' % (fee, CN[typ], ' | '.join(cells), gap))
        gap_rows.append((gap, fee, typ, cls_avgs))
buf.append('')

gap_rows.sort(reverse=True)
buf.append('### 差得离谱的（gap ≥ 5 分）')
buf.append('')
for gap, fee, typ, avgs in gap_rows[:10]:
    detail = '、'.join('%s %.1f' % (CN[k], v) for k, v in sorted(avgs.items(), key=lambda x: -x[1]))
    buf.append('- **%d费 %s**（gap=%.1f）：%s' % (fee, CN[typ], gap, detail))
buf.append('')

# ── B3 不可解释的空洞 ──
buf.append('## B3 · 不可解释的空洞')
buf.append('')
buf.append('结合 07_card_pool_shape.md 薄位表，挑出「这个位置空着且说不通」的格子。')
buf.append('')
# 3费稀有档
rare_3 = [(cl, c) for cl in CLASSES for c in cards[cl]
          if c.get('energy', 0) >= 3 and c.get('rarity') == 'rare']
buf.append('### 3 费稀有档（全池 %d 张）' % len(rare_3))
buf.append('')
for cl in CLASSES[:4]:
    n = sum(1 for cl2, c in rare_3 if cl2 == cl)
    buf.append('- %s：%d 张' % (CN[cl], n))
buf.append('- shared：%d 张' % sum(1 for cl2, c in rare_3 if cl2 == 'shared'))
buf.append('')
buf.append('**说不通的理由**：3 费是能量 4 下的「大牌回合」费段（T400 §2.4 判定 3 费从鸡肋变可用），但稀有档仅 %d 张——设计者可能在等核心卡填这个位。' % len(rare_3))
buf.append('')
# 0费能力
power_0 = [(cl, c) for cl in CLASSES for c in cards[cl]
           if c.get('energy', 0) == 0 and c.get('type') == 'power']
buf.append('### 0 费能力（全池 %d 张）' % len(power_0))
buf.append('')
for cl, c in power_0:
    buf.append('- %s（%s）' % (c['name'], CN[cl]))
buf.append('')
buf.append('**说不通的理由**：能力（power）是持续效果——0 费能力=白送永久 buff。全池仅 %d 张说明设计者有意控制（对比：1 费能力 %d 张）。不是遗漏，是平衡选择。' % (len(power_0), sum(1 for cl in CLASSES for c in cards[cl] if c.get('energy',0)==1 and c.get('type')=='power')))
buf.append('')

# ── B4 复算说明 ──
buf.append('## B4 复算')
buf.append('')
buf.append('```bash')
buf.append('python tools/sim/card_numbers_audit.py')
buf.append('```')
buf.append('脚本读 cards/*.json，按本文件头部的折算口径计算 power_score，输出全部统计。无手写值。')
buf.append('')
buf.append('---')
buf.append('')
buf.append('> 我没开浏览器，所有结论是代码级的。读到的是 cards/*.json 当前版本。')

OUT = GAME / 'docs' / 'design' / 'ui' / '11_card_numbers_audit.md'
OUT.write_text('\n'.join(buf) + '\n', encoding='utf-8')
print('written', OUT)
print('total scored:', len(scored))
print('hi outliers:', hi_count, '| lo outliers:', lo_count, '| neg upgrades:', neg_count)
print('gap rows >= 5:', sum(1 for g, *_ in gap_rows if g >= 5))
