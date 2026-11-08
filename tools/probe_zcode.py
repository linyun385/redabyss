# -*- coding: utf-8 -*-
"""检查 ZCode 窗口状态：进程、窗口、界面态、繁忙条。"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r'D:\idv_datamine_isolated\tools')
import night_watch as nw

print('proc_alive:', nw.proc_alive())
hwnd = nw.find_window()
print('hwnd:', hwnd)
if hwnd:
    try:
        layout, info = nw.detect_layout(hwnd)
        print('layout:', layout, '|', info)
    except Exception as e:
        print('layout err:', e)
    try:
        busy, binfo = nw.detect_busy(hwnd)
        print('busy:', busy, '|', binfo)
    except Exception as e:
        print('busy err:', e)
    try:
        rect = nw.get_rect(hwnd) if hasattr(nw, 'get_rect') else None
        print('rect:', rect)
    except Exception as e:
        print('rect err:', e)
