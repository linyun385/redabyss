# -*- coding: utf-8 -*-
"""一次性探针：从 ZCode 事件日志复原「它在不在干活的判定」，验证误报率。

不做常驻，只用来对照时间线：给定时刻 t，按当时的日志能不能判对。
判定（每个时刻只用 t 之前的数据，不偷看未来）：
  ACTIVE  = 有未完成的 tool.call（toolCallId 有 started 没 completed）
            或未完成的 model.request（spanId 有 started 没 completed）
            或最近 60 秒内有非心跳事件
  STOPPED = 以上都不成立
"""
import json, sys
from datetime import datetime, timedelta, timezone

LOG = r'C:\Users\Administrator\.zcode\cli\log\2026-10-30.jsonl'
LOG2 = r'C:\Users\Administrator\.zcode\cli\log\zcode-2026-10-30.jsonl'
HEART = ('memory_sample',)


def load(path):
    ev = []
    for line in open(path, encoding='utf-8', errors='replace'):
        try:
            o = json.loads(line)
        except Exception:
            continue
        ts = o.get('timestamp')
        if not ts:
            continue
        ev.append(o)
    ev.sort(key=lambda o: o['timestamp'])
    return ev


def classify_at(ev, t, quiet=60, tool_cap=1800):
    open_tool, open_model = {}, {}
    last_act = None
    for o in ev:
        ts = o['timestamp']
        if ts > t:
            break
        e = o.get('event') or ''
        if e in HEART:
            continue
        if e == 'tool.call.started':
            open_tool[o.get('toolCallId')] = ts
        elif e == 'tool.call.completed':
            open_tool.pop(o.get('toolCallId'), None)
        elif e == 'model.request.started':
            open_model[o.get('spanId')] = ts
        elif e == 'model.request.completed':
            open_model.pop(o.get('spanId'), None)
        last_act = ts
    dt = lambda a, b: (datetime.fromisoformat(b.replace('Z', '+00:00')) -
                       datetime.fromisoformat(a.replace('Z', '+00:00'))).total_seconds()
    # 未完成但已经超过 tool_cap 的算死壳，不算在跑
    live_tool = {k: v for k, v in open_tool.items() if dt(v, t) < tool_cap}
    live_model = {k: v for k, v in open_model.items() if dt(v, t) < tool_cap}
    quiet_s = dt(last_act, t) if last_act else 99999
    if live_tool:
        return 'ACTIVE', '工具在跑 %d 个（%s 起，%.0fs）' % (
            len(live_tool), min(live_tool.values())[11:19], min(dt(v, t) for v in live_tool.values()))
    if live_model:
        return 'ACTIVE', '等模型回 %d 个（%s 起）' % (len(live_model), min(live_model.values())[11:19])
    if quiet_s <= quiet:
        return 'ACTIVE', '%.0fs 前还有事件' % quiet_s
    return 'STOPPED', '静默 %.0fs（最后事件 %s）' % (quiet_s, last_act[11:19] if last_act else '-')


if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else LOG2
    ev = load(path)
    print('事件 %d 条，范围 %s ~ %s' % (len(ev), ev[0]['timestamp'][11:19], ev[-1]['timestamp'][11:19]))
    base = datetime.fromisoformat(ev[0]['timestamp'].replace('Z', '+00:00'))
    t = base
    end = datetime.fromisoformat(ev[-1]['timestamp'].replace('Z', '+00:00'))
    while t <= end:
        st, why = classify_at(ev, t.isoformat().replace('+00:00', 'Z'))
        print('%s %-7s %s' % (t.strftime('%H:%M:%S'), st, why))
        t += timedelta(seconds=30)
