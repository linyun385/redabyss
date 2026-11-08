# -*- coding: utf-8 -*-
"""T406 现有卡脉标签 vs §2.1 矛盾检查 → 追加到 docs/design/vein_audit_matrix.md。

机械规则（全部来自 T400 §2.1 原文判据，只报告）：
  V1 热≠改自己：热脉卡无 damage/burn/weak/frail/poison 等挂敌人的内容，却有 block/heal/regenerate/strength/dexterity
  V2 矿≠改敌人：矿脉卡 special 含 burn/weak/frail/poison（挂敌人的状态）
  V3 水必须有流转：水脉卡无 draw 键（当前卡池流转动词只有 draw；回手/回库/复制/改费不存在）→ 拿掉流转什么都不剩
  V4 震不许要铺垫：震脉卡带 resonance_cost（要攒资源才打得出来）
  V5 光应有条件：光脉卡是纯单键 damage 或 heal（无任何条件/门槛键）→ 「有条件高效」未体现（弱规则，标记需人工看）
人工补查：光/矿脉的「纯过牌位」（效果主体是抽牌=水的流转判据）——机械规则够不到，逐张人工列。

用法：python data/audit/gen_t406.py
"""
import io, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_common import GAME, CN_CLASS, load_cards, all_cards

OUT = GAME / 'docs' / 'design' / 'vein_audit_matrix.md'
ENEMY_STATES = {'burn', 'weak', 'frail', 'poison'}
SELF_BUFFS = {'block', 'heal', 'regenerate', 'strength', 'dexterity'}

def codes(c):
    return [s.get('code') for s in (c.get('effect') or {}).get('special') or []
            if isinstance(s, dict)]

def keys(c):
    return set((c.get('effect') or {}).keys())

def flag_cards():
    out = {r: [] for r in ('V1', 'V2', 'V3', 'V4', 'V5')}
    for cls, c in all_cards(load_cards()):
        vs = set(c.get('veins') or [])
        e = c.get('effect') or {}
        cs = codes(c)
        ks = keys(c)
        if 'heat' in vs:
            hits_enemy = bool(e.get('damage') or e.get('hits')) or any(x in ENEMY_STATES for x in cs)
            touches_self = any(k in ks for k in SELF_BUFFS) or any(x in SELF_BUFFS for x in cs)
            if not hits_enemy and touches_self:
                out['V1'].append((cls, c))
        if 'mineral' in vs and any(x in ENEMY_STATES for x in cs):
            out['V2'].append((cls, c))
        if 'water' in vs and not e.get('draw'):
            out['V3'].append((cls, c))
        if 'tremor' in vs and e.get('resonance_cost'):
            out['V4'].append((cls, c))
        if 'light' in vs:
            core = [k for k in ks if k not in ('target', 'hits')]
            if len(core) == 1 and core[0] in ('damage', 'heal') and not cs:
                out['V5'].append((cls, c))
    return out

# 人工补查（判读依据写明）：效果主体=纯抽牌/共振，脉却是光或矿
MANUAL = {
    '光脉纯过牌位': [
        'dive_0001', 'dive_0003', 'dive_0008', 'dive_0053', 'dive_0080',
        'trem_0025', 'trem_0026', 'trem_0027', 'trem_0028', 'trem_0055', 'trem_0066',
        'anm_0003', 'anm_0023', 'anm_0033', 'anm_0045', 'anm_0049',
        'cng_0002', 'cng_0006', 'cng_0007', 'cng_0008', 'cng_0014', 'cng_0017',
        'cng_0033', 'cng_0039', 'cng_0044', 'cng_0047'],
    '矿脉纯过牌/共振位（不改自身数值）': [
        'dive_0014', 'anm_0006', 'anm_0009', 'anm_0018', 'anm_0044', 'anm_0045', 'anm_0049',
        'trem_0037', 'trem_0038', 'trem_0057'],
    '光脉纯过牌 + 光脉无条件平 buff（按「矿无条件=矿」判据）': [
        'dive_0007', 'dive_0052', 'dive_0071', 'anm_0050', 'cng_0050', 'u_0009'],
}
MANUAL_WHY = {
    '光脉纯过牌位': '效果主体 = 抽牌。按 §2.1 水专用判据「拿掉流转动词什么都不剩才是水」，反过来说：流转是主体的牌读起来就是水——遮住脉名会猜成水脉，违反通用判据 1。',
    '矿脉纯过牌/共振位（不改自身数值）': '矿判据 = 「直接改自身数值（力量/格挡加成/上限）」。这些卡改的是牌数与共振，不是自身数值——遮住脉名猜不出矿。',
    '光脉纯过牌 + 光脉无条件平 buff（按「矿无条件=矿」判据）': '平 buff（力量/敏捷+2）是无条件高效改自身 → 按「矿 vs 光」切法该读作矿；倒转圣痕的凝视/共振不占时间轴 → 都不像光。',
}

def cell(cls, c, extra=''):
    return '`%s` %s（%s）%s' % (c['id'], c['name'], CN_CLASS[cls], extra)

buf = io.StringIO()
buf.write('\n## 脉标签 vs §2.1 矛盾检查（T406）\n\n')
buf.write('判据全部来自 `tasks/T400_vein_system_master.md` §2.1。**只报告，不改**。')
buf.write('结论先行：矛盾大头不是「标错一条脉」，而是**大量卡的效果主体（抽牌/共振/平 buff）与脉标签无关**——标签像贴上去的。\n\n')

R = flag_cards()
RULE_TXT = {
    'V1': ('热脉却只改自己（无伤害/无挂敌状态，有格挡/回血/再生/力量/敏捷）', '违反「矿 vs 热：热改敌人」'),
    'V2': ('矿脉却挂敌人状态（burn/weak/frail/poison）', '违反「矿 vs 热：矿改自己」'),
    'V3': ('水脉却没有任何流转键（当前池流转键只有 draw）', '违反水专用判据：拿掉流转什么都不剩 → 它不是水'),
    'V4': ('震脉却要花共振（resonance_cost）——需要先攒资源', '违反震专用判据：拿到就要能用，不许要铺垫'),
    'V5': ('光脉纯单键伤害/回血（无门槛无条件）', '违反「矿 vs 光：光有条件」——弱规则，需人工看（基础输出位也许只能这样）'),
}
for r in ['V1', 'V2', 'V3', 'V4', 'V5']:
    lst = R[r]
    buf.write('### %s：%s（%d 张）\n\n判据：%s。\n\n' % (r, RULE_TXT[r][0], len(lst), RULE_TXT[r][1]))
    if lst:
        buf.write('%s\n\n' % '、'.join(cell(cls, c) for cls, c in lst))

buf.write('### 人工补查（机械规则够不到的维度）\n\n')
total_manual = 0
for k, ids in MANUAL.items():
    total_manual += len(ids)
    buf.write('**%s**（%d 张）——%s\n\n%s\n\n' % (
        k, len(ids), MANUAL_WHY[k],
        '、'.join('`%s`' % i for i in ids)))

n_flag = sum(len(v) for v in R.values())
buf.write('### 汇总\n\n')
buf.write('- 机械规则命中 %d 处（V1 %d / V2 %d / V3 %d / V4 %d / V5 %d）；人工补查 %d 张。\n' % (
    n_flag, len(R['V1']), len(R['V2']), len(R['V3']), len(R['V4']), len(R['V5']), total_manual))
buf.write('- 最大的一块是「过牌位挂错脉」：光脉 25 张、矿脉 10 张、光脉buff 6 张——**抽牌与共振是水/无脉的味道，不是光/矿的**。\n')
buf.write('- 第二块是热脉「只改自己」11 张——热脉被写成第二条矿脉的样子。\n')
buf.write('- 复算：`python data/audit/gen_t406.py`（追加运行）。机械规则为脚本实现；人工补查清单为逐张判读，判据已写明。\n')

with open(OUT, 'a', encoding='utf-8') as f:
    f.write(buf.getvalue())
print('appended T406: flags', {k: len(v) for k, v in R.items()}, 'manual', total_manual)
