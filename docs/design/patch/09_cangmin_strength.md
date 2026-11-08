# D2 · 疯先知×力量成长 —— 补牌设计（2 张）

> 继承 T342 的等级与优先级（弱但可行·中优先）；每张给：暂名/字段/与现有卡的差异/为什么这条弱路需要它/引擎前提。**全部为设计草案，不落 json**；id 留给落地任务。

## 设计 1：醒来的拳头

| 项 | 内容 |
|---|---|
| 职业/类型/稀有度/费 | 疯先知 / power / uncommon / 1 |
| effect（可贴 json 的草案） | `{"target": "self", "special": [{"code": "strength", "value": 1}], "dream": false}` |
| 效果说明 | 醒侧力量 +1——cng_0019 是它现在的唯一同伴 |
| 与现有卡的差异 | cng strength 仅 cng_0019 一张；本卡把乘区从 1 张变成 2 张 |
| 为什么这条弱路需要它 | 疯先知伤害 14 张的数量够、缺放大器；力量是全游戏最通用的乘区 |
| 引擎前提 | 零改动 |

## 设计 2：梦的重量

| 项 | 内容 |
|---|---|
| 职业/类型/稀有度/费 | 疯先知 / power / rare / 2 |
| effect（可贴 json 的草案） | `{"target": "self", "special": [{"code": "strength", "value": 2}], "dream": true}` |
| 效果说明 | 梦侧力量 +2——「梦里打人用想念」，想念有重量 |
| 与现有卡的差异 | dream 侧 power 0 张（cng 的 power 全在醒侧）；本卡给梦境流一个乘区理由 |
| 为什么这条弱路需要它 | 双世界流的内部平衡：醒侧有倍攻手段、梦侧只有回复，力量补进梦侧让两边都有打法 |
| 引擎前提 | 零改动 |

## 本路现池全表（脚本实算）

| 卡 | 名称 | 费 | 代价 | 稀有度 | 机制 |
|---|---|---|---|---|---|
| cng_0050 | 疯先知的笔记 | 1 | mark | special | special+special:dexterity |
| cng_0019 | 王权梦 | 2 | none | rare | special+special:strength |

现池 2 张；本路的 designs 正是上表缺口的补位。

## 与通用牌的分工

本路引用的通用牌：通·借来的凝视 + 通·守夜人的钟 + 通·活水引泉。分工原则：通用牌做「跨职业的结构件」，职业牌做「这条路的叙事件」——两者同池不冲突（T341 汇总表）。

## 落地顺序与验证

| 步 | 动作 | 验证 |
|---|---|---|
| 1 | 零引擎改动的设计先贴 cards | node tools/_t46_wire.js 后进局实测 |
| 2 | 机制依赖项等前提（灼烧叠加/条件键/turn_start 位） | 改动前后各跑 node tools/sim.js --runs 200 对照 |
| 3 | 平衡观察记回 T342 对应格 | 两周目玩感 + sim 通关率同量级 |

## 邻路对照（同机制在其他职业的现状）

| 职业 | 现状 |
|---|---|
| diver | strength 7 张 |
| anmin | strength 4 张 |
| tremor | strength 4 张 |

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
| diver | strength 7 张 |
| anmin | strength 4 张 |
| tremor | strength 4 张 |

对照的作用：确认本路的补牌**不会**把别的职业已经成型的体系复制一份——补的是「这一职业自己的说法」，不是抄别家。

## 逐设计的最相似现存卡（脚本按机制重合度计算）

**醒来的拳头** 的最近邻：

| 卡 | 名称 | 费 | 重合机制 |
|---|---|---|---|
| dive_0056 | 死亡合同（增补条款） | 0 | special+special:strength |
| dive_0017 | 星髓矿业·深地车 | 1 | special+special:strength |
| dive_0020 | 黑曜采掘·加班条例 | 1 | special+special:strength |

（重合度越高，越要在 flavor 与数值定位上拉开——「同机制不同叙事」是红渊换皮的规矩，T321 已证换皮泛滥的代价。）

**梦的重量** 的最近邻：

| 卡 | 名称 | 费 | 重合机制 |
|---|---|---|---|
| dive_0056 | 死亡合同（增补条款） | 0 | special+special:strength |
| dive_0017 | 星髓矿业·深地车 | 1 | special+special:strength |
| dive_0020 | 黑曜采掘·加班条例 | 1 | special+special:strength |

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

2 张设计中 2 张零引擎改动、0 张依赖机制修复；落地顺序建议：先零改动者，机制依赖项等 T342 对应前提。

## 决定记录

- 「暂名」全部不带 id 前缀（防与 539 个真实 id 撞车、防验收脚本误判）；字段结构对齐 T341 的普查口径。
- 灼烧系三张（06/07/08）都以「灼烧叠加机制修复」为前提——T332 已证现状是覆盖制（[index.html:5856]），先修机制再上牌。
