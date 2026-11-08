import re
from pathlib import Path
wb = Path('docs/ART_PROMPT_WORKBOOK.md')
lines = wb.read_text(encoding='utf-8').split('\n')
kind = None
out = []
changed = 0
for l in lines:
    if l.startswith('### 敌人'): kind = 'foe'
    elif l.startswith('### 卡牌'): kind = 'card'
    elif l.startswith('### 事件'): kind = 'event'
    elif l.startswith('## '): kind = None
    if kind and re.match(r'^>\s+(a|an|the)\s', l, re.I):
        body = l[1:].strip()
        add = []
        if 'lit from below' not in body.lower():
            add.append('lit from below by a red glow rising from the floor')
        if kind in ('foe', 'card') and not re.search(r'upside down|inverted|hanging|belly-up|underside', body, re.I):
            add.append('hanging inverted, feeding organs on the underside')
        if add:
            body = body.rstrip('.') + ', ' + ', '.join(add)
            changed += 1
        l = '> ' + body
    out.append(l)
wb.write_text('\n'.join(out), encoding='utf-8')
print('给样板补固定尾巴：', changed, '条')
