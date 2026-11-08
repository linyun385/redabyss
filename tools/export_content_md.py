# -*- coding: utf-8 -*-
"""把卡牌 / 敌人 / 事件 / 遗物 导成可读、可查、可批注的 md（全中文）。

为什么要有这一步：
  JSON 能读但不能扫，设计者要「具体查具体调」，需要在表格里一眼看到
  「这个职业有哪些机制」「哪些卡作用一样」。
  而且基础表必须由脚本生成 —— 手抄会漏行、会抄错数值。

术语以 docs/GLOSSARY.md 为准（共鸣、五脉、凝视…），不要自己起译名。
id 保留英文原样 —— 那是定位用的。

产出：docs/content/*.md
用法：python tools/export_content_md.py
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
GAME = Path(__file__).resolve().parents[1]
OUT = GAME / 'docs' / 'content'

# ── 中英对照（术语取自 docs/GLOSSARY.md） ─────────────────────
CN = {
    # 卡牌类型
    'attack': '攻击', 'skill': '技能', 'power': '能力',
    # 稀有度
    'common': '普通', 'uncommon': '罕见', 'rare': '稀有',
    'special': '特殊', 'boss': '首领',
    # 五脉
    'light': '光脉', 'water': '水脉', 'heat': '热脉',
    'tremor': '震脉', 'mineral': '矿脉',
    # 代价类型
    'none': '无', 'vitality': '体力', 'lock': '每层一次',
    'memory': '记忆', 'mark': '标记',
    # 机制
    'block': '格挡', 'damage': '伤害', 'draw': '抽牌', 'heal': '治疗',
    'resonance_gain': '共鸣+', 'resonance_cost': '共鸣→', 'resonance_drain': '共鸣流失',
    'gaze_cost': '凝视→', 'gaze_gain': '凝视+',
    # special 效果码
    'special:regenerate': '再生', 'special:strength': '力量',
    'special:dexterity': '敏捷', 'special:burn': '灼烧',
    'special:retain': '保留', 'special:resonance_lock': '共鸣锁定',
    'special:exhaust': '消耗', 'special:thorns': '荆棘',
    'special:weak': '虚弱', 'special:frail': '脆弱',
    'special:poison': '中毒', 'special:delete_random': '随机删牌',
    'special:gaze_reduce': '凝视-',
    # 目标
    'self': '自身', 'single': '单体', 'all': '全体', 'random': '随机',
    # 敌人
    'normal': '普通', 'elite': '精英',
    'defend': '防御', 'buff': '强化', 'debuff': '削弱',
    # 效果字段
    'hits': '段', 'amount': '量', 'times': '次',
}

# effect 里这些 key 是「参数」不是「机制」
PARAMS = {'target', 'value', 'n', 'amount', 'times', 'x', 'self', 'all', 'random',
          'hits',    # 伤害段数，是 damage 的参数
          'turns',   # 持续回合，是所属效果的参数
          }


def cn(x, default=None):
    if x is None:
        return default if default is not None else '—'
    s = str(x)
    return CN.get(s, s)


def load(p):
    return json.loads((GAME / p).read_text(encoding='utf-8'))


def flat_effect(e):
    """把 effect 压成一行中文 + 中文机制标签集合。

    ★ special 数组里的 code 是真正的机制来源（消耗/再生/中毒…），
      必须展开成独立标签，否则 76 张卡的差异全被压成一个键。
    """
    if not e:
        return '—', set()
    tags = set()
    parts = []

    def walk(d):
        if isinstance(d, dict):
            for k, v in d.items():
                if k in PARAMS:
                    continue
                if k == 'special' and isinstance(v, list):
                    for sp in v:
                        if isinstance(sp, dict) and sp.get('code'):
                            tags.add('special:' + str(sp['code']))
                    continue
                if isinstance(v, (dict, list)):
                    walk(v)
                else:
                    key = cn(k)
                    val = CN.get(str(v), v) if isinstance(v, str) else v
                    tags.add(k)
                    parts.append('%s %s' % (key, val))
        elif isinstance(d, list):
            for x in d:
                walk(x)

    walk(e)
    # 射程/段数补在后面，方便读
    extra = []
    if isinstance(e, dict):
        if e.get('target'):
            extra.append(cn(e['target']))
        if e.get('hits') and e.get('hits') != 1:
            extra.append('%s 段' % e['hits'])
    body = '，'.join(parts) if parts else '—'
    if extra:
        body += '（%s）' % '，'.join(extra)
    return body, tags


def esc(s):
    return (s or '').replace('|', '｜').replace('\n', ' ').strip()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    cards = {p.stem: load('cards/%s.json' % p.stem) for p in GAME.glob('cards/*.json')}
    foes = load('enemies/all.json')
    evts = load('events/all.json')
    rels = load('relics/all.json')

    mech_by_class = {}
    idx_rows = []

    # ── 卡牌：每职业一份 ────────────────────────────────
    for cls, deck in sorted(cards.items()):
        L = ['# 卡牌 · %s（%d 张）' % (cn(cls) if cls not in ('diver', 'tremor', 'anmin', 'cangmin') else
                                      {'diver': '下潜者', 'tremor': '震语者',
                                       'anmin': '维护者', 'cangmin': '疯先知'}[cls], len(deck)), '',
             '> 从 `cards/%s.json` 导出，脚本生成，勿手改。' % cls,
             '> 「机制」列用来找同类卡和重复卡；「效果」是一行摘要，精确数值看 json。', '',
             '| id | 名字 | 类型 | 稀有度 | 费 | 机制 | 效果 | 正文 |',
             '|---|---|---|---|---|---|---|---|']
        mech = Counter()
        for c in deck:
            eff, tags = flat_effect(c.get('effect'))
            mech.update(tags)
            mtxt = '、'.join(cn(t) for t in sorted(tags)) or '—'
            L.append('| `%s` | %s | %s | %s | %s | %s | %s | %s |' % (
                c['id'], esc(c.get('name')), cn(c.get('type')), cn(c.get('rarity')),
                c.get('energy', ''), mtxt, esc(eff), esc(c.get('flavor'))[:40]))
            if c.get('cost_type') and c['cost_type'] != 'none':
                L.append('| | | *代价：%s* | | | | | |' % cn(c['cost_type']))
        L.append('')
        L.append('## 机制频次')
        L.append('')
        L.append('| 机制 | 出现次数 |')
        L.append('|---|---|')
        for k, v in mech.most_common():
            L.append('| %s | %d |' % (cn(k), v))
        L.append('')
        (OUT / ('cards_%s.md' % cls)).write_text('\n'.join(L), encoding='utf-8')
        mech_by_class[cls] = mech
        idx_rows.append(('cards_%s.md' % cls, '%s · %d 张' % (
            {'diver': '下潜者', 'tremor': '震语者', 'anmin': '维护者',
             'cangmin': '疯先知'}[cls], len(deck))))

    # ── 敌人 ────────────────────────────────────────
    L = ['# 敌人（%d 个）' % len(foes), '',
         '> 从 `enemies/all.json` 导出。「意图模式」按顺序循环，如「攻击 2 → 攻击 2 → 防御 3」。', '']
    by_layer = defaultdict(list)
    for e in foes:
        by_layer[e.get('layer')].append(e)
    for lay in sorted(by_layer, key=lambda x: (x is None, x)):
        L.append('## 第 %s 带（%d 个）' % (lay, len(by_layer[lay])))
        L.append('')
        L.append('| id | 名字 | 档 | 生命 | 意图模式 | 特性 |')
        L.append('|---|---|---|---|---|---|')
        for e in by_layer[lay]:
            pat = ' → '.join('%s %s' % (cn(i.get('type')), i.get('value', ''))
                             for i in e.get('intent_pattern') or []) or '—'
            L.append('| `%s` | %s | %s | %s | %s | %s |' % (
                e['id'], esc(e.get('name')), cn(e.get('tier')), e.get('hp', ''),
                esc(pat), esc('、'.join(e.get('traits') or [])) or '—'))
        L.append('')
    (OUT / 'enemies.md').write_text('\n'.join(L), encoding='utf-8')
    idx_rows.append(('enemies.md', '敌人 · %d 个' % len(foes)))

    # ── 事件 ────────────────────────────────────────
    L = ['# 事件（%d 个）' % len(evts), '',
         '> 从 `events/all.json` 导出。每个事件一节，选项逐条列出。', '']
    by_layer = defaultdict(list)
    for e in evts:
        by_layer[e.get('layer')].append(e)
    for lay in sorted(by_layer, key=lambda x: (x is None, x)):
        L.append('## 第 %s 带（%d 个）' % (lay, len(by_layer[lay])))
        L.append('')
        for e in by_layer[lay]:
            L.append('### `%s`　%s' % (e['id'], esc(e.get('title'))))
            L.append('')
            L.append('> %s' % esc(e.get('body')))
            L.append('')
            for i, o in enumerate(e.get('options') or [], 1):
                veins = '、'.join(cn(v) for v in (o.get('veins') or [])) or '—'
                res = o.get('result') or {}
                rs = '，'.join('%s %s' % (cn(k), v) for k, v in res.items()) or '无'
                L.append('%d. **%s**　〔%s〕→ %s' % (i, esc(o.get('text')), veins, esc(rs)))
                if o.get('result_text'):
                    L.append('   - %s' % esc(o['result_text']))
            L.append('')
    (OUT / 'events.md').write_text('\n'.join(L), encoding='utf-8')
    idx_rows.append(('events.md', '事件 · %d 个' % len(evts)))

    # ── 遗物 ────────────────────────────────────────
    L = ['# 遗物（%d 个）' % len(rels), '',
         '> 从 `relics/all.json` 导出。注意：遗物**没有专属图**，只有文字。', '',
         '| id | 名字 | 稀有度 | 脉 | 效果 | 正文 |',
         '|---|---|---|---|---|---|']
    for r in rels:
        L.append('| `%s` | %s | %s | %s | %s | %s |' % (
            r['id'], esc(r.get('name')), cn(r.get('rarity')),
            '、'.join(cn(v) for v in (r.get('veins') or [])) or '—',
            esc(r.get('effect_text')), esc(r.get('flavor'))[:30]))
    L.append('')
    (OUT / 'relics.md').write_text('\n'.join(L), encoding='utf-8')
    idx_rows.append(('relics.md', '遗物 · %d 个' % len(rels)))

    # ── 机制对照 ─────────────────────────────────────
    allmech = set()
    for m in mech_by_class.values():
        allmech |= set(m)
    hdr = {'diver': '下潜者', 'tremor': '震语者', 'anmin': '维护者', 'cangmin': '疯先知'}
    L = ['# 机制对照表', '',
         '> 同一行 = 同一个机制在各职业里的使用次数。',
         '> **只有一格非零 = 孤立机制；多职业都用 = 通用语言。**', '',
         '| 机制 | ' + ' | '.join(hdr[c] for c in sorted(cards)) + ' | 合计 |',
         '|---|' + '---|' * (len(cards) + 1)]
    for mech in sorted(allmech, key=lambda k: -sum(m.get(k, 0) for m in mech_by_class.values())):
        row = [mech_by_class[c].get(mech, 0) for c in sorted(cards)]
        L.append('| %s | %s | %d |' % (cn(mech), ' | '.join(str(x) for x in row), sum(row)))
    L.append('')
    (OUT / 'mechanisms.md').write_text('\n'.join(L), encoding='utf-8')
    idx_rows.append(('mechanisms.md', '机制对照 · %d 种' % len(allmech)))

    # ── 索引 ────────────────────────────────────────
    L = ['# 内容总表（脚本生成）', '',
         '> 由 `tools/export_content_md.py` 从 `cards/`、`enemies/`、`events/`、`relics/` 导出。',
         '> **数据变了要重跑脚本，不要手改这些文件。**', '',
         '| 文件 | 内容 |', '|---|---|']
    for f, d in idx_rows:
        L.append('| [%s](%s) | %s |' % (f, f, d))
    L += ['', '## 怎么用', '',
          '1. 查某张卡 → 打开对应职业的表，`Ctrl+F` 搜 id 或名字',
          '2. 想知道「某个机制被几个职业用」→ 看 mechanisms.md',
          '3. 想改 → **改 json，不要改 md**，改完重跑本脚本', '',
          '## 名词', '',
          '术语以 `docs/GLOSSARY.md` 为准。本表里的换算：', '',
          '| 原值 | 显示为 |', '|---|---|']
    for k, v in CN.items():
        L.append('| `%s` | %s |' % (k, v))
    L.append('')
    (OUT / 'README.md').write_text('\n'.join(L), encoding='utf-8')

    print('导出到 docs/content/：')
    for f in sorted(OUT.glob('*.md')):
        print('  %-18s %6d 字' % (f.name, len(f.read_text(encoding='utf-8'))))
    print()
    print('机制总数：%d' % len(allmech))
    solo = [m for m in allmech if sum(x.get(m, 0) for x in mech_by_class.values()) == 1]
    print('只用过一次的孤立机制：%d 个 %s' % (len(solo), '、'.join(cn(x) for x in sorted(solo))))
    return 0


if __name__ == '__main__':
    sys.exit(main())
