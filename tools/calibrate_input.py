# -*- coding: utf-8 -*-
"""校准会话态输入框坐标：粘贴一段测试文字（不回车），截图，然后清空。

用法：python tools/calibrate_input.py 0.45 0.893
"""
import ctypes
import sys
import time
from pathlib import Path

GAME = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(GAME / 'tools'))
import zwin
import pyperclip
from PIL import ImageGrab

u = ctypes.windll.user32
TEST = '坐标校准测试（不要发送）'


def key(vk, up=False):
    u.keybd_event(vk, 0, 2 if up else 0, 0)


def click_at(x, y):
    u.SetCursorPos(int(x), int(y))
    time.sleep(0.12)
    u.mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(0.05)
    u.mouse_event(0x0004, 0, 0, 0, 0)


def main():
    rx = float(sys.argv[1]) if len(sys.argv) > 1 else 0.45
    ry = float(sys.argv[2]) if len(sys.argv) > 2 else 0.893
    h = zwin.find_zcode()
    zwin.force_foreground(h)
    time.sleep(0.5)
    x, y = zwin.pt(h, rx, ry)
    print('click', x, y)
    click_at(x, y)
    time.sleep(0.6)
    pyperclip.copy(TEST)
    time.sleep(0.3)
    key(0x11); key(0x56); key(0x56, True); key(0x11, True)   # ctrl+v
    time.sleep(1.0)
    l, t, r, b = zwin.rect(h)
    ImageGrab.grab(bbox=(l, t, r, b)).save(str(GAME / 'tools' / '_calib_paste.png'))
    # 清空，别把测试文字留在框里
    time.sleep(0.3)
    key(0x11); key(0x41); key(0x41, True); key(0x11, True)
    time.sleep(0.2)
    key(0x2E); key(0x2E, True)
    print('pasted + cleared, shot saved')


if __name__ == '__main__':
    main()
