# -*- coding: utf-8 -*-
"""红渊模拟公共库（H01-H15 共用）。

★ 边界声明：本库不是真引擎。它按 docs/design/ 的文档假设搭的近似模型：
  - 战斗：DPS/承伤用文档口径（前期 DPS≈15、4 能量、平均费 1.09），不模拟真实卡牌结算
  - 抽卡：按 T400 §2.3 权重公式近似（稀有度 6/3/1 × 脉亲和 × 硬保证）
  - 经济：金币 randInt(20,40)/场、boss 50-80、零件 1-2/4/10，按 web 引擎实测常数
  - 不模拟：升级、遗物联动、协议、双世界、共振层反应对战斗的影响
参数集中在 PARAMS；随机一律用传入的 rng（固定种子可复现）。
数据源：cards/*.json 与 data/audit/raw_all.json（只读）。
"""
import json, math, random
from pathlib import Path

GAME = Path(__file__).resolve().parents[2]
from config import (BASE_ENERGY, DRAW_PER_TURN, HAND_LIMIT, PLAYER_HP,
                    PLAYER_DPS, DPS_DISCOUNT, GOLD_FIGHT, GOLD_BOSS,
                    PARTS_KILL, PARTS_ELITE, PARTS_BOSS, RARITY_W,
                    VEIN_SCALE, VEIN_CAP, VEIN_AFFINITY, AFFINITY, SEED)

PARAMS = {
    'BASE_ENERGY': BASE_ENERGY,
    'DRAW_PER_TURN': DRAW_PER_TURN,
    'HAND_LIMIT': HAND_LIMIT,
    'PLAYER_DPS': PLAYER_DPS,
    'DPS_DISCOUNT': DPS_DISCOUNT,
    'GOLD_FIGHT': GOLD_FIGHT,
    'GOLD_BOSS': GOLD_BOSS,
    'PARTS_KILL': PARTS_KILL,
    'PARTS_ELITE': PARTS_ELITE,
    'PARTS_BOSS': PARTS_BOSS,
    'RARITY_W': RARITY_W,
    'VEIN_AFFINITY': VEIN_AFFINITY,
    'VEIN_SCALE': VEIN_SCALE,
    'VEIN_CAP': VEIN_CAP,
    'AFFINITY': AFFINITY,
    'EVENTS_PER_LAYER': {1: 1.0, 2: 0.5, 3: 0.5, 4: 0.5, 5: 0.5, 6: 1.0, 7: 1.0, 8: 1.0},  # T512
    'HP': PLAYER_HP,
}
CN_VEIN = {'light': '光', 'water': '水', 'heat': '热', 'tremor': '震', 'mineral': '矿'}
CN_CLASS = {'diver': '下潜者', 'tremor': '震语者', 'anmin': '维护者', 'cangmin': '疯先知', 'shared': '通用'}


def load_json(rel):
    return json.loads((GAME / rel).read_text(encoding='utf-8'))


def load_cards():
    out = {}
    for f in ['diver', 'tremor', 'anmin', 'cangmin', 'shared']:
        out[f] = load_json('cards/%s.json' % f)
    return out


def load_raw():
    return load_json('data/audit/raw_all.json')


def class_pool(cls, cards):
    """CLASS_POOL = 角色池 + 通用池（web:414314 同款）。"""
    return cards.get(cls, []) + cards['shared']


def reward_weights(pool, owned_vein_count, main_vein, affinity_veins):
    """T400 §2.3 权重：rarity × (1+min(持有,6)*0.25) × (擅长 1.3)。
    持有该脉张数按卡牌 veins 计（多脉卡给每条脉各计一次）。"""
    ws = []
    for c in pool:
        w = PARAMS['RARITY_W'].get(c.get('rarity'), 1)
        vs = c.get('veins') or []
        if vs and main_vein in vs:
            w *= (1 + min(owned_vein_count, PARAMS['VEIN_CAP']) * PARAMS['VEIN_SCALE'])
        if vs and any(a in vs for a in affinity_veins):
            w *= PARAMS['VEIN_AFFINITY']
        ws.append(w)
    return ws


def show_three(rng, pool, owned_counts, main_vein, affinity_veins):
    """三选一展示（**无放回加权抽样**）+ T400 硬保证（≥1 主脉、≥1 非主脉）。
    事故留档：首版算了 reward_weights 但采样用 randrange 均匀——权重从未生效（I01 发现，已修）。"""
    ws = reward_weights(pool, owned_counts.get(main_vein, 0), main_vein, affinity_veins)
    pool_idx = list(range(len(pool)))
    w = ws[:]
    picks, idx = [], set()
    while len(picks) < 3 and pool_idx:
        i = rng.choices(pool_idx, weights=w, k=1)[0]
        pos = pool_idx.index(i)
        pool_idx.pop(pos)
        w.pop(pos)
        idx.add(i)
        picks.append(i)
    def is_main(i):
        return main_vein in (pool[i].get('veins') or [])
    if not any(is_main(i) for i in picks):
        cand = [i for i in range(len(pool)) if is_main(i) and i not in idx]
        if cand:
            picks[-1] = rng.choice(cand)
            idx.add(picks[-1])
    if all(is_main(i) for i in picks):
        cand = [i for i in range(len(pool)) if not is_main(i) and i not in idx]
        if cand:
            picks[-1] = rng.choice(cand)
            idx.add(picks[-1])
    return [pool[i] for i in picks]


def pick_card(rng, shown, owned_counts, target_vein=None, policy='vein'):
    """玩家拿牌策略：vein=目标脉优先（+100）再按稀有度；random=随机。
    事故留档：首版算完 scored 却 return shown[0]——分数被丢弃、永远拿第一张（I06 发现，已修）。"""
    if policy == 'random':
        return rng.choice(shown)
    scored = []
    for i, c in enumerate(shown):
        vs = c.get('veins') or []
        s = 0
        if target_vein and target_vein in vs:
            s += 100
        s += {'rare': 3, 'uncommon': 2, 'common': 1}.get(c.get('rarity'), 0)
        scored.append((s, rng.random(), i))
    scored.sort(reverse=True)
    return shown[scored[0][2]]


def layer_enemy_pool(raw, layer, cls=None):
    """该层可用敌人（通用主+副池；角色池仅覆盖其层数——近似：主+副池合并按层取样）。"""
    es = [e for e in raw['enemies'] if e['layer'] == layer]
    if cls == 'anmin':
        es = [e for e in raw['anminEnemies'] if e['layer'] == layer] or es
    elif cls == 'cangmin':
        es = [e for e in raw['cngEnemies'] if e['layer'] == layer] or es
    return es


def enemy_metrics(e):
    its = list(e.get('intent_pattern') or [])
    for ph in e.get('phases') or []:
        its.extend(ph.get('intent_pattern') or [])
    atks = [i.get('value') or 0 for i in its if i.get('type') == 'attack']
    freq = len(atks) / len(its) if its else 0
    avg = sum(atks) / len(atks) if atks else 0
    s = str(e['hp'])
    hp = (lambda a, b: (a + b) / 2)(*map(float, s.split('-'))) if '-' in s else float(s)
    return hp, avg, freq


def simulate_fight(rng, e, dps=PARAMS['PLAYER_DPS'], discount=PARAMS['DPS_DISCOUNT']):
    """近似战斗：回合数=血/DPS；玩家承伤=平均单发×攻击频率×回合数（defend 回合按 0 摊入）。
    返回 (rounds, damage_taken)。"""
    hp, avg_atk, freq = enemy_metrics(e)
    rounds = max(1, math.ceil(hp / dps))
    taken = avg_atk * freq * (hp / dps)   # 用小数回合数（未取整）累积更平滑
    return rounds, taken


def gold_for_fight(rng, tier):
    a, b = PARAMS['GOLD_FIGHT']
    if tier == 'boss':
        a, b = PARAMS['GOLD_BOSS']
        return rng.randint(a, b)
    return rng.randint(a, b)


def parts_for(rng, tier):
    if tier == 'boss': return PARAMS['PARTS_BOSS']
    if tier == 'elite': return PARAMS['PARTS_ELITE']
    return rng.randint(*PARAMS['PARTS_KILL'])
