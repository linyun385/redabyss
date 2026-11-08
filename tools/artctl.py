# -*- coding: utf-8 -*-
"""artctl.py — 素材流水线编排入口（T245）。

用途：
    把既有的四个环节串成一个入口，只做编排不改逻辑：
      families → build_families.py（族表）
      jobs     → _make_jobs.py（出图任务）        [或 --night 用 job_builder.py 的 jobs_night]
      gen      → wanx_gen.py（调万相/远端生图）    [GPU 本地链路请用 tools/gen_art_diffusers.py，不在本入口内]
      sync     → art_sync.py（把产物同步进 web/assets/art）

参数（子命令式）：
    python tools/artctl.py families [原脚本参数...]
    python tools/artctl.py jobs     [--night] [原脚本参数...]
    python tools/artctl.py gen      [原脚本参数...]
    python tools/artctl.py sync     [原脚本参数...]
    python tools/artctl.py plan                 # 只打印将执行的命令，不真跑（默认干跑）
    通用：--run 真执行；--help 见各子脚本自身

产出：
    由各子脚本决定（data/families.json、data/jobs_*.json、art 产物、web/assets/art 同步）。
    本脚本自己只写 data/artctl_last_run.json（每次执行的命令与退出码）。
"""
import argparse
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable or "python"

STEPS = {
    "families": ["tools", "build_families.py"],
    "jobs": ["tools", "_make_jobs.py"],
    "gen": ["tools", "wanx_gen.py"],
    "sync": ["tools", "art_sync.py"],
}


def main():
    ap = argparse.ArgumentParser(description="素材流水线编排入口（families→jobs→gen→sync）")
    ap.add_argument("step", choices=list(STEPS) + ["plan"], help="要跑的环节；plan=打印四步命令")
    ap.add_argument("--night", action="store_true", help="jobs 环节改用 tools/job_builder.py（夜班清单）")
    ap.add_argument("--run", action="store_true", help="真执行（缺省=干跑，只打印命令）")
    ap.add_argument("passthru", nargs="*", help="透传给子脚本的参数")
    a = ap.parse_args()

    plan = []
    if a.step == "plan":
        for name in ("families", "jobs", "gen", "sync"):
            script = "job_builder.py" if (name == "jobs" and a.night) else STEPS[name][1]
            plan.append([PY, "-I", os.path.join(ROOT, "tools", script)] + a.passthru)
        for cmd in plan:
            print(" ".join(cmd))
        print("（干跑：加 --run 真执行）")
        return 0

    script = "job_builder.py" if (a.step == "jobs" and a.night) else STEPS[a.step][1]
    cmd = [PY, "-I", os.path.join(ROOT, "tools", script)] + a.passthru
    print(" ".join(cmd))
    if not a.run:
        print("（干跑：加 --run 真执行）")
        return 0

    t0 = time.time()
    proc = subprocess.run(cmd, cwd=ROOT)
    rec = {
        "step": a.step,
        "script": script,
        "cmd": cmd,
        "exit": proc.returncode,
        "seconds": round(time.time() - t0, 1),
    }
    out = os.path.join(ROOT, "data", "artctl_last_run.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(rec, f, ensure_ascii=False, indent=1)
    print("artctl: step=%s exit=%d (%.1fs) → %s" % (a.step, proc.returncode, rec["seconds"], os.path.relpath(out, ROOT)))
    return proc.returncode


if __name__ == "__main__":
    sys.exit(main())
