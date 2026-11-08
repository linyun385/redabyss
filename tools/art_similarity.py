# -*- coding: utf-8 -*-
"""T66 版权闸门：生成图 vs 密教参考图（只读、不复制）做感知哈希比对。

- dHash 9x8 → 64 bit（梯度方向鲁棒，缩放/亮度不敏感）
- 参考图：C:\\Users\\Administrator\\Desktop\\杂七杂八\\红渊\\密教图片素材（对照风格用）\\
  （43 张全量比对，比任务书的 25 张 A 组更严格）
- 阈值写死：汉明距离 ≤ 6 视为过近 → 弃用重生成（换 seed）。
  依据：dHash 64bit 随机图对的汉明距离近似二项分布（均值 32、σ≈4）；≤6 是
  8σ 之外，正常独立生成不可能命中；而构图/配色被模型「背下来」时会显著
  低于 20。取 6 而不是 10 是宁可误杀——样张阶段产量小，重生成成本可控。
- 用法：python tools/art_similarity.py            # 扫 art/ 下全部生成图
        python tools/art_similarity.py --out <单个文件>   # 单图快查
"""
import argparse
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
ART = ROOT / 'art'
REF_DIR = Path(r'C:\Users\Administrator\Desktop\杂七杂八\红渊\密教图片素材（对照风格用）')
THRESHOLD = 6   # 汉明距离 ≤ 6 → 过近，弃用


def dhash(img, hash_size=8):
    g = img.convert('L').resize((hash_size + 1, hash_size), Image.LANCZOS)
    px = list(g.getdata())
    rows = [px[i * (hash_size + 1):(i + 1) * (hash_size + 1)] for i in range(hash_size)]
    bits = []
    for row in rows:
        for i in range(hash_size):
            bits.append(1 if row[i] > row[i + 1] else 0)
    v = 0
    for b in bits:
        v = (v << 1) | b
    return v


def hamming(a, b):
    return bin(a ^ b).count('1')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='')
    args = ap.parse_args()

    refs = []
    for p in sorted(REF_DIR.iterdir()):
        if p.suffix.lower() not in ('.png', '.jpg', '.jpeg', '.webp'):
            continue
        try:
            refs.append((p.name, dhash(Image.open(p))))
        except Exception as ex:
            print(f'[warn] 参考图读不了 {p.name}: {ex}')
    print(f'参考图 {len(refs)} 张（阈值 hamming ≤ {THRESHOLD}）')

    targets = [args.out] if args.out else \
        [str(p) for p in sorted(ART.rglob('*.webp'))]

    results = []
    rejects = 0
    for t in targets:
        h = dhash(Image.open(t))
        best = min(((hamming(h, rh), name) for name, rh in refs), default=(999, ''))
        status = 'REJECT' if best[0] <= THRESHOLD else 'ok'
        if status == 'REJECT':
            rejects += 1
        results.append({'file': str(t), 'ref': best[1], 'hamming': best[0], 'status': status})
        print(f'[{status}] {Path(t).name}  最近参考 {best[1]}  d={best[0]}')

    rep = {'threshold': THRESHOLD, 'refs': len(refs), 'checked': len(results),
           'rejects': rejects, 'results': results}
    (ROOT / 'tools' / 'art_similarity.json').write_text(
        json.dumps(rep, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'命中(过近) {rejects} / {len(results)}，明细在 tools/art_similarity.json')
    raise SystemExit(1 if rejects else 0)


if __name__ == '__main__':
    main()
