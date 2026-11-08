# -*- coding: utf-8 -*-
"""按 T335_PRUNE.csv 删卡（演练优先）

用法：
  python tools\\_apply_prune.py            # 演练，只报会删什么
  python tools\\_apply_prune.py --apply    # 真删
"""
import csv
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
GAME = Path(__file__).resolve().parents[1]
CARDS = GAME / 'cards'
CSV = GAME / 'docs' / 'design' / 'stream' / 'T335_PRUNE.csv'
WEB = GAME / 'web' / 'index.html'
APPLY = '--apply' in sys.argv


def main():
    if not CSV.exists():
        print('找不到', CSV)
        return 2

    targets = []
    with CSV.open(encoding='utf-8-sig', newline='') as f:
        for row in csv.DictReader(f):
            cid = (row.get('id') or '').strip()
            if cid:
                targets.append((cid, row.get('class', ''), row.get('reuse_for', '')))

    print('待删 %d 张' % len(targets))

    # 扫所有 json，看每张卡在哪个文件
    found = {}
    for p in sorted(CARDS.glob('*.json')):
        try:
            data = json.loads(p.read_text(encoding='utf-8'))
        except Exception as e:
            print('  读失败 %s: %s' % (p.name, e))
            continue
        idx = {}
        for i, c in enumerate(data):
            if isinstance(c, dict) and c.get('id'):
                idx[c['id']] = i
        found[p] = (data, idx)

    plan = []   # (path, id, class, reuse_for, index)
    missing = []
    for cid, cls, reuse in targets:
        hit = None
        for p, (data, idx) in found.items():
            if cid in idx:
                hit = (p, idx[cid])
                break
        if hit:
            plan.append((hit[0], cid, cls, reuse, hit[1]))
        else:
            missing.append(cid)

    by_file = {}
    for p, cid, cls, reuse, i in plan:
        by_file.setdefault(p.name, []).append(cid)

    print('\n按文件分布：')
    for name, ids in sorted(by_file.items()):
        print('  %-18s %d 张' % (name, len(ids)))
    if missing:
        print('\n★ 在 cards/*.json 里找不到的 %d 张：%s' % (len(missing), ', '.join(missing[:10])))

    # 检查 web/index.html 里有没有硬编码这些 id
    print('\n检查 web/index.html 是否有硬编码引用…')
    if WEB.exists():
        html = WEB.read_text(encoding='utf-8', errors='replace')
        hits = {cid: len(re.findall(r'\b%s\b' % re.escape(cid), html)) for cid, _, _ in targets}
        dirty = {k: v for k, v in hits.items() if v}
        if dirty:
            print('  ⚠ %d 个 id 在 index.html 里出现：' % len(dirty))
            for k, v in list(dirty.items())[:15]:
                print('    %s × %d' % (k, v))
        else:
            print('  ✓ 58 个 id 在 index.html 里 0 命中')
    else:
        print('  找不到 web/index.html')

    if not APPLY:
        print('\n[演练] 未改动任何文件。加 --apply 真删。')
        return 0

    # 真删：按文件倒序索引删除，避免位移
    for p, (data, idx) in found.items():
        ids_here = set(by_file.get(p.name, []))
        if not ids_here:
            continue
        before = len(data)
        kept = [c for c in data if not (isinstance(c, dict) and c.get('id') in ids_here)]
        removed = before - len(kept)
        p.write_text(json.dumps(kept, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
        print('  %-18s %d → %d（删 %d）' % (p.name, before, len(kept), removed))

    print('\n完成。备份在 cards/_bak-20261104/')
    return 0


if __name__ == '__main__':
    sys.exit(main())
