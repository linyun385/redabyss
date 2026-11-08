# SFX_T32 — T32「音效架构」夜间补做审计（只审计，不改代码）

> 性质：夜班补做记录。本轮**未改 web/、engine/ 任何文件**，仅新增本文档。
> 任务书：`tasks/T32.md`。审计时间：2026-11-03。审计方式：静态检索 + 复跑 check_web（只读）。

## 0. 关键背景：T32 与 T41 是同一任务的两个版本

- `tasks/T32.md` 与 `tasks/T41.md` 同时存在，diff 确认为同一任务的不同稿：
  - T41（执行稿）**删除了** T32 的「三、静音与设置入口」（齿轮/静音开关/灰音量条/清单入口/localStorage）要求；
  - T41 **删除了**战斗类中的「暴击」项；
  - T41 **新增了**「三、氛围音」：`setLayerAmbience(depth)` 空实现并挂进 `applyLayerTheme()`。
- 工作已按 **T41** 执行并记录：`TASK_DONE.md` 第 274–280 行有「## T41 完成（音效架构：只留钩子，不生成音频）」，**无 T32 记录**——即补做号前提成立：活干了，记在 T41 名下。
- 以下逐条以 **T32 任务书原文**为验收基准，并注明 T41 视角的差异。

## 1. 验收点清单与判定

计数：**已覆盖 8 / 部分 3 / 未覆盖 1**（共 12 条）。

### A1 接口形态 `playSfx(code, opts)` — 已覆盖
- 证据：`web/index.html:7574-7581`。函数存在，签名 `(code, opts)`；`if (window.__SFX_LOG) window.__SFX_LOG.push(code)` 与任务书片段一致。
- 超出任务书的部分（均不发声，不违规）：`window.__SFX_MUTED` 早退（7579 行，静音入口留位）；`window.RedAbyssSFX` 接管通道（7580-7581 行，兼容 T16 旧占位）。

### A2 code 命名规范（语义化点分） — 已覆盖
- 证据：全部调用点为 `card.play.attack / enemy.hit / ui.click` 风格，见 A3 的 code 对账表；无下划线旧风格残留（旧 `sfx(name)` 已在 T41 迁移，`web/sfx/README.txt:3` 仍提旧 API，见 S6）。

### A3 所有需要音效的地方都调用它 — 部分
- 证据：`playSfx(` 共 **26 处调用**，去重后 **18 个不同 code**（15 个字面量 + `index.html:6928` 三元式派生 card.play.attack/skill/power）。战斗起止、出牌（含代价叠加）、受击/格挡/击杀、共振/凝视、Boss 阶段、切世、彩蛋、通关、死亡、界面 8 处点击均已接线。
- 缺口：清单里的 `state.energy_empty` 在当前 `index.html` **0 处引用**。T41 notes（TASK_DONE:276）声明接了"能量空"，T53 notes（TASK_DONE:403）也证明当时点击处理器里有这行——后续重构中丢失，属**回归**。见 S1。

### A4 `docs/SFX_LIST.md` 存在、按类别组织 — 已覆盖
- 证据：`docs/SFX_LIST.md` 存在，5 类主表（卡牌 4 / 战斗 5 / 状态 3 / 界面 3 / 特殊 5 = **20 个 code**）+ 氛围音设计表（ambience.depth1–8）。
- 备注：TASK_DONE T41 notes 写「21 个 code」，主表实数 20（4+5+3+3+5），计数差 1，疑为笔误。见 S4。

### A5 类别最低覆盖 — 部分
- 卡牌 4 种（attack/skill/power/cost）：✅ 清单 10–13 行。
- 战斗（命中、格挡、暴击、死亡）：命中 `enemy.hit` ✅、格挡 `combat.block` ✅、死亡 `combat.kill` ✅ + 额外 combat.start/combat.hurt；**暴击 ❌**——清单无 crit code，且游戏本体无暴击机制（`grep -ri 暴击|crit engine/ data/ cards/` = 0 命中）。T41 稿已删此项。见 S2。
- 状态（共振阈值、凝视增加、能量耗尽）：`state.resonance` / `state.gaze` / `state.energy_empty` ✅ 三条全在清单（energy_empty 仅清单在、调用缺，归 A3 记账）。
- 界面（点击、切换、展开）：点击 `ui.click` ✅、展开/收起 `ui.open` / `ui.close` ✅；**"切换"无专属 code** △——现由 ui.click（8 处）与 open/close 兼任。见 S5。
- 特殊（Boss 阶段切换、世界切换、通关、死亡）：`special.boss_phase / world_switch / victory / death` ✅ + 额外 special.egg。

### A6 每个 code 有一句「不要什么」 — 已覆盖
- 证据：SFX_LIST 主表 20/20 行、氛围音表 8/8 行均带「不要什么」列，无空缺。

### A7 静音与设置入口（齿轮 + 静音开关 + 灰音量条 + 清单入口 + localStorage） — 未覆盖
- 证据：`grep -ni 齿轮|gear|settings|mute` 在 `web/index.html` 中无任何 UI 命中；`__SFX_MUTED` 仅在 playSfx 内被读（7579 行），**无任何代码写它**；localStorage 现有键（redabyss_cleared / redabyss_endings / T40 提示键）无 sfx 相关键。
- 判定：对 T32 原文为 0/5 子项未做。**原因明确**：执行的 T41 稿整段删除了本要求。按补做纪律不改代码，留白天拍板。见 S3。

### A8 自检 1：`window.__SFX_LOG` 能收集到所有 code — 已覆盖
- 证据：机制在 playSfx 首行（7578 行）；setLayerAmbience（7582-7585 行）同样写入 `ambience.depthN` 占位记录并已在 `applyLayerTheme` 挂接（6498 行）。T41 notes（TASK_DONE:279）记录了实开 __SFX_LOG 打一场战斗的实测。

### A9 自检 2：日志里出现的 code 都在 SFX_LIST.md 里 — 已覆盖
- 证据：T41 实测 6 种（ui.click×2 / combat.start / card.play.attack / enemy.hit / combat.hurt）全部在清单（TASK_DONE:279）。今日静态复核：18 个接线 code ⊆ 清单 20 个，见 A3 对账。

### A10 自检 3：没有"未定义"的 code — 已覆盖
- 证据：26 处调用去重 + 6928 行三元式 3 分支逐一对账 SFX_LIST，0 个未定义 code。（反向：清单 20 中 19 个已接线，唯一缺口 energy_empty 即 A3 缺口。）

### A11 不许生成音频文件 / 不找素材 / 不用在线资源 — 已覆盖
- 证据：`find web -iname *.mp3|*.wav|*.ogg|*.m4a|*.aac|*.flac` = 0；`web/sfx/` 仅 README.txt（T16 文字占位）；index.html 无 `<audio>` / `new Audio` / `AudioContext` / 音频文件引用（7576 行仅注释"未来接 Web Audio"）；engine/ 同样 0 命中。
- check_web（本轮复跑）：`node tools/check_web.js` → **全部通过（0 个警告）**，含「完全自包含，无网络依赖」「<img> 全部为站内相对路径（5 处）」「站内素材存在性校验通过（84 个引用）」。

### A12 TASK_DONE.md 记录（notes 写 code 数与分类数） — 部分
- 证据：无「## T32」记录；有等价工作「## T41 完成」（TASK_DONE:274-280），notes 含 code 数（写了 21，实数 20，差 1）与分类数（5 类）。
- 判定：工作有记录但任务号错位 + 计数笔误。补记/并档属文档改动，留白天。见 S4。

## 2. code 对账表（今日静态）

| 清单 code（20） | 接线位置 | 状态 |
|---|---|---|
| card.play.attack / skill / power | index.html:6928（三元式） | 已接线 |
| card.play.cost | 6929 | 已接线 |
| combat.start | 6846 | 已接线 |
| enemy.hit | 7794 | 已接线 |
| combat.hurt | 7667 | 已接线 |
| combat.block | 7673 | 已接线 |
| combat.kill | 7785 | 已接线 |
| state.resonance | 7733 | 已接线 |
| state.gaze | 7715 | 已接线 |
| state.energy_empty | — | **清单有、代码无（回归缺口，S1）** |
| ui.click | 6569, 8199, 8210, 8583, 8824, 8947, 8982, 8989 | 已接线 |
| ui.open / ui.close | 6883（三元式） | 已接线 |
| special.boss_phase | 7814 | 已接线 |
| special.world_switch | 6873 | 已接线 |
| special.egg | 6979 | 已接线 |
| special.victory | 7070, 7463（两条胜利路径） | 已接线 |
| special.death | 7396 | 已接线 |
| ambience.depth1–8（占位） | setLayerAmbience 7582-7585 → applyLayerTheme 6498 | 已接线（T41 新增项） |

## 3. 最小补齐建议（均不改本轮执行，留白天拍板）

- **S1（1 行，建议优先）**：`state.energy_empty` 回归补接——在 `doPlay` 的 `if (!r.ok) { toast(r.msg); … }`（index.html:6930）分支内，当失败原因属能量不足时补 `playSfx('state.energy_empty')`。
- **S2（清单 1 行或标注）**：暴击——游戏无暴击机制，二选一：SFX_LIST 战斗表加 `combat.crit` 预留行，或在 T32 验收备注"无暴击机制，该项不适用"。
- **S3（仅当按 T32 原文验收）**：右上角齿轮 + 设置面板（静音开关写 `localStorage` 键（建议 `redabyss_sfx_muted`），启动读入 `window.__SFX_MUTED`；音量条 disabled；SFX_LIST 入口）。纯 UI 增量，playSfx 已预留早退位，改动面小。
- **S4（记录勘误）**：TASK_DONE T41 notes「21 个 code」→ 实数 20（4+5+3+3+5）；并决定是否补一条「T32=T41 同任务并档」说明。
- **S5（可选）**：界面"切换"若要独立 code，清单加一行 `ui.switch`；或明确声明由 ui.open/close + ui.click 覆盖。
- **S6（顺手）**：`web/sfx/README.txt` 仍指旧 `sfx(name)` API，可更新为 `playSfx(code, opts)` + `window.RedAbyssSFX` 接管说明（该通道 playSfx 已兼容）。

## 4. 本轮操作记录

- 读取：tasks/T32.md、tasks/T41.md（diff）、docs/SFX_LIST.md、web/sfx/README.txt、TASK_DONE.md 相关段、web/index.html 定向检索。
- 检索命令均为只读 grep/find/ls；`node tools/check_web.js` 为只读校验。
- 写入：仅本文档 `docs/SFX_T32.md`。web/、engine/ 零改动。
