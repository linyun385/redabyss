# -*- coding: utf-8 -*-
"""设计包验收：把 GLM 写的 docs/design/*.md 机械校验。

三项最关键：
  1. 引用的卡 id 必须真实存在（防止编造"这两张卡重复"）
  2. [文件:行号] 必须真实存在
  3. 禁用词 —— 尤其是「整体来看」「比较均衡」这类等于没说的话

用法：
  python tools/check_design_refs.py
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

GAME = Path(__file__).resolve().parents[1]
DESIGN = GAME / 'docs' / 'design'

MIN_CHARS = 2500

BANNED = ['以此类推', '类似地', '限于篇幅', '不再赘述', 'TODO', '待补', '这里省略',
          '整体来看', '比较均衡', '存在重复', '有待加强', '建议优化', '暂略']

REF_RE = re.compile(r'\[([^\[\]\s]+\.(?:html|js|mjs|json|py|md|css)):(\d+)(?:\s*[-–]\s*(\d+))?\]')

PREFER = {'index.html': ['web'], 'core.js': ['engine']}

REQUIRED = {
    'T320_MECHANISMS.md': ['职业', '机制'],
    'T321_REDUNDANCY.md': ['重复', '升级'],
    'T322_MONOTONY.md': ['诊断', '方向'],
    'T323_RULES.md': ['共振', '凝视', '能量'],
    'T324_GAPS.md': ['空白'],
}


def resolve(name):
    name = name.replace('\\', '/')
    if '/' in name:
        for base in (GAME, DESIGN):
            p = base / name
            if p.exists():
                return p
    for d in PREFER.get(name, []):
        p = GAME / d / name
        if p.exists():
            return p
    hits = [p for p in GAME.rglob(name) if p.is_file() and 'node_modules' not in p.parts]
    return sorted(hits, key=lambda p: len(p.parts))[0] if hits else None


def real_card_ids():
    ids = set()
    for p in GAME.glob('cards/*.json'):
        for c in json.loads(p.read_text(encoding='utf-8')):
            ids.add(c['id'])
    for f in ('enemies/all.json', 'events/all.json', 'relics/all.json'):
        p = GAME / f
        if p.exists():
            for r in json.loads(p.read_text(encoding='utf-8')):
                ids.add(r['id'])
    return ids


CARD_ID_RE = re.compile(r'\b((?:dive|trem|anm|cng|enemy|event|relic)_[0-9a-z_]+)\b')


def check(md, known):
    txt = md.read_text(encoding='utf-8')
    issues = []

    # 1. 卡 id 真实性
    used = set(CARD_ID_RE.findall(txt))
    fake = sorted(i for i in used if i not in known)

    # 2. 文件行号
    bad_refs = []
    for fname, a, b in REF_RE.findall(txt):
        p = resolve(fname)
        if not p:
            bad_refs.append((fname, a, '文件不存在'))
            continue
        try:
            n = len(p.read_text(encoding='utf-8', errors='replace').split('\n'))
        except Exception as e:
            bad_refs.append((fname, a, '读不了'))
            continue
        if int(a) < 1 or (int(b) if b else int(a)) > n:
            bad_refs.append((fname, a, '行号越界（%d 行）' % n))

    # 3. 禁用词
    banned = [(w, txt.count(w)) for w in BANNED if w in txt]

    # 4. 字数
    body = re.sub(r'```.*?```', '', txt, flags=re.S)
    body = re.sub(r'[|`#*\-\s]', '', body)
    chars = len(body)

    # 5. 必备内容
    miss = [w for w in REQUIRED.get(md.name, []) if w not in txt]

    return {
        'file': md.name, 'ids': len(used), 'refs': len(REF_RE.findall(txt)),
        'chars': chars, 'fake': fake, 'bad_refs': bad_refs,
        'banned': banned, 'miss': miss,
        'ok': not (fake or bad_refs or banned or miss or chars < MIN_CHARS),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--min', type=int, default=MIN_CHARS)
    ap.add_argument('--dir', default='', help='要检查的目录（默认 docs/design）')
    a = ap.parse_args()

    global DESIGN
    if a.dir:
        DESIGN = (GAME / a.dir) if not Path(a.dir).is_absolute() else Path(a.dir)

    if not DESIGN.exists():
        print('! docs/design/ 还不存在 —— 任务还没产出。')
        return 1
    mds = [m for m in sorted(DESIGN.glob('*.md')) if not m.name.startswith('_')]
    if not mds:
        print('! docs/design/ 是空的。')
        return 1

    known = real_card_ids()
    print('# 设计包验收（库里真实 id 共 %d 个）\n' % len(known))
    print('| 文件 | 引用 id | 文件引用 | 字数 | 结论 |')
    print('|---|---|---|---|---|')
    rs = [check(m, known) for m in mds]
    for r in rs:
        print('| %s | %d | %d | %d | %s |'
              % (r['file'], r['ids'], r['refs'], r['chars'], '✅' if r['ok'] else '❌'))
    print()

    for r in rs:
        if r['ok']:
            continue
        print('## %s' % r['file'])
        if r['chars'] < a.min:
            print('- 篇幅不足：%d < %d' % (r['chars'], a.min))
        if r['fake']:
            print('- **库里不存在的 id** %d 个（编造或抄错）：' % len(r['fake']))
            for i in r['fake'][:12]:
                print('  - `%s`' % i)
        if r['bad_refs']:
            print('- 文件引用对不上 %d 处：' % len(r['bad_refs']))
            for f, ln, why in r['bad_refs'][:10]:
                print('  - `%s:%s` → %s' % (f, ln, why))
        if r['banned']:
            print('- 禁用词：%s' % '、'.join('%s×%d' % x for x in r['banned']))
        if r['miss']:
            print('- 缺必备内容：%s' % '、'.join(r['miss']))
        print()

    nok = sum(1 for r in rs if r['ok'])
    print('**通过 %d / %d**' % (nok, len(rs)))
    return 0 if nok == len(rs) else 1


if __name__ == '__main__':
    sys.exit(main())
