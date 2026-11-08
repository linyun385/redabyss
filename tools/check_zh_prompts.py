# -*- coding: utf-8 -*-
"""机械校验 zh_prompts_full.json：红光段 / 主体段 / 排除句是否齐全，主体段有没有集合名词。"""
import json
import random
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
GAME = Path(__file__).resolve().parents[1]
P = GAME / 'data' / 'zh_prompts_full.json'

RED = '洞底是一整片深红的光'
NEED = [RED, '是画面的主体，占满画面中部', '没有画框，没有边框',
        '整幅画用石版画的方式绘制']
BAN = ['一片', '一丛', '一群', '一些']
HEAD_MIN = 60


def head(p):
    i = p.find(RED)
    return p[:i] if i > 0 else p


def main():
    rows = json.loads(P.read_text(encoding='utf-8'))
    bad = []
    for r in rows:
        p = r['prompt']
        miss = [n for n in NEED if n not in p]
        h = head(p)
        ban = [b for b in BAN if b in h]
        probs = []
        if miss:
            probs.append('缺段:' + '/'.join(miss))
        if ban:
            probs.append('集合名词:' + '/'.join(ban))
        if len(h) < HEAD_MIN:
            probs.append('主体段太短:%d字' % len(h))
        if re.search(r'[（(]\s*[\u4e00-\u9fa5]+:[\d.]+\s*[)）]', p):
            probs.append('带了权重括号')
        if probs:
            bad.append((r['id'], r.get('name', ''), probs))

    print('总数 %d，通过 %d，有问题 %d' % (len(rows), len(rows) - len(bad), len(bad)))
    for i, (rid, nm, pr) in enumerate(bad[:25], 1):
        print(' %2d. %-14s %-10s %s' % (i, rid, nm, ' | '.join(pr)))
    if len(bad) > 25:
        print(' ...还有 %d 条' % (len(bad) - 25))

    print('\n--- 抽 5 条主体段 ---')
    for r in random.Random(7).sample(rows, 5):
        print('\n[%s %s] %s' % (r['id'], r.get('name', ''), r.get('family', '')))
        print(head(r['prompt']))
    return 0


if __name__ == '__main__':
    sys.exit(main())
