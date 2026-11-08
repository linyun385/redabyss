# -*- coding: utf-8 -*-
"""T501 敌人↔卡牌对应 → docs/design/enemy_card_map.md

判读规则（按优先级取第一条命中，可多挂副考验）：
  规则数据源：敌人的 intent_pattern + 全部 phases 里的 intent_pattern（取并集）。
  R1 穿透(pierce)攻击存在   → 考「生命缓冲/回复」，罚纯格挡（格挡被穿）→ 回答牌：回血/再生系
  R2 偷取(status=steal)     → 罚囤资源流 → 回答牌：共振锁定系、尽快结束战斗的爆发
  R3 弃牌抽取(drain_discard)→ 罚依赖手牌/牌库运营 → 回答牌：抽牌引擎、卡组瘦身
  R4 多段(times>=2)攻击     → 考单回合高格挡/多段格挡，罚低格挡 → 回答牌：大格挡、荆棘
  R5 单发大攻击(>=12)       → 考爆发斩杀（杀不掉就挨重锤）→ 回答牌：斩杀位、虚弱
  R6 防御意图占比 >=40%     → 考破防，罚纯单段直伤 → 回答牌：多段、灼烧、易伤
  R7 buff 次数 >=2          → 考速杀，罚拖延 → 回答牌：爆发、灼烧
  R8 都不中                 → 考基本功（格挡+直伤循环）

数值证据全部写进行内（如 pierce/steal/12点），统计节由脚本汇总。

用法：python data/audit/gen_t501.py
"""
import io, sys
from pathlib import Path
from collections import Counter
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_common import GAME

OUT = GAME / 'docs' / 'design' / 'enemy_card_map.md'
RAW = __import__('json').load(open(GAME / 'data' / 'audit' / 'raw_all.json', encoding='utf-8'))

CN_TIER = {'normal': '普通', 'elite': '精英', 'boss': 'boss'}
CN_POOL = {'enemies': '通用池', 'anminEnemies': '维护者池', 'cngEnemies': '疯先知池'}
ANSWER = {
    'R1': '回血/再生系（如 dive_0032 曜元（缓释）、cng_0036 归乡）——格挡对穿透无效，只能用生命缓冲',
    'R2': '共振锁定系（dive_0016 / trem_0019 / anm_0020）防被偷，或速战速决不给它偷的机会',
    'R3': '抽牌引擎（dive_0053 备用电源、cng_0033 昴宿低语）+ 卡组瘦身（trem_0022 回归墟骨）',
    'R4': '大格挡（cng_0020 城墙梦、trem_0045 埋骨礼（合葬））或荆棘反打（dive_0065 接地缆）',
    'R5': '斩杀位（dive_0012 轨道炮支援、cng_0040 墟语）+ 减攻（dive_0030 镇爆弹的虚弱）',
    'R6': '多段（dive_0024 钻探平台、trem_0010 震语：三震）或灼烧/易伤（dive_0034 焚烧记录、dive_0022 硬矿钻（重型））',
    'R7': '爆发速杀（dive_0046 深部震源、trem_0023 震语：沸息）——拖得越久它越强',
    'R8': '基本功：一条格挡基准牌 + 一条直伤基准牌（如 anm_0004 + anm_0002）就能过',
}

def collect_intents(e):
    its = list(e.get('intent_pattern') or [])
    for ph in e.get('phases') or []:
        its.extend(ph.get('intent_pattern') or [])
    return its

def classify(e):
    its = collect_intents(e)
    atks = [i for i in its if i.get('type') == 'attack']
    defs = [i for i in its if i.get('type') == 'defend']
    buffs = [i for i in its if i.get('type') == 'buff']
    debuffs = [i for i in its if i.get('type') == 'debuff']
    multi = [i for i in atks if (i.get('times') or 1) >= 2]
    pierce = [i for i in atks if i.get('pierce')]
    steal = [i for i in debuffs if i.get('status') == 'steal']
    drain = [i for i in atks if i.get('drain_discard')]
    max_atk = max([i.get('value') or 0 for i in atks] + [0])
    def_ratio = len(defs) / len(its) if its else 0
    tags, ev = [], []
    if pierce:
        tags.append('R1'); ev.append('穿透攻击 %s 点' % '/'.join(str(i.get('value')) for i in pierce))
    if steal:
        tags.append('R2'); ev.append('偷取(status=steal)')
    if drain:
        tags.append('R3'); ev.append('从弃牌堆取音/取牌攻击')
    if multi:
        tags.append('R4'); ev.append('多段攻击 %s' % ['%s点x%s' % (i.get('value'), i.get('times')) for i in multi])
    if max_atk >= 12:
        tags.append('R5'); ev.append('单发最高 %s 点' % max_atk)
    if def_ratio >= 0.4 and defs:
        tags.append('R6'); ev.append('防御意图 %d/%d' % (len(defs), len(its)))
    if len(buffs) >= 2:
        tags.append('R7'); ev.append('增益 %d 次' % len(buffs))
    if not tags:
        tags.append('R8')
    if debuffs and not steal:
        ev.append('附加减益 ' + ','.join(i.get('status') or '?' for i in debuffs))
    return tags, ev, max_atk

buf = io.StringIO()
buf.write('# T501 · 敌人 ↔ 卡牌对应（每只敌人在考什么、罚什么）\n\n')
buf.write('> 数据源：`web/index.html` 行 6401 `const RAW` 的 `enemies`(113) + `anminEnemies`(16) + `cngEnemies`(16) = **145 只**，')
buf.write('经 node 抽出缓存于 `data/audit/raw_all.json`。\n')
buf.write('> 判读规则 R1–R8 见文末，按优先级取主考验（行内加粗），其余命中作附加；所有规则基于敌人意图数据的机械判读，可复算。\n\n')

all_rows = []
for pool in ['enemies', 'anminEnemies', 'cngEnemies']:
    for e in RAW[pool]:
        e['_pool'] = pool
        all_rows.append(e)

buf.write('## 逐层表\n\n')
stat_main = Counter()
stat_sub = Counter()
for layer in range(1, 9):
    rows = [e for e in all_rows if e['layer'] == layer]
    buf.write('### 第 %d 层（%d 只）\n\n' % (layer, len(rows)))
    buf.write('| id | 名字 | 等级 | 池 | 血量 | 主考验（罚什么） | 附加 | 该带的牌 |\n|---|---|---|---|---|---|---|---|\n')
    for e in sorted(rows, key=lambda x: {'normal': 0, 'elite': 1, 'boss': 2}[x['tier']]):
        tags, ev, max_atk = classify(e)
        main = tags[0]
        stat_main[main] += 1
        stat_sub.update(tags[1:])
        sub = '、'.join(tags[1:]) if len(tags) > 1 else '—'
        buf.write('| %s | %s | %s | %s | %s | **%s**（%s） | %s | %s |\n' % (
            e['id'], e['name'], CN_TIER[e['tier']], CN_POOL[e['_pool']], e['hp'],
            main, '；'.join(ev) if ev else '—', sub, ANSWER[main]))

buf.write('\n## 统计\n\n')
buf.write('| 考验 | 主考验敌人数 | 附加出现数 | 一句话 |\n|---|---|---|---|\n')
desc = {
    'R1': '穿透穿透格挡——纯格挡流的天敌',
    'R2': '偷资源——共振/凝视流必须带锁定或速杀',
    'R3': '抽弃牌攻击——惩罚不管理牌库的玩家',
    'R4': '多段攻击——考单回合格挡上限',
    'R5': '大单发——考斩杀速度',
    'R6': '爱防御——考破防手段（多段/灼烧/易伤）',
    'R7': '爱增益——考速杀',
    'R8': '基本功——格挡+直伤循环就够',
}
for k in ['R8', 'R4', 'R5', 'R6', 'R7', 'R1', 'R2', 'R3']:
    buf.write('| %s | %d | %d | %s |\n' % (k, stat_main[k], stat_sub[k], desc[k]))
buf.write('\n合计：%d 只敌人。\n\n' % len(all_rows))

buf.write('## 判读规则（复算用）\n\n')
buf.write('1. 取敌人 `intent_pattern` 与全部 `phases[].intent_pattern` 的并集。\n')
buf.write('2. R1：存在 `pierce` 攻击；R2：存在 `status=steal` 的 debuff；R3：存在 `drain_discard` 攻击；\n')
buf.write('   R4：存在 `times>=2` 的攻击；R5：最大攻击值 ≥12；R6：防御意图占比 ≥40%；R7：buff ≥2 次；R8：兜底。\n')
buf.write('3. 主考验 = 命中规则中编号最小者；表内数字全部来自意图原始数据。\n')
buf.write('4. 复算：`python data/audit/gen_t501.py`。\n')
buf.write('\n### 观察一句\n\n')
top = stat_main.most_common(2)
buf.write('被打得最多的两种打法：**%s**。' % '、'.join('%s（%s%d 只）' % (k, desc[k][0:14], n) for k, n in top))
buf.write('R8 基本功敌人占 %d 只，说明前期主要在考「会挡、会打」；越往后 R1/R2/R5 这类针对性考验越多。\n' % stat_main['R8'])

OUT.write_text(buf.getvalue(), encoding='utf-8')
print('written', OUT, len(all_rows), 'enemies; main:', dict(stat_main))
