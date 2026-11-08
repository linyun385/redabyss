# -*- coding: utf-8 -*-
"""给主体段涉及文字的提示词补一句「文字模糊成墨痕」，避免模型在画面上写出乱码字。
只补一次（幂等）。用法：python tools/_patch_text_rule.py [--apply]
"""
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
GAME = Path(__file__).resolve().parents[1]
P = GAME / 'data' / 'zh_prompts_full.json'
MARK = '看不清任何一个字'
ADD = '画面里出现的纸张、牌子、册子、告示上只有模糊的墨痕，看不清任何一个字。'
PAT = re.compile(r'字|写着|笔迹|名单|告示|协议|名册|表格|登记')


def main():
    apply = '--apply' in sys.argv
    rows = json.loads(P.read_text(encoding='utf-8'))
    hit = []
    for r in rows:
        p = r['prompt']
        if MARK in p:
            continue
        i = p.find('洞底是一整片深红的光')
        head = p[:i] if i > 0 else p
        if not PAT.search(head):
            continue
        if i > 0:
            r['prompt'] = head + ADD + p[i:]
        else:
            r['prompt'] = p.rstrip('。') + '。' + ADD
        hit.append(r['id'])
    print('需要补的 %d 条' % len(hit))
    for i in hit[:8]:
        print('  -', i)
    if apply:
        P.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding='utf-8')
        print('已写入 %s' % P.name)
    else:
        print('(演练；加 --apply 才写)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
