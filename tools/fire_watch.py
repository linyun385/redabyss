# -*- coding: utf-8 -*-
"""红渊项目夜间救火器 v3 —— 带自动换会话

分级处理停摆（都基于「产出目录多久没动静」）：
  1. 停摆 >10 分钟  -> 发一句「继续。」
  2. 再停摆 >10 分钟 -> 判定会话已坏（1210 上下文超长），
                       自动 新建会话 + 发下一条任务消息
  3. 循环往复，直到时间窗结束

为什么需要自动换会话：
  2026-10-28 实测，跑够久的会话会撞上智谱 1210（API 调用参数有误），
  retryable=false，同一个会话里怎么重试都没用，只能换新会话。
  换会话零成本，因为所有任务细节都在 tasks/*.md 里。
"""
import sys, io, time, json, re, argparse, subprocess
from datetime import datetime, timezone
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r'C:\Users\Administrator\Desktop\杂七杂八\红渊\game\tools')
import zwin
import pyautogui, pyperclip
from PIL import ImageGrab

GAME = Path(r'C:\Users\Administrator\Desktop\杂七杂八\红渊\game')
TASKS = GAME / 'tasks'
DONE = GAME / 'TASK_DONE.md'
QUEUE = TASKS / 'queue.json'
STATE = GAME / 'tools' / '_fire_state.json'
LOGF = GAME / 'tools' / '_fire.log'
SHOTS = GAME / 'tools'

HOME_BOX = (0.595, 0.5206)     # 首页态输入框（2026-10-29 23:2x 实测）
SESSION_BOX = (0.30, 0.915)    # 会话态输入框**文本区上部**（实测可用）
# 踩过的坑，别改回去：
#   (0.59, 0.95)  = 右侧发送按钮 → 点了会选中整页文字，什么都没粘进去
#   (0.315,0.946) = 「完全访问」下拉 → 点了会弹模式菜单
#   (0.55, 0.92)  = 旧常量，在全屏/停靠 Chrome 的布局下点在按钮行上，粘不进去
EXCLUDE_PREFIX = ('tasks/', 'tools/')
EXCLUDE_FILES = ('DESIGN.md', 'glossary.json', 'TASK_DONE.md')


def log(msg):
    line = '[%s] %s' % (datetime.now().strftime('%H:%M:%S'), msg)
    print(line, flush=True)
    try:
        open(LOGF, 'a', encoding='utf-8').write(line + '\n')
    except Exception:
        pass


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


def last_done_task():
    """从 TASK_DONE.md 里找最后一个完成的任务号。"""
    try:
        text = DONE.read_text(encoding='utf-8', errors='replace')
    except Exception:
        return 0
    nums = [int(n) for n in re.findall(r'##\s*T(\d+)\s*[完写]', text)]
    return max(nums) if nums else 0


def done_set():
    """已完成的 {任务号: True}。格式 `## T35 完成`。"""
    try:
        text = DONE.read_text(encoding='utf-8', errors='replace')
    except Exception:
        return set()
    return set(int(n) for n in re.findall(r'##\s*T(\d+)\s*[完写]', text))


def next_in_queue():
    """按 tasks/queue.json 的顺序找第一个「还没写进 TASK_DONE」的任务。

    2026-10-29 修正：原来按 TASK_DONE 最大编号 +1 推，会推到 T27（旧队列
    残留、T27-T34 已废弃），今晚的队列是 T35-T43，必须读 queue.json。
    返回 (label, message) 或 (None, None)。
    """
    try:
        q = json.loads(QUEUE.read_text(encoding='utf-8'))
    except Exception:
        return None, None
    if not isinstance(q, list):
        return None, None
    done = done_set()
    for item in q:
        tid = str(item.get('task_id', '')).strip()
        m = re.match(r'T(\d+)$', tid)
        if not m:
            continue
        if int(m.group(1)) in done:
            continue
        msg = item.get('message') or msg_for_task(int(m.group(1)))
        if msg:
            return tid, msg
    return None, None


def msg_for_task(n):
    f = TASKS / ('T%d.md' % n)
    if not f.exists():
        return None
    return ('继续红渊卡牌项目。前 %d 个任务已完成，产物都在 '
            'C:/Users/Administrator/Desktop/杂七杂八/红渊/game/。'
            '现在做 T%d：读 game/tasks/T%d.md 并严格照做。'
            '做完跑对应自检，通过后追加写 game/TASK_DONE.md。'
            % (n - 1, n, n))


def shot(hwnd, name):
    try:
        l, t, r, b = zwin.rect(hwnd)
        ImageGrab.grab(bbox=(l, t, r, b)).save(str(SHOTS / name))
    except Exception:
        pass


_PREV = {'img': None}


_LOG = {'path': None, 'size': -1, 'changed_at': 0.0}


def zcode_log_path():
    """ZCode 的实时运行日志（后端，不看前台）。

    2026-10-30 00:05 实测：`~/.zcode/cli/log/zcode-<日期>.jsonl` 每几秒就长一截
    （12 秒长了 1153 字节，内容是 session event persistence / rpc 调用），
    而它停手后就不再增长。比前端像素干净得多，也不用把窗口拉到前台。
    """
    import os
    d = Path(os.path.expanduser('~')) / '.zcode' / 'cli' / 'log'
    today = d / ('zcode-%s.jsonl' % datetime.now().strftime('%Y-%m-%d'))
    if today.exists():
        return today
    try:
        return max(d.glob('zcode-*.jsonl'), key=lambda p: p.stat().st_mtime)
    except Exception:
        return None


def log_silent_seconds():
    """后端日志多久没长过（秒）。返回 None 表示读不到日志。"""
    p = zcode_log_path()
    if not p:
        return None
    _LOG['path'] = str(p)
    try:
        size = p.stat().st_size
    except Exception:
        return None
    if size != _LOG['size']:
        _LOG['size'] = size
        _LOG['changed_at'] = time.time()
        return 0.0
    if not _LOG['changed_at']:
        _LOG['changed_at'] = time.time()
    return time.time() - _LOG['changed_at']


_EV = {'key': None, 'state': None}

HEART_EVENTS = ('zcode_protocol.process.memory_sample', 'memory_sample')


def zcode_event_log():
    """事件日志（比 zcode-<日期>.jsonl 更结构化）：每行一个 JSON，带 turnId/toolCallId。"""
    import os
    d = Path(os.path.expanduser('~')) / '.zcode' / 'cli' / 'log'
    today = d / ('zcode-%s.jsonl' % datetime.now().strftime('%Y-%m-%d'))
    if today.exists():
        return today
    try:
        return max(d.glob('zcode-*.jsonl'), key=lambda p: p.stat().st_mtime)
    except Exception:
        return None


def events_state(quiet=120, tool_cap=1800):
    """用 ZCode 自己的事件流判「在不在干活」——比看文件时间准得多。

    2026-10-30 00:22 复盘：仓库文件 295 秒没变，但日志里 model.request 每 30 秒一条，
    它一直在浏览器里实测 → 产出时间戳判据必然误报。事件流能直接看到：
      · tool.call.started 有、completed 没有  → 工具正在跑（长命令/浏览器操作）
      · model.request.started 有、completed 没有 → 正在等模型回
      · 最近 60s 有过事件 → 还在动
    真停了才会三项都不成立。今天 00:00-00:19 的时间线用这个判定，全程 ACTIVE，零误报。
    """
    p = zcode_event_log()
    if not p:
        return None, 'no log'
    try:
        size = p.stat().st_size
    except Exception:
        return None, 'stat fail'
    key = (str(p), size)
    if _EV['key'] == key and _EV['state']:
        st, detail, last_ts, tool_since, model_since = _EV['state']
    else:
        open_tool, open_model = {}, {}
        last_ts = None
        for line in p.open(encoding='utf-8', errors='replace'):
            try:
                o = json.loads(line)
            except Exception:
                continue
            e = o.get('event') or ''
            ts = o.get('timestamp')
            if not ts or e in HEART_EVENTS:
                continue
            if e == 'tool.call.started':
                open_tool[o.get('toolCallId')] = ts
            elif e == 'tool.call.completed':
                open_tool.pop(o.get('toolCallId'), None)
            elif e == 'model.request.started':
                open_model[o.get('spanId')] = ts
            elif e == 'model.request.completed':
                open_model.pop(o.get('spanId'), None)
            last_ts = ts
        # 用**最近**那次未完成调用算年龄（不是最早那次）。
        # 2026-10-30 01:12 踩过：一个陈年未完成 tool 把 a_tool 拉到 1800s 以上，
        # 于是刚起的 model.request 被忽略，GLM 明明在思考却被判停摆。
        tool_since = max(open_tool.values()) if open_tool else None
        model_since = max(open_model.values()) if open_model else None
        st = 'active' if (open_tool or open_model) else 'quiet'
        detail = 'tool=%d model=%d' % (len(open_tool), len(open_model))
        _EV['state'] = (st, detail, last_ts, tool_since, model_since)
        _EV['key'] = key

    def age(ts):
        if not ts:
            return 99999.0
        try:
            return (datetime.now(timezone.utc) -
                    datetime.fromisoformat(ts.replace('Z', '+00:00'))).total_seconds()
        except Exception:
            return 99999.0

    a_tool, a_model, a_last = age(tool_since), age(model_since), age(last_ts)
    if a_tool < tool_cap:
        return True, '工具在跑 %.0fs（%s）' % (a_tool, detail)
    if a_model < tool_cap:
        return True, '等模型回 %.0fs（%s）' % (a_model, detail)
    if a_last <= quiet:
        return True, '%.0fs 前还有事件（%s）' % (a_last, detail)
    return False, '静默 %.0fs（%s）' % (a_last, detail)


def button_state(hwnd):
    """判据（2026-10-29 23:5x 改）：看会话区**下半段有没有在变**，不看按钮。

    为什么换掉老判据：150% 缩放 + Chrome 停靠在右侧那种布局下，右下角按钮
    在「工作中」和「已停」两种状态都读到 ~0.94（实测 GLM 23:08 就停了，
    它还报在跑，白盯 13 分钟）。
    GLM 干活时这块一直在变（思考计时、新消息、终端输出）；停住则帧差 = 0.00。

    返回 (帧差, 是否在动)。
    """
    try:
        l, t, r, b = zwin.rect(hwnd)
        w, h = r - l, b - t
        img = ImageGrab.grab(bbox=(l + int(w * 0.17), t + int(h * 0.60),
                                   l + int(w * 0.55), t + int(h * 0.885))).convert('L')
        px = list(img.resize((96, 48)).getdata())
        prev = _PREV['img']
        _PREV['img'] = px
        if prev is None or len(prev) != len(px):
            return 0.0, True          # 首帧按「在动」处理，避免一上来就发
        d = sum(abs(a - b) for a, b in zip(px, prev)) / len(px)
        return d, d > 0.15
    except Exception:
        return None, None


def user_idle_seconds():
    """距上次键盘/鼠标输入多少秒。照抄 D:\idv_datamine_isolated\tools\night_watch.py:132
    的老做法（那边 2026-10-28 就实现过「你在用电脑就别动」）。"""
    import ctypes

    class LASTINPUTINFO(ctypes.Structure):
        _fields_ = [('cbSize', ctypes.c_uint), ('dwTime', ctypes.c_ulong)]
    li = LASTINPUTINFO()
    li.cbSize = ctypes.sizeof(LASTINPUTINFO)
    if not ctypes.windll.user32.GetLastInputInfo(ctypes.byref(li)):
        return 0.0
    return (ctypes.windll.kernel32.GetTickCount() - li.dwTime) / 1000.0


def click_at(x, y):
    """物理像素点击。不能用 pyautogui.click：本机 150% 缩放下它会点偏
    （实测 (1833,803) 被点到 (2023,869)，消息根本进不了输入框）。"""
    import ctypes
    u_ = ctypes.windll.user32
    u_.SetCursorPos(int(x), int(y))
    time.sleep(0.12)
    u_.mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(0.05)
    u_.mouse_event(0x0004, 0, 0, 0, 0)


def send_at(hwnd, ratio, text, wait=0.7):
    """点指定位置 -> 清空 -> 粘贴 -> 不回车。"""
    if not zwin.force_foreground(hwnd):
        return False
    time.sleep(0.5)
    x, y = zwin.pt(hwnd, *ratio)
    click_at(x, y)
    time.sleep(0.4)
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.1)
    pyautogui.press('delete')
    time.sleep(0.2)
    pyperclip.copy(text)
    time.sleep(0.2)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(wait)
    return True


def send_continue(hwnd):
    """停摆时不要发空话「继续。」——把**当前这一项还没完成的任务**原文再发一遍，
    这样它醒过来就知道该干什么（GLM 忙时会无视排队消息，见 2026-10-29 23:2x）。"""
    qid, qmsg = next_in_queue()
    text = qmsg if qmsg else '继续。'
    if send_at(hwnd, SESSION_BOX, text):
        pyautogui.press('enter')
        time.sleep(0.3)
        shot(hwnd, '_fire_nudge.png')
        log('  已发推进消息（%s）' % (qid or '继续。'))
        return True
    return False


def new_session_and_send(hwnd):
    """新建会话 + 发下一条任务。返回是否成功。"""
    if not zwin.force_foreground(hwnd):
        log('  拉不到前台，跳过换会话')
        return False
    # 优先读 queue.json（今晚队列 T35-T43），读不到才退回旧逻辑
    qid, qmsg = next_in_queue()
    if qid:
        target, msg = qid, qmsg
    else:
        n = last_done_task()
        target, msg = None, None
        for cand in range(n + 1, n + 6):
            m = msg_for_task(cand)
            if m:
                target, msg = cand, m
                break
        if not target:
            log('  队列已空且找不到下一个任务文件，改为发兜底')
            msg = ('继续。看看 game/tasks/ 里还有哪些任务没做，按编号顺序接着做下一个。'
                   '做完把结果追加写进 game/TASK_DONE.md。')
            target = '兜底'

    log('  换会话：新建任务，准备发送 T%s' % target)
    pyautogui.hotkey('ctrl', 'n')
    time.sleep(3.0)
    shot(hwnd, '_fire_new_task.png')

    if not send_at(hwnd, HOME_BOX, msg, wait=0.8):
        return False
    shot(hwnd, '_fire_pasted.png')
    pyautogui.press('enter')
    time.sleep(8)
    shot(hwnd, '_fire_sent.png')
    log('  新会话已发送 T%s' % target)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--start', default='22:40')
    ap.add_argument('--stop', default='09:00')
    ap.add_argument('--interval', type=int, default=30)
    ap.add_argument('--idle', type=int, default=600, help='产出停滞判定秒数')
    ap.add_argument('--visual-idle', type=int, default=60,
                    help='界面静止多少秒算停摆（比产出更灵敏）')
    ap.add_argument('--hard-idle', type=int, default=1800,
                    help='无论界面怎么动，产出停滞超过这么久就强制干预（兜底）')
    ap.add_argument('--escalate', type=int, default=600,
                    help='发过「继续。」后再等多少秒仍停摆就换会话')
    ap.add_argument('--gap', type=int, default=120, help='两次动作最小间隔')
    ap.add_argument('--user-idle', type=int, default=20,
                    help='你多久没碰键鼠才算「人走了」；不到这个时长就完全不打扰你'
                         '（照抄 night_watch.py 的老做法）')
    ap.add_argument('--judge', default='events', choices=['pixel', 'log', 'events'],
                    help='判据：pixel=会话区帧差（要看得到窗口）；log=运行日志有没有长；'
                         'events=按事件流判未完成工具/模型调用（最准，默认）')
    ap.add_argument('--notify-only', action='store_true',
                    help='只检测不输入：判定停摆就打印现场并 exit 3，让指挥席（DSH 会话）接手。'
                         '这是用户 2026-10-29 23:5x 定的主方案：只有人会读画面、会判断停在哪，'
                         '脚本盲打字 4 次全都静默失败。')
    ap.add_argument('--confirm', type=int, default=2,
                    help='连续判定「已停」多少次才通知（默认 2 次，进一步压误报）')
    ap.add_argument('--alarm', default='once', choices=['off', 'once', 'loud'],
                    help='停摆时用声音叫你：off=不响；once=短报警；loud=长报警'
                         '（同一晚第 2 次停摆起自动升级成 loud）')
    ap.add_argument('--once', action='store_true')
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    try:
        st = json.loads(STATE.read_text(encoding='utf-8'))
    except Exception:
        st = {}
    last_act = float(st.get('last_act_ts', 0))
    nudged_at = float(st.get('nudged_at', 0))   # 上次发「继续。」的时间
    sessions = int(st.get('sessions', 1))
    stop_hits = 0          # 连续判定「已停」的次数，够 --confirm 次才通知（降误报）
    vis = {'hash': None, 'ts': 0}               # 界面指纹状态

    log('=== 救火器 v3 启动 | %s->%s idle=%ds escalate=%ds dry=%s ==='
        % (args.start, args.stop, args.idle, args.escalate, args.dry_run))

    while True:
        now = time.time()
        hhmm = datetime.now().strftime('%H:%M')
        inside = (args.start <= hhmm < args.stop) if args.start < args.stop \
            else (hhmm >= args.start or hhmm < args.stop)
        if not inside:
            if args.once or args.dry_run:
                log('不在时间窗，强跑一轮')
            else:
                time.sleep(60)
                continue

        # ---- 0. 你先：你还在碰键鼠就完全不打扰（照抄 night_watch 的老做法）----
        # 这一步必须在任何拉窗口/点像素之前，否则会跟你抢前台。
        ui = user_idle_seconds()
        if not (args.once or args.dry_run or args.notify_only) and ui < args.user_idle:
            if int(now) % 300 < args.interval:      # 每 5 分钟记一次，别刷屏
                log('你在用电脑（距上次输入 %.0fs < %ds），本轮不动' % (ui, args.user_idle))
            time.sleep(args.interval)
            continue

        hwnd = zwin.find_zcode()
        if not hwnd:
            log('ZCode 窗口不在了 -> 退出')
            break

        why_note = '-'
        if args.judge == 'events':
            # 后端判据（最准）：看事件流里有没有「未完成的工具调用 / 未完成的模型请求」
            ok, why = events_state()
            if ok is None:
                log('  读不到事件日志（%s），跳过本轮' % why)
                time.sleep(args.interval)
                continue
            working = ok
            silent = 0 if ok else args.idle
            ratio = 0
            why_note = why
            if args.once or args.dry_run:
                log('  事件判据：%s → %s' % (why, '在跑' if ok else '已停'))
        elif args.judge == 'log':
            # 后端判据：ZCode 自己的运行日志多久没长过 = 它多久没动手
            ls = log_silent_seconds()
            if ls is None:
                log('  读不到 ZCode 日志，跳过本轮')
                time.sleep(args.interval)
                continue
            silent = ls
            ratio = ls
            working = ls < 10
            why_note = '日志 %.0fs 没长' % ls
        else:
            act = produced_mtime()
            silent = now - act if act else 99999
            ratio, working = button_state(hwnd)
            why_note = '帧差 %.2f / 产出 %.0fs' % (ratio if ratio is not None else -1, silent)
            if working is None:
                log('  读不到会话区，按停摆处理')
                working = False

        if working:
            stop_hits = 0

        if working and silent < args.hard_idle:
            if args.once:
                log('正常：界面在动（帧差 %.2f）| 产出 %.0fs 前' % (ratio, silent))
                break
            nudged_at = 0
            time.sleep(args.interval)
            continue

        if silent > args.hard_idle:
            log('!! 硬兜底：产出已停滞 %.0fs（界面看着在动也不算数）' % silent)

        if silent < args.idle:
            if args.once:
                log('界面停了（帧差 %.2f）但 %.0fs 前有产出，再等等' % (ratio, silent))
                break
            time.sleep(args.interval)
            continue

        # ---- notify-only：到这里就交给人（DSH 会话），自己绝不输入 ----
        if args.notify_only:
            if not args.once:
                stop_hits += 1
                if stop_hits < args.confirm:
                    log('  疑似停摆 %d/%d（events 静默 %s），再确认一轮'
                        % (stop_hits, args.confirm, why_note))
                    time.sleep(args.interval)
                    continue
            log('=== GLM 停摆，交指挥席 ===')
            log('  判据=%s | %s | 静默 %.0fs | 已写进 TASK_DONE 的：%s'
                % (args.judge, why_note, silent, sorted(done_set())[-6:]))
            # 叫醒：第一次用 once，同一晚第 2 次起自动升级成 loud
            if args.alarm != 'off':
                stops = 0
                try:
                    stp = GAME / 'tools' / '_fire_stop.json'
                    if stp.exists():
                        stops = int(json.loads(stp.read_text(encoding='utf-8')).get('stops', 0))
                except Exception:
                    stops = 0
                mode = 'loud' if (stops >= 1 or args.alarm == 'loud') else 'once'
                log('  报警：%s（本晚第 %d 次停摆）' % (mode, stops + 1))
                try:
                    subprocess.run(['powershell', '-ExecutionPolicy', 'Bypass', '-File',
                                    str(GAME / 'tools' / 'alarm.ps1'),
                                    '-Text', '红渊夜班：GLM 停住了，需要你看一眼。',
                                    '-Mode', mode], timeout=120)
                except Exception as e:
                    log('  报警失败：%s' % e)
                stops += 1
            else:
                stops = 0
            try:
                (GAME / 'tools' / '_fire_stop.json').write_text(json.dumps({
                    'ts': datetime.now().isoformat(timespec='seconds'),
                    'judge': args.judge, 'why': why_note,
                    'silent_s': round(silent, 1), 'stops': stops,
                    'done': sorted(done_set())}, ensure_ascii=False, indent=2), encoding='utf-8')
            except Exception:
                pass
            sys.exit(3)

        log('停摆 %.0fs（阈值 %ds）| 上次催促 %.0fs 前 | 已换会话 %d 次'
            % (silent, args.idle, (now - nudged_at) if nudged_at else -1, sessions))

        if now - last_act < args.gap:
            if args.once:
                break
            time.sleep(args.interval)
            continue

        # 第一次：先发「继续。」
        if not nudged_at:
            if args.dry_run:
                log('  [dry] 会发「继续。」')
                last_act = now
                nudged_at = now
            else:
                if send_continue(hwnd):
                    last_act = now
                    nudged_at = now
            try:
                STATE.write_text(json.dumps({'last_act_ts': last_act,
                                             'nudged_at': nudged_at,
                                             'sessions': sessions}), encoding='utf-8')
            except Exception:
                pass
            if args.once:
                break
            time.sleep(args.interval)
            continue

        # 催促过了还停 -> 升级为换会话
        if now - nudged_at >= args.escalate:
            if args.dry_run:
                log('  [dry] 会换会话并发送 T%d'
                    % (last_done_task() + 1))
                last_act = now
                nudged_at = 0
            else:
                if new_session_and_send(hwnd):
                    sessions += 1
                    last_act = now
                    nudged_at = 0
                    log('  换会话完成（累计 %d 次）' % sessions)
                else:
                    last_act = now      # 失败也退避一轮
            try:
                STATE.write_text(json.dumps({'last_act_ts': last_act,
                                             'nudged_at': nudged_at,
                                             'sessions': sessions}), encoding='utf-8')
            except Exception:
                pass
            if args.once:
                break
            time.sleep(args.interval)
            continue

        log('  等升级条件（距催促 %.0fs / 需 %ds）'
            % (now - nudged_at, args.escalate))
        if args.once:
            break
        time.sleep(args.interval)

    log('=== 救火器退出（本晚换会话 %d 次）===' % sessions)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        log('手动停止')
