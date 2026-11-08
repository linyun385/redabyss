# -*- coding: utf-8 -*-
"""点 ZCode 输入框右下角的发送按钮（Enter 在这个界面不触发发送）。

★ 2026-11-05 23:26 实测重校准。窗口 1875×1439，按钮圆心在原截图 (1710, 1353)，
  窗口内相对坐标 = (1710/1875, 1353/1439) = (0.912, 0.940)。

  旧值是 (0.944, 0.983) → (1770, 1414)，往右下偏了 60 px，会点到按钮外面。
  那个值是估的，没校准过。别再信注释里写的「已校准」。

  校准方法：截图 → 裁右下角 260×180 → 放大 4 倍 → 量圆心 → 除以窗口尺寸。
"""
import sys, io, time, ctypes
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
GAME = Path(r'C:\Users\Administrator\Desktop\杂七杂八\红渊\game')
sys.path.insert(0, str(GAME / 'tools'))
import zwin
from PIL import ImageGrab

SEND_BTN = (0.912, 0.940)   # 2026-11-05 23:26 实测，见文件头注释

user32 = ctypes.windll.user32
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004


def click_at(x, y):
    user32.SetCursorPos(int(x), int(y))
    time.sleep(0.15)
    user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.06)
    user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)


def main():
    hwnd = zwin.find_zcode()
    if not hwnd:
        print('找不到 ZCode 窗口')
        return 2
    l, t, r, b = zwin.rect(hwnd)
    print('窗口:', zwin.title(hwnd), (l, t, r, b), '尺寸', (r - l, b - t))
    zwin.force_foreground(hwnd)
    time.sleep(0.8)
    x, y = zwin.pt(hwnd, *SEND_BTN)
    print('点发送按钮 (%d, %d)' % (x, y))
    click_at(x, y)
    time.sleep(3)
    ImageGrab.grab(bbox=(l, t, r, b)).save(str(GAME / 'tools' / '_nudge_clicked.png'))
    print('截图: tools/_nudge_clicked.png')
    return 0


if __name__ == '__main__':
    sys.exit(main())
