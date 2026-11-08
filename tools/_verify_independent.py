# -*- coding: utf-8 -*-
"""独立复核脚本（不依赖浏览器）：素材表 / 路径 / 外链 / 体积。"""
import json
import re
import sys
from pathlib import Path

GAME = Path(__file__).resolve().parents[1]
WEB = GAME / 'web'
HTML = WEB / 'index.html'


def art_table(s):
    i = s.find('window.ART = ')
    st = s.find('{', i)
    d = 0
    for k in range(st, len(s)):
        if s[k] == '{':
            d += 1
        elif s[k] == '}':
            d -= 1
            if d == 0:
                return st, k + 1, json.loads(s[st:k + 1])
    raise SystemExit('ART 表解析失败')


def main():
    s = HTML.read_text(encoding='utf-8')
    st, en, tab = art_table(s)
    vals = list(tab.values())
    rel = [v for v in vals if isinstance(v, str) and v.startswith('assets/art/')]
    missing = [v for v in rel if not (WEB / v).exists()]
    print('HTML %.0f KB' % (len(s) / 1024))
    print('ART 条目 %d | 相对路径 %d | 缺失文件 %d' % (len(tab), len(rel), len(missing)))
    if missing:
        print('  缺失示例:', missing[:5])
    print('data:image 残留 %d' % s.count('data:image/'))
    http_asset = re.findall(r'https?://[^"\'\s)]+\.(?:png|jpe?g|webp|gif|svg|mp3|ogg|wav)', s, re.I)
    print('http(s) 素材引用 %d' % len(http_asset))
    print('a1dio/audio 标签数 %d' % len(re.findall(r'<audio\b', s, re.I)))
    # 素材体积统计
    sizes = sorted((WEB / v).stat().st_size for v in rel if (WEB / v).exists())
    if sizes:
        print('素材 %d 个，总 %.2f MB，最大 %.1f KB，中位 %.1f KB'
              % (len(sizes), sum(sizes) / 1024 / 1024, sizes[-1] / 1024, sizes[len(sizes) // 2] / 1024))
    # 新地图默认判定：看是否有 map=old 分支 + 默认走生成器的标志
    old_branch = 'map=old' in s
    gen_hint = ('MAPGEN-LIB' in s) and ('generateRegion' in s or 'mapgen' in s.lower())
    print('回退分支 map=old: %s | 生成器内联: %s' % (old_branch, gen_hint))


if __name__ == '__main__':
    main()
