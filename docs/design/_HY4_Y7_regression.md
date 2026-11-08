# HY4 · Y7 回归：公共路径五条

> 2026-11-06 02:45。**逐行读代码**，没有跑起来看。五条结论：**5 条一致 / 0 条不一致 / 0 条无法判断**（每条都带前提条件）。

## 基线与 git

| 项 | 结果 |
|---|---|
| `game/.git` | 不存在 |
| `红渊/.git` | 不存在 |
| git diff | **未执行**。任务书要求「先确认 git 是否初始化过，没有就别折腾」，确认未初始化后停止 |

没有 git 基线，改用 **`engine/core.js`（1027 行旧副本）** 做改动前对照。`_VERIFY_anmin_core_cards.md` 第 127 行明确记它「仍是旧副本、没有这批新 code，页面不加载它」，所以它是本次改动前的近似基线。

**基线可靠性核验**（脚本全文计数，证明哪些差异是本次新增、哪些是历史漂移）：

| 特征 | `web/index.html` | `engine/core.js` | 归属 |
|---|---|---|---|
| `part_cost` | 10 | 0 | 本次新增 |
| `runStrengthCarry` | 9 | 0 | 本次新增 |
| `mechGrow` | 4 | 0 | 本次新增 |
| `isMinion` | 12 | 0 | 本次新增 |
| `nextTurnBonusEnergy` | 7 | 0 | 本次新增 |
| `sp.value !== undefined`（value 优先 v） | 1 | 0 | **历史漂移**（2026-11-04 修，非本次） |
| `code === 'exhaust'` 双写法 | 3 | 0 | **历史漂移**（2026-11-04 修，非本次） |
| 「这张牌本场已锁死」提示文案 | 1 | 0 | **历史漂移**（文案，非逻辑） |

三个公共子函数 `veinChainBonus`（web 5888 / core 425）、`cardCost`（web 5866 / core 403）、`activateProtocol`（web 6550 / core 959）在两版**逐字一致**（脚本逐行比对前 16 行），说明连携加成、费用计算、协议激活的实现没被动过。

## 逐条结论

### 第 1 条 · 普通攻击牌伤害公式 → **一致**

> 要求：`伤害 = effect.damage + 连携加成 + buffs.strength`（没有 `runStrengthCarry` 时结果应和以前一样）

| 位置 | 代码 |
|---|---|
| 旧 `core.js:448` | `let bonus = chainBonus * 2;` |
| 旧 `core.js:458` | `if (layer.rule === 'bright' && ...light...) bonus += 2;` |
| 旧 `core.js:463` | `const dmgEach = Math.max(0, e.damage + bonus + (C.buffs.strength \|\| 0) + (C.activeProtocol === 'purge' ? 3 : 0));` |
| 新 `web:5911` | `let bonus = chainBonus * 2;`（同） |
| 新 `web:5914–5915` | `const noBonus = !!(card.no_bonus \|\| e.no_bonus); if (noBonus) bonus = 0;`（**新增**） |
| 新 `web:5925` | `if (!noBonus && layer.rule === 'bright' && ...) bonus += 2;`（多了 `!noBonus` 前置） |
| 新 `web:5931` | `const str = noBonus ? 0 : ((C.buffs.strength \|\| 0) + (C.runStrengthCarry \|\| 0) + (C.activeProtocol === 'purge' ? 3 : 0));` |
| 新 `web:5932` | `const dmgEach = Math.max(0, e.damage + bonus + str);` |

**代入前提** `runStrengthCarry = 0`、`no_bonus = false`：
`str = buffs.strength + 0 + purge3`，`bonus = chainBonus*2 + (bright ? 2 : 0)` → `dmgEach = max(0, e.damage + bonus + buffs.strength + purge3)`，与 `core.js:463` **逐项相同**。

`hits` / `targets` 循环（旧 462、464–469 / 新 5929、5933–5938）结构一致。唯一改动：新 5934 行 `target:'all'` 的目标过滤多了 `&& !x.isMinion`；**场上没有子代理时** `x.isMinion` 为 undefined，`!undefined === true`，与旧 465 行 `filter(x => !x.dead)` 结果完全相同。

**前提边界**：`no_bonus = true` 时新公式不同（bonus 归零、str 归零）。全池 `no_bonus` 只有 1 张 `anm_0053` 悬浮体，它是 `type:power` 且 `effect` 里没有 `damage` 字段，因此**当前数据下不存在被改变数值的攻击牌**。

### 第 2 条 · 格挡牌公式 → **一致**

| 位置 | 代码 |
|---|---|
| 旧 `core.js:473` | `gainBlock(C, Math.max(0, e.block + bonus + (C.buffs.dexterity \|\| 0)));` |
| 新 `web:5942` | `gainBlock(C, Math.max(0, e.block + bonus + (noBonus ? 0 : (C.buffs.dexterity \|\| 0))));` |

`no_bonus = false` 时括号里就是 `C.buffs.dexterity || 0`，与旧版相同；`bonus` 的推导演算见第 1 条，同前提下同值。

**前提边界**：`no_bonus = true` 时敏捷不加成。全池唯一 `no_bonus` 卡 `anm_0053` 无 `block` 字段，当前数据下不触发。

### 第 3 条 · 有 `anmin_mark` 的协议卡还能正常激活 → **一致**

| 检查点 | 旧 | 新 | 比对 |
|---|---|---|---|
| 重复激活拒绝 | `core.js:364` | `web:5813` | 逐字一致 |
| 结算后激活 | `core.js:392` | `web:5852` | 逐字一致 |
| `activateProtocol` 函数体 | `core.js:959–963` | `web:6550–6554` | 逐字一致（5 行全同） |

新增的拦截点在 `web:5792–5793`：

```js
const partCost = card.part_cost || 0;
if (partCost && (C.parts || 0) < partCost) return { ok:false, ... };
```

全池带 `anmin_mark` 的卡只有 **1 张**：`u_0016` 越权的批文（`shared`，`protocol:'purge'`，`energy:1`，**无 `part_cost`**）。`partCost = 0` → `if (0 && ...)` 短路，不拦截。

新增的 `C._playingCard`（5836/5838）、`growOnBefore`（5822/5841）对无 `mech_grow` 的协议卡不产生副作用。

### 第 4 条 · 敌人 `defend` 意图行为不变 → **一致**

| 位置 | 代码 |
|---|---|
| 旧 `core.js:768–770` | `} else if (it.type === 'defend') { e.block += it.value; log(C, e.name + ' 合拢了。'); }` |
| 新 `web:6350–6357` | 同样两行，之后追加 `if (C.buffs.enemyDefendDraw) { draw(C, C.buffs.enemyDefendDraw); log(...); }` |

`enemyDefendDraw` 只由 `anm_0055` 的 `enemy_defend_draw` special 设置（`web:6033`）。不带该 buff 时 `C.buffs.enemyDefendDraw` 为 undefined → 分支不进，`e.block += it.value` 和日志完全照旧。

`enemyAct` 里其余新增内容也不改 defend 分支：
- `web:6291–6299` minion 分叉：只在 `e.isMinion` 时 return，真敌人不进入。
- `web:6305–6307` 攻击窃能量钩子：在 `it.type === 'attack'` 分支内（6302），且需 `enemyAtkEnergy`。
- `web:6324–6329` 子代理承伤转移：在攻击循环内，且需场上存在 minion。

### 第 5 条 · 回合开始能量 → **一致**

| 位置 | 代码 |
|---|---|
| 旧 `core.js:258` | `C.energy = Math.max(0, run.energyMax + (run.energyBonus \|\| 0) - (C.energyPenalty \|\| 0));` |
| 新 `web:5652` | `C.energy = Math.max(0, run.energyMax + (run.energyBonus \|\| 0) - (C.energyPenalty \|\| 0) + (C.nextTurnBonusEnergy \|\| 0));` |

`nextTurnBonusEnergy = 0` 时末项为 0，两式相同。新增的 5653–5656 行（日志 + 清零）包在 `if (C.nextTurnBonusEnergy)` 里，为 0 时不执行。

**注意**：任务书把旧行为简写成 `energyMax + energyBonus`，代码里其实还有 `- (C.energyPenalty || 0)`。这项在 `core.js:258` **本来就有**（`core.js:35` 的 `locked` 层规则会设 `C.energyPenalty = 1`），不是本次新增，不能算回归。

`beginTurn` 其余新增行：
- 5603 `C.discardedThisTurn = 0`（新计数器，不改能量）
- 5616–5622 悬浮体塞牌：只在 `C.floatingCount > 0` 时
- 5623–5635 子代理成长扣零件：只在有存活 minion 时，扣的是 `C.parts` 不是能量
- 5660 `C.buffs.mechGrow = false`：只清新增 buff

全部在能量算式之外或不改变该算式。

## 汇总

| # | 老行为 | 结论 | 前提条件 |
|---|---|---|---|
| 1 | 攻击牌 `damage + 连携 + strength` | **一致** | `runStrengthCarry = 0`、`no_bonus = false`、场上无 minion |
| 2 | 格挡牌 `block + 连携 + dexterity` | **一致** | `no_bonus = false` |
| 3 | `anmin_mark` 协议卡正常激活 | **一致** | 协议卡无 `part_cost`（全池仅 `u_0016`，确实无） |
| 4 | 敌人 defend 行为不变 | **一致** | 无 `enemyDefendDraw` buff、无 minion |
| 5 | 回合开始能量 = `energyMax + energyBonus` | **一致** | `nextTurnBonusEnergy = 0`（`energyPenalty` 是老项，两版都有） |

**5 条一致，0 条不一致，0 条无法判断。**

## 顺带发现（不属于五条，但读代码时撞到）

1. `web:5934` 的 `!x.isMinion` 过滤是本次新增的**唯一**改变了「老卡在某种局面下打谁」的地方：群体攻击不再打到子代理。这是有意设计（验证文档第 57 行），但当场上同时有子代理时，旧公式与新公式的**目标列表**不同；本项第 1 条判「一致」的前提之一是「无 minion」。
2. `no_bonus` 同时抑制连携、bright 层加成、力量、敏捷、purge 协议 +3（`web:5914/5925/5931/5942`），是全路径开关。当前只有 `anm_0053` 一张卡用它，且该卡既无 damage 也无 block，所以本次没有可观测的数值变化；**若以后给 `no_bonus` 卡加伤害/格挡，公式会与旧版不同**。
3. `core.js` 与 `web/index.html` 的历史漂移（`value` 优先 `v`、`exhaust` 双写法、锁死提示文案）不是本次改动；用 core.js 当基线时若不先剔除这三项，会误报成回归。

## 边界声明

- 【实测】全部结论为**逐行读源码**得出，行号指当前 `web/index.html` 与 `engine/core.js`；三个公共子函数用脚本逐行比对，确认逐字一致。
- 【未验证】没有运行游戏、没有跑测试；「一致」是**代码等价性判断**，不是运行时实测。
- 【未验证】`engine/core.js` 是旧副本而非「本次改动前一刻」的精确快照，两者存在上表列出的历史漂移；这些漂移已逐项辨认并排除，但不能排除还有未辨认的历史差异。
- 【未验证】没有 git，无法用 `git diff` 交叉验证改动清单；本次改动范围以 `_VERIFY_anmin_core_cards.md` 第三节的自述为准。
