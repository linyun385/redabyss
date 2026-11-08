# -*- coding: utf-8 -*-
"""T67 素材嵌入：把 art/ 下的生成图降采样到长边 ≤512、按类型体积帽压 webp，
生成 base64 data URI 的 ART 常量表，注入 web/index.html（标记化，幂等）。

体积帽（T67 硬约束）：卡面 ≤30KB / 敌人 ≤20KB / 立绘 ≤60KB / 结局 ≤120KB。
超帽策略：quality 82→78（任务书允许档），仍超则长边 512→448 再压；到 78+448 仍超就
如实报告（不许改检查器阈值过关）。

用法：python tools/art_embed.py            # 全量嵌入（跳过文件里已有的 id）
      python tools/art_embed.py --dry      # 只打印体积表不写盘
"""
import argparse
import base64
import io
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / 'tools' / 'art_manifest.json'
HTML = ROOT / 'web' / 'index.html'

CAPS = {'face': 30, 'foe': 20, 'class': 60, 'end': 120}   # KB
LONG_EDGE = 512
EDGE_LADDER = [512, 448, 384, 341, 320, 300]   # 超帽逐级降尺寸（任务书授权：降 quality 或尺寸）
Q_RANGE = [82, 80, 78]


def cap_of(entry_id):
    return CAPS['end' if entry_id.startswith('end_') else
                'class' if entry_id.startswith('class_') else
                'foe' if entry_id.startswith('foe_') else 'face']


def base_edge(entry_id):
    # T69 预算策略：面/敌量大（72 张）用 448 基线压总体积；立绘/结局量少保持 512
    if entry_id.startswith('class_'): return 512
    if entry_id.startswith('end_'): return 448
    return 320


def compress(img, long_edge, q):
    im = img.copy()
    w, h = im.size
    scale = long_edge / max(w, h)
    if scale < 1:
        im = im.resize((max(1, round(w * scale)), max(1, round(h * scale))), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, 'WEBP', quality=q, method=6)
    return buf.getvalue()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry', action='store_true')
    args = ap.parse_args()

    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    art = {}
    report = []
    total_raw = 0
    over = []
    for e in manifest['entries']:
        src = ROOT / e['out']
        if not src.exists():
            continue
        img = Image.open(src)
        cap_kb = cap_of(e['id'])
        data = None
        for edge in [base_edge(e['id'])] + [x for x in EDGE_LADDER if x < base_edge(e['id'])]:
            for q in Q_RANGE:
                data = compress(img, edge, q)
                if len(data) <= cap_kb * 1024:
                    break
            if len(data) <= cap_kb * 1024:
                break
        kb = len(data) / 1024
        total_raw += len(data)
        if kb > cap_kb:
            over.append({'id': e['id'], 'kb': round(kb, 1), 'cap': cap_kb})
        art[e['id']] = 'data:image/webp;base64,' + base64.b64encode(data).decode('ascii')
        report.append({'id': e['id'], 'src': e['out'], 'kb': round(kb, 1), 'cap': cap_kb,
                       'edge': edge, 'q': q})
        print(f"{e['id']:28s} {kb:6.1f} KB（帽 {cap_kb}）edge={edge} q={q}")

    b64_total = sum(len(v) for v in art.values())
    print(f'\n共 {len(art)} 张；原始 webp 合计 {total_raw/1024:.0f} KB；base64 后 {b64_total/1024:.0f} KB')
    if over:
        print('超帽（如实报告，不放宽检查器）:')
        for o in over:
            print('  ', o)

    if args.dry:
        return

    html = HTML.read_text(encoding='utf-8')
    OPEN = '/* ==ART-TABLE== T67 素材常量表（tools/art_embed.py 生成；重跑即刷新；data: URI 内联） == */'
    CLOSE = '/* ==/ART-TABLE== */'
    block = '<script>\n' + OPEN + '\nwindow.ART = ' + json.dumps(art, ensure_ascii=False,
              separators=(',', ':')) + ';\n' + CLOSE + '\n</script>'
    oi = html.find(OPEN)
    if oi >= 0:
        so = html.rindex('<script>', 0, oi)
        ci = html.find(CLOSE, oi)
        se = html.find('</script>', ci) + 9
        html = html[:so] + block + html[se:]
        print('ART 表已替换')
    else:
        anchor = html.index('/* ==/MAPGEN-BINDINGS== */')
        se = html.find('</script>', anchor) + 9
        html = html[:se] + '\n' + block + html[se:]
        print('ART 表已注入')
    HTML.write_text(html, encoding='utf-8')

    (ROOT / 'tools' / 'art_embed_report.json').write_text(
        json.dumps({'entries': report, 'total_raw_kb': round(total_raw / 1024, 1),
                    'total_b64_kb': round(b64_total / 1024, 1), 'over': over},
                   ensure_ascii=False, indent=1), encoding='utf-8')
    print('体积明细 → tools/art_embed_report.json')


if __name__ == '__main__':
    main()
