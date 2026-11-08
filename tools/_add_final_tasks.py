# -*- coding: utf-8 -*-
"""把 T67 / T69 / T70 追加到队列（T68 由用户另行派发，不进队列避免重复）。"""
import json
from pathlib import Path

GAME = Path(__file__).resolve().parents[1]
Q = GAME / 'tasks' / 'queue.json'

NEW = [
    ('T67', '素材全量接入 + 体积与回归：ART 常量表、check_web 允许 data URI（仍拦外链）、1.6MB 增量预算、三主题截图'),
    ('T69', '批量补齐剩余 68 条素材：640×936、单张≤30KB、失败清单、闸门 0 命中'),
    ('T70', '终局回归：三检查器 + 200seed/500局地图 + 四职业胜率 + 10张手牌压测 + 三主题截图 + 新地图默认验证'),
]


def main():
    q = json.loads(Q.read_text(encoding='utf-8'))
    ids = {t for t, _ in NEW}
    q = [i for i in q if i['task_id'] not in ids]
    for tid, desc in NEW:
        msg = ('[%s] 读 C:/Users/Administrator/Desktop/杂七杂八/红渊/game/tasks/%s.md 并严格照做。%s。'
               '做完跑对应自检，通过后追加写 C:/Users/Administrator/Desktop/杂七杂八/红渊/game/TASK_DONE.md。'
               '不许跳步；不许为过关放宽检查器。') % (tid, tid, desc)
        q.append({'task_id': tid, 'message': msg})
    Q.write_text(json.dumps(q, ensure_ascii=False, indent=2), encoding='utf-8')
    print('queue tail:', [i['task_id'] for i in q][-6:], 'total', len(q))


if __name__ == '__main__':
    main()
