# -*- coding: utf-8 -*-
"""截 ZCode 窗口，存到 tools/_shot.png，用于人眼确认输入框状态。"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r'D:\idv_datamine_isolated\tools')
import night_watch as nw
from PIL import ImageGrab
from pathlib import Path

hwnd = nw.find_window()
if not hwnd:
    print('no window'); sys.exit(1)
l, t, r, b = nw.window_rect(hwnd)
print('rect:', l, t, r, b, 'size:', r - l, b - t)
try:
    nw.force_foreground(hwnd)
except Exception as e:
    print('foreground err:', e)
img = ImageGrab.grab(bbox=(l, t, r, b))
out = Path(__file__).parent / '_shot.png'
img.save(out)
print('saved:', out, img.size)
