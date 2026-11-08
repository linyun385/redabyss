# -*- coding: utf-8 -*-
"""用 ctypes 枚举窗口，定位真正的 ZCode 窗口及其 rect。"""
import sys, io, ctypes
from ctypes import wintypes
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

u = ctypes.windll.user32
u.GetWindowTextW.restype = ctypes.c_int
u.GetWindowTextLengthW.restype = ctypes.c_int

WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)


def title(h):
    n = u.GetWindowTextLengthW(h)
    if n <= 0:
        return ''
    buf = ctypes.create_unicode_buffer(n + 1)
    u.GetWindowTextW(h, buf, n + 1)
    return buf.value


def rect(h):
    r = wintypes.RECT()
    u.GetWindowRect(h, ctypes.byref(r))
    return (r.left, r.top, r.right, r.bottom)


hits = []
def cb(h, _):
    if u.IsWindowVisible(h):
        t = title(h)
        if not t:
            return True
        low = t.lower()
        if 'zcode' in low or '读取' in t or '读 c:/' in low or 't1 ' in low:
            l, tp, r, b = rect(h)
            hits.append((h, t[:60], (l, tp, r, b), r - l, b - tp))
    return True

u.EnumWindows(WNDENUMPROC(cb), 0)
print('matches:', len(hits))
for h in hits:
    print(' ', h)

# 也打印前台窗口
fg = u.GetForegroundWindow()
print('foreground:', fg, title(fg)[:50], rect(fg))
