# -*- coding: utf-8 -*-
"""发送常驻指令：文本从文件读（python 显式 utf-8），避免 PowerShell 传参把中文搞成乱码。

用法：python tools/send_standing.py tools/_standing_msg.txt [--dry]
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
INPUT = (0.45, 0.893)          # 2026-10-30 23:07 校准（ZCode 3.17.1 会话态）


def key(vk, up=False):
    u.keybd_event(vk, 0, 2 if up else 0, 0)


def click_at(x, y):
    u.SetCursorPos(int(x), int(y))
    time.sleep(0.12)
    u.mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(0.05)
    u.mouse_event(0x0004, 0, 0, 0, 0)


def main():
    src = GAME / (sys.argv[1] if len(sys.argv) > 1 else 'tools/_standing_msg.txt')
    dry = '--dry' in sys.argv
    text = src.read_text(encoding='utf-8-sig').strip()
    print('text chars', len(text))

    h = zwin.find_zcode()
    zwin.force_foreground(h)
    time.sleep(0.5)
    x, y = zwin.pt(h, *INPUT)
    click_at(x, y)
    time.sleep(0.5)
    key(0x11); key(0x41); key(0x41, True); key(0x11, True)   # ctrl+a 清空旧内容
    time.sleep(0.15)
    key(0x2E); key(0x2E, True)
    time.sleep(0.25)
    pyperclip.copy(text)
    time.sleep(0.3)
    key(0x11); key(0x56); key(0x56, True); key(0x11, True)
    time.sleep(1.2)
    l, t, r, b = zwin.rect(h)
    ImageGrab.grab(bbox=(l, t, r, b)).save(str(GAME / 'tools' / '_standing_pasted.png'))
    if dry:
        print('已粘贴未发送（--dry）')
        return
    key(0x0D); key(0x0D, True)
    time.sleep(2.5)
    ImageGrab.grab(bbox=(l, t, r, b)).save(str(GAME / 'tools' / '_standing_sent.png'))
    print('已发送')


if __name__ == '__main__':
    main()
