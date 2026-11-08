# -*- coding: utf-8 -*-
"""把 T74-T78 追加进队列并排出依赖顺序。"""
import json
from pathlib import Path

GAME = Path(__file__).resolve().parents[1]
Q = GAME / 'tasks' / 'queue.json'

ORDER = ['T74', 'T75', 'T77', 'T76', 'T78']
DESC = {
    'T74': '修复三件：生成性能（100图<2s）、深度节奏（步数≥36）、小图不挡标题',
    'T75': '可见节点显示真实类型 + 允许回返（有代价：坏事件/战斗/精英/8% BOSS）',
    'T77': '开局牌库审计：太强太无脑的牌移出初始牌库，进奖励池',
    'T76': '选项与背景视觉区分：对比度硬指标 + 类型色条',
    'T78': '开始界面重构：只给卡面 → 点开详情（左卡面右详情）→ 确认才开局',
}


def main():
    q = json.loads(Q.read_text(encoding='utf-8'))
    q = [i for i in q if i['task_id'] not in ORDER]
    for tid in ORDER:
        msg = ('[%s] 读 C:/Users/Administrator/Desktop/杂七杂八/红渊/game/tasks/%s.md 并严格照做。%s。'
               '验收断言逐条给数字/截图；素材走 web/assets 相对路径不许内联；不许为过关放宽检查器；'
               '做完追加写 TASK_DONE.md。') % (tid, tid, DESC[tid])
        q.append({'task_id': tid, 'message': msg})
    Q.write_text(json.dumps(q, ensure_ascii=False, indent=2), encoding='utf-8')
    print('tail:', [i['task_id'] for i in q][-6:], 'total', len(q))


if __name__ == '__main__':
    main()
