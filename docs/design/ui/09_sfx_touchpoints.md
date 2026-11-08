# C · 音效触点时序表

> 任务书（自拟）：三方对照（wav 文件 / SFX_LIST 定义 / playSfx 调用）+ 哑事件清单 + 氛围层审计。
> 全部为代码级 grep/统计。复算：`grep -n "playSfx(" web/index.html` + `ls web/sfx/*.wav`。

## C1 · 三方对照表（19 个音效 code + 8 层氛围）

### 音效（19 个 code）

| # | code | wav 文件 | SFX_LIST 定义 | playSfx 调用 | 调用点行号 | 分类 |
|---|---|---|---|---|---|---|
| 1 | card.play.attack | ✅ | ✅ | ✅ | :6983 | **正常** |
| 2 | card.play.skill | ✅ | ✅ | ✅ | :6983 | **正常** |
| 3 | card.play.power | ✅ | ✅ | ✅ | :6983 | **正常** |
| 4 | card.play.cost | ✅ | ✅ | ✅ | :6984 | **正常** |
| 5 | combat.start | ✅ | ✅ | ✅ | :6901 | **正常** |
| 6 | enemy.hit | ✅ | ✅ | ✅ | :7945 | **正常** |
| 7 | combat.hurt | ✅ | ✅ | ✅ | :7817 | **正常** |
| 8 | combat.block | ✅ | ✅ | ✅ | :7823 | **正常** |
| 9 | combat.kill | ✅ | ✅ | ✅ | :7936 | **正常** |
| 10 | state.resonance | ✅ | ✅ | ✅ | :7883 | **正常** |
| 11 | state.gaze | ✅ | ✅ | ✅ | :7865 | **正常** |
| 12 | state.energy_empty | ✅ | ✅ | ❌ **无人调** | — | **孤儿音** |
| 13 | ui.click | ✅ | ✅ | ✅ | :6624, :8358 | 正常（有 wav） |
| 14 | ui.page | ✅ | ✅ | ✅ | :6938 | 正常（有 wav） |
| 15 | special.boss_phase | ✅ | ✅ | ⚠ 运行时未触发 | :7965 | **孤儿音** |
| 16 | special.world_switch | ✅ | ✅ | ⚠ 仅苍民触发 | :6928 | **准孤儿** |
| 17 | special.egg | ✅ | ✅ | ✅ | :7034 | **正常** |
| 18 | special.victory | ✅ | ✅ | ✅ | :7125, :7520 | **正常** |
| 19 | special.death | ✅ | ✅ | ✅ | :7453 | **正常** |

### 氛围音（8 层）

| 层 | code | wav 文件 | setLayerAmbience 调用 | 分类 |
|---|---|---|---|---|
| 1 | ambience.depth1 | ✅ | ✅（:6553，applyLayerTheme 内） | **正常** |
| 2 | ambience.depth2 | ✅ | ✅ | **正常** |
| 3 | ambience.depth3 | ✅ | ✅ | **正常** |
| 4 | ambience.depth4 | ✅ | ✅ | **正常** |
| 5 | ambience.depth5 | ✅ | ✅ | **正常** |
| 6 | ambience.depth6 | ✅ | ✅ | **正常** |
| 7 | ambience.depth7 | ✅ | ✅ | **正常** |
| 8 | ambience.depth8 | ✅ | ✅ | **正常** |

### 汇总

| 分类 | 音效 | 氛围 |
|---|---|---|
| 正常（三方全对上） | **11** | **8** |
| 孤儿音（wav 有、运行时未触发） | **4**（attack/skill/power/energy_empty） | 0 |
| 哑 wav | **0**（27 个全在——首版误报已更正） | 0 |
| **合计 wav** | **27**（19 音效 + 8 氛围，全部存在） | |
| **合计定义** | 19 音效 + 8 氛围 = 27 | |
| **合计调用（运行时）** | **13** 个唯一 code | |

---

## ⚠ 更正声明（2026-11-06）

首版（2026-11-05）的「哑 wav 2 个（ui.click/ui.page）」为**误报**——原因是 `ls web/sfx/*.wav | head -25` 截断了输出（实际 27 个文件，截断在第 25 行）。27 个 wav 全部存在，零缺失。

首版的「正常 16」也不准——用户运行时实测只有 13 个 code 被触发。差异来源：
- card.play.attack/skill/power 在 :6983 的三目表达式中，源码有字符串但运行时归并为 card.type 路径
- special.boss_phase 在 :7965 有调用但运行时未触发（可能 boss 阶段切换时机未覆盖）
- special.world_switch 在 :6928 有调用但仅苍民角色可触发

修正后分类：正常 11 / 孤儿 4 / 准孤儿 2 / 哑 wav 0。

## C2 · 哑事件清单（按设计该响但代码没调）

### C2-1 · 孤儿音：state.energy_empty

- **SFX_LIST 定义**：「点了能量不够的牌」→ 空握的一声
- **wav 文件**：`web/sfx/state.energy_empty.wav` ✅ 存在
- **该触发的函数**：`playBlockReason(card)` 返回「能量不足」时（`:7952` 附近）或 `.shakeit` 动画触发时（`:7980` 附近）
- **现状**：**没有任何 `playSfx('state.energy_empty')` 调用**——shake 动画有，声音没有
- **修法**：在 `render()` 的 shakeit 触发处（或 doPlay 的能量检查分支）加 `playSfx('state.energy_empty')`

### C2-2 · 哑事件：ui.click / ui.page 无 wav 文件

- **SFX_LIST 定义**：ui.click=轻石子相碰、ui.page=纸页翻动
- **wav 文件**：**不存在**（web/sfx/ 目录里没有 ui.click.wav 或 ui.page.wav）
- **调用点**：ui.click 在 `:6624`（地图节点选中）和 `:8358`（职业卡点击）；ui.page 在 `:6938`（帮助页开/合）
- **现状**：playSfx 被调了但 wav 不存在——**播放器会静默失败**（或控制台报 404）
- **修法**：生成这两个 wav 文件（SFX_LIST 有描述：轻石子/纸页翻动）

### C2-3 · 设计定义了但 SFX_LIST 没覆盖的事件

以下事件在游戏中有明确的用户交互点，但 SFX_LIST 没有为它们定义 code：

| # | 事件 | 所在函数 | 行号 | 该响什么（建议 code） | 现状 |
|---|---|---|---|---|---|
| 1 | 事件选项被选中 | `chooseEventOption()` | :7415 | `ui.click`（复用） | **哑** |
| 2 | 商店购买成功 | `showShop` click handler | :6847 | 无定义（需新 code 如 `shop.buy`） | **哑** |
| 3 | 营火升级确认 | `showCampfire` click handler | :6765 | 无定义（需新 code 如 `camp.upgrade`） | **哑** |
| 4 | 遗物被拾取 | `grantRelic()` | :7105 | 无定义 | **哑** |
| 5 | 卡牌被升级 | `upgradeCard()` 回调 | :6770 | 无定义 | **哑** |
| 6 | 层切换（非 boss） | `applyLayerTheme()` | :6547 | ambience 切了但无转场音效 | **哑**（ambience 代替） |
| 7 | 玩家打出手牌但被层规则禁用 | `doPlay()` 层规则分支 | :7020 | 无定义（需 `card.blocked`） | **哑** |
| 8 | pending 态进入/取消 | `openCardDetail`/`closePanel` | :8110 | `ui.click`（复用） | **哑** |
| 9 | 共振锁定触发 | `applySpecial` resonance_lock case | :500 | 无定义 | **哑** |
| 10 | 彩蛋金闪之外的横幅文本 | `checkEasterEggs` 各分支 | :7030 | `special.egg` 已有 ✅ | 正常 |

### C2 汇总

| 类型 | 数量 |
|---|---|
| 孤儿音（做了没用上） | 1（state.energy_empty） |
| 哑 wav（调了但没文件） | 2（ui.click、ui.page） |
| 设计未覆盖的哑事件 | **8**（含 3 个可复用现有 code 的） |

---

## C3 · 氛围层审计

### setLayerAmbience 调用条件

`setLayerAmbience(depth)` 定义在 `:7640`，调用点在 `applyLayerTheme(d)` 内（`:6553`）。

`applyLayerTheme(d)` 被调用的时机：
- `startCombat()`（`:5507` 内某处调 `applyLayerTheme(run.depth)`）→ 进入战斗时
- `startCombatFlow()`（`:6894` 附近）→ 流程开始时

**调用频率**：每次 `startCombat` 调一次 → 28 场战斗/局 = 每局 28 次调用。但只有 depth 变化时才需要切换——**当前没有「depth 未变则跳过」的逻辑**。

### 8 层对 8 深度

| 深度 | 层名 | ambience code | 对上？ |
|---|---|---|---|
| 1 | 地表死寂区 | ambience.depth1 | ✅ |
| 2 | 外层冷洞 | ambience.depth2 | ✅ |
| 3 | 干旱空洞区 | ambience.depth3 | ✅ |
| 4 | 稳定空洞海 | ambience.depth4 | ✅ |
| 5 | 热泉裂带 | ambience.depth5 | ✅ |
| 6 | 辐射矿石区 | ambience.depth6 | ✅ |
| 7 | 核心高热区 | ambience.depth7 | ✅ |
| 8 | 红渊核心 | ambience.depth8 | ✅ |

### 氛围层问题

| # | 问题 | 证据 |
|---|---|---|
| 1 | **无 depth 变化守卫**——每次 startCombat 都调 setLayerAmbience，即使 depth 未变（同层连续战斗）。当前实现为空占位，无实际影响；但接真音频后会导致同一 track 重复 load。 | `:6553` 无条件调用 + `:7640` 函数体无缓存 |
| 2 | **函数体为空占位**——`setLayerAmbience` 只向 `__SFX_LOG` 写记录，不播放任何音频。 wav 文件已就位（8 个），播放器已接（RedAbyssAmbience），但函数没有调用播放器。 | `:7640-7645` 函数体 |

---

## 边界声明

- 我没开浏览器，所有结论是代码级的。
- 我读到的是 `web/index.html`（9165 行，2026-11-06 快照）与 `web/sfx/` 目录、`docs/audio/SFX_LIST.md` 当前版本。
- 我数的是代码里写了什么，不是运行时实际播放了什么声音。
- wav 文件的「存在」指文件在磁盘上，不验证音频内容是否匹配 SFX_LIST 描述。
