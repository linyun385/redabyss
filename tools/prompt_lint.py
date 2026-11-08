# -*- coding: utf-8 -*-
"""prompt_lint.py — 提示词合规扫描（T243）。

用途：
    扫 data/zh_prompts_full.json，按三张禁用词表逐条报命中，输出 data/lint.json。
    词表来源（任务书说的「规则 VIII/IX/X」落地为实际文档里的三张表）：
      rule=mech      — ART_PROMPT_SPEC §六 机械校验禁词（装置/设备/仪器/…/字）
      rule=appliance — 现代电器/灯具名词（第一轮图质检的主要翻车源）
      rule=species   — ART_PROMPT_SPEC §VIII 现实物种名禁令
      rule=en_bad    — §四 反面清单的英文禁词（symbol/pencil/diagram/text/…）

参数：
    --in PATH     提示词文件（默认 data/zh_prompts_full.json）
    --ids a,b,c   只扫这些 id；缺省全量
    --full        同时扫整条 prompt（缺省只扫主体段=「洞底是一整片深红的光」前半）
    --out PATH    输出（默认 data/lint.json）

产出：
    data/lint.json {"meta","items":[{id,hits:[{rule,word}]}],"summary"}
"""
import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MARKER = "洞底是一整片深红的光"

WORDS = {
    "mech": ["装置", "设备", "仪器", "开关", "仪表", "面板", "屏幕", "机器", "编号", "标签", "刻度", "刻字", "铭文", "字"],
    "appliance": ["灯", "屏", "按钮", "显示", "喇叭", "收音", "天线", "插座", "电线", "电缆", "键盘", "表盘", "配电", "断路", "荧光", "霓虹", "数码"],
    "species": ["蜘蛛", "螃蟹", "蜥蜴", "蜗牛", "蕨", "苔藓", "鳗鱼", "青蛙", "蟾蜍", "螳螂", "甲虫", "水蛭", "珊瑚", "海葵", "藤壶"],
    "en_bad": ["symbol", "emblem", "abstract", "essence", "embodiment", "pencil", "graphite", "charcoal",
               "diagram", "callout", "inset", "multiple views", "study sheet", "text", "letters", "labels",
               "signature", "chart", "annotation"],
}


def main():
    ap = argparse.ArgumentParser(description="提示词合规扫描：逐条报禁用词命中")
    ap.add_argument("--in", dest="src", default=os.path.join(ROOT, "data", "zh_prompts_full.json"))
    ap.add_argument("--ids", default=None)
    ap.add_argument("--full", action="store_true", help="扫整条 prompt 而不是只扫主体段")
    ap.add_argument("--out", default=os.path.join(ROOT, "data", "lint.json"))
    a = ap.parse_args()

    data = json.load(open(a.src, encoding="utf-8"))
    if a.ids:
        want = set(s.strip() for s in a.ids.split(",") if s.strip())
        data = [x for x in data if x["id"] in want]

    items = []
    counter = {}
    for x in data:
        p = x["prompt"]
        seg = p if a.full else (p.split(MARKER, 1)[0] if MARKER in p else p)
        hits = []
        low = seg.lower()
        for rule, words in WORDS.items():
            for w in words:
                if w.isascii():
                    if re.search(r"\b" + re.escape(w) + r"\b", low):
                        hits.append({"rule": rule, "word": w})
                elif w in seg:
                    hits.append({"rule": rule, "word": w})
        for h in hits:
            key = (h["rule"], h["word"])
            counter[key] = counter.get(key, 0) + 1
        if hits:
            items.append({"id": x["id"], "hits": hits})

    summary = [{"rule": r, "word": w, "count": c} for (r, w), c in sorted(counter.items(), key=lambda kv: -kv[1])]
    out = {
        "meta": {
            "tool": "tools/prompt_lint.py",
            "src": os.path.relpath(a.src, ROOT),
            "scope": "full" if a.full else "主体段（洞底是一整片深红的光 之前）",
            "scanned": len(data),
            "flagged": len(items),
            "wordlists": "mech=SPEC§六禁词; appliance=电器名词; species=SPEC§VIII物种名; en_bad=SPEC§四英文禁词",
        },
        "items": items,
        "summary": summary,
    }
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("lint: 扫 %d 条，命中 %d 条，词项 %d 个 → %s" % (len(data), len(items), len(summary), os.path.relpath(a.out, ROOT)))


if __name__ == "__main__":
    sys.exit(main())
