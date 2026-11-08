# -*- coding: utf-8 -*-
"""一停就写：盯住 GLM，停住就立刻把指令写进输入框并发送（不排队列）。

为什么不用「排队后续修改」（2026-10-29 23:2x 用户点明）：
  GLM 一忙就无视排队消息，直接停下来；排队等于没发。
  所以必须**等它停了再写、写完立刻发**。

判据（v2，实测可靠）：
  会话列（x 17%~55%、y 3%~86%）缩成 96×48 灰图算帧差。
  GLM 干活时那块一直在变（思考计时、新消息、终端输出）；
  停住就不动。连续 --still 秒不动 = 已停 → 立刻写入并发送。
  用按钮亮度判据会瞎：实测两种状态下都读到 0.94（GLM 其实早停了）。

写入坐标（2026-10-29 23:2x 实测，踩过两次坑）：
  (0.30, 0.915) = 输入框文本区上部  ← 用这个
  (0.59, 0.95)  = 右侧发送按钮        ← 点了会选整页文字，什么都没粘进去
  (0.315,0.946) = 「完全访问」下拉     ← 点了会弹模式菜单
  鼠标点击必须走 SetCursorPos（pyautogui 在 150% 缩放下会点偏）。

用法：
  python tools/auto_send.py                 # 一停就发，一直守
  python tools/auto_send.py --still 60      # 静止 60s 算停
  python tools/auto_send.py --once-stop     # 只处理第一次停顿就退出（调试）
"""
import sys, io, time, re, json, argparse, ctypes
from datetime import datetime
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
GAME = Path(r'C:\Users\Administrator\Desktop\杂七杂八\红渊\game')
sys.path.insert(0, str(GAME / 'tools'))
import zwin
import numpy as np
import pyperclip
from PIL import ImageGrab

DONE = GAME / 'TASK_DONE.md'
QUEUE = GAME / 'tasks' / 'queue.json'
ORDER = GAME / 'tools' / 'STANDING_ORDER.txt'
LOG = GAME / 'tools' / '_auto_send.log'
SHOTS = GAME / 'tools'

BOX = (0.17, 0.60, 0.55, 0.885)   # 会话区**下半段**：最近消息 +「工作中 N 秒」+ 思考计时都在这
# 2026-10-29 23:26 实测：整段 0.03~0.86 只差 0.256（误判成停），
# 只看下半段 0.60~0.885 差 0.52~1.6（正确反映在动）。静止时帧差 = 0.00。
INPUT_BOX = (0.30, 0.915)

u = ctypes.windll.user32


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
    img = ImageGrab.grab(bbox=(l + int(w * BOX[0]), t + int(h * BOX[1]),
                               l + int(w * BOX[2]), t + int(h * BOX[3]))).convert('L')
    return np.asarray(img.resize((96, 48)), dtype=np.float32)


def shot(hwnd, name):
    try:
        l, t, r, b = zwin.rect(hwnd)
        ImageGrab.grab(bbox=(l, t, r, b)).save(str(SHOTS / name))
    except Exception:
        pass


def key(vk, up=False):
    u.keybd_event(vk, 0, 2 if up else 0, 0)


def click_at(x, y):
    u.SetCursorPos(int(x), int(y))
    time.sleep(0.12)
    u.mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(0.05)
    u.mouse_event(0x0004, 0, 0, 0, 0)


def done_tasks():
    try:
        t = DONE.read_text(encoding='utf-8', errors='replace')
        return set(int(n) for n in re.findall(r'##\s*T(\d+)\s*[完写]', t))
    except Exception:
        return set()


def queue_left():
    try:
        q = json.loads(QUEUE.read_text(encoding='utf-8'))
    except Exception:
        return []
    done = done_tasks()
    left = []
    for it in q:
        tid = str(it.get('task_id', '')).strip()
        m = re.match(r'T(\d+)$', tid)
        if m and int(m.group(1)) not in done:
            left.append(tid)
    return left


def user_idle_seconds():
    """距上次键盘/鼠标输入多少秒（你不在电脑前时才会大）。"""
    class LASTINPUTINFO(ctypes.Structure):
        _fields_ = [('cbSize', ctypes.c_uint), ('dwTime', ctypes.c_ulong)]
    li = LASTINPUTINFO()
    li.cbSize = ctypes.sizeof(LASTINPUTINFO)
    if not u.GetLastInputInfo(ctypes.byref(li)):
        return 0.0
    return (ctypes.windll.kernel32.GetTickCount() - li.dwTime) / 1000.0


def fg_hwnd():
    return u.GetForegroundWindow()


def write_and_send(hwnd, text, tag):
    """写入输入框 → 截图 → 回车发送 → 截图。发完把焦点还给原来的窗口。"""
    prev_fg = fg_hwnd()
    zwin.force_foreground(hwnd)
    time.sleep(0.5)
    x, y = zwin.pt(hwnd, *INPUT_BOX)
    click_at(x, y)
    time.sleep(0.6)
    key(0x11); key(0x41); key(0x41, True); key(0x11, True)   # ctrl+a
    time.sleep(0.15)
    key(0x2E); key(0x2E, True)                               # delete
    time.sleep(0.25)
    pyperclip.copy(text)
    time.sleep(0.3)
    key(0x11); key(0x56); key(0x56, True); key(0x11, True)   # ctrl+v
    time.sleep(1.2)
    shot(hwnd, '_auto_pasted_%s.png' % tag)
    key(0x0D); key(0x0D, True)                               # enter
    time.sleep(2.5)
    shot(hwnd, '_auto_sent_%s.png' % tag)
    # 焦点还回去（你在 DSH 里讲话时被抢一下就别扭）
    if prev_fg and prev_fg != hwnd:
        try:
            u.SetForegroundWindow(prev_fg)
        except Exception:
            pass
    log('  已写入并发送（%s）' % tag)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--interval', type=int, default=5)
    ap.add_argument('--still', type=int, default=90)
    ap.add_argument('--thresh', type=float, default=0.3)
    ap.add_argument('--cooldown', type=int, default=120)
    ap.add_argument('--you-idle', type=int, default=45,
                    help='你多久没碰键鼠才算“人不在”；只有那时才允许抢焦点')
    ap.add_argument('--max-hours', type=float, default=9.0)
    ap.add_argument('--once-stop', action='store_true')
    a = ap.parse_args()

    text = ORDER.read_text(encoding='utf-8').strip()
    hwnd = zwin.find_zcode()
    if not hwnd:
        log('ZCode 窗口不在'); return 2

    log('=== 一停就写 启动（still=%ds cooldown=%ds）| 队列剩 %s ==='
        % (a.still, a.cooldown, ','.join(queue_left()) or '空'))
    prev = None
    last_move = time.time()
    last_send = 0.0
    t0 = time.time()
    n = 0
    last_rect = None

    while True:
        if (time.time() - t0) / 3600 > a.max_hours:
            log('守满 %.1f 小时，退出' % a.max_hours); return 0

        hwnd = zwin.find_zcode()
        if not hwnd:
            log('ZCode 窗口没了，退出'); return 2

        rc = zwin.rect(hwnd)
        if rc != last_rect:
            log('窗口位置/尺寸 = %s（用户动过窗口就重新采样，避免误判）' % (rc,))
            last_rect = rc
            prev = None
            time.sleep(a.interval)
            continue

        cur = frame(hwnd)
        if prev is None:
            prev = cur
            time.sleep(a.interval)
            continue
        d = float(np.abs(cur - prev).mean())
        prev = cur
        now = time.time()

        if d > a.thresh:
            last_move = now
            time.sleep(a.interval)
            continue

        still = now - last_move
        left = queue_left()
        if not left:
            log('队列已空（全部写进 TASK_DONE），退出'); return 0

        if still >= a.still and now - last_send > a.cooldown:
            # 你还醒着、正在别的窗口（比如 DSH 里跟我说话）→ 不抢焦点，等一等
            fg = fg_hwnd()
            idle = user_idle_seconds()
            if fg != hwnd and idle < a.you_idle:
                log('GLM 停了，但你正在用电脑（前台非 ZCode，距上次输入 %.0fs < %ds），先不打扰'
                    % (idle, a.you_idle))
                time.sleep(a.interval)
                continue

            log('GLM 静止 %.0fs → 立刻写入并发送（队列剩 %s）' % (still, ','.join(left)))
            n += 1
            try:
                write_and_send(hwnd, text, str(n))
                last_send = time.time()
                last_move = time.time()
            except Exception as e:
                log('  发送异常：%s' % e)
            if a.once_stop:
                return 0
        else:
            log('静止 %.0fs / %ds（队列剩 %s）' % (still, a.still, ','.join(left[:3])))

        time.sleep(a.interval)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        log('手动停止')
        sys.exit(0)
