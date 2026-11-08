# -*- coding: utf-8 -*-
"""发送一条消息到 ZCode 新任务。用法：python send_t1.py "消息" [home|session]"""
import sys, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r'D:\idv_datamine_isolated\tools')
import night_watch as nw
from PIL import ImageGrab
from pathlib import Path

text = sys.argv[1] if len(sys.argv) > 1 else ''
where = sys.argv[2] if len(sys.argv) > 2 else 'auto'

hwnd = nw.find_window()
if not hwnd:
    print('no window'); sys.exit(1)

layout, info = nw.detect_layout(hwnd)
print('layout before:', layout)
if where == 'auto':
    ratio = nw.HOME_BOX_RATIO if layout == 'home' else nw.INPUT_BOX_RATIO
else:
    ratio = nw.HOME_BOX_RATIO if where == 'home' else nw.INPUT_BOX_RATIO
print('using ratio:', ratio)

ok = nw.send_text(text, False, ratio)
print('send_text ->', ok)

time.sleep(6)
layout2, info2 = nw.detect_layout(hwnd)
busy, binfo = nw.detect_busy(hwnd)
print('layout after:', layout2, '| busy:', busy, binfo)

l, t, r, b = nw.window_rect(hwnd)
img = ImageGrab.grab(bbox=(l, t, r, b))
out = Path(__file__).parent / '_shot_sent.png'
img.save(out)
print('saved', out)
