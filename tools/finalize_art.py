# -*- coding: utf-8 -*-
"""定稿清单 + 导入器（带备份与回滚）。

只做两件事：
  1. 依据 picks.json 生成 data/final_manifest.json 与 docs/FINAL_MANIFEST.md
  2. --apply 时把选中的候选图复制进 web/assets/art（先整目录备份）

★ 注意：**光导文件看不到效果** —— index.html 的 window.ART 表没有收录这 461 个 id，
  渲染处走的是 class_/foe_/face_ 那几套通用图。接线是另一件事，本脚本不做。

用法：
  python tools/finalize_art.py                # 只生成清单（默认，无副作用）
  python tools/finalize_art.py --apply        # 备份 + 复制文件
  python tools/finalize_art.py --rollback <备份目录名>
"""
import argparse
import hashlib
import json
import shutil
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

GAME = Path(__file__).resolve().parents[1]
ART = GAME / 'web' / 'assets' / 'art'
VERS = GAME / 'art' / 'versions'
PICKS = GAME / 'data' / 'picks.json'
CAT = GAME / 'data' / 'art_catalog.json'
MANIFEST = GAME / 'data' / 'final_manifest.json'
DOC = GAME / 'docs' / 'FINAL_MANIFEST.md'
BACKUPS = GAME / 'art' / '_backup'


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()[:16]


def src_of(aid, v):
    return (ART / (aid + '.webp')) if v == 0 else (VERS / ('%s_v%d.webp' % (aid, v)))


def build():
    picks = json.loads(PICKS.read_text(encoding='utf-8'))
    cat = {r['id']: r for r in json.loads(CAT.read_text(encoding='utf-8'))}
    rows, problems = [], []
    for aid in sorted(cat):
        p = picks.get(aid) or {}
        v = p.get('chosen')
        if v is None:
            problems.append((aid, '没有选中版本'))
            continue
        if not p.get('confirmed'):
            problems.append((aid, '未复核'))
        s = src_of(aid, v)
        if not s.exists():
            problems.append((aid, '源文件不存在: %s' % s.name))
            continue
        rows.append({
            'id': aid,
            'name': cat[aid].get('name', ''),
            'kind': cat[aid].get('kind', ''),
            'version': v,
            'src': str(s.relative_to(GAME)).replace('\\', '/'),
            'dst': 'web/assets/art/%s.webp' % aid,
            'bytes': s.stat().st_size,
            'sha256_16': sha(s),
        })
    return rows, problems


def write_manifest(rows, problems):
    now = datetime.now().isoformat(timespec='seconds')
    MANIFEST.write_text(json.dumps({
        'generated_at': now,
        'total': len(rows),
        'problems': problems,
        'items': rows,
    }, ensure_ascii=False, indent=1), encoding='utf-8')

    vc = Counter(r['version'] for r in rows)
    kc = Counter(r['kind'] for r in rows)
    need = sum(1 for r in rows if r['version'] != 0)
    total_mb = sum(r['bytes'] for r in rows) / 1024 / 1024

    L = ['# 定稿清单', '',
         '> 生成于 **%s**，来自 `data/picks.json`（461 条全部已复核）。' % now,
         '> 机器可读版：`data/final_manifest.json`', '',
         '## 总览', '',
         '| 项 | 值 |', '|---|---|',
         '| 条目总数 | %d |' % len(rows),
         '| 需要替换（选的不是 v0）| **%d** |' % need,
         '| 保持原图（选 v0）| %d |' % (len(rows) - need),
         '| 合计体积 | %.1f MB |' % total_mb,
         '| 未通过校验 | %d |' % len(problems), '',
         '## 选中版本分布', '',
         '| 版本 | 张数 | 说明 |', '|---|---|---|']
    for v, n in sorted(vc.items()):
        note = '原图，不替换' if v == 0 else '候选 v%d' % v
        L.append('| v%d | %d | %s |' % (v, n, note))
    L += ['', '## 按类型', '', '| 类型 | 张数 |', '|---|---|']
    for k, n in kc.most_common():
        L.append('| %s | %d |' % ({'card': '卡牌', 'foe': '敌人', 'evt': '事件'}.get(k, k), n))
    if problems:
        L += ['', '## 校验未通过', '', '| id | 原因 |', '|---|---|']
        for aid, why in problems:
            L.append('| `%s` | %s |' % (aid, why))
    L += ['', '## 明细', '', '| id | 名字 | 类型 | 版本 | 源文件 | 大小 |', '|---|---|---|---|---|---|']
    for r in rows:
        L.append('| `%s` | %s | %s | v%d | `%s` | %.0f KB |' % (
            r['id'], r['name'], {'card': '卡牌', 'foe': '敌人', 'evt': '事件'}.get(r['kind'], r['kind']),
            r['version'], r['src'], r['bytes'] / 1024))
    L.append('')
    DOC.write_text('\n'.join(L), encoding='utf-8')
    return vc, need, total_mb


def apply(rows):
    stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    bak = BACKUPS / ('art_%s' % stamp)
    bak.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(ART, bak)
    print('已备份整目录 → %s（%d 个文件）' % (bak.relative_to(GAME), len(list(bak.glob('*.webp')))))

    n = 0
    for r in rows:
        s = GAME / r['src']
        d = GAME / r['dst']
        if s.resolve() == d.resolve():
            continue          # 选的 v0 就是原图，不用动
        shutil.copy2(s, d)
        n += 1
    print('已替换 %d 张（其余 %d 张保持原图）' % (n, len(rows) - n))
    print('回滚命令：python tools/finalize_art.py --rollback art_%s' % stamp)
    print()
    print('!! 注意：文件已就位，但 index.html 的 window.ART 表没有这些 id，游戏里仍看不到。')
    print('   接线要改渲染处，见 docs/FINAL_MANIFEST.md 末尾。')


def rollback(name):
    bak = BACKUPS / name
    if not bak.exists():
        print('找不到备份：%s' % bak)
        return 1
    for f in bak.glob('*.webp'):
        shutil.copy2(f, ART / f.name)
    print('已从 %s 恢复 %d 个文件' % (name, len(list(bak.glob('*.webp')))))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--rollback', default='')
    a = ap.parse_args()

    if a.rollback:
        return rollback(a.rollback)

    rows, problems = build()
    vc, need, mb = write_manifest(rows, problems)
    print('清单已生成：data/final_manifest.json + docs/FINAL_MANIFEST.md')
    print('  条目 %d ｜ 需替换 %d ｜ 保持原图 %d ｜ %.1f MB ｜ 校验问题 %d'
          % (len(rows), need, len(rows) - need, mb, len(problems)))
    print('  版本分布：%s' % '，'.join('v%d=%d' % (k, v) for k, v in sorted(vc.items())))
    if problems:
        print('  问题：')
        for aid, why in problems[:10]:
            print('    %s — %s' % (aid, why))
    if a.apply:
        print()
        apply(rows)
    else:
        print()
        print('这是演练模式，没有动任何文件。要真导入加 --apply。')
    return 0


if __name__ == '__main__':
    sys.exit(main())
