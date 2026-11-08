# -*- coding: utf-8 -*-
"""清空输入框后用校准坐标发送。用法：python clear_send.py "消息" """
import sys, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r'D:\idv_datamine_isolated\tools')
import night_watch as nw
import pyautogui, pyperclip
from PIL import ImageGrab
from pathlib import Path

HOME_BOX = (0.58, 0.49)      # 2026-10-28 实测校准（旧常量 0.55 会落在按钮行）
SESSION_BOX = (0.60, 0.95)
sys.path.insert(0, r'C:\Users\Administrator\Desktop\杂七杂八\红渊\game\tools')
try:
    from night_drive import box_ratio
except Exception:
    box_ratio = lambda: SESSION_BOX

text = sys.argv[1] if len(sys.argv) > 1 else ''
hwnd = nw.find_window()
if not hwnd:
    print('no window'); sys.exit(1)
layout, _ = nw.detect_layout(hwnd)
ratio = HOME_BOX if layout == 'home' else box_ratio()
print('layout:', layout, 'ratio:', ratio)

if not nw.force_foreground(hwnd):
    print('cannot foreground'); sys.exit(1)
time.sleep(0.5)

l, t, r, b = nw.window_rect(hwnd)
x = int(l + ratio[0] * (r - l))
y = int(t + ratio[1] * (b - t))
pyautogui.click(x, y)
time.sleep(0.4)

# 清空已有内容
pyautogui.hotkey('ctrl', 'a')
time.sleep(0.1)
pyautogui.press('delete')
time.sleep(0.2)

pyperclip.copy(text)
time.sleep(0.2)
pyautogui.hotkey('ctrl', 'v')
time.sleep(0.6)

img = ImageGrab.grab(bbox=(l, t, r, b))
(out := Path(__file__).parent / '_shot_before_enter.png').parent.mkdir(exist_ok=True)
img.save(out)
print('saved pre-enter shot:', out)

pyautogui.press('enter')
time.sleep(8)

layout2, _ = nw.detect_layout(hwnd)
busy, binfo = nw.detect_busy(hwnd)
print('after enter -> layout:', layout2, '| busy:', busy, binfo)

img2 = ImageGrab.grab(bbox=(l, t, r, b))
out2 = Path(__file__).parent / '_shot_after_enter.png'
img2.save(out2)
print('saved:', out2)
