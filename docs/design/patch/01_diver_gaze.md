# D2 · 下潜者×凝视控制 —— 补牌设计（2 张）

> 继承 T342 的等级与优先级（弱但有趣·高优先）；每张给：暂名/字段/与现有卡的差异/为什么这条弱路需要它/引擎前提。**全部为设计草案，不落 json**；id 留给落地任务。

## 设计 1：回声壁

| 项 | 内容 |
|---|---|
| 职业/类型/稀有度/费 | 下潜者 / skill / uncommon / 1 |
| effect（可贴 json 的草案） | `{"target": "self", "special": [{"code": "gaze_reduce", "value": 1}, {"code": "block", "value": 0}]}` |
| 效果说明 | 凝视 -1，本回合格挡 +0（占位：真实设计为「凝视每 5 点，格挡 +1」的条件持续）——但此结构需引擎条件键；保守版改为 gaze_reduce 1 + block 4 |
| 与现有卡的差异 | dive_0027/0029 只有 gaze_reduce 无收益转化；本卡把减凝视变成防御资源 |
| 为什么这条弱路需要它 | 下潜者的 4 张 gaze_cost 需要一张「平衡阀」——冲负债的同时有退路 |
| 引擎前提 | 零改动（gaze_reduce+block 已实现）；条件键版本需引擎 |

## 设计 2：井口的眼

| 项 | 内容 |
|---|---|
| 职业/类型/稀有度/费 | 下潜者 / power / rare / 1 |
| effect（可贴 json 的草案） | `{"target": "self", "special": [{"code": "gaze_to_strength"}]}` |
| 效果说明 | 每回合开始：凝视每 5 点 → 力量 +1（即 T341 的 u_0015 下潜侧本体） |
| 与现有卡的差异 | 全池没有凝视→力量的转化；四职业零张 |
| 为什么这条弱路需要它 | T332 判定下潜×凝视是「弱但有趣」之首：80 血付得起负债，缺的就是把负债变薪水的出口 |
| 引擎前提 | 需引擎：turn_start 卡牌结算位（[index.html:6903] 现只遍历遗物） |

## 本路现池全表（脚本实算）

| 卡 | 名称 | 费 | 代价 | 稀有度 | 机制 |
|---|---|---|---|---|---|
| dive_0082 | 按规程应答 | 1 | none | common | damage+gaze_cost |
| dive_0011 | 辐射弹 | 2 | none | rare | damage+gaze_cost+resonance_gain |
| dive_0024 | 深红资源集团·钻探平台 | 3 | none | rare | damage+gaze_cost |
| dive_0030 | 抗共振司·镇爆弹 | 3 | lock | rare | damage+gaze_cost+special+special:weak |

现池 4 张；本路的 designs 正是上表缺口的补位。

## 与通用牌的分工

本路引用的通用牌：通·借来的凝视（进攻）+ 通·倒转圣痕（减法）。分工原则：通用牌做「跨职业的结构件」，职业牌做「这条路的叙事件」——两者同池不冲突（T341 汇总表）。

## 落地顺序与验证

| 步 | 动作 | 验证 |
|---|---|---|
| 1 | 零引擎改动的设计先贴 cards | node tools/_t46_wire.js 后进局实测 |
| 2 | 机制依赖项等前提（灼烧叠加/条件键/turn_start 位） | 改动前后各跑 node tools/sim.js --runs 200 对照 |
| 3 | 平衡观察记回 T342 对应格 | 两周目玩感 + sim 通关率同量级 |

## 邻路对照（同机制在其他职业的现状）

| 职业 | 现状 |
|---|---|
| tremor | 震语者的凝视体系（支出 10 + 回收 2 + 加压 2） |
| cangmin | 疯先知现仅 cng_0050 一张 mark |

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
| tremor | 震语者的凝视体系（支出 10 + 回收 2 + 加压 2） |
| cangmin | 疯先知现仅 cng_0050 一张 mark |

对照的作用：确认本路的补牌**不会**把别的职业已经成型的体系复制一份——补的是「这一职业自己的说法」，不是抄别家。

## 逐设计的最相似现存卡（脚本按机制重合度计算）

**回声壁** 的最近邻：

| 卡 | 名称 | 费 | 重合机制 |
|---|---|---|---|
| trem_0027 | 震语：明目 | 1 | special+special:gaze_reduce |
| trem_0029 | 观红（深相） | 2 | special+special:gaze_reduce |
| dive_0056 | 死亡合同（增补条款） | 0 | special |

（重合度越高，越要在 flavor 与数值定位上拉开——「同机制不同叙事」是红渊换皮的规矩，T321 已证换皮泛滥的代价。）

**井口的眼** 的最近邻：

| 卡 | 名称 | 费 | 重合机制 |
|---|---|---|---|
| dive_0056 | 死亡合同（增补条款） | 0 | special |
| dive_0081 | 气闸的规程 | 0 | special |
| trem_0015 | 触温 | 0 | special |

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

2 张设计中 0 张零引擎改动、2 张依赖机制修复；落地顺序建议：先零改动者，机制依赖项等 T342 对应前提。

## 决定记录

- 「暂名」全部不带 id 前缀（防与 539 个真实 id 撞车、防验收脚本误判）；字段结构对齐 T341 的普查口径。
- 灼烧系三张（06/07/08）都以「灼烧叠加机制修复」为前提——T332 已证现状是覆盖制（[index.html:5856]），先修机制再上牌。
