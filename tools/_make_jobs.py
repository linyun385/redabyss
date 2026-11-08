# -*- coding: utf-8 -*-
"""把 zh_prompts_full.json 按类别拆成 wanx_gen 可直接吃的任务文件。
用法：python tools/_make_jobs.py foe|evt|card
产出：data\jobs_<kind>.json  [{id, prompt}]
"""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
GAME = Path(__file__).resolve().parents[1]
P = GAME / 'data' / 'zh_prompts_full.json'


def main():
    kind = sys.argv[1] if len(sys.argv) > 1 else 'foe'
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    rows = json.loads(P.read_text(encoding='utf-8'))
    pref = {'foe': 'enemy_', 'evt': 'event_', 'card': ''}[kind]
    if kind == 'card':
        sel = [r for r in rows if not r['id'].startswith(('enemy_', 'event_'))]
    else:
        sel = [r for r in rows if r['id'].startswith(pref)]
    if limit:
        sel = sel[:limit]
    out = GAME / 'data' / ('jobs_%s.json' % kind)
    out.write_text(json.dumps([{'id': r['id'], 'prompt': r['prompt']} for r in sel],
                              ensure_ascii=False, indent=1), encoding='utf-8')
    print('写出 %s：%d 条' % (out.name, len(sel)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
