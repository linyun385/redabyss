# FIX_T34 — T34「布局修复与机制说明」补做审计

- 日期：2026-11-03（夜班补做）
- 性质：**纯审计，未改任何代码**。T34 当年未写入 TASK_DONE.md，但其六个问题在后续迭代（T37/T44/T53/T71/T74/T78 等）中已各自被修。本文逐条核对 `tasks/T34.md` 原文与现状，给出判定、证据（文件:行号）与遗留建议。
- 说明：T34 标题写「用户提了 5 个问题」，正文实际列了**六个**小节（问题一~问题六，问题六为机制说明专项）。本文全部覆盖，验收里的浏览器手工项（真开浏览器点 10 回合等）静态审计无法执行，一律以 CSS/JS 结构证据代替，并如实标注。

## 问题一：日志撑爆页面，点不到「结束回合」🔴

**原文要点**：回合多了日志累积，页面被撑高出现页面级滚动条，「结束回合」被挤出视口。根因是 flex 子项默认 `min-height: auto`。验收：打完 10 回合页面无滚动条，`document.documentElement.scrollHeight === innerHeight`。

**判定：已修。**

**证据**（均在 `web/index.html`）：
- L30-38：`#screen-combat { flex: 1 1 0; min-height: 0; display: flex; flex-direction: column; ... }`——`min-height: 0` 就位，且注释原文写着「战斗屏必须能被压缩，否则日志会把页面撑爆、把『结束回合』挤出视口」，即当年就是按此问题修的。
- L171-174：`#log-wrap { flex: 1 1 0; overflow-y: auto; padding: 8px 14px; border-bottom: 1px solid #2a1517; min-height: 60px; }`——与任务书修复 CSS 逐字一致（`flex: 1 1 0` 用 0 不用 auto，`min-height: 60px` 保留）。
- L184：`#hand-area { padding: 8px 14px 12px; flex: 0 0 auto; }`——手牌区不压缩，一致。
- 外围 L24 / L28：`body { overflow: hidden; }`、`#app { height: 100vh; overflow: hidden; }`，页面级滚动条被双保险拦死。
- 「结束回合」按钮（`#btn-end`）在 `#hand-foot` 内随手牌区 `flex: 0 0 auto` 固定于视口底部，不再被日志推移。

**建议**：无需改动。

## 问题二：HUD 横向撑破 🔴

**原文要点**：遗物变多后顶部一排横向超出屏幕。任务书给了两个方案：CSS 溢出处理（`overflow: hidden` + 遗物收缩省略），「或者更简单：遗物超过 4 个时折叠成遗物 ×N」。

**判定：已修（溢出处理方案，遗物行独立换行）。**

**证据**（`web/index.html`）：
- L84-89：`#hud { ... white-space: nowrap; flex: 0 0 auto; overflow: hidden; }`——`overflow: hidden` 就位，HUD 不会再横向撑破父级。
- L90：`.hud-stats { display: flex; gap: 18px; justify-content: center; flex-wrap: wrap; }`——数值行可换行。
- L103：`.hud-relics { display: flex; gap: 8px; justify-content: center; flex-wrap: wrap; font-size: 12px; }`——遗物独立成行、可换行，遗物多时向下堆叠而非横向溢出。
- L118 / L642：`#hud-relics span { cursor: help; ... }`——每个遗物带悬停说明。

**建议**：无需改动。若日后遗物多到 HUD 纵向过高，可给 `.hud-relics` 加 `max-height: 1.6em; overflow: hidden;` 一行做限高（可选，非必须）。

## 问题三：HUD 应该常驻所有界面 🟡

**原文要点**：只有战斗界面有 HUD，路上（地图、事件、商店、营火）扣血/得金币/加凝视看不到。验收：地图上扣血，回地图立刻见血量变化。

**判定：已修。**

**证据**（`web/index.html`）：
- L831-844：`<header id="hud">` 位于 `#app` 直下、三个 `<section>` 屏幕之前，DOM 注释「HUD 常驻：所有界面都在（选职业时隐藏）」——结构上已提升到 `#app` 层级。
- L6504：`showMap()` 内 `$('#hud').classList.remove('hidden');   // HUD 常驻：进局后所有界面都显示`。
- L6505-6512：非战斗界面同步 `run.hp / run.gaze / run.gold / progressText()`，且注释「HUD 常驻后，层行不能只靠战斗渲染刷新」；格挡/能量/共鸣作为战斗内概念在地图上收起（L6506-6508）——数据来源统一走 `run` 对象，符合任务书要求。
- L6456：`restart()` 回选职业界面时才收起 HUD，语义正确。
- 金币在商店/事件变动后经 `showMap()` 重绘，凝视变化另有 L7711 处的闪红动画（`#gaze-val.flash`）。

**建议**：无需改动。验收点属手工浏览器项，结构上数据链路（showMap 读 run 重绘 HUD）已满足。

## 问题四：三个界面尺寸不一致 🟡

**原文要点**：开场/路程/战斗三界面宽度、留白、居中方式不一，切换时画面跳。任务书建议三屏共用同一条 `.screen` 容器规则。验收：三界面来回切换，左右边距、标题位置不跳。

**判定：已修（实现为统一 1240px「内容梁」，非任务书原样的单一 `.screen` 规则）。**

**证据**（`web/index.html`）：
- L40-41：注释「── 统一内容梁：所有界面同宽、同位置 ──」+ `:root { --lane: 1240px; }`。
- L30-38：`#screen-combat` 用 `max-width: var(--lane); margin: 0 auto; box-sizing: border-box;`，注释明确「和地图/事件/开场共用同一条 1240px 内容梁，切换界面不跳」。
- L43：`#screen-select { margin: auto; ... width: 100%; max-width: var(--lane); }`。
- L320-322 附近：`#screen-flow { flex: 1 1 0; min-height: 0; overflow-y: auto; ... }`，`#flow-panel { max-width: var(--lane); margin: auto; width: 100%; }`。
- 三屏宽度梁同为 `--lane: 1240px`、同为水平居中，横向不跳；未做单一 `.screen` 类，而是按屏写规则但共用同一变量。

**建议**：无需改动。若追求彻底统一，可把 `#screen-flow` 的 `padding: 24px 16px` 与 `#screen-select` 的垂直居中策略对齐成一条规则（可选，现状三屏间距差异很小，且 T78 重做选职业界面时已按梁对齐）。

## 问题五：keep_block 遗物让格挡无限累积 🔴

**原文要点**：拿到 keep_block 遗物后格挡一路累积到 44，变成第二条命。任务书给三个方案，推荐 A（回合结束保留一半）。另要求把遗物 `effect_text` 改准确。

**判定：已修（采用推荐方案 A：保留一半）。**

**证据**：
- `engine/core.js` L648-651：
  ```js
  // 遗物改则：格挡保留（2026-10-29 与 web 对齐：不再无限累积，只留一半）
  let keepBlock = false;
  (C.run.relics || []).forEach(r => { if (r.mod && r.mod.keep_block) keepBlock = true; });
  if (keepBlock) C.block = Math.floor(C.block / 2); else C.block = 0;
  ```
  即任务书原根因代码 `if (!keepBlock) C.block = 0;`（永不清零）已改为 `Math.floor(C.block / 2)`，滚雪球被斩断。
- `web/index.html` L6005-6008：内联引擎副本为同一逻辑（含「遗物改则：格挡保留」注释），web 与 engine 已对齐。
- `effect_text` 已改准，四处 keep_block 遗物文案全部与「留一半」一致：
  - `relics/all.json` relic_27 圣火残留（长明）：「回合结束时，格挡只熄一半。」
  - `relics/all.json` relic_55 渊民的合葬结：「回合结束时，格挡留下一半……」
  - `relics/anmin.json` anrelic_11 封存册残页：「回合结束时，格挡封存一半……」
  - `relics/cangmin.json` cngrelic_10 猎巫密册（残）：「回合结束时，格挡只记下一半……」
- 文案三处互洽：HUD 格挡项悬停 title（L833「遗物可留一半」）、`?` 面板格挡行（L919「有遗物替它续着的话，剩一半」）、遗物 effect_text，说的都是同一规则。

**建议**：无需改动。`node tools/test_engine.js` 全部通过，引擎侧行为有测试背书。

## 问题六：核心机制没有说明 🟡

**原文要点**：用户玩了两局仍不理解格挡。要做三件事：1) HUD 格挡数字后加极小标记（如 `🛡 44 ↓`）悬停显示「回合结束会消失」；2) 战斗界面右下角加 `?` 按钮，点开一页纸机制速查（生命/格挡/能量/共鸣/凝视五条，文风按 STYLE_SAMPLES）；3) 首次获得 keep_block 类遗物时浮提示「你的格挡不会再消失了。」

**判定：已修（第 1 件以变体实现，第 2 件完整实现，第 3 件未实现且原文案已因机制变更失实）。**

**证据**（`web/index.html`）：
- 第 2 件（`?` 面板，完整）：
  - L892：`<button id="btn-help" title="机制速查">?</button>`，位于 `#hand-foot` 内「结束回合」右侧，即战斗界面底部偏右；L296 CSS 注释「? 机制速查（战斗右下角）」。
  - L914-928：`#help-page`「下潜须知」，含**生命/格挡/能量/共鸣/凝视/代价**六行速查，覆盖任务书要求的四机制且超配两条。格挡条目原文：「敌人动手时，先落在它上面。你的回合一结束，它就散了——有遗物替它续着的话，剩一半。」文风即任务书要求的调子（「这一页写给还没死的人。」）。手工自检第 6 条「? 面板能看到四个机制的说明」结构上满足。
- 第 1 件（HUD 格挡说明，变体）：
  - L833：格挡项整项带悬停 title「格挡：敌人动手时先落在它上面；你的回合一结束就散（遗物可留一半）」。没有做 `↓` 小标记字符，但悬停即见说明的效果达成，且 T37（L110-111）加了获得格挡时的盾形脉冲动画作为视觉反馈。
- 第 3 件（首获 keep_block 浮提示）：全文件检索「不会再消失」无命中，未实现。**且该文案已失实**——机制已改为留一半，「不会再消失」不再成立。

**建议**（最小修复，未动代码）：若要补齐第 3 件，在获得 keep_block 类遗物（relic_27 / relic_55 / anrelic_11 / cngrelic_10）时 toast 一次，文案需改为与现行机制一致，例如：「回合结束后，你的格挡只散一半。」实现上在发遗物入口加一个 `run.flags.seen_keep_block` 判定即可，约 5 行。`↓` 标记可不做（现悬停方案已覆盖说明职责）。

## 自检记录（铁律：未改 web/、engine/ 任何文件，仅新增本文档）

```
node tools/check_web.js      → 全部通过（0 个警告；17 项 ok：自包含、引擎内联、
                               四核心 API 接线、HUD 要素齐全、素材 84 处引用全存在等）
node tools/test_engine.js    → 全部通过
node tools/pack_check.js all → 全部通过（5 个警告，均为扩充内容计数提示：
                               卡 83/敌人 113/遗物 77/事件 82 等，与 T34 无关）
```

## 结论速览

| # | 问题 | 判定 | 一句话证据 |
|---|------|------|-----------|
| 一 | 日志撑爆页面 | 已修 | `#screen-combat` min-height:0 + `#log-wrap` flex:1 1 0/overflow-y:auto（L32/L171），与任务书 CSS 逐字一致 |
| 二 | HUD 横向撑破 | 已修 | `#hud` overflow:hidden + 遗物行独立 flex-wrap:wrap（L84/L103） |
| 三 | HUD 常驻所有界面 | 已修 | `#hud` 提至 `#app` 直下，showMap 同步 run 数值（L831/L6504-6512） |
| 四 | 三界面尺寸不一 | 已修 | 统一 `--lane:1240px` 内容梁，三屏同宽同位（L41/L43/L320） |
| 五 | keep_block 格挡无限累积 | 已修 | 方案 A 留一半，engine/web 双侧一致，4 件遗物 effect_text 已改准 |
| 六 | 机制无说明 | 已修（1 处遗留） | `?` 面板六行速查 + 格挡悬停说明均在；首获 keep_block 浮提示未做且原文案已失实，见上文最小建议 |

T34 可视为**实质完成**：六个问题中五个完全修复、一个（问题六）修了主体并留一个可选小项。遗留事项仅问题六第 3 点的首获提示，属锦上添花，不阻断体验。
