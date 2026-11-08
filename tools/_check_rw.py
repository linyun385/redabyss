# -*- coding: utf-8 -*-
"""_check_rw.py — 校验 data/rewrite/RW_*.json 是否符合 T128–T157 任务书验收。
用法: python -I tools/_check_rw.py [组号...]  (缺省查全部)
只读原始素材，不改任何数据文件。
"""
import json, re, sys, io, os, hashlib

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BANNED = ["装置", "设备", "仪器", "开关", "仪表", "面板", "屏幕", "机器", "编号",
          "标签", "刻度", "刻字", "铭文", "字"]
APPL = ["灯", "屏", "按钮", "显示", "喇叭", "收音", "天线", "插座", "电线", "电缆",
        "键盘", "摄像", "音箱", "表盘", "配电", "断路", "荧光", "霓虹", "数码"]
LENS = ["贴地仰视", "仰视", "斜俯", "俯视", "斜侧", "斜放", "平放", "立放", "倒挂", "半埋", "特写", "贴地", "视角"]
CRAFT = ["锈", "铆", "焊", "砸", "磕", "凿", "豁", "瘪", "斑", "裂", "疤", "蚀", "磨", "磕碰", "坑"]
MARKER = "洞底是一整片深红的光"


def main():
    tg = json.load(open(os.path.join(ROOT, "data", "rewrite", "_targets.json"), encoding="utf-8"))
    targets = tg["targets"]
    groups = [targets[i:i + 5] for i in range(0, len(targets), 5)]
    prompts = {x["id"]: x["prompt"] for x in json.load(open(os.path.join(ROOT, "data", "zh_prompts_full.json"), encoding="utf-8"))}
    only = set(int(a) for a in sys.argv[1:]) if len(sys.argv) > 1 else None
    failures = []
    for gi, ids in enumerate(groups, 1):
        if only and gi not in only:
            continue
        path = os.path.join(ROOT, "data", "rewrite", "RW_%03d.json" % gi)
        if not os.path.exists(path):
            failures.append("RW_%03d: 文件缺失" % gi)
            continue
        try:
            arr = json.load(open(path, encoding="utf-8"))
        except Exception as e:
            failures.append("RW_%03d: JSON 解析失败 %s" % (gi, e))
            continue
        if not isinstance(arr, list) or len(arr) != len(ids):
            failures.append("RW_%03d: 条数 %d != 清单 %d" % (gi, len(arr) if isinstance(arr, list) else -1, len(ids)))
            continue
        if [x.get("id") for x in arr] != ids:
            failures.append("RW_%03d: id 顺序与清单不一致: %s" % (gi, [x.get("id") for x in arr]))
            continue
        for x in arr:
            rid, p = x["id"], x.get("prompt", "")
            tag = "RW_%03d %s" % (gi, rid)
            if "\n" in p or "\r" in p:
                failures.append(tag + ": 分行")
            n = len(re.sub(r"\s", "", p))
            if not (80 <= n <= 140):
                failures.append(tag + ": 字数 %d 不在 80–140" % n)
            for w in BANNED + APPL:
                if w in p:
                    failures.append(tag + ": 禁用词「%s」命中" % w)
            if MARKER in p or "深红的光，从下往上照" in p:
                failures.append(tag + ": 主体段混入了光照段")
            if MARKER in prompts[rid]:
                orig_tail = prompts[rid].split(MARKER, 1)[1]
                new_full = p + MARKER + orig_tail
                if len(new_full) < len(prompts[rid]) - 160:
                    failures.append(tag + ": 与原主体段长度差过大(疑似未按规格重写)")
            if not any(w in p for w in LENS):
                failures.append(tag + ": 缺镜头位置词")
            if not any(w in p for w in CRAFT):
                failures.append(tag + ": 缺工艺痕迹词")
    if failures:
        print("FAIL %d 项:" % len(failures))
        for f in failures:
            print(" -", f)
        sys.exit(1)
    n_files = len([f for f in os.listdir(os.path.join(ROOT, "data", "rewrite")) if re.match(r"RW_\d+\.json$", f)])
    print("全部通过：RW 文件 %d 个，抽查组 %s，禁用词 0 命中、字数/镜头/工艺/分行全部达标" % (n_files, ",".join(map(str, sorted(only))) if only else "全部"))


if __name__ == "__main__":
    main()
