# -*- coding: utf-8 -*-
"""把 A/B 验证过的「无高光无灰阶」约束批量套到全部 461 条提示词尾部。

依据：2026-11-03 A/B（trem_0001 等 5 组 × 原/加约束）—— 加约束后出图从
「金属高光 + 平滑明暗的半写实渲染」变成「硬排线、黑轮廓、平涂红的版画」，
用户确认「V1 是我要的」。这条约束进正式提示词。

幂等：已经含标记句的条目跳过，重复跑安全。
用法：python tools/_apply_extra.py [--apply]
"""
import json
import shutil
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
GAME = Path(__file__).resolve().parents[1]
P = GAME / 'data' / 'zh_prompts_full.json'
MARK = '只用墨黑与血红两种色块'
EXTRA = ('整幅画只用墨黑与血红两种色块，中间没有灰阶过渡；所有表面都是哑光的，'
         '没有高光，没有反光，没有金属亮斑；形体只靠硬边轮廓和排线分开，不靠明暗塑形。')


def main():
    data = json.loads(P.read_text(encoding='utf-8'))
    todo = [r for r in data if MARK not in (r.get('prompt') or '')]
    print('总 %d 条，待加约束 %d 条，已有 %d 条' % (len(data), len(todo), len(data) - len(todo)))
    if '--apply' not in sys.argv:
        print('干跑。加 --apply 才写盘。')
        for r in todo[:3]:
            print('  样例 %s：尾部追加「%s…」' % (r['id'], EXTRA[:24]))
        return 0

    bak = P.with_suffix('.json.bak11')
    if not bak.exists():
        shutil.copy2(P, bak)
        print('备份 →', bak.name)

    n = 0
    for r in todo:
        pr = (r.get('prompt') or '').rstrip()
        if not pr:
            continue
        r['prompt'] = pr + ('。' if not pr.endswith('。') else '') + EXTRA
        n += 1
    P.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding='utf-8')

    # 复查
    data2 = json.loads(P.read_text(encoding='utf-8'))
    ok = sum(1 for r in data2 if MARK in (r.get('prompt') or ''))
    print('写入 %d 条。复查：%d / %d 已含约束句' % (n, ok, len(data2)))
    over = [r['id'] for r in data2 if (r.get('prompt') or '').count(MARK) > 1]
    print('重复追加的:', over if over else '无')
    return 0


if __name__ == '__main__':
    sys.exit(main())
