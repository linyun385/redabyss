# -*- coding: utf-8 -*-
"""把 T66/T67（素材任务）追加到队列末尾，并把「口径 B」写进 T60 的前提。"""
import json
from pathlib import Path

GAME = Path(__file__).resolve().parents[1]
Q = GAME / 'tasks' / 'queue.json'

NEW = [
    ('T66', '素材生产管线与样张：art_manifest 清单 + diffusers 批量 + 相似度闸门 + 10 张样张送审（不接游戏）'),
    ('T67', '素材全量接入 + 体积与回归：ART 常量表、check_web 允许 data URI、体积预算、三主题截图'),
]

B_NOTE = (
    '> **口径已定（2026-10-30 18:50 用户拍板）：走口径 B —— 复用 + 带修饰。**\n'
    '> 即：每生态一批唯一内容（12–16 敌 / 8 事件 / 12 卡 / 9 遗物），深度带只调数值·词缀·精英化。\n'
    '> 口径 A（每格独有）不再作为方案，只作为对比数字保留。\n\n'
)


def main():
    q = json.loads(Q.read_text(encoding='utf-8'))
    for tid, desc in NEW:
        msg = ('[%s] 读 C:/Users/Administrator/Desktop/杂七杂八/红渊/game/tasks/%s.md 并严格照做。%s。'
               '做完跑对应自检，通过后追加写 C:/Users/Administrator/Desktop/杂七杂八/红渊/game/TASK_DONE.md。'
               '注意：T66 只出样张送审，用户点头后才做 T67。') % (tid, tid, desc)
        q = [i for i in q if i['task_id'] != tid]
        q.append({'task_id': tid, 'message': msg})

    # T60 顶部补一句口径已定
    t60 = GAME / 'tasks' / 'T60.md'
    s = t60.read_text(encoding='utf-8')
    if '口径已定' not in s:
        lines = s.split('\n')
        for i, l in enumerate(lines):
            if l.startswith('## '):
                lines.insert(i, B_NOTE.rstrip() + '\n')
                break
        t60.write_text('\n'.join(lines), encoding='utf-8')
        print('T60 已标注口径 B')

    Q.write_text(json.dumps(q, ensure_ascii=False, indent=2), encoding='utf-8')
    print('queue:', [i['task_id'] for i in q][-6:], 'total', len(q))


if __name__ == '__main__':
    main()
