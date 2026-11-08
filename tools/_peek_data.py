# -*- coding: utf-8 -*-
"""看三个数据文件的结构：字段名 + 样本，输出尽量短。"""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
GAME = Path(__file__).resolve().parents[1]


def peek(rel, n=2):
    p = GAME / rel
    d = json.loads(p.read_text(encoding='utf-8'))
    print('\n==== %s ====' % rel)
    if isinstance(d, dict):
        print('顶层是 dict，键:', list(d.keys())[:12])
        for k in list(d.keys())[:2]:
            v = d[k]
            print(' [%s] 类型 %s' % (k, type(v).__name__))
            if isinstance(v, list) and v:
                print('  条数 %d，首条字段: %s' % (len(v), list(v[0].keys())))
                print('  样本:', json.dumps(v[0], ensure_ascii=False)[:400])
            elif isinstance(v, dict):
                print('  子键:', list(v.keys())[:12])
    elif isinstance(d, list):
        print('顶层是 list，条数 %d，首条字段: %s' % (len(d), list(d[0].keys()) if d else None))
        for x in d[:n]:
            print('  样本:', json.dumps(x, ensure_ascii=False)[:400])


peek('enemies/all.json')
peek('events/all.json')
peek('cards/anmin.json')
