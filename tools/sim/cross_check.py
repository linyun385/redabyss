# -*- coding: utf-8 -*-
"""K03 交叉验证探针：人工读代码得出预言，用实际运行验证。5 个脚本 × 每个一条「可证伪预言」。"""
import sys, io, random
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from simlib import load_cards, class_pool, show_three, pick_card, load_raw, layer_enemy_pool, simulate_fight

cards = load_cards()
raw = load_raw()
ok = fail = 0

def check(name, predict, actual, agree):
    global ok, fail
    ok += agree; fail += (not agree)
    print('[%s] %s' % ('PASS' if agree else 'FAIL', name))
    print('   人工预言：%s' % predict)
    print('   实际运行：%s' % actual)

# 探针 1 · sim_reward：硬保证「≥1 非主脉」——构造全主脉展示场景验证替换分支
# 人工预言：若三张全是主脉（light），最后一张会被替换成非主脉
pool = class_pool('diver', cards)
rng = random.Random(7)
all_main_shown = 0
for _ in range(500):
    shown = show_three(rng, pool, {'light': 6}, 'light', [])
    if all('light' in (c.get('veins') or []) for c in shown):
        all_main_shown += 1
check('show_three 硬保证（≥1 非主脉）',
      '500 次抽样中不应出现「三张全主脉」（替换分支强制非主脉）',
      '全主脉次数 = %d' % all_main_shown,
      all_main_shown == 0)

# 探针 2 · pick_card：目标脉优先 +100——两张同稀有度时必拿目标脉
pool2 = class_pool('tremor', cards)
rng2 = random.Random(3)
grab = 0; n2 = 500
for _ in range(n2):
    shown = show_three(rng2, pool2, {'tremor': 0}, 'tremor', [])
    taken = pick_card(rng2, shown, {}, target_vein='tremor')
    if 'tremor' in (taken.get('veins') or []):
        grab += 1
has_tremor = sum(1 for c in shown if 'tremor' in (c.get('veins') or []))
check('pick_card 目标脉优先',
      '每次展示中含震脉牌时（本样本最后一次=%d 张）必拿震脉' % has_tremor,
      'n=%d 次中拿走震脉 %d 次（=含震脉的展示次数合计）' % (n2, grab),
      grab == sum(1 for _ in range(0)))  # 占位——下行用真实合计重验
# 重新精确对账：逐次统计「展示含震脉」与「拿走震脉」应相等
rng3 = random.Random(3)
shown_with, taken_with = 0, 0
for _ in range(n2):
    shown = show_three(rng3, pool2, {'tremor': 0}, 'tremor', [])
    w = sum(1 for c in shown if 'tremor' in (c.get('veins') or []))
    if w: shown_with += 1
    taken = pick_card(rng3, shown, {}, target_vein='tremor')
    if 'tremor' in (taken.get('veins') or []): taken_with += 1
check('pick_card 目标脉优先（精确对账）',
      '展示含震脉的次数 == 拿走震脉的次数',
      '含震展示 %d / 拿走震 %d' % (shown_with, taken_with),
      shown_with == taken_with)

# 探针 3 · simulate_fight：回合数=ceil(血/DPS)、承伤=攻击×频率×小数回合
pool3 = layer_enemy_pool(raw, 3)
e = pool3[0]
r, t = simulate_fight(random.Random(0), e)
its = list(e.get('intent_pattern') or [])
atks = [i.get('value') or 0 for i in its if i.get('type') == 'attack']
s = str(e['hp']); hp = (lambda a,b:(a+b)/2)(*map(float,s.split('-'))) if '-' in s else float(s)
expect_r = max(1, -(-hp // 15))
expect_t = (sum(atks)/len(atks)) * (len(atks)/len(its)) * (hp/15)
check('simulate_fight 公式',
      '回合=ceil(%.1f/15)=%.0f；承伤=%.1f' % (hp, expect_r, expect_t),
      '回合=%.0f 承伤=%.2f' % (r, t),
      r == expect_r and abs(t - expect_t) < 0.01)

# 探针 4 · layer_enemy_pool：cls=None 只取通用池、cls='anmin' 取维护者池
p_none = {x['id'] for x in layer_enemy_pool(raw, 1)}
p_anmin = {x['id'] for x in layer_enemy_pool(raw, 1, cls='anmin')}
check('layer_enemy_pool 池切换',
      'L1 通用池不含 anmenemy_*；anmin 池只含 anmenemy_*',
      '通用 %d 只（含 anmenemy: %s）；anmin %d 只（含 anmenemy: %s）' % (
          len(p_none), any(i.startswith('anmenemy') for i in p_none), len(p_anmin),
          all(i.startswith('anmenemy') for i in p_anmin)),
      (not any(i.startswith('anmenemy') for i in p_none)) and all(i.startswith('anmenemy') for i in p_anmin))

# 探针 5 · reward_weights：封顶——持有 6 与持有 10 的权重应相同（cap=6）
sys.path.insert(0, str(Path(__file__).resolve().parent))
from simlib import reward_weights, PARAMS
pool4 = class_pool('diver', cards)
w6 = reward_weights(pool4, 6, 'light', [])
w10 = reward_weights(pool4, 10, 'light', [])
check('reward_weights 封顶',
      '持有 6 与持有 10 的主脉权重相同（cap=6）',
      'max(w6)=%.2f max(w10)=%.2f' % (max(w6), max(w10)),
      abs(max(w6) - max(w10)) < 1e-9)

print('\nPASS %d / FAIL %d' % (ok, fail))
