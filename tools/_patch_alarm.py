# -*- coding: utf-8 -*-
"""给 fire_watch.py 补 subprocess 导入与 --alarm 参数（写成文件跑，别用 python -c 内联）。"""
import ast
from pathlib import Path

GAME = Path(__file__).resolve().parents[1]
P = GAME / 'tools' / 'fire_watch.py'
s = P.read_text(encoding='utf-8')
changed = []

if 'import subprocess' not in s:
    for old in ('import sys, io, time, json, re, argparse, ctypes',
                'import sys, io, time, json, re, argparse'):
        if old in s:
            s = s.replace(old, old + ', subprocess', 1)
            changed.append('import subprocess')
            break
    else:
        s = 'import subprocess\n' + s
        changed.append('import subprocess (top)')

if "'--alarm'" not in s:
    anchor = "    ap.add_argument('--once', action='store_true')"
    add = (
        "    ap.add_argument('--alarm', default='once', choices=['off', 'once', 'loud'],\n"
        "                    help='停摆时用声音叫你：off=不响；once=短报警；loud=长报警'\n"
        "                         '（同一晚第 2 次停摆起自动升级成 loud）')\n"
    )
    if anchor in s:
        s = s.replace(anchor, add + anchor, 1)
        changed.append('--alarm')
    else:
        raise SystemExit('找不到 --once 锚点')

ast.parse(s)
P.write_text(s, encoding='utf-8')
print('changed:', changed)
print('alarm in args:', "'--alarm'" in s)
