# -*- coding: utf-8 -*-
"""精确查：special 的 value 字段有没有被归一化成 v。跳过 RAW 那种超长行。"""
import re

lines = open('web/index.html', encoding='utf-8').read().split('\n')
print('总行数', len(lines))
pats = ['sp.value', 's.value', 'sp.v', 'normalize', "special ||", 'code === ', 'it.value', 'sp.v ||']
for i, ln in enumerate(lines, 1):
    if len(ln) > 800:
        continue
    for p in pats:
        if p in ln:
            print('%5d | %s' % (i, ln.strip()[:150]))
            break
