# D5 · 卡牌关键词频次表

> 口径：effect 顶层键计数 + special 码计数（219 张，一卡一键计一次）。复算脚本内嵌 data/audit/。

## effect 顶层键

| 键 | 次数 | 备注 |
|---|---|---|
| target | 219 | 全卡必有（目标声明，非效果） |
| block | 68 | 主防御轴 |
| damage | 59 | 主输出轴 |
| hits | 59 | 多段标记 |
| draw | 55 | 过牌轴 |
| resonance_gain | 26 | 共振进项 |
| heal | 21 | 治疗轴 |
| gaze_cost | 15 | 凝视门槛（15 张） |
| resonance_cost | 7 | 共振消费（仅 7 张） |
| resonance_drain | 5 | 共振泄压（5 张） |
| gaze_gain | 2 | 加凝视（2 张） |

## special 码

| 码 | 次数 | 状态 |
|---|---|---|
| regenerate | 16 | ✅ 实装 |
| strength | 13 | ✅ 实装 |
| dexterity | 10 | ✅ 实装 |
| burn | 10 | ✅ 实装（覆盖语义） |
| resonance_lock | 5 | ✅ 实装 |
| retain | 5 | ✅ 实装（beginTurn） |
| exhaust | 3 | ✅ 实装（playCard） |
| thorns | 3 | ✅ 实装 |
| weak | 3 | ✅ 实装（×0.75） |
| gaze_reduce | 3 | ✅ 实装 |
| frail | 2 | ❌ **死状态**（dealToEnemy 不读，见 T447） |
| delete_random | 1 | ✅ 实装（唯一张 trem_0022） |
| poison | 1 | ✅ 实装（唯一张 anm_0039） |
| rule_bypass | 1 | ✅ 实装（唯一张 share_0001） |
| resonance_gain | 1 | ❌ **无 case**（u_0009 专用，落 default 红字） |

## 只用 1~2 次的键/码（死机制候选）

- `gaze_gain`（2 次）：加凝视的主动进项只有 2 张——凝视经济的「主动轴」几乎不存在，全靠 mark 代价与事件。
- `resonance_drain`（5 次）：泄压阀太薄，对照 L6 起必然过载（resource_curve.md）。
- special `frail`（2 次）：**已证实死状态**——两张卡的白挂件。
- special `resonance_gain`（1 次）：**已证实无 case**——u_0009 的半边效果。
- special `poison` / `rule_bypass` / `delete_random`（各 1 次）：单卡专属机制——要么是「为一张卡写的机制」，要么那张卡就是机制展示位。
- effect `resonance_cost`（7 次）：不算死机制但消费端薄——共振经济的「花」比「攒」少一个数量级（攒 26 张卡+每回合自动）。
