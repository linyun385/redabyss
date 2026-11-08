# -*- coding: utf-8 -*-
"""motif_tag.py — 提示词母题标签（T268）。

对 data/zh_prompts_full.json 的每条 prompt（主体段 = MARKER 前半）打构图母题标签：
    吊挂 / 半埋 / 斜靠 / 散落 / 链挂（多命中全记，primary 按优先级取最具体者）
    链挂 > 吊挂 > 半埋 > 斜靠 > 散落；全不命中 = none。

产出：data/motifs.json {"meta","items":[{id,motifs,primary}],"summary"}
无时间戳无随机，同输入两次运行逐字节一致。
"""
import collections
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MARKER = "洞底是一整片深红的光"

MOTIFS = {
    "链挂": ["铁链", "链条", "吊链", "锁链", "链子", "缆绳吊", "钢缆吊"],
    "吊挂": ["悬挂", "吊在", "吊挂", "吊着", "挂在横梁", "悬在半空", "悬在", "倒吊"],
    "半埋": ["半埋", "埋在", "嵌在岩", "嵌进", "沉在", "陷在", "卡在岩"],
    "斜靠": ["斜靠", "倚在", "斜插", "横卧", "侧躺", "搁在", "斜搁"],
    "散落": ["散落", "散在", "散着", "摊开", "堆积", "落满"],
}
PRIORITY = ["链挂", "吊挂", "半埋", "斜靠", "散落"]


def main():
    data = json.load(open(os.path.join(ROOT, "data", "zh_prompts_full.json"), encoding="utf-8"))
    items, summary = [], collections.Counter()
    primary_c = collections.Counter()
    for x in data:
        seg = x["prompt"].split(MARKER, 1)[0] if MARKER in x["prompt"] else x["prompt"]
        motifs = [m for m in PRIORITY if any(w in seg for w in MOTIFS[m])]
        primary = motifs[0] if motifs else "none"
        summary["primary:" + primary] += 1
        for m in motifs:
            summary["tagged:" + m] += 1
        if not motifs:
            summary["none"] += 1
        items.append({"id": x["id"], "motifs": motifs, "primary": primary})
    total = len(items)
    none_n = summary["none"]
    out = {
        "meta": {"total": total, "scope": "主体段（MARKER 前半）", "priority": PRIORITY,
                 "words": MOTIFS},
        "summary": {
            "primary_counts": {p: summary["primary:" + p] for p in PRIORITY + ["none"]},
            "tagged_counts": {p: summary["tagged:" + p] for p in PRIORITY},
            "multi_tag": sum(1 for i in items if len(i["motifs"]) > 1),
            "coverage_pct": round(100 * (total - none_n) / total, 1),
        },
        "items": items,
    }
    json.dump(out, open(os.path.join(ROOT, "data", "motifs.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    print("母题标签（扫 %d 条，覆盖率 %.1f%%，多母题 %d 条）"
          % (total, out["summary"]["coverage_pct"], out["summary"]["multi_tag"]))
    print("| 母题 | 作为主母题 | 被标记 |")
    print("|---|---|---|")
    for p in PRIORITY:
        print("| %s | %d | %d |" % (p, out["summary"]["primary_counts"][p], out["summary"]["tagged_counts"][p]))
    print("| none | %d | — |" % none_n)
    print("-> data/motifs.json")


if __name__ == "__main__":
    main()
