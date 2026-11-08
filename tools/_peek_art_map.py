# -*- coding: utf-8 -*-
"""看敌人/职业/结局的图片 id 派生规则（写文件跑，避免 PowerShell 引号问题）。"""
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
s = (Path(__file__).resolve().parents[1] / 'web' / 'index.html').read_text(encoding='utf-8')

for key in ('ART[fid]', 'class_', 'end_', 'foeArtId', 'face_foe'):
    for m in re.finditer(re.escape(key), s):
        i = m.start()
        seg = s[max(0, i - 500):i + 160].replace('\n', ' ')
        print('===', key, '===')
        print(seg[-640:])
        print()
        break
