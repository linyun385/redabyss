# -*- coding: utf-8 -*-
"""查 exhaust / retain 在 playCard 里怎么处理（special 里的 code 认不认）。"""
import io
lines = open('web/index.html', encoding='utf-8').read().split('\n')
out = io.StringIO()
for i, ln in enumerate(lines, 1):
    if len(ln) > 800:
        continue
    if 'exhaust' in ln or "_locked" in ln:
        out.write('%5d | %s\n' % (i, ln.strip()[:170]))
open('tools/_exhaust_check.txt', 'w', encoding='utf-8').write(out.getvalue())
print('done')
