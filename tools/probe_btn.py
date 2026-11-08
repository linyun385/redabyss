# -*- coding: utf-8 -*-
"""校准右下角按钮：工作时是方块■，停止后变成箭头↑。
用亮像素占比区分，实测两种状态的数值。"""
import sys, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r'C:\Users\Administrator\Desktop\杂七杂八\红渊\game\tools')
import zwin
from PIL import ImageGrab

hwnd = zwin.find_zcode()
l, t, r, b = zwin.rect(hwnd)
w, h = r - l, b - t
print('窗口:', (l, t, r, b), '尺寸:', w, h)


def probe(rx, ry, half, thr):
    cx, cy = l + int(w * rx), t + int(h * ry)
    box = (cx - half, cy - half, cx + half, cy + half)
    img = ImageGrab.grab(bbox=box).convert('L')
    px = list(img.getdata())
    ratio = sum(1 for v in px if v > thr) / len(px)
    return cx, cy, ratio, max(px), sum(px) / len(px)


print('\n=== 右下角按钮区域（扫描几个候选位置）===')
for rx in (0.80, 0.82, 0.826, 0.84):
    for ry in (0.93, 0.947, 0.96):
        cx, cy, ratio, mx, mean = probe(rx, ry, 18, 110)
        print('  rx=%.3f ry=%.3f -> (%d,%d) 亮占比=%.3f 最亮=%d 均值=%.1f'
              % (rx, ry, cx, cy, ratio, mx, mean))

print('\n=== 保存该区域放大图，供人眼确认 ===')
cx, cy = l + int(w * 0.826), t + int(h * 0.947)
box = (cx - 40, cy - 40, cx + 40, cy + 40)
img = ImageGrab.grab(bbox=box)
img = img.resize((240, 240), 0)
img.save(r'C:\Users\Administrator\Desktop\杂七杂八\红渊\game\tools\_btn.png')
print('  saved _btn.png')
