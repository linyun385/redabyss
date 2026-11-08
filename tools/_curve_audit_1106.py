# -*- coding: utf-8 -*-
"""卡牌数值曲线审计（2026-11-06 夜班 · 方向池 12）。

只读：web/index.html 的 RAW 数据段。
只写：docs/design/curves/curve_report_auto.md（脚本产出，含全部表格与离群清单）。

跑法（干跑即写文档，不碰任何数据）：
    python -I tools/_curve_audit_1106.py
"""
import io, os, re, json, statistics

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'docs', 'design', 'curves', 'curve_report_auto.md')
BANDS = ['0费', '1费', '2费', '3费+']

def load_raw():
    txt = io.open(os.path.join(ROOT, 'web', 'index.html'), encoding='utf-8').read()
    m = re.search(r'const RAW = (\{.*?\});\n', txt, re.S)
    return json.loads(m.group(1))

def card_band(en):
    if en <= 0: return '0费'
    if en == 1: return '1费'
    if en == 2: return '2费'
    return '3费+'

def effect_nums(card):
    """(damage_total, block, price_channels)。hits 计入；special 间接数值（灼烧等）与 power 增益不计。
    price_channels：能抵消数值的价格通道（静态可判定），供分拣用。"""
    e = card.get('effect') or {}
    dmg = (e.get('damage') or 0) * (e.get('hits') or 1)
    blk = e.get('block') or 0
    price = []
    if e.get('resonance_cost'): price.append('共振%s' % e['resonance_cost'])
    if e.get('gaze_cost'): price.append('凝视%s' % e['gaze_cost'])
    if card.get('cost_type', 'none') != 'none': price.append(card['cost_type'])
    if e.get('exhaust') or any(s.get('code') == 'exhaust' for s in e.get('special', [])): price.append('消耗')
    if card.get('dream'): price.append('梦世界')
    if e.get('draw'): price.append('抽%s' % e['draw'])
    if e.get('heal'): price.append('回%s' % e['heal'])
    for s in e.get('special', []):
        code = s.get('code')
        if code in ('exhaust', 'retain'): continue
        price.append('%s%s%s' % (code, s.get('value', '') or '', ('/t%s' % s['turns']) if s.get('turns') else ''))
    return dmg, blk, price

def fmt(x):
    return str(int(x)) if float(x) == int(x) else str(round(x, 1))

def b2e(band):
    return {'0费': 0.5, '1费': 1, '2费': 2, '3费+': 3}[band]  # 0费按半费折算，避免除零

def main():
    raw = load_raw()
    rows = []  # (cls, id, name, rarity, band, energy, dmg, blk)
    for cls in ('diver', 'tremor', 'anmin', 'cangmin', 'shared'):
        for c in raw.get(cls, []):
            dmg, blk, price = effect_nums(c)
            if dmg == 0 and blk == 0:
                continue
            en = c.get('energy', 0) or 0
            rows.append((cls, c['id'], c['name'], c.get('rarity', '?'), card_band(en), en, dmg, blk, price))

    stats = {}
    for b in BANDS:
        d = [r[6] for r in rows if r[4] == b and r[6] > 0]
        k = [r[7] for r in rows if r[4] == b and r[7] > 0]
        stats[b] = {
            'n_dmg': len(d), 'med_dmg': statistics.median(d) if d else 0,
            'n_blk': len(k), 'med_blk': statistics.median(k) if k else 0,
        }

    out = []
    out.append('# 卡牌数值曲线 · 脚本产出（自动生成，勿手改）')
    out.append('')
    out.append('> 由 `tools/_curve_audit_1106.py` 生成。数据源：`web/index.html` 的 RAW（含 anmin 同步副本）。')
    out.append('> 口径：damage × hits 为总伤；block 直接取；special 内的间接数值（灼烧/中毒/抽牌/回复）与 power 增益**不计**——只统计「打出即兑现」的伤/挡。带这些附加的卡会被口径低估，见分析文档的三色分拣。')
    out.append('> 样本：全部五类卡池中「打出即含伤或挡」的卡，共 %d 张。' % len(rows))
    out.append('')
    out.append('## 一、各费用档的中位数（全稀有度合并）')
    out.append('')
    out.append('| 档 | 伤害卡数 | 伤中位数 | 伤/能量中位 | 格挡卡数 | 挡中位数 | 挡/能量中位 |')
    out.append('|---|---|---|---|---|---|---|')
    for b in BANDS:
        s = stats[b]
        e = b2e(b)
        out.append('| %s | %d | %s | %.2f | %d | %s | %.2f |' % (
            b, s['n_dmg'], fmt(s['med_dmg']), (s['med_dmg'] / e if s['med_dmg'] else 0),
            s['n_blk'], fmt(s['med_blk']), (s['med_blk'] / e if s['med_blk'] else 0)))
    out.append('')
    out.append('## 一点五、分稀有度中位数（common / uncommon；rare 及以上样本太稀，不分层）')
    out.append('')
    out.append('| 档 | 稀有度 | 伤中位数 | 挡中位数 |')
    out.append('|---|---|---|---|')
    for b in BANDS:
        for rar in ('common', 'uncommon'):
            d = [r[6] for r in rows if r[4] == b and r[6] > 0 and r[3] == rar]
            k = [r[7] for r in rows if r[4] == b and r[7] > 0 and r[3] == rar]
            out.append('| %s | %s | %s | %s |' % (b, rar, fmt(statistics.median(d)) if d else '-', fmt(statistics.median(k)) if k else '-'))
    out.append('')
    out.append('## 二、偏离档位中位数 ±30% 的卡（全稀有度中位口径）')
    out.append('')
    out.append('| 类 | id | 名字 | 稀有度 | 档 | 费 | 伤 | 挡 | 偏离 | 方向 | 价格通道/附加 |')
    out.append('|---|---|---|---|---|---|---|---|---|---|---|')
    flagged = 0
    for cls, cid, name, rar, band, en, dmg, blk, price in rows:
        s = stats[band]
        e = b2e(band)
        if dmg > 0 and s['med_dmg']:
            dev = (dmg / s['med_dmg']) - 1
            if abs(dev) >= 0.30:
                out.append('| %s | %s | %s | %s | %s | %s | %s | - | %+.0f%% | %s | %s |' % (
                    cls, cid, name, rar, band, en, dmg, dev * 100, '偏低' if dev < 0 else '偏高', '、'.join(price) or '-'))
                flagged += 1
        if blk > 0 and s['med_blk']:
            dev = (blk / s['med_blk']) - 1
            if abs(dev) >= 0.30:
                out.append('| %s | %s | %s | %s | %s | %s | - | %s | %+.0f%% | %s | %s |' % (
                    cls, cid, name, rar, band, en, blk, dev * 100, '偏低' if dev < 0 else '偏高', '、'.join(price) or '-'))
                flagged += 1
    out.append('')
    out.append('离群条目合计：%d 条（一卡可因伤/挡各偏离各计一次）。' % flagged)
    io.open(OUT, 'w', encoding='utf-8').write('\n'.join(out) + '\n')
    print('写入 %s' % OUT)
    print('样本 %d 张，离群 %d 条' % (len(rows), flagged))

if __name__ == '__main__':
    main()
