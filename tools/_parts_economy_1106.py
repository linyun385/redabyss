# -*- coding: utf-8 -*-
"""零件经济曲线 · 蒙特卡洛模拟（2026-11-06 第二轮方向 12）。

与第一轮 05_curves.md 的差别：那一轮是**静态汇率表**（纸面推演），
本轮用同一套脚本方法做**动态模拟**——把维护者的收入/支出卡放进真实抽牌
流程里跑 N 场战斗，回答「一场战斗实际能攒/花多少零件」的分布问题。

只读：web/index.html 的 RAW（anmin 池）。
只写：docs/design/curves/parts_economy_auto.md。

跑法：python -I tools/_parts_economy_1106.py [场次，默认 2000]
"""
import io, os, re, json, sys, random, statistics

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'docs', 'design', 'curves', 'parts_economy_auto.md')
RUNS = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
NEWLINE = chr(10)

def load_anmin():
    txt = io.open(os.path.join(ROOT, 'web', 'index.html'), encoding='utf-8').read()
    raw = json.loads(re.search(r'const RAW = (\{.*?\});\n', txt, re.S).group(1))
    return raw['anmin']

# ---- 每张卡的零件语义（静态标注，依据引擎 6023-6035/5988 行的实测行为）----
def parts_profile(c):
    """返回 (income_per_play 分布参数, part_cost, 档位说明)。
    income: ('per_card', k) 本回合每打一张牌得 k（mech_grow，赋值语义：同回合多张互覆）
            ('per_discard', k) 弃光手牌每张 k（需 discard_hand 配对）
            ('none', 0)
    """
    e = c.get('effect') or {}
    sps = e.get('special') or []
    codes = [s.get('code') for s in sps]
    has_discard = 'discard_hand' in codes
    pfd = next((s.get('value', 1) for s in sps if s.get('code') == 'parts_from_discard'), 0)
    mg = next((s.get('value', 1) for s in sps if s.get('code') == 'mech_grow'), 0)
    cost = c.get('part_cost', 0) or 0
    if pfd and has_discard:
        return ('per_discard', pfd), cost
    if mg:
        return ('per_card', mg), cost
    return ('none', 0), cost

def simulate(deck_profiles, strategy='greedy', hand_cap=10, turns=5, plays_per_turn=4, rng=random):
    """极简战斗模型：只保留**牌序与零件语义**。
    循环：回合开始抽满手牌（牌库空则洗弃牌堆）→ 按 strategy 出 plays_per_turn 张 →
    未打出的手牌全部进弃牌堆（对齐引擎 beginTurn 弃未保留手牌的行为）。
    mech_grow 按赋值语义（同回合后打者覆盖先打者，6025 行），beginTurn 清零。
    弃换卡（discard_hand+parts_from_discard）打出时结算剩余手牌 ×k，并终结当轮出牌。
    strategy: 'greedy' 收入卡优先（乐观上界）｜'random' 随机出牌（基线）。
    敌方/能量/效果全部抽象——这回答的是收支分布，不是强度。"""
    lib = deck_profiles[:]
    rng.shuffle(lib)
    discard, hand = [], []
    income = spend = 0
    for t in range(turns):
        hand = [h for h in hand if h is not None]
        while len(hand) < hand_cap:
            if not lib:
                lib = discard[:]
                discard = []
                rng.shuffle(lib)
            if not lib:
                break
            hand.append(lib.pop())
        order = list(range(len(hand)))
        if strategy == 'greedy':
            order.sort(key=lambda i: 0 if hand[i][1] == 'per_card' else (1 if hand[i][1] == 'per_discard' else 2))
        grow = 0
        played = 0
        idx = 0
        while played < plays_per_turn and idx < len(order):
            i = order[idx]
            if hand[i] is None:
                idx += 1
                continue
            p = hand[i]
            income += grow  # 增生在打出前结算（这张牌自己不算）
            if p[1] == 'per_card':
                grow = p[2]
            elif p[1] == 'per_discard':
                spend += p[3]
                rest = sum(1 for j in order[idx+1:] if hand[j] is not None)
                income += rest * p[2]
                for j in range(len(hand)):
                    if hand[j] is not None:
                        discard.append(hand[j])
                        hand[j] = None
                played += 1
                break
            spend += p[3]
            discard.append(p)
            hand[i] = None
            played += 1
            idx += 1
        for j in range(len(hand)):  # 未打出的手牌进弃牌堆（引擎 beginTurn 行为）
            if hand[j] is not None:
                discard.append(hand[j])
                hand[j] = None
        grow = 0
    return income, spend

def load_draft():
    p = os.path.join(ROOT, 'docs', 'design', 'anmin_minions', 'cards_draft.json')
    return json.load(io.open(p, encoding='utf-8'))

def main():
    cards = load_anmin()
    draft = load_draft()
    def build_profiles(cards_iter):
        ps = []
        for c in cards_iter:
            if c['id'] in ('anm_0052', 'anm_0053'):  # 召唤/悬浮不进本模型
                continue
            (kind, k), cost = parts_profile(c)
            if kind != 'none' or cost:
                ps.append((c['id'], c['name'], kind, k, cost))
        return ps
    live_p = build_profiles(cards)
    live_inc = [x for x in live_p if x[2] != 'none']
    live_spd = [x for x in live_p if x[4] > 0]
    draft_p = build_profiles(draft)
    draft_inc = [x for x in draft_p if x[2] != 'none']
    draft_spd = [x for x in draft_p if x[4] > 0]

    def deck_of(entries):
        return [(e[0], e[2], e[3], e[4]) for e in entries]

    filler = lambda n: [('filler%d' % i, 'none', 0, 0) for i in range(n)]

    # 场景：18 张牌组（手牌上限 10 之上，保证洗牌循环有方差）、每回合出 4 张、5 回合
    S = []
    S.append(('S1 · 现网基线（增生×2+换代×2+14 填充）',
              deck_of(live_inc * 2 if len(live_inc) < 3 else live_inc) + filler(14)))
    S.append(('S2 · 现网 + 全部现网零件费卡（武器试验/发电/重铸 各1）',
              deck_of(live_inc) + deck_of(live_spd) + filler(14 - len(live_inc))))
    S.append(('S3 · 现网收入 + 草稿收入（0058/0059/0060/0065 各2）+ 草稿支出卡各1 + 填充',
              deck_of(live_inc) + deck_of(draft_inc) + deck_of(draft_spd) + filler(max(0, 18 - len(live_inc) - len(draft_inc) - len(draft_spd)))))

    out = []
    out.append('# 零件经济 · 蒙特卡洛模拟产出（自动生成，勿手改）')
    out.append('')
    out.append('> 由 `tools/_parts_economy_1106.py` 生成（%d 次模拟/场景/策略，固定种子可复现）。' % RUNS)
    out.append('> 模型：18 张牌组、手牌上限 10、每回合出 4 张、5 回合；牌库空则洗弃牌堆；回合结束弃光未打出的手牌（对齐引擎 beginTurn）。')
    out.append('> mech_grow 按引擎实测**赋值语义**（同回合后打者覆盖，6025 行），出牌前结算（自己不算）。')
    out.append('> 双策略夹逼：greedy=收入卡优先（乐观上界），random=随机出牌（基线）。敌方/能量/效果抽象——回答的是收支分布，不是强度。')
    out.append('> 数据口径：S1/S2 用现网 RAW.anmin；S3 额外并入 docs/design/anmin_minions/cards_draft.json（草稿未入库，单独成景）。')
    for title, deck in S:
        rngA = random.Random(20261106)
        resA = [simulate(deck, 'greedy', rng=rngA) for _ in range(RUNS)]
        rngB = random.Random(20261106)
        resB = [simulate(deck, 'random', rng=rngB) for _ in range(RUNS)]
        def q(v, r): return sorted(v)[min(len(v)-1, len(v)*r//10)]
        inc = [x[0] for x in resA]; spd = [x[1] for x in resA]; net = [x[0]-x[1] for x in resA]
        inc2 = [x[0] for x in resB]; net2 = [x[0]-x[1] for x in resB]
        out.append('')
        out.append('## %s' % title)
        out.append('')
        out.append('| 指标 | 收入(greedy) | 支出(greedy) | 净存(greedy) | 收入(random) | 净存(random) |')
        out.append('|---|---|---|---|---|---|')
        out.append('| 中位 | %.1f | %.1f | %.1f | %.1f | %.1f |' % (statistics.median(inc), statistics.median(spd), statistics.median(net), statistics.median(inc2), statistics.median(net2)))
        out.append('| P10 | %.1f | %.1f | %.1f | %.1f | %.1f |' % (q(inc,1), q(spd,1), q(net,1), q(inc2,1), q(net2,1)))
        out.append('| P90 | %.1f | %.1f | %.1f | %.1f | %.1f |' % (q(inc,9), q(spd,9), q(net,9), q(inc2,9), q(net2,9)))
        neg = sum(1 for n in net if n < 0)
        neg2 = sum(1 for n in net2 if n < 0)
        out.append('')
        out.append('净存为负占比：greedy %.1f%% / random %.1f%%' % (neg*100.0/RUNS, neg2*100.0/RUNS))
    io.open(OUT, 'w', encoding='utf-8').write(NEWLINE.join(out) + NEWLINE)
    print('写入 %s' % OUT)

if __name__ == '__main__':
    main()
