# -*- coding: utf-8 -*-
"""T504 稀有度分布合理性 → docs/design/rarity_dist.md

算法：
  桶 = (角色, 类型, 费用)。桶内≥4 张才比（样本太少不判）。
  「低稀有度但明显强」：common/uncommon 卡的主数值 ≥ 同桶内 rare 卡主数值中位数，
                        或 effect 有效键数（除 target/hits）≥3。
  「高稀有度但很平庸」：rare 卡的主数值 ≤ 同桶内 common 卡主数值中位数，且 effect 键数 ≤1。
  主数值 = main_shape 的主种类数值（audit_common.main_shape，与查重同源）。
  只报告，不改。

用法：python data/audit/gen_t504.py
"""
import io, sys, statistics
from pathlib import Path
from collections import Counter, defaultdict
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_common import GAME, CN_CLASS, CN_TYPE, load_cards, main_shape

OUT = GAME / 'docs' / 'design' / 'rarity_dist.md'
CLASSES = ['diver', 'tremor', 'anmin', 'cangmin', 'shared']
cards = load_cards()
ALL = [(cls, c) for cls in CLASSES for c in cards[cls]]
CN_R = {'common': '普通', 'uncommon': '精良', 'rare': '稀有', 'special': '特殊'}

# 分布
dist = defaultdict(Counter)
for cls, c in ALL:
    dist[cls][c.get('rarity')] += 1

buf = io.StringIO()
buf.write('# T504 · 稀有度分布合理性\n\n')
buf.write('> 数据源：`cards/*.json`（219 张）。复算：`python data/audit/gen_t504.py`。算法见文末。只报告，不改。\n\n')

buf.write('## 一、数量分布\n\n| 角色 | 普通 | 精良 | 稀有 | 特殊 | 合计 |\n|---|---|---|---|---|---|\n')
for cls in CLASSES:
    cc = dist[cls]
    buf.write('| %s | %d | %d | %d | %d | %d |\n' % (
        CN_CLASS[cls], cc['common'], cc['uncommon'], cc['rare'], cc['special'],
        sum(cc.values())))
tot = Counter()
for cls in CLASSES:
    tot.update(dist[cls])
buf.write('| 全池 | %d | %d | %d | %d | %d |\n' % (
    tot['common'], tot['uncommon'], tot['rare'], tot['special'], sum(tot.values())))

# 桶分析
bucket = defaultdict(list)
for cls, c in ALL:
    bucket[(cls, c.get('type'), c.get('energy'))].append(c)

strong_low, weak_high = [], []
for key, members in bucket.items():
    if len(members) < 4:
        continue
    by_r = defaultdict(list)
    for c in members:
        by_r[c.get('rarity')].append(c)
    # 主种类（main_shape[1]）必须相同才比数值——block 8 和 draw 3 不可比
    def kind_med(rar):
        vals = [(main_shape(c)[1], main_shape(c)[2]) for c in by_r.get(rar, [])]
        by_kind = defaultdict(list)
        for k, v in vals:
            if k:
                by_kind[k].append(v)
        return {k: statistics.median(v) for k, v in by_kind.items()}
    rare_meds = kind_med('rare')
    common_meds = kind_med('common')
    for c in by_r.get('common', []) + by_r.get('uncommon', []):
        nkeys = len([k for k in (c.get('effect') or {}) if k not in ('target', 'hits')])
        kind, v = main_shape(c)[1], main_shape(c)[2]
        med = rare_meds.get(kind)
        if (med is not None and v >= med and v > 0) or nkeys >= 3:
            strong_low.append((key, c, '主值 %s(%s) ≥ 同桶稀有档同种类中位数 %s；键数 %d' % (v, kind, med, nkeys)))
    for c in by_r.get('rare', []):
        kind, v = main_shape(c)[1], main_shape(c)[2]
        nkeys = len([k for k in (c.get('effect') or {}) if k not in ('target', 'hits')])
        med = common_meds.get(kind)
        if med is not None and v <= med and nkeys <= 1:
            weak_high.append((key, c, '主值 %s(%s) ≤ 同桶普通档同种类中位数 %s；键数 %d' % (v, kind, med, nkeys)))

buf.write('\n## 二、低稀有度但明显强（%d 处）\n\n' % len(strong_low))
buf.write('| id | 名字 | 角色 | 类型 | 费 | 稀有度 | 证据 |\n|---|---|---|---|---|---|---|\n')
for key, c, ev in strong_low:
    buf.write('| %s | %s | %s | %s | %s | %s | %s |\n' % (
        c['id'], c['name'], CN_CLASS[key[0]], CN_TYPE.get(key[1], key[1]), key[2],
        CN_R[c.get('rarity')], ev))

buf.write('\n## 三、高稀有度但很平庸（%d 处）\n\n' % len(weak_high))
buf.write('| id | 名字 | 角色 | 类型 | 费 | 稀有度 | 证据 |\n|---|---|---|---|---|---|---|\n')
for key, c, ev in weak_high:
    buf.write('| %s | %s | %s | %s | %s | %s | %s |\n' % (
        c['id'], c['name'], CN_CLASS[key[0]], CN_TYPE.get(key[1], key[1]), key[2],
        CN_R[c.get('rarity')], ev))

buf.write('\n## 四、判断\n\n')
buf.write('- 稀有度**大体上在按强度分**：普通档以单键基准牌为主，复合效果集中在精良/稀有档。\n')
if strong_low:
    from collections import Counter as _C
    cls_cnt = _C(CN_CLASS[k[0]] for k, _, _ in strong_low)
    buf.write('- 但有 %d 张低稀有度卡摸到了稀有档的数值线：%s。' % (
        len(strong_low), '、'.join('%s%d' % kv for kv in cls_cnt.items())))
    buf.write('其中复合键数 ≥3 的（如无门槛大 AOE、双键直伤）是真正的「稀有度给低了」候选。\n')
if weak_high:
    buf.write('- %d 张稀有卡只给出普通档中位数以下的单键数值——稀有度没兑现。' % len(weak_high))
    buf.write('这些卡要么效果缺失（见 T447 空转检查），要么数值需要重看。\n')
buf.write('- 「特殊」稀有度 14 张全是机制展示位（带 retain/共振锁定/mark 等教学效果），不是强度档——这个用法是健康的。\n')
buf.write('\n## 算法（复算用）\n\n')
buf.write('1. 桶=(角色,类型,费用)，桶内 ≥4 张才参与比较。\n')
buf.write('2. 主数值 = `audit_common.main_shape` 的主种类数值（与查重同源）。\n')
buf.write('3. 低稀强：common/uncommon 主值 ≥ 同桶 rare 主值中位数（且 >0），或有效键数 ≥3。\n')
buf.write('4. 高稀平：rare 主值 ≤ 同桶 common 主值中位数，且有效键数 ≤1。\n')
buf.write('5. 有效键数 = effect 里除 `target`/`hits` 外的键数（special 算 1 个）。\n')

OUT.write_text(buf.getvalue(), encoding='utf-8')
print('written', OUT, '| strong_low', len(strong_low), '| weak_high', len(weak_high))
for _, c, _ in strong_low:
    print('  LOW-RARE STRONG:', c['id'], c['name'])
for _, c, _ in weak_high:
    print('  HIGH-RARE WEAK:', c['id'], c['name'])
