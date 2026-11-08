# -*- coding: utf-8 -*-
"""rule_coverage.py — 规则 VIII/IX/X 覆盖率统计（T270）。

前置（先生成两份 lint 数据）：
    python tools/prompt_lint.py                                   # 主体段口径 -> data/lint.json
    python tools/prompt_lint.py --full --out data/lint_full_prompts.json

本脚本：
    读 data/lint.json + data/rewrite/_targets.json + data/zh_prompts_full.json，
    打印按规则 / 按职业前缀的覆盖率表，写 data/rule_coverage.json。
    同样的输入跑两遍，输出逐字节一致（无时间戳、无随机）。

口径：
    覆盖率 = 主体段 0 命中的提示词占比（即「合规率」）。
    规则名沿用 tools/prompt_lint.py 的词表键：
      species=SPEC§VIII 现实物种禁令；appliance=规则IX 电器名词；
      mech=SPEC§六 机械校验禁词（任务书口径的规则 X 事件牌/纸/设备同族）；en_bad=§四英文禁词。
"""
import collections
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RULES = ["species", "appliance", "mech", "en_bad"]
RULE_CN = {"species": "VIII 去物种", "appliance": "IX 去电器", "mech": "X/§六 机械禁词", "en_bad": "§四英文禁词"}


def load(p):
    return json.load(open(os.path.join(ROOT, p), encoding="utf-8"))


def main():
    lint = load(os.path.join("data", "lint.json"))
    full = load(os.path.join("data", "lint_full_prompts.json"))
    prompts = load(os.path.join("data", "zh_prompts_full.json"))
    targets = load(os.path.join("data", "rewrite", "_targets.json"))
    rw_ids = set(targets["targets"]) if isinstance(targets, dict) else set(targets)

    n = lint["meta"]["scanned"]
    prefix_total = collections.Counter(
        re.match(r"([a-z]+)_", x["id"]).group(1) for x in prompts
    )

    def digest(lintdoc):
        hit_ids = collections.defaultdict(set)
        words = collections.defaultdict(collections.Counter)
        for it in lintdoc["items"]:
            for h in it.get("hits", []):
                hit_ids[h["rule"]].add(it["id"])
                words[h["rule"]][h["word"]] += 1
        return hit_ids, words

    hit1, w1 = digest(lint)
    hit2, _ = digest(full)

    out = {"meta": {"scanned": n, "rewrite_targets": len(rw_ids),
                    "lint_scope": lint["meta"].get("scope", "")},
           "by_rule": {}, "by_prefix": {}}
    for r in RULES:
        ids1 = hit1.get(r, set())
        out["by_rule"][r] = {
            "name_cn": RULE_CN[r],
            "word_hits": sum(w1[r].values()),
            "prompt_hits": len(ids1),
            "coverage_pct": round(100 * (n - len(ids1)) / n, 1),
            "top_words": dict(w1[r].most_common(8)),
            "covered_by_rewrite": len(ids1 & rw_ids),
            "not_in_rewrite": sorted(ids1 - rw_ids),
        }

    hit_prefix = collections.defaultdict(set)
    for it in lint["items"]:
        hit_prefix[re.match(r"([a-z]+)_", it["id"]).group(1)].add(it["id"])
    for p, tot in sorted(prefix_total.items()):
        h = hit_prefix.get(p, set())
        row = {"total": tot, "hit": len(h), "coverage_pct": round(100 * (tot - len(h)) / tot, 1)}
        for r in RULES:
            row[r] = len({i for i in hit1.get(r, set()) if i.startswith(p + "_")})
        out["by_prefix"][p] = row

    json.dump(out, open(os.path.join(ROOT, "data", "rule_coverage.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    print("规则 VIII/IX/X 覆盖率（口径：主体段 0 命中 = 合规；扫 %d 条）" % n)
    print("| 规则 | 词项命中 | 命中条数 | 覆盖率 | rewrite 清单覆盖 |")
    print("|---|---|---|---|---|")
    for r in RULES:
        d = out["by_rule"][r]
        print("| %s（%s） | %d | %d | %.1f%% | %d/%d |"
              % (RULE_CN[r], r, d["word_hits"], d["prompt_hits"],
                 d["coverage_pct"], d["covered_by_rewrite"], d["prompt_hits"]))
    print()
    print("| 池 | 总量 | 命中条数 | 覆盖率 | species | appliance | mech |")
    print("|---|---|---|---|---|---|---|")
    for p, row in out["by_prefix"].items():
        print("| %s | %d | %d | %.1f%% | %d | %d | %d |"
              % (p, row["total"], row["hit"], row["coverage_pct"],
                 row["species"], row["appliance"], row["mech"]))
    print("\n-> data/rule_coverage.json")


if __name__ == "__main__":
    main()
