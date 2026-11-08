# H2 · 键盘可达性实证

> 输入：`C:\Users\Administrator\Desktop\杂七杂八\红渊\game\web\index.html`（冻结版本）
> 输出口径：代码级事实，只写能数、能指回行号的东西。

---

## 1. 检索方法与界面清单

**键盘监听检索式**：`addEventListener\(['"](keydown|keyup|keypress)['"]|onkeydown|onkeyup|onkeypress|\.onkey`。
结果：**7 处 `keydown`，全部绑定在 `document` 上**；`keyup` / `keypress` / 内联 `onkeydown=` / `.onkeydown` **均为 0 处**。
（另有 2 处非键盘输入：`#fm-svg` 的 `wheel` 9053 与 `pointerdown` 9054，`#hand .card` 的 `pointerdown` 7905，均不计入监听表。）

**界面容器**：代码里只有 3 个 `<section class="screen">`：

| 容器 | 行号 | 承载的界面 |
|---|---|---|
| `#screen-select` | 851 | 开始页（职业卡面 855–870） |
| `#screen-combat` | 882 | 战斗 |
| `#screen-flow` | 913 | 地图 6556、营火 6682、商店 6833、事件 7370、奖励 7156/7251/7279、结算 7452/7519 |

`showScreen()` 6516–6519 只在这 3 个 section 间切 `hidden`。**任务书列的「图鉴」「设置」没有独立 section**：以 `图鉴|codex|设置|settings` 检索，只命中 CSS 注释 516 和事件选项 `ev.options`（7380、7400、8755），没有对应界面函数或 DOM。全局只有一组浮动按钮 `.fontbtns`（932–936：字号 ±、低饱和）和帮助浮层 `#help-overlay`（918–930）。

**phase 取值**：6449 注释列出 `select | intro | combat | reward | event | gameover | victory`；实际赋值另有 `map`（6557）。事件是 `event`（7371），商店/营火/奖励统一是 `reward`（6683、6740、6775、6834、7237、7252、7280、7415），结算是 `gameover`（7454）/ `victory`（7522）。

---

## 2. 第一张表：监听清单（7 处）

| 位置（行号） | 绑定目标 | 支持的键 | 生效条件 | 作用 |
|---|---|---|---|---|
| 6933–6935 | `document` | `w` / `W` | 按钮 `#btn-world` 存在、`!b.disabled`、不含 `hidden`（6934）；**无 phase 守卫** | `b.click()` → 触发 6925 的入梦/醒切换 |
| 6960–6966 | `document` | `Escape` | **无 phase 守卫** | 6962 关 `#help-overlay`；6963 关 `#card-detail`；6964 清 `pending`（且 `window.G.phase === 'combat'` 时 `render()`） |
| 8271–8273 | `document` | `Escape` | `modalClass` 非空（8272），即职业详情模态打开 | `closeClassModal()`（8260） |
| 8291–8311 | `document` | `Escape` / 方向键 / `Enter` / `Space` / `e` `E` / 数字 `1`–`9` | 分三段守卫：① `Escape` 无守卫（8292）；② `phase === 'map'`（8293）且 `.mnode.pickable` 非空（8295）；③ `phase === 'combat' && C && !C.over`（8304） | ① 8292 `hideOverlay()`（8211）；② 8298–8300 方向键在 `.mnode.pickable` 间 `.focus()`，8301 `Enter`/`Space` 点击当前焦点；③ 8305 `Enter`/`e`/`E` 点 `#btn-end`；8306–8309 数字键点第 n−1 张 `#hand .card` |
| 9014–9029 | `document`（注册于新地图 IIFE，8319） | `ArrowUp` / `ArrowDown` / `ArrowLeft` / `ArrowRight` / `Space` / `Enter` | `st.region && st.runRef === run`（9015）、`!fm.open`（9016）、`phase === 'map'`（9017）；且整个 IIFE 在 `?map=old` 时 `return`（8321）不注册 | 9018–9020 方向键 `moveCursor()`（8995）；9021–9027 `Space`/`Enter` 若光标在 `currentPicks()`（8987）内则 `enterNode(st.cursorId)` |
| 9049–9051 | `document`（同一 IIFE） | `Escape` | `fm.open`（9050） | `closeFullMap()`（8604） |
| 9063–9069 | `document`（同一 IIFE） | `Tab` | `st.region && st.runRef === run`（9065），即「局内」；`?map=old` 时不注册（8321） | 9066 `e.preventDefault()` **阻止 Tab 原生焦点移动**；9068 用 Tab 开/关总图（`openFullMap` 8592 / `closeFullMap` 8604） |

**重叠**：`phase === 'map'` 时，8291（8293–8302）与 9014（9014–9029）**同时命中方向键与 `Enter`/`Space`**：前者操作 `.mnode.pickable` 的 DOM 焦点并 `.click()`（8301），后者操作新地图 `st.cursorId` 并 `enterNode()`（9026）。两者是否在同一时刻都生效，取决于 `st.region` 是否已赋值（8692 `st.region = MG.generate(...)`、8704 `st.runRef = run`）——本审计未追踪该赋值调用链，见 §5。

---

## 3. 第二张表：界面 × 键盘矩阵

判定口径：「有键盘操作」= 有**显式 `keydown` 代码路径**能推进该界面；或局外 Tab 未被劫持、控件是原生 `<button>`（此时依赖浏览器原生行为，已标注）。

| 界面 | 有无键盘操作 | 能做什么 | 不能做什么（必须鼠标） |
|---|---|---|---|
| **开始页**（`#screen-select` 851） | **有（原生，代码无显式 keydown 绑定）** | 局外（`run` 未建立、`st.region` 为空）9063 的 Tab 守卫不成立 → Tab 可聚焦 4 个 `<button classface>`（855、859、863、867）；`Enter`/`Space` 按原生 `<button>` 行为触发 8265 的 click → 开职业详情模态；模态内 8258 自动 `.focus()` 到 `#btn-dive-confirm`（8256），可原生触发 8276 的委托点击开局；`Escape` 8271 关模态 | 无显式 keydown 绑定；原生 `<button>` 的键盘激活**运行时未验证**（§5）。点遮罩关（8268）、`×` 关闭（876 / 8267）只有 click |
| **地图**（`phase='map'`，6556） | **有** | 方向键在 `.mnode.pickable` 间移动焦点（8298–8300；节点 `tabIndex=0` 6606、`role=button` 6607）；`Enter`/`Space` 进入节点（8301 → 6609）；新地图下方向键移光标 + `Enter`/`Space` 进节点（9018–9027）；`Tab` 开/关总图（9068）；`Escape` 关总图（9050）/关 overlay（8292） | 总图缩放 3 个按钮（8345–8346 创建，9055–9057 绑 click）、总图节点 `<g tabindex="0">`（8500，click 8658/8666）、小图行程行（8555 click）、HUD「地图」按钮（8340、9059）、`#btn-fullmap`（960、9044）都只有 click；Tab 被 9066 劫持后无法用 Tab 到达这些控件 |
| **战斗**（`phase='combat'`，6895） | **有（部分）** | `Enter` / `e` / `E` 结束回合（8305 → 6967）；`w`/`W` 入梦/醒（6934 → 6925）；`Escape` 取消选牌、关卡牌详情（6962–6964）；数字 `1`–`9` 尝试点第 n−1 张手牌（8306–8309，**代码级不成立，见 §4.1**） | **选敌人目标**：`#enemy-area .enemy` 只有 click（7839），没有任何键盘路径；手牌交互只绑 `pointerdown`（7905 → 7977），拖动/点击出牌必须鼠标；`#cd-play` / `#cd-cancel` / `#cd-close`（8109–8111 `onclick`）、牌堆三个 span（8208–8210 click）、`#btn-help`（6936）、`#hud-parts`（8214）、字号/低饱和按钮（8280、8285、8290）均只有 click |
| **事件**（`phase='event'`，7370） | **无** | 仅 `Escape` 能关 overlay（8292）；8291 在 8304 因 `phase !== 'combat'` 直接 `return` | 事件选项 `<button class="optbtn">`（7381，click 7393）、「接着看/继续下潜」（7434–7435）全部只能点。虽有原生可聚焦的 `<button>`，但局内 Tab 被 9066 阻止 |
| **商店**（`phase='reward'`，6833） | **无** | 同上（仅 Esc） | 商品格 `.shopitem` 是 `<div>` 无 `tabIndex`（6845，click 6850）、「离开」按钮（6879，click 6880）只能点 |
| **营火**（`phase='reward'`，6682） | **无** | 同上（仅 Esc） | 3 个 `.campopt` 是 `<div>` 无 `tabIndex`（6693，click 6697）；升级/移除选卡面板的卡（6764、6795 click）、「继续」按钮（6750、6784）只能点 |
| **奖励**（`phase='reward'`，7156 / 7251 / 7279） | **无** | 同上（仅 Esc） | 奖励卡 `renderCardStatic()` 产物是 `<div class="card">`（7353，click 7262）；遗物行 `.relicrow` 是 `<div>`（7286，click 7291）；「跳过」（7272–7273）、「不拿」（7301–7302）只能点 |
| **结算**（`phase='gameover'` 7454 / `victory'` 7522） | **无** | 同上（仅 Esc） | 「重新开始」（7471–7472、7561–7562、7567–7568）、「进入静默段」（7475–7477）、「回头」（7552–7554）全是 click |
| **图鉴** | **无对应界面** | — | 检索 `图鉴|codex` 无命中；未见界面函数、DOM 或 phase |
| **设置** | **无对应界面** | — | 只有全局浮动 `.fontbtns`（932–936）与 `#help-overlay`（918–930）；`#font-minus`/`#font-plus`/`#lowsat`（8280/8285/8290）、`#btn-help`/`#btn-help-close`（6936/6941）全是 click，局内 Tab 被劫持后无法 Tab 到达 |

### 3.1 附加：浮层 × 键盘（任务书未列，但影响「能不能全程键盘」）

| 浮层 | 行号 | 键盘能做什么 | 必须鼠标 |
|---|---|---|---|
| 职业详情模态 `#class-modal` | 874–880 | `Escape` 关（8271）；`#btn-dive-confirm` 被自动 focus（8258） | 点遮罩（8268）、`×`（8267） |
| 帮助浮层 `#help-overlay` | 918–930 | `Escape` 关（6962） | 打开按钮 `#btn-help`（6936）、`#btn-help-close`（6941）、点遮罩（6944） |
| 总图 `#fullmap-layer` | 963–969 | `Tab` 开关（9068）、`Escape` 关（9050） | 节点（8658/8666）、缩放（9055–9057）、`#fm-close`（9045）、点背景（9046）、滚轮缩放（9053）、拖拽平移（9054） |
| 通用遮罩 `#overlay`（牌堆查看 8190、改造/拆解 8151） | 957 | `Escape` 关（8292 → 8211） | 打开（8208–8210、8214）、改造/拆解/关闭 3 个按钮（8163、8175、8183）、「合上」（8204） |
| 卡牌详情 `#card-detail` | 900–910 | `Escape` 关（6963） | 打开靠手牌 `pointerdown`（7905 → 7998）；「打出/收回/关闭」（8109–8111） |
| 字号/低饱和 `.fontbtns` | 932–936 | 无 | 3 个按钮（8280、8285、8290） |
| toast / phase-banner | 931 / 937 | 无（纯展示） | — |

---

## 4. 三处决定「能不能全程键盘」的代码级事实

### 4.1 数字键 1–9 的 `.click()` 与手牌监听器类型不匹配

- 手牌元素：7888 `el('div', 'card' + ...)`，7905 只绑定 `d.addEventListener('pointerdown', ...)` → `startCardPointer()`（7977）。
- 数字键路径：8308 取 `#hand .card`，8309 调用 `cardEl.click()`。
- 全文检索 `#hand` / `.click()` 结果：`#hand .card` **没有任何 `click` 监听注册**（相关行 188–189、238–252、7905、7961、8308–8309 均为样式、`pointerdown` 或查询）。
- 按 DOM 事件语义，`HTMLElement.click()` 只派发 `click` 事件，不派发 `pointerdown`。因此 8309 这条数字键路径在代码层面**不会进入 `startCardPointer`**。
- 对照：8301 地图节点的 `.click()` **有效**，因为 6609 确实注册了 `click`；8305 `#btn-end` 的 `.click()` **有效**，因为 6967 注册了 `click`。

### 4.2 Tab 在局内被全局劫持

- 9063–9069：局内（`st.region && st.runRef === run`，9065）任意 `Tab` 都会 9066 `preventDefault()`，然后 9068 开/关总图。
- 该监听**没有 phase 守卫**：战斗、事件、商店、营火、奖励、结算全部命中。
- 结果是：这些界面里所有原生 `<button>`（事件选项 7381、跳过 7272、重新开始 7471 等）虽然可聚焦，但无法用 Tab 到达。
- CSS 471 确实给 `button:focus-visible, .mnode:focus-visible, .campopt:focus-visible, .card:focus-visible` 写了焦点样式；显式设 `tabIndex = 0` 的只有 6606（地图节点）和 8500（总图 `<g>`）两处。

### 4.3 敌人目标没有键盘入口

- 敌人 box：7801 `el('div', 'enemy' + ...)`，7839 `box.addEventListener('click', ...)` → 7841 `doPlay(pending, e.idx)`。
- 需要指定目标的牌由 `needsTarget()`（7606）判定；拖动时 7997 给敌人加 `.targetable` 类，但最终落点仍由指针坐标 `dropEnemy()`（8006）决定。
- 8291 的战斗分支只有「结束回合」和「数字键点手牌」，**没有任何选择敌人的键**。所以即便数字键能选中牌，需要目标的牌仍无法用键盘完成。

**结论（代码级）**：只有开始页（原生 Tab + button）和地图（显式方向键/回车）有可用键盘路径；战斗只有「结束回合、入梦、取消」三个动作；事件/商店/营火/奖励/结算没有推进界面的键盘入口。因此**不能全程用键盘玩**。

---

## 5. 未验证项

- **未验证：原生 `<button>` 的键盘激活行为未做运行时测试**（开始页 4 个 `.classface`、模态内 `#btn-dive-confirm` 等）。本报告只说明「代码没有显式 keydown 绑定、控件是 `<button>`、`Tab` 在局外未被劫持」三件可数的事实。
- **未验证：8291 与 9014 两条地图监听在运行时是否同时生效**。`st.region` / `st.runRef` 的赋值在 8692 / 8704，本次未追踪其调用链；只确认了守卫文本（9015）与 IIFE 的 `?map=old` 早退（8321）。
- **未验证：`?map=old` 回退模式下的实际表现**。8321 使整个新地图 IIFE 不执行，故 9014 / 9049 / 9063 三个监听不注册；此时 Tab 不被劫持，但本次未逐界面重算该模式下的可达性。
- **未验证：`const RAW`（6401，184653 字符）与 `window.ART`（3945，23442 字符）未解析**。它们是数据行，与键盘监听无关；检索工具已自动折叠这两行。
- **未验证：图鉴/设置是否以其它名称存在**。本次按 `图鉴|codex|设置|settings` 与 3 个 `section.screen` 清单核对，未命中。

---

## 6. 边界声明

- 我没开浏览器，所有结论是**代码级**的，不是视觉判断；文中不含「看起来」「感觉」「可能有点」这类描述。
- 我读到的是 `web/index.html` 的**当前冻结版本**（641927 B / 本地实测 9165 行；任务书标 8930 行，差异原因未查明）。如果之后代码变了，行号会漂移，结论要重跑。
- 我数的是**代码里写了什么**，不是**运行时实际渲染成什么**。特别是 §4.1 的「`.click()` 不触发 `pointerdown`」是按 DOM 事件语义推得的代码级结论，未在浏览器中验证；这类情况统一标注为「代码有、运行时不保证」。
- 只读审计：未修改 `web/`、`engine/`、`cards/` 下任何文件；本文件是 `docs/design/ui/` 下新建的产出。
