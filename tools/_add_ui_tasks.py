# -*- coding: utf-8 -*-
"""把 T71/T72/T73 追加进队列（T74 = 复跑 T70 终局回归）。"""
import json
from pathlib import Path

GAME = Path(__file__).resolve().parents[1]
Q = GAME / 'tasks' / 'queue.json'

NEW = [
    ('T71', '小图/总图版式重构：尺寸放大、总图改滚动、新增行程列表、格子改图标、生态配色提亮'),
    ('T72', '生态分布与权重重构：每带 2-4 生态、单带最大占比≤60%、相邻带交集≥1、过渡带'),
    ('T73', '深度带节奏重做：每带节点≥9-14、单局步数 40-70、每带到访≥4.5、BOSS 3-6 次'),
]


def main():
    q = json.loads(Q.read_text(encoding='utf-8'))
    ids = {t for t, _ in NEW}
    q = [i for i in q if i['task_id'] not in ids]
    for tid, desc in NEW:
        msg = ('[%s] 读 C:/Users/Administrator/Desktop/杂七杂八/红渊/game/tasks/%s.md 并严格照做（含里面列的验收断言，'
               '逐条给数字/截图）。做完跑自检，全绿后追加写 C:/Users/Administrator/Desktop/杂七杂八/红渊/game/TASK_DONE.md。'
               '素材已外置到 web/assets/art，不要内联；check_web 已允许站内相对路径但禁外链。不给过关放宽检查器。'
               % (tid, tid))
        q.append({'task_id': tid, 'message': msg})
    Q.write_text(json.dumps(q, ensure_ascii=False, indent=2), encoding='utf-8')
    print('queue tail:', [i['task_id'] for i in q][-5:], 'total', len(q))


if __name__ == '__main__':
    main()
