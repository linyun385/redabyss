# -*- coding: utf-8 -*-
"""给 ZCode 发一条完整消息：粘贴 + 截图 + 点发送 + 截图，全程用同一份窗口矩形。

为什么合成一个脚本：
  2026-11-05 23:26 踩过——glm_nudge.py 粘贴用一次 rect，_send_click.py 点击用另一次 rect，
  中间窗口被移动了（651,65 → 459,173），点到了别处。合成一个就不会对不上。

用法：
  python tools/_glm_send.py --text-file tasks/INBOX/05_send.txt
  python tools/_glm_send.py --text-file ... --dry   只粘贴不发送
"""
import sys, io, time, argparse, ctypes
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
GAME = Path(r'C:\Users\Administrator\Desktop\杂七杂八\红渊\game')
sys.path.insert(0, str(GAME / 'tools'))
import zwin
import pyautogui, pyperclip
from PIL import ImageGrab

INPUT_BOX = (0.63, 0.887)    # 2026-11-05 02:10 校准
SEND_BTN = (0.912, 0.940)    # 2026-11-05 23:26 实测重校准

user32 = ctypes.windll.user32
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004


def click_at(x, y):
    user32.SetCursorPos(int(x), int(y))
    time.sleep(0.15)
    user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.06)
    user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)


def shot(rect, name):
    l, t, r, b = rect
    p = GAME / 'tools' / name
    ImageGrab.grab(bbox=(l, t, r, b)).save(str(p))
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--text-file', required=True)
    ap.add_argument('--dry', action='store_true')
    a = ap.parse_args()

    text = Path(a.text_file).read_text(encoding='utf-8').strip()
    print('要发 %d 字' % len(text))

    h = zwin.find_zcode()
    if not h:
        print('找不到 ZCode 窗口')
        return 2
    ok = zwin.force_foreground(h)
    time.sleep(0.9)
    rect = zwin.rect(h)
    l, t, r, b = rect
    print('窗口:', rect, '尺寸', (r - l, b - t), '前台:', ok)
    if r - l < 600 or b - t < 400:
        print('!! 窗口尺寸异常，中止')
        return 3

    # 1) 点输入框并清空
    ix, iy = int(l + INPUT_BOX[0] * (r - l)), int(t + INPUT_BOX[1] * (b - t))
    print('点输入框 (%d, %d)' % (ix, iy))
    click_at(ix, iy)
    time.sleep(0.4)
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.12)
    pyautogui.press('delete')
    time.sleep(0.25)

    # 2) 粘贴
    pyperclip.copy(text)
    time.sleep(0.25)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(1.4)
    print('已粘贴，截图:', shot(rect, '_send_pasted.png').name)

    if a.dry:
        print('DRY —— 没点发送')
        return 0

    # 3) 点发送（同一份 rect）
    sx, sy = int(l + SEND_BTN[0] * (r - l)), int(t + SEND_BTN[1] * (b - t))
    print('点发送按钮 (%d, %d)' % (sx, sy))
    click_at(sx, sy)
    time.sleep(3.0)
    print('截图:', shot(rect, '_send_after.png').name)
    return 0


if __name__ == '__main__':
    sys.exit(main())
