# -*- coding: utf-8 -*-
"""GLM 哨兵：只检测、只写状态文件，不注入、不叫人。

它不试图给 ZCode 发消息（做不到）。它的唯一职责是：
持续观察 GLM 的产出有没有在动，把结论写进 _glm_status.json，
剩下的交给 DSH 会话（由 schedule 定期叫醒后读这个文件）。

看什么：
  1. TASK_DONE.md 的大小和 mtime      —— GLM 记账的唯一地方
  2. tasks/INBOX/ 下未处理文件数
  3. 最新 rollout jsonl 的字节数和 mtime —— GLM 在跑模型时这个会涨

判断：
  - 任一项在 STALL_SEC 秒内动过 → 活着
  - 全都不动 → 疑似停了，state = 'stalled'

用法：
  python tools/glm_sentinel.py            # 前台跑（调试用）
  python tools/glm_sentinel.py --loop     # 常驻循环（后台任务用）
"""
import sys, io, os, json, time, glob, argparse
from pathlib import Path
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

GAME = Path(r'C:\Users\Administrator\Desktop\杂七杂八\红渊\game')
ZCODE_ROLLOUT = Path(os.path.expanduser('~')) / '.zcode' / 'cli' / 'rollout'
STATUS = GAME / 'tools' / '_glm_status.json'

TASK_DONE = GAME / 'TASK_DONE.md'
INBOX = GAME / 'tasks' / 'INBOX'

STALL_SEC = 15 * 60       # 15 分钟完全没动静 → 疑似停了
CHECK_SEC = 60            # 每 60 秒看一次


def newest_rollout():
    try:
        fs = sorted(ZCODE_ROLLOUT.glob('model-io-sess*.jsonl'),
                    key=lambda p: p.stat().st_mtime, reverse=True)
        return fs[0] if fs else None
    except Exception:
        return None


def probe():
    now = time.time()
    out = {'ts': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'epoch': now}

    # 1. 账本
    try:
        st = TASK_DONE.stat()
        out['ledger'] = {'size': st.st_size, 'mtime': st.st_mtime,
                         'age_sec': int(now - st.st_mtime)}
        # 记账条数
        try:
            txt = TASK_DONE.read_text(encoding='utf-8', errors='replace')
            out['ledger']['entries'] = txt.count('\n## T')
        except Exception:
            out['ledger']['entries'] = -1
    except Exception as e:
        out['ledger'] = {'error': str(e)}

    # 2. INBOX
    try:
        pending = [p.name for p in INBOX.glob('*.md') if p.name.lower() != 'readme.md']
        out['inbox'] = {'pending': sorted(pending), 'count': len(pending)}
    except Exception as e:
        out['inbox'] = {'error': str(e)}

    # 3. rollout
    r = newest_rollout()
    if r:
        try:
            st = r.stat()
            out['rollout'] = {'name': r.name, 'size': st.st_size,
                              'mtime': st.st_mtime, 'age_sec': int(now - st.st_mtime)}
        except Exception as e:
            out['rollout'] = {'error': str(e)}
    else:
        out['rollout'] = {'error': 'no rollout file'}

    return out


def analyse(cur, prev):
    """和上一次比，看有没有动过。"""
    moved = []

    if 'ledger' in cur and 'ledger' in prev:
        a, b = prev['ledger'], cur['ledger']
        if a.get('size') != b.get('size') or a.get('entries') != b.get('entries'):
            moved.append('ledger')
    if 'rollout' in cur and 'rollout' in prev:
        a, b = prev['rollout'], cur['rollout']
        if a.get('size') != b.get('size'):
            moved.append('rollout')
    if 'inbox' in cur and 'inbox' in prev:
        if prev['inbox'].get('count') != cur['inbox'].get('count'):
            moved.append('inbox')

    # 距「最后一次确认有动静」多久了
    last_move_ts = prev.get('last_move_epoch') or cur['epoch']
    if moved:
        last_move_ts = cur['epoch']
    idle = int(cur['epoch'] - last_move_ts)

    cur['last_move_epoch'] = last_move_ts
    cur['last_move_moved'] = moved
    cur['idle_sec'] = idle
    cur['stalled'] = idle >= STALL_SEC
    cur['state'] = 'stalled' if cur['stalled'] else 'alive'
    return cur


def write_status(obj):
    tmp = STATUS.with_suffix('.tmp')
    try:
        tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding='utf-8')
        os.replace(tmp, STATUS)
    except Exception as e:
        print('写状态失败:', e)


def one_shot():
    prev = {}
    try:
        if STATUS.exists():
            prev = json.loads(STATUS.read_text(encoding='utf-8'))
    except Exception:
        prev = {}
    cur = analyse(probe(), prev)
    write_status(cur)
    return cur


def loop():
    print('哨兵启动。每 %d 秒检查一次，%d 分钟无动静判定停滞。' % (CHECK_SEC, STALL_SEC // 60))
    print('状态文件:', STATUS)
    try:
        while True:
            cur = one_shot()
            print('[%s] state=%s idle=%ds inbox=%d ledger=%s rollout=%s' % (
                cur['ts'], cur['state'], cur['idle_sec'],
                cur.get('inbox', {}).get('count', -1),
                cur.get('ledger', {}).get('entries', -1),
                cur.get('rollout', {}).get('size', -1)))
            time.sleep(CHECK_SEC)
    except KeyboardInterrupt:
        print('哨兵手动停止')


def until_stall():
    """阻塞模式：一直守着，检测到停滞就退出。

    退出 = 后台 job 完成 = 会话收到通知 = 我被叫醒。
    这是唯一不需要定时轮询的唤醒机制。
    """
    print('哨兵（阻塞模式）启动。检测到停滞就退出，退出即叫醒 DSH。', flush=True)
    print('阈值 %d 分钟，每 %d 秒看一次。' % (STALL_SEC // 60, CHECK_SEC), flush=True)
    prev = {}
    try:
        if STATUS.exists():
            prev = json.loads(STATUS.read_text(encoding='utf-8'))
    except Exception:
        prev = {}

    # 启动基线重置：不继承上一轮留下的「已停滞」计时，否则一启动就误判退出。
    # 2026-11-05 02:11 踩过：上一轮 status 是 stalled，新哨兵读进来立刻 idle=900 秒退出。
    prev['last_move_epoch'] = time.time()
    prev['idle_sec'] = 0
    prev.pop('stalled', None)
    print('基线已重置，从现在开始计时。', flush=True)

    beat = 0
    while True:
        cur = analyse(probe(), prev)
        write_status(cur)
        beat += 1
        # 每 10 分钟打一次心跳，免得日志太吵
        if beat % 10 == 0 or cur['stalled']:
            print('[%s] state=%s idle=%ds inbox=%d ledger=%s' % (
                cur['ts'], cur['state'], cur['idle_sec'],
                cur.get('inbox', {}).get('count', -1),
                cur.get('ledger', {}).get('entries', -1)), flush=True)

        if cur['stalled']:
            print('=== STALLED === 停滞 %d 秒，退出以叫醒 DSH' % cur['idle_sec'], flush=True)
            print(json.dumps(cur, ensure_ascii=False, indent=1), flush=True)
            print('', flush=True)
            print('>>> 叫醒了 DSH，下一步该做的（读完这段再动手）：', flush=True)
            print('  1. 看 game/TASK_DONE.md 最后两条，确认停在哪', flush=True)
            print('  2. 数 game/tasks/INBOX/*.md 还有几个待处理', flush=True)
            print('  3. 记一行到 game/tools/_glm_alerts.log', flush=True)
            print('  4. INBOX 空了就往里补任务（QUEUE_20261105.md 兜底方向）', flush=True)
            print('  5. ★ 处理完必须立刻重挂一个新哨兵，否则监控就断了：', flush=True)
            print('     python tools/glm_sentinel.py --until-stall  （run_in_background）', flush=True)
            return 1
        prev = cur
        time.sleep(CHECK_SEC)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--loop', action='store_true', help='常驻轮询，永不退出（只写状态）')
    ap.add_argument('--until-stall', action='store_true', help='阻塞守候，检测到停滞就退出（用来叫醒 DSH）')
    a = ap.parse_args()
    if a.until_stall:
        sys.exit(until_stall())
    elif a.loop:
        loop()
    else:
        c = one_shot()
        print(json.dumps(c, ensure_ascii=False, indent=1))
