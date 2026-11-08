# X2 · CSS 变量清点

> 任务书：`tasks/HY4_batch2.md` §X2。审计对象 `web/index.html`（9258 行，2026-11-06 快照）样式块 `:6–:829`（全文仅 1 个 `<style>` 标签），另核 `tools/check_contrast.js`、`docs/UI_CONTRAST.md`、`docs/art/ART_STYLE_MATRIX.md` 作孤儿变量旁证。
> 方法：**按源码正则逐行枚举**，未开浏览器。行号 `:N` 指 `web/index.html`；外部文件用 `文件名:N`。
> `:6401` 的 `const RAW = "…"`（184653 字符）是卡牌数据，本篇未从该行取任何数值。
> 口径：`var()` 引用按**出现次数**计（同一行出现 2 次算 2 次）；定义按 `--x:` 声明**位置**计；「选择器」取该 `var()` 所在规则的选择器，`@keyframes` 内的记为 `@keyframes 名 / 帧`。

## 0 · 总账

| 指标 | 值 | 依据 |
|---|---|---|
| CSS 自定义属性**唯一名字** | **25 个** | 定义表 §1；其中 24 个定义在 `:root`/`html`/`body`，1 个（`--fan`）定义在组件上 |
| CSS 定义**位置**总数 | **49 处** | §1.1 的 9 个根级块共 47 处 + `:240 --fan` + `:609 --art-line` 组件级覆盖 |
| CSS `var()` 引用**总次数** | **262 次** | §2；分布在 **27 个唯一引用名**上 = 23 个已定义且有引用的名字 + 4 个 CSS 未定义但被引用的名字（`--layer-bg`/`--tx`/`--ty`/`--rot`）；25 个已定义名字中 2 个孤儿（0 引用）不计入 |
| 带 fallback 的 `var()` | **7 次** | 全部是 `:240/:245/:249` 的 `var(--tx,0px)` / `var(--ty,0px)` / `var(--rot,0deg)`；**其余 255 次全部无 fallback** |
| 孤儿变量（定义未用） | **2 个** | `--grain-opacity`、`--opt-sub`（§4） |
| CSS 未定义即被引用 | **4 个名字** | `--layer-bg`、`--tx`、`--ty`、`--rot`（§5），全部由 JS `setProperty` 运行时注入 |
| 运行时 JS 定义 | 6 处 | `:6550` `--bg`、`:6551` `--text`、`:6552` `--layer-bg`、`:8064` `--tx`、`:8065` `--ty`、`:8066` `--rot` |
| JS 读回变量 | 3 处 | `:8078`/`:8079`/`:8080` `getPropertyValue('--tx'/'--ty'/'--rot')` |
| 变量定义中引用别的变量 | **11 次** | `:537`(2)、`:666`(2)、`:667`(1)、`:668`(1)、`:671`(3)、`:672`(2)，见 §6 |

> 与 `04_css_audit.md:13` 对照：该文件记「49 个变量定义 / 255 处 `var(--…)`」。当前快照**定义数一致（49）**，引用数为 **262**（+7）；`04_css_audit.md` 记录的是更早的快照，`index.html` 在 2026-11-05 23:44 有过修改。本篇以当前快照为准。

---

## 1 · 定义清单

### 1.1 `:root` / `html` / `body` 上的 9 个定义块

| # | 块（行号 / 选择器） | 定义数 | 变量名 |
|---|---|---|---|
| 1 | `:7–15 :root` | 11 | `--bg`, `--opt-bg`, `--opt-bg-hover`, `--opt-fg`, `--opt-sub`, `--opt-border`, `--opt-bar`, `--red`, `--red-hi`, `--text`, `--dim` |
| 2 | `:41 :root` | 1 | `--lane: 1240px` |
| 3 | `:281 html[data-theme="B"], html[data-theme="C"]` | 6 | `--opt-bg`, `--opt-bg-hover`, `--opt-fg`, `--opt-sub`, `--opt-border`, `--opt-bar`（覆盖块 1） |
| 4 | `:532 :root` | 4 | `--paper`, `--ink`, `--ink-dim`, `--grain-opacity` |
| 5 | `:534 html[data-theme="A"]` | 6 | `--opt-bg`, `--opt-bg-hover`, `--opt-fg`, `--opt-sub`, `--opt-border`, `--opt-bar`（覆盖块 1） |
| 6 | `:536–542 html[data-theme="A"] body` | 5 | `--bg`, `--text`, `--dim`, `--red`, `--red-hi`（覆盖块 1，**作用在 `body` 而非 `:root`**） |
| 7 | `:608 :root` | 1 | `--art-line` |
| 8 | `:665–669 :root` | 7 | `--mm-panel`, `--mm-ink`, `--mm-dim`, `--mm-border`, `--mm-node`, `--mm-node-ink`, `--mm-pick` |
| 9 | `:670–673 html[data-theme="B"], html[data-theme="C"]` | 6 | `--mm-panel`, `--mm-ink`, `--mm-dim`, `--mm-border`, `--mm-node`, `--mm-node-ink`（覆盖块 8；**`--mm-pick` 无覆盖**） |

小计 47 处定义，24 个唯一名字。

### 1.2 组件级定义（非 `:root`）

| 变量 | 定义位置 | 值 | 作用域 |
|---|---|---|---|
| `--fan` | `:240 #hand .card` | `translateX(calc(-50% + var(--tx, 0px))) translateY(var(--ty, 0px)) rotate(var(--rot, 0deg))` | 仅 `#hand .card` 及其后代；被 `:241`、`:523`、`:653` 引用 |
| `--art-line` | `:609 html[data-theme="B"] .card .art, html[data-theme="C"] .card .art` | `rgba(43,33,24,.26)`（覆盖 `:608` 的 `rgba(240,236,230,.16)`） | 仅 B/C 主题下的 `.card .art` |

### 1.3 全部 25 个变量：定义点 / 值 / 引用数

| 变量 | 定义点（行号:选择器） | 默认值 / 覆盖值 | CSS `var()` 引用数 |
|---|---|---|---|
| `--bg` | `:8 :root`、`:537 html[A] body`、JS `:6550` | `#0a0506` / `color-mix(in srgb, var(--paper) 78%, var(--layer-bg) 22%)` | 2 |
| `--text` | `:13 :root`、`:538 html[A] body`、JS `:6551` | `#d8cfc9` / `#2b2118` | 21 |
| `--dim` | `:14 :root`、`:539 html[A] body` | `#a89a90` / `#6b5334` | 25 |
| `--red` | `:11 :root`、`:540 html[A] body` | `#8b1a1a` / `#8b2a20` | 28 |
| `--red-hi` | `:12 :root`、`:541 html[A] body` | `#e2705f` / `#6b1a12` | 62 |
| `--lane` | `:41 :root` | `1240px` | 3 |
| `--paper` | `:532 :root` | `#d9cfbe` | 12 |
| `--ink` | `:532 :root` | `#2b2118` | 9 |
| `--ink-dim` | `:532 :root` | `#6b5334` | 9 |
| `--grain-opacity` | `:532 :root` | `.55` | **0（孤儿）** |
| `--art-line` | `:608 :root`、`:609 B/C .card .art` | `rgba(240,236,230,.16)` / `rgba(43,33,24,.26)` | 8 |
| `--opt-bg` | `:10 :root`、`:281 B/C`、`:534 A` | `#e7dfcc` / `#e7dfcc` / `#f2ead8` | 3 |
| `--opt-bg-hover` | `:10 :root`、`:281 B/C`、`:534 A` | `#f5eee0` / `#f5eee0` / `#faf4e9` | 2 |
| `--opt-fg` | `:10 :root`、`:281 B/C`、`:534 A` | `#2b2118`（三处同值） | 2 |
| `--opt-sub` | `:10 :root`、`:281 B/C`、`:534 A` | `#6b5334`（三处同值） | **0（孤儿）** |
| `--opt-border` | `:10 :root`、`:281 B/C`、`:534 A` | `#2b2118` / `#6b5334` / `#2b2118` | 3 |
| `--opt-bar` | `:10 :root`、`:281 B/C`、`:534 A` | `#84b2e4`（三处同值） | 2 |
| `--mm-panel` | `:666 :root`、`:671 B/C` | `#101418` / `var(--paper)` | 5 |
| `--mm-ink` | `:666 :root`、`:671 B/C` | `var(--text)` / `var(--ink)` | 14 |
| `--mm-dim` | `:666 :root`、`:671 B/C` | `var(--dim)` / `var(--ink-dim)` | 11 |
| `--mm-border` | `:667 :root`、`:672 B/C` | `#2a323a` / `#b39a6b` | 10 |
| `--mm-node` | `:667 :root`、`:672 B/C` | `var(--text)` / `var(--ink)` | 1 |
| `--mm-node-ink` | `:667 :root`、`:672 B/C` | `#101418` / `var(--paper)` | 1 |
| `--mm-pick` | `:668 :root` | `var(--red-hi)`（**仅 1 处定义，无主题覆盖**） | 18 |
| `--fan` | `:240 #hand .card` | 见 §1.2 | 3 |
| `--layer-bg` | **CSS 无定义**，JS `:6552` | 运行时 `t.bg`（层色） | 1 |
| `--tx` / `--ty` / `--rot` | **CSS 无定义**，JS `:8064`/`:8065`/`:8066` | 运行时 `px` / `px` / `deg` | 各 3 / 3 / 1 |

> `--layer-bg`、`--tx`、`--ty`、`--rot` 列入本表是为完整覆盖「引用名」；它们**不是 CSS 定义**（见 §5）。

---

## 2 · 每个变量：引用次数与引用行号

| 变量 | 次数 | 去重选择器数 | 全部引用行号 |
|---|---|---|---|
| `--red-hi` | **62** | 55 | `:44,55,56,58,69,81,106,108,114,117,118,130,132,138,139,143,146,164,198,208,212,266,272,274,277,279,294,298,307,313,316,320,324,332,348,359,363,365,368,381,382,397,398,409,422,426,438,451,452,469,477,497,501,642,668,711` |
| `--red` | 28 | 27 | `:64,76,86,142,147,180,183,184,206,257,277,295,311,321,360,366,397,402,409,420,427,439,450,456,469,659,708,826` |
| `--dim` | 25 | 25 | `:45,74,102,104,152,179,229,231,232,264,275,291,303,314,333,334,350,370,383,394,423,453,466,639,666` |
| `--text` | 21 | 20 | `:20,64,70,72,80,105,133,181,225,273,292,317,336,364,366,398,424,450,666,667,708` |
| `--mm-pick` | 18 | 16 | `:700,727,733,747,749,752,753,754,757,758,774,775,797,813,817,818` |
| `--mm-ink` | 14 | 14 | `:698,699,715,722,724,732,734,739,745,755,778,787,794,811` |
| `--paper` | 12 | 11 | `:282,537,562,568,572,574,580,582,585,593,671,672` |
| `--mm-dim` | 11 | 11 | `:696,741,742,756,764,768,777,779,791,798,816` |
| `--mm-border` | 10 | 10 | `:703,716,724,729,764,767,788,794,800,806` |
| `--ink` | 9 | 8 | `:283,565,573,576,583,587,590,671,672` |
| `--ink-dim` | 9 | 9 | `:566,569,570,575,586,591,594,595,671` |
| `--art-line` | 8 | 5 | `:614,615,619,626,627,630,631,635` |
| `--mm-panel` | 5 | 5 | `:715,739,741,756,787` |
| `--lane` | 3 | 3 | `:35,43,329` |
| `--fan` | 3 | 3 | `:241,523,653` |
| `--tx` | 3 | 3 | `:240,245,249` |
| `--ty` | 3 | 3 | `:240,245,249` |
| `--opt-bg` | 3 | 3 | `:343,433,442` |
| `--opt-border` | 3 | 3 | `:344,434,442` |
| `--bg` | 2 | 2 | `:19,599` |
| `--opt-bg-hover` | 2 | 2 | `:348,438` |
| `--opt-fg` | 2 | 2 | `:343,433` |
| `--opt-bar` | 2 | 2 | `:344,434` |
| `--mm-node` | 1 | 1 | `:735` |
| `--mm-node-ink` | 1 | 1 | `:736` |
| `--rot` | 1 | 1 | `:240` |
| `--layer-bg` | 1 | 1 | `:537` |
| `--grain-opacity` | **0** | 0 | — |
| `--opt-sub` | **0** | 0 | — |

> 次数 ≠ 去重选择器数 / 去重行号的例子：`:208 .card.selected` 一行用了 2 次 `--red-hi`；`:477` 与 `:501` 各有一条 `@keyframes atkpulse`（同名重复定义），其中 `:477`/`:501` 各有 2 次 `--red-hi`。故 `--red-hi` 62 次 / 56 个行号 / 55 个去重选择器。

---

## 3 · 每个变量：在哪些选择器里用（去重）

- **`--red-hi`（55）**：`#screen-select h1`、` .classface .cname`、` .classface:hover, .classface:focus-visible`、` .classface:focus-visible`、`#class-modal-detail h2`、`#class-modal-close:hover`、`#hud .v.hp-low`、`@keyframes gazeblink / 50%`、`@keyframes pilepulse / 50%`、`@keyframes turnflash / 0%`、`#hud-relics span`、`.enemy.targetable`、` .enemy .ename`、`@keyframes ehit / 40%`、` .enemy .intent .i-atk`、` .enemy .hpbar .pmark`、`#phase-banner`、` .float`、` .card:hover`、` .card.selected`、` .card .cost`、`#card-detail .cd-close:hover`、`#cd-side h3`、`#cd-lines .warn`、`#cd-side button`、`#cd-side button:hover:not(:disabled)`、`#btn-end`、`#btn-end:hover`、`#btn-help:hover`、`#help-page h3`、`#help-page .hrow b`、`#help-page .btnrow button`、`#help-page .btnrow button:hover`、`#flow-panel h2`、` .optbtn:hover:not(:disabled)`、`#flow-panel .btnrow button`、`#flow-panel .btnrow button:hover`、`#flow-panel .statline b`、`#flow-panel .memoline`、` .relicrow .relic:hover`、` .relicrow .relic b`、` .mnode.here`、` .mnode.pickable`、`#toast`、`#overlay .panel h3`、`#overlay .panel button`、` .campopt:hover`、` .shopitem:hover`、` .shopitem b`、` .fontbtns button:hover`、`@keyframes atkpulse / 50%`、`.v.clarity-low`、`#hud-relics .rbadge, .relicrow .rbadge`、`:root`（`:668` 定义内引用）、`#hud-mapbtn:hover`
- **`--red`（27）**：`#class-modal-box`、`#class-modal-detail .cm-mechs li::before`、`#hud`、` .enemy .hpbar > i`、`#phase-banner`、`#log div.turnline`、`#log div.blocked`（×2 行）、` .card.costly`、`#card-detail`、`#cd-side button`、`#btn-end`、`#help-page`、`#help-page .btnrow button`、`#flow-panel .btnrow button`、`#flow-panel .ending`、` .mnode.here`、`@keyframes mblink / 50%`、`#toast`、`#overlay .panel`、`#overlay .panel button`、` .campopt b`、` .shopitem`、` .shopitem.cant:hover`、` .fontbtns button:hover`、`@keyframes resflash / 50%`、`#hud-mapbtn`、` .ending-art`
- **`--dim`（25）**：`#screen-select .sub`、`#class-modal-detail .cm-mechs li`、`.hud-stats .k`、`#hud .k`、` .enemy .hpnum`、`#log div`、`.card .cveins span`、`.card .ctype`、`.card .ctext`、`#card-detail .cd-close`、`#cd-lines .osub`、`#piles span`、`#btn-help`、`#help-page .hnote`、`#flow-panel .progress`、`#flow-panel .flavor`、`.optbtn .osub`、`#flow-panel .hintline`、` .relicrow .relic i`、` .mnode`、`#overlay .panel .prow`、` .shopitem i`、` .fontbtns button`、` .enemy .eart .esym-n`、`:root`（`:666` 定义内引用）
- **`--text`（20）**：`body`、`#class-modal-box`、`#class-modal-detail .cm-line`、`#class-modal-detail .cm-stats li`、`#class-modal-close`、`#hud .v`、` .enemy .intent`、`#log div.hurt`、`.card .cname`、`#cd-lines`、`#piles span:hover`、`#help-page .hrow span`、`#flow-panel .rulerow`、`#flow-panel .statline`、`#flow-panel .ending`、` .mnode.pickable`、`#overlay .panel .prow b`、` .shopitem`、`:root`（`:666`/`:667` 定义内引用）、`#hud-mapbtn`
- **`--mm-pick`（16）**：`#mm-legend .lg-tip`、`#btn-fullmap:hover`、`.fm-line.cross`、`.fm-node.btrack:hover circle`、`.fm-node.pick circle`、`.fm-node.here circle`、`.fm-node.hl circle`、`.fm-node.hl .fm-glyph`、`.fm-blabel.cur`、`.fm-band-cur`、`.mm-row.active`、`.mm-ic`、`#fm-zbar button:hover`、`#fm-close:hover`、`.fm-node.cursor circle`、`.fm-node.cursor text`
- **`--mm-ink`（14）**：`#mm-legend b`、`#mm-legend .lg-i`、`#minimap`、`#minimap .mm-head b`、`#btn-fullmap`、`.fm-line`、`.fm-line.walked`、`.fm-node.near circle`、`.fm-node.btrack circle`、`.fm-depth`、`.mm-gain`、`#fullmap-box`、`#fm-zbar button`、`#fm-close`
- **`--paper`（11）**：`html[B] #card-detail, html[C] #card-detail`、`html[A] body`、`.card`（B）、`.card .cost`（B）、`#log-wrap`（B）、`#help-page`（B）、`.card`（C）、`#log-wrap`（C）、`#help-page`（C）、`.card .cost`（C）、`html[B], html[C]`（`:671`/`:672` 定义内引用）
- **`--mm-dim`（11）**：`#mm-dock.big #mm-legend`、`.fm-node.unseen circle`、`.fm-node.unseen .fm-glyph`、`.fm-blabel`、`.mm-log-cap`、`.mm-log-empty`、`.mm-tail`、`.mm-desc`、`#fm-hint`、`#fm-zoom-val`、`.map-hint`
- **`--mm-border`（10）**：`#mm-dock.big #mm-log`、`#minimap`、`#btn-fullmap`、`#mm-body`、`.mm-log-cap`、`#mm-log-rows::-webkit-scrollbar-thumb`、`#fullmap-box`、`#fm-zbar button`、`#fm-svg`、`#fm-svg::-webkit-scrollbar-thumb`
- **`--ink`（8）**：`html[B] #cd-lines, html[C] #cd-lines`、`.card .cname`（B）、`#log`（B）、`#help-page .hrow span`（B）、`#log div`（C）、`#help-page .hrow span`（C）、`.card .cname`（C）、`html[B], html[C]`（定义内引用）
- **`--ink-dim`（9）**：`.card .ctext`（B）、`.card .ctype`（B）、`.card .cveins span`（B）、`#help-page .hnote`（B）、`#help-page .hnote`（C）、`.card .ctext`（C）、`.card .ctype`（C）、`.card .cveins span`（C）、`html[B], html[C]`（定义内引用）
- **`--art-line`（5）**：`.card .art.v-light`、`.card .art.v-water`、`.card .art.v-tremor`、`.card .art.v-mineral`、`.card .art.v-none`
- **`--mm-panel`（5）**：`#minimap`、`.fm-node.near circle`、`.fm-node.unseen circle`、`.fm-blabel`、`#fullmap-box`
- **`--lane`（3）**：`#screen-combat`（`:35`）、`#screen-select`（`:43`）、`#flow-panel`（`:329`）
- **`--fan`（3）**：`#hand .card`（`:241`）、`@media (prefers-reduced-motion: reduce) / #hand .card:hover:not(.dimmed):not(.dragging)`（`:523`）、`body.perf-low #hand .card:hover:not(.dragging)`（`:653`）
- **`--tx` / `--ty`（各 3）**：`#hand .card`（`:240`/`:245` 定义内）、`#hand .card:hover:not(.dimmed):not(.wrongworld):not(.dragging)`（`:245`）、`#hand .card.selected`（`:249`）
- **`--opt-bg`（3）**：`.optbtn`（`:343`）、`.campopt`（`:433`）、`.campopt.disabled:hover`（`:442`）
- **`--opt-border`（3）**：`.optbtn`（`:344`）、`.campopt`（`:434`）、`.campopt.disabled:hover`（`:442`）
- **`--bg`（2）**：`body`（`:19`）、`html[data-theme="C"] body`（`:599`）
- **`--opt-bg-hover`（2）**：`.optbtn:hover:not(:disabled)`（`:348`）、`.campopt:hover`（`:438`）
- **`--opt-fg`（2）**：`.optbtn`（`:343`）、`.campopt`（`:433`）
- **`--opt-bar`（2）**：`.optbtn`（`:344`）、`.campopt`（`:434`）
- **`--mm-node`（1）**：`.fm-node`（`:735`）
- **`--mm-node-ink`（1）**：`.fm-node .fm-glyph`（`:736`）
- **`--rot`（1）**：`#hand .card`（`:240` 定义内）
- **`--layer-bg`（1）**：`html[data-theme="A"] body`（`:537` 定义内）

---

## 4 · 孤儿变量（定义了没人用）

### 4.1 `--grain-opacity`

| 项 | 值 |
|---|---|
| 定义 | `:532 :root { --grain-opacity: .55 }`（全项目仅此 1 处定义） |
| CSS `var()` 引用 | **0 次**（`:6–:829` 全文 0 次；`web/*.html` 与 JS 亦 0 次） |
| 旁证 | `docs/art/ART_STYLE_MATRIX.md:16` 把它列为 C 主题「纸纹/暗角」的实现变量 |
| 代码事实 | C 主题 body 背景在 `:597–605` 用 3 条硬编码 `rgba(...)` 渐变（`radial-gradient` + 2 条 `repeating-linear-gradient`），**没有引用 `var(--grain-opacity)`**；`:605` 只写 `background-blend-mode: normal` |

→ 定义与文档一致、与实际实现不一致；变量值 `.55` 不参与任何计算。

### 4.2 `--opt-sub`

| 项 | 值 |
|---|---|
| 定义 | `:10 :root`、`:281 html[B],html[C]`、`:534 html[A]`（3 处，三处同值 `#6b5334`） |
| CSS `var()` 引用 | **0 次**（`:6–:829` 全文 0 次） |
| 检查器消费 | `tools/check_contrast.js:83` 把它列进 `need` 必填数组；`:87` 取 `v['--opt-sub']` 参与对比度计算 |
| 规范声明 | `docs/UI_CONTRAST.md:19` 写「副说明（.osub，--opt-sub）」 |
| **代码事实** | `:350 .optbtn .osub { color: var(--dim) }` —— 实际用的是 `--dim`（`:14` = `#a89a90`），**不是 `--opt-sub`**；`.campopt span` `:440` 只写了 `font-size:13px`，无 color |

→ `check_contrast.js` 校验的是 `--opt-sub` 与 `--opt-bg` 的对比度，但页面上 `.osub` 元素的颜色来自 `--dim`。**检查器验证的变量与元素实际使用的变量不是同一个**（代码事实，非渲染判断）。三个主题各定义一份却 0 引用，是四选项变量里唯一未被消费的。

### 4.3 非孤儿但引用极少（备查，不计入孤儿）

`--mm-node`（1 次，`:735`）、`--mm-node-ink`（1 次，`:736`）、`--rot`（1 次，`:240`）、`--layer-bg`（1 次，`:537`）——均有引用，不计入 §4。

---

## 5 · 用了但 CSS 里没有定义的变量

**严格结论：0 个「CSS 与 JS 都未定义」的名字。** 下列 4 个名字在 CSS 中无定义、被 `var()` 引用，但全部由 JS `setProperty` 运行时注入；按任务书口径列全并逐个判定是否构成真 bug。

| 变量 | 引用位置 | 有无 fallback | 运行时定义 | 判定 |
|---|---|---|---|---|
| `--layer-bg` | `:537 html[A] body { --bg: color-mix(in srgb, var(--paper) 78%, var(--layer-bg) 22%) }` | **无** | JS `:6552 s.setProperty('--layer-bg', t.bg)`，`applyLayerTheme()` `:6547–6554`，调用点 `:5508`（startCombat）、`:6558`（showMap） | **条件性真 bug**，见 5.1 |
| `--tx` | `:240`、`:245`、`:249`（共 3 次） | **有**（3 次均 `var(--tx, 0px)`） | JS `:8064`，并由 `:8078` `getPropertyValue` 读回 | 安全：未注入时退化为 `0px` |
| `--ty` | `:240`、`:245`、`:249`（共 3 次） | **有**（3 次均 `var(--ty, 0px)`） | JS `:8065`，`:8079` 读回 | 安全：未注入时退化为 `0px` |
| `--rot` | `:240`（1 次） | **有**（`var(--rot, 0deg)`） | JS `:8066`，`:8080` 读回 | 安全：未注入时退化为 `0deg` |

### 5.1 `--layer-bg`：唯一的无 fallback 缺口

- `:537` 的 `var(--layer-bg)` **没有 fallback**，是 262 次引用里唯一一个既无 CSS 定义、又无 fallback 的引用（262 − 7 次带 fallback = 255 次无 fallback，其中除本条外的 254 次所引用的变量在 CSS 中均有定义：`--fan` 定义在组件 `:240`，其余定义在 `:root`/`html`/`body`）。
- `:537` 定义在 `html[data-theme="A"] body` 上；A 主题不是默认值（`:2` 为 `data-theme="C"`），且 `:527` 注释写明主题切换靠 `document.documentElement.dataset.theme = 'A'|'B'|'C'|'off'`，全文未找到 JS 内的 `dataset.theme =` 赋值（仅 `:527` 注释）→ 需手工/控制台切换。
- `applyLayerTheme()` 只在进入战斗（`:5508`）与进入地图（`:6558`）时调用。在**选人屏（`#screen-select`）之前**，`:537` 若已因 A 主题生效而 `--layer-bg` 尚未注入，按 CSS 自定义属性规则该声明整体 invalid-at-computed-value-time，`body` 上的 `--bg` 会回落到从 `html` 继承的值（`:8` 静态 `#0a0506` 或 JS `:6550` 注入的层色），而不是 78/22 的纸色混色结果。
- **代码有、运行时不保证**：是否触发取决于主题切换时机与 `applyLayerTheme()` 调用顺序；未开浏览器验证，标记为条件性风险而非实测故障。

### 5.2 `--tx` / `--ty` / `--rot` 的补充

这 3 个名字是「CSS 无定义但**不会**失效」的一类：7 次引用全部带 fallback（`:240`、`:245`、`:249`），且 `layoutFan()`（`:8053–8068`）在每次布局时写入、拖拽逻辑（`:8078–8080`）再读回。归类为「运行时变量」，**不是 bug**。

---

## 6 · 变量链、优先级与运行时注入（代码事实）

1. **11 次「定义里引用变量」**：`:537`（`--paper`、`--layer-bg`）、`:666`（`--text`、`--dim`）、`:667`（`--text`）、`:668`（`--red-hi`）、`:671`（`--paper`、`--ink`、`--ink-dim`）、`:672`（`--ink`、`--paper`）。这些 `var()` 在**定义所在元素**上解析：`:666–668` 定义在 `:root`（html），取 `:8/:12/:13/:14` 的值；而 `:536–542` 的 A 主题覆盖写在 `body` 上，**不参与** `:root` 处这些 `var()` 的解析。→ B/C 主题 `--mm-*` 有 `:670–673` 覆盖，A 主题**没有** `--mm-*` 覆盖（`:670` 只匹配 B/C），这一层差异属「代码有、运行时不保证」，未开浏览器验证。
2. **JS 内联覆盖 `:root`**：`applyLayerTheme()` `:6550`/`:6551` 把 `--bg`/`--text` 写到 `document.documentElement.style`（`<html>` 的内联样式）。内联样式优先级高于样式表里的 `:root {…}`（`:8`/`:13`），所以在 B/C/off 主题下（`body` 自身无 `--bg`/`--text` 声明），`:8 --bg:#0a0506` 与 `:13 --text:#d8cfc9` 在 `applyLayerTheme()` 执行后被层色覆盖。→ 静态值「代码有、运行时不保证」。
3. **主题覆盖落点不一致**：块 3（`:281`）、块 5（`:534`）、块 9（`:670`）写在 `html[…]` 上，与块 1/4/8 的 `:root` 同元素、靠选择器特异性覆盖；块 6（`:536`）写在 `body` 上，与 `:root` 不同元素、靠继承/自身声明生效。两类落点不同，见第 1 条。
4. **`--mm-pick` 无主题覆盖**：`:668` 只在 `:root` 定义一次（`var(--red-hi)`）；`:670–673` 的 B/C 覆盖块里没有它。9 个 mm 变量中唯一如此。
5. **重复定义**：`:477` 与 `:501` 各有一份完全相同的 `@keyframes atkpulse`，不影响变量但使 `--red-hi` 的引用计数 +2（见 §2 注）。
6. **主题只改颜色不改尺寸**：B/C/A 覆盖规则（`:536–605`、`:670–673`）不含任何 width/height/font-size 声明，与 `x1_sizes.md` 的结论一致。

---

## 未验证清单

本篇所有计数与行号均可由源码复算；下表是**结论层面**无法由静态代码确定的项，按任务书口径标注：

| # | 项 | 标注 |
|---|---|---|
| 1 | `--layer-bg` 在 A 主题选人屏的实际计算值 | **未验证**：需运行时观察 `applyLayerTheme()`（`:6547`）调用时机与主题切换顺序；未开浏览器 |
| 2 | `:root`（`:666–668`）处 `--mm-*` 的 `var()` 实际解析结果 | **未验证**：按规范不受 `body` 上 A 主题覆盖（`:536–542`）影响，但属运行时计算值行为；未开浏览器 |
| 3 | `document.documentElement.style` 内联 `--bg`/`--text`（`:6550–6551`）与 `:root` 静态值（`:8`/`:13`）的最终生效值 | **未验证**：取决于 `applyLayerTheme()` 何时执行；未开浏览器 |
| 4 | `check_contrast.js:87` 的 `--opt-sub` 断言与页面 `.osub`（`:350`）实际色值的对比度差 | **未验证**：只能确定「用的不是同一个变量」；差值需另跑检查器，本篇不越界 |
| 5 | `04_css_audit.md:13` 的 255 处与当前 262 处的 7 处差来自哪几条规则 | **未验证**：只能确定两个快照不同；未对历史快照做逐行 diff |

---

## 边界声明

- 我没开浏览器，所有定义/引用/次数是**按源码静态枚举算的**，不是运行时实测值；本篇不含尺寸核算，尺寸结论见 `x1_sizes.md`。
- CSS 优先级打架时，写了也未必生效；这类标「代码有、运行时不保证」（本篇涉及 `:537` 的 `--layer-bg`、`:6550–6552` 的内联覆盖、`:666–668` 的变量链解析点、`:536–542` 的 body 级覆盖）。
- 主题：`<html data-theme="C">`（`:2`）；B/C/A 覆盖块只改颜色变量值，不改任何变量名或尺寸。
- 本篇仅新增 `docs/design/ui/x2_css_vars.md`，未修改 `web/`、`engine/`、`cards/*.json`、`tools/` 或任何源文件。
- 复算方式：对 `web/index.html` `:6–:829` 去注释后，正则 `(--[A-Za-z0-9_-]+)\s*:` 取定义、`var\(\s*(--[A-Za-z0-9_-]+)` 取引用；`var()` 的选择器上下文用「遇到 `{` 压栈 / `}` 出栈」的单遍扫描定位；JS 侧 `setProperty`/`getPropertyValue` 单独枚举，跳过 `:6401` RAW 行。
