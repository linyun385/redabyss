# -*- coding: utf-8 -*-
"""dup_finder.py — 图雷同检测（T248）。

用途：
    对 461 张图算感知哈希（dHash 8×8），两两比较汉明距离，
    相似度 > 阈值（默认 0.9）的组输出到 data/dups.json。

参数：
    --dir PATH       图片目录（默认 web/assets/art）
    --threshold F    相似度阈值（默认 0.9，1-距离/64）
    --out PATH       输出（默认 data/dups.json）

产出：
    data/dups.json {"meta","groups":[[id,...]],"pairs":[{a,b,sim}], "hist": {...}}
    （无雷同时 groups/pairs 为空数组，meta/hist 仍为真实数字）
"""
import argparse
import json
import os
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def dhash(im):
    im = im.convert("L").resize((9, 8))
    px = list(im.getdata())
    bits = 0
    for row in range(8):
        for col in range(8):
            bits = (bits << 1) | (1 if px[row * 9 + col] > px[row * 9 + col + 1] else 0)
    return bits


def main():
    ap = argparse.ArgumentParser(description="感知哈希找雷同图（相似度>阈值成组）")
    ap.add_argument("--dir", default=os.path.join(ROOT, "web", "assets", "art"))
    ap.add_argument("--threshold", type=float, default=0.9)
    ap.add_argument("--out", default=os.path.join(ROOT, "data", "dups.json"))
    a = ap.parse_args()

    from PIL import Image

    cat = json.load(open(os.path.join(ROOT, "data", "art_catalog.json"), encoding="utf-8"))
    ids = [c["id"] for c in cat]
    hashes = {}
    for i in ids:
        p = os.path.join(a.dir, i + ".webp")
        if os.path.exists(p):
            hashes[i] = dhash(Image.open(p))
    keys = list(hashes.keys())
    pairs = []
    hist = Counter()
    for x in range(len(keys)):
        h1 = hashes[keys[x]]
        for y in range(x + 1, len(keys)):
            d = bin(h1 ^ hashes[keys[y]]).count("1")
            sim = 1 - d / 64.0
            hist[round(sim, 1)] += 1
            if sim > a.threshold:
                pairs.append({"a": keys[x], "b": keys[y], "sim": round(sim, 3)})

    # 并查集成组
    parent = {k: k for k in keys}
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for pr in pairs:
        ra, rb = find(pr["a"]), find(pr["b"])
        if ra != rb:
            parent[ra] = rb
    groups = {}
    for k in keys:
        groups.setdefault(find(k), []).append(k)
    group_list = sorted([sorted(v) for v in groups.values() if len(v) > 1], key=len, reverse=True)

    out = {
        "meta": {
            "tool": "tools/dup_finder.py",
            "hash": "dHash 8x8 (64bit)",
            "threshold": a.threshold,
            "count": len(keys),
            "pairs_over_threshold": len(pairs),
            "note": "相似度=1-汉明距离/64；hist 键为相似度一位小数分桶",
        },
        "groups": group_list,
        "pairs": pairs,
        "hist": {str(k): v for k, v in sorted(hist.items(), reverse=True)},
    }
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("dups: %d 张两两比对，>%0.2f 的对 %d 个、组 %d 个 → %s" % (
        len(keys), a.threshold, len(pairs), len(group_list), os.path.relpath(a.out, ROOT)))


if __name__ == "__main__":
    sys.exit(main())
