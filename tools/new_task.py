# -*- coding: utf-8 -*-
"""新建 ZCode 任务（干净上下文），供红渊项目使用。"""
import sys, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r'D:\idv_datamine_isolated\tools')
import night_watch as nw
import pyautogui
from PIL import ImageGrab
from pathlib import Path

hwnd = nw.find_window()
if not hwnd:
    print('no window'); sys.exit(1)
if not nw.force_foreground(hwnd):
    print('cannot foreground'); sys.exit(1)
time.sleep(0.6)

print('before: layout =', nw.detect_layout(hwnd))
pyautogui.hotkey('ctrl', 'n')
time.sleep(2.5)

l, t, r, b = nw.window_rect(hwnd)
img = ImageGrab.grab(bbox=(l, t, r, b))
out = Path(__file__).parent / '_shot_new.png'
img.save(out)
print('saved', out)
print('after: layout =', nw.detect_layout(hwnd))
