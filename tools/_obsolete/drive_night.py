# -*- coding: utf-8 -*-
"""夜班驱动器 v1（2026-10-29 23:1x）

和 fire_watch.py 的分工：
  - fire_watch.py：老脚本，判据（右下角按钮）是好的，但**点击用了 pyautogui**，
    本机 150% 缩放下会点偏（实测 (1833,803) 点到 (2023,869)），消息根本发不出去。
  - 本脚本：判据沿用「右下角按钮 ■=工作中 / ↑=已停」，点击改用物理像素，
    并且**下一棒直接按 tasks/queue.json 派**（不再发“继续。”这种没信息量的话）。

循环：
  1. ZCode 在前台 → 读按钮 ▢/↑
  2. ■ 工作中 → 什么都不做
  3. ↑ 已停 → 找队列里第一个没写进 TASK_DONE 的任务，把它的派发原文发进当前会话
  4. 同一任务发了 escalate 秒还没完成 → ctrl+N 新会话再发
  5. 队列跑空 → 记日志退出
"""
import sys, io, time, json, re, argparse, ctypes
from datetime import datetime
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
GAME = Path(r'C:\Users\Administrator\Desktop\杂七杂八\红渊\game')
sys.path.insert(0, str(GAME / 'tools'))
import zwin
import pyperclip
import numpy as np
from PIL import ImageGrab

DONE = GAME / 'TASK_DONE.md'
QUEUE = GAME / 'tasks' / 'queue.json'
STATE = GAME / 'tools' / '_drive_night_state.json'
LOG = GAME / 'tools' / '_drive_night.log'
SHOTS = GAME / 'tools'

BTN = (0.9096, 0.952)        # 右下角 发送■/停止 按钮中心（2026-10-29 23:12 像素校准）
COMPOSER = (0.595, 0.9655)   # 会话态输入框（“继续输入以排队后续修改”）
HOME_INPUT = (0.595, 0.5206) # 首页输入框
EXCLUDE_PREFIX = ('tasks/', 'tools/', 'web/art/', 'docs/artstyle/')
EXCLUDE_FILES = ('DESIGN.md', 'glossary.json', 'TASK_DONE.md')

u = ctypes.windll.user32


def log(m):
    line = '[%s] %s' % (datetime.now().strftime('%H:%M:%S'), m)
    print(line, flush=True)
    try:
        with open(LOG, 'a', encoding='utf-8') as f:
            f.write(line + '\n')
    except Exception:
        pass


def click_at(x, y):
    u.SetCursorPos(int(x), int(y))
    time.sleep(0.12)
    u.mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(0.05)
    u.mouse_event(0x0004, 0, 0, 0, 0)


def shot(hwnd, name):
    try:
        l, t, r, b = zwin.rect(hwnd)
        ImageGrab.grab(bbox=(l, t, r, b)).save(str(SHOTS / name))
    except Exception:
        pass


def button_state(hwnd):
    """在窗口底部横条里**扫**出发送/停止按钮，不写死坐标。

    为什么不能写死：2026-10-29 夜里 GLM 把 Chrome 停靠在 ZCode 右侧，
    ZCode 窗口变窄，按钮从 0.91 跑到 0.60；换个布局就读不到（读成 0.00）。
    做法：取底部横条（y 88%~99%、x 25%~99%），在横条里找填充最高的 21×21 小窗，
    填充 ≥0.80 → ■ 工作中；≤0.45 → ↑ 已停；其余 → 读不准。
    """
    try:
        l, t, r, b = zwin.rect(hwnd)
        w, h = r - l, b - t
        x0, x1 = l + int(w * 0.25), l + int(w * 0.99)
        y0, y1 = t + int(h * 0.88), t + int(h * 0.99)
        img = ImageGrab.grab(bbox=(x0, y0, x1, y1)).convert('L')
        a = (np.asarray(img) > 110).astype(np.float32)
        H, W = a.shape
        k = 21
        if H < k or W < k:
            return None, None
        # 积分图求每个 21x21 窗口的填充率
        ii = np.zeros((H + 1, W + 1), dtype=np.float32)
        ii[1:, 1:] = a.cumsum(0).cumsum(1)
        S = ii[k:, k:] - ii[:-k, k:] - ii[k:, :-k] + ii[:-k, :-k]
        S = S / (k * k)
        best = float(S.max())
        return best, best >= 0.80
    except Exception:
        return None, None


def done_set():
    try:
        text = DONE.read_text(encoding='utf-8', errors='replace')
    except Exception:
        return set()
    return set(int(n) for n in re.findall(r'##\s*T(\d+)\s*[完写]', text))


def next_in_queue():
    try:
        q = json.loads(QUEUE.read_text(encoding='utf-8'))
    except Exception:
        return None, None
    done = done_set()
    for it in q:
        tid = str(it.get('task_id', '')).strip()
        m = re.match(r'T(\d+)$', tid)
        if not m or int(m.group(1)) in done:
            continue
        return tid, it.get('message', '')
    return None, None


def produced_mtime():
    newest = 0.0
    for p in GAME.rglob('*'):
        if not p.is_file():
            continue
        rel = p.relative_to(GAME).as_posix()
        if rel.startswith(EXCLUDE_PREFIX) or rel in EXCLUDE_FILES:
            continue
        try:
            newest = max(newest, p.stat().st_mtime)
        except Exception:
            pass
    return newest


def send(hwnd, text, box, home=False):
    if not zwin.force_foreground(hwnd):
        log('  拉不到前台')
        return False
    time.sleep(0.5)
    if home:
        u.keybd_event(0x11, 0, 0, 0)      # ctrl down
        u.keybd_event(0x4E, 0, 0, 0)      # N
        u.keybd_event(0x4E, 0, 2, 0)
        u.keybd_event(0x11, 0, 2, 0)
        time.sleep(3.0)
        shot(hwnd, '_drive_newtask.png')
    x, y = zwin.pt(hwnd, *box)
    click_at(x, y)
    time.sleep(0.5)
    # 清空输入框（ctrl+a / delete）——键盘事件不受 DPI 影响
    u.keybd_event(0x11, 0, 0, 0)
    u.keybd_event(0x41, 0, 0, 0)
    u.keybd_event(0x41, 0, 2, 0)
    u.keybd_event(0x11, 0, 2, 0)
    time.sleep(0.15)
    u.keybd_event(0x2E, 0, 0, 0)          # delete
    u.keybd_event(0x2E, 0, 2, 0)
    time.sleep(0.2)
    pyperclip.copy(text)
    time.sleep(0.3)
    u.keybd_event(0x11, 0, 0, 0)
    u.keybd_event(0x56, 0, 0, 0)          # V
    u.keybd_event(0x56, 0, 2, 0)
    u.keybd_event(0x11, 0, 2, 0)
    time.sleep(1.2)
    shot(hwnd, '_drive_pasted.png')
    u.keybd_event(0x0D, 0, 0, 0)          # enter
    u.keybd_event(0x0D, 0, 2, 0)
    time.sleep(4)
    shot(hwnd, '_drive_sent.png')
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--interval', type=int, default=20)
    ap.add_argument('--idle', type=int, default=180, help='按钮停多久算停摆')
    ap.add_argument('--escalate', type=int, default=600, help='同任务发过多久还没完成就换会话')
    ap.add_argument('--gap', type=int, default=120, help='两次发送最小间隔')
    ap.add_argument('--once', action='store_true')
    ap.add_argument('--dry', action='store_true')
    args = ap.parse_args()

    try:
        st = json.loads(STATE.read_text(encoding='utf-8'))
    except Exception:
        st = {}
    last_send_ts = float(st.get('last_send_ts', 0))
    last_task = st.get('last_task', '')
    sessions = int(st.get('sessions', 0))
    blind_since = 0

    def save():
        try:
            STATE.write_text(json.dumps({'last_send_ts': last_send_ts,
                                         'last_task': last_task,
                                         'sessions': sessions}), encoding='utf-8')
        except Exception:
            pass

    log('=== 驱动器启动 interval=%ds idle=%ds escalate=%ds gap=%ds dry=%s ==='
        % (args.interval, args.idle, args.escalate, args.gap, args.dry))

    while True:
        now = time.time()
        hwnd = zwin.find_zcode()
        if not hwnd:
            log('ZCode 窗口不在，退出')
            break

        # 每次都先把 ZCode 拉到前台再读按钮。
        # 原因：2026-10-29 23:08 GLM 用浏览器实测时 Chrome 盖住了 ZCode 右下角，
        # 读到的是 Chrome 的暗色像素（0.00）→ 被判成“已停” → 重复发任务。
        # 按钮只有在前台时才读得准。GLM 的浏览器操作走 CDP，不吃前台焦点。
        try:
            zwin.force_foreground(hwnd)
        except Exception:
            pass

        ratio, working = button_state(hwnd)
        prod = produced_mtime()
        silent = now - prod if prod else 99999
        task, msg = next_in_queue()

        if ratio is None:
            # 读不到按钮时**绝不能当成“已停”**——2026-10-29 23:08 就是这么
            # 把 T35 重复发了第二遍。先尝试把 ZCode 拉到前台重读一次。
            try:
                zwin.force_foreground(hwnd)
                time.sleep(0.4)
                ratio, working = button_state(hwnd)
            except Exception:
                ratio, working = None, None
            if ratio is None:
                log('按钮读不到（窗口被盖住/最小化），本轮跳过')
                blind_since = blind_since or now
                if now - blind_since > 900:
                    log('!! 已经 %.0fs 读不到按钮，需要人工看一眼' % (now - blind_since))
                if args.once:
                    break
                time.sleep(args.interval)
                continue
        blind_since = 0

        log('按钮=%.2f %s | 队列下一棒=%s | 产出停滞 %.0fs'
            % (ratio, '工作中' if working else '已停', task or '（空）', silent))

        if task is None:
            log('队列跑空，全部完成，退出')
            break

        if working:
            if args.once:
                break
            time.sleep(args.interval)
            continue

        # 已停：判断该不该发
        if now - last_send_ts < args.gap:
            if args.once:
                break
            time.sleep(args.interval)
            continue

        if silent < args.idle and last_task == task:
            # 刚发过、它还在想，别催
            if args.once:
                break
            time.sleep(args.interval)
            continue

        same_task_stuck = (last_task == task and now - last_send_ts > args.escalate)
        if args.dry:
            log('  [dry] 会发 %s（换会话=%s）' % (task, same_task_stuck))
            if args.once:
                break
            time.sleep(args.interval)
            continue

        log('  发送 %s（换会话=%s）' % (task, same_task_stuck))
        ok = send(hwnd, msg, HOME_INPUT if same_task_stuck else COMPOSER, home=same_task_stuck)
        if ok:
            last_send_ts = time.time()
            last_task = task
            if same_task_stuck:
                sessions += 1
            save()
            log('  已发 %s（累计换会话 %d）' % (task, sessions))
        else:
            last_send_ts = time.time()
            save()

        if args.once:
            break
        time.sleep(args.interval)

    log('=== 驱动器退出（换会话 %d 次）===' % sessions)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        log('手动停止')
