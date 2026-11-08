# -*- coding: utf-8 -*-
"""把 T79/T80/T81 追加进队列（顺序：提速 → 分族 → 批量生成接入）。"""
import json
from pathlib import Path

GAME = Path(__file__).resolve().parents[1]
Q = GAME / 'tasks' / 'queue.json'

ORDER = ['T80', 'T79', 'T81']
DESC = {
    'T80': '生图提速：640×936 单张从 422 秒压到 ≤60 秒（VAE fp16/force_upcast、缓存 embeds）',
    'T79': '形态族划分与逐族提示词：三类不混用、族内成员≤3、覆盖 145怪/266卡/102事件',
    'T81': '按族批量生成 + 接入：id→族→图 映射改造、闸门、抽样、三检查器',
}


def main():
    q = json.loads(Q.read_text(encoding='utf-8'))
    q = [i for i in q if i['task_id'] not in ORDER]
    for tid in ORDER:
        msg = ('[%s] 读 C:/Users/Administrator/Desktop/杂七杂八/红渊/game/tasks/%s.md 并严格照做。%s。'
               '先读 docs/ART_DIRECTION_V2.md（三档抽象度 + 复用规则 R1–R6）。'
               '验收逐条给数字；不许为过关放宽验收；素材走 web/assets 相对路径；做完追加 TASK_DONE.md。'
               % (tid, tid, DESC[tid]))
        q.append({'task_id': tid, 'message': msg})
    Q.write_text(json.dumps(q, ensure_ascii=False, indent=2), encoding='utf-8')
    print('tail:', [i['task_id'] for i in q][-5:], 'total', len(q))


if __name__ == '__main__':
    main()
