# D2 · 震语者×再生续航 —— 补牌设计（2 张）

> 继承 T342 的等级与优先级（弱但有趣·中优先）；每张给：暂名/字段/与现有卡的差异/为什么这条弱路需要它/引擎前提。**全部为设计草案，不落 json**；id 留给落地任务。

## 设计 1：涌喉·含泉

| 项 | 内容 |
|---|---|
| 职业/类型/稀有度/费 | 震语者 / skill / uncommon / 1 |
| effect（可贴 json 的草案） | `{"heal": 3, "target": "self", "veins_hint": "water"}` |
| 效果说明 | 直接回复 3——涌喉家族（水脉）第一张非 regen 的直接回复 |
| 与现有卡的差异 | 震语者 heal 0 张（T320）；trem_0033 的 regen 4 要等回合成长，本卡是即时止血 |
| 为什么这条弱路需要它 | T342：通·活水引泉一张不够撑「不治伤流」，需要水脉自家的止血位 |
| 引擎前提 | 零改动 |

## 设计 2：静底·守夜

| 项 | 内容 |
|---|---|
| 职业/类型/稀有度/费 | 震语者 / skill / rare / 2 |
| effect（可贴 json 的草案） | `{"block": 8, "target": "self", "special": [{"code": "regenerate", "value": 3}]}` |
| 效果说明 | 格挡 8 + 再生 3——静底家族的 regen 上限卡（现最大 trem_0033 的 4 点单发） |
| 与现有卡的差异 | 静底家族现有 regen 1-2 点；3 点+格挡合成让它成为该流的中坚 |
| 为什么这条弱路需要它 | 「不治伤流」需要一张能当回合牌打的高值 regen，而不是慢慢等 |
| 引擎前提 | 零改动 |

## 本路现池全表（脚本实算）

| 卡 | 名称 | 费 | 代价 | 稀有度 | 机制 |
|---|---|---|---|---|---|
| trem_0015 | 触温 | 0 | none | common | block+special+special:regenerate |
| trem_0031 | 尝水 | 0 | none | common | draw+special+special:regenerate |
| trem_0016 | 喷息·热池边 | 1 | none | common | block+special+special:regenerate |
| trem_0033 | 涌喉·水契 | 1 | none | uncommon | special+special:regenerate |
| trem_0073 | 静底·翻灰 | 1 | none | common | block+special+special:regenerate |
| trem_0035 | 尝水（深井） | 2 | none | rare | draw+special+special:regenerate |
| trem_0014 | 听地神脉搏 | 3 | lock | rare | gaze_cost+resonance_gain+special+special:reg |

现池 7 张；本路的 designs 正是上表缺口的补位。

## 与通用牌的分工

本路引用的通用牌：通·活水引泉（即时回复）。分工原则：通用牌做「跨职业的结构件」，职业牌做「这条路的叙事件」——两者同池不冲突（T341 汇总表）。

## 落地顺序与验证

| 步 | 动作 | 验证 |
|---|---|---|
| 1 | 零引擎改动的设计先贴 cards | node tools/_t46_wire.js 后进局实测 |
| 2 | 机制依赖项等前提（灼烧叠加/条件键/turn_start 位） | 改动前后各跑 node tools/sim.js --runs 200 对照 |
| 3 | 平衡观察记回 T342 对应格 | 两周目玩感 + sim 通关率同量级 |

## 邻路对照（同机制在其他职业的现状）

| 职业 | 现状 |
|---|---|
| anmin | 维护者 heal 7 + regen 2 |
| cangmin | 疯先知 heal 9 张 |

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
| anmin | 维护者 heal 7 + regen 2 |
| cangmin | 疯先知 heal 9 张 |

对照的作用：确认本路的补牌**不会**把别的职业已经成型的体系复制一份——补的是「这一职业自己的说法」，不是抄别家。

## 逐设计的最相似现存卡（脚本按机制重合度计算）

**涌喉·含泉** 的最近邻：

| 卡 | 名称 | 费 | 重合机制 |
|---|---|---|---|
| anm_0032 | 闭环利用 | 0 | heal |
| cng_0010 | 忆盐 | 0 | heal |
| cng_0012 | 母亲的祷文 | 0 | heal |

（重合度越高，越要在 flavor 与数值定位上拉开——「同机制不同叙事」是红渊换皮的规矩，T321 已证换皮泛滥的代价。）

**静底·守夜** 的最近邻：

| 卡 | 名称 | 费 | 重合机制 |
|---|---|---|---|
| trem_0015 | 触温 | 0 | block+special+special:regenerate |
| dive_0005 | 氧气再生器 | 1 | block+special+special:regenerate |
| dive_0018 | 墟盐 | 1 | block+special+special:regenerate |

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
