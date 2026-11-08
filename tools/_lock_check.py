# -*- coding: utf-8 -*-
"""查 cost_type='lock' 的 _locked 到底锁多久：谁设、谁清、deck 在战斗间怎么复制。"""
import io
lines = open('web/index.html', encoding='utf-8').read().split('\n')
pats = ['_locked', 'deck:', 'run.deck', 'deck =', 'deepCopy', 'JSON.parse(JSON.stringify']
out = io.StringIO()
for i, ln in enumerate(lines, 1):
    if len(ln) > 800:
        continue
    for p in pats:
        if p in ln:
            out.write('%5d | %s\n' % (i, ln.strip()[:170]))
            break
open('tools/_lock_check.txt', 'w', encoding='utf-8').write(out.getvalue())
print('done')
