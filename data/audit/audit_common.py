# -*- coding: utf-8 -*-
"""脉象盘点公共数据层（T401–T416 及后续批次共用）。

数据源（优先级）：
1. cards/{diver,tremor,anmin,cangmin,shared}.json —— 权威
2. data/audit/raw_cards.json —— 由 web/index.html `const RAW =`（行 6401）经 node JSON.parse 抽出，
   仅用于比对不一致项，不作为数据来源。

算法全部写在此文件，产出文档的文末会注明算法。
"""
import json, sys
from pathlib import Path
from collections import defaultdict

GAME = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(GAME / 'tools'))
from card_desc import describe_card  # noqa: E402  复用引擎翻译，不重写

CLASSES = ['diver', 'tremor', 'anmin', 'cangmin', 'shared']
CN_CLASS = {'diver': '下潜者', 'tremor': '震语者', 'anmin': '维护者',
            'cangmin': '疯先知', 'shared': '通用'}
CN_VEIN = {'light': '光', 'water': '水', 'heat': '热', 'tremor': '震',
           'mineral': '矿'}
CN_TYPE = {'attack': '攻击', 'skill': '技能', 'power': '能力'}
CN_RARITY = {'common': '普通', 'uncommon': '精良', 'rare': '稀有',
             'special': '特殊'}

DEBUFF_CODES = {'burn', 'poison', 'weak', 'frail'}
BUFF_CODES = {'strength', 'dexterity', 'regenerate', 'thorns'}


def load_cards():
    """返回按 class 分组的卡列表（跳过 _draft 等 _ 开头文件）。"""
    out = {}
    for cls in CLASSES:
        p = GAME / 'cards' / (cls + '.json')
        out[cls] = json.loads(p.read_text(encoding='utf-8'))
    return out


def all_cards(cards=None):
    """返回 [(cls, card), ...] 共 219 项，顺序 = CLASSES 顺序 = 文件内原顺序。"""
    cards = cards or load_cards()
    return [(cls, c) for cls in CLASSES for c in cards[cls]]


def card_veins(c):
    """脉标签列表（中文）。空列表 → ['无']。"""
    vs = c.get('veins') or []
    return [CN_VEIN.get(v, v) for v in vs] if vs else ['无']


def vein_key(c):
    """脉列值：单脉返回脉名，多脉返回 '多脉(光+震)'。"""
    vs = card_veins(c)
    return vs[0] if len(vs) == 1 else '多脉(%s)' % '+'.join(vs)


def effect_types(c):
    """T403 判型规则：一张卡可归多类。
    - damage 或 hits → 伤害
    - block → 格挡
    - draw / energy / discard → 资源
    - special code ∈ {burn,poison,weak,frail} → 减益
    - special code ∈ {strength,dexterity,regenerate,thorns} → 增益
    （energy/discard 键当前卡池不存在，规则仍保留以便复算。）
    """
    e = c.get('effect') or {}
    t = []
    if e.get('damage') or e.get('hits'):
        t.append('伤害')
    if e.get('block'):
        t.append('格挡')
    if e.get('draw') or e.get('energy') or e.get('discard'):
        t.append('资源')
    codes = [s.get('code') for s in (e.get('special') or []) if isinstance(s, dict)]
    if any(cd in DEBUFF_CODES for cd in codes):
        t.append('减益')
    if any(cd in BUFF_CODES for cd in codes):
        t.append('增益')
    return t


def main_shape(c):
    """与 tools/dup_check.py 同一定义：主效果签名。"""
    e = c.get('effect') or {}
    target = e.get('target') or ''
    hits = e.get('hits') or 1
    keys = tuple(sorted(k for k in e if k not in ('target', 'hits')))
    for k in ('damage', 'block', 'draw', 'heal', 'resonance_gain'):
        if e.get(k):
            return (keys, k, int(e[k]), target, hits)
    sp = e.get('special') or []
    if sp:
        s0 = sp[0] if isinstance(sp[0], dict) else {'code': sp[0]}
        v = s0.get('value', s0.get('v', 0))
        return (keys, 'special:' + str(s0.get('code')), int(v or 0), target, hits)
    return (keys, None, 0, target, hits)


def effect_fp(c):
    """完全撞指纹：effect 规范化 JSON（与 tools/dup_check.py 的 fp 相同）。"""
    return json.dumps(c.get('effect') or {}, sort_keys=True, ensure_ascii=False)


def dup_scan(pairs=None):
    """全 219 张两两查重（与 tools/dup_check.py 同判据，但范围是全部卡而非仅通用×职业）。
    返回 (exact_groups, near_groups)：
      exact_groups: [(签名, [(cls,id,name), ...]), ...] 仅保留 ≥2 成员的组
      near_groups: 同上，近似撞（键集合同 + 主种类同 + 主数值差≤2 + target/hits 同）
    """
    pairs = pairs or all_cards()
    exact, near = defaultdict(list), defaultdict(list)
    for cls, c in pairs:
        exact[effect_fp(c)].append((cls, c))
        near[main_shape(c)].append((cls, c))
    exact = {k: v for k, v in exact.items() if len(v) >= 2}
    near = {k: v for k, v in near.items() if len(v) >= 2}
    return exact, near


def load_raw_cards():
    p = GAME / 'data' / 'audit' / 'raw_cards.json'
    return json.loads(p.read_text(encoding='utf-8'))


def raw_vs_json_diffs():
    """比对 cards/*.json（权威）与 web/index.html RAW 的卡数据。
    返回 [(id, cls, [字段差异描述...]), ...]，只列有差异的卡。
    比对字段：name/type/rarity/veins/energy/effect/cost_type/cost_text/flavor/upgrade。
    """
    raw = load_raw_cards()
    diffs = []
    for cls in CLASSES:
        jmap = {c['id']: c for c in load_cards()[cls]}
        rmap = {c['id']: c for c in raw.get(cls) or []}
        for cid in sorted(set(jmap) | set(rmap)):
            if cid not in jmap:
                diffs.append((cid, CN_CLASS[cls], ['RAW 有、json 无']))
                continue
            if cid not in rmap:
                diffs.append((cid, CN_CLASS[cls], ['json 有、RAW 无']))
                continue
            d = []
            j, r = jmap[cid], rmap[cid]
            for f in ('name', 'type', 'rarity', 'veins', 'energy',
                      'effect', 'cost_type', 'cost_text', 'flavor', 'upgrade'):
                if json.dumps(j.get(f), sort_keys=True, ensure_ascii=False) != \
                   json.dumps(r.get(f), sort_keys=True, ensure_ascii=False):
                    d.append(f)
            if d:
                diffs.append((cid, CN_CLASS[cls], d))
    return diffs


def one_line(c):
    """效果一句话：直接复用 tools/card_desc.describe_card（CARD_EFFECTS_AUTO.md 同源）。"""
    return describe_card(c)
