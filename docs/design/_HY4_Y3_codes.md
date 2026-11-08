# HY4 · Y3 新 special code 使用率审计

> 2026-11-06 02:38。脚本：`tools/hy4_special_codes.js`（共用 `tools/hy4_common.js`）。
> 运行：`node tools/hy4_special_codes.js` / `--json`。

## 口径

| 项 | 值 |
|---|---|
| 卡池键 | `diver` 57 + `tremor` 57 + `anmin` 54 + `cangmin` 47 + `shared` 11 = **226 张** |
| 扫的字段 | `effect.special[].code` + `upgrade.effect.special[].code` |
| 不计入 | `enemies` / `relics` / `events` / `layers` / `*Enemies` / `*Relics` / `*Events`（不是卡牌） |
| 扫出 distinct code | **24 个** |
| 引擎 `applySpecial` 的 case | **24 个**（`web/index.html` 5959 行起） |
| `cardDesc` 映射 key | **21 个**（8434 行起） |

> 任务书写「扫全部 219 张」。219 是加入核心卡之前的数字；`_VERIFY_anmin_core_cards.md` 记两轮共新增 7 张核心卡（47 → 54），219 + 7 = **226**。本项按实际 226 张计。

## 一、白名单 8 个：每个 code 出现在几张卡里 / 是谁

「合并卡数」= 主效果或升级效果任一处出现即计 1 张卡，按卡 id 去重。

| code | 主效果卡数 | 升级效果卡数 | 合并卡数 | 卡 id |
|---|---|---|---|---|
| `mech_grow` | 1 | 1 | 1 | anm_0051 |
| `perm_strength` | 1 | 1 | 1 | anm_0054 |
| `energy_gain` | 1 | 2 | 2 | anm_0056, anm_0057 |
| `energy_on_enemy_attack` | 1 | 0 | 1 | anm_0055 |
| `enemy_defend_draw` | 1 | 0 | 1 | anm_0055 |
| `discard_hand` | 1 | 1 | 1 | anm_0057 |
| `parts_from_discard` | 1 | 1 | 1 | anm_0057 |
| `random_effect` | **0** | **0** | **0** | （无） |

**8 个 code 共覆盖 6 张卡**（0051 / 0054 / 0055 / 0056 / 0057，0057 用 3 个 code），全部集中在黯民。

## 二、写了但一次都没用上的 code

⚠️ **`random_effect`：卡池数据里 0 张卡使用。**

但不是死机制：`web/index.html` 5718–5731 行 `makeFloatingToken()` 动态生成的「悬浮触发」牌带 `effect.special:[{code:'random_effect'}]`。这张牌由 `beginTurn`（5618–5621 行）按 `C.floatingCount` 每回合塞进手牌，带 `_token: true`、不进牌组，所以**它只存在于运行时，不在 RAW 卡池里**。

结论：按任务书给的「从 RAW 里扫」口径，它是 0 次；按「整个游戏有没有用到」口径，它被 1 种运行时牌使用（每次打出触发 6036–6050 行的 5 选 1 随机池）。两种口径都要写清，不能只说「没用上」。

## 三、有没有卡用了白名单外的 code

**有，17 个，全部标 ⚠️。** 分三类：

### ⚠️ A 类：老 code，白名单外但合法（13 个）

这批是核心卡落地前就存在的 code，白名单只收「本次新增」，所以它们必然在白名单外。引擎有 case、卡面有中文。

| code | 卡数 | 卡 id | 引擎 | cardDesc |
|---|---|---|---|---|
| ⚠️ `burn` | 10 | dive_0033, dive_0034, trem_0017, trem_0023, trem_0024, trem_0080, anm_0011, cng_0034, u_0008, u_0012 | 有 | 有 |
| ⚠️ `delete_random` | 1 | trem_0022 | 有 | 有 |
| ⚠️ `dexterity` | 10 | dive_0007, dive_0017, dive_0052, trem_0020, trem_0058, trem_0067, anm_0016, anm_0050, cng_0050, u_0011 | 有 | 有 |
| ⚠️ `frail` | 3 | dive_0022, trem_0034, anm_0055 | 有 | 有 |
| ⚠️ `gaze_reduce` | 3 | trem_0027, trem_0029, u_0009 | 有 | 有 |
| ⚠️ `poison` | 1 | anm_0039 | 有 | 有 |
| ⚠️ `regenerate` | 16 | dive_0005, dive_0018, dive_0032, dive_0037, dive_0038, dive_0076, trem_0014, trem_0015, trem_0016, trem_0031, trem_0033, trem_0035, anm_0040, anm_0041, cng_0028, cng_0042 | 有 | 有 |
| ⚠️ `resonance_lock` | 5 | dive_0016, dive_0023, trem_0019, anm_0020, anm_0027 | 有 | 有 |
| ⚠️ `retain` | 6 | dive_0081, trem_0001, trem_0018, trem_0039, trem_0082, anm_0043 | 有 | 有 |
| ⚠️ `strength` | 13 | dive_0017, dive_0020, dive_0035, dive_0056, dive_0075, trem_0044, trem_0058, trem_0067, anm_0015, anm_0035, anm_0041, anm_0050, cng_0019 | 有 | 有 |
| ⚠️ `thorns` | 3 | dive_0019, dive_0065, cng_0025 | 有 | 有 |
| ⚠️ `weak` | 4 | dive_0030, anm_0055, cng_0037, u_0013 | 有 | 有 |
| ⚠️ `exhaust` | 3 | dive_0003, trem_0070, trem_0071 | 有（空 case，由 playCard 5857 处理） | 无 m 映射，但 8467 行独立显示「消耗」 |

### ⚠️ B 类：本次新增、但任务书白名单漏收（2 个）

| code | 卡数 | 卡 id | 引擎 case | cardDesc | 说明 |
|---|---|---|---|---|---|
| ⚠️ `floating_body` | 1 | anm_0053 悬浮体 | 6052 行有 | 有 | 第二轮重做悬浮体时新增，白名单是 8 个 code 的第一轮清单 |
| ⚠️ `summon_minion` | 1 | anm_0052 子代理 | 6057 行有 | **无** | 第二轮新增的召唤物 code，卡面什么都不显示 |

### ⚠️ C 类：真问题（2 个）

| code | 卡数 | 卡 id | 问题 |
|---|---|---|---|
| ⚠️ `resonance_gain` | 1 | u_0009（倒转圣痕，含升级版共 2 处 special） | **引擎 `applySpecial` 没有这个 case**（24 个 case 里无它），会落进 6063 行 default 分支打「未实现」红字；`cardDesc` 也无映射。数据在 `effect.special` 里，但引擎只认顶层 `e.resonance_gain`（5947 行）→ 这张卡的「共振 +3 / +4」永远不会生效，且卡面不显示。**这是老问题，不是本次改动引入的**（`engine/core.js` 旧副本同样无此 case），但既然全池扫到了就记在这里。 |
| ⚠️ `rule_bypass` | 1 | share_0001（强行供能，主+升级共 2 处） | 引擎 5979 行有 case，`cardDesc` 无映射 → 卡面不显示「这一回合层规则压不住」，但效果会生效。 |

## 四、总数对账

脚本只从卡池构建 `stat`，不会替白名单补行，所以「全池总表 24 行」= RAW 里实际出现的 24 个 code，`random_effect` 不在其中。

| 分类 | 个数 | 明细 |
|---|---|---|
| 卡池实际 distinct code | **24** | 脚本总表 24 行 |
| └ 白名单内且卡池用到 | **7** | mech_grow, perm_strength, energy_gain, energy_on_enemy_attack, enemy_defend_draw, discard_hand, parts_from_discard |
| └ ⚠️ 白名单外 | **17** | A 类 13 + B 类 2 + C 类 2 |
| 白名单内、卡池 0 次 | **1** | `random_effect`（只由运行时 `makeFloatingToken()` 使用） |
| 全游戏涉及的不同 code 名 | **25** | 24 + `random_effect` |

24 = 7 + 17；25 = 8（白名单）+ 17（白名单外）。两式自洽。

## 五、结论

1. 白名单 8 个中 **7 个在卡池里用上了**，`random_effect` 0 次但由运行时 token 使用。
2. 不存在「白名单外 code 被引擎漏实现」的**新**问题 —— 唯一漏实现的 `resonance_gain`（u_0009）是历史遗留。
3. 本次新增但白名单漏收 2 个：`floating_body`、`summon_minion`；后者还缺卡面中文（Y4 详述）。
4. ⚠️ 白名单外共 17 个 code：13 个老 code 合法、2 个本次新增漏收（`floating_body` / `summon_minion`）、2 个有缺陷（`resonance_gain` 引擎无 case、`rule_bypass` 卡面无中文）。

## 边界声明

- 【实测】数字来自 `node tools/hy4_special_codes.js` 实跑；引擎 case 集合由脚本从 `function applySpecial` 函数体内正则抽取 `case 'xxx':`，cardDesc key 由 `const m = {...}` 抽取。
- 【未验证】运行时是否真的触发每个 code 未验证（没开浏览器）；本项只统计**数据里写了几次、源码里有没有对应分支**。
- 引擎 case 集合用正则从函数体抽取，只覆盖 `switch` 里的 `case '...'`；若某 code 在 `applyCardEffect` 顶层字段分支里处理（如 `resonance_gain`），不算 `applySpecial` 的 case，文档已单独说明。
