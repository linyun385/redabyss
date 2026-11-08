# -*- coding: utf-8 -*-
"""打包交付：默认打 zip（web/ 整目录）；--inline 额外生成单文件内联版。

为什么要有两种：
  · zip 版：素材在 web/assets/ 下（图片/音频），体积不受限，更新方便
  · inline 版：把 ART 表里的 webp 塞回 data URI，得到一个可单发的 HTML（体积会大，仅供"双击即玩"）

用法：
  python tools/build_pack.py                 # dist/redabyss-YYYYMMDD.zip
  python tools/build_pack.py --inline        # 额外生成 dist/redabyss-single-YYYYMMDD.html
"""
import argparse
import base64
import json
import re
import zipfile
from datetime import datetime
from pathlib import Path

GAME = Path(__file__).resolve().parents[1]
WEB = GAME / 'web'
DIST = GAME / 'dist'
TAG = 'window.ART = '


def art_table(html):
    i = html.find(TAG)
    start = html.find('{', i)
    depth = 0
    for k in range(start, len(html)):
        if html[k] == '{':
            depth += 1
        elif html[k] == '}':
            depth -= 1
            if depth == 0:
                return start, k + 1, json.loads(html[start:k + 1])
    raise SystemExit('ART 表解析失败')


def build_zip(stamp):
    DIST.mkdir(exist_ok=True)
    out = DIST / ('redabyss-%s.zip' % stamp)
    n = 0
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p in WEB.rglob('*'):
            if not p.is_file():
                continue
            rel = p.relative_to(WEB)
            if '.bak' in p.name:
                continue
            z.write(p, rel.as_posix())
            n += 1
    return out, n


def build_inline(stamp):
    html = (WEB / 'index.html').read_text(encoding='utf-8')
    start, end, table = art_table(html)
    inlined = {}
    total = 0
    for k, v in table.items():
        p = WEB / v
        if not p.exists():
            inlined[k] = v
            continue
        data = p.read_bytes()
        total += len(data)
        inlined[k] = 'data:image/webp;base64,' + base64.b64encode(data).decode()
    body = json.dumps(inlined, ensure_ascii=False, separators=(',', ':'))
    out_html = html[:start] + body + html[end:]
    DIST.mkdir(exist_ok=True)
    out = DIST / ('redabyss-single-%s.html' % stamp)
    out.write_text(out_html, encoding='utf-8')
    return out, len(table), total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--inline', action='store_true')
    a = ap.parse_args()
    stamp = datetime.now().strftime('%Y%m%d-%H%M')

    z, n = build_zip(stamp)
    print('zip: %s（%d 个文件，%.1f MB）' % (z, n, z.stat().st_size / 1024 / 1024))
    if a.inline:
        f, cnt, raw = build_inline(stamp)
        print('inline: %s（%d 张素材，素材 %.1f MB，文件 %.1f MB）'
              % (f, cnt, raw / 1024 / 1024, f.stat().st_size / 1024 / 1024))


if __name__ == '__main__':
    main()
