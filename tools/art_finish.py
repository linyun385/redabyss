# -*- coding: utf-8 -*-
"""把 manifest 里还缺的素材补完（512×748 加速版），然后跑闸门。

为什么要这个脚本：GLM 那批是 640×936，实测 4 分钟/张（显存溢出），
剩 10 张要 40 分钟。这里改用 512×748（长边缩短 20%，像素少 36%），
单张约 40–60 秒，10 张 ~10 分钟。已存在的文件自动跳过（断点续跑）。
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

GAME = Path(__file__).resolve().parents[1]
GEN = GAME / 'tools' / 'gen_art_diffusers.py'
PY = sys.executable
SIZE = {'card': (512, 752), 'enemy': (512, 752), 'portrait': (512, 768), 'ending': (512, 752)}


def prompt_text(e):
    p = e.get('prompt')
    if isinstance(p, dict):
        return ' '.join(x for x in (p.get('prefix'), p.get('obj'), p.get('suffix')) if x)
    return str(p)


def main():
    os.environ.setdefault('HF_ENDPOINT', 'https://hf-mirror.com')
    m = json.loads((GAME / 'tools' / 'art_manifest.json').read_text(encoding='utf-8'))
    missing = [e for e in m['entries'] if not (GAME / e['out']).exists()]
    print('缺', len(missing), '张')
    ok = fail = 0
    t_all = time.time()
    for e in missing:
        out = GAME / e['out']
        out.parent.mkdir(parents=True, exist_ok=True)
        kind = 'portfolio'
        o = str(e['out'])
        if '/ending' in o:
            kind = 'ending'
        elif '/portrait' in o or '/class' in o:
            kind = 'portrait'
        elif '/enem' in o:
            kind = 'enemy'
        w, h = SIZE.get(kind, (512, 748))
        t0 = time.time()
        r = subprocess.run([PY, str(GEN), '--raw', '--prompt', prompt_text(e),
                            '--neg', str(e.get('negative') or ''),
                            '--out', str(out), '--width', str(w), '--height', str(h),
                            '--steps', '20', '--seed', str(e.get('seed') or 7)],
                           capture_output=True, text=True, encoding='utf-8', errors='replace')
        took = time.time() - t0
        good = r.returncode == 0 and out.exists()
        print('%-52s %s %4.0fs' % (o, 'ok' if good else 'FAIL', took), flush=True)
        if good:
            ok += 1
        else:
            fail += 1
            print((r.stderr or '')[-200:])
    print('补完 %d 张，失败 %d 张，总耗时 %.0f 分钟' % (ok, fail, (time.time() - t_all) / 60))


if __name__ == '__main__':
    main()
