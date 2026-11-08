# -*- coding: utf-8 -*-
"""glm_watch.py v4 —— 哨兵模式（2026-11-04 按 AGENTS.md §7 重写）

★ 为什么改：v3 违反用户定下的规程。
  用户原话：「监控脚本本质是把你自己叫醒去操作给GLM输入，实在没办法了你再吵醒我」。
  v3 自己调 send_now.py 发话 —— 但 send_now.py 报 rc=0 只代表进程退出，
  文字根本进不了 ZCode（2026-11-04 01:23/01:26/01:29 三次全是假成功）。

v4 只做三件事：
  1. 检测停滞（rollout 总字节 + 最新 mtime，双条件）
  2. 停滞 → 写 tools/_glm_alert.json（把「建议发什么」写进去，让 DSH 会话醒来处理）
  3. DSH 迟迟没处理（再等 15 分钟）→ 才用语音叫用户

它不再发送、不再直接叫人。

用法：
  python tools\\glm_watch.py --dry-run      只报状态
  python tools\\glm_watch.py                真跑（后台）
  python tools\\glm_watch.py --no-wake      永不语音叫用户
"""
import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
GAME = Path(__file__).resolve().parents[1]
HERE = GAME / 'tools'
STATE = HERE / '_glm_watch_state.json'
ALERT = HERE / '_glm_alert.json'
LOG = HERE / '_glm_watch.log'
ROLL = Path(r'C:\Users\Administrator\.zcode\cli\rollout')
NOTIFY = Path(r'C:\Users\Administrator\Documents\deepseek-harness\default-workspace\notify_done.ps1')
DESIGN = GAME / 'docs' / 'design'
LESSON = GAME / 'docs' / 'lesson'
TASKS = GAME / 'tasks'

IDLE_ALERT = 300      # 停滞多久写告警（给 DSH 会话）
IDLE_WAKE = 1200      # 告警后再多久没人处理，才叫用户
RETRY_EVERY = 900
RETRY_MAX = 4
INTERVAL = 30

MILESTONES = [
    ('T320', DESIGN, ['T320_MECHANISMS.md', 'T321_REDUNDANCY.md',
                      'T322_MONOTONY.md', 'T323_RULES.md', 'T324_GAPS.md']),
    ('T330', DESIGN / 'stream', ['T330_STREAMS_TODAY.md', 'T331_UNIVERSAL_POOL.md',
                                 'T332_MATRIX.md', 'T333_EVENTS.md', 'T334_COST.md']),
    ('T335', DESIGN / 'stream', ['T335_PRUNE.md', 'T335_PRUNE.csv']),
    ('T300', LESSON, ['00_MAP.md', '01_PLAY_CARD.md', '02_SYNTAX_BASIC.md',
                      '03_SYNTAX_PROJECT.md', '04_DATA.md', '05_EXERCISE.md']),
]


def log(msg):
    line = '%s  %s' % (datetime.now().strftime('%m-%d %H:%M:%S'), msg)
    print(line, flush=True)
    try:
        with LOG.open('a', encoding='utf-8') as f:
            f.write(line + '\n')
    except Exception:
        pass


def snapshot():
    if not ROLL.exists():
        return 0, 0, 0.0
    total = n = 0
    newest = 0.0
    for p in ROLL.glob('model-io-sess*.jsonl'):
        try:
            st = p.stat()
            total += st.st_size
            newest = max(newest, st.st_mtime)
            n += 1
        except Exception:
            continue
    return total, n, newest


def describe_progress():
    bits = []
    for name, d, files in MILESTONES:
        try:
            have = sum(1 for f in files if (d / f).exists())
        except Exception:
            have = 0
        bits.append('%s %d/%d' % (name, have, len(files)))
    return ' | '.join(bits)


def write_alert(reason, idle, total, n):
    """写给 DSH 会话看的告警。含建议动作。"""
    d = {
        'at': datetime.now().isoformat(timespec='seconds'),
        'reason': reason,
        'idle_sec': round(idle),
        'files': n,
        'total': total,
        'progress': describe_progress(),
        'todo': [
            '1. 打开 ZCode 看它在干什么（pet_act shot 或读窗口）',
            '2. 需要发话就用 tools/send_now.py，但必须验证：120 秒内 rollout 增长才算发出去',
            '3. 发完盯 2 分钟；没增长就换方式（点输入框、手动粘贴坐标）',
            '4. 处理完删掉这个文件',
        ],
    }
    try:
        ALERT.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding='utf-8')
        log('★ 已写告警 %s（停 %.0f 秒，进度 %s）' % (ALERT.name, idle, d['progress']))
    except Exception as e:
        log('写告警失败 %s' % e)


def clear_alert():
    try:
        if ALERT.exists():
            ALERT.unlink()
    except Exception:
        pass


def alert_age():
    try:
        return time.time() - ALERT.stat().st_mtime if ALERT.exists() else None
    except Exception:
        return None


def wake_user(reason, n):
    if not NOTIFY.exists():
        log('  [WAKE] 找不到 notify_done.ps1，蜂鸣')
        for _ in range(6):
            print('\a', end='', flush=True)
            time.sleep(0.4)
        return
    try:
        subprocess.Popen(['pwsh', '-NoProfile', '-File', str(NOTIFY),
                          '-Message', 'GLM 卡住了，DSH 也没处理（第 %d 次）' % n,
                          '-Detail', reason,
                          '-SpeakEverySeconds', '25', '-MaxSpeaks', '12'],
                         cwd=str(NOTIFY.parent))
        log('  [WAKE] 已起语音闹铃（第 %d 次）' % n)
    except Exception as e:
        log('  [WAKE] 闹铃失败 %s' % str(e)[:80])


def write_state(d):
    try:
        d['updated'] = datetime.now().isoformat(timespec='seconds')
        STATE.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding='utf-8')
    except Exception:
        pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--no-wake', action='store_true')
    a = ap.parse_args()

    total, n, newest = snapshot()
    if n == 0:
        log('rollout 目录里没有 model-io 文件（%s）' % ROLL)
        return 2

    if a.dry_run:
        gap = time.time() - newest
        log('监控 %d 个文件 %.2f MB；最近写入 %.0f 秒前' % (n, total / 1048576, gap))
        log('进度：%s' % describe_progress())
        log('告警文件：%s' % ('存在，%.0f 秒前写的' % alert_age() if ALERT.exists() else '无'))
        return 0

    log('哨兵 v4 启动：间隔 %ds，停滞 %ds 写告警，%ds 无人处理后叫用户'
        % (INTERVAL, IDLE_ALERT, IDLE_WAKE))
    log('进度：%s' % describe_progress())

    last_total, last_mtime = total, newest
    last_growth = time.time()
    alerted_at = 0.0
    wake_count = 0
    last_wake = 0.0

    while True:
        time.sleep(INTERVAL)
        cur_total, cur_n, cur_mtime = snapshot()
        grew = cur_total - last_total
        if grew > 0 or cur_mtime > last_mtime + 0.5:
            last_total, last_mtime = cur_total, cur_mtime
            last_growth = time.time()
            alerted_at = 0.0
            wake_count = 0
            clear_alert()
            log('有产出（%.2f MB，%+d）%s' % (cur_total / 1048576, grew, describe_progress()))
            write_state({'state': 'running', 'files': cur_n, 'total': cur_total, 'delta': grew})
            continue

        idle = time.time() - last_growth

        # 第一层：停滞 → 写告警，把 DSH 叫醒
        if idle >= IDLE_ALERT and alerted_at == 0.0:
            write_alert('rollout 已 %.0f 秒无新增' % idle, idle, cur_total, cur_n)
            alerted_at = time.time()
            write_state({'state': 'alert_written', 'files': cur_n, 'total': cur_total,
                         'idle_sec': round(idle)})
            continue

        # 第二层：告警放了很久没人处理，才叫用户
        if alerted_at and idle >= IDLE_ALERT + IDLE_WAKE:
            if a.no_wake:
                continue
            now = time.time()
            if wake_count < RETRY_MAX and (last_wake == 0 or now - last_wake >= RETRY_EVERY):
                wake_count += 1
                last_wake = now
                wake_user('告警 %.0f 秒无人处理；进度 %s' % (now - alerted_at, describe_progress()),
                          wake_count)
                write_state({'state': 'user_woken', 'wake_count': wake_count,
                             'files': cur_n, 'total': cur_total, 'idle_sec': round(idle)})
            continue


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        log('手动停止')
