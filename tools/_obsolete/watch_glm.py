# -*- coding: utf-8 -*-
"""盯 GLM 是不是还在动（v2：看画面有没有变化，不看按钮）。

为什么换判据（2026-10-29 23:20 血的教训）：
  v1 用「右下角按钮亮度」判断，结果在任何状态下都读到 0.94——
  GLM 其实 23:08 就停了，它还在报「工作中」，白盯了 12 分钟。
  原因是那个按钮/输入框边框在两种状态下都有一大块亮像素，亮度分不出来。

v2 判据：**看会话正文有没有在变**。
  GLM 干活时会话区一直在变（「思考 · 持续了几秒」的数字、新消息、终端输出）。
  停下来后那块区域就一动不动。
  只取会话列（x 17%~55%、y 3%~86%），避开左侧任务列表、右侧 Chrome、
  以及桌面宠物动画；缩到 96×48 灰图算帧差。

  帧差 > --move-thresh（默认 0.3，灰度均值差）→ 算在动
  连续 --still 秒没动（默认 90）→ 判定已停，打印现场后 exit 0

用法：
  python tools/watch_glm.py --probe        # 只报一次「在动/没动」
  python tools/watch_glm.py                # 盯到停为止（停下就退出＝该你接手）
  python tools/watch_glm.py --still 120    # 容忍更久的静止
"""
import sys, io, time, argparse
from datetime import datetime
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
GAME = Path(r'C:\Users\Administrator\Desktop\杂七杂八\红渊\game')
sys.path.insert(0, str(GAME / 'tools'))
import zwin
import numpy as np
from PIL import ImageGrab

LOG = GAME / 'tools' / '_watch.log'
DONE = GAME / 'TASK_DONE.md'

BOX = (0.17, 0.03, 0.55, 0.86)   # 会话列（相对窗口比例）


def log(m):
    line = '[%s] %s' % (datetime.now().strftime('%H:%M:%S'), m)
    print(line, flush=True)
    try:
        with open(LOG, 'a', encoding='utf-8') as f:
            f.write(line + '\n')
    except Exception:
        pass


def frame(hwnd):
    l, t, r, b = zwin.rect(hwnd)
    w, h = r - l, b - t
    x0, y0 = l + int(w * BOX[0]), t + int(h * BOX[1])
    x1, y1 = l + int(w * BOX[2]), t + int(h * BOX[3])
    img = ImageGrab.grab(bbox=(x0, y0, x1, y1)).convert('L').resize((96, 48))
    return np.asarray(img, dtype=np.float32)


def done_tasks():
    import re
    try:
        t = DONE.read_text(encoding='utf-8', errors='replace')
        return sorted(set(int(n) for n in re.findall(r'##\s*T(\d+)\s*[完写]', t)))
    except Exception:
        return []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--interval', type=int, default=10)
    ap.add_argument('--still', type=int, default=90, help='静止多少秒算已停')
    ap.add_argument('--move-thresh', type=float, default=0.3)
    ap.add_argument('--max-hours', type=float, default=9.0)
    ap.add_argument('--probe', action='store_true')
    a = ap.parse_args()

    hwnd = zwin.find_zcode()
    if not hwnd:
        log('ZCode 窗口不在'); return 2

    if a.probe:
        zwin.force_foreground(hwnd); time.sleep(0.3)
        f1 = frame(hwnd); time.sleep(4); f2 = frame(hwnd)
        d = float(np.abs(f1 - f2).mean())
        log('probe 帧差=%.3f → %s | 已完成 %s'
            % (d, '在动' if d > a.move_thresh else '没动', done_tasks()[-3:]))
        return 0

    log('=== 开始盯（interval=%ds still=%ds thresh=%.2f）==='
        % (a.interval, a.still, a.move_thresh))
    prev = None
    last_move = time.time()
    t0 = time.time()
    while True:
        if (time.time() - t0) / 3600 > a.max_hours:
            log('盯满 %.1f 小时，退出' % a.max_hours); return 0

        hwnd = zwin.find_zcode()
        if not hwnd:
            log('ZCode 窗口没了，退出'); return 2
        try:
            zwin.force_foreground(hwnd)
        except Exception:
            pass

        cur = frame(hwnd)
        if prev is None:
            prev = cur
            time.sleep(a.interval)
            continue

        d = float(np.abs(cur - prev).mean())
        prev = cur
        now = time.time()
        if d > a.move_thresh:
            last_move = now
            log('在动（帧差 %.2f）' % d)
        else:
            still = now - last_move
            log('没动 %.0fs / %ds（帧差 %.2f）' % (still, a.still, d))
            if still >= a.still:
                log('=== GLM 已停，该指挥席接手了 ===')
                log('  静止 %.0fs；已完成任务 %s' % (still, done_tasks()[-5:]))
                return 0

        time.sleep(a.interval)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        log('手动停止')
        sys.exit(0)
