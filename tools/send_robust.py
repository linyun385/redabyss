# -*- coding: utf-8 -*-
"""可靠地给 ZCode 发一条消息：先把 DSH 窗口最小化（它会盖住 ZCode），发完恢复。

用法：
  python tools/send_robust.py T35            # 发 queue.json 里 T35 的原文（最稳）
  python tools/send_robust.py --text "..."   # 发自定义文本
  加 --dry 只粘贴不回车
"""
import sys, io, time, json, argparse, ctypes
from ctypes import wintypes
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
GAME = Path(r'C:\Users\Administrator\Desktop\杂七杂八\红渊\game')
sys.path.insert(0, str(GAME / 'tools'))
import zwin
import pyautogui, pyperclip
from PIL import ImageGrab

INPUT_BOX = (0.45, 0.893)   # 2026-10-30 23:07 校准（ZCode 3.17.1 会话态）       # 会话态输入框**左中**位置（2026-10-29 23:2x 实测）
# 注意：不要点 0.59！那里是右侧发送按钮，点了等于先选整页文字、什么都没粘进去。
HOME_INPUT = (0.595, 0.5206)     # 首页（新建任务）输入框

user32 = ctypes.windll.user32
EnumWindows = user32.EnumWindows
GetWindowTextW = user32.GetWindowTextW
ShowWindow = user32.ShowWindow

MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004


def click_at(x, y):
    """物理像素点击。**不要用 pyautogui.click**：
    2026-10-29 实测本机 150% 缩放下 pyautogui 会把 (1833,803) 点到 (2023,869)，
    结果把整页文字选中、消息根本没进输入框。SetCursorPos 本身是准确的。"""
    user32.SetCursorPos(int(x), int(y))
    time.sleep(0.12)
    user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.05)
    user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)


def find_by_title(substr):
    found = []

    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def cb(h, _):
        n = user32.GetWindowTextLengthW(h)
        if n:
            buf = ctypes.create_unicode_buffer(n + 1)
            GetWindowTextW(h, buf, n + 1)
            if substr in buf.value and user32.IsWindowVisible(h):
                found.append(h)
        return True

    EnumWindows(cb, 0)
    return found[0] if found else None


def shot(hwnd, name):
    l, t, r, b = zwin.rect(hwnd)
    ImageGrab.grab(bbox=(l, t, r, b)).save(str(GAME / 'tools' / name))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('task', nargs='?', default='')
    ap.add_argument('--text', default='')
    ap.add_argument('--dry', action='store_true')
    a = ap.parse_args()

    if a.text:
        msg = a.text
    elif a.task:
        q = json.loads((GAME / 'tasks' / 'queue.json').read_text(encoding='utf-8'))
        hits = [i for i in q if i.get('task_id') == a.task]
        if not hits:
            print('queue 里没有', a.task); sys.exit(2)
        msg = hits[0]['message']
    else:
        print('需要任务号或 --text'); sys.exit(2)

    dsh = find_by_title('DeepSeek Harness')
    if dsh:
        ShowWindow(dsh, 6)          # SW_MINIMIZE
        print('已最小化 DSH', dsh)
        time.sleep(0.8)

    try:
        hwnd = zwin.find_zcode()
        if not hwnd:
            print('no ZCode'); return 1
        zwin.force_foreground(hwnd)
        time.sleep(0.8)
        x, y = zwin.pt(hwnd, *INPUT_BOX)
        pyautogui.click(x, y)
        time.sleep(0.5)
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.15)
        pyautogui.press('delete')
        time.sleep(0.2)
        pyperclip.copy(msg)
        time.sleep(0.3)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(1.2)
        shot(hwnd, '_send_pasted.png')
        if a.dry:
            print('已粘贴未发送（--dry）'); return 0
        pyautogui.press('enter')
        time.sleep(4)
        shot(hwnd, '_send_after_enter.png')
        print('已发送', a.task or '(text)')
        return 0
    finally:
        if dsh:
            ShowWindow(dsh, 9)      # SW_RESTORE
            print('已恢复 DSH')


if __name__ == '__main__':
    sys.exit(main())
