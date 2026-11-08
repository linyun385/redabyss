# -*- coding: utf-8 -*-
"""新建 ZCode 任务并用可靠坐标发送第一条消息。"""
import sys, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r'C:\Users\Administrator\Desktop\杂七杂八\红渊\game\tools')
import zwin
import pyautogui, pyperclip
from PIL import ImageGrab

HOME_BOX = (0.58, 0.49)

msg = sys.argv[1] if len(sys.argv) > 1 else ''

hwnd = zwin.find_zcode()
if not hwnd:
    print('no window'); sys.exit(1)
print('hwnd:', hwnd, 'rect:', zwin.rect(hwnd))
if not zwin.force_foreground(hwnd):
    print('WARN foreground')
time.sleep(0.6)

# 新建任务
pyautogui.hotkey('ctrl', 'n')
time.sleep(3.0)

l, t, r, b = zwin.rect(hwnd)
img = ImageGrab.grab(bbox=(l, t, r, b))
img.save(r'C:\Users\Administrator\Desktop\杂七杂八\红渊\game\tools\_shot_newtask.png')
print('new task shot saved')

# 点首页输入框
x, y = zwin.pt(hwnd, *HOME_BOX)
print('home box at', x, y)
pyautogui.click(x, y)
time.sleep(0.5)

pyautogui.hotkey('ctrl', 'a')
pyautogui.press('delete')
time.sleep(0.2)

pyperclip.copy(msg)
time.sleep(0.2)
pyautogui.hotkey('ctrl', 'v')
time.sleep(0.7)

img2 = ImageGrab.grab(bbox=(l, t, r, b))
img2.save(r'C:\Users\Administrator\Desktop\杂七杂八\红渊\game\tools\_shot_pasted.png')
print('pasted shot saved')

pyautogui.press('enter')
time.sleep(8)

img3 = ImageGrab.grab(bbox=(l, t, r, b))
img3.save(r'C:\Users\Administrator\Desktop\杂七杂八\红渊\game\tools\_shot_sent2.png')
print('sent shot saved')
