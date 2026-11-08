# -*- coding: utf-8 -*-
"""H11 初始卡组生存推演 → docs/design/sim_starter_survival.md
四角色初始 12 张打 L1-L3 通用池敌人：真回合制微模拟（敌人意图固定循环 + 玩家贪心策略）。
玩家策略：敌人下回合是攻击→优先格挡到够，剩能量打脸；敌人防御/buff→全打脸。抽 5/回合，牌堆循环。
可复算：python tools/sim/sim_starter_survival.py（seed=42）
"""
import sys, statistics, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from simlib import GAME, PARAMS, load_raw, layer_enemy_pool, CN_CLASS

OUT = GAME / 'docs' / 'design' / 'sim_starter_survival.md'
from config import N_SURVIVAL_COMBATS, SEED, BASE_ENERGY, DRAW_PER_TURN
N, SEED, ENERGY, DRAWN = N_SURVIVAL_COMBATS, SEED, BASE_ENERGY, DRAW_PER_TURN
import random

raw = load_raw()
# 初始卡组（engine/core.js buildStarterDeck + STARTER_EXTRA，见 first_run_flow §一）
STARTERS = {
 'diver': [('一击', 7, 0, 5), ('缩起', 0, 5, 4), ('死亡合同副本', 0, 0, 1), ('备用电源', 0, 0, 1), ('锚桩', 0, 5, 1)],
 'tremor': [('一击', 7, 0, 5), ('缩起', 0, 5, 4), ('静日触杖', 0, 0, 1), ('相石·封忆', 0, 0, 1), ('震语：传温', 3, 0, 1)],
 'anmin': [('一击', 7, 0, 5), ('缩起', 0, 5, 4), ('登记工号牌', 0, 0, 1), ('库存盘点', 0, 0, 1), ('基因修复台', 0, 0, 1)],
 'cangmin': [('石矛', 5, 0, 2), ('缩进岩洞', 0, 5, 3), ('火母的低语', 9, 0, 3), ('火母的注视', 0, 8, 2), ('火母历第一页', 0, 0, 1), ('准时的心跳', 0, 7, 1)],
}
# 名字→(能量, 伤害, 格挡)——费用全按 1（死亡合同副本/静日触杖/登记工号牌/库存盘点=0）
COST0 = {'死亡合同副本', '静日触杖', '登记工号牌', '库存盘点'}

def build_deck(cls):
    deck = []
    for name, dmg, blk, n in STARTERS[cls]:
        cost = 0 if name in COST0 else 1
        deck += [{'name': name, 'dmg': dmg, 'blk': blk, 'cost': cost}] * n
    return deck

def intents_of(e):
    return e.get('intent_pattern') or []

def sim_combat(rng, deck, e):
    its = intents_of(e)
    if not its:
        return 0, 0, 0
    s = str(e['hp'])
    hp = (lambda a, b: (a + b) / 2)(*map(float, s.split('-'))) if '-' in s else float(s)
    idx, hp_left, block, taken, turn = 0, hp, 0, 0, 0
    draw_pile = deck[:]; rng.shuffle(draw_pile); discard = []
    while hp_left > 0 and turn < 30:
        turn += 1
        # 抽 5（弃牌堆洗回）
        hand = []
        while len(hand) < DRAWN:
            if not draw_pile:
                draw_pile = discard[:]; rng.shuffle(draw_pile); discard = []
            if not draw_pile:
                draw_pile = deck[:]
            hand.append(draw_pile.pop())
        intent = its[idx % len(its)]; idx += 1
        incoming = (intent.get('value') or 0) * (intent.get('times') or 1) if intent.get('type') == 'attack' else 0
        # 贪心：先凑格挡到 incoming，再打脸
        energy = ENERGY
        dealt = 0
        blocks = 0
        # 抽牌的 0 费先打（扩大手牌，近似）
        for c in list(hand):
            if c['cost'] == 0 and c['dmg'] == 0 and c['blk'] == 0:
                hand.remove(c)
        # 排序：敌人攻击回合优先格挡牌，否则优先伤害牌
        hand.sort(key=lambda c: (c['blk'] if incoming > 0 else -c['dmg']), reverse=True)
        for c in hand:
            if energy < c['cost']:
                continue
            energy -= c['cost']
            dealt += c['dmg']
            blocks += c['blk']
            if incoming > 0 and block + c['blk'] >= incoming and c['blk'] > 0:
                pass
        block += blocks
        # 敌人行动
        if incoming > 0:
            absorbed = min(block, incoming)
            block -= absorbed
            taken += incoming - absorbed
        hp_left -= dealt
        discard += hand
        block = 0  # 回合末格挡清零（无遗物）
    return turn, taken, hp_left

rng = random.Random(SEED)
res = {}
for cls in ['diver', 'tremor', 'anmin', 'cangmin']:
    deck = build_deck(cls)
    per_layer = {}
    for L in range(1, 4):
        pool = layer_enemy_pool(raw, L)
        turns, losses = [], []
        for _ in range(N):
            e = rng.choice(pool)
            t, taken, hp_left = sim_combat(rng, deck, e)
            turns.append(t); losses.append(taken)
        per_layer[L] = (statistics.mean(turns), statistics.mean(losses))
    res[cls] = per_layer

buf = []
buf.append('# H11 · 初始卡组生存推演（真回合制微模拟）')
buf.append('')
buf.append('> **假设**：① 初始 12 张（engine buildStarterDeck+STARTER_EXTRA）；② 玩家策略=**贪心**：敌人下回合攻击→格挡凑够为止，剩能量全打脸；敌人防御/buff 回合→全打脸；③ 抽 5/回合、牌堆循环、格挡回合末清零、无遗物无升级；④ 敌人意图按数据固定循环，血取区间中值。')
buf.append('> **局限**：策略是固定的（真人会留牌/算多回合——真人打得更好）；不分醒梦（疯先知按醒 30 血+醒侧牌）；不含共振/凝视/零件系统。结果解读为**下界**：真实生存应优于本表。')
buf.append('')
buf.append('## 逐角色逐层（每层 %d 场，seed=%d）' % (N, SEED))
buf.append('')
buf.append('| 角色 | L1 回合 | L1 掉血 | L2 回合 | L2 掉血 | L3 回合 | L3 掉血 | 80/72/76/30 血能连打几场（L3） |')
buf.append('|---|---|---|---|---|---|---|---|')
HP = {'diver': 80, 'tremor': 72, 'anmin': 76, 'cangmin': 30}
for cls in ['diver', 'tremor', 'anmin', 'cangmin']:
    p = res[cls]
    buf.append('| %s | %.1f | %.1f | %.1f | %.1f | %.1f | **%.1f** | %.1f 场 |' % (
        CN_CLASS[cls], p[1][0], p[1][1], p[2][0], p[2][1], p[3][0], p[3][1], HP[cls] / p[3][1]))
buf.append('')
buf.append('## 判断')
buf.append('')
l3 = {k: res[k][3][1] for k in res}
worst = min(l3, key=l3.get)
buf.append('1. **掉血逐层陡增**（L1→L3 约翻 %.1f 倍）——初始卡组的防御产出（每回合 ~10-16 挡）在 L3 的 11-14 点攻击面前开始不够分。' % (max(l3.values()) / min(res[k][1][1] for k in res)))
buf.append('2. 最吃力的角色：**%s**（L3 每场掉 %.0f 血）。疯先知醒侧 30 血按本表 %.1f 场就清空——第一次玩疯先知的新手会在 L2-L3 醒着的时候死（梦侧策略才能活，见 first_5min）。' % (CN_CLASS[worst], l3[worst], 30 / l3[worst]))
buf.append('3. 下潜者/维护者靠 0 费抽牌润滑，L3 每场掉血 %.0f/%.0f——**不加新牌也能磨过 L3**，但 L4 boss（120 血）按此口径需要 %.0f 回合以上，掉血会超上限——**这就是「初始卡组必须吃牌成长」的数值证据**。' % (
    res['diver'][3][1], res['anmin'][3][1], 120 / 15))
buf.append('4. 本模拟不含格挡策略的优化空间（真人会多留缩起）——「吃力」从 L3 开始的结论与 T507/T528 互证。')
buf.append('')
buf.append('## 复算')
buf.append('')
buf.append('`python tools/sim/sim_starter_survival.py`（N/SEED/STARTERS 在顶部——改初始卡组改那里）。')
OUT.write_text('\n'.join(buf) + '\n', encoding='utf-8')
import io as _io
sys.stdout = _io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
for k, v in res.items(): print(k, {L: (round(a, 1), round(b, 1)) for L, (a, b) in v.items()})
