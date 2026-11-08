# -*- coding: utf-8 -*-
"""CSS 机器级审计 → 输出统计摘要（供 04_css_audit.md 引用）
统计 web/index.html 样式块的：魔法数字/变量引用/!important/内联style/重复规则
可复算：python tools/sim/css_audit.py
"""
import re, collections
from pathlib import Path

GAME = Path(__file__).resolve().parents[2]
html = (GAME / 'web' / 'index.html').read_text(encoding='utf-8')

# 提取样式块
css_start = html.index('<style>') + len('<style>')
css_end = html.index('</style>')
css = html[css_start:css_end]

# 提取 HTML body 的内联 style
body = html[html.index('<body>'):html.index('<script>')]
inline_styles = re.findall(r'style="([^"]*)"', body)

# 1. 魔法数字 px（非变量、非 calc 内）
px_vals = re.findall(r'(?<![\w-])(\d+(?:\.\d+)?)px', css)
px_counter = collections.Counter(px_vals)

# 2. CSS 变量
var_defs = re.findall(r'--[\w-]+\s*:', css)
var_refs = re.findall(r'var\(--[\w-]+\)', css)

# 3. !important
importants = re.findall(r'!important', css)

# 4. 内联 style
inline_count = len(inline_styles)
inline_cursors = sum(1 for s in inline_styles if 'cursor' in s)
inline_bgs = sum(1 for s in inline_styles if 'background' in s)

# 5. 选择器块
selectors = re.findall(r'([^{}]+)\{', css)
selector_count = len([s for s in selectors if s.strip() and not s.strip().startswith('/*')])

# 6. 重复属性组（简化：统计 background+border-color 组合出现次数）
bg_border = len(re.findall(r'background.*;.*border-color|border-color.*;.*background', css))

print('CSS lines:', css_end - css_start)
print('selector blocks:', selector_count)
print('px values total:', len(px_vals), '| unique:', len(px_counter))
print('top 10 px:', px_counter.most_common(10))
print('var defs:', len(var_defs), '| var refs:', len(var_refs))
print('!important:', len(importants))
print('inline styles:', inline_count, '(cursor:', inline_cursors, '/ bg:', inline_bgs, ')')
print('bg+border-color pairs:', bg_border)
