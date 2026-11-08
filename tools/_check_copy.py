# -*- coding: utf-8 -*-
"""_check_copy.py — 校验 data/copy/card_*.md / foe_*.md / evt_*.md。
用法: python -I tools/_check_copy.py [card|foe|evt] [组号...]
"""
import json, re, sys, io, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def main():
    kind = sys.argv[1] if len(sys.argv) > 1 else "all"
    only = set(int(a) for a in sys.argv[2:]) if len(sys.argv) > 2 else None
    tj = json.load(open(os.path.join(ROOT, "data", "copy", "_targets.json"), encoding="utf-8"))
    cat = {c["id"]: c for c in json.load(open(os.path.join(ROOT, "data", "art_catalog.json"), encoding="utf-8"))}
    fails = []
    total = 0
    specs = []
    if kind in ("all", "card"):
        specs += [("card", tj["cards"], 20, 35, "card_%03d.md")]
    if kind in ("all", "foe"):
        specs += [("foe", tj["foes"], 20, 30, "foe_%03d.md")]
    if kind in ("all", "evt"):
        specs += [("evt", tj["evts"], 25, 40, "evt_%03d.md")]
    for k, ids, lo, hi, pat in specs:
        groups = [ids[i:i + 20] for i in range(0, len(ids), 20)]
        for gi, gids in enumerate(groups, 1):
            if only and gi not in only:
                continue
            path = os.path.join(ROOT, "data", "copy", pat % gi)
            if not os.path.exists(path):
                fails.append("%s %03d: 文件缺失" % (k, gi))
                continue
            lines = [l.rstrip() for l in open(path, encoding="utf-8").read().splitlines() if l.strip()]
            if len(lines) != len(gids):
                fails.append("%s %03d: 行数 %d != %d" % (k, gi, len(lines), len(gids)))
                continue
            for idx, (line, cid) in enumerate(zip(lines, gids)):
                parts = line.split("|", 1)
                if len(parts) != 2 or parts[0].strip() != cid:
                    fails.append("%s %03d 第%d行: id 不符「%s」应 %s" % (k, gi, idx + 1, line[:30], cid))
                    continue
                txt = parts[1].strip()
                n = len(re.sub(r"\s", "", txt))
                total += 1
                if not (lo <= n <= hi + 3):
                    fails.append("%s %03d %s: 长度 %d 不在 %d–%d(+3容差)「%s」" % (k, gi, cid, n, lo, hi, txt[:20]))
                if "！" in txt or "!" in txt:
                    fails.append("%s %03d %s: 有感叹号" % (k, gi, cid))
                if ("「" in txt and "」" in txt) or ('"' in txt):
                    fails.append("%s %03d %s: 带引号" % (k, gi, cid))
                d = cat[cid]["desc"]
                if len(re.sub(r"\s", "", d)) >= 8 and re.sub(r"\s", "", d) == re.sub(r"\s", "", txt):
                    fails.append("%s %03d %s: 整句复制 desc" % (k, gi, cid))
    if fails:
        print("FAIL %d 项:" % len(fails))
        for f in fails[:50]:
            print(" -", f)
        sys.exit(1)
    print("全部通过：已核 %d 条，id 与清单一致、长度/引号/感叹号/复制检查全过" % total)

if __name__ == "__main__":
    main()
