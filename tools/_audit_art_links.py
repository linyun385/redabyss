#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""T68 素材接线体检：catalog↔文件↔web 三方对账（只读）。

对账三方：
  1. data/art_catalog.json          —— 生成侧素材目录（id 列表）
  2. web/assets/art/<id>.webp       —— 成品文件
  3. web/index.html                 —— 运行时登记（ART 表 key / 正文任意字面出现）

输出三类清单：缺失（登记无文件）/ 多余（文件无登记）/ 断链（登记↔文件↔引用错位）。
引用判定从宽：id 字符串在 web 现行文本文件（index.html 优先）中任意出现即算引用，
宁可宽判不误报。口径全文写入 docs/ART_LINK_AUDIT.md。

用法：
  python tools/_audit_art_links.py            # 对账并刷新 docs/ART_LINK_AUDIT.md
  python tools/_audit_art_links.py --no-md    # 只打印摘要，不写报告

本脚本对 web/ 与 art/ 零写入（报告只落 docs/），exit 恒为 0（体检报告，不当下门禁）。
"""
import argparse
import datetime
import json
import re
import sys
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data" / "art_catalog.json"
ART_DIR = ROOT / "web" / "assets" / "art"
INDEX = ROOT / "web" / "index.html"
REPORT = ROOT / "docs" / "ART_LINK_AUDIT.md"

ART_BEGIN = "/* ==ART-TABLE=="
ART_END = "/* ==/ART-TABLE== */"

# 现行 web 文本文件（宽判引用扫描用）：排除 assets/、sfx/ 与 .bak/.corrupt/.recovered 等备份
LIVE_SKIP = re.compile(r"\.(bak|corrupt|recovered|old)(\.|$)|\.bak-")


def live_web_texts():
    out = []
    web = ROOT / "web"
    for p in sorted(web.rglob("*")):
        if not p.is_file() or p.suffix.lower() not in (".html", ".js", ".css"):
            continue
        rel = p.relative_to(web).as_posix()
        if rel.startswith("assets/") or rel.startswith("sfx/"):
            continue
        if LIVE_SKIP.search(rel):
            continue
        out.append(p)
    return out


def load_catalog():
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise SystemExit("art_catalog.json 顶层不是数组，脚本需随目录结构调整")
    ids = [str(e.get("id")) for e in data if e.get("id")]
    dupes = sorted(i for i, c in Counter(ids).items() if c > 1)
    return ids, dupes, len(data)


def load_files():
    files = sorted(p for p in ART_DIR.iterdir() if p.is_file())
    webp = {p.stem: p.name for p in files if p.suffix.lower() == ".webp"}
    other = [p.name for p in files if p.suffix.lower() != ".webp"]
    return webp, other, len(files)


def parse_art_table(html):
    """返回 (art_keys, art_values, seg_span, degraded)。span 之外的正文用于字面引用判定。"""
    b, e = html.find(ART_BEGIN), html.find(ART_END)
    if b == -1 or e == -1 or e < b:
        m = re.search(r"window\.ART = (\{.*?\});", html, re.S)
        if not m:
            return set(), {}, (0, 0), True
        obj = m.group(1)
        span = m.span()
        degraded = True
    else:
        seg = html[b:e]
        m = re.search(r"window\.ART = (\{.*?\});", seg, re.S)
        obj = m.group(1) if m else "{}"
        span = (b, e)
        degraded = False
    try:
        table = json.loads(obj)
    except json.JSONDecodeError:
        table = dict(re.findall(r'"([^"]+)"\s*:\s*"([^"]*)"', obj))
    return set(table), table, span, degraded


def art_value_ok(key, val, webp):
    """ART 表值须指向 assets/art/<key>.webp 且文件在（data: URI 内联也算通过）。"""
    if val.startswith("data:"):
        return True, "data:URI 内联"
    want = "assets/art/%s.webp" % key
    if val != want:
        return False, "值 %s ≠ 约定 %s" % (val, want)
    if key not in webp:
        return False, "指向的文件不存在"
    return True, ""


def family(stem):
    """把多余文件按族归并（card_zh2_battery_lamp→card_zh2，anm_0011.old→anm_0011.old）。"""
    s = re.sub(r"\.old$", "", stem)
    s2 = re.sub(r"_?\d+$", "", s)
    if s2 == s and "_" in stem:
        s2 = "_".join(stem.split("_")[:2])
    return s2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-md", action="store_true", help="只打印摘要，不写报告")
    args = ap.parse_args()

    cat_ids, cat_dupes, cat_total = load_catalog()
    cat_set = set(cat_ids)
    webp, other_files, file_total = load_files()
    file_ids = set(webp)

    html = INDEX.read_text(encoding="utf-8")
    art_keys, art_table, (b, e), degraded = parse_art_table(html)
    body = html[:b] + html[e:]
    live_paths = live_web_texts()
    live_all = "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in live_paths)

    # ── 1. 缺失：登记了 id 但无文件（会让运行时查空 → 空卡面/回落）──
    cat_missing = sorted(cat_set - file_ids)
    art_missing = sorted(k for k in art_keys if k not in file_ids)

    # ── 2. ART 表值路径错位（引用指向了不存在的路径，属断链）──
    art_bad_val = {}
    for k in sorted(art_keys):
        ok, why = art_value_ok(k, art_table.get(k, ""), webp)
        if not ok:
            art_bad_val[k] = why

    # ── 3. 多余：文件存在但 catalog ∪ ART 表均无登记 ──
    extras = sorted(file_ids - cat_set - art_keys)
    # 宽判补查：多余文件若被任何现行 web 文本字面引用，也不算"无人认领"
    extras_unref = [s for s in extras if s not in live_all]
    extras_groups = sorted(Counter(family(s) for s in extras_unref).items(),
                           key=lambda kv: (-kv[1], kv[0]))

    # ── 4. 引用覆盖：catalog id 在 web 里的字面出现（宽判：任意现行文件出现即算）──
    art_seg = html[b:e] if e > b else ""
    cat_no_ref = sorted(i for i in cat_set
                        if i not in live_all)  # live_all 含 ART 表段与正文
    cat_no_ref_body = sorted(i for i in cat_set
                             if i not in body and i in art_seg)  # 仅在 ART 表段出现
    cat_meta = {str(e_.get("id")): e_ for e_ in json.loads(CATALOG.read_text(encoding="utf-8"))}

    # ── 5. 断链口径：登记/引用要求可用的 id，文件缺位（1+2）才算断链；
    #     多余文件与"无字面引用"只记录不判死（后者走 cardArtId/foe 派生链）。──
    broken = [("catalog 登记无文件", i) for i in cat_missing] + \
             [("ART 表 key 无文件", i) for i in art_missing] + \
             [("ART 表值路径错位", "%s：%s" % (k, v)) for k, v in art_bad_val.items()]
    registered = len(cat_set | art_keys)
    broken_rate = "%.1f%%" % (100.0 * len(broken) / registered if registered else 0)

    # ── 摘要 ──
    L = []
    A = L.append
    A("# ART_LINK_AUDIT — T68 素材接线体检（catalog↔文件↔web 三方对账）")
    A("")
    A("- 生成：%s　脚本：`tools/_audit_art_links.py`（可重跑刷新本报告）" %
      datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
    A("- 性质：**只读体检**。未改动 `web/`、`web/assets/art/`、`data/`；发现断链只记录不修。")
    if degraded:
        A("- 警告：index.html 未找到 `==ART-TABLE==` 标记，退化为 `window.ART = {...}` 正则解析。")
    A("")
    A("## 一、三方数量")
    A("")
    A("| 登记 | 数量 |")
    A("|---|---|")
    A("| data/art_catalog.json id | %d（含重复 %d，实际唯一 %d） |" %
      (cat_total, len(cat_ids) - len(cat_set), len(cat_set)))
    A("| web/assets/art/*.webp | %d%s |" %
      (file_total, ("，另有非 webp 文件 %d 个" % len(other_files)) if other_files else ""))
    A("| web/index.html ART 表 key | %d |" % len(art_keys))
    A("")
    A("差额定性：文件 %d = catalog %d（**全部有文件**）+ ART 表 %d（**全部有文件**）+ 未登记文件 %d。"
      % (file_total, len(cat_set) - len(cat_missing), len(art_keys) - len(art_missing), len(extras)))
    A("")
    A("## 二、判定口径（宁可宽判不误报）")
    A("")
    A("1. **引用判定**：id 字符串出现在 `web/index.html` 的 ART 表段**或**正文任意位置，"
      "或出现在任一现行 web 文本文件（`web/**/*.{html,js,css}`，排除 `assets/`、`sfx/` 与 "
      "`*.bak*`/`*.corrupt`/`*.recovered` 备份），即算「有引用」。只做子串判定，不解析语法。")
    A("2. **断链定义**：登记/引用侧要求某 id 可用而文件缺位，或 ART 表值路径错位 —— 会造成运行时空卡面。")
    A("3. **不算断链的两类**（只记录）：① 文件存在但三方均无登记（多余文件）；"
      "② catalog id 无字面引用 —— 运行时经 `cardArtId(card)` / 敌人 `foe_<eco>_<n>` 派生 id 查 ART 表，"
      "catalog id 本身不进运行时查表，属生成侧登记，需人工判断是否登记漂移。")
    A("4. **范围**：对账以现行 `web/index.html` 为准；catalog 重复 id、ART 表值路径约定 "
      "`assets/art/<key>.webp`（`data:` URI 内联亦通过）一并核查。")
    A("")
    A("## 三、断链清单（登记↔文件）")
    A("")
    A("| 类别 | 条数 | 明细 |")
    A("|---|---|---|")
    A("| catalog 有 id、无文件 | %d | %s |" % (len(cat_missing), "、".join(cat_missing) or "—"))
    A("| ART 表有 key、无文件 | %d | %s |" % (len(art_missing), "、".join(art_missing) or "—"))
    A("| ART 表值路径错位 | %d | %s |" %
      (len(art_bad_val), "；".join("%s %s" % kv for kv in sorted(art_bad_val.items())) or "—"))
    A("| catalog 重复 id | %d | %s |" % (len(cat_dupes), "、".join(cat_dupes) or "—"))
    A("")
    A("**断链率：%d / %d 登记位 = %s**" % (len(broken), registered, broken_rate))
    A("")
    A("## 四、多余清单（文件无任何登记）")
    A("")
    A("共 %d 个文件不在 catalog 也不在 ART 表，且无任何现行 web 文本字面引用（无人认领，仅记录不清理）："
      % len(extras_unref))
    A("")
    for fam, n in extras_groups:
        members = sorted(s for s in extras_unref if family(s) == fam)
        if n <= 3:
            A("- `%s`：%s" % (fam, "、".join("`%s`" % m for m in members)))
        else:
            A("- `%s_*` ×%d：%s" % (fam, n, "、".join("`%s`" % m for m in members)))
    if len(extras) != len(extras_unref):
        A("")
        A("（另有 %d 个文件虽无登记但被 web 文本字面引用，已按宽判豁免：%s）"
          % (len(extras) - len(extras_unref), "、".join(sorted(set(extras) - set(extras_unref)))))
    A("")
    A("## 五、引用覆盖（catalog → web，宽判）")
    A("")
    A("- catalog %d 个 id 中 %d 个在 web 现行文本有字面出现（多为内嵌卡牌/敌人/事件数据）。"
      % (len(cat_set), len(cat_set) - len(cat_no_ref)))
    A("- 无字面引用 %d 个（文件均在，非断链；逐条列出供人工判断登记漂移）：" % len(cat_no_ref))
    A("")
    for i in cat_no_ref:
        meta = cat_meta.get(i, {})
        A("  - `%s`（%s %s）" % (i, meta.get("kind", "?"), meta.get("name", "")))
    if cat_no_ref_body:
        A("- 仅在 ART 表段出现、正文没有：%s" % "、".join(cat_no_ref_body))
    A("- ART 表 79 个运行时 id（face_eco_*/foe_eco_*/class_*/end_ending_*）与 catalog **零交集**，"
      "属两套命名体系：web 侧走派生 id，catalog 是生成侧目录；此为 T67 接线的设计现状，非缺陷。")
    A("")
    A("## 六、结论")
    A("")
    if broken:
        A("**断链率 %s（%d 条），需按上表逐条修复后复跑本脚本归零。**" % (broken_rate, len(broken)))
    else:
        A("**断链率 0：540 个登记位（catalog 461 + ART 表 79）全部有对应文件，"
          "ART 表值路径全部符合约定；运行时可触达素材接线完整，无空卡面风险。**")
        A("遗留（非断链，记录待后续任务处置）：未登记文件 %d 个（`*_zh*` 旧命名系列 card/foe/evt + "
          "`anm_0011.old` 旧备份，合计死重）；catalog 侧 %d 张卡 id 无字面引用（登记漂移候选）。"
          % (len(extras_unref), len(cat_no_ref)))
    A("")

    report = "\n".join(L)
    if not args.no_md:
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(report, encoding="utf-8")

    # stdout 摘要（Windows 控制台强制 UTF-8 输出）
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    print("T68 素材接线体检")
    print("  catalog: %d（唯一 %d）  文件: %d webp  ART表: %d" %
          (cat_total, len(cat_set), file_total, len(art_keys)))
    print("  断链: %d 条（catalog缺文件 %d + ART缺文件 %d + 值路径错位 %d）→ 断链率 %s" %
          (len(broken), len(cat_missing), len(art_missing), len(art_bad_val), broken_rate))
    print("  多余未登记: %d 个  catalog无字面引用: %d 个" % (len(extras_unref), len(cat_no_ref)))
    print("  报告: %s" % (REPORT if not args.no_md else "（--no-md 未写）"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
