# -*- coding: utf-8 -*-
"""查敌人意图（intent）支持哪几种类型，有没有「给玩家塞牌」的能力。"""
import io
lines = open('web/index.html', encoding='utf-8').read().split('\n')
pats = ['it.type', "case 'attack'", "case 'defend'", "case 'buff'", "case 'debuff'",
        'enemyAct', 'function enemyTurn', 'drawPile.push', 'discardPile.push']
out = io.StringIO()
for i, ln in enumerate(lines, 1):
    if len(ln) > 800:
        continue
    for p in pats:
        if p in ln:
            out.write('%5d | %s\n' % (i, ln.strip()[:170]))
            break
open('tools/_intent_check.txt', 'w', encoding='utf-8').write(out.getvalue())
print('done')
