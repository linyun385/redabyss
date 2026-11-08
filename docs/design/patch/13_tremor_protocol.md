# D2 · 震语者×协议流 —— 补牌设计（1 张）

> 继承 T342 的等级与优先级（弱但可行·中优先）；每张给：暂名/字段/与现有卡的差异/为什么这条弱路需要它/引擎前提。**全部为设计草案，不落 json**；id 留给落地任务。

## 设计 1：禁声令（代读）

| 项 | 内容 |
|---|---|
| 职业/类型/稀有度/费 | 震语者 / power / rare / 1 |
| effect（可贴 json 的草案） | `{"target": "self"}` |
| 效果说明 | 激活 silence（禁抽+驳敌方 buff [engine/core.js:772]）——对 31 处 buff 意图是精准克制 |
| 与现有卡的差异 | u_0016 是 purge 版；本卡是 silence 变体——两条协议各有流派适配（震语者的 memory 删牌早已习惯「失去」） |
| 为什么这条弱路需要它 | silence 驳 buff 对精英战（buff 意图集中区）是独有的战术开关 |
| 引擎前提 | 零改动（silence 效果已实现：[index.html:5757] 附近 draw 拦截、[engine/core.js:772] buff 驳回） |

## 本路现池全表（脚本实算）

| 卡 | 名称 | 费 | 代价 | 稀有度 | 机制 |
|---|---|---|---|---|---|
| trem_0009 | 震语：断脉 | 1 | memory | uncommon | damage |
| trem_0017 | 震语：焚名 | 1 | memory | common | damage+special+special:burn |
| trem_0042 | 震语：断忆 | 1 | memory | uncommon | damage |
| trem_0043 | 静底·焚忆 | 1 | memory | uncommon | draw |
| trem_0047 | 震台石碑（残诵） | 1 | memory | uncommon | resonance_gain |
| trem_0021 | 埋骨礼 | 2 | memory | uncommon | block |
| trem_0038 | 相石·满录 | 2 | memory | rare | draw+resonance_gain |
| trem_0044 | 相石·封忆 | 2 | memory | rare | special+special:strength |
| trem_0045 | 埋骨礼（合葬） | 2 | memory | uncommon | block |
| trem_0024 | 震语：熔名 | 3 | memory | rare | damage+special+special:burn |

现池 10 张；本路的 designs 正是上表缺口的补位。

## 与通用牌的分工

本路引用的通用牌：通·越权的批文（silence 变体）。分工原则：通用牌做「跨职业的结构件」，职业牌做「这条路的叙事件」——两者同池不冲突（T341 汇总表）。

## 落地顺序与验证

| 步 | 动作 | 验证 |
|---|---|---|
| 1 | 零引擎改动的设计先贴 cards | node tools/_t46_wire.js 后进局实测 |
| 2 | 机制依赖项等前提（灼烧叠加/条件键/turn_start 位） | 改动前后各跑 node tools/sim.js --runs 200 对照 |
| 3 | 平衡观察记回 T342 对应格 | 两周目玩感 + sim 通关率同量级 |

## 邻路对照（同机制在其他职业的现状）

| 职业 | 现状 |
|---|---|
| anmin | 协议母语 |
| diver | purge 版入口 |

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
| anmin | 协议母语 |
| diver | purge 版入口 |

对照的作用：确认本路的补牌**不会**把别的职业已经成型的体系复制一份——补的是「这一职业自己的说法」，不是抄别家。

## 逐设计的最相似现存卡（脚本按机制重合度计算）

**禁声令（代读）** 的最近邻：

| 卡 | 名称 | 费 | 重合机制 |
|---|---|---|---|

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

## 同费带对照（1 费卡 158 张，抽 5）

| 卡 | 名称 | 类型 | 机制 |
|---|---|---|---|
| anm_0001 | 现场回收 | skill | block |
| anm_0039 | 菌婪者组织样本 | attack | damage+special |
| cng_0039 | 光导 | skill | block+draw |
| dive_0042 | 震髓探测器（阵列） | skill | draw+resonance_gain |
| trem_0016 | 喷息·热池边 | skill | block+special |

trem_0042（1费 伤害+memory）是震语者「代价即机制」的样本——本路设计卡与其**争的是同一个能量预算**，差异必须落在机制（见各设计的「与现有卡的差异」行），不能落在数值。

### trem_0042 的出图提示词摘录（本路最接近的现存卡）

> 地底铁皮墙的墙角，一块巴掌大的扁平铸铁盖板斜靠在墙边。这块铸铁盖板是画面的主体，占满画面中部，表面有一片被工具刮得发亮的凹痕，边缘有细小的裂纹和锈迹，几处砸扁的边角和歪斜的焊缝清晰可见。一条铁链与挂钩从上方垂下，钩在盖板的一角，链条上挂着几…

设计卡若真做出来，其提示词要沿这份文本的工艺语系（石版排线/血红底/单一朱红强调）另写，并把主体从「震语：断忆」换成设计卡的新对象——**不得复用同一段主体描述**（T321 换皮教训）。

## 本路小结

1 张设计中 0 张零引擎改动、1 张依赖机制修复；落地顺序建议：先零改动者，机制依赖项等 T342 对应前提。

## 决定记录

- 「暂名」全部不带 id 前缀（防与 539 个真实 id 撞车、防验收脚本误判）；字段结构对齐 T341 的普查口径。
- 灼烧系三张（06/07/08）都以「灼烧叠加机制修复」为前提——T332 已证现状是覆盖制（[index.html:5856]），先修机制再上牌。
