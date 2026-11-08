# -*- coding: utf-8 -*-
"""把磁盘上已有、但不在 art_manifest.json 里的图补进清单，让评审页能显示。
只做追加，不改既有条目；改前先备份。用法：python tools/_manifest_add.py [--apply]
"""
import json
import shutil
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
GAME = Path(__file__).resolve().parents[1]
TOOLS = GAME / 'tools'
MAN = TOOLS / 'art_manifest.json'
ART = GAME / 'web' / 'assets' / 'art'
CAT = GAME / 'data' / 'art_catalog.json'
PROMPTS = GAME / 'data' / 'zh_prompts_full.json'

ECO = {'enemy_': 'foe', 'event_': 'evt', 'anm_': 'card_anmin', 'cng_': 'card_cangmin',
       'dive_': 'card_diver', 'trm_': 'card_tremor'}


def eco_of(i):
    for p, e in ECO.items():
        if i.startswith(p):
            return e
    return 'other'


def main():
    apply = '--apply' in sys.argv
    m = json.loads(MAN.read_text(encoding='utf-8'))
    entries = m['entries']
    have = {e['id'] for e in entries}
    names = {r['id']: r.get('name', '') for r in
             json.loads(CAT.read_text(encoding='utf-8'))} if CAT.exists() else {}
    prompts = {r['id']: r['prompt'] for r in
               json.loads(PROMPTS.read_text(encoding='utf-8'))} if PROMPTS.exists() else {}

    add = []
    for p in sorted(ART.glob('*.webp')):
        i = p.stem
        if i in have:
            continue
        add.append({'id': i, 'out': p.name, 'eco': eco_of(i), 'lang': 'zh',
                    'obj': names.get(i, ''), 'prompt': prompts.get(i, ''),
                    'negative': '', 'size': [1024, 1024], 'seed': 0})

    print('清单现有 %d 条；磁盘上未收录 %d 条' % (len(entries), len(add)))
    for a in add[:6]:
        print('  + %-16s %-14s %s' % (a['id'], a['eco'], a['obj']))
    if len(add) > 6:
        print('  ...')
    if not apply:
        print('\n(演练模式，加 --apply 才真写)')
        return 0

    bak = MAN.with_suffix('.json.bak')
    shutil.copy2(MAN, bak)
    entries.extend(add)
    MAN.write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding='utf-8')
    print('\n已写入，共 %d 条；备份 → %s' % (len(entries), bak.name))
    return 0


if __name__ == '__main__':
    sys.exit(main())
