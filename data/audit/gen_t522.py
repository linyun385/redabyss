# -*- coding: utf-8 -*-
"""T522 敌人意图可预测性 → docs/design/intent_predictability.md

引擎事实（先摆证据）：
  `engine/core.js:695` `const intent = pat[e.intentIdx % pat.length]` —— 意图是**固定循环**，无随机；
  `engine/core.js:723` 换阶段时 `e.intentIdx = 0` —— 阶段切换重置循环，但阶段本身由血量阈值触发（同样确定）。
结论：**全部 145 只敌人在机械口径上都是「完全可算」**。
体感分档（代理口径，写明）：记忆负担 = 循环长度 + 阶段数；
  完全可算（易记）：循环 ≤3 且无 phases；大致能猜：循环 4~5 或 1 次 phases；要记的：循环 ≥6 或多 phases。
复算：python data/audit/gen_t522.py

用法：python data/audit/gen_t522.py
"""
import io, sys, json
from pathlib import Path
from collections import Counter
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_common import GAME

OUT = GAME / 'docs' / 'design' / 'intent_predictability.md'
RAW = json.load(open(GAME / 'data' / 'audit' / 'raw_all.json', encoding='utf-8'))
POOL = [('enemies', '通用'), ('anminEnemies', '维护者'), ('cngEnemies', '疯先知')]
CN_TIER = {'normal': '普通', 'elite': '精英', 'boss': 'boss'}

rows = []
for pk, pn in POOL:
    for e in RAW[pk]:
        L = len(e.get('intent_pattern') or [])
        P = len(e.get('phases') or [])
        if P == 0 and L <= 3:
            tier = '完全可算（易记）'
        elif P <= 1 and L <= 5:
            tier = '大致能猜'
        else:
            tier = '要记的'
        rows.append((e, pn, L, P, tier))

c = Counter(t[4] for t in rows)
buf = io.StringIO()
buf.write('# T522 · 敌人意图可预测性\n\n')
buf.write('> **引擎证据**：`engine/core.js:695` `pat[e.intentIdx % pat.length]`——意图固定循环，无随机；')
buf.write('`:723` 换阶段时循环归零；阶段由血量阈值触发（同样确定）。\n')
buf.write('> **机械口径结论：145 只敌人全部「完全可算」**——不存在随机意图。\n')
buf.write('> 体感分档是「记忆负担」代理：循环 ≤3 且无阶段=易记；4~5 或 1 次阶段=大致能猜；≥6 或多阶段=要记的。')
buf.write('复算：`python data/audit/gen_t522.py`。\n\n')

buf.write('## 分布\n\n| 体感档 | 只数 |\n|---|---|\n')
for k in ['完全可算（易记）', '大致能猜', '要记的']:
    buf.write('| %s | %d |\n' % (k, c[k]))
buf.write('\n## 逐只表\n\n| id | 名字 | 层 | 等级 | 循环长度 | 阶段数 | 体感档 |\n|---|---|---|---|---|---|---|\n')
for e, pn, L, P, tier in rows:
    buf.write('| %s | %s | %s | %s | %d | %d | %s |\n' % (
        e['id'], e['name'], e['layer'], CN_TIER[e['tier']], L, P, tier))

buf.write('\n## 判断\n\n')
buf.write('- 本游戏**没有随机意图**——所有敌人都按谱出招，玩家的可计算性在引擎层被保证了。\n')
buf.write('- 需要记住的是 boss：多阶段 + 每阶段重置循环。boss 战的「学谱」成本明显高于普通敌——这是设计上的难度梯度，不是随机性。\n')
buf.write('- 体感上「完全随机」的档为 0——如果玩测中玩家报告「随机感」，来源不是意图系统，可能是多敌人同场时每只各自循环叠加造成的混合节奏。\n')

OUT.write_text(buf.getvalue(), encoding='utf-8')
print('written', OUT, dict(c))
