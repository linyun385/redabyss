# -*- coding: utf-8 -*-
"""art_qa.py — 批量图质检器（T242）。

用途：
    对 web/assets/art/ 下的成图逐张算数字：尺寸 / 红占比 / 亮度 / 冷色占比 / 是否近黑。
    只出数字不做判断（判断由 QA_*.md 人/模型复核完成）。

参数：
    --dir PATH    图片目录（默认 web/assets/art）
    --ids a,b,c   只算这些 id（不带 .webp）；缺省=art_catalog.json 全量
    --out PATH    输出 json（默认 data/qa_auto.json）

产出：
    data/qa_auto.json  {"meta": {...}, "items": [{id,size,red_ratio,luma,cold_ratio,near_black}]}
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    ap = argparse.ArgumentParser(description="批量图质检器：只算数字不做判断")
    ap.add_argument("--dir", default=os.path.join(ROOT, "web", "assets", "art"))
    ap.add_argument("--ids", default=None, help="逗号分隔的 id 列表；缺省=catalog 全量")
    ap.add_argument("--out", default=os.path.join(ROOT, "data", "qa_auto.json"))
    a = ap.parse_args()

    from PIL import Image

    if a.ids:
        ids = [s.strip() for s in a.ids.split(",") if s.strip()]
    else:
        cat = json.load(open(os.path.join(ROOT, "data", "art_catalog.json"), encoding="utf-8"))
        ids = [c["id"] for c in cat]

    items = []
    missing = []
    for i in ids:
        p = os.path.join(a.dir, i + ".webp")
        if not os.path.exists(p):
            missing.append(i)
            continue
        im = Image.open(p).convert("RGB")
        im.thumbnail((256, 256))  # 降采样足够出统计数字
        px = list(im.getdata())
        n = len(px)
        red = cold = dark = 0
        luma_sum = 0
        for r, g, b in px:
            luma_sum += 0.2126 * r + 0.7152 * g + 0.0722 * b
            if r > 60 and r >= g * 1.4 and r >= b * 1.4:
                red += 1
            if b > r * 1.15 or (g > r * 1.25 and b >= r):
                cold += 1
            if r + g + b < 45:
                dark += 1
        luma = luma_sum / n
        items.append({
            "id": i,
            "size": list(Image.open(p).size),
            "red_ratio": round(red / n, 4),
            "luma": round(luma, 2),
            "cold_ratio": round(cold / n, 4),
            "near_black": bool(luma < 28 and red / n < 0.05),
        })

    out = {
        "meta": {
            "tool": "tools/art_qa.py",
            "dir": os.path.relpath(a.dir, ROOT),
            "count": len(items),
            "missing": missing,
            "note": "红占比=r≥60且 r≥1.4g 且 r≥1.4b 的像素占比；冷色=b≥1.15r 或 (g≥1.25r 且 b≥r)；near_black=luma<28 且红占比<0.05（256px 降采样统计）",
        },
        "items": items,
    }
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    nb = sum(1 for x in items if x["near_black"])
    print("qa_auto: %d 张已算（缺 %d）→ %s；near_black=%d" % (len(items), len(missing), os.path.relpath(a.out, ROOT), nb))


if __name__ == "__main__":
    sys.exit(main())
