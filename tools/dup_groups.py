# -*- coding: utf-8 -*-
"""dup_groups.py — 雷同分组与保留/重画建议（T267）。

前置数据（均为既有脚本产物，本脚本只读）：
    data/dups.json        —— tools/dup_finder.py（dHash 8x8, 阈值 0.9）
    data/qa_auto.json     —— tools/art_qa.py（red_ratio / luma / cold_ratio / near_black）
    data/stat_tone.json   —— tools/_tone_stats.py（全池 P50 基线）
    data/rewrite/_targets.json —— rewrite 147 清单

口径（可复算，无随机无时间戳）：
    keep_score(id) = |red_ratio - 全池P50(red_ratio)| + |luma - 全池P50(luma)| + 2*near_black
      —— 越接近全池中位越「有代表性」，越极端越该重画；near_black 双倍权重。
    组内按 keep_score 升序：前 1/3（至少 1 张）为「保留」，含 sim>=0.95 对的最差成员强制进「重画」，
    已在 T335_PRUNE.csv 删卡清单内的成员标「pruned（不投入重画）」。

产出：
    stdout 表格 + data/dup_groups.json
"""
import collections
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(p):
    return json.load(open(os.path.join(ROOT, p), encoding="utf-8"))


def pct(sorted_vals, p):
    if not sorted_vals:
        return 0.0
    k = (len(sorted_vals) - 1) * p
    f, c = int(k), min(int(k) + 1, len(sorted_vals) - 1)
    return sorted_vals[f] + (sorted_vals[c] - sorted_vals[f]) * (k - f)


def main():
    dups = load(os.path.join("data", "dups.json"))
    qa = {x["id"]: x for x in load(os.path.join("data", "qa_auto.json"))["items"]}
    tone = load(os.path.join("data", "stat_tone.json"))
    pool = tone.get("all") or tone.get("pool") or {}
    if not pool:
        # 从 stat_tone 的分段结构兜底：取全部条目重算 P50
        vals = {"red": [], "luma": []}
        for x in qa.values():
            vals["red"].append(x["red_ratio"])
            vals["luma"].append(x["luma"])
        p50 = {"red": pct(sorted(vals["red"]), 0.5), "luma": pct(sorted(vals["luma"]), 0.5)}
    else:
        p50 = {"red": pool.get("red_ratio", {}).get("P50", 0.35), "luma": pool.get("luma", {}).get("P50", 60)}

    prune_ids = set()
    pcsv = os.path.join(ROOT, "docs", "design", "stream", "T335_PRUNE.csv")
    if os.path.exists(pcsv):
        import csv
        with open(pcsv, encoding="utf-8-sig") as fh:
            prune_ids = {r["id"] for r in csv.DictReader(fh)}
    rw_ids = set(load(os.path.join("data", "rewrite", "_targets.json"))["targets"])

    def score(i):
        q = qa[i]
        return (abs(q["red_ratio"] - p50["red"]) + abs(q["luma"] - p50["luma"])
                + (2.0 if q.get("near_black") else 0.0))

    hot_pairs = [p for p in dups["pairs"] if p["sim"] >= 0.95]
    out = {"meta": {"threshold": dups["meta"]["threshold"], "pairs": len(dups["pairs"]),
                    "groups": len(dups["groups"]), "p50": p50,
                    "hot_pairs_ge_095": len(hot_pairs)}, "groups": []}

    for gi, members in enumerate(dups["groups"], 1):
        ranked = sorted(members, key=score)
        keep_n = max(1, (len(members) + 2) // 3)
        keep, rest = ranked[:keep_n], ranked[keep_n:]
        redo_forced = {x["a"] for x in hot_pairs if x["a"] in members} | \
                      {x["b"] for x in hot_pairs if x["b"] in members}
        rows = []
        for i in members:
            tag = "keep" if i in keep else ("redo" if (i in redo_forced or len(members) <= 2) else "review")
            if i in prune_ids:
                tag = "pruned"
            rows.append({"id": i, "score": round(score(i), 4), "tag": tag,
                         "red_ratio": qa[i]["red_ratio"], "luma": qa[i]["luma"],
                         "near_black": qa[i].get("near_black", False),
                         "in_rewrite": i in rw_ids})
        out["groups"].append({"group": gi, "size": len(members), "rows": rows})

    json.dump(out, open(os.path.join(ROOT, "data", "dup_groups.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    print("雷同分组（dHash 阈值 %.2f，%d 对，%d 组；全池 P50 red=%.3f luma=%.1f）"
          % (dups["meta"]["threshold"], len(dups["pairs"]), len(dups["groups"]), p50["red"], p50["luma"]))
    for g in out["groups"]:
        keep = [r["id"] for r in g["rows"] if r["tag"] == "keep"]
        redo = [r["id"] for r in g["rows"] if r["tag"] == "redo"]
        pruned = [r["id"] for r in g["rows"] if r["tag"] == "pruned"]
        review = [r["id"] for r in g["rows"] if r["tag"] == "review"]
        print("组%d（%d 张）keep=%d redo=%d review=%d pruned=%d" %
              (g["group"], g["size"], len(keep), len(redo), len(review), len(pruned)))
        print("   keep  :", "、".join(keep[:6]) + ("…" if len(keep) > 6 else ""))
        print("   redo  :", "、".join(redo[:6]) + ("…" if len(redo) > 6 else ""))
        print("   review:", "、".join(review[:6]) + ("…" if len(review) > 6 else ""))
        if pruned:
            print("   pruned:", "、".join(pruned[:6]) + ("…" if len(pruned) > 6 else ""))
    print("-> data/dup_groups.json")


if __name__ == "__main__":
    main()
