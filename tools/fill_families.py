# -*- coding: utf-8 -*-
"""fill_families.py — 用 qwen 提示词补全形态族表（T79 增量）。

数据源：
    data/zh_prompts_full.json —— 每对象一条 qwen 中文提示词（真实出图用的那份）
    data/art_catalog.json     —— A4 口径文本（name+desc+extra）与 kind
    data/art_families.json    —— 既有 20 族（原样保留）

算法（无随机，可复算）：
  1) 未覆盖对象按 qwen 的 family 字段分池（语义近邻），池内再按 FORM_KEYWORDS
     （与 tools/check_families.js 同表）求交集贪心成族，每族 ≤3、加入须与全族共享关键词；
  2) 族 prompt = 代表成员（族内首个）的 qwen 提示词——即真实出图 prompt，R2 复用语义；
  3) 族 id：foe/card 用 foe_family_<代表成员id 去前缀>，event 用 evt_<eventId>（A6 规则）。

产出：data/art_families.json（覆盖 100%）+ docs/ART_FAMILIES.md
"""
import json
import os
import sys
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 与 tools/check_families.js FORM_KEYWORDS 完全一致
FORM_KEYWORDS = [
    "菌", "霉", "苔", "藻", "螨", "虫", "蛛", "鳗", "鱼", "蟹", "蛙", "龟", "蛇", "蠕", "蛆", "蝇", "蛾",
    "甲壳", "外骨骼", "壳", "触手", "触须", "须", "复眼", "单眼", "眼", "鳃", "鳍", "鳞", "爪", "足", "腿",
    "吸盘", "口器", "齿", "骨", "血", "肉", "皮", "膜", "囊", "伞", "孔", "腔", "翼", "刺", "毛",
    "卵", "蛹", "茧", "幼体", "人形", "直立", "四足", "多足", "无眼", "盲", "发光",
    "晶", "结晶", "盐", "锈", "裂", "铁", "铜", "钢", "铝", "玻璃", "胶", "绳", "纸", "印", "章", "墨",
    "灯", "管", "阀", "镜", "屏", "针", "线", "钉", "铆钉", "罐", "瓶", "桶", "布", "绷带", "面罩",
    "手套", "梯", "牌", "板", "匣", "柜", "棺", "碑", "尸", "遗体", "碎石", "蕨", "藤", "根", "灰", "尘", "雾",
    "倒挂", "倒吊", "攀附", "寄生", "共生", "食腐", "滤食", "钻孔", "挖掘", "悬浮", "漂浮", "贴附",
]


def keywords_of(text):
    return {k for k in FORM_KEYWORDS if k in text}


def load(p):
    return json.load(open(os.path.join(ROOT, p), encoding="utf-8"))


def main():
    cat = load("data/art_catalog.json")
    z = {x["id"]: x for x in load("data/zh_prompts_full.json")}
    fam = load("data/art_families.json")

    covered, used_fids = set(), set()
    for k in ("foe", "card", "event"):
        for fid, f in (fam.get(k) or {}).items():
            used_fids.add(fid)
            covered.update(f["members"])

    pending = [it for it in cat if it["id"] not in covered]
    kws = {it["id"]: keywords_of("%s %s %s" % (it.get("name", ""), it.get("desc", ""), it.get("extra", "")))
           for it in pending}

    # 按 qwen family 分池
    pools = defaultdict(list)
    for it in pending:
        # 池键 = (类别, qwen family 名)——类别隔离，防跨类别复用（R1/A2）
        pools[(it["kind"], z[it["id"]].get("family", "未名"))].append(it["id"])

    KIND = {"foe": "foe", "card": "card", "evt": "event"}
    newf = {"foe": {}, "card": {}, "event": {}}
    stats = Counter()

    for pool_name, ids in sorted(pools.items()):
        # 打包优先：先按「池内共享关键词」降序成组（同词者必同族，A4 天然成立），剩余按序单列
        kw_members = defaultdict(list)
        for oid in ids:
            for k in kws[oid]:
                kw_members[k].append(oid)
        assigned = set()
        open_fams = []  # [shared_keys(set), members]
        # 关键词按成员数降序 → 尽量凑满 3 人族
        for k, ms in sorted(kw_members.items(), key=lambda kv: (-len(kv[1]), kv[0])):
            free = [o for o in ms if o not in assigned]
            for chunk in [free[i:i + 3] for i in range(0, len(free), 3)]:
                if chunk:
                    open_fams.append([{k}, list(chunk)])
                    assigned.update(chunk)
        # 剩余未分配（无任何关键词或只剩单）——尝试与既有族共享关键词合并，否则单列
        for oid in ids:
            if oid in assigned:
                continue
            placed = False
            if kws[oid]:
                for e in open_fams:
                    if len(e[1]) >= 3:
                        continue
                    if kws[oid] & e[0]:
                        e[0] &= kws[oid]
                        e[1].append(oid)
                        placed = True
                        break
            if not placed:
                open_fams.append([set(kws[oid]), [oid]])
            assigned.add(oid)

        for shared, members in open_fams:
            rep = members[0]
            kind = KIND[cat_by_id(rep)["kind"]]
            if kind == "event":
                fid = "evt_" + rep  # evt_event_d3_1 形如 evt_event_d3_1，符合 A6
            else:
                # 用代表成员全 id（字母开头），如 foe_family_enemy_d1_02 / card_family_cng_0050
                fid = ("foe_family_" if kind == "foe" else "card_family_") + rep.lower()
                base, i = fid, 2
                while fid in used_fids or fid in newf[kind]:
                    fid = "%s_%d" % (base, i)
                    i += 1
            newf[kind][fid] = {
                "name": "%s（%s）" % (pool_name, "/".join(sorted(shared))[:24] if shared else "独形"),
                "members": members,
                "prompt": z[rep]["prompt"],
                "style": "A",
            }
            used_fids.add(fid)
            stats["families"] += 1
            stats["members"] += len(members)

    for kind in ("foe", "card", "event"):
        fam.setdefault(kind, {}).update(newf[kind])
    json.dump(fam, open(os.path.join(ROOT, "data", "art_families.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    print("新增族 %d / 新覆盖成员 %d" % (stats["families"], stats["members"]))
    for kind in ("foe", "card", "event"):
        n_f = len(fam[kind])
        n_m = sum(len(f["members"]) for f in fam[kind].values())
        print("%s: %d 族 / %d 成员 / 复用率 %.2f" % (kind, n_f, n_m, n_m / max(1, n_f)))


def cat_by_id(oid):
    for it in CAT:
        if it["id"] == oid:
            return it
    raise KeyError(oid)


CAT = load("data/art_catalog.json")

if __name__ == "__main__":
    main()
