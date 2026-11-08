# -*- coding: utf-8 -*-
"""把卡牌的 effect JSON 翻译成中文人话。

★ 唯一原则：按【引擎实际结算的代码】翻译，不按数据里写的字面翻译。
   两者不一致的地方，会在〔〕里点出来 —— 那是真 bug，不是笔误。

依据（web/index.html，2026-11-04 当天读过）：
  applyCardEffect  5807-5850   顶层键怎么结算
  applySpecial     5852-5879   special 各 code 怎么结算
  playCard 扣代价  5733-5734   resonance_cost 真的扣；gaze_cost 只查不扣（5709）
  upgradeCard      6330-6351   upgrade 是【逐键合并】，special 是【追加】
"""

# special code → 中文短名
SPECIAL_CN = {
    'burn': '灼烧', 'poison': '中毒', 'weak': '虚弱', 'frail': '脆弱',
    'strength': '力量', 'dexterity': '敏捷', 'regenerate': '再生', 'thorns': '荆棘',
    'resonance_lock': '共振锁定', 'gaze_reduce': '降低凝视', 'delete_random': '随机删牌',
    'exhaust': '消耗', 'rule_bypass': '无视层规则', 'retain': '保留',
}

# 这些 code 在 applySpecial 里读 sp.v，而卡片数据里写的是 value → 引擎取默认值
READS_V = ['burn', 'poison', 'strength', 'dexterity', 'regenerate', 'thorns', 'gaze_reduce']
DEFAULT_V = {'burn': 3, 'poison': 3, 'strength': 1, 'dexterity': 1,
             'regenerate': 2, 'thorns': 3, 'gaze_reduce': 1}


def _sp_val(sp, default):
    """2026-11-04 引擎已修：value 优先 → v → 默认值。
       返回 (实际值, 数据里写的值或 None)；现在两者应当一致。"""
    given = sp.get('value')
    if given is None:
        given = sp.get('v')
    return (default if given is None else given), given


def _desc_special(sps, flags=True):
    """翻译一个 special 列表 → 字符串列表。"""
    out = []
    for sp in (sps or []):
        if isinstance(sp, str):
            sp = {'code': sp}
        code = sp.get('code')
        if not code:
            continue

        if code in READS_V:
            real, given = _sp_val(sp, DEFAULT_V.get(code, 1))
            if code == 'gaze_reduce':
                s = '凝视 -%d' % real
            else:
                s = '%s +%d' % (SPECIAL_CN.get(code, code), real)
            if flags and given is not None and given != real:
                s += '〔数据写的是 %s，但引擎读不到这个字段，实际按 %d 算〕' % (given, real)
            out.append(s)

        elif code == 'burn':
            real, given = _sp_val(sp, 3)
            turns = sp.get('turns') or 3
            s = '给目标挂灼烧：每回合 %d 点，持续 %d 回合' % (real, turns)
            if flags and given is not None and given != real:
                s += '〔数据写的是 %s，实际按 %d 算〕' % (given, real)
            out.append(s)

        elif code == 'poison':
            real, _ = _sp_val(sp, 3)
            out.append('给目标挂中毒 %d' % real)

        elif code in ('weak', 'frail'):
            turns = sp.get('turns')
            if turns is None:
                turns = sp.get('value')
            if turns is None:
                turns = 2
            out.append('目标%s %d 回合' % (SPECIAL_CN[code], turns))

        elif code == 'resonance_lock':
            out.append('共振锁定（本场本层内共振不再增长）')
        elif code == 'delete_random':
            out.append('随机删掉牌库里的 1 张牌')
        elif code == 'exhaust':
            out.append('消耗：打出后本场战斗不再回来')
        elif code == 'rule_bypass':
            out.append('本回合无视这一层的层规则')
        elif code == 'retain':
            out.append('保留：回合结束不弃掉')
        else:
            out.append('［这版没实现的效果：%s］' % code)

    return out


def describe_card(card, flags=True):
    """整张卡（不含升级）→ 一句中文描述。"""
    e = card.get('effect') or {}
    out = []

    dmg = e.get('damage')
    if dmg:
        hits = e.get('hits') or 1
        s = '造成 %d 点伤害' % dmg
        if hits > 1:
            s += '，连打 %d 段（合计 %d）' % (hits, dmg * hits)
        s += '，对所有敌人' if e.get('target') == 'all' else '，对一个敌人'
        out.append(s)

    if e.get('block'):
        out.append('获得 %d 点格挡' % e['block'])
    if e.get('draw'):
        out.append('抽 %d 张牌' % e['draw'])
    if e.get('resonance_gain'):
        out.append('共振 +%d' % e['resonance_gain'])
    if e.get('resonance_drain'):
        out.append('共振 -%d' % e['resonance_drain'])
    if e.get('resonance_cost'):
        out.append('消耗共振 %d（不够就出不来）' % e['resonance_cost'])
    if e.get('gaze_cost'):
        out.append('需要凝视 ≥ %d（只查门槛，不扣）' % e['gaze_cost'])
    if e.get('gaze_gain'):
        out.append('凝视 +%d（危险值，越高越被盯上）' % e['gaze_gain'])
    if e.get('gaze_reduce'):
        out.append('凝视 -%d' % e['gaze_reduce'])
    if e.get('heal'):
        out.append('回复 %d 点生命' % e['heal'])

    out.extend(_desc_special(e.get('special'), flags))

    if not out:
        out.append('没有效果（纯白板）')
    return '　'.join(out)


def describe_upgrade(card, flags=True):
    """升级 = 在原 effect 上逐键合并（upgradeCard）：special 追加，其余覆盖。"""
    u = card.get('upgrade') or {}
    if not u:
        return ''
    parts = []
    if u.get('name_suffix'):
        parts.append('名字加「%s」' % u['name_suffix'])

    ue = u.get('effect') or {}
    changed = []
    # 非 special 键是直接覆盖原值
    for k, v in ue.items():
        if k == 'special':
            continue
        if k == 'damage':
            hits = ue.get('hits', (card.get('effect') or {}).get('hits') or 1)
            changed.append('伤害变成 %d%s' % (v, '，连打 %d 段（合计 %d）' % (hits, v * hits) if hits > 1 else ''))
        elif k == 'block':
            changed.append('格挡变成 %d' % v)
        elif k == 'draw':
            changed.append('抽牌变成 %d 张' % v)
        elif k == 'heal':
            changed.append('回复变成 %d' % v)
        elif k == 'hits':
            base = (card.get('effect') or {}).get('damage')
            if base:
                changed.append('段数变成 %d（当前合计 %d）' % (v, base * v))
            else:
                changed.append('段数变成 %d' % v)
        elif k == 'resonance_gain':
            changed.append('共振 +%d' % v)
        elif k == 'resonance_drain':
            changed.append('共振 -%d' % v)
        elif k == 'resonance_cost':
            changed.append('消耗共振 %d' % v)
        else:
            changed.append('%s 改成 %s' % (k, v))

    sp_add = ue.get('special')
    if isinstance(sp_add, list):
        if sp_add:
            changed.append('再追加：' + '　'.join(_desc_special(sp_add, flags)))
            changed.append('（追加是叠在原有上的，不是替换）')
        else:
            changed.append('清空原有 special')

    if changed:
        parts.append('；'.join(changed))
    if u.get('cost_type'):
        parts.append('代价类型改写成 %s' % u['cost_type'])
    if u.get('flavor_add'):
        parts.append('风味文本加一句')
    return '；'.join(parts)
