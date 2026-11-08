# -*- coding: utf-8 -*-
"""把用户发来的几张图，与 art/versions 下的备选做指纹比对，认出它们分别是哪个 id。

为什么需要：用户直接贴图问「这几张选中了吗」，图没有文件名，只能靠内容对回 id。
用 dHash（9x8 灰度差分）做最近邻，距离 0–8 基本就是同一张（重编码后仍稳）。
"""
import sys
from pathlib import Path
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')
GAME = Path(__file__).resolve().parents[1]
VERS = GAME / 'art' / 'versions'
ATT = Path(r'C:\Users\Administrator\.dsh\attachments\v1\objects')

FILES = {
    '图1 环形斑蛹': r'bf\bfb15965e8f2392c83d45c41ee16ea9239f8d32c0ae558ef03316d6e6a457153',
    '图2 长尾爬行': r'b0\b0c6631e2e1cfbc08f80d3503e7a754b40c5a19fd21b3f6275748729ff9a01fc',
    '图3 分节虫': r'5e\5ea78d9973f42737da0e28505a9cbb90fe9b022c9a2990865b6aae198d08ae67',
    '图4 带角爬行': r'c3\c31f94194b5428f0361a642d1e3095ebdddf62877fa5e3bb0c533a9972e2bdf3',
    '图5 水母状': r'4c\4ccf5ae8aef0460570ee19528d9ccc121756b075788663dcb1030e2c14bb3108',
    '图6 甲虫': r'f0\f07c9b8bbbad39d5bc5227f382f012d9f822688d5689a0fcc5781aa54b297f95',
}


def dhash(p, size=8):
    im = Image.open(p).convert('L').resize((size + 1, size), Image.LANCZOS)
    px = list(im.getdata())
    bits = []
    for r in range(size):
        for c in range(size):
            bits.append(1 if px[r * (size + 1) + c] > px[r * (size + 1) + c + 1] else 0)
    return bits


def ham(a, b):
    return sum(x != y for x, y in zip(a, b))


def main():
    targets = [(n, ATT / p) for n, p in FILES.items()]
    targets = [(n, p) for n, p in targets if p.exists()]
    if not targets:
        print('附件路径都不存在')
        return 1
    pool = []
    for f in sorted(VERS.glob('*.webp')):
        pool.append((f.stem, dhash(f)))
    # 也把现用图纳入比对
    for f in sorted((GAME / 'web' / 'assets' / 'art').glob('*.webp')):
        pool.append(('cur:' + f.stem, dhash(f)))
    print('比对池 %d 张\n' % len(pool))
    for name, p in targets:
        h = dhash(p)
        cand = sorted(((ham(h, ph), k) for k, ph in pool))[:3]
        print('%-14s → %s' % (name, ' ｜ '.join('%s(距离%d)' % (k, d) for d, k in cand)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
