# -*- coding: utf-8 -*-
"""给 ZCode 会话说一句话：粘进去，先不回车，截图验证后再发。

为什么不用 send_robust.py：那个脚本的输入框坐标是 10-30 校准的，
窗口布局变了就点偏（它自己的注释里记着踩过的坑）。
这里改成"窗口内比例坐标 + 先 dry 后发"，每次都能截图确认。

用法：
  python tools/glm_nudge.py --text "..."        # 只粘贴不发送
  python tools/glm_nudge.py --text "..." --send # 粘贴后回车
"""
import sys, io, time, argparse, ctypes
from ctypes import wintypes
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

GAME = Path(r'C:\Users\Administrator\Desktop\杂七杂八\红渊\game')
sys.path.insert(0, str(GAME / 'tools'))
import zwin
import pyautogui, pyperclip
from PIL import ImageGrab

# 窗口内相对坐标（2026-11-05 02:10 按截图校准）
INPUT_BOX = (0.63, 0.887)

user32 = ctypes.windll.user32
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004


def click_at(x, y):
    """物理像素点击。不用 pyautogui.click —— 150% 缩放下它会点偏。"""
    user32.SetCursorPos(int(x), int(y))
    time.sleep(0.15)
    user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.06)
    user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)


def shot(hwnd, name):
    l, t, r, b = zwin.rect(hwnd)
    ImageGrab.grab(bbox=(l, t, r, b)).save(str(GAME / 'tools' / name))
    return GAME / 'tools' / name


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--text', default='')
    ap.add_argument('--text-file', default='')
    ap.add_argument('--send', action='store_true')
    a = ap.parse_args()

    if a.text_file:
        text = Path(a.text_file).read_text(encoding='utf-8').strip()
    elif a.text:
        text = a.text
    else:
        print('需要 --text 或 --text-file')
        return 2
    print('要发的文本（%d 字）：' % len(text))
    print(text)

    hwnd = zwin.find_zcode()
    if not hwnd:
        print('找不到 ZCode 窗口')
        return 2

    zwin.force_foreground(hwnd)
    time.sleep(0.8)

    x, y = zwin.pt(hwnd, *INPUT_BOX)
    print('点击输入框 (%d, %d)' % (x, y))
    click_at(x, y)
    time.sleep(0.4)

    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.12)
    pyautogui.press('delete')
    time.sleep(0.2)

    pyperclip.copy(text)
    time.sleep(0.25)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(1.2)

    p = shot(hwnd, '_nudge_pasted.png')
    print('已粘贴，截图:', p)

    if not a.send:
        print('DRY —— 没回车。看一眼截图确认粘进去了，再加 --send 真发。')
        return 0

    pyautogui.press('enter')
    time.sleep(4)
    p2 = shot(hwnd, '_nudge_sent.png')
    print('已回车，截图:', p2)
    return 0


if __name__ == '__main__':
    sys.exit(main())
