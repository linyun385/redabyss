# -*- coding: utf-8 -*-
"""T71 代码级核验（utf-8 输出，避免 GBK 编码炸）。"""
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
GAME = Path(__file__).resolve().parents[1]
s = (GAME / 'web' / 'index.html').read_text(encoding='utf-8')

ids = sorted(set(re.findall(r'id="(mm-[^"]+)"', s)))
print('小图/总图相关 id:', ids)


def show(label, pat, n=200):
    m = re.search(pat, s)
    print('%-12s %s' % (label, re.sub(r'\s+', ' ', m.group(0))[:n] if m else '未找到'))


show('#mm-dock', r'#mm-dock\s*\{[^}]{0,240}')
show('#mm-log', r'#mm-log\s*\{[^}]{0,200}')

icon_m = re.search(r'ICON = \{([^}]*)\}', s)
print('ICON 表:', icon_m.group(1) if icon_m else '未找到')
print('八个图标都在:', all(g in s for g in ['⚔', '☠', '✧', '◈', '✉', '⌂', '◆', '◉']))

print('缩放 0.6/2 关键字:', s.count('0.6'), '/', s.count('2)'), '| clamp/zoom 代码:',
      len(re.findall(r'(?:scale|zoom)', s, re.I)), '处')
print('行程列表:', {k: s.count(k) for k in ['mm-log', '还没走过', '行程']})

i = s.find('==T56-MAP-MODULE==')
mod = s[i:]
print('新地图模块内禁字统计:', {ch: mod.count(ch) for ch in '战事随商英'})
print('未探明节点是否只报 ?:', mod.count("'?'"), '处', '| aria 未探明:', mod.count('未探明'))
