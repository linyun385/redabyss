# -*- coding: utf-8 -*-
"""qa_report.py — 汇总图质检报告（T246）。

用途：
    解析 data/qa/QA_*.md（第一轮逐张判定）与 data/qa/RC_*.md（第二轮复检），
    汇总成 data/qa_report.md：不合格数、缺陷分布、按卡组分布、复检结论分布。

参数：
    --qa-dir PATH  质检目录（默认 data/qa）
    --out PATH     输出（默认 data/qa_report.md）

产出：
    data/qa_report.md
"""
import argparse
import glob
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFECTS = ["可读文字", "电器外形", "白画框", "主体偏移", "偏色", "纸书册"]


def _cells(line):
    if not line.startswith("|"):
        return None
    cells = [c.strip() for c in line.split("|")]
    if len(cells) < 4:
        return None
    cid = cells[1] or ""
    if cid == "id" or not re.fullmatch(r"[a-z]+[a-z_0-9]*", cid):
        return None
    return cells


def parse_qa(path):
    fails, rows = [], 0
    for line in open(path, encoding="utf-8"):
        cells = _cells(line)
        if not cells:
            continue
        rows += 1
        sug = cells[-2]
        if sug and sug != "—":
            fails.append((cells[1], sug, cells[2:-2]))
    return rows, fails


def parse_rc(path):
    verdicts = []
    for line in open(path, encoding="utf-8"):
        cells = _cells(line)
        if cells:
            verdicts.append((cells[1], cells[-2]))
    return verdicts


def seg_of(i):
    p = i.split("_")[0]
    return {"enemy": "enemy", "event": "event", "dive": "dive", "trem": "trem", "anm": "anm", "cng": "cng"}.get(p, p)


def main():
    ap = argparse.ArgumentParser(description="汇总 data/qa/*.md 成 qa_report.md")
    ap.add_argument("--qa-dir", default=os.path.join(ROOT, "data", "qa"))
    ap.add_argument("--out", default=os.path.join(ROOT, "data", "qa_report.md"))
    a = ap.parse_args()

    total, fail_all, seg = 0, [], Counter()
    for path in sorted(glob.glob(os.path.join(a.qa_dir, "QA_*.md"))):
        rows, fails = parse_qa(path)
        total += rows
        fail_all += fails
        for i, _, _ in fails:
            seg[seg_of(i)] += 1

    defcol = Counter()
    for _, _, cols in fail_all:
        for k, c in enumerate(cols):
            if c and c != "—":
                defcol[DEFECTS[k] if k < len(DEFECTS) else "其他"] += 1

    rc = Counter()
    rc_total = 0
    for path in sorted(glob.glob(os.path.join(a.qa_dir, "RC_*.md"))):
        for _, v in parse_rc(path):
            rc_total += 1
            rc[v.split("（")[0].strip()] += 1

    L = ["# 图质检汇总报告（qa_report）", "",
         "- 生成：tools/qa_report.py", "",
         "## 第一轮（QA_001–047，逐张 7 项）", "",
         "- 抽检：%d 张" % total,
         "- 不合格：%d 张（%.1f%%）" % (len(fail_all), 100.0 * len(fail_all) / max(total, 1)),
         "- 缺陷分布：" + "、".join("%s %d" % (k, v) for k, v in defcol.most_common()),
         "- 按卡组分布：" + "、".join("%s %d" % (k, v) for k, v in sorted(seg.items())), ""]
    if fail_all:
        L += ["| id | 建议改法 |", "|---|---|"]
        for i, sug, _ in fail_all:
            L.append("| %s | %s |" % (i, sug.replace("|", "/")[:60]))
        L.append("")
    L += ["## 第二轮复检（RC_001–012，材质/厚度/对题）", "",
          "- 复检：%d 张" % rc_total,
          "- 结论分布：" + "、".join("%s %d" % (k, v) for k, v in rc.most_common()), ""]
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write("\n".join(L))
    print("qa_report: 一轮 %d/%d 不合格，二轮 %d 张复检 → %s" % (len(fail_all), total, rc_total, os.path.relpath(a.out, ROOT)))


if __name__ == "__main__":
    sys.exit(main())
