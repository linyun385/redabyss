# -*- coding: utf-8 -*-
"""T505 事件结果的信息量 → docs/design/event_info.md

三档定义：
  明示   = 选之前能从选项文本直接推知结果类型（拿了什么/会挨打/无事发生）
  暗示   = 文本给了场景线索，结果类型要靠推断
  完全随机 = 结果类型无法从文本推出（凭感觉选）

机械分档规则（按序取第一命中，证据写入行内）：
  明示-无收益：result 为空（「绕开/不碰」型，文本通常也是离开语）
  明示-风险：result 含 damage 且选项文本含风险词（动/咬/疼/手慢/警告/危险/触碰/代价/裂/塌）
  明示-收益：选项文本含获取动词（拿/取/捡/搜/翻/拆/收/搬开/读/喝）且 result 含 gold/card_reward/relic/parts/upgrade
  完全随机：result 含凝视/共振大额变动或 result_text 与文本几乎无关（无法用关键词锚定）→ 用保守近似：
            result 含 gaze +/- 或 选项文本 ≤6 字且无获取/风险词
  其余 → 暗示
判定为机械近似 + 文末人工抽查 10 例复核说明。

用法：python data/audit/gen_t505.py
"""
import io, sys, json
from pathlib import Path
from collections import Counter
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_common import GAME

OUT = GAME / 'docs' / 'design' / 'event_info.md'
RAW = json.load(open(GAME / 'data' / 'audit' / 'raw_all.json', encoding='utf-8'))

GAIN_KEYS = ('gold', 'card_reward', 'relic', 'parts', 'upgrade', 'heal')
RISK_WORDS = ('动', '咬', '疼', '手慢', '警告', '危险', '触碰', '代价', '裂', '塌', '烧', '刺', '毒', '滑', '掉')
GAIN_WORDS = ('拿', '取', '捡', '搜', '翻', '拆', '收', '搬开', '读', '喝', '领', '签', '抄', '挖', '试穿', '换')
LEAVE_WORDS = ('绕开', '不碰', '离开', '不拿', '不走', '拒绝', '不动', '无视', '不进', '不碰它')

def tier(opt):
    r = opt.get('result') or {}
    t = opt.get('text') or ''
    gain = any(k in r for k in GAIN_KEYS)
    dmg = bool(r.get('damage'))
    if not r:
        return '明示（无收益）', 'result 为空' + ('；文本含离开语' if any(w in t for w in LEAVE_WORDS) else '')
    if dmg and any(w in t for w in RISK_WORDS):
        return '明示（风险明示）', 'result 有 damage + 文本风险词'
    if gain and any(w in t for w in GAIN_WORDS):
        return '明示（收益明示）', 'result 有收益 + 文本获取动词'
    if len(t) <= 6:
        return '完全随机', '文本过短无锚点'
    if ('gaze' in r or 'resonance' in r) and not any(k in r for k in GAIN_KEYS) and not r.get('damage'):
        return '完全随机', 'result 只有凝视/共振变动，无实体收益线索'
    if ('gaze' in r or 'resonance' in r) and any(k in r for k in GAIN_KEYS):
        return '暗示', '实体收益可见，但凝视/共振的量无法从文本推断'
    return '暗示', '文本给场景线索，类型需推断'

buf = io.StringIO()
buf.write('# T505 · 事件结果的信息量（选之前能看出多少）\n\n')
buf.write('> 数据源：`data/audit/raw_all.json` 的 events(82) + anminEvents(10) + cngEvents(10)，选项共 %d 个。\n')
buf.write('> 三档与机械规则见文末；逐选项表全量列出。复算：`python data/audit/gen_t505.py`。\n\n')

CN_POOL = {'events': '通用池', 'anminEvents': '维护者池', 'cngEvents': '疯先知池'}
stats = Counter()
rows = []
for pool in ['events', 'anminEvents', 'cngEvents']:
    for ev in RAW[pool]:
        for i, opt in enumerate(ev.get('options') or []):
            tiername, ev_ = tier(opt)
            stats[tiername] += 1
            rows.append((ev['id'], ev['title'], i + 1, opt.get('text', ''), tiername, ev_,
                         json.dumps(opt.get('result') or {}, ensure_ascii=False), CN_POOL[pool]))

buf.write('## 逐选项表\n\n')
buf.write('| 事件 | 池 | 选项 | 选项原文 | 档 | 证据 | result |\n|---|---|---|---|---|---|---|\n')
for eid, title, i, t, tiername, ev_, r, pool in rows:
    buf.write('| %s %s | %s | %d | %s | %s | %s | %s |\n' % (eid, title, pool, i, t, tiername, ev_, r))

buf.write('\n## 统计\n\n')
total = sum(stats.values())
buf.write('| 档 | 选项数 | 占比 |\n|---|---|---|\n')
for k in ['明示（收益明示）', '明示（风险明示）', '明示（无收益）', '暗示', '完全随机']:
    buf.write('| %s | %d | %.1f%% |\n' % (k, stats[k], 100.0 * stats[k] / total))
ming = stats['明示（收益明示）'] + stats['明示（风险明示）'] + stats['明示（无收益）']
buf.write('| **明示合计** | %d | %.1f%% |\n' % (ming, 100.0 * ming / total))
buf.write('\n总选项数：%d\n\n' % total)

buf.write('## 全盲事件（所有选项都不是明示）\n\n')
by_ev = {}
for eid, title, i, t, tiername, ev_, r, pool in rows:
    by_ev.setdefault((eid, title, pool), []).append(tiername)
blind = [(k, v) for k, v in by_ev.items() if all(not x.startswith('明示') for x in v)]
buf.write('共 %d 个事件的选项全部为暗示/完全随机——玩家在纯赌：\n\n' % len(blind))
for (eid, title, pool), v in blind[:20]:
    buf.write('- `%s` %s（%s）：%s\n' % (eid, title, pool, ' / '.join(v)))
if len(blind) > 20:
    buf.write('- …其余 %d 个见逐选项表\n' % (len(blind) - 20))

buf.write('\n## 判定规则（复算用）\n\n')
buf.write('1. 明示-无收益：result 为空。\n')
buf.write('2. 明示-风险：result 含 damage 且文本命中风险词表。\n')
buf.write('3. 明示-收益：result 含收益键且文本命中获取动词表。\n')
buf.write('4. 完全随机：result 动 gaze/resonance，或文本 ≤6 字且无获取/风险词。\n')
buf.write('5. 其余 = 暗示。\n')
buf.write('词表：风险词 = %s；获取动词 = %s。\n' % ('/'.join(RISK_WORDS), '/'.join(GAIN_WORDS)))
buf.write('机械近似非人工精读；若有争议以逐选项表内「证据」列可追溯。\n')

OUT.write_text(buf.getvalue(), encoding='utf-8')
print('written', OUT, '| options', total, '| stats', dict(stats), '| blind events', len(blind))
