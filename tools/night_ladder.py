# -*- coding: utf-8 -*-
"""夜班升级阶梯（Level 2/3）：叫不醒 → 半小时再叫 → 一小时后每 10 分钟硬催。

设计（2026-10-30 23:0x 用户定）：
  L1  fire_watch 检测到停摆 → alarm.ps1 短报警（once）
  L2  30 分钟内没人处理 → 本脚本再响一次（loud：念 4 遍 + 长蜂鸣）
  L3  超过 60 分钟还没动 → 每 10 分钟：发一次「下一棒任务原文」+ loud 报警，直到监控显示在工作

判据复用 fire_watch.events_state()（后端事件流，不看前台）。
安全阀：
  · 用户 60 秒内碰过键鼠 → 什么都不做（不抢焦点、不发消息）
  · 只有 --allow-send 才真的输入；默认只报警不输入（坐标没校准前别开）
  · 队列空 → 不发，只报警
"""
import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

GAME = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(GAME / 'tools'))
import fire_watch as fw          # 复用事件判据 / 队列 / 空闲检测
from PIL import ImageGrab
import numpy as np

LOG = GAME / 'tools' / '_ladder.log'
ALARM = GAME / 'tools' / 'alarm.ps1'
SEND = GAME / 'tools' / 'send_robust.py'


def log(m):
    line = '[%s] %s' % (datetime.now().strftime('%H:%M:%S'), m)
    print(line, flush=True)
    try:
        LOG.open('a', encoding='utf-8').write(line + '\n')
    except Exception:
        pass


def alarm(mode, text='红渊夜班：GLM 还是停着，需要你过来。'):
    try:
        subprocess.run(['powershell', '-ExecutionPolicy', 'Bypass', '-File', str(ALARM),
                        '-Text', text, '-Mode', mode], timeout=180)
        log('  报警 %s 已响' % mode)
    except Exception as e:
        log('  报警失败：%s' % e)


def send_next_task():
    """把队列里第一个未完成任务的原文发过去（走已经验证过的物理点击脚本）。"""
    tid, msg = fw.next_in_queue()
    if not msg:
        log('  队列空/取不到消息，跳过发送')
        return False
    try:
        r = subprocess.run([sys.executable, str(SEND), '--text', msg],
                           capture_output=True, text=True, encoding='utf-8', errors='replace',
                           timeout=180)
        ok = '已发送' in (r.stdout or '')
        log('  发送 %s → %s' % (tid, 'ok' if ok else '失败'))
        return ok
    except Exception as e:
        log('  发送异常：%s' % e)
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--interval', type=int, default=20)
    ap.add_argument('--still', type=int, default=240, help='事件流静默多久算停摆')
    ap.add_argument('--l2-after', type=int, default=1800, help='停摆后多久再响（默认 30 分钟）')
    ap.add_argument('--l3-after', type=int, default=3600, help='停摆后多久开始硬催（默认 60 分钟）')
    ap.add_argument('--l3-every', type=int, default=600, help='硬催间隔（默认 10 分钟）')
    ap.add_argument('--user-idle', type=int, default=60, help='用户 60 秒内碰过键鼠就别动')
    ap.add_argument('--allow-send', action='store_true', help='允许 L3 真的输入（坐标校准后再开）')
    ap.add_argument('--max-hours', type=float, default=9.0)
    a = ap.parse_args()

    log('=== 升级阶梯启动 | L2@%ds L3@%ds 每%ds | 允许输入=%s ==='
        % (a.l2_after, a.l3_after, a.l3_every, a.allow_send))
    dead = 0
    t0 = None            # 本次停摆起始时间
    last_alarm = 0.0
    last_send = 0.0
    start = time.time()

    while True:
        if (time.time() - start) / 3600 > a.max_hours:
            log('跑满 %.1f 小时，退出' % a.max_hours)
            return 0

        ok, why = fw.events_state()
        if ok is None:
            log('  读不到事件日志（%s），跳过' % why)
            time.sleep(a.interval)
            continue

        if ok:
            if t0 is not None:
                log('  恢复了（%s）——阶梯重置' % why)
            t0 = None
            dead = 0
            time.sleep(a.interval)
            continue

        dead += 1
        if dead < 3:                       # 连续 3 次判停（约 1 分钟）才算
            log('  疑似停摆 %d/3（%s）' % (dead, why))
            time.sleep(a.interval)
            continue

        if t0 is None:
            t0 = time.time()
            log('  确认停摆（%s），开始计时' % why)

        idle = fw.user_idle_seconds()
        if idle < a.user_idle:
            log('  用户正在操作（空闲 %.0fs），不打扰' % idle)
            time.sleep(a.interval)
            continue

        el = time.time() - t0
        # L2：30 分钟后再响
        if el >= a.l2_after and last_alarm == 0.0:
            alarm('loud', '红渊夜班：已经停了三十分钟，还没有人处理。')
            last_alarm = time.time()

        # L3：一小时后每 10 分钟硬催
        if el >= a.l3_after and time.time() - max(last_send, last_alarm) >= a.l3_every:
            log('  L3：已经停 %.0f 分钟，开始硬催' % (el / 60))
            if a.allow_send:
                send_next_task()
                last_send = time.time()
            alarm('loud', '红渊夜班：任务还是停着，我十分钟后再试一次。')

        time.sleep(a.interval)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        log('手动停止')
