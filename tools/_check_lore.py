# -*- coding: utf-8 -*-
"""_check_lore.py — 校验 data/lore/LORE_*.md 是否符合 T158–T204 任务书验收。
用法: python -I tools/_check_lore.py [组号...]
"""
import json, re, sys, io, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def main():
    cat = json.load(open(os.path.join(ROOT, "data", "art_catalog.json"), encoding="utf-8"))
    ids = [c["id"] for c in cat]
    names = {c["id"]: c["name"] for c in cat}
    groups = [ids[i:i + 10] for i in range(0, len(ids), 10)]
    only = set(int(a) for a in sys.argv[1:]) if len(sys.argv) > 1 else None
    fails = []
    total = 0
    for gi, gids in enumerate(groups, 1):
        if only and gi not in only:
            continue
        path = os.path.join(ROOT, "data", "lore", "LORE_%03d.md" % gi)
        if not os.path.exists(path):
            fails.append("LORE_%03d: 文件缺失" % gi)
            continue
        text = open(path, encoding="utf-8").read()
        secs = re.split(r"^## ", text, flags=re.M)[1:]
        if len(secs) != len(gids):
            fails.append("LORE_%03d: 节数 %d != 清单 %d" % (gi, len(secs), len(gids)))
        for k, sec in enumerate(secs):
            if k >= len(gids):
                break
            head = sec.splitlines()[0].strip()
            want = "%s %s" % (gids[k], names[gids[k]])
            if not head.startswith(gids[k]):
                fails.append("LORE_%03d 第%d节标题 id 错: %s" % (gi, k + 1, head))
            body = sec.split("\n", 1)[1] if "\n" in sec else ""
            paras = [p for p in re.split(r"\n\s*\n", body) if p.strip()]
            if len(paras) < 3:
                fails.append("LORE_%03d %s: 段落数 %d < 3" % (gi, gids[k], len(paras)))
                continue
            joined = "".join(re.sub(r"\s", "", p) for p in paras)
            n = len(joined)
            total += 1
            if not (120 <= n <= 200):
                fails.append("LORE_%03d %s: 总字数 %d 不在 120–180(容差+20)" % (gi, gids[k], n))
            for lab in ("画面：", "来历：", "画理："):
                if lab not in sec:
                    fails.append("LORE_%03d %s: 缺「%s」段" % (gi, gids[k], lab))
            d = [c["desc"] for c in cat if c["id"] == gids[k]][0]
            dcore = re.sub(r"\s", "", d)
            if len(dcore) >= 8 and dcore in joined:
                fails.append("LORE_%03d %s: 整句复制 desc" % (gi, gids[k]))
    if fails:
        print("FAIL %d 项:" % len(fails))
        for f in fails[:60]:
            print(" -", f)
        sys.exit(1)
    print("全部通过：抽查组 %s，已核 %d 条，三段齐全、字数达标、id 与 catalog 一致、无整句复制 desc" % (
        ",".join(map(str, sorted(only))) if only else "全部", total))

if __name__ == "__main__":
    main()
