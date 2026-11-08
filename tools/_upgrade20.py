# -*- coding: utf-8 -*-
"""把 zh_prompts_20.json 升级成 20b：统一换掉光照段和风格尾巴（红光加强 + 禁画框）。

截断点：提示词里第一处「洞底是一层深红的光」或「地面有深红的光」或「洞底是一层深红光」。
截断前的部分是「主体描述」，保留原样；之后整段替换成新版 RED + TAIL。
"""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
GAME = Path(__file__).resolve().parents[1]
SRC = GAME / 'data' / 'zh_prompts_20.json'
DST = GAME / 'data' / 'zh_prompts_20b.json'

RED = ('洞底是一整片深红的光，从下往上照。红光铺满画面下三分之一，整个洞底、岩壁的下半截都被染红，'
       '红色浓到发暗。光的颜色是纯正的深红，没有橙色，没有黄光。'
       '{subj}的下缘被染成朱红，上部沉入黑暗，阴影投向岩顶。暗面也带红，不是死黑。')
TAIL = ('背景留大片纯黑，但整幅画铺满整个画面，没有画框，没有边框，没有装裱，没有留白纸边。'
        '没有天空，没有地平线，没有文字。'
        '整幅画用石版画的方式绘制：细密排线，深墨轮廓，赭黄与烟灰只用在岩壁和器物上，'
        '画面的光全部是血红，红色是画面里最饱和的颜色。')

CUTS = ['洞底是一层深红的光', '地面有深红的光', '洞底是一层深红光', '光从画面下方']


def main():
    jobs = json.loads(SRC.read_text(encoding='utf-8'))
    out = []
    for j in jobs:
        p = j['prompt']
        cut = min([p.find(c) for c in CUTS if p.find(c) >= 0] or [-1])
        if cut < 0:
            print('!! 找不到光照截断点:', j['id'])
            out.append(j)
            continue
        head = p[:cut].rstrip('。；，')
        subj = '主体' if j['id'].startswith(('foe_', 'evt_')) else '这件东西'
        out.append({'id': j['id'].replace('_zh2_', '_zh3_'),
                    'prompt': head + '。' + RED.format(subj=subj) + TAIL})
    DST.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding='utf-8')
    print('写出', DST.name, len(out), '条')
    print('样例:', out[0]['prompt'][:150])
    return 0


if __name__ == '__main__':
    sys.exit(main())
