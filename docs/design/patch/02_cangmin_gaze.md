# D2 · 疯先知×凝视控制 —— 补牌设计（2 张）

> 继承 T342 的等级与优先级（弱但有趣·高优先）；每张给：暂名/字段/与现有卡的差异/为什么这条弱路需要它/引擎前提。**全部为设计草案，不落 json**；id 留给落地任务。

## 设计 1：梦里的眼睛

| 项 | 内容 |
|---|---|
| 职业/类型/稀有度/费 | 疯先知 / skill / uncommon / 1 |
| effect（可贴 json 的草案） | `{"target": "self", "dream": true, "special": [{"code": "gaze_gain", "value": 2}, {"code": "resonance_gain", "value": 1}]}` |
| 效果说明 | 凝视 +2、共振 +1——主动踩油门：疯先知用凝视换共振（配合通·倒转圣痕减回来） |
| 与现有卡的差异 | 全池 gaze_gain 仅 2 张且都是震语者；疯先知 0 张；本卡是它第一次主动碰凝视 |
| 为什么这条弱路需要它 | 疯先知没有任何资源语言（T320）；凝视+共振的双资源小循环是它接入体系成本最低的门 |
| 引擎前提 | 零改动（gaze_gain/resonance_gain 已实现）；dream 字段沿用 cangmin 惯例 |

## 设计 2：背面的祷文

| 项 | 内容 |
|---|---|
| 职业/类型/稀有度/费 | 疯先知 / skill / rare / 1 |
| effect（可贴 json 的草案） | `{"target": "self", "special": [{"code": "gaze_reduce", "value": 3}, {"code": "regenerate", "value": 2}]}` |
| 效果说明 | 凝视 -3 + 再生 2——把「被看的痕迹」转化成回血，正对 30 血职业的死穴 |
| 与现有卡的差异 | cng 现有 heal 9 张全是直接回复，没有「凝视转回复」的语义 |
| 为什么这条弱路需要它 | 疯先知×凝视格的防御半边；与通·借来的凝视（进攻半边）组成一攻一守 |
| 引擎前提 | 零改动 |

## 本路现池全表（脚本实算）

| 卡 | 名称 | 费 | 代价 | 稀有度 | 机制 |
|---|---|---|---|---|---|
| cng_0050 | 疯先知的笔记 | 1 | mark | special | special+special:dexterity |

现池 1 张；本路的 designs 正是上表缺口的补位。

## 与通用牌的分工

本路引用的通用牌：通·借来的凝视 + 通·倒转圣痕。分工原则：通用牌做「跨职业的结构件」，职业牌做「这条路的叙事件」——两者同池不冲突（T341 汇总表）。

## 落地顺序与验证

| 步 | 动作 | 验证 |
|---|---|---|
| 1 | 零引擎改动的设计先贴 cards | node tools/_t46_wire.js 后进局实测 |
| 2 | 机制依赖项等前提（灼烧叠加/条件键/turn_start 位） | 改动前后各跑 node tools/sim.js --runs 200 对照 |
| 3 | 平衡观察记回 T342 对应格 | 两周目玩感 + sim 通关率同量级 |

## 邻路对照（同机制在其他职业的现状）

| 职业 | 现状 |
|---|---|
| tremor | 震语者 14 张全体系 |
| diver | 下潜者 4 张 gaze_cost 孤岛 |

对照的作用：确认本路的补牌**不会**把别的职业已经成型的体系复制一份——补的是「这一职业自己的说法」，不是抄别家。

## 贴 json 前的字段核对单（每张设计都要过）

| 字段 | 核对点 |
|---|---|
| id | 唯一、不与 539 个现有 id 撞（grep cards/*.json） |
| class | 职业 id：diver/tremor/anmin/cangmin（本篇按路内职业） |
| type | attack/skill/power 三选一 |
| rarity | common/uncommon/rare（special 不给新卡） |
| veins | 五脉之一或空数组；双脉需带 T341 §四 的降级注记 |
| energy | 整数 0-3；对照本路价格带 |
| effect | 只用引擎已实现键（T341 §三 的清单反查） |
| cost_type | none 或 memory/vitality/mark/lock 四种 |
| flavor | 世界观一致（GLOSSARY 唯一写法） |
| upgrade | 数值为最终值、special 为追加（[engine/core.js:980]） |

## 邻路对照（同机制在其他职业的现状）

| 职业 | 现状 |
|---|---|
| tremor | 震语者 14 张全体系 |
| diver | 下潜者 4 张 gaze_cost 孤岛 |

对照的作用：确认本路的补牌**不会**把别的职业已经成型的体系复制一份——补的是「这一职业自己的说法」，不是抄别家。

## 逐设计的最相似现存卡（脚本按机制重合度计算）

**梦里的眼睛** 的最近邻：

| 卡 | 名称 | 费 | 重合机制 |
|---|---|---|---|
| dive_0056 | 死亡合同（增补条款） | 0 | special |
| dive_0081 | 气闸的规程 | 0 | special |
| trem_0015 | 触温 | 0 | special |

（重合度越高，越要在 flavor 与数值定位上拉开——「同机制不同叙事」是红渊换皮的规矩，T321 已证换皮泛滥的代价。）

**背面的祷文** 的最近邻：

| 卡 | 名称 | 费 | 重合机制 |
|---|---|---|---|
| trem_0015 | 触温 | 0 | special+special:regenerate |
| trem_0031 | 尝水 | 0 | special+special:regenerate |
| dive_0005 | 氧气再生器 | 1 | special+special:regenerate |

（重合度越高，越要在 flavor 与数值定位上拉开——「同机制不同叙事」是红渊换皮的规矩，T321 已证换皮泛滥的代价。）

## 贴 json 前的字段核对单（每张设计都要过）

| 字段 | 核对点 |
|---|---|
| id | 唯一、不与 539 个现有 id 撞（grep cards/*.json） |
| class | 职业 id：diver/tremor/anmin/cangmin（本篇按路内职业） |
| type | attack/skill/power 三选一 |
| rarity | common/uncommon/rare（special 不给新卡） |
| veins | 五脉之一或空数组；双脉需带 T341 §四 的降级注记 |
| energy | 整数 0-3；对照本路价格带 |
| effect | 只用引擎已实现键（T341 §三 的清单反查） |
| cost_type | none 或 memory/vitality/mark/lock 四种 |
| flavor | 世界观一致（GLOSSARY 唯一写法） |
| upgrade | 数值为最终值、special 为追加（[engine/core.js:980]） |

## 本路小结

2 张设计中 1 张零引擎改动、1 张依赖机制修复；落地顺序建议：先零改动者，机制依赖项等 T342 对应前提。

## 决定记录

- 「暂名」全部不带 id 前缀（防与 539 个真实 id 撞车、防验收脚本误判）；字段结构对齐 T341 的普查口径。
- 灼烧系三张（06/07/08）都以「灼烧叠加机制修复」为前提——T332 已证现状是覆盖制（[index.html:5856]），先修机制再上牌。
