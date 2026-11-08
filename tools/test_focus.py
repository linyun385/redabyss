# -*- coding: utf-8 -*-
"""点击输入框并截图，验证坐标是否落在输入框上（不输入内容、不回车）。"""
import sys, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r'C:\Users\Administrator\Desktop\杂七杂八\红渊\game\tools')
import zwin
import pyautogui
from PIL import ImageGrab

hwnd = zwin.find_zcode()
if not hwnd:
    print('no window'); sys.exit(1)
print('hwnd:', hwnd, 'rect:', zwin.rect(hwnd))

if not zwin.force_foreground(hwnd):
    print('WARN: cannot foreground')
time.sleep(0.5)

x, y = zwin.pt(hwnd, 0.57, 0.91)
print('click at', x, y)
pyautogui.click(x, y)
time.sleep(0.8)

l, t, r, b = zwin.rect(hwnd)
img = ImageGrab.grab(bbox=(l, t, r, b))
out = r'C:\Users\Administrator\Desktop\杂七杂八\红渊\game\tools\_shot_focus.png'
img.save(out)
print('saved', out, img.size)
print('foreground is zcode:', zwin.foreground() == hwnd)
