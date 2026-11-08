# HY4 · Y4 卡面描述映射完整性

> 2026-11-06 02:40。静态读源码，未开浏览器。脚本：`tools/hy4_carddesc.js`（共用 `tools/hy4_common.js`）。
> 映射表位置：`web/index.html` 第 **8434** 行 `function cardDesc`，表体 8450–8459 行 `const m = {...}`，共 **21** 项。
> 命中判断在 8460 行：`if (!m[s.code]) return;` —— **没有映射就直接跳过，卡面什么都不显示**（不是显示英文 code）。

## 表一 · 缺映射的 code

### 1a 白名单 8 个逐条核验

| code | 映射中文 | 卡池使用 | 判定 |
|---|---|---|---|
| `mech_grow` | 本回合每打一张牌得零件 | anm_0051 | ✅ 有中文 |
| `perm_strength` | 永久力量（跨战斗） | anm_0054 | ✅ 有中文 |
| `energy_gain` | 能量 | anm_0056, anm_0057（升级） | ✅ 有中文 |
| `energy_on_enemy_attack` | 敌方攻击时得能量 | anm_0055 | ✅ 有中文 |
| `enemy_defend_draw` | 敌方防御时抽牌 | anm_0055 | ✅ 有中文 |
| `discard_hand` | 弃光手牌 | anm_0057 | ✅ 有中文 |
| `parts_from_discard` | 每弃一张得零件 | anm_0057 | ✅ 有中文 |
| `random_effect` | 随机效果 | 卡池 0 张（运行时 token 用） | ✅ 有中文 |

**白名单内缺映射：0 个**（8/8 都有中文）。这一项任务书预期会有缺失，实际没有。

### 1b 全池实际用到、但卡面无中文的 code（真正的缺映射）

| code | 卡 id | 卡面表现 | 性质 |
|---|---|---|---|
| `summon_minion` | **anm_0052 子代理** | ⚠️ **什么都不显示** | 本次第二轮新增的卡，映射表没跟上。玩家只看到「零件 -5」，看不到会召唤出什么 |
| `rule_bypass` | share_0001 强行供能（主+升级） | ⚠️ **什么都不显示** | 老 code，效果生效（5979 行）但卡面无提示 |
| `resonance_gain` | u_0009 倒转圣痕（主+升级） | ⚠️ **什么都不显示** | 老 code，且引擎 `applySpecial` 无此 case（Y3 C 类），双重缺失 |
| `exhaust` | dive_0003, trem_0070, trem_0071 | ✅ 显示「消耗」，但**不走 m 表** | 8467 行独立分支 `if (e.exhaust || special 里有 exhaust) parts.push('消耗')`，所以不算缺显示 |

**结论：真正让玩家看不到效果的是前 3 个 code、4 张卡，其中 `summon_minion`（anm_0052）是这次改动新落地的卡。**

## 表二 · 死映射（映射表里有、白名单里没有的 code）

共 **13** 个。逐条列出，并给出「有没有卡在用」的判定 —— 任务书把「白名单外」直接叫死代码，这个口径不成立，见最后一列。

| code | 映射中文 | 卡池使用张数 | 判定 |
|---|---|---|---|
| `burn` | 灼烧 | 10 | 否，老 code 在用 |
| `delete_random` | 删除一张牌 | 1 | 否，老 code 在用 |
| `dexterity` | 敏捷 | 10 | 否，老 code 在用 |
| `floating_body` | 悬浮体（每回合多给 1 张触发牌） | 1（anm_0053） | 否，**本次新增**，只是没进 8 个 code 的白名单 |
| `frail` | 脆弱 | 3 | 否，老 code 在用 |
| `gaze_reduce` | 凝视 - | 3 | 否，老 code 在用 |
| `poison` | 中毒 | 1 | 否，老 code 在用 |
| `regenerate` | 再生 | 16 | 否，老 code 在用 |
| `resonance_lock` | 共振锁定 | 5 | 否，老 code 在用 |
| `retain` | 保留 | 6 | 否，老 code 在用 |
| `strength` | 力量 | 13 | 否，老 code 在用 |
| `thorns` | 荆棘 | 3 | 否，老 code 在用 |
| `weak` | 虚弱 | 4 | 否，老 code 在用 |

13 个全部有卡在用，**按「没人用」定义，死映射是 0 个**。白名单只收本次新增的 8 个 code，映射表却是全池共用的，所以「白名单外」是设计使然，不是死代码。

### 按「有没有卡用」重新定义死映射

| code | 映射中文 | 卡池使用 | 判定 |
|---|---|---|---|
| `random_effect` | 随机效果 | **0 张** | 唯一一个「映射表有、卡池 0 张卡用」的项。但**不是死代码**：`web/index.html` 5718–5731 行 `makeFloatingToken()` 生成的运行时牌用它，卡面会显示「随机效果」。按数据口径是死映射，按运行口径是活映射 |

## 两表汇总

| 表 | 个数 | 具体 code |
|---|---|---|
| 缺映射（白名单内） | 0 | （无；8 个逐条核验见 1a） |
| 缺映射（全池实际用到，卡面不显示） | **3** | `summon_minion`, `rule_bypass`, `resonance_gain` |
| 死映射（白名单外） | **13** | `burn`, `delete_random`, `dexterity`, `floating_body`, `frail`, `gaze_reduce`, `poison`, `regenerate`, `resonance_lock`, `retain`, `strength`, `thorns`, `weak` |
| 死映射（映射表有、卡池 0 张用） | 1 | `random_effect`（运行时 token 在用） |
| 映射表总项数 | 21 | 8（白名单内）+ 13（白名单外） |

## 边界声明

- 【实测】映射表 key 与中文值由 `tools/hy4_carddesc.js` 从源码 `const m = {...}` 抽取；卡池使用情况由同一脚本扫 RAW 得到，可 `node tools/hy4_carddesc.js` 复算。
- 【未验证】没开浏览器，卡面实际渲染结果未验证；「什么都不显示」是按 8460 行 `if (!m[s.code]) return;` 与 8469–8470 行拼接逻辑推出的**代码结论**，不是截图结论。
- 【未验证】`cardDesc` 之外是否还有另一处卡面渲染路径（如升级预览、牌堆查看）也读 special code，本项未逐处排查；若存在，上述 3 个 code 的显示情况可能不同。
- `exhaust` 不计入缺映射，依据是 8467 行独立兜底分支；这一条是读代码判断，未验证运行时。
