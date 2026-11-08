# -*- coding: utf-8 -*-
"""把 ZCode 还原到前台并截图。只还原 + 截图，不发任何东西。

用法：
  python tools/_zcode_restore_shot.py
"""
import sys, io, time
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
GAME = Path(r'C:\Users\Administrator\Desktop\杂七杂八\红渊\game')
sys.path.insert(0, str(GAME / 'tools'))
import zwin
from PIL import ImageGrab


def main():
    h = zwin.find_zcode()
    if not h:
        print('找不到 ZCode 窗口')
        return 2
    before = zwin.rect(h)
    print('还原前 rect:', before, '最小化:', bool(zwin._u.IsIconic(h)))

    ok = zwin.force_foreground(h)
    time.sleep(1.2)

    l, t, r, b = zwin.rect(h)
    print('还原后 rect:', (l, t, r, b), '尺寸:', (r - l, b - t))
    print('force_foreground 返回:', ok)
    print('当前前台就是它:', zwin.foreground() == h)

    if r - l < 600 or b - t < 400:
        print('!! 窗口尺寸异常，可能还是最小化')
        return 3

    p = GAME / 'tools' / '_zcode_now.png'
    ImageGrab.grab(bbox=(l, t, r, b)).save(str(p))
    print('截图:', p)
    return 0


if __name__ == '__main__':
    sys.exit(main())
