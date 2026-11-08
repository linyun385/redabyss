# -*- coding: utf-8 -*-
"""lore_index.py — 图鉴文案索引（T247）。

用途：
    解析 data/lore/LORE_*.md（## <id> <卡名> + 画面/来历/画理 三段），
    汇成 data/lore_index.json，给图鉴界面/检索用。

参数：
    --lore-dir PATH  目录（默认 data/lore）
    --out PATH       输出（默认 data/lore_index.json）

产出：
    data/lore_index.json {"meta","entries":[{id,name,file,chars,画面,来历,画理}]}
"""
import argparse
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    ap = argparse.ArgumentParser(description="汇总 data/lore/*.md 成 lore_index.json")
    ap.add_argument("--lore-dir", default=os.path.join(ROOT, "data", "lore"))
    ap.add_argument("--out", default=os.path.join(ROOT, "data", "lore_index.json"))
    a = ap.parse_args()

    entries = []
    for path in sorted(glob.glob(os.path.join(a.lore_dir, "LORE_*.md"))):
        text = open(path, encoding="utf-8").read()
        for sec in re.split(r"^## ", text, flags=re.M)[1:]:
            head = sec.splitlines()[0].strip()
            m = re.match(r"([a-z]+[a-z_0-9]*)\s+(.+)", head)
            if not m:
                continue
            cid, name = m.group(1), m.group(2)
            body = sec.split("\n", 1)[1] if "\n" in sec else ""
            paras = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
            rec = {"id": cid, "name": name, "file": os.path.basename(path), "chars": 0}
            for p in paras:
                for lab, key in (("画面：", "画面"), ("来历：", "来历"), ("画理：", "画理")):
                    if p.startswith(lab):
                        rec[key] = p[len(lab):].strip().replace("\n", "")
            rec["chars"] = len("".join(re.sub(r"\s", "", rec.get(k, "")) for k in ("画面", "来历", "画理")))
            entries.append(rec)

    out = {
        "meta": {"tool": "tools/lore_index.py", "dir": os.path.relpath(a.lore_dir, ROOT), "count": len(entries)},
        "entries": entries,
    }
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("lore_index: %d 条 → %s" % (len(entries), os.path.relpath(a.out, ROOT)))


if __name__ == "__main__":
    sys.exit(main())
