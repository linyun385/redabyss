# T514 · 游戏内数字全清单

> 每项都给数据来源文件（精确到文件与行号，行号为本夜 2026-11-05 快照）。复算命令见文末。
> ⚠ 发现一处引擎副本不同步（见 §9）。

## 1. 内容总量

| 项 | 数值 | 来源 |
|---|---|---|
| 层数 | 8 | `web/index.html` RAW.layers.layers（行 6401 内） |
| 卡牌 | 219（diver 57 / tremor 57 / anmin 47 / cangmin 47 / shared 11） | `cards/*.json` |
| 敌人 | 145（通用 113 / 维护者池 16 / 疯先知池 16） | RAW.enemies / anminEnemies / cngEnemies |
| 遗物 | 107（通用 77 / 维护者 15 / 疯先知 15） | RAW.relics / anminRelics / cngRelics |
| 事件 | 102（通用 82 / 维护者 10 / 疯先知 10） | RAW.events / anminEvents / cngEvents |
| 层节点 | 每层 4 行 × 1~2 选项 | RAW.layers.layers[].rows |

## 2. 玩家基础数值

| 项 | 数值 | 来源 |
|---|---|---|
| 初始生命 | 下潜者 80 / 维护者 76 / 震语者 72 / 疯先知 30（醒）/ 梦 60（独立血池） | `engine/core.js` newRun（行 62-71） |
| 初始能量 | **4**（web 实跑版） | `web/index.html:5375` `BASE_ENERGY = 4` |
| 每回合抽牌 | 5（lockdown 协议 -1） | `web/index.html:5374` `DRAW_PER_TURN = 5`；5603 |
| 手牌上限 | 10 | `web/index.html:5373` `HAND_LIMIT = 10` |
| 初始卡组 | 12 张（基础 10 + 固定补位 2；二周目 -1 补位 +死亡合同） | `engine/core.js` buildStarterDeck；`web/index.html` startRun STARTER_EXTRA（行 ~6479） |
| 疯先知清醒度 | 初始 3，上限 5；战斗胜 +2 | engine/core.js newRun；web/index.html finishCombat（行 6188） |

## 3. 经济

| 项 | 数值 | 来源 |
|---|---|---|
| 普通战斗金币 | 20~40（randInt） | `web/index.html:6195` |
| boss 金币 | 50~80（50 + rng×31） | `web/index.html:7165` 附近 |
| 维护者金币 | 全部折算成零件（不发金币） | `web/index.html:6195` 注释 |
| 零件掉落（维护者） | 普通 1~2 / 精英 4 / boss 10 | `engine/core.js` dealToEnemy（行 ~494 后段） |
| 改造价 | 2 零件 = +2 伤 或 +3 挡（本局永久） | `web/index.html:6232-6244` salvageUpgrade |
| 拆解价 | 3 零件 = 威胁 +1（剩余敌人攻击 +1）+ 战后 1 随机遗物 | `web/index.html:6247-6255` dismantle |

## 4. 商店（前哨杂货）

| 项 | 价格（金） | 来源 |
|---|---|---|
| 普通卡 | 40~60 | `web/index.html:6813-6821` shopPrice/buildShopStock |
| 精良卡 | 75~110 | 同上 |
| 稀有卡 | 150~200 | 同上 |
| 遗物（普通/精良位） | 120~160 | 同上 |
| 遗物（稀有/boss 位） | 250~320 | 同上 |
| 删牌服务 | 75（一次） | 同上 |
| 静脉合剂（回 35% 最大生命） | 60（一次） | 同上 |
| 商店出现层 | 第 2/3/6 层各 1 行（期望 0.5 次/层） | RAW.layers rows；`event_density.md` |

## 5. 资源阈值

| 项 | 数值 | 来源 |
|---|---|---|
| 共振阈值 | 10 / 20 / 30 三档，触发层反应；**≥30 过载（每回合掉 layer.res 血）** | `engine/core.js:303-312` checkResonance |
| 共振每层增量 | 每回合 +layer.res（第 5 层 +5 等，逐层见 RAW.layers） | `engine/core.js:243` |
| 凝视结局 | 凝视 ≥20 → 长审；≤5 → 背身；其间 → 同行 | `web/index.html:6221-6228` pickEnding |
| 威胁等级 | 拆解 +1/次；剩余敌人攻击 buffAtk +1 | `web/index.html:6247` dismantle |

## 6. 敌人强度（区间口径见 enemy_compact）

| 项 | 数值 | 来源 |
|---|---|---|
| 普通敌血量 | 第 1 层 8~13 → 第 8 层 18~42 | RAW.enemies hp 字段 |
| 精英血量 | 27~102 | 同上 |
| boss 血量 | 46~200 | 同上 |
| 最高单发攻击 | 30（穹顶之影 buff 后）/ 24（墟蛹三阶段 8×3 穿透另计） | 意图字段最大值 |
| 期望承伤中位数（普通敌） | 11（玩家 DPS=15 模型） | `enemy_avoid.md` 模型 |

## 7. 结局与奖励节奏

| 项 | 数值 | 来源 |
|---|---|---|
| 战斗奖励 | 普通=金+拿牌三选一；精英=拿牌+遗物三选一；boss=必给遗物+金 | `web/index.html:7140-7148` |
| 拿牌权重 | 普通 6 / 精良 3 / 稀有 1 | `web/index.html` weightedCards（行 ~442280 旧注） |
| 事件给牌 | 纯随机无权重 | `web/index.html` cardsOfRarity（行 ~451451 旧注） |
| 通关标记 | `redabyss_cleared` localStorage；二周目开局带死亡合同（增补条款） | `web/index.html` startRun |
| 层奖励金（depth<8 时 boss） | 50~80 | `web/index.html:7165` |

## 8. 引擎里查到但游戏里「感觉不到」的数字

| 项 | 数值 | 来源 | 说明 |
|---|---|---|---|
| 弱话倍率 | 敌人带 weak 时攻击 ×0.75 | `engine/core.js:745` | 真实生效 |
| 穿透攻击 | pierce 完全无视格挡 | `engine/core.js` 意图结算 | 真实生效 |
| 灼烧覆盖 | burn 直接赋值，后施盖前施，不叠加 | `engine/core.js:494` | 铺火牌互相覆盖 |
| **脆弱 frail** | 施加后**无任何结算** | `engine/core.js:497`（施加）:675（递减） | **死状态**：dealToEnemy 不读 frail |

## 9. 发现的不同步（报告，不改）

- **BASE_ENERGY**：`engine/core.js:14` = **3**，`web/index.html:5375` = **4**。web 是实跑版本（T400 §2.4 改的就是 web），engine 模块副本没跟上。两个副本还有多处（HAND_LIMIT 两处都是 10，一致）。**未确认：以哪个为准——按 T400 §2.4 的记录应以 4 为准，engine/core.js 是过期副本。**

## 10. 复算

```
python -c "
import json, sys; sys.path.insert(0,'data/audit')
from audit_common import load_cards, all_cards
print('cards', sum(len(v) for v in load_cards().values()))
RAW = json.load(open('data/audit/raw_all.json', encoding='utf-8'))
print('enemies', len(RAW['enemies'])+len(RAW['anminEnemies'])+len(RAW['cngEnemies']))
print('relics', len(RAW['relics'])+len(RAW['anminRelics'])+len(RAW['cngRelics']))
print('events', len(RAW['events'])+len(RAW['anminEvents'])+len(RAW['cngEvents']))
print('layers', len(RAW['layers']['layers']))
"
```

预期：cards 219 / enemies 145 / relics 107 / events 102 / layers 8。
引擎数字（血量/能量/抽牌/价格/阈值）逐条给了文件行号，用 `sed -n '<行号>p <文件>'` 直接核对。
