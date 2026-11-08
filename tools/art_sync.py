# -*- coding: utf-8 -*-
"""把 art/ 下新生成的素材同步进 web/assets/art/，并重建 window.ART 表（路径版）。

- 清单是唯一真相：tools/art_manifest.json 的 entries[].id ↔ entries[].out
- 目标：web/assets/art/<id>.webp（统一转 webp，长边 ≤768，q82）
- 只处理"art/ 有文件但 web/assets/art 缺"的条目；已存在的跳过（幂等）
- ART 表按清单全量重建（已有 70 条 + 新增的 9 条一起）

用法：python tools/art_sync.py [--dry]
"""
import json
import sys
from pathlib import Path

from PIL import Image

GAME = Path(__file__).resolve().parents[1]
MANIFEST = GAME / 'tools' / 'art_manifest.json'
OUTDIR = GAME / 'web' / 'assets' / 'art'
HTML = GAME / 'web' / 'index.html'
TAG = 'window.ART = '
MAX_EDGE = 768
QUALITY = 82


def main():
    dry = '--dry' in sys.argv
    m = json.loads(MANIFEST.read_text(encoding='utf-8'))
    OUTDIR.mkdir(parents=True, exist_ok=True)
    table, added, missing = {}, 0, []
    for e in m['entries']:
        eid, out = e['id'], GAME / e['out']
        dst = OUTDIR / (eid + '.webp')
        if not out.exists():
            missing.append(str(out))
            continue
        if not dst.exists():
            if not dry:
                im = Image.open(out).convert('RGB')
                im.thumbnail((MAX_EDGE, MAX_EDGE), Image.LANCZOS)
                im.save(dst, 'WEBP', quality=QUALITY, method=6)
            added += 1
        table[eid] = 'assets/art/%s.webp' % eid

    body = json.dumps(table, ensure_ascii=False, separators=(',', ':'))
    if not dry:
        s = HTML.read_text(encoding='utf-8')
        i = s.find(TAG)
        start = s.find('{', i)
        depth = 0
        for k in range(start, len(s)):
            if s[k] == '{':
                depth += 1
            elif s[k] == '}':
                depth -= 1
                if depth == 0:
                    end = k + 1
                    break
        # 2026-11-05 事故：原来这里拿 manifest 的 79 条**全量覆盖** window.ART，
        # 把已有 552 条砍到 79 条，473 张卡牌/敌人/事件图全部丢映射、游戏退回占位图。
        # 现在改成「读现有表 → 只把 manifest 的条目补进去 → 不删任何键」。
        existing = {}
        try:
            st = s.find('{', i)
            dep = 0
            for k in range(st, len(s)):
                if s[k] == '{':
                    dep += 1
                elif s[k] == '}':
                    dep -= 1
                    if dep == 0:
                        existing = json.loads(s[st:k + 1])
                        break
        except Exception:
            existing = {}
        kept = len(existing)
        merged = dict(existing)
        merged.update(table)
        body = json.dumps(merged, ensure_ascii=False, separators=(',', ':'))
        print('ART 表：原 %d 条，manifest %d 条，合并后 %d 条（只增不删）'
              % (kept, len(table), len(merged)))
        s = s[:start] + body + s[end:]
        HTML.write_text(s, encoding='utf-8')
    print('ART 条目 %d，新增落盘 %d，源文件缺失 %d' % (len(table), added, len(missing)))
    for x in missing[:5]:
        print('  缺:', x)
    print('HTML %.0f KB' % (len(HTML.read_text(encoding='utf-8')) / 1024) if not dry else '(dry)')


if __name__ == '__main__':
    main()
