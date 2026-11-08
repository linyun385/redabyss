# -*- coding: utf-8 -*-
"""从敌人批里挑出要重跑的 id，生成 data/jobs_foe_rerun.json。

来源：tools/_check_foe_art.py 的红/亮体检（36 张可疑）→ 拼 art/_review20/sheet_bad2.png 人眼过一遍。
分两类：
  A 类 提示词已重写（跑成现实物种 / 跑成纸类）—— 见 tools/_fix_foe7.py
  B 类 提示词不动，问题在构图：主体不在画面里、太小、跑成剪影/人体/植物
"""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
GAME = Path(__file__).resolve().parents[1]
P = GAME / 'data' / 'zh_prompts_full.json'
OUT = GAME / 'data' / 'jobs_foe_rerun.json'

A = ['enemy_d6_03', 'enemy_d3_03', 'enemy_d2_01', 'enemy_d5_07',
     'enemy_d4_05', 'enemy_d4_02', 'enemy_d8_08']
B = ['enemy_d4_08', 'enemy_d1_08', 'enemy_d5_e3', 'enemy_d1_b1', 'enemy_d8_05',
     'enemy_d7_05', 'enemy_d7_01', 'enemy_d4_09', 'enemy_d8_03', 'enemy_d4_03',
     'enemy_d1_e3', 'enemy_d2_04', 'enemy_d6_01', 'enemy_d1_05', 'enemy_d2_09',
     'enemy_d4_10', 'enemy_d8_11']


def main():
    rows = {r['id']: r['prompt'] for r in json.loads(P.read_text(encoding='utf-8'))}
    jobs, miss = [], []
    for rid in A + B:
        if rid not in rows:
            miss.append(rid)
            continue
        jobs.append({'id': rid, 'prompt': rows[rid]})
    OUT.write_text(json.dumps(jobs, ensure_ascii=False, indent=1), encoding='utf-8')
    print('写出 %s：%d 条（A 类 提示词已改 %d / B 类 只重摇 %d）缺 %s'
          % (OUT.name, len(jobs), len(A), len(B), miss))
    return 0


if __name__ == '__main__':
    sys.exit(main())
