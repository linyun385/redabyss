# -*- coding: utf-8 -*-
"""从 T341_UNIVERSAL_JSON.md 提取零引擎改动的通用牌，追加进 cards/shared.json

用法：
  python tools\\_apply_universal.py           干跑
  python tools\\_apply_universal.py --apply   真写
"""
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
GAME = Path(__file__).resolve().parents[1]
MD = GAME / 'docs' / 'design' / 'delivery' / 'T341_UNIVERSAL_JSON.md'
SHARED = GAME / 'cards' / 'shared.json'
APPLY = '--apply' in sys.argv


def main():
    if not MD.exists():
        print('找不到', MD)
        return 2
    text = MD.read_text(encoding='utf-8')

    # 只取 §二（零引擎改动）到 §三 之间
    a = text.find('## 二、十张零引擎改动的草案')
    b = text.find('## 三、')
    if a < 0:
        print('找不到 §二')
        return 2
    seg = text[a: b if b > a else len(text)]

    blocks = re.findall(r'```json\s*\n(.*?)\n```', seg, re.S)
    print('§二 里提取到 %d 个 json 块' % len(blocks))

    cards = []
    for i, blk in enumerate(blocks, 1):
        try:
            c = json.loads(blk)
        except Exception as e:
            print('  第 %d 块解析失败：%s' % (i, e))
            print('  片段：', blk[:100].replace('\n', ' '))
            continue
        if 'id' not in c or 'name' not in c:
            print('  第 %d 块缺 id/name，跳过' % i)
            continue
        cards.append(c)

    cur = json.loads(SHARED.read_text(encoding='utf-8'))
    existing = {c['id'] for c in cur}
    print('shared.json 现有 %d 张' % len(cur))

    add = []
    for c in cards:
        if c['id'] in existing:
            print('  已存在，跳过:', c['id'], c['name'])
            continue
        add.append(c)
        print('  + %s %s  energy=%s type=%s' % (c['id'], c['name'],
                                                c.get('energy'), c.get('type')))

    print('\n待新增 %d 张；写后共 %d 张' % (len(add), len(cur) + len(add)))
    if not APPLY:
        print('[干跑] 未写。加 --apply 真写。')
        return 0

    out = cur + add
    SHARED.write_text(json.dumps(out, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print('已写入 cards/shared.json')
    return 0


if __name__ == '__main__':
    sys.exit(main())
