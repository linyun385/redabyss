# -*- coding: utf-8 -*-
"""强制把 ZCode 拉到前台并截图（用 AttachThreadInput 绕过 SetForegroundWindow 限制）。"""
import sys, io, time, ctypes
from ctypes import wintypes
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    ctypes.windll.user32.SetProcessDPIAware()

u = ctypes.windll.user32
k = ctypes.windll.kernel32
u.GetWindowTextLengthW.restype = ctypes.c_int
WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)


def title(h):
    n = u.GetWindowTextLengthW(h)
    if n <= 0:
        return ''
    b = ctypes.create_unicode_buffer(n + 1)
    u.GetWindowTextW(h, b, n + 1)
    return b.value


def rect(h):
    r = wintypes.RECT()
    u.GetWindowRect(h, ctypes.byref(r))
    return (r.left, r.top, r.right, r.bottom)


def pid_of(h):
    p = wintypes.DWORD()
    u.GetWindowThreadProcessId(h, ctypes.byref(p))
    return p.value


cands = []
def cb(h, _):
    if u.IsWindowVisible(h) and title(h) == 'ZCode':
        cands.append((h, pid_of(h), rect(h)))
    return True
u.EnumWindows(WNDENUMPROC(cb), 0)

print('标题为 ZCode 的可见窗口:', cands)
if not cands:
    print('找不到'); sys.exit(1)

hwnd = cands[0][0]
l, t, r, b = rect(hwnd)
print('选中 hwnd=%d pid=%d rect=%s size=%dx%d' % (hwnd, cands[0][1], (l, t, r, b), r - l, b - t))

# 强力置前
u.ShowWindow(hwnd, 9)          # restore
u.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 0x0001 | 0x0002)  # HWND_TOPMOST, SWP_NOMOVE|SWP_NOSIZE
fg = u.GetForegroundWindow()
tid_fg = u.GetWindowThreadProcessId(fg, None)
tid_me = k.GetCurrentThreadId()
u.AttachThreadInput(tid_me, tid_fg, True)
u.BringWindowToTop(hwnd)
u.SetForegroundWindow(hwnd)
u.AttachThreadInput(tid_me, tid_fg, False)
time.sleep(0.8)
print('foreground 现在是:', title(u.GetForegroundWindow()))

from PIL import ImageGrab
l, t, r, b = rect(hwnd)
img = ImageGrab.grab(bbox=(l, t, r, b))
out = r'C:\Users\Administrator\Desktop\杂七杂八\红渊\game\tools\_shot_zcode_real.png'
img.save(out)
print('saved', out, img.size)

# 取消置顶，恢复正常层级
u.SetWindowPos(hwnd, 0, 0, 0, 0, 0, 0x0001 | 0x0002 | 0x0004)  # HWND_TOP, NOMOVE|NOSIZE|NOACTIVATE
