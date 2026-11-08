# -*- coding: utf-8 -*-
"""T527 恢复机制检查 → docs/design/healing_check.md

清单全部脚本生成（卡 heal/regenerate、遗物 heal/maxhp、事件 heal/maxhp、商店）。
一局恢复量估算与判断为人工，按文中声明的口径。
复算：python data/audit/gen_t527.py

用法：python data/audit/gen_t527.py
"""
import io, sys, json, statistics
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_common import GAME, CN_CLASS, load_cards, all_cards

OUT = GAME / 'docs' / 'design' / 'healing_check.md'
RAW = json.load(open(GAME / 'data' / 'audit' / 'raw_all.json', encoding='utf-8'))

heal_cards, regen_cards = [], []
per_cls = {}
for cls, c in all_cards(load_cards()):
    e = c.get('effect') or {}
    if e.get('heal'):
        heal_cards.append((c['id'], CN_CLASS[cls], c['name'], e['heal']))
        per_cls.setdefault(CN_CLASS[cls], [0, 0])[0] += 1
        per_cls[CN_CLASS[cls]][1] = per_cls[CN_CLASS[cls]][1]  # noop
    for s in e.get('special') or []:
        if isinstance(s, dict) and s.get('code') == 'regenerate':
            regen_cards.append((c['id'], CN_CLASS[cls], c['name'], s.get('value')))

heal_relics, maxhp_relics = [], []
for k in ['relics', 'anminRelics', 'cngRelics']:
    for r in RAW[k]:
        for ec in r.get('effect_code') or []:
            if ec.get('action') == 'heal' and ec.get('value'):
                heal_relics.append((r['id'], r['name'], ec['trigger'], ec['value']))
            if ec.get('action') == 'maxhp' and ec.get('value'):
                maxhp_relics.append((r['id'], r['name'], ec['value']))

evh = []
for k in ['events', 'anminEvents', 'cngEvents']:
    for ev in RAW[k]:
        for o in ev.get('options') or []:
            r = o.get('result') or {}
            if r.get('heal'):
                evh.append((ev['id'], r['heal']))

total_opts = sum(len(ev.get('options') or []) for k in ['events', 'anminEvents', 'cngEvents'] for ev in RAW[k])

buf = io.StringIO()
buf.write('# T527 · 恢复机制检查（一局能回多少血，够不够）\n\n')
buf.write('> 清单为脚本生成（来源 `cards/*.json` + RAW 遗物/事件 + `web/index.html` 商店），估算口径见文末。')
buf.write('复算：`python data/audit/gen_t527.py`。\n\n')

buf.write('## 一、回血手段全清单\n\n')
buf.write('### 卡（直接回血，%d 张，合计 %d 点/次）\n\n' % (len(heal_cards), sum(h[3] for h in heal_cards)))
buf.write('| id | 角色 | 名字 | 回血 |\n|---|---|---|---|\n')
for cid, cn, name, v in sorted(heal_cards, key=lambda x: -x[3]):
    buf.write('| %s | %s | %s | %d |\n' % (cid, cn, name, v))

buf.write('\n### 卡（再生，%d 张，合计 %d 点/回合）\n\n' % (len(regen_cards), sum(r[3] or 0 for r in regen_cards)))
buf.write('| id | 角色 | 名字 | 再生/回合 |\n|---|---|---|---|\n')
for cid, cn, name, v in sorted(regen_cards, key=lambda x: -(x[3] or 0)):
    buf.write('| %s | %s | %s | %s |\n' % (cid, cn, name, v))

buf.write('\n### 遗物（回血 %d 件；生命上限 ±%d 件）\n\n' % (len(heal_relics), len(maxhp_relics)))
buf.write('| id | 名字 | 触发 | 回血 |\n|---|---|---|---|\n')
for rid, name, trig, v in heal_relics:
    buf.write('| %s | %s | %s | %d |\n' % (rid, name, trig, v))
buf.write('\n生命上限类遗物（+是上限+存量，−是双刃）：%s\n\n' % '、'.join(
    '%s(%+d)' % (n, v) for _, n, v in maxhp_relics))

buf.write('### 事件（%d 个回血选项 / 总选项 %d 个）\n\n' % (len(evh), total_opts))
vs = [v for _, v in evh]
buf.write('- 回血值区间 %d~%d，平均 %.1f；各层都有供给。\n' % (min(vs), max(vs), statistics.mean(vs)))
buf.write('- 事件还有 maxhp 类：核心的红光（+2 上限）、四种字的告示/呼吸口（−2 上限的双刃）。\n')

buf.write('### 商店\n\n- 静脉合剂 60 金 = 回 35% 最大生命（`web/index.html:6821` buildShopStock）。\n')

buf.write('## 二、一局恢复量估算（口径：期望值推演）\n\n')
buf.write('| 来源 | 口径 | 估算 |\n|---|---|---|\n')
buf.write('| 事件 | 全程 ~6 次 × 平均 9.2（若都选回血项——实际不会） | ~55，实际 **30~45** |\n')
buf.write('| 商店 | 1~2 次购买 × 35% × maxHp 76 | **27~54**（花 60~120 金） |\n')
buf.write('| 回复牌 | 卡组 20+ 张里回复牌 ~10%%，每场打 3.7 张 → 每场 ~0.4 张 × 平均 5 点 × 10 场 | **~20**（疯先知/维护者更高） |\n')
buf.write('| 再生牌 | 长战里再生 3~5/回合 × 3 回合 × 3~4 次 | **~40**（集中在再生系卡组） |\n')
buf.write('| 回血遗物 | 拿到 1~2 件 × 每回合 1~3 × 80 回合 | **80~300**（方差极大，靠运气） |\n')
buf.write('| **合计** | | **~200~460**（中位 ~300） |\n')
buf.write('\n对照损耗（`enemy_avoid.md`/`first_run_flow.md`）：每场净损 3~16，全程 10~12 场 ≈ **损耗 150~400**。\n')

buf.write('## 三、判断\n\n')
buf.write('1. **供给够，且偏多**：中位恢复 ~300 vs 损耗 ~150~400——只要主动拿回血，常规局不该死于磨血。\n')
buf.write('2. **事件是最大回血源，而且泛滥**：306 个选项里 83 个带回血（27%%）——几乎每个事件都有「歇一会儿」的选项且普遍 6~15 点。事件的紧张感被回血选项稀释：选回血=稳，选项设计上的风险收益被压平（对照 `event_rr.md` 的必选清单）。\n')
buf.write('3. **难度来源因此是尖峰不是消耗**：精英/穿透/多段的一回合大伤害（15~30 点）超过任何单回合恢复能力——这是健康的（死亡来自失误而非资源枯竭），但要警惕玩家「躺平靠事件回血」的玩法。\n')
buf.write('4. **疯先知例外**：醒侧 30 血，单发 10+ 的攻击两回合就致命；他的梦侧 60 血池是独立资源（`healPlayer` 打的是 run.hp / dreamHp 分流，`index.html:5997` 附近）——恢复体系对他按 30 血口径计算，供给过剩反而让他成「最不需要回复的职业」。\n')
buf.write('5. **维护者的零件变现**：维修凝胶（回 7）+ 基因修复台（回 8）+ 事件 14 点差额调配——维护者是回复供给最厚的职业，符合「保运行」的定位。\n')
buf.write('\n### 复算\n\n`python data/audit/gen_t527.py`（清单部分全自动）；估算表为人工推演，口径已写明。\n')

OUT.write_text(buf.getvalue(), encoding='utf-8')
print('written', OUT, '| heal cards', len(heal_cards), '| regen', len(regen_cards),
      '| relics', len(heal_relics), '| events', len(evh))
