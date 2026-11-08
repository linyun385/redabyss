# -*- coding: utf-8 -*-
"""教学包验收：把 GLM 写的 docs/lesson/*.md 机械校验一遍。

不听自述，只认文件。四项检查：

  1. 引用真实性 —— 每一处 [文件:行号] 都要真的存在、行号在范围内、那一行不空
  2. 代码真实性 —— 每个 ```js 代码块必须逐字出现在源文件里（缩进差异忽略）
  3. 禁用词   —— 以此类推 / TODO / 待补 / 限于篇幅 …
  4. 篇幅     —— 正文（不含代码块）≥ MIN_CHARS 字

用法：
  python tools/check_lesson_refs.py
  python tools/check_lesson_refs.py --min 2000 --verbose
"""
import argparse
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

GAME = Path(__file__).resolve().parents[1]
LESSON = GAME / 'docs' / 'lesson'

MIN_CHARS = 3000

BANNED = ['以此类推', '类似地', '限于篇幅', '不再赘述', 'TODO', '待补',
          '这里省略', '详见后文', '暂略', '（略）']

REF_RE = re.compile(r'\[([^\[\]\s]+\.(?:html|js|mjs|json|py|md|css)):(\d+)(?:\s*[-–]\s*(\d+))?\]')
JS_BLOCK_RE = re.compile(r'```(?:js|javascript|html)?\s*\n(.*?)```', re.S)

# 常见文件名 → 优先在这些目录找
PREFER = {
    'index.html': ['web'],
    'core.js': ['engine'],
}

REQUIRED = {
    '00_MAP.md': ['顶层', '行'],
    '01_PLAY_CARD.md': ['流程'],
    '02_SYNTAX_BASIC.md': ['let', '函数', '对象', '循环', '模板'],
    '03_SYNTAX_PROJECT.md': ['闭包', '事件', 'localStorage', 'JSON'],
    '04_DATA.md': ['effect', '新卡'],
    '05_EXERCISE.md': ['验证', '撤'],
}


def resolve(name):
    """把 'index.html' 解析成项目里的真实路径。"""
    name = name.replace('\\', '/')
    # 已经是相对路径（含 /）就先按原样试
    if '/' in name:
        p = GAME / name
        if p.exists():
            return p
        # docs/lesson/02_x.md 这种自己引用自己
        p2 = LESSON / name
        if p2.exists():
            return p2
    for d in PREFER.get(name, []):
        p = GAME / d / name
        if p.exists():
            return p
    hits = [p for p in GAME.rglob(name) if p.is_file() and 'node_modules' not in p.parts]
    if hits:
        # 越短的路径越可能是权威源
        hits.sort(key=lambda p: len(p.parts))
        return hits[0]
    return None


def norm(s):
    """归一化成「逐行 strip 后拼接」，用来做忽略缩进的逐字比对。"""
    return '\n'.join(x.strip() for x in s.split('\n') if x.strip())


def check_file(md):
    txt = md.read_text(encoding='utf-8')
    lines = txt.split('\n')
    issues = []

    # ── 1. 引用真实性 ──────────────────────────────
    refs = REF_RE.findall(txt)
    bad_refs = []
    for fname, a, b in refs:
        p = resolve(fname)
        if not p:
            bad_refs.append((fname, a, '文件不存在'))
            continue
        try:
            src = p.read_text(encoding='utf-8', errors='replace').split('\n')
        except Exception as e:
            bad_refs.append((fname, a, '读不了：%s' % e))
            continue
        lo = int(a)
        hi = int(b) if b else lo
        if lo < 1 or hi > len(src):
            bad_refs.append((fname, a, '行号越界（该文件 %d 行）' % len(src)))
            continue
        chunk = ''.join(x.strip() for x in src[lo - 1:hi])
        if not chunk:
            bad_refs.append((fname, a, '指向空行'))

    # ── 2. 代码块真实性 ────────────────────────────
    blocks = JS_BLOCK_RE.findall(txt)
    fake_blocks = []
    for blk in blocks:
        nb = norm(blk)
        if len(nb) < 40:          # 太短的块（单行命令）不比
            continue
        found = False
        for fname, _, _ in refs:  # 只在本文引用过的文件里找
            p = resolve(fname)
            if not p:
                continue
            try:
                ns = norm(p.read_text(encoding='utf-8', errors='replace'))
            except Exception:
                continue
            if nb in ns:
                found = True
                break
        if not found:
            fake_blocks.append(blk.strip().split('\n')[0][:60])

    # ── 3. 禁用词 ──────────────────────────────────
    banned_hit = [(w, txt.count(w)) for w in BANNED if w in txt]

    # ── 4. 篇幅 ────────────────────────────────────
    body = JS_BLOCK_RE.sub('', txt)
    body = re.sub(r'[|`#*\-\s]', '', body)
    chars = len(body)

    # ── 5. 必备内容 ────────────────────────────────
    need = REQUIRED.get(md.name, [])
    missing = [w for w in need if w not in txt]

    return {
        'file': md.name,
        'refs': len(refs),
        'blocks': len(blocks),
        'chars': chars,
        'bad_refs': bad_refs,
        'fake_blocks': fake_blocks,
        'banned': banned_hit,
        'missing': missing,
        'ok': not (bad_refs or fake_blocks or banned_hit or chars < MIN_CHARS or missing),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--min', type=int, default=MIN_CHARS)
    ap.add_argument('--verbose', action='store_true')
    a = ap.parse_args()

    if not LESSON.exists():
        print('! docs/lesson/ 还不存在 —— 任务还没产出任何东西。')
        return 1
    mds = sorted(LESSON.glob('*.md'))
    mds = [m for m in mds if not m.name.startswith('_')]
    if not mds:
        print('! docs/lesson/ 是空的。')
        return 1

    print('# 教学包验收\n')
    print('| 文件 | 引用 | 代码块 | 正文字数 | 结论 |')
    print('|---|---|---|---|---|')
    results = [check_file(m) for m in mds]
    for r in results:
        flag = '✅' if r['ok'] else '❌'
        print('| %s | %d | %d | %d | %s |'
              % (r['file'], r['refs'], r['blocks'], r['chars'], flag))
    print()

    for r in results:
        if r['ok'] and not a.verbose:
            continue
        print('## %s' % r['file'])
        if r['chars'] < a.min:
            print('- 篇幅不足：%d < %d' % (r['chars'], a.min))
        if r['bad_refs']:
            print('- **引用对不上** %d 处：' % len(r['bad_refs']))
            for f, ln, why in r['bad_refs'][:12]:
                print('  - `%s:%s` → %s' % (f, ln, why))
        if r['fake_blocks']:
            print('- **代码块在源文件里找不到**（可能是编的）%d 处：' % len(r['fake_blocks']))
            for s in r['fake_blocks'][:8]:
                print('  - `%s`' % s)
        if r['banned']:
            print('- 禁用词：%s' % '、'.join('%s×%d' % x for x in r['banned']))
        if r['missing']:
            print('- 缺少必备内容：%s' % '、'.join(r['missing']))
        print()

    progress = LESSON / '_PROGRESS.md'
    if progress.exists():
        print('## 执行者自报进度（只作参考，不作结论）\n')
        print(progress.read_text(encoding='utf-8')[:1200])
        print()

    nok = sum(1 for r in results if r['ok'])
    print('**通过 %d / %d**' % (nok, len(results)))
    return 0 if nok == len(results) else 1


if __name__ == '__main__':
    sys.exit(main())
