# -*- coding: utf-8 -*-
"""T520 每张卡"如果重设计"的建议 → docs/design/redesign_notes.md

四类标：改数值 / 改机制 / 改定位 / 不用改。
建议来源（规则级联，取最高优先）：
  P1 效果为空或含死机制（frail 无结算，引擎实证）→ 改机制
  P2 脉标签与 §2.1 矛盾（T406 V1-V5 + 人工补查名单）→ 改定位（标签/效果主体二选一）
  P3 完全撞（T402 全 219 扫描，同 effect 跨卡）→ 改数值（把同配方拉开数值档）
  P4 近似撞分量成员 → 改数值
  P5 其余 → 不用改（基准牌/独占机制卡）
每张一句具体建议；只在「改」类给方向，不给删卡建议。
手工覆盖表 OVER 放判读特例。复算：python data/audit/gen_t520.py

用法：python data/audit/gen_t520.py
"""
import io, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_common import GAME, CN_CLASS, CN_VEIN, load_cards, all_cards, effect_fp, main_shape
from collections import defaultdict

OUT = GAME / 'docs' / 'design' / 'redesign_notes.md'

# ── T406 矛盾名单（与 gen_t406 相同规则重算） ──
ENEMY_STATES = {'burn', 'weak', 'frail', 'poison'}
SELF_BUFFS = {'block', 'heal', 'regenerate', 'strength', 'dexterity'}
MANUAL_SETS = {
    'dive_0001', 'dive_0003', 'dive_0008', 'dive_0053', 'dive_0080',
    'trem_0025', 'trem_0026', 'trem_0027', 'trem_0028', 'trem_0055', 'trem_0066',
    'anm_0003', 'anm_0023', 'anm_0033', 'anm_0045', 'anm_0049',
    'cng_0002', 'cng_0006', 'cng_0007', 'cng_0008', 'cng_0014', 'cng_0017',
    'cng_0033', 'cng_0039', 'cng_0044', 'cng_0047',
    'dive_0014', 'anm_0006', 'anm_0009', 'anm_0018', 'anm_0044', 'anm_0045', 'anm_0049',
    'trem_0037', 'trem_0038', 'trem_0057',
    'dive_0007', 'dive_0052', 'dive_0071', 'anm_0050', 'cng_0050', 'u_0009',
}

def contradiction(c):
    vs = set(c.get('veins') or [])
    e = c.get('effect') or {}
    cs = [s.get('code') for s in e.get('special') or [] if isinstance(s, dict)]
    if 'heat' in vs:
        hits_enemy = bool(e.get('damage') or e.get('hits')) or any(x in ENEMY_STATES for x in cs)
        touches_self = any(k in e for k in SELF_BUFFS) or any(x in SELF_BUFFS for x in cs)
        if not hits_enemy and touches_self:
            return '热脉只改自己'
    if 'mineral' in vs and any(x in ENEMY_STATES for x in cs):
        return '矿脉挂敌状态'
    if 'water' in vs and not e.get('draw'):
        return '水脉无流转'
    if 'tremor' in vs and e.get('resonance_cost'):
        return '震脉要攒共振'
    if c['id'] in MANUAL_SETS:
        return '过牌/平buff 挂错脉'
    return None

# ── 完全撞 / 近似撞（T402 同款） ──
fp_map = defaultdict(list)
shape_bucket = defaultdict(list)
PAIRS = list(all_cards(load_cards()))
for cls, c in PAIRS:
    fp_map[effect_fp(c)].append(c['id'])
    shp = main_shape(c)
    shape_bucket[(shp[0], shp[1], shp[3], shp[4])].append(c)
exact_of = {}
for fp, ids in fp_map.items():
    if len(ids) >= 2:
        for i in ids:
            exact_of[i] = ids
near_adj = defaultdict(set)
for members in shape_bucket.values():
    for i, a in enumerate(members):
        for b in members[i + 1:]:
            if effect_fp(a) == effect_fp(b):
                continue
            if abs(main_shape(a)[2] - main_shape(b)[2]) in (1, 2):
                near_adj[a['id']].add(b['id'])
                near_adj[b['id']].add(a['id'])

# ── 手工特例（判读） ──
OVER = {
 'u_0016': ('改机制', 'anmin_mark 激活 purge 协议是生效的，但 effect 字段为空——卡面没有任何效果描述，玩家不知道这是张协议开关牌。要改的是呈现：效果文本补上（机制本身别动）'),
 'dive_0022': ('改机制', '挂的脆弱（frail）引擎从不结算（dealToEnemy 不读 status.frail）——要么给 frail 加结算，要么把脆弱换成有效状态；数值本身没问题'),
 'trem_0034': ('改机制', '同上：脆弱 1 回合是无效果的装饰——换状态或删挂件；14 伤+共振支付的主体保留'),
 'dive_0026': ('改定位', '震脉但花共振——按 §2.1「震不许要铺垫」它是光（有条件高效）的配方；建议改脉标签或把共振支付改成凝视门槛'),
 'dive_0029': ('改定位', '同 dive_0026：共振支付的抽牌更像水（流转主体）+共振定价，不像震'),
 'dive_0046': ('改定位', '36 伤花共振 15 是大招不是「拿到就能用」的震——建议改脉或把它的定位写成「震脉的例外大额位」'),
 'trem_0013': ('改数值', '三段+共振支付+凝视门槛三种定价叠一张，且 54 字全池最长卡面——先减一层定价（去掉共振支付或门槛二选一）'),
 'share_0001': ('不用改', '规则豁免位是通用池唯一元机制，别动'),
 'u_0003': ('改定位', 'T408 建议：回血主体更像矿（无条件改自己）——给脉或保持无脉二选一'),
 'u_0006': ('改定位', 'T408 建议：无条件直伤归矿；或保持无脉作为「生命定价」系列的一员'),
 'dive_0039': ('改定位', '名字是矿票、效果是纯抽牌（水的味道）——名字与效果二选一对齐'),
 'dive_0081': ('改定位', 'T408：无条件格挡=矿味道——建议给矿脉'),
 'trem_0039': ('改定位', 'T408：无条件格挡=矿味道——建议给矿脉'),
 'trem_0058': ('改定位', 'T408：凝视 8 门槛成长，按有条件判据偏光；成长味偏矿——设计者拍板'),
 'trem_0060': ('改定位', 'T408：凝视门槛 AOE 偏光'),
 'trem_0082': ('改定位', 'T408：格挡主体偏矿'),
 'trem_0010': ('改数值', '三段 27 点但门槛只要凝视 2——全池门槛最松的三段卡，建议把凝视门槛调到 3-4 档'),
}

def suggest(c):
    cid = c['id']
    if cid in OVER:
        return OVER[cid]
    e = c.get('effect') or {}
    cs = [s.get('code') for s in e.get('special') or [] if isinstance(s, dict)]
    if not any(k for k in e if k not in ('target',)) and not cs:
        return ('改机制', 'effect 为空——先补效果')
    con = contradiction(c)
    if con:
        vein = '+'.join(CN_VEIN.get(v, v) for v in (c.get('veins') or [])) or '无脉'
        return ('改定位', '%s：%s 脉标签与效果主体错位（T406）——改标签或改效果主体，二选一' % (con, vein))
    if cid in exact_of:
        others = [i for i in exact_of[cid] if i != cid]
        return ('改数值', '与 %s 完全同效果——把数值档拉开（±2 以上）或给其中之一加一层小机制' % '、'.join(others[:3]))
    if near_adj.get(cid):
        return ('改数值', '与 %s 主数值同档——若非有意梯度，微调数值错开一档' % '、'.join(sorted(near_adj[cid])[:3]))
    return ('不用改', '基准位/独占位，与体系无冲突')

buf = io.StringIO()
buf.write('# T520 · 每张卡「如果重设计」的建议\n\n')
buf.write('> 规则级联：P1 死机制/空效果→改机制；P2 脉标签矛盾（T406）→改定位；P3/P4 重复→改数值；P5 其余→不用改。\n')
buf.write('> 特例手工覆盖 %d 张（判读）。**只有建议，没有删卡**。复算：`python data/audit/gen_t520.py`。\n\n' % len(OVER))

CAT_ORDER = ['改机制', '改定位', '改数值', '不用改']
counts = defaultdict(int)
by_cat = defaultdict(list)
for cls, c in all_cards(load_cards()):
    cat, note = suggest(c)
    counts[cat] += 1
    by_cat[cat].append((cls, c, note))

for cat in CAT_ORDER:
    buf.write('## %s（%d 张）\n\n' % (cat, counts[cat]))
    for cls, c, note in by_cat[cat]:
        buf.write('- `%s` %s（%s）：%s\n' % (c['id'], c['name'], CN_CLASS[cls], note))
    buf.write('\n')

buf.write('### 汇总\n\n')
buf.write('- 改机制 %d（含空效果与死机制 frail）、改定位 %d（脉标签错位）、改数值 %d（重复档）、不用改 %d。\n' % (
    counts['改机制'], counts['改定位'], counts['改数值'], counts['不用改']))
buf.write('- 改数值类里大部分是「结构性重复」的梯度成员——真实需要动的是 P3 完全撞的那批（见 T402 清单）。\n')
buf.write('- 改定位类的本质：这批卡的**名字/标签与效果在讲两个故事**——修正方向是把两者对齐，不是削弱。\n')

OUT.write_text(buf.getvalue(), encoding='utf-8')
print('written', OUT, dict(counts))
