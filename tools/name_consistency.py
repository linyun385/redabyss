# -*- coding: utf-8 -*-
"""name_consistency.py — 术语一致性自动检查（D12/R3-D12）。

用法：
    python tools/name_consistency.py

从 GLOSSARY.md 提取正名列表，扫描 docs/ 下全部 md，
报告每个正名的别名出现次数。输出 data/name_consistency.json。
"""
import json, os, re, sys, collections

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 正名 → 别名列表（从 D12 glossary_check.md 的冲突清单硬编码）
NAMES = {
    "共振": ["共鸣", "resonance"],
    "凝视": ["gaze", "被看的痕迹"],
    "维护者": ["黯民", "anmin"],
    "苍民": ["疯先知", "cangmin"],
    "震语者": ["深渊震语者", "tremor"],
    "通用牌": ["无色牌", "shared 卡", "shared牌"],
    "下潜者": ["diver"],
    "层": ["band", "深度带"],
}

def main():
    glossary = open(os.path.join(ROOT, "docs", "GLOSSARY.md"), encoding="utf-8").read()
    md_files = []
    for dirpath, _, filenames in os.walk(os.path.join(ROOT, "docs")):
        for fn in filenames:
            if fn.endswith(".md") and not fn.startswith("_"):
                md_files.append(os.path.join(dirpath, fn))

    results = []
    for name, aliases in NAMES.items():
        for alias in aliases:
            count = 0
            files = []
            for mf in md_files:
                txt = open(mf, encoding="utf-8", errors="replace").read()
                c = txt.count(alias)
                if c > 0:
                    count += c
                    files.append(os.path.relpath(mf, ROOT))
            if count > 0:
                results.append({"正名": name, "别名": alias, "出现次数": count,
                               "文件": files[:8]})
    results.sort(key=lambda x: -x["出现次数"])

    out = {"meta": {"scanned": len(md_files), "names": len(NAMES)}, "items": results}
    json.dump(out, open(os.path.join(ROOT, "data", "name_consistency.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    print("术语一致性检查（扫 %d 个 md，%d 个正名）" % (len(md_files), len(NAMES)))
    print("| 正名 | 别名 | 出现次数 | 文件数 |")
    print("|---|---|---|---|")
    for r in results:
        print("| %s | %s | %d | %d |" % (r["正名"], r["别名"], r["出现次数"], len(r["文件"])))
    print("-> data/name_consistency.json")

if __name__ == "__main__":
    main()
