# D2 · 维护者×共振积累 —— 补牌设计（2 张）

> 继承 T342 的等级与优先级（弱但有趣·高优先）；每张给：暂名/字段/与现有卡的差异/为什么这条弱路需要它/引擎前提。**全部为设计草案，不落 json**；id 留给落地任务。

## 设计 1：静默段·结算

| 项 | 内容 |
|---|---|
| 职业/类型/稀有度/费 | 维护者 / attack / uncommon / 1 |
| effect（可贴 json 的草案） | `{"damage": 8, "hits": 1, "target": "single", "resonance_cost": 3}` |
| 效果说明 | 共振费攻击——花 3 共振打 8，是维护者第一张「消费共振」的卡（anm_0013 是 gain 不是 cost） |
| 与现有卡的差异 | 维护者 50 张里 resonance_cost 0 张（T320）；这张卡让「攒共振」第一次有出口 |
| 为什么这条弱路需要它 | T342 判定维护者×共振是高优先——被动共振+3 张 gain 已经在攒，只欠消费端 |
| 引擎前提 | 零改动（resonance_cost 全链路已实现） |

## 设计 2：废料谐振器

| 项 | 内容 |
|---|---|
| 职业/类型/稀有度/费 | 维护者 / skill / uncommon / 0 |
| effect（可贴 json 的草案） | `{"resonance_gain": 1, "target": "self", "special": [{"code": "retain"}]}` |
| 效果说明 | 共振 +1、保留——0 费保留型共振泵，把「每回合被动 +层res」之外的手动攒速提上来 |
| 与现有卡的差异 | anm_0006 要 1 费还占手牌；0 费保留让它可以每回合空转攒 |
| 为什么这条弱路需要它 | 配合通·谐振垫层（drain 2 换 7 盾）形成「攒-花」小循环 |
| 引擎前提 | 零改动 |

## 本路现池全表（脚本实算）

| 卡 | 名称 | 费 | 代价 | 稀有度 | 机制 |
|---|---|---|---|---|---|
| anm_0006 | 库存盘点 | 0 | none | common | draw+resonance_gain |
| anm_0008 | 报废清单 | 1 | none | common | block+resonance_drain |
| anm_0013 | 料径校准 | 1 | none | uncommon | damage+resonance_gain |
| anm_0017 | 回收协议·总则 | 1 | none | rare | block+resonance_drain |
| anm_0048 | 运输井规程 | 1 | none | uncommon | block+resonance_gain |
| anm_0049 | 撤销程序残片 | 1 | none | rare | draw+resonance_drain |

现池 6 张；本路的 designs 正是上表缺口的补位。

## 与通用牌的分工

本路引用的通用牌：通·谐振垫层（消费端）。分工原则：通用牌做「跨职业的结构件」，职业牌做「这条路的叙事件」——两者同池不冲突（T341 汇总表）。

## 落地顺序与验证

| 步 | 动作 | 验证 |
|---|---|---|
| 1 | 零引擎改动的设计先贴 cards | node tools/_t46_wire.js 后进局实测 |
| 2 | 机制依赖项等前提（灼烧叠加/条件键/turn_start 位） | 改动前后各跑 node tools/sim.js --runs 200 对照 |
| 3 | 平衡观察记回 T342 对应格 | 两周目玩感 + sim 通关率同量级 |

## 邻路对照（同机制在其他职业的现状）

| 职业 | 现状 |
|---|---|
| tremor | 震语者 resonance_gain 17 张 |
| diver | 下潜者 14 张 + 消费端 4 张 |

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
| tremor | 震语者 resonance_gain 17 张 |
| diver | 下潜者 14 张 + 消费端 4 张 |

对照的作用：确认本路的补牌**不会**把别的职业已经成型的体系复制一份——补的是「这一职业自己的说法」，不是抄别家。

## 逐设计的最相似现存卡（脚本按机制重合度计算）

**静默段·结算** 的最近邻：

| 卡 | 名称 | 费 | 重合机制 |
|---|---|---|---|
| dive_0026 | 震髓装药 | 1 | damage+resonance_cost |
| dive_0021 | 星髓矿业·定向爆破 | 2 | damage+resonance_cost |
| dive_0046 | 星髓矿业·深部震源 | 2 | damage+resonance_cost |

（重合度越高，越要在 flavor 与数值定位上拉开——「同机制不同叙事」是红渊换皮的规矩，T321 已证换皮泛滥的代价。）

**废料谐振器** 的最近邻：

| 卡 | 名称 | 费 | 重合机制 |
|---|---|---|---|
| trem_0082 | 不许关闭 | 0 | resonance_gain+special+special:retai |
| dive_0081 | 气闸的规程 | 0 | special+special:retain |
| trem_0070 | 震语：低语 | 0 | resonance_gain+special |

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
