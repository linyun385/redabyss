# -*- coding: utf-8 -*-
"""把光照段里「<任意名词>下缘」统一改成「它的下缘」。
重写主体段之后，尾部常残留旧主体名（扳手／电池／手册／鳗鱼…），与新的主体描述不一致。
用法：python tools/_fix_tail2.py [--apply]
"""
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
GAME = Path(__file__).resolve().parents[1]
P = GAME / 'data' / 'zh_prompts_full.json'
SPLIT = '洞底是一整片深红的光'
# 「X的下缘」「X下缘」→「它的下缘」；最多 6 字，且排除「它」本身
PAT = re.compile(r'[\u4e00-\u9fa5A-Za-z]{1,6}(?:的)?下缘')


def main():
    apply = '--apply' in sys.argv
    rows = json.loads(P.read_text(encoding='utf-8'))
    n = 0
    for r in rows:
        p = r['prompt']
        i = p.find(SPLIT)
        if i < 0:
            continue
        head, tail = p[:i], p[i:]
        t2 = PAT.sub('它的下缘', tail)
        if t2 != tail:
            n += 1
            r['prompt'] = head + t2
    print('修尾部 %d 条' % n)
    if apply:
        P.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding='utf-8')
        print('已写入', P.name)
    else:
        print('(演练；加 --apply 才写)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
