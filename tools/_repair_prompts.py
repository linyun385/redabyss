# -*- coding: utf-8 -*-
"""修补 zh_prompts_full.json：
  ① 模型把「（后接红光段与画法段）」当文字写出来的 → 截掉占位符 + 补全红光段与画法段
  ② 完全缺红光段/画法段的 → 在正文末尾补上
不改动已有完整段落；只做拼接，不重新调模型。
"""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
GAME = Path(__file__).resolve().parents[1]
P = GAME / 'data' / 'zh_prompts_full.json'

RED_KEY = '洞底是一整片深红的光'
RED = ('洞底是一整片深红的光，从下往上照。红光铺满画面下三分之一，整个洞底、岩壁的下半截都被染红，'
       '红色浓到发暗。光的颜色是纯正的深红，没有橙色，没有黄光。'
       'X的下缘被染成朱红，上部沉入黑暗，阴影投向岩顶。暗面也带红，不是死黑。')
TAIL = ('背景留大片纯黑，但整幅画铺满整个画面，没有画框，没有边框，没有装裱，没有留白纸边。'
        '没有天空，没有地平线，没有文字。'
        '整幅画用石版画的方式绘制：细密排线，深墨轮廓，赭黄与烟灰只用在岩壁和器物上，'
        '画面的光全部是血红，红色是画面里最饱和的颜色。')
PLACEHOLDERS = ['（后接红光段与画法段）', '(后接红光段与画法段)', '（后接红光段）', '（其余同上）']


def subject_of(head):
    """从主体句里找主体称呼：取「这/那」后面的短语，找不到就用「主体」。"""
    for key in ['这个', '这只', '这条', '这根', '这块', '这具', '这盘', '这台', '这把', '这丛', '这团']:
        i = head.find(key)
        if i >= 0:
            seg = head[i:i + 14]
            for stop in ['是画面的主体', '倒挂', '挂在', '蹲', '趴', '躺', '蜷', '悬', '横', '贴']:
                j = seg.find(stop)
                if j > 0:
                    return seg[len(key):j].strip('，。 ') or '主体'
    return '主体'


def main():
    rows = json.loads(P.read_text(encoding='utf-8'))
    fixed = 0
    for r in rows:
        p = r['prompt']
        if RED_KEY in p and '没有画框' in p and '石版画的方式绘制' in p:
            continue
        for ph in PLACEHOLDERS:
            p = p.replace(ph, '')
        # 截到红光段之前（若已有一段不完整的红光描述）
        i = p.find(RED_KEY)
        if i > 0:
            p = p[:i]
        p = p.rstrip('，。；、 ')
        subj = subject_of(p)
        r['prompt'] = p + '。' + RED.replace('X', subj) + TAIL
        fixed += 1
    P.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding='utf-8')
    print('修补 %d 条，总 %d 条' % (fixed, len(rows)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
