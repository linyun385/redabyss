# T443 · 层规则全表（引擎实现逐条对账）

> 数据源：**层规则不在 RAW.layers 里**（那里只有 id/name/nodes/rows）——全部规则字段硬编码在
> `engine/core.js:18-25`，web 内联副本同步在同表（`web/index.html:5386` 附近）。
> 本表把每条规则的**引擎实现行号**列全。行号为 2026-11-05 快照。复算：`grep -n "rule ===" engine/core.js`。
> 这份表是「层规则影响脉象加成」的对账底稿。

## 1. 层定义（engine/core.js:18-25，逐字段）

| 层 | 名字 | 协议号 | res（共振/回合） | mode（共振反应） | rule（层规则） |
|---|---|---|---|---|---|
| 1 | 地表死寂区 | L0–L1 | 1 | dormant | `no_light` |
| 2 | 外层冷洞 | L1 | 2 | dormant | `cold` |
| 3 | 干旱空洞区 | L1–L2 | 3 | steady | `dry` |
| 4 | 稳定空洞海 | L2–L3 | 4 | pulse | `bright` |
| 5 | 热泉裂带 | L2–L4 | 5 | resonant | `heat_tick` |
| 6 | 辐射矿石区 | L4–L5 | 6 | overload | `rad_tick` |
| 7 | 核心高热区 | L5 | 7 | locked | `burn_hand` |
| 8 | 红渊核心 | L6 | 8 | void | `final` |

## 2. rule 逐条实现（哪个字段控制、代码在哪）

| rule | 层 | 玩家看到的效果 | 引擎实现 | 控制字段 |
|---|---|---|---|---|
| `no_light` | L1 | **光脉牌整张失效**（能量照扣，事件栏红字说明）——除非 `C.ruleBypass`（share_0001 强行供能） | `core.js:451-456`（失效分支）；`:452` 读 `C.ruleBypass` | `layer.rule` + 卡 `veins` 含 light |
| `cold` | L2 | **每回合第一张牌 +1 费**（手冻僵了） | `core.js:408-413`（`!C.playedThisTurn` 时 `c += 1`）；首回合有红字提示 | `layer.rule` + 出牌计数 `C.playedThisTurn` |
| `dry` | L3 | **水脉牌费 +1**（第一次有提示） | `core.js:406`（`c += 1`）；`:339-341` 提示 `_dryWarned` | `layer.rule` + 卡 `veins` 含 water |
| `bright` | L4 | **光脉牌效果 +2**（伤害和格挡都吃） | `core.js:458` `bonus += 2` → `:461` 进伤害、`:464` 进格挡 | `layer.rule` + 卡 `veins` 含 light |
| `heat_tick` | L5 | 每 3 回合掉 2 血（灼烧计数） | `core.js:274-278`（`C.heat % 3 === 0`） | `layer.rule` + 计数器 `C.heat` |
| `rad_tick` | L6 | 每回合掉 1 血 + **抽 1 张**（辐射给牌） | `core.js:279-282` | `layer.rule` |
| `burn_hand` | L7 | **每回合烧掉随机 1 张手牌**（进消耗堆，本场不回） | `core.js:284-289` | `layer.rule` |
| `final` | L8 | **无实现（死字段）** | 全代码库无 `rule === 'final'` 处理器 | — |

⚠ **L8 的 rule='final' 是死字段**：第 8 层的实际效果全部来自 mode='void'（见下），`rule` 值没有任何代码读它。要么补实现要么删字段——报告，不改。

## 3. mode 逐条实现（共振阈值触发的层反应，core.js:29-37）

共振每回合 `+layer.res`（`core.js:243`），过 **10/20/30** 三档时触发一次 `MODE_REACTION[C.layer.mode].apply`（`core.js:303-309`）；共振 ≥30 每回合过载掉 `layer.res` 血（`:311-312`）。

| mode | 层 | 反应 | 引擎实现 |
|---|---|---|---|
| dormant | L1/L2 | 无反应 | `core.js:30` `apply: () => {}` |
| steady | L3 | 回血 3 | `core.js:31` |
| pulse | L4 | 全体敌人各 5 伤 | `core.js:32` |
| resonant | L5 | 抽 2 张 | `core.js:33` |
| overload | L6 | 全体敌人攻击 +3（1 回合） | `core.js:34` |
| locked | L7 | 本回合能量 -1 | `core.js:35` → `:258` 结算 energyPenalty |
| void | L8 | **脉连携加成锁死** | `core.js:36` 设 `veinLocked` → `:426` `veinChainBonus` 返回 0 |

## 4. 层规则 ↔ 脉象加成（本表核心）

| 影响方式 | 层 | 机制 | 对哪条脉 |
|---|---|---|---|
| **直接加成** | L4 bright | 光脉牌伤害/格挡 +2 | 光 |
| **直接禁用** | L1 no_light | 光脉牌整张失效（`ruleBypass` 可豁免） | 光 |
| **费用惩罚** | L3 dry | 水脉牌 +1 费（遗物 `mod.vein_cost` 可抵，`core.js:415-421`） | 水 |
| **费用惩罚** | L2 cold | 每回合第一张 +1 费（不限脉，但 0 费牌不受影响） | 全部（间接） |
| **连携锁死** | L8 void | `veinChainBonus` 归零——**同脉连打 +1/+2 的旧加成在第 8 层失效** | 全部 |
| **共振节奏** | 全层 | 每回合 +res（1~8 递增）→ 更快摸到 10/20/30 阈值与 30 过载 | 全部 |

**对脉象系统重构的落点**：T400 阶段 2 要把 `veinChain` 改造成 `veins[脉]` 等级——第 8 层 `veinLocked` 锁的就是这个函数（`:426`），改造时这个豁免位必须保留，否则 L8 的「红光消失」会静默失效。

## 5. 双副本同步检查

层定义存在两份：`engine/core.js:18-25` 与 `web/index.html:5386` 附近内联。本夜逐行比对**内容一致**（res/mode/rule/protocol 全同）。改层规则时两处必须同步（master/00 篇第 4 节铁律）。

## 6. 复算

```
grep -n "rule ===" engine/core.js   # 全部 rule 分支行号
grep -n "MODE_REACTION" engine/core.js
sed -n '18,25p' engine/core.js      # 层定义表
python -c "import json;d=json.load(open('data/audit/raw_all.json',encoding='utf-8'));print([l['name'] for l in d['layers']['layers']])"
```

注意：RAW.layers 里**没有** protocol/res/mode/rule 字段（只有 id/name/nodes/rows）——层数与名字来自数据，规则来自引擎硬编码。这个分裂本身就是对账要点。
