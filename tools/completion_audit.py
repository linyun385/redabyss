# -*- coding: utf-8 -*-
"""完成度体检：把「完成度」数成数字，别靠感觉。

数的是**盘上真实存在的东西**，不读任何文档里的自述。
每次改完内容重跑一次，看数字有没有往前走。

用法：
  python tools/completion_audit.py            # 打印摘要 + 写 docs/COMPLETION_AUDIT.md
  python tools/completion_audit.py --brief    # 只打印摘要，不写文件
"""
import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
GAME = Path(__file__).resolve().parents[1]
DOCS = GAME / 'docs'
OUT = DOCS / 'COMPLETION_AUDIT.md'


def load(p):
    try:
        return json.loads((GAME / p).read_text(encoding='utf-8'))
    except Exception as e:
        print('!! 读不了 %s : %s' % (p, e))
        return None


def artset():
    """art/ 目录里真实存在的图（webp），id = 文件名去掉扩展名。"""
    s = {}
    for d in ('web/assets/art', 'art/versions'):
        p = GAME / d
        if not p.exists():
            continue
        for f in p.glob('*.webp'):
            key = re.sub(r'_v\d+$', '', f.stem)
            s.setdefault(key, set()).add(d)
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--brief', action='store_true')
    ap.add_argument('--vs', action='store_true', help='加一节对标（读 data/benchmarks.json）')
    a = ap.parse_args()

    cards = {}
    for p in sorted(GAME.glob('cards/*.json')):
        d = load(p.relative_to(GAME).as_posix()) or []
        cards[p.stem] = d
    enemies = {p.stem: (load(p.relative_to(GAME).as_posix()) or [])
               for p in sorted(GAME.glob('enemies/*.json'))}
    events = {p.stem: (load(p.relative_to(GAME).as_posix()) or [])
              for p in sorted(GAME.glob('events/*.json'))}
    relics = {}
    for p in sorted(GAME.glob('relics/*.json')):
        relics[p.stem] = load(p.relative_to(GAME).as_posix()) or []
    layers = (load('layers/layers.json') or {}).get('layers', [])
    cat = load('data/art_catalog.json') or []
    art = artset()

    foe_all = enemies.get('all', [])
    evt_all = events.get('all', [])
    rel_all = relics.get('all', [])

    L = []          # markdown 行
    S = {}          # 摘要数字

    def h(s=''):
        L.append(s)

    def num(x):
        return '{:,}'.format(x)

    # ── 卡池 ─────────────────────────────────────────
    h('# 完成度体检 — 红渊')
    h()
    h('> 生成时间：**%s**　|　口径：只数磁盘上真实存在的条目，不读任何文档自述。'
      % datetime.now().strftime('%Y-%m-%d %H:%M'))
    h('> 重跑：`python tools/completion_audit.py`')
    h()
    h('## 一、卡池')
    h()
    h('| 职业 | 卡数 | 攻击 | 技能 | 能力 | 普通 | 稀有 | 有升级 | 有正文 | 有图 |')
    h('|---|---|---|---|---|---|---|---|---|---|')
    card_ids = set()
    tot = Counter()
    for cls, d in cards.items():
        ids = {c['id'] for c in d}
        card_ids |= ids
        t = Counter(c.get('type') for c in d)
        r = Counter(c.get('rarity') for c in d)
        up = sum(1 for c in d if c.get('upgrade'))
        txt = sum(1 for c in d if (c.get('flavor') or '').strip())
        img = sum(1 for c in d if c['id'] in art)
        h('| %s | %d | %d | %d | %d | %d | %d | %d | %d | %d |'
          % (cls, len(d), t.get('attack', 0), t.get('skill', 0), t.get('power', 0),
             r.get('common', 0), r.get('rare', 0) + r.get('uncommon', 0),
             up, txt, img))
        tot.update({'n': len(d), 'up': up, 'txt': txt, 'img': img})
    h('| **合计** | **%d** | | | | | | **%d** | **%d** | **%d** |'
      % (tot['n'], tot['up'], tot['txt'], tot['img']))
    h()
    S['卡牌'] = (tot['n'], tot['img'])
    missing_card_art = sorted(card_ids - set(art))
    if missing_card_art:
        h('**缺图卡牌 %d 张**：`%s`%s'
          % (len(missing_card_art), '`, `'.join(missing_card_art[:12]),
             ' …' if len(missing_card_art) > 12 else ''))
        h()

    # ── 敌人 ─────────────────────────────────────────
    h('## 二、敌人')
    h()
    by_layer = Counter(e.get('layer') for e in foe_all)
    by_tier = Counter(e.get('tier') for e in foe_all)
    foe_img = sum(1 for e in foe_all if e['id'] in art)
    h('| 项 | 值 |')
    h('|---|---|')
    h('| 总数 | %d |' % len(foe_all))
    h('| 按层 | %s |' % ('　'.join('L%s:%d' % (k, v) for k, v in sorted(by_layer.items(), key=lambda x: (x[0] is None, x[0])))))
    h('| 按档 | %s |' % ('　'.join('%s:%d' % (k, v) for k, v in by_tier.most_common())))
    h('| 有图 | %d / %d（%.0f%%） |' % (foe_img, len(foe_all), 100.0 * foe_img / max(1, len(foe_all))))
    h()
    S['敌人'] = (len(foe_all), foe_img)

    # ── 事件 ─────────────────────────────────────────
    h('## 三、事件')
    h()
    ev_layer = Counter(e.get('layer') for e in evt_all)
    opt = Counter(len(e.get('options') or []) for e in evt_all)
    ev_img = sum(1 for e in evt_all if e['id'] in art)
    h('| 项 | 值 |')
    h('|---|---|')
    h('| 总数 | %d |' % len(evt_all))
    h('| 按层 | %s |' % ('　'.join('L%s:%d' % (k, v) for k, v in sorted(ev_layer.items(), key=lambda x: (x[0] is None, x[0])))))
    h('| 选项数分布 | %s |' % ('　'.join('%d 选项:%d' % (k, v) for k, v in sorted(opt.items()))))
    h('| 有图 | %d / %d（%.0f%%） |' % (ev_img, len(evt_all), 100.0 * ev_img / max(1, len(evt_all))))
    h()
    S['事件'] = (len(evt_all), ev_img)

    # ── 遗物 ─────────────────────────────────────────
    h('## 四、遗物')
    h()
    rel_rar = Counter(r.get('rarity') for r in rel_all)
    rel_img = sum(1 for r in rel_all if r['id'] in art)
    h('| 项 | 值 |')
    h('|---|---|')
    h('| 总数 | %d |' % len(rel_all))
    h('| 稀有度 | %s |' % ('　'.join('%s:%d' % (k, v) for k, v in rel_rar.most_common())))
    h('| 有专属图 | %d / %d |' % (rel_img, len(rel_all)))
    h()
    S['遗物'] = (len(rel_all), rel_img)

    # ── 地图 ─────────────────────────────────────────
    h('## 五、地图')
    h()
    h('| 层 | 名称 | 节点 |')
    h('|---|---|---|')
    for x in layers:
        h('| %s | %s | %d |' % (x.get('id'), x.get('name'), len(x.get('nodes') or [])))
    h()
    S['层数'] = len(layers)
    S['层节点'] = sum(len(x.get('nodes') or []) for x in layers)

    # ── 美术总账 ─────────────────────────────────────
    h('## 六、美术总账')
    h()
    kind = Counter(c.get('kind') for c in cat)
    have = sum(1 for c in cat if c['id'] in art)
    vers = sum(len(v) for v in art.values() if 'art/versions' in v)
    h('| 项 | 值 |')
    h('|---|---|')
    h('| 素材条目 | %d（card %d / foe %d / evt %d） |'
      % (len(cat), kind.get('card', 0), kind.get('foe', 0), kind.get('evt', 0)))
    h('| 已有正图 | %d / %d（%.0f%%） |' % (have, len(cat), 100.0 * have / max(1, len(cat))))
    h('| 备选图 | %s 张 |' % num(vers))
    h('| 孤儿图（有图无条目） | %d |'
      % len([k for k in art if k not in {c['id'] for c in cat} and k not in card_ids]))
    h()

    # ── 结局 ─────────────────────────────────────────
    endings = []
    ep = DOCS / 'ENDINGS.md'
    if ep.exists():
        t = ep.read_text(encoding='utf-8')
        # 只认「## 一、xxx」且紧接着一行出现「触发条件」的小节 —— 那才是真结局。
        # 文档里还有「## 五、多周目」「## localStorage 键名」这种说明性小节，不能算。
        for m in re.finditer(r'^## [一二三四五六七八九十]+、(.+)$', t, re.M):
            tail = t[m.end():m.end() + 400]
            if '触发条件' in tail:
                endings.append(m.group(1).split('（')[0].strip())
    h('## 七、结局')
    h()
    h('| 项 | 值 |')
    h('|---|---|')
    h('| 结局数 | %d |' % len(endings))
    h('| 清单 | %s |' % ('、'.join(endings) if endings else '（未解析到）'))
    h()
    S['结局'] = len(endings)

    # ── 一句话总账 ───────────────────────────────────
    content_total = tot['n'] + len(foe_all) + len(evt_all)
    art_total = tot['img'] + foe_img + ev_img
    h('## 八、总账')
    h()
    h('| 维度 | 现状 |')
    h('|---|---|')
    h('| 可玩内容条目 | %d（卡 %d + 敌 %d + 事 %d + 遗物 %d） |'
      % (content_total + len(rel_all), tot['n'], len(foe_all), len(evt_all), len(rel_all)))
    h('| 有图的条目 | %d / %d（%.0f%%） |'
      % (art_total, content_total, 100.0 * art_total / max(1, content_total)))
    h('| 地图 | %d 层 / %d 节点 |' % (S['层数'], S['层节点']))
    h('| 结局 | %d |' % S['结局'])
    h()
    h('> **这些是「有多少」，不是「好不好」。** 好不好只能人来打分 → `docs/SCORECARD.md`')
    h()

    # ── 对标 ─────────────────────────────────────────
    bench = load('data/benchmarks.json') or {}
    if a.vs and bench:
        h('## 九、对标（vs %s）'
          % '、'.join(v.get('name', k) for k, v in bench.items() if not k.startswith('_')))
        h()
        mine = {
            'classes': len(cards),
            'cards': tot['n'],
            'relics': len(rel_all),
            'enemies': len(foe_all),
            'events': len(evt_all),
            'acts': len(layers),
            'nodes': sum(len(x.get('nodes') or []) for x in layers),
            'endings': S['结局'],
        }
        label = {'classes': '角色', 'cards': '卡牌', 'relics': '遗物', 'enemies': '敌人',
                 'events': '事件', 'acts': '幕/层', 'nodes': '地图节点', 'endings': '结局'}
        refs = [(k, v) for k, v in bench.items() if not k.startswith('_')]
        for key, ref in refs:
            h('**%s**' % ref.get('name', key))
            h()
            h('| 指标 | 红渊 | %s | 比值 | 对方数据把握度 |' % ref.get('name', key))
            h('|---|---|---|---|---|')
            for m, cn in label.items():
                r = ref.get('metrics', {}).get(m) or {}
                rv = r.get('v')
                mv = mine.get(m)
                if rv is None:
                    h('| %s | %s | 待核 | — | unknown |' % (cn, num(mv)))
                else:
                    ratio = (mv / rv * 100.0) if rv else 0
                    h('| %s | %s | %s | %.0f%% | %s |'
                      % (cn, num(mv), num(rv), ratio, r.get('conf', '?')))
            h()

        # 比例对照：只有比例才跨游戏可比。绝对值受规模影响。
        # ★ 分母用「地图节点」而不是「幕/层」—— 杀戮尖塔一「幕」约 15 个节点，
        #   红渊一「层」只有 7 个，拿层做分母是把两种东西当同一种量。
        h('### 结构性比例（这个才可比）')
        h()
        sts = bench.get('slay_the_spire', {}).get('metrics', {})
        try:
            sv = {k: sts[k]['v'] for k in sts if sts[k].get('v')}
            nodes = mine['nodes'] or 1
            pairs = [
                ('卡 / 角色', tot['n'] / max(1, len(cards)),
                 sv['cards'] / sv['classes'] if 'cards' in sv and 'classes' in sv else None,
                 '每职业卡池深度'),
                ('敌 / 地图节点', len(foe_all) / nodes,
                 sv['enemies'] / sv['nodes'] if 'enemies' in sv and 'nodes' in sv else None,
                 '一地方面对多少种敌人'),
                ('事件 / 地图节点', len(evt_all) / nodes,
                 sv['events'] / sv['nodes'] if 'events' in sv and 'nodes' in sv else None,
                 '一地方面对多少种事件'),
                ('遗物 / 卡', len(rel_all) / max(1, tot['n']),
                 sv['relics'] / sv['cards'] if 'relics' in sv and 'cards' in sv else None,
                 '每张卡背后有多少遗物在联动'),
            ]
            h('| 比例 | 红渊 | 杀戮尖塔 | 相对 | 这一项在问什么 |')
            h('|---|---|---|---|---|')
            for name, mv, rv, why in pairs:
                if rv is None:
                    h('| %s | %.2f | 待核 | — | %s |' % (name, mv, why))
                else:
                    d = (mv / rv - 1) * 100
                    tag = '偏低' if d < -10 else ('偏高' if d > 10 else '接近')
                    h('| %s | %.2f | %.2f | %+.0f%%（%s） | %s |' % (name, mv, rv, d, tag, why))
            h()
        except Exception as e:
            h('（比例对照算不出来：%s）' % e)
            h()

        # 每角色明细：平均数会掩盖分布，分布才是要做的事
        h('### 每角色卡池（平均数会骗人）')
        h()
        target = sts.get('cards', {}).get('v', 0) / sts.get('classes', {}).get('v', 1) \
            if sts.get('cards', {}).get('v') and sts.get('classes', {}).get('v') else None
        h('| 职业 | 卡数 | 对标每角色 | 差 |')
        h('|---|---|---|---|')
        for cls, d in cards.items():
            if target:
                dlt = len(d) - target
                h('| %s | %d | %.0f | %+d |' % (cls, len(d), target, dlt))
            else:
                h('| %s | %d | 待核 | — |' % (cls, len(d)))
        h()

        h('### ★ 这些百分比不能加总')
        h()
        h('「幕数 8 vs 3 = 267%」不是完成度，是设计选择 —— 幕越多不等于越完成。'
          '同理结局数、角色数偏高都不代表更好。')
        h()
        h('**能当完成度看的**：卡牌、遗物这类「本该铺满但可能还没铺满」的内容量。')
        h('**不能当完成度看的**：幕数、结局数、角色数 —— 那是设计意图，不达标叫「设计不同」不叫「没做完」。')
        h()
        h('所以不要找一个「综合完成度 %」—— 那个数一定是假的。要看的是'
          '**哪一项偏低**，而且偏低的是不是你以为已经做完的那一项。')
        h()

    text = '\n'.join(L)
    print(text)

    if not a.brief:
        OUT.write_text(text, encoding='utf-8')
        print('\n→ 已写 %s' % OUT.relative_to(GAME))
    return 0


if __name__ == '__main__':
    sys.exit(main())
