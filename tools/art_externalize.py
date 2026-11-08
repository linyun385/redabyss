# -*- coding: utf-8 -*-
"""把 index.html 里 window.ART 的 data URI 全部落盘成 web/assets/art/*.webp，表里改存相对路径。

背景（2026-10-31）：
  单文件内联导致 ART 表 2.1MB+，`check_web.js` 3MB 上限被顶穿，而且以后有背景/音频根本放不下。
  用户拍板：素材外置到 web/assets/，index.html 用相对路径引用，交付用 zip 打包（可选单文件构建）。

用法：python tools/art_externalize.py [--dry]
"""
import base64
import json
import re
import sys
from pathlib import Path

GAME = Path(__file__).resolve().parents[1]
HTML = GAME / 'web' / 'index.html'
OUTDIR = GAME / 'web' / 'assets' / 'art'
TAG = 'window.ART = '


def main():
    dry = '--dry' in sys.argv
    s = HTML.read_text(encoding='utf-8')
    i = s.find(TAG)
    if i < 0:
        raise SystemExit('没找到 window.ART')

    # 从 "window.ART = {" 开始做括号匹配，取出 JSON 体
    start = s.find('{', i)
    depth = 0
    end = None
    for k in range(start, len(s)):
        c = s[k]
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                end = k + 1
                break
    body = s[start:end]
    try:
        table = json.loads(body)
    except Exception as e:
        raise SystemExit('ART 表不是合法 JSON：%s' % e)

    OUTDIR.mkdir(parents=True, exist_ok=True)
    newtab = {}
    n_data = 0
    raw_bytes = 0
    for k, v in table.items():
        if isinstance(v, str) and v.startswith('data:image/'):
            head, b64 = v.split(',', 1)
            ext = 'webp' if 'webp' in head else ('png' if 'png' in head else 'jpg')
            data = base64.b64decode(b64)
            raw_bytes += len(data)
            p = OUTDIR / ('%s.%s' % (k, ext))
            if not dry:
                p.write_bytes(data)
            newtab[k] = 'assets/art/%s.%s' % (k, ext)
            n_data += 1
        else:
            newtab[k] = v          # 已经是路径，原样保留

    new_body = json.dumps(newtab, ensure_ascii=False, separators=(',', ':'))
    out = s[:start] + new_body + s[end:]
    if not dry:
        HTML.write_text(out, encoding='utf-8')
    print('ART 条目 %d，其中 data URI %d 条 → 落盘 %.2f MB' % (len(table), n_data, raw_bytes / 1024 / 1024))
    print('新 HTML %.0f KB（原 %.0f KB）' % (len(out) / 1024, len(s) / 1024))
    print('素材目录', OUTDIR)


if __name__ == '__main__':
    main()
