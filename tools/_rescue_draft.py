# -*- coding: utf-8 -*-
"""从清理时的备份里把被覆盖的「命运的旧日左轮」捞回来。
只补 name / design_note / upgrade_note 三个字段，别的（你后来改的）一律不动。"""
import json, shutil, time
from pathlib import Path

GAME = Path(__file__).resolve().parents[1]
P = GAME / 'cards' / '_draft.json'
BAK = GAME / 'cards' / '_draft.json.bak-20261104-132059'

d = json.loads(P.read_text(encoding='utf-8'))
b = json.loads(BAK.read_text(encoding='utf-8'))

old = None
for o in b.get('ops', []):
    if o.get('id') == 'u_00xx':
        old = o.get('card')
        break

if not old:
    print('备份里也没找到 u_00xx，只能手工重建')
    raise SystemExit(1)

shutil.copy2(P, P.with_name('_draft.json.bak-rescue-' + time.strftime('%Y%m%d-%H%M%S')))

fixed = 0
for o in d.get('ops', []):
    if o.get('id') == 'u_00xx':
        c = o.setdefault('card', {})
        c['name'] = old.get('name')
        c['design_note'] = old.get('design_note', '')
        c['upgrade_note'] = old.get('upgrade_note', '')
        fixed += 1

P.write_text(json.dumps(d, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
print('restored ops:', fixed)
print('name now =', [c.get('card', {}).get('name') for c in d['ops'] if c.get('id') == 'u_00xx'])
print('note now =', [c.get('card', {}).get('design_note') for c in d['ops'] if c.get('id') == 'u_00xx'])
