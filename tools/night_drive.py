#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""红渊卡牌项目夜间驱动器。

与 night_watch.py 的区别（这三条都是 2026-10-28 的教训）：
  1. 不读第五人格的 kb/PROGRESS.json，也不判断「界面态=首页就不管」
     —— 那个判断是 10-27 空转 5 小时的直接原因
  2. 任务消息不粘贴长文，只发一句「去读哪个任务文件」
     —— 减少粘贴失败，也让任务可改可追溯
  3. 停摆就点继续；点两次没反应就发文字；队列空就发兜底
     —— 任何时候都不 break 退出

用法：
  python night_drive.py --dry-run --once       # 试跑一轮
  python night_drive.py                        # 正式值守（23:00-09:00）
"""
import sys, time, json, argparse
from datetime import datetime
from pathlib import Path

sys.path.insert(0, r'D:\idv_datamine_isolated\tools')
import night_watch as nw

GAME = Path(r'C:\Users\Administrator\Desktop\杂七杂八\红渊\game')
TASKS = GAME / 'tasks'
STATE = GAME / 'tools' / '_drive_state.json'
LOGF = GAME / 'tools' / '_drive.log'

EXCLUDE_PREFIX = ('tasks/', 'tools/')
EXCLUDE_FILES = ('DESIGN.md', 'glossary.json', 'TASK_DONE.md')

# 输入框坐标会随窗口大小变，2026-10-28 两次实测：
#   非全屏（窗口 1845x1508）: 首页 (0.58, 0.49) / 会话 (0.60, 0.95)
#   全屏  （窗口 2582x1550）: 会话 (0.57, 0.91)   ← 底部边距变大，不能用 0.95
# 旧常量 HOME_BOX_RATIO=(0.60,0.55) 会点在「自主模式/模型选择」按钮行上，粘不进去。
HOME_BOX = (0.58, 0.49)
SESSION_BOX = (0.60, 0.95)
SESSION_BOX_FULL = (0.57, 0.91)


def box_ratio():
    try:
        hwnd = nw.find_window()
        layout, _ = nw.detect_layout(hwnd)
        if layout == 'home':
            return HOME_BOX
        l, t, r, b = nw.window_rect(hwnd)
        if (r - l) > 2400:      # 全屏
            return SESSION_BOX_FULL
        return SESSION_BOX
    except Exception:
        return SESSION_BOX


def log(msg):
    line = '[%s] %s' % (datetime.now().strftime('%m-%d %H:%M:%S'), msg)
    print(line, flush=True)
    try:
        with open(LOGF, 'a', encoding='utf-8') as f:
            f.write(line + '\n')
    except Exception:
        pass


def read_json(p, default):
    try:
        return json.loads(Path(p).read_text(encoding='utf-8'))
    except Exception:
        return default


def write_json(p, obj):
    try:
        Path(p).write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')
    except Exception:
        pass


def produced_mtime() -> float:
    """GLM 在这两个小时内真正写出过的文件的最新时间。"""
    newest = 0.0
    if not GAME.exists():
        return 0.0
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


def load_queue(path):
    try:
        return json.loads(Path(path).read_text(encoding='utf-8'))
    except Exception:
        return []


def dispatch(queue, st, dry) -> bool:
    idx = int(st.get('task_index', 0))
    if idx >= len(queue):
        return False
    t = queue[idx]
    tid = t.get('task_id') or ('T%d' % (idx + 1))
    msg = t.get('message') or ''
    if not msg:
        st['task_index'] = idx + 1
        return False
    log('=== 派发 %s（%d/%d）===' % (tid, idx + 1, len(queue)))
    ratio = box_ratio()
    if nw.send_text(msg, dry, ratio):
        st['task_index'] = idx + 1
        st['last_text_ts'] = time.time()
        log('%s 已下发' % tid)
        return True
    log('%s 下发失败' % tid)
    return False


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--start', default='23:00')
    ap.add_argument('--stop', default='09:00')
    ap.add_argument('--interval', type=int, default=30, help='轮询秒')
    ap.add_argument('--idle', type=int, default=600, help='多久算停摆（写卡需要思考，别太短）')
    ap.add_argument('--min-gap', type=int, default=120, help='两次点继续最小间隔')
    ap.add_argument('--text-gap', type=int, default=420, help='两次发文字最小间隔')
    ap.add_argument('--queue', default=str(GAME / 'tasks' / 'queue.json'))
    ap.add_argument('--done-mark', default=str(GAME / 'TASK_DONE.md'))
    ap.add_argument('--fallback', default='继续。看看 tasks/ 目录里还有哪些任务没做，'
                                          '按编号顺序接着做下一个。做完把结果追加写进 game/TASK_DONE.md。')
    ap.add_argument('--once', action='store_true')
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args(argv)

    st = read_json(STATE, {})
    st.setdefault('task_index', 0)
    st.setdefault('clicks', 0)
    st.setdefault('texts', 0)
    last_click = float(st.get('last_click_ts', 0))
    last_text = float(st.get('last_text_ts', 0))

    queue = load_queue(args.queue)
    mark = Path(args.done_mark)
    log('=== night_drive 启动 | 窗口 %s->%s idle=%ds 队列 %d 项 index=%s dry=%s ==='
        % (args.start, args.stop, args.idle, len(queue), st['task_index'], args.dry_run))
    for i, t in enumerate(queue):
        log('  [%d] %s' % (i, t.get('task_id', '?')))

    while True:
        now = time.time()
        if not nw.in_window(datetime.now(), args.start, args.stop):
            if args.once or args.dry_run:
                log('注意：不在时间窗，但 --once/--dry-run 强制跑一轮')
            else:
                log('不在时间窗，等 %s' % args.start)
                time.sleep(60)
                continue

        if not nw.proc_alive():
            log('ZCode 窗口不在了')
            break

        # ---- 1. 完成标记 ----
        if mark.exists():
            log('检测到 TASK_DONE.md -> 归档并派下一个')
            nw.archive_mark(mark)
            if dispatch(queue, st, args.dry_run):
                write_json(STATE, st)
                last_text = st.get('last_text_ts', last_text)
                if args.once:
                    break
                time.sleep(args.interval)
                continue
            else:
                log('队列已耗尽 -> 发兜底')
                if now - last_text >= args.text_gap:
                    if nw.send_text(args.fallback, args.dry_run, box_ratio()):
                        last_text = time.time()
                        st['last_text_ts'] = last_text
                        st['texts'] += 1
                        log('兜底已下发')
                write_json(STATE, st)
                if args.once:
                    break
                time.sleep(args.interval)
                continue

        # ---- 2. 停摆判定 ----
        act = produced_mtime()
        silent = now - act if act else 99999
        if silent < args.idle:
            log('正常：上次产出 %.0fs 前' % silent)
            if args.once:
                break
            time.sleep(args.interval)
            continue

        log('停摆 %.0fs（阈值 %ds）' % (silent, args.idle))

        # ---- 3a. 有系统繁忙提示 -> 点继续 ----
        busy, binfo = nw.detect_busy(nw.find_window())
        if busy:
            log('  繁忙提示条 %s' % str(binfo))
            if now - last_click >= args.min_gap:
                if nw.click_continue(args.dry_run):
                    last_click = time.time()
                    st['last_click_ts'] = last_click
                    st['clicks'] += 1
                    log('  已点继续（第 %d 次）' % st['clicks'])
                    write_json(STATE, st)
                    if args.once:
                        break
                    time.sleep(args.interval)
                    continue
        # ---- 3b. 没繁忙条 -> 发文字 ----
        if now - last_text >= args.text_gap:
            if nw.send_text('继续。', args.dry_run, box_ratio()):
                last_text = time.time()
                st['last_text_ts'] = last_text
                st['texts'] += 1
                log('  已发送「继续。」（第 %d 次）' % st['texts'])
                write_json(STATE, st)
                if args.once:
                    break
                time.sleep(args.interval)
                continue
        log('  冷却中（距上次动作 %.0fs）' % (now - max(last_click, last_text)))
        if args.once:
            break
        time.sleep(args.interval)

    write_json(STATE, st)
    log('=== night_drive 退出 ===')
    return 0


if __name__ == '__main__':
    sys.exit(main())
