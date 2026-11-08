# -*- coding: utf-8 -*-
"""可靠的 ZCode 窗口定位（DPI 感知 + 按标题精确匹配）。

为什么需要这个：
  2026-10-28 实测，night_watch.find_window() 会返回一个 rect 为全屏的其他窗口，
  拿它算输入框坐标会点错地方。本模块直接按窗口标题 "ZCode" 找，并在
  DPI 感知模式下取物理像素坐标，与 pyautogui 的点击坐标系一致。

用法：
  import zwin
  hwnd = zwin.find_zcode()
  l, t, r, b = zwin.rect(hwnd)
  x, y = zwin.pt(hwnd, 0.57, 0.91)      # 按窗口比例算绝对坐标
"""
import ctypes
from ctypes import wintypes

# 必须在任何坐标 API 之前开启 DPI 感知，否则拿到的是缩放后的虚拟坐标
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)   # per-monitor
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

_u = ctypes.windll.user32
_u.GetWindowTextLengthW.restype = ctypes.c_int

WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)


def title(hwnd):
    n = _u.GetWindowTextLengthW(hwnd)
    if n <= 0:
        return ''
    buf = ctypes.create_unicode_buffer(n + 1)
    _u.GetWindowTextW(hwnd, buf, n + 1)
    return buf.value


def rect(hwnd):
    r = wintypes.RECT()
    _u.GetWindowRect(hwnd, ctypes.byref(r))
    return (r.left, r.top, r.right, r.bottom)


def pt(hwnd, rx, ry):
    """按窗口内相对比例算绝对像素坐标。"""
    l, t, r, b = rect(hwnd)
    return int(l + rx * (r - l)), int(t + ry * (b - t))


def find_zcode(exclude_titles=('DeepSeek Harness',)):
    """找 ZCode 主窗口。标题精确等于 'ZCode'，或包含 'ZCode' 但排除我们的 app。"""
    best = []
    def cb(h, _):
        if not _u.IsWindowVisible(h):
            return True
        t = title(h)
        if not t or t in exclude_titles:
            return True
        if t == 'ZCode':
            best.insert(0, h)
        elif 'zcode' in t.lower() and 'deepseek' not in t.lower():
            best.append(h)
        return True
    _u.EnumWindows(WNDENUMPROC(cb), 0)
    for h in best:
        l, t2, r, b = rect(h)
        # 排除太小的窗口（弹窗/托盘）
        if (r - l) > 600 and (b - t2) > 400:
            return h
    return best[0] if best else 0


def foreground():
    return _u.GetForegroundWindow()


def force_foreground(hwnd):
    """把窗口拉到前台。最小化时先恢复。
    用 AttachThreadInput 绕过 SetForegroundWindow 的权限限制——
    单纯 SetForegroundWindow 在当前进程不是前台时会静默失败。"""
    import time
    _k = ctypes.windll.kernel32
    if _u.IsIconic(hwnd):
        _u.ShowWindow(hwnd, 9)   # SW_RESTORE
    if _u.GetForegroundWindow() == hwnd:
        return True
    try:
        fg = _u.GetForegroundWindow()
        tid_fg = _u.GetWindowThreadProcessId(fg, None)
        tid_me = _k.GetCurrentThreadId()
        _u.AttachThreadInput(tid_me, tid_fg, True)
        _u.BringWindowToTop(hwnd)
        _u.SetForegroundWindow(hwnd)
        _u.AttachThreadInput(tid_me, tid_fg, False)
    except Exception:
        _u.BringWindowToTop(hwnd)
        _u.SetForegroundWindow(hwnd)
    time.sleep(0.25)
    return _u.GetForegroundWindow() == hwnd


if __name__ == '__main__':
    h = find_zcode()
    print('hwnd:', h)
    print('title:', title(h))
    print('rect:', rect(h))
    l, t, r, b = rect(h)
    print('size:', r - l, 'x', b - t)
    print('pt(0.57,0.91):', pt(h, 0.57, 0.91))
