# -*- coding: utf-8 -*-
"""
arm_watch.py —— 等 GLM 真的开始写，再挂上 glm_watch.py

为什么需要它：
  glm_watch.py 的 idle 是从「进程启动」算的。如果 GLM 还没开工就先起监控，
  头 180 秒会立刻误判成「没动静」并给 GLM 发一句「继续。」—— 那是在打断它。

做法：
  盯 ~/.zcode/cli/rollout 里 model-io-sess*.jsonl 的 mtime/大小。
  一旦有文件比基线新（或出现新文件），就 subprocess 拉起 glm_watch.py，自己退出。

用法（后台跑）：
  python tools\\arm_watch.py            # 最多等 90 分钟
  python tools\\arm_watch.py --minutes 30
"""
import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROLLOUT = Path.home() / ".zcode" / "cli" / "rollout"
HERE = Path(__file__).resolve().parent
STATE = HERE / "_arm_watch_state.json"
LOG = HERE / "_arm_watch.log"

POLL_SEC = 20


def snapshot():
    """返回 {name: (size, mtime_epoch)}"""
    out = {}
    if not ROLLOUT.exists():
        return out
    for p in ROLLOUT.glob("model-io-sess*.jsonl"):
        try:
            st = p.stat()
            out[p.name] = (st.st_size, st.st_mtime)
        except OSError:
            pass
    return out


def log(msg):
    line = f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {msg}"
    print(line, flush=True)
    try:
        with LOG.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
    except OSError:
        pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--minutes", type=int, default=90, help="最多等多久（分钟）")
    args = ap.parse_args()

    base = snapshot()
    base_max_mtime = max((v[1] for v in base.values()), default=0)
    log(f"armed: {len(base)} 个 rollout 文件, 基线 max_mtime={datetime.fromtimestamp(base_max_mtime):%H:%M:%S}")
    STATE.write_text(json.dumps({
        "state": "armed",
        "baseline_files": len(base),
        "baseline_epoch": base_max_mtime,
        "armed_at": datetime.now().isoformat(timespec="seconds"),
    }, ensure_ascii=False, indent=1), encoding="utf-8")

    deadline = time.time() + args.minutes * 60
    while time.time() < deadline:
        time.sleep(POLL_SEC)
        cur = snapshot()
        cur_max = max((v[1] for v in cur.values()), default=0)
        # 判定：出现了基线里没有的新文件，或任何文件 mtime 越过基线
        new_files = set(cur) - set(base)
        grew = cur_max > base_max_mtime + 5
        if new_files or grew:
            why = []
            if new_files:
                why.append(f"新文件 {len(new_files)} 个")
            if grew:
                why.append(f"mtime +{cur_max - base_max_mtime:.0f}s")
            log(f"检测到 GLM 开始写（{' / '.join(why)}）→ 拉起 glm_watch.py")
            STATE.write_text(json.dumps({
                "state": "launched",
                "trigger": " / ".join(why),
                "at": datetime.now().isoformat(timespec="seconds"),
            }, ensure_ascii=False, indent=1), encoding="utf-8")
            try:
                subprocess.Popen(
                    [sys.executable, str(HERE / "glm_watch.py")],
                    cwd=str(HERE),
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=getattr(subprocess, "DETACHED_PROCESS", 0),
                )
                log("glm_watch.py 已拉起（detached）")
            except Exception as e:
                log(f"拉起失败: {e}")
            return 0

    log(f"等了 {args.minutes} 分钟 GLM 仍无动静，退出（未拉起监控）")
    STATE.write_text(json.dumps({
        "state": "timeout",
        "at": datetime.now().isoformat(timespec="seconds"),
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    return 2


if __name__ == "__main__":
    sys.exit(main())
