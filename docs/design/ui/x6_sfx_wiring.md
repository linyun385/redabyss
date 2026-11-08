# X6 · 音效三方对照（wav 文件 / SFX_LIST 定义 / index.html 调用）

> 任务来源：`tasks/HY4_batch2.md` §X6（:80-95）、硬规矩（:99-108）、边界声明（:109-113）。
> 参照：`docs/design/ui/09_sfx_touchpoints.md`（内有 2026-11-06 更正声明，:58-67）。
> **本次只读现有文件，只新建本文件；未写 `_HY4_PROGRESS.md`（主代理统一追加）。**
> 全部为磁盘文件清单与源码的**静态对照**，不是运行时实测。

---

## 0 · 数据来源、快照与复核方法

| 来源 | 怎么拿 | 本次实测命令/依据 | 结果 |
|---|---|---|---|
| 实际文件 | `web/sfx/*.wav` 完整目录列表 | `ls -1 "…/web/sfx"/*.wav` + bash 循环逐个计数（`wav_total=27`），再用 `ls -1 …/*.wav \| wc -l` 复核得 27 | 27 个 wav，另有 1 个非 wav 条目 `web/sfx/README.txt`（目录共 28 条） |
| 定义清单 | `docs/audio/SFX_LIST.md` 里的 code 表 | 表体行 `grep -nE '^\|' docs/audio/SFX_LIST.md` | 音效 19（:10-48，含 `enemy.hit` :20）+ 氛围 8（:56-63）= 27 个 code |
| 代码引用 | `web/index.html` 里所有 `playSfx('...')` 与 `RedAbyssAmbience(...)` | `grep -n "playSfx\s*("`、`grep -n "RedAbyssAmbience|setLayerAmbience|ambience.depth|__SFX_LOG"`、全量字面量校验 `grep -nE "'(card\|combat\|state\|ui\|special\|ambience)\.[a-z_.]+'"` | 24 个 `playSfx` 调用点、18 个唯一字面量 code、1 处 `RedAbyssAmbience(depth)` 动态调用 |

**快照**：`web/index.html` 当前 `wc -l` = **9489 行**（`web/index.html` 全文）。`09_sfx_touchpoints.md` 记录的是 **9165 行旧快照**（`docs/design/ui/09_sfx_touchpoints.md:151`），两者行号不同；**本文全部行号以当前 9489 行快照实测为准**，不沿用 09 文档里的行号。

**27 个 wav 完整列表（不截断，`ls -1` 全量输出，逐个可复核）**：
`ambience.depth1.wav`、`ambience.depth2.wav`、`ambience.depth3.wav`、`ambience.depth4.wav`、`ambience.depth5.wav`、`ambience.depth6.wav`、`ambience.depth7.wav`、`ambience.depth8.wav`、`card.play.attack.wav`、`card.play.cost.wav`、`card.play.power.wav`、`card.play.skill.wav`、`combat.block.wav`、`combat.hurt.wav`、`combat.kill.wav`、`combat.start.wav`、`enemy.hit.wav`、`special.boss_phase.wav`、`special.death.wav`、`special.egg.wav`、`special.victory.wav`、`special.world_switch.wav`、`state.energy_empty.wav`、`state.gaze.wav`、`state.resonance.wav`、`ui.click.wav`、`ui.page.wav`（均位于 `web/sfx/`）。

**历史教训核对（按用户要求，避免重犯）**：
- 首版曾用 `ls web/sfx/*.wav | head -25` 截断，把第 26、27 个文件（`ui.click.wav`、`ui.page.wav`）误报为「缺文件」。本次**用脚本数总数、不截断**，实测 27 个全在；`ui.click.wav`、`ui.page.wav` 存在性单独探测均为 `EXISTS`。依据：`09_sfx_touchpoints.md:60`（更正声明）+ 本次脚本输出。
- 首版曾把**源码字面量**误当成**运行时触发**。本次把两者分列（§2 只记「源码字面量有/无」，§4 单列运行时判定），并对三目/条件分支/守卫/动态拼接逐点标注。依据：`09_sfx_touchpoints.md:62-67`。

---

## 1 · 统计数字（每个数字可复核）

| # | 指标 | 值 | 复核依据（路径:行号 / 脚本） |
|---|---|---|---|
| 1 | wav 总数 | **27** | `web/sfx/*.wav` 脚本逐个计数 `wav_total=27`；`ls -1 …/*.wav \| wc -l` = 27；完整列表见 §0 |
| 2 | `web/sfx/` 目录总条目（含非 wav） | **28** | `ls -1 "…/web/sfx" \| wc -l` = 28 = 27 wav + 1 `README.txt` |
| 3 | 定义 code 数（SFX_LIST） | **27** | `docs/audio/SFX_LIST.md` 表体：音效 19（:10-13、:19-23、:29-31、:37-38、:44-48）+ 氛围 8（:56-63） |
| 3a | ├ 音效 code | **19** | `docs/audio/SFX_LIST.md:10-48`；19 = 4 卡牌 + 5 战斗 + 3 状态 + 2 界面 + 5 特殊 |
| 3b | └ 氛围 code | **8** | `docs/audio/SFX_LIST.md:56-63`（depth1–depth8） |
| 4 | `playSfx` 调用点总数（去重定义/注释） | **24** | `web/index.html` 行号：`:6846, :7123, :7150, :7160, :7205, :7206, :7256, :7347, :7675, :7742, :8039, :8045, :8087, :8105, :8158, :8167, :8187, :8589, :8600, :8985, :9226, :9349, :9384, :9391`；`:7856` 为函数定义、`:7853` 为注释，均不计入 |
| 5 | `playSfx` 字面量字符串出现次数 | **26** | 24 个调用点中 `:7205` 为三目含 3 个字面量、其余 23 个各 1 个 → 23 + 3 = 26；行号同 #4 |
| 6 | `playSfx` 唯一 code 字面量（去重） | **18** | 19 个音效 code 减去 `state.energy_empty`（无 playSfx 调用）= 18；清单见 §2「源码字面量 ✅」的 18 行 |
| 7 | 预载数组字面量（**非调用**） | **19** | `web/index.html:7949-7953` `var list = [...]` 供 `load()` 预载，非 `playSfx`；与 19 音效 code 一一对应 |
| 8 | `RedAbyssAmbience(...)` 调用点 | **1** | `web/index.html:7864`（`setLayerAmbience` 内转发，参数 `depth` 为变量）；`:7917` 是函数定义、`:7869` 是注释，不计入 |
| 9 | 动态拼接 / 变量参数点（氛围 code、文件名、URL、播放参数） | **5** | `web/index.html:7863`（拼 code）、`:7896`（拼 URL）、`:7906`（变量 code）、`:7927`（拼文件名）、`:7864`（变量 depth 调用）；§4.1 B 表另列入口 `:6775`、3 处守卫 `:7921/:7925/:7926`、预载 `:7947/:7949-7953`，均不计入此 5 个拼接点 |
| 10 | 孤儿音 | **1** | §3.1；`state.energy_empty`（`web/sfx/state.energy_empty.wav` 存在，无 playSfx 调用） |
| 11 | 缺文件 | **0** | §3.2；18 个调用 code + 动态 depth1–8 对应 wav 全部存在（脚本实测 27 全在） |
| 12 | 未定义 | **0** | §3.3；18 个调用 code 全部在 `docs/audio/SFX_LIST.md:10-48`，动态 depth1–8 在 `:56-63` |

**口径说明（防混淆）**：#4「调用点」= 代码里 `playSfx(...)` 出现次数（不含定义/注释）；#6「唯一 code 字面量」= 这些调用里出现的不同字符串；#7 预载数组是 `load()` 的 fetch 清单，只下载不播放，**不计入调用、也不视为运行时触发**。三者分母不同，不可互换。

---

## 2 · 三方完整对照表（27 个 code，每个 code 一行）

列约定：`wav` = `web/sfx/<code>.wav` 是否存在（✅/❌，依据 §0 脚本）；`定义` = `docs/audio/SFX_LIST.md` 是否有该 code（✅ 附行号）；`源码字面量` = `web/index.html` 是否有 `playSfx('<code>')` 字面量（✅ 附行号 / ❌）；`调用点行号` = 逐个列出并标注调用形态。**每格均填写，无空格。**

| # | code | wav | 定义 | 源码字面量 | 调用点行号（含调用形态标注） |
|---|---|---|---|---|---|
| 1 | card.play.attack | ✅ | ✅ `docs/audio/SFX_LIST.md:10` | ✅ `:7205` | `:7205`（**三目第 1 分支**，`card.type==='attack'` 时取此值；同表达式另 2 分支见 #2/#3） |
| 2 | card.play.skill | ✅ | ✅ `docs/audio/SFX_LIST.md:11` | ✅ `:7205` | `:7205`（**三目第 3 分支**，兜底 `else`） |
| 3 | card.play.power | ✅ | ✅ `docs/audio/SFX_LIST.md:12` | ✅ `:7205` | `:7205`（**三目第 2 分支**，`card.type==='power'` 时取此值） |
| 4 | card.play.cost | ✅ | ✅ `docs/audio/SFX_LIST.md:13` | ✅ `:7206` | `:7206`（**条件分支内**，`if (card.cost_type && card.cost_type!=='none')`） |
| 5 | combat.start | ✅ | ✅ `docs/audio/SFX_LIST.md:19` | ✅ `:7123` | `:7123`（`startCombat` 内直接调用） |
| 6 | enemy.hit | ✅ | ✅ `docs/audio/SFX_LIST.md:20` | ✅ `:8167` | `:8167`（**条件分支 + `enqueueAnim` 回调内**，`if (!e.dead && prev.hps[e.idx] > e.hp)`） |
| 7 | combat.hurt | ✅ | ✅ `docs/audio/SFX_LIST.md:21` | ✅ `:8039` | `:8039`（**条件分支内**，`if (run.hp < prev.hp)`，`web/index.html:8035`） |
| 8 | combat.block | ✅ | ✅ `docs/audio/SFX_LIST.md:22` | ✅ `:8045` | `:8045`（**条件分支内**，`if (C.block > (prev.block\|\|0) && bi)`，`web/index.html:8044`） |
| 9 | combat.kill | ✅ | ✅ `docs/audio/SFX_LIST.md:23` | ✅ `:8158` | `:8158`（**条件分支内**，`if (e.dead && prev.dead && prev.dead[e.idx]===false)`） |
| 10 | state.resonance | ✅ | ✅ `docs/audio/SFX_LIST.md:29` | ✅ `:8105` | `:8105`（**条件分支内**，`if (C.resonanceFired > prev.resFired \|\| C.resonance>=30)`，`web/index.html:8104`） |
| 11 | state.gaze | ✅ | ✅ `docs/audio/SFX_LIST.md:30` | ✅ `:8087` | `:8087`（**条件分支内**，`if (run.gaze > prev.gaze)`） |
| 12 | state.energy_empty | ✅ | ✅ `docs/audio/SFX_LIST.md:31` | ❌ 无 | **无 `playSfx` 调用**；仅 `web/index.html:7951` 出现在预载数组（load 字面量，非播放）→ 孤儿音，见 §3.1 |
| 13 | ui.click | ✅ | ✅ `docs/audio/SFX_LIST.md:37` | ✅ 多处 | `:6846`（`resolveNode`）、`:8589`、`:8600`、`:8985`、`:9226`、`:9349`、`:9384`、`:9391`（**均为事件监听/键盘回调内直接字面量**，共 8 处） |
| 14 | ui.page | ✅ | ✅ `docs/audio/SFX_LIST.md:38` | ✅ `:7160` | `:7160`（`#btn-help` click 回调内直接字面量） |
| 15 | special.boss_phase | ✅ | ✅ `docs/audio/SFX_LIST.md:44` | ✅ `:8187` | `:8187`（**双层条件分支内**：`if (e.phases && !e.dead)` + `if (prev.phaseIdx… !== e.phaseIdx && e.phaseIdx>0)`，`web/index.html:8177`、`:8184`） |
| 16 | special.world_switch | ✅ | ✅ `docs/audio/SFX_LIST.md:45` | ✅ `:7150` | `:7150`（`#btn-world` click 回调；**前置守卫** `if (!C \|\| C.over \|\| run.classId!=='cangmin') return;` 在 `web/index.html:7148`） |
| 17 | special.egg | ✅ | ✅ `docs/audio/SFX_LIST.md:46` | ✅ `:7256` | `:7256`（彩蛋函数内直接调用） |
| 18 | special.victory | ✅ | ✅ `docs/audio/SFX_LIST.md:47` | ✅ `:7347`、`:7742` | `:7347`（胜利分支，位于 `if (C.result!=='win'){showGameOver();return;}` 之后，`web/index.html:7346`）、`:7742`（`showVictory` 内）；共 2 处 |
| 19 | special.death | ✅ | ✅ `docs/audio/SFX_LIST.md:48` | ✅ `:7675` | `:7675`（`showGameOver` 内直接调用） |
| 20 | ambience.depth1 | ✅ | ✅ `docs/audio/SFX_LIST.md:56` | ❌ 无 | **无 `playSfx` 字面量**；动态路径：`web/index.html:6775` `setLayerAmbience(d)` → `:7864` `RedAbyssAmbience(depth)` → `:7927` `load('ambience.depth'+depth)`（depth=1）；日志 `:7863` |
| 21 | ambience.depth2 | ✅ | ✅ `docs/audio/SFX_LIST.md:57` | ❌ 无 | **无 `playSfx` 字面量**；动态路径同 #20，depth=2（`:6775` → `:7864` → `:7927`；日志 `:7863`） |
| 22 | ambience.depth3 | ✅ | ✅ `docs/audio/SFX_LIST.md:58` | ❌ 无 | **无 `playSfx` 字面量**；动态路径同 #20，depth=3（`:6775` → `:7864` → `:7927`；日志 `:7863`） |
| 23 | ambience.depth4 | ✅ | ✅ `docs/audio/SFX_LIST.md:59` | ❌ 无 | **无 `playSfx` 字面量**；动态路径同 #20，depth=4（`:6775` → `:7864` → `:7927`；日志 `:7863`） |
| 24 | ambience.depth5 | ✅ | ✅ `docs/audio/SFX_LIST.md:60` | ❌ 无 | **无 `playSfx` 字面量**；动态路径同 #20，depth=5（`:6775` → `:7864` → `:7927`；日志 `:7863`） |
| 25 | ambience.depth6 | ✅ | ✅ `docs/audio/SFX_LIST.md:61` | ❌ 无 | **无 `playSfx` 字面量**；动态路径同 #20，depth=6（`:6775` → `:7864` → `:7927`；日志 `:7863`） |
| 26 | ambience.depth7 | ✅ | ✅ `docs/audio/SFX_LIST.md:62` | ❌ 无 | **无 `playSfx` 字面量**；动态路径同 #20，depth=7（`:6775` → `:7864` → `:7927`；日志 `:7863`） |
| 27 | ambience.depth8 | ✅ | ✅ `docs/audio/SFX_LIST.md:63` | ❌ 无 | **无 `playSfx` 字面量**；动态路径同 #20，depth=8（`:6775` → `:7864` → `:7927`；日志 `:7863`） |

**对照表口径小结**：27 行 wav 全 ✅、27 行定义全 ✅；「源码字面量 ✅」= 18 行（#1-11、#13-19）、「❌」= 9 行（#12 `state.energy_empty` + #20-27 氛围 8 层）。氛围 8 层**不是**孤儿音（有动态拼接 `load` 路径），详见 §3.1 与 §4。

---

## 3 · 三类清单

### 3.1 孤儿音（有 wav 文件但代码里没人调用）—— **1 条**

判定口径：`web/sfx/<code>.wav` 存在，且 `web/index.html` 中**既无** `playSfx('<code>')` 字面量调用，**也无**指向该文件的动态拼接 `load(...)` 运行时加载路径。

| # | code | wav | 定义 | 源码调用情况 | 结论依据 |
|---|---|---|---|---|---|
| 1 | `state.energy_empty` | ✅ `web/sfx/state.energy_empty.wav` | ✅ `docs/audio/SFX_LIST.md:31` | 无任何 `playSfx('state.energy_empty')`；`web/index.html:7951` 仅在预载数组 `list` 里作为 `load()` 参数出现（预载下载文件，**不播放**） | 全量字面量校验 `grep -nE "'(card\|combat\|state\|ui\|special\|ambience)\.[a-z_.]+'"` 无任何调用行含该 code 作 `playSfx` 参数；`09_sfx_touchpoints.md:23`、`:71-77` 同判为孤儿音 |

**不列入孤儿音的边界情形**：
- 氛围 8 层（#20-27）：源码无 `playSfx` 字面量，但 `web/index.html:7927` `load('ambience.depth'+depth)` 在运行时 `depth=1..8` 会加载对应 wav，属于**动态拼接调用路径**，不是「没人调用」。运行时是否真的触发另见 §4（未验证）。
- `card.play.attack` / `card.play.skill` / `card.play.power`：在 `:7205` 三目里有字面量，**静态上「有人调用」**，故不计入静态孤儿音；但运行时归并、触发未验证，见 §4。

### 3.2 缺文件（代码调用了但目录里没有对应 wav）—— **0 条**

| 核对对象 | 数量 | 对应 wav 是否存在 | 依据 |
|---|---|---|---|
| 18 个 `playSfx` 唯一 code 字面量 | 18 | 全部 ✅ | §2 表 #1-11、#13-19 的 wav 列全 ✅；脚本实测 27 个 wav 全在 |
| 动态 `ambience.depth'+depth`（运行时 depth=1..8） | 8 | 全部 ✅ `ambience.depth1..8.wav` | `web/index.html:7927` + §0 完整 wav 列表 |
| 预载数组 19 个 code | 19 | 全部 ✅ | `web/index.html:7949-7953` + §0 完整 wav 列表 |

**结论：0 条（无）。** 首版「`ui.click` / `ui.page` 缺 wav」为 `ls | head -25` 截断造成的误报（`docs/design/ui/09_sfx_touchpoints.md:60` 更正声明、`:79-85` 的 C2-2 为**未同步的残留错误**）；本次脚本单独探测 `ui.click.wav = EXISTS`、`ui.page.wav = EXISTS`，27 个 wav 全部存在，零缺失。

### 3.3 未定义（代码调用了但 SFX_LIST 里没有该 code）—— **0 条**

| 核对对象 | 数量 | 是否在 SFX_LIST | 依据 |
|---|---|---|---|
| 18 个 `playSfx` 唯一 code 字面量 | 18 | 全部 ✅ | `docs/audio/SFX_LIST.md:10-48`（19 音效 code 内） |
| 动态 `ambience.depthN`（depth=1..8） | 8 | 全部 ✅ | `docs/audio/SFX_LIST.md:56-63`（氛围表） |
| `RedAbyssAmbience(depth)` 转发 | 1 处调用 | 参数经 `'ambience.depth'+depth` 落到已定义 code | `web/index.html:7863`、`:7864`、`:7927` |

**结论：0 条（无）。** 代码里出现的每一个 code 字面量、以及动态拼接可能产生的 `ambience.depth1..8`，都能在 `docs/audio/SFX_LIST.md` 找到定义；未发现任何「调用了但清单没写」的 code。

---

## 4 · 源码字面量 vs 运行时真正会触发（重点区分）

### 4.1 动态拼接 / 三目 / 条件分支 / 事件回调 调用点（逐个列行号）

**A. `playSfx` 的非「无条件直接字面量」调用点**

| 行号 | code | 形态 | 守卫 / 触发前提（源码可见） | 运行时触发判定 |
|---|---|---|---|---|
| `:7205` | card.play.attack / power / skill | **三目表达式**（1 个调用点，3 个字面量） | 按 `card.type` 三选一（`web/index.html:7205`） | **未验证：未开浏览器，仅静态对照**；且源码字面量 ≠ 三分支都触发 |
| `:7206` | card.play.cost | **条件分支** | `if (card.cost_type && card.cost_type!=='none')`（`:7206`） | **未验证：未开浏览器**；条件不满足则不触发 |
| `:7150` | special.world_switch | **前置守卫** | `web/index.html:7148` `if (!C \|\| C.over \|\| run.classId!=='cangmin') return;` → 仅苍民角色、战斗中、未结束 | **未验证：未开浏览器**；非苍民角色恒不触发 |
| `:8039` | combat.hurt | **条件分支** | `if (prev.hp!==undefined && run.hp<prev.hp)`（`:8035`） | **未验证：未开浏览器** |
| `:8045` | combat.block | **条件分支** | `if (C.block>(prev.block\|\|0) && bi)`（`:8044`） | **未验证：未开浏览器** |
| `:8087` | state.gaze | **条件分支** | `if (run.gaze>prev.gaze)`（`:8087`） | **未验证：未开浏览器** |
| `:8105` | state.resonance | **条件分支** | `if (C.resonanceFired>prev.resFired \|\| C.resonance>=30)`（`:8104`） | **未验证：未开浏览器** |
| `:8158` | combat.kill | **条件分支** | `if (e.dead && prev.dead && prev.dead[e.idx]===false)`（`:8158`） | **未验证：未开浏览器** |
| `:8167` | enemy.hit | **条件分支 + 动画队列回调** | `if (!e.dead && prev.hps[e.idx]!==undefined && prev.hps[e.idx]>e.hp)`（`:8161`）且 `enqueueAnim` 回调内（`:8163`） | **未验证：未开浏览器** |
| `:8187` | special.boss_phase | **双层条件分支** | `if (e.phases && !e.dead)`（`:8177`）+ `if (prev.phaseIdx[e.idx]!==undefined && prev.phaseIdx[e.idx]!==e.phaseIdx && e.phaseIdx>0)`（`:8184`） | **未验证：未开浏览器**；09 文档记「运行时未触发」，见 §4.3 |
| `:7347` | special.victory | **胜利分支**（顺序隐含） | 位于 `if (C.result!=='win'){showGameOver();return;}` 之后（`:7346`） | **未验证：未开浏览器** |
| `:6846` | ui.click | 函数体内（`resolveNode`） | 地图节点推进时被调用 | **未验证：未开浏览器** |
| `:7123` | combat.start | 函数体内（`startCombat`） | 进入战斗时被调用 | **未验证：未开浏览器** |
| `:7160` | ui.page | **事件回调** | `#btn-help` click 回调（`:7158`） | **未验证：未开浏览器**（需用户交互） |
| `:7256` | special.egg | 函数体内（彩蛋） | 彩蛋触发函数内 | **未验证：未开浏览器** |
| `:7675` | special.death | 函数体内（`showGameOver`） | 结算调用 | **未验证：未开浏览器** |
| `:7742` | special.victory | 函数体内（`showVictory`） | 结算调用 | **未验证：未开浏览器** |
| `:8589` | ui.click | **事件回调** | `.classface` click（`:8588`） | **未验证：未开浏览器**（需用户交互） |
| `:8600` | ui.click | **事件回调 + 条件** | `if (btnC && modalClass)`（`:8600`） | **未验证：未开浏览器** |
| `:8985` | ui.click | **事件回调 + 条件** | `if (box && box.dataset.dragged) return;`（`:8984`） | **未验证：未开浏览器** |
| `:9226` | ui.click | **函数体内 + 三重守卫** | `backtrackTo` 内 `:9223-9225` 三个 `return` 守卫 | **未验证：未开浏览器** |
| `:9349` | ui.click | **键盘事件回调 + 条件** | `if (st.cursorId && picks.indexOf(st.cursorId)>=0)`（`:9347`） | **未验证：未开浏览器** |
| `:9384` | ui.click | **事件回调** | `hudMapBtn` click（`:9383`） | **未验证：未开浏览器**（需用户交互） |
| `:9391` | ui.click | **键盘事件回调 + 条件** | `if (e.key!=='Tab') return;` + `if (!st.region …) return;`（`:9388-9389`） | **未验证：未开浏览器** |

**B. 动态拼接点（无 `playSfx` 字面量，氛围层走此路径）**

| 行号 | 代码 | 形态 | 运行时触发判定 |
|---|---|---|---|
| `:6775` | `setLayerAmbience(d);`（在 `applyLayerTheme(d)` 内） | 氛围入口调用（参数 `d` 变量） | **未验证：未开浏览器**；`applyLayerTheme` 由 `showMap`（`:6780`）等调用 |
| `:7863` | `window.__SFX_LOG.push('ambience.depth' + depth)` | **动态拼接 code**（写日志，非播放） | **未验证：未开浏览器**（依赖 `window.__SFX_LOG` 是否存在，`:7863`） |
| `:7864` | `window.RedAbyssAmbience(depth)` | **变量参数调用**（`RedAbyssAmbience` 唯一调用点，见 §1 #8） | **未验证：未开浏览器**（依赖 `typeof window.RedAbyssAmbience==='function'`，`:7864`） |
| `:7896` | `fetch('sfx/' + name + '.wav')` | **动态拼接 URL** | **未验证：未开浏览器**（网络/文件加载结果不在静态对照范围） |
| `:7906` | `load(code)`（`RedAbyssSFX` 内） | **变量参数**（code 由 `playSfx` 转发，`web/index.html:7859`） | **未验证：未开浏览器** |
| `:7927` | `load('ambience.depth' + depth)` | **动态拼接文件名** | **未验证：未开浏览器** |
| `:7921` | `if (depth === ambDepth) return;` | 守卫（depth 未变则直接返回，不加载） | **代码有、运行时不保证**（守卫条件静态不可判定） |
| `:7925` | `if (depth < 1 \|\| depth > 8) return;` | 范围守卫（越界不播放） | **代码有、运行时不保证** |
| `:7926` | `if (window.__SFX_MUTED) return;` | 静音守卫 | **代码有、运行时不保证** |
| `:7947` | `document.addEventListener('pointerdown', function once() …)` | 首次交互才解锁/预载 | **未验证：未开浏览器**（需用户交互） |
| `:7949-7953` | `var list = [19 个 code]` + `:7954` `load(list[i])` | 预载字面量数组（`load` 下载，**非播放**） | **未验证：未开浏览器**；**不计入 §1 #4 调用点** |

### 4.2 运行时触发判定（本次结论）

| 判定项 | 本次结论 | 原因 |
|---|---|---|
| 24 个 `playSfx` 调用点是否真的执行 | **未验证：未开浏览器，全部为源码与文件清单的静态对照** | 每个调用点都在函数体/事件回调/条件分支/守卫之后，静态无法确证执行路径 |
| 18 个唯一 code 是否都真的发声 | **未验证：未开浏览器** | 需 `AudioContext` 解锁（`:7872`、`:7947`）、`fetch` 成功（`:7896`）、`decodeAudioData` 成功（`:7898`）等运行时条件 |
| 三目 `:7205` 三个分支是否都触发 | **未验证：未开浏览器** | 三目运行时只取 1 个值；源码 3 个字面量 ≠ 3 次触发 |
| 氛围 8 层是否真的切换/播放 | **未验证：未开浏览器** | `:7921`/`:7925`/`:7926` 三处守卫；`09_sfx_touchpoints.md:93-95`、`:144` 也记「没在游戏里实测过」「函数体为空占位」 |
| `state.energy_empty` 是否运行时触发 | **否（静态可确证）** | 源码无任何 `playSfx('state.energy_empty')` 调用（全量字面量校验），这是**源码级事实**，不依赖浏览器；故 §3.1 判为孤儿音 |
| 27 个 wav 是否存在 | **是（静态可确证）** | 磁盘文件清单脚本实测，不依赖浏览器 |

### 4.3 外部参照：09 文档已更正事实（**非本次实测**）

`docs/design/ui/09_sfx_touchpoints.md:58-67` 记录的用户历史运行时实测结论，本次**未开浏览器、无法复核**，仅作参照，不写入 §1/§3 的本次结论：

| 09 文档条目 | 内容 | 本次处理 |
|---|---|---|
| `:60` | 首版「哑 wav 2 个（ui.click/ui.page）」为 `ls \| head -25` 截断误报，27 个 wav 全在、零缺失 | §3.2 已用脚本独立复核，结论一致（0 条缺文件） |
| `:63` | `card.play.attack/skill/power` 在 `:6983`（旧快照）三目中，源码有字符串但运行时归并为 `card.type` 路径 | §4.1 A 表标 `:7205` 三目、触发未验证；不把 3 个字面量当 3 次触发 |
| `:64` | `special.boss_phase` 有调用但运行时未触发（boss 阶段切换时机未覆盖） | §4.1 A 表标 `:8187` 双层条件、未验证；不据此改判静态清单 |
| `:65` | `special.world_switch` 仅苍民角色可触发 | §2 #16、§4.1 A 表已用当前快照 `:7148` 守独立核实「仅 cangmin」这一源码事实 |
| `:62` | 用户运行时实测只有 **13 个 code** 被触发 | **外部历史数据，非本次实测**；本次静态口径为 18 个唯一字面量（§1 #6），两者分母不同、不可直接相减 |
| `:67` | 修正后分类「正常 11 / 孤儿 4 / 准孤儿 2 / 哑 wav 0」 | 那是**运行时触发视角**的分类；本文 §3 是**静态源码视角**（孤儿 1 / 缺文件 0 / 未定义 0），口径不同，不冲突 |

---

## 5 · 与历史文档 / 代码注释的冲突核对（均可复核）

| # | 冲突 | 实测事实 | 依据 |
|---|---|---|---|
| 1 | `09_sfx_touchpoints.md:79-85`（C2-2）称「ui.click / ui.page 无 wav 文件、播放器静默失败」 | **残留错误**：两个 wav 都存在 | 本次脚本 `ui.click.wav = EXISTS`、`ui.page.wav = EXISTS`；且 `09_sfx_touchpoints.md:60` 更正声明已推翻该说法，但 C2-2 正文未同步 |
| 2 | `web/index.html:7873` 注释写「音频文件：web/sfx/<code>.wav，**28 个（20 音效 + 8 氛围）**」 | 实测 **27 个（19 音效 + 8 氛围）** | 脚本计数 `wav_total=27`；`docs/audio/SFX_LIST.md:71`、`:78`（v2 把 `ui.open/close` 合并成 `ui.page`，音效由 20 减为 19）与 `tasks/HY4_batch2.md:88`（27 个）均与 27 一致 → 注释为过时数字 |
| 3 | `09_sfx_touchpoints.md:151` 记 `index.html` 为 **9165 行快照** | 当前 `wc -l` = **9489 行** | 本次 `wc -l < web/index.html`；故 09 文档里的行号（如 `:6983`、`:6624`）与当前快照（`:7205`、`:6846`）不同，本文一律用当前实测行号 |
| 4 | `09_sfx_touchpoints.md:49` 汇总「正常 11 / 孤儿 4」 | 本文静态口径「孤儿 1 / 缺文件 0 / 未定义 0」 | 口径差异见 §4.3；本文按 `tasks/HY4_batch2.md:93-95` 的**静态**定义（有文件没人调 / 调了没文件 / 调了没定义）判定，不沿用运行时触发分类 |

---

## 边界声明

- **我没开浏览器**：本文全部结论都是 `web/index.html`（9489 行快照）、`docs/audio/SFX_LIST.md`、`web/sfx/` 磁盘文件清单三者的**静态对照**，不是运行时实测，不是实际播放了什么声音。
- **源码字面量 ≠ 运行时触发**：§2 只记录「源码里写了什么字符串」；§4 把所有三目 / 条件分支 / 守卫 / 动态拼接 / 事件回调逐点标注，凡是静态无法确证执行的，一律写「未验证：原因 = 未开浏览器，仅静态对照」。§4.3 引用的 13 个运行时 code 是 09 文档记录的历史实测，本次无法复核，不作为本次结论。
- **代码有、运行时不保证**：条件分支守卫（如 `web/index.html:7148`、`:7921`、`:7925`、`:7926`）、`AudioContext` 解锁（`:7872`、`:7947`）、`fetch` 成败（`:7896`）都可能导致「写了但未生效」；按 `tasks/HY4_batch2.md:112` 的规矩，这类一律标「代码有、运行时不保证」。CSS 优先级打架同理：写了也未必生效，本文不涉及 CSS 渲染结论。
- **wav 的「存在」**仅指文件在磁盘上（`web/sfx/`），不验证音频内容是否与 `docs/audio/SFX_LIST.md` 描述匹配（`09_sfx_touchpoints.md:153` 同口径）。
- **只读约束**：本次未修改 `web/`、`engine/`、`cards/*.json`，未写 `_HY4_PROGRESS.md`（主代理统一追加），只新建本文件 `docs/design/ui/x6_sfx_wiring.md`。
- **数字复核**：§1 每个数字均指回行号或脚本；§2 27 行对照表每格均填写、无空格；无法复核的运行时触发一律「未验证：原因」，未使用「看起来」「感觉」等表述。
