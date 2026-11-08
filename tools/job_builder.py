# -*- coding: utf-8 -*-
"""job_builder.py — 出图任务生成器（T244）。

用途：
    读 data/rewrite/RW_*.json（新主体段）与 data/qa/QA_*.md 里的不合格 id，
    合成可执行的出图任务清单 data/jobs_night.json。
    prompt = 新主体段（有 rewrite 用 rewrite，没有用原主体段）+「洞底是一整片深红的光」+ 原尾部。
    原文件 data/zh_prompts_full.json 只读不写。

参数：
    --rw-dir PATH   rewrite 目录（默认 data/rewrite）
    --out PATH      输出（默认 data/jobs_night.json）
    --limit N       最多生成 N 条（调试用）

产出：
    data/jobs_night.json {"meta","jobs":[{id,fix,prompt,reason}]}
"""
import argparse
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MARKER = "洞底是一整片深红的光"


def qa_failed_ids():
    """从 data/qa/QA_*.md 抽「建议改法」列非 — 的 id（保持文件序）。"""
    failed = []
    for path in sorted(glob.glob(os.path.join(ROOT, "data", "qa", "QA_*.md"))):
        for line in open(path, encoding="utf-8"):
            if not line.startswith("|"):
                continue
            cells = [c.strip() for c in line.split("|")]
            if len(cells) < 4 or not re.fullmatch(r"[a-z]+[a-z_0-9]*", cells[1] or ""):
                continue
            sug = cells[-2]
            if sug and sug != "—" and cells[1] not in failed:
                failed.append(cells[1])
    return failed


def main():
    ap = argparse.ArgumentParser(description="合成出图任务清单 jobs_night.json")
    ap.add_argument("--rw-dir", default=os.path.join(ROOT, "data", "rewrite"))
    ap.add_argument("--out", default=os.path.join(ROOT, "data", "jobs_night.json"))
    ap.add_argument("--limit", type=int, default=None)
    a = ap.parse_args()

    prompts = {x["id"]: x["prompt"] for x in json.load(open(os.path.join(ROOT, "data", "zh_prompts_full.json"), encoding="utf-8"))}

    rewrites = {}
    for path in sorted(glob.glob(os.path.join(a.rw_dir, "RW_*.json"))):
        for x in json.load(open(path, encoding="utf-8")):
            rewrites[x["id"]] = x["prompt"]

    failed = [i for i in qa_failed_ids() if i in prompts]
    ids = list(rewrites.keys()) + [i for i in failed if i not in rewrites]
    if a.limit:
        ids = ids[: a.limit]

    jobs = []
    for i in ids:
        orig = prompts[i]
        if MARKER in orig:
            tail = MARKER + orig.split(MARKER, 1)[1]
        else:
            tail = ""
        front = rewrites.get(i) or orig.split(MARKER, 1)[0]
        jobs.append({
            "id": i,
            "fix": "rewrite" if i in rewrites else "none",
            "prompt": front + tail,
            "reason": "rewrite 主体段" if i in rewrites else "QA 不合格（主体段待重写）",
        })

    out = {
        "meta": {
            "tool": "tools/job_builder.py",
            "rewrite_ids": len(rewrites),
            "qa_failed_ids": len(failed),
            "jobs": len(jobs),
            "note": "prompt=主体段+原尾部；fix=rewrite 表示已带新主体段，fix=none 表示仅 QA 不合格、主体段还没有重写稿",
        },
        "jobs": jobs,
    }
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("jobs: rewrite=%d + qa_only=%d = %d 条 → %s" % (
        len(rewrites), sum(1 for j in jobs if j["fix"] == "none"), len(jobs), os.path.relpath(a.out, ROOT)))


if __name__ == "__main__":
    sys.exit(main())
