# ECO_RELIC_CARD.md — 生态遗物 + 专属卡牌（T63 产出）

> 配额来源：`docs/CONTENT_PLAN.md` §3.1 缺口列（遗物 +1 arid；素卡 +6：surface 3 / nexus 3）。落地：`relics/all.json` 77 件（relic_77 带 `eco` + `mod` 字段）、`cards/diver.json` 83 张（dive_0081–83，surface 素卡）、`cards/tremor.json` 83 张（trem_0081–83，nexus 素卡）。
> 「每生态至少 1 个改变玩法遗物」由**现有脉亲和池**满足（脚本核过 8 生态各 5–15 件非纯数值遗物，如 surface 净化者的灰、cold 地文历残页、vent 静日触杖、rad 上一任的矿牌）；本任务新遗物补的是 arid 的数量缺口，且它本身是改则件。
> 引擎缺口清单：**无**。relic 的 `mod.vein_cost` 通道引擎早已实现（`engine/core.js:396`，现有 76 件从未用过）——本任务第一次给它喂数据，不算新动作。

---

## 1. eco_arid 遗物

| 名称 | 效果 | 为什么属于这个生态 |
|---|---|---|
| relic_77 **泉权的账戳**（rare） | 开战时格挡 +3（combat_start:block）；**水脉牌费用 −1**（`mod:{vein_cost:'water', vein_cost_delta:-1}`） | D3 的禁忌是水有路权（LAYERS.md）；层规则 `dry` 让水脉 +1（游戏内 LAYER_NOTE「水脉枯竭」）——账戳把泉权的印盖在水牌上，规程也得认。**改玩法而非数值**：它改的是层规则的结算结果。 |

## 2. surface 素卡（diver 池，无脉=素品口径）

| 名称 | 费用/稀有度 | 效果 | 呼应点 |
|---|---|---|---|
| dive_0081 气闸的规程 | 0费/common | 格挡 4，retain（留在手里） | 敌 d1_e3 气闸的守夜者（开合循环）——规程留在手里，什么时候开自己定 |
| dive_0082 按规程应答 | 1费/common | 伤害 9，gaze_cost 1（凝视 ≥1 才能打） | 事件 d1_7「报自己的编号」/ boss 静默号的 gift——红光在听，你用它的注意力打它 |
| dive_0083 坠轨的清单 | 1费/uncommon | 抽 2，cost_type vitality（最大生命 −1） | 事件 d1_8「拿清单上没有的」——没登记的最重，签了收就扣余量 |

## 3. nexus 素卡（tremor 池，无脉=素品口径）

| 名称 | 费用/稀有度 | 效果 | 呼应点 |
|---|---|---|---|
| trem_0081 值班交接 | 1费/common | 格挡 5，共振 +1 | 事件 d8_4 值班交接 / 敌 d8_06 值班的影子——到岗就有班产生的共鸣 |
| trem_0082 不许关闭 | 0费/common | 格挡 2，共振 +1，retain | 敌 d8_10 不许关闭的告示——牌子不许灭，也不许扔 |
| trem_0083 谐振的余音 | 2费/uncommon | 伤害 5 × 2 段 | 敌 d8_09 谐振的余音（attack×2 循环）——第二段打你没防备的地方 |

## 4. 三组 combo（结算顺序写实）

**A. 泉权的账戳 × 水脉牌 × D3 dry 层规则（遗物改规则，卡吃规则）**
结算顺序：打出任何水脉牌（如 diver 氧气再生器）→ 引擎 `cardCost`（core.js:389）起算能量 → 391–393 行：`C.layer.rule === 'dry' && card.veins 含 water` → **+1** → 396–397 行：遍历 run.relics 的 `mod`，relic_77 的 `vein_cost:'water' && vein_cost_delta:-1` → **−1** → 净 0，水脉牌在 D3 恢复原价。既有 31 张水脉卡全部吃到这个减免。

**B. 按规程应答 × 事件 d1_7「报自己的编号」 × boss 静默号的 gift**
结算顺序：事件选项 r.gaze+3（web 事件处理器 6588 行，`run.gaze` 即时入账）→ 战斗中 boss 的 gift 意图再 +1（engine debuff#gift 分支）→ 打出 dive_0082：引擎 playCard 339 行先查 `run.gaze ≥ gaze_cost(1)`（不消耗，纯门槛）→ 通过则 damage 9 结算（enemyAct 之外，走玩家出牌的 dealToEnemy 链）。凝视的副作用（gazeMul 每十点全体敌伤 +10%）是这张卡的隐性成本。

**C. 值班交接 / 不许关闭 × D8 time_loop 层规则 × 共鸣阈值**
结算顺序：打出 trem_0081（resonance_gain:1）→ 引擎玩家出牌效果处理把 `C.resonance +1` → 每回合 beginTurn 再叠层规则 `C.layer.res`（D8 = 8）→ 达到 10/20/30 阈值触发 MODE_REACTION（D8 mode='void'：红光消失/脉锁）→ trem_0082 的 retain 让第二张「不许关闭」留在手里，下一回合再 +1——两张素卡把共鸣阈值从「每回合 +8」抬成「+8 加手牌」，在 D8 的三阈值内多踩一脚。

## 5. 超模自检（tools/_t63_check.js，折算系数沿用 card_audit.js 口径）

| 新卡 | 价值 | 同费同稀有度现有上限 | 比值 |
|---|---|---|---|
| dive_0081 | 5.0 | 8.0 | 0.63 |
| dive_0082 | 9.0 | 14.0 | 0.64 |
| dive_0083 | 5.0 | 16.0 | 0.31 |
| trem_0081 | 5.5 | 14.0 | 0.39 |
| trem_0082 | 3.5 | 8.0 | 0.44 |
| trem_0083 | 10.0 | 18.0 | 0.56 |

最大比值 **0.64**，全部 ≤ 1.3 ✓。
