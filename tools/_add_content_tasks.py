# -*- coding: utf-8 -*-
"""把 T60-T65 追加进 tasks/queue.json（写成文件跑，避免 PowerShell 引号/反引号转义）。"""
import json
from pathlib import Path

GAME = Path(__file__).resolve().parents[1]
Q = GAME / 'tasks' / 'queue.json'

NEW = [
    ('T60', '内容缺口盘点与配额方案：算清「生态×深度带×类型」要多少条，给口径A/B两种总量与推荐'),
    ('T61', '生态敌人设计与落地：每生态普通/精英/BOSS 候选按配额生产，意图循环去重'),
    ('T62', '生态事件设计与落地：每生态母题不同，选项带代价陷阱，效果走引擎已有动作'),
    ('T63', '生态遗物 + 专属卡牌：每生态按配额生产，含 3 组 combo 与超模比值自检'),
    ('T64', '文风统一与去重：text_lint 脚本 + GLOSSARY 术语规范 + 修一轮说明书腔'),
    ('T65', '内容接入与全量回归：绑定表补全 + 500 局地图模拟 + 四职业胜率对比 + 问题清单'),
]


def main():
    q = json.loads(Q.read_text(encoding='utf-8'))
    ids = {tid for tid, _ in NEW}
    q = [i for i in q if i['task_id'] not in ids]
    for tid, desc in NEW:
        msg = ('[%s] 读 C:/Users/Administrator/Desktop/杂七杂八/红渊/game/tasks/%s.md 并严格照做。%s。'
               '做完跑对应自检，通过后追加写 C:/Users/Administrator/Desktop/杂七杂八/红渊/game/TASK_DONE.md。'
               '不许跳步；需求原文见 docs/MAPGEN_BRIEF.md，文风见 docs/STYLE_SAMPLES.md。') % (tid, tid, desc)
        q.append({'task_id': tid, 'message': msg})
    Q.write_text(json.dumps(q, ensure_ascii=False, indent=2), encoding='utf-8')
    print('queue:', [i['task_id'] for i in q])


if __name__ == '__main__':
    main()
