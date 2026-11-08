# -*- coding: utf-8 -*-
"""K05 · 模拟器集中配置。所有脚本的口径常数从本文件读——改数值只改这里，run_all.py 一次刷新全部报告。
本文件只搬数值不改逻辑；各脚本的实验专属参数（样本数等）仍留在脚本顶部并在 config 里登记副本口径。
"""

# ── 引擎口径（来自 web/index.html 实跑版，行号见 all_numbers.md） ──
BASE_ENERGY = 4
DRAW_PER_TURN = 5
HAND_LIMIT = 10
PLAYER_HP = {'diver': 80, 'tremor': 72, 'anmin': 76, 'cangmin': 30}

# ── 战斗近似口径（combat_pace.md 双口径的「前期」档，全队列一致） ──
PLAYER_DPS = 15
DPS_DISCOUNT = 0.8

# ── 经济常数（web 实测行号） ──
GOLD_FIGHT = (20, 40)
GOLD_BOSS = (50, 80)
PARTS_KILL = (1, 2)
PARTS_ELITE = 4
PARTS_BOSS = 10

# ── 抽卡权重（T400 §2.3） ──
RARITY_W = {'common': 6, 'uncommon': 3, 'rare': 1, 'special': 3}
VEIN_SCALE = 0.25
VEIN_CAP = 6
VEIN_AFFINITY = 1.3
AFFINITY = {'diver': ['light', 'mineral'], 'tremor': ['tremor', 'heat'],
            'cangmin': ['water', 'heat'], 'anmin': ['mineral', 'water']}

# ── 层结构（event_density 行选择模型） ──
FIGHTS_PER_LAYER = {1: 3.5, 2: 3.5, 3: 3.5, 4: 3.5, 5: 3.5, 6: 3.5, 7: 3.5, 8: 3.0}
ELITE_ROWS = {1: 0, 2: 1, 3: 2, 4: 1, 5: 1, 6: 2, 7: 1, 8: 1}
EVENT_P = {1: 1.0, 2: 0.5, 3: 0.5, 4: 0.5, 5: 0.5, 6: 1.0, 7: 1.0, 8: 1.0}
SHOPS = {2, 3, 6}
LAYERS = 8

# ── 遗物价值模型（sim_relic_value / relic_recalc / relic_triage 共用） ──
RELIC_FIGHTS = 20
RELIC_TURNS_PER_FIGHT = 8
RELIC_KILLS_PER_FIGHT = 1.5
GOLD_PER_POINT = 60 / (0.35 * 76)   # 静脉合剂锚
ENERGY_PER_POINT = 7.6              # K01 口径 B
VEIN_PLAYS = 6                      # K01 口径 B：对应脉卡一局打出次数
KEEP_BLOCK_PER_TURN = 2.4           # K01 口径 B
COST_REDIRECT_TIMES = 4             # K01 口径 B

# ── 全局随机种子（各脚本默认从这里取） ──
SEED = 42

# ── 实验样本数（各脚本默认；单独实验可在脚本顶部覆盖） ──
N_REWARD_PLAYERS = 1000
N_REWARD_FIGHTS = 20
N_COMBAT_SAMPLE = 400
N_ECONOMY_RUNS = 1000
N_BUILD_RUNS = 1000
BUILD_TARGET = 5
BUILD_MAX_F = 60
N_SENS_SAMPLE = 2000
N_VEIN_LEVEL_RUNS = 1000
N_DECISION_TURNS = 2000
N_SURVIVAL_COMBATS = 200
N_FULLRUN_PER_CLASS = 50
