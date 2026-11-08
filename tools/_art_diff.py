# -*- coding: utf-8 -*-
"""对比三个 index.html 里的 window.ART 表，列出当前相对旧备份丢了哪些条目。"""
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
GAME = Path(r'C:\Users\Administrator\Desktop\杂七杂八\红渊\game')
WEB = GAME / 'web'

TAG = 'window.ART = '


def art_of(p):
    s = p.read_text(encoding='utf-8')
    i = s.find(TAG)
    if i < 0:
        return None
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
    return json.loads(s[start:end])


cur = art_of(WEB / 'index.html')
old1 = art_of(WEB / 'index.html.bak-20261104-205730-partsaccum')
old2 = art_of(WEB / 'index.html.bak-20261104-172409-energy4')

print('当前 ART 条目:', len(cur))
print('昨 20:57 备份:', len(old1) if old1 else 'N/A')
print('昨 17:24 备份:', len(old2) if old2 else 'N/A')

for name, old in (('20:57', old1), ('17:24', old2)):
    if not old:
        continue
    lost = sorted(set(old) - set(cur))
    add = sorted(set(cur) - set(old))
    print('\n相对 %s：丢了 %d 条，多了 %d 条' % (name, len(lost), len(add)))
    if lost:
        print('  丢的条目（前 40）：')
        for k in lost[:40]:
            print('   ', k, '->', old[k])
    if add:
        print('  多的条目（前 10）：', add[:10])

# 三张卡的 id：按中文名在 cards/*.json 里找
print('\n--- 按卡名找 id ---')
for cn in ('渊光重工·工作灯', '聚能枪', '震髓探测器'):
    hit = []
    for p in (GAME / 'cards').glob('*.json'):
        try:
            for c in json.loads(p.read_text(encoding='utf-8')):
                if c.get('name') == cn:
                    hit.append((c['id'], p.name))
        except Exception:
            pass
    print(cn, '->', hit)
