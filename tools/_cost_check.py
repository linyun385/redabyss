# -*- coding: utf-8 -*-
"""查 resonance_cost / gaze_cost 在 playCard 里有没有真的扣。"""
import io
lines = open('web/index.html', encoding='utf-8').read().split('\n')
out = io.StringIO()
for i, ln in enumerate(lines, 1):
    if len(ln) > 800:
        continue
    if 'resonance_cost' in ln or 'gaze_cost' in ln or 'resonance -=' in ln or 'gaze -=' in ln:
        out.write('%5d | %s\n' % (i, ln.strip()[:160]))
open('tools/_cost_check.txt', 'w', encoding='utf-8').write(out.getvalue())
print('done')
