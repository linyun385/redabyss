# -*- coding: utf-8 -*-
"""分步测试：点输入框 -> 粘贴 -> 截图（不回车）。用于校准输入框坐标。"""
import sys, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r'D:\idv_datamine_isolated\tools')
import night_watch as nw
import pyautogui, pyperclip
from PIL import ImageGrab
from pathlib import Path

TEXT = sys.argv[1] if len(sys.argv) > 1 else 'TEST_PASTE_中文测试'
RX = float(sys.argv[2]) if len(sys.argv) > 2 else 0.58
RY = float(sys.argv[3]) if len(sys.argv) > 3 else 0.49

hwnd = nw.find_window()
if not hwnd:
    print('no window'); sys.exit(1)
print('layout:', nw.detect_layout(hwnd))
if not nw.force_foreground(hwnd):
    print('cannot foreground'); sys.exit(1)
time.sleep(0.5)

l, t, r, b = nw.window_rect(hwnd)
x = int(l + RX * (r - l))
y = int(t + RY * (b - t))
print('click at', x, y)

pyautogui.click(x, y)
time.sleep(0.4)
pyperclip.copy(TEXT)
time.sleep(0.2)
pyautogui.hotkey('ctrl', 'v')
time.sleep(0.6)

img = ImageGrab.grab(bbox=(l, t, r, b))
out = Path(__file__).parent / '_shot_paste.png'
img.save(out)
print('saved', out)
print('clipboard:', repr(pyperclip.paste()[:40]))
