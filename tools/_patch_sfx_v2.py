# -*- coding: utf-8 -*-
"""v2 音效改名的收尾：把 ui.open / ui.close 统一成 ui.page。

用户 2026-11-05：「界面切换这块，我觉得可以只做一个（书页翻动的声音）」。

两处：
  L6938  playSfx(o.classList.contains('hidden') ? 'ui.open' : 'ui.close');
  L7730  预载清单里的 'ui.click', 'ui.open', 'ui.close',
"""
import sys
import shutil
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
GAME = Path(__file__).resolve().parents[1]
HTML = GAME / 'web' / 'index.html'

PAIRS = [
    ("playSfx(o.classList.contains('hidden') ? 'ui.open' : 'ui.close');",
     "playSfx('ui.page');   /* 2026-11-05 合并：翻开/合上同一个书页声 */"),
    ("'ui.click', 'ui.open', 'ui.close',",
     "'ui.click', 'ui.page',"),
]


def main():
    apply = '--apply' in sys.argv
    src = HTML.read_text(encoding='utf-8')
    print('index.html %d 字节' % len(src.encode('utf-8')))

    ok = True
    for old, new in PAIRS:
        n = src.count(old)
        print('  匹配 %d 次：%s' % (n, old[:52]))
        if n != 1:
            ok = False
    if not ok:
        print('\n!! 有不等于 1 的匹配，停下。')
        return 2

    out = src
    for old, new in PAIRS:
        out = out.replace(old, new, 1)

    print('\n替换后 %d 字节' % len(out.encode('utf-8')))
    if not apply:
        print('[演练] 加 --apply 才真写')
        return 0

    bak = HTML.with_name('index.html.bak-%s-sfxv2' % datetime.now().strftime('%Y%m%d-%H%M%S'))
    shutil.copy2(str(HTML), str(bak))
    print('备份:', bak.name)
    HTML.write_text(out, encoding='utf-8')

    chk = HTML.read_text(encoding='utf-8')
    print('复查 ui.page:', chk.count("'ui.page'"), '次')
    print('残留 ui.open:', chk.count("'ui.open'"), '次')
    print('残留 ui.close:', chk.count("'ui.close'"), '次')
    return 0


if __name__ == '__main__':
    sys.exit(main())
