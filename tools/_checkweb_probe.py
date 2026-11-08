# -*- coding: utf-8 -*-
"""回归测试：确认 check_web.js 仍然会拦 http(s) 外链素材（改了规则后必须验）。

做法：临时把一条 http 图片引用塞进 index.html → 跑检查器 → 期望 FAIL → 还原。
异常也保证还原（finally）。
"""
import subprocess
import sys
from pathlib import Path

GAME = Path(__file__).resolve().parents[1]
HTML = GAME / 'web' / 'index.html'
BAK = GAME / 'web' / '_checkweb_probe_bak.html'
PROBE = '<img src="https://evil.example.com/probe.png" alt="probe">'


def main():
    orig = HTML.read_text(encoding='utf-8')
    BAK.write_text(orig, encoding='utf-8')
    try:
        HTML.write_text(orig.replace('</body>', PROBE + '\n</body>'), encoding='utf-8')
        r = subprocess.run(['node', str(GAME / 'tools' / 'check_web.js')],
                           capture_output=True, text=True, encoding='utf-8', errors='replace')
        out = r.stdout or ''
        fails = [l.strip() for l in out.splitlines() if 'FAIL' in l]
        print('注入外链后：exit=%d，FAIL 条数=%d' % (r.returncode, len(fails)))
        for l in fails[:4]:
            print('  ', l)
        print('判定：', '通过（检查器仍会拦外链）' if r.returncode != 0 else '失败（检查器没拦住！）')
    finally:
        HTML.write_text(orig, encoding='utf-8')
        BAK.unlink(missing_ok=True)
        # 还原后再跑一次确认干净
        r2 = subprocess.run(['node', str(GAME / 'tools' / 'check_web.js')],
                            capture_output=True, text=True, encoding='utf-8', errors='replace')
        print('还原后 exit=%d（应为 0）' % r2.returncode)


if __name__ == '__main__':
    sys.exit(main())
