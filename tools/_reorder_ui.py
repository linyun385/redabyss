# -*- coding: utf-8 -*-
"""重排待跑顺序：T72（生态）→ T73（节奏）→ T71（版式）。"""
import json
from pathlib import Path

GAME = Path(__file__).resolve().parents[1]
Q = GAME / 'tasks' / 'queue.json'
ORDER = ['T72', 'T73', 'T71']


def main():
    q = json.loads(Q.read_text(encoding='utf-8'))
    pending = {i['task_id']: i for i in q if i['task_id'] in ORDER}
    head = [i for i in q if i['task_id'] not in ORDER]
    new = head + [pending[t] for t in ORDER if t in pending]
    Q.write_text(json.dumps(new, ensure_ascii=False, indent=2), encoding='utf-8')
    print('tail:', [i['task_id'] for i in new][-4:])


if __name__ == '__main__':
    main()
