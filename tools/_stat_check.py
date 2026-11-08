# -*- coding: utf-8 -*-
"""查敏捷 / 力量 / 格挡 的完整链路：加在哪、什么时候扣、会不会清零。"""
import io
lines = open('web/index.html', encoding='utf-8').read().split('\n')
pats = ['buffs.dexterity', 'buffs.strength', 'function gainBlock', 'buffs.thorns',
        'gainBlock(', 'C.block =', 'block = 0']
out = io.StringIO()
for i, ln in enumerate(lines, 1):
    if len(ln) > 800:
        continue
    for p in pats:
        if p in ln:
            out.write('%5d | %s\n' % (i, ln.strip()[:165]))
            break
open('tools/_stat_check.txt', 'w', encoding='utf-8').write(out.getvalue())
print('done')
