# -*- coding: utf-8 -*-
import json, glob, sys, io
sys.path.insert(0, 'tools')
from card_desc import describe_card, describe_upgrade

want = {'dive_0001', 'anm_0035', 'cng_0025', 'cng_0038', 'anm_0039', 'cng_0037',
        'cng_0024', 'anm_0049', 'share_0001', 'cng_0018'}
out = io.StringIO()
n = 0
for f in sorted(glob.glob('cards/*.json')):
    for c in json.load(open(f, encoding='utf-8')):
        if c['id'] in want:
            n += 1
            out.write('=== %s %s ===\n' % (c['id'], c['name']))
            out.write('  %s\n' % describe_card(c))
            u = describe_upgrade(c)
            if u:
                out.write('  升级：%s\n' % u)
            out.write('  raw effect: %s\n' % json.dumps(c.get('effect'), ensure_ascii=False))
            out.write('\n')
open('tools/_desc_test.txt', 'w', encoding='utf-8').write(out.getvalue())
print('matched', n)
