# -*- coding: utf-8 -*-
"""清理尾部残留：把「鳗它的」「墟它的」这类「<单字>它的」修成「它的」。
原因：上一版正则只匹配到双字物种名的后半个字（鳗鱼→鱼、墟蟹→蟹），留下了前半个。
用法：python tools/_fix_tail.py [--apply]
"""
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
GAME = Path(__file__).resolve().parents[1]
P = GAME / 'data' / 'zh_prompts_full.json'
BAD = re.compile(r'[\u4e00-\u9fa5]它的')
ALLSPECIES = re.compile(r'蜘蛛|跳蛛|螨|甲虫|蚂蚁|蝎|蜈蚣|蟹|虾|蛇|蜥蜴|螈|蛙|蟾|鱼|鳗|水母|海葵|珊瑚|蝠|鸟|鼠|兔|猫|犬|蠕虫|蛭|蜗牛|蛞蝓|蘑菇|真菌|苔藓|蕨|藤|草|树')


def main():
    apply = '--apply' in sys.argv
    rows = json.loads(P.read_text(encoding='utf-8'))
    n = 0
    for r in rows:
        p = r['prompt']
        i = p.find('洞底是一整片深红的光')
        if i < 0:
            continue
        head, tail = p[:i], p[i:]
        t2 = BAD.sub('它的', tail)
        if t2 != tail:
            n += 1
            r['prompt'] = head + t2
    print('修复 %d 条' % n)
    left = [r['id'] for r in rows if ALLSPECIES.search(r['prompt'])]
    print('仍含物种名的 %d 条：%s' % (len(left), left[:10]))
    if apply:
        P.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding='utf-8')
        print('已写入', P.name)
    else:
        print('(演练；加 --apply 才写)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
