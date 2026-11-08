# -*- coding: utf-8 -*-
"""用 zwin 的可靠坐标给 ZCode 发消息。用法：python send_now.py "消息" """
import sys, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r'C:\Users\Administrator\Desktop\杂七杂八\红渊\game\tools')
import zwin
import pyautogui, pyperclip
from PIL import ImageGrab

INPUT_BOX = (0.55, 0.92)

text = sys.argv[1] if len(sys.argv) > 1 else ''
dry = '--dry' in sys.argv

hwnd = zwin.find_zcode()
if not hwnd:
    print('no window'); sys.exit(1)
print('hwnd:', hwnd, 'rect:', zwin.rect(hwnd))

if not zwin.force_foreground(hwnd):
    print('WARN 拉不到前台，仍尝试')
time.sleep(0.6)

x, y = zwin.pt(hwnd, *INPUT_BOX)
print('input box at', x, y)
if dry:
    print('[dry] 不发送'); sys.exit(0)

pyautogui.click(x, y)
time.sleep(0.4)
print('foreground after click:', zwin.foreground() == hwnd)

# 清空残留
pyautogui.hotkey('ctrl', 'a')
time.sleep(0.1)
pyautogui.press('delete')
time.sleep(0.2)

pyperclip.copy(text)
time.sleep(0.2)
pyautogui.hotkey('ctrl', 'v')
time.sleep(0.7)

l, t, r, b = zwin.rect(hwnd)
img = ImageGrab.grab(bbox=(l, t, r, b))
img.save(r'C:\Users\Administrator\Desktop\杂七杂八\红渊\game\tools\_shot_pre_send.png')
print('pre-send shot saved')

pyautogui.press('enter')
time.sleep(4)

img2 = ImageGrab.grab(bbox=(l, t, r, b))
img2.save(r'C:\Users\Administrator\Desktop\杂七杂八\红渊\game\tools\_shot_post_send.png')
print('sent. post shot saved')
