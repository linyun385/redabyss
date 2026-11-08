# -*- coding: utf-8 -*-
"""调整队列顺序：把 T60（配额盘点）提到 T58（绑定表）之前，让内容生产先有配额依据。"""
import json
from pathlib import Path

GAME = Path(__file__).resolve().parents[1]
Q = GAME / 'tasks' / 'queue.json'

ORDER = ['T54', 'T55', 'T56', 'T57', 'T60', 'T58', 'T59', 'T61', 'T62', 'T63', 'T64', 'T65']


def main():
    q = json.loads(Q.read_text(encoding='utf-8'))
    done = [i for i in q if i['task_id'] not in ORDER]
    pending = {i['task_id']: i for i in q if i['task_id'] in ORDER}
    newq = done + [pending[t] for t in ORDER if t in pending]
    Q.write_text(json.dumps(newq, ensure_ascii=False, indent=2), encoding='utf-8')
    print('pending order:', [i['task_id'] for i in newq if i['task_id'] in ORDER])


if __name__ == '__main__':
    main()
