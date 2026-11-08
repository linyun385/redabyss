# -*- coding: utf-8 -*-
"""查 buffs（力量/敏捷/荆棘/再生）在哪初始化、哪清零 —— 判断是不是整场有效。"""
import io
lines = open('web/index.html', encoding='utf-8').read().split('\n')
pats = ['buffs = ', 'buffs:', 'buffs=','regen', 'newCombat', 'startCombat', 'function beginTurn']
out = io.StringIO()
for i, ln in enumerate(lines, 1):
    if len(ln) > 800:
        continue
    for p in pats:
        if p in ln:
            out.write('%5d | %s\n' % (i, ln.strip()[:160]))
            break
open('tools/_buffs_check.txt', 'w', encoding='utf-8').write(out.getvalue())
print('done')
