# -*- coding: utf-8 -*-
"""修复被 art_sync 砍掉的 ART 表：用昨天 552 条的完整表 + 当前 79 条合并后写回。

合并策略：旧表为底，当前表里旧表没有的键补进去（只增不删）。
默认 dry-run，加 --apply 才写。
"""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
GAME = Path(r'C:\Users\Administrator\Desktop\杂七杂八\红渊\game')
WEB = GAME / 'web'
TAG = 'window.ART = '


def art_of(p):
    s = p.read_text(encoding='utf-8')
    i = s.find(TAG)
    start = s.find('{', i)
    depth = 0
    for k in range(start, len(s)):
        if s[k] == '{':
            depth += 1
        elif s[k] == '}':
            depth -= 1
            if depth == 0:
                return json.loads(s[start:k + 1])


def write_art(p, table):
    s = p.read_text(encoding='utf-8')
    i = s.find(TAG)
    start = s.find('{', i)
    depth = 0
    for k in range(start, len(s)):
        if s[k] == '{':
            depth += 1
        elif s[k] == '}':
            depth -= 1
            if depth == 0:
                end = k + 1
                break
    body = json.dumps(table, ensure_ascii=False, separators=(',', ':'))
    p.write_text(s[:start] + body + s[end:], encoding='utf-8')


old = art_of(WEB / 'index.html.bak-20261104-205730-partsaccum')
cur = art_of(WEB / 'index.html')
merged = dict(old)
only_cur = [k for k in cur if k not in merged]
for k in only_cur:
    merged[k] = cur[k]

print('旧表 %d 条，当前 %d 条，合并后 %d 条（当前独有 %d 条）'
      % (len(old), len(cur), len(merged), len(only_cur)))

missing_files = []
for k, v in merged.items():
    if not (WEB / v).exists():
        missing_files.append((k, v))
print('表里指向但磁盘缺失的文件:', len(missing_files))
for k, v in missing_files[:10]:
    print('   ', k, '->', v)

if '--apply' in sys.argv:
    import shutil
    bak = WEB / ('index.html.bak-%s-arterfix' % __import__('time').strftime('%Y%m%d-%H%M%S'))
    shutil.copy2(WEB / 'index.html', bak)
    write_art(WEB / 'index.html', merged)
    print('已写回，备份:', bak.name)
    print('写回后条目:', len(art_of(WEB / 'index.html')))
else:
    print('(dry-run，加 --apply 才写)')
