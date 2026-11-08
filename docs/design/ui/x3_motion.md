# X3 · 动画与过渡清点

> 数据源：`web/index.html`（9490 行 / 662497 字节，2026-11-06 版本）。
> 任务来源：`tasks/HY4_batch2.md` X3 节 + 硬规矩（§99–113）。
> 产出：本文件。除本文件外未新建或修改任何项目文件；未写 `_HY4_PROGRESS.md`（按本次任务指令由主代理统一追加）。

---

## 0. 清点口径与复核方法

**CSS 边界**：`<style>` 在 `index.html:6`，`</style>` 在 `index.html:831`，CSS 有效区为 **第 7–830 行**。`index.html:6620` 的 `const RAW = {...}` 为 187571 字符的卡牌 JSON 数据，位于 CSS 区外；全文件扫描 `transition` / `animation` 字样时，CSS 区（7–830 行）之外 **0 行命中**，故该行不含任何过渡/动画声明。补充扫描中 `index.html:6620` 曾被 `float` 正则命中，系数据字段 `floating_body`，按 batch2 §17–18 的提醒判定为**数据文本、非动画代码**。

**脚本方法**（`node`，逐字符解析，规避超长行）：
1. 按 `\r?\n` 读入全文，仅取第 7–830 行构建「字符 + 原始行号」流；
2. 掩掉 `/* ... */` 注释与 `"..."` / `'...'` 字符串（替换为等长空格、保留换行，行号不漂移），并记录注释文本；
3. 状态机按 `{` / `}` / `;` 分块，括号内 `;` 不当分隔符（`(` `)` 深度保护）；`@media` / `@keyframes` 记为容器块，其余为规则块；每条规则记录：选择器、`{` 前行号、所在 `@media`、逐条声明（`属性: 值` + 行号）；
4. 属性名用正则 `^(-\w+-)?transition(-property|-duration|-timing-function|-delay)?$` 与 `^(-\w+-)?animation(-name|-duration|-timing-function|-delay|-iteration-count|-direction|-fill-mode|-play-state)?$` 匹配，**同时覆盖简写与长写**；
5. 简写按 CSS 语法按顶层逗号拆组、按空白分词：带 `s`/`ms` 单位的 token 依次为时长/延迟；`ease`/`linear`/`steps(...)`/`cubic-bezier(...)` 为缓动；`infinite` 或纯数字为迭代次数；`forwards`/`none` 为填充模式；其余首 token 为属性（transition）或动画名（animation）；
6. 交叉引用：每条 `animation` 的名字 ↔ 全部 `@keyframes` 定义；`@media (prefers-reduced-motion: reduce)` 内 `animation: none` 的选择器列表 ↔ 全部产生动画的声明，精确字符串比对得覆盖/遗漏；
7. 另对**全文件 9490 行**做补充扫描：长写属性、厂商前缀（`-webkit-` / `-moz-` / `-o-` / `-ms-`）、`transition: all` 简写、`@media`、`prefers-reduced-motion`、`@keyframes`、CSS 区外 `transition`/`animation` 字样、JS `style.transition`/`style.animation`/`setProperty`/WAAPI `.animate(`/`animationend`/`matchMedia`，以及 JS `classList` 触发动画类的行号。

**复核方式**：§1 统计总表每个数字均附「行号清单」或「脚本口径 + 0 命中结论」，可按行号回 `web/index.html` 逐行核对；§2–§4 每张表的行号列即原文位置。脚本为一次性工具，置于系统临时目录，**未写入项目**。

**分类口径**（静态、可复核，避免主观判断）：
- **装饰** = `iteration-count: infinite` 的持续循环（呼吸/脉动/闪烁），或纯氛围光效/背景渐变/hover 位移，不传达具体数值或事件确认；
- **反馈** = 一次性、由具体游戏事件触发（受击 / 禁用 / 状态变化 / 数值变化 / 出牌 / 新回合）；
- **覆盖声明** = `transition: none` / `animation: none` 这类禁用声明，本身不是动效，单列不归入两类。
- 每条动效的分类依据写在表末列，均指向注释行号、选择器或 JS 触发行号。

---

## 1. 统计总表

| 指标 | 数值 | 行号 / 选择器依据 | 复核方式 |
|---|---|---|---|
| `transition` 声明处数 | **11** | 25、52、151、202、254、382、402、413、490、491、500 | §2 表逐行回原文 |
| └ 展开的属性组数（简写逗号分组） | 16 | 52(3)、202(3)、382(2)、402(1)、490(1)、491(1)、500(2)、25(1)、151(1)、413(1) | 脚本按顶层逗号拆组求和 |
| └ 其中 `transition: none` 覆盖声明 | 1 | 254（`#hand .card.dragging`，原文 `transition: none !important;`） | 原文 |
| └ 产生过渡的声明 | 10 | 上列 11 行减去 254 | 11 − 1 |
| └ 长写 `transition-*` 属性 | 0 | 全文件扫描 0 行命中 | 补充脚本 |
| └ 厂商前缀 `-webkit-/-moz-/-o-/-ms-transition` | 0 | 全文件扫描 0 行命中 | 补充脚本 |
| └ `transition: all .2s` 式 `all` 简写 | 0 | 全文件扫描 0 行命中 | 补充脚本 |
| `animation` 声明处数 | **21** | 107、110、113、116、136、139、167、206、374、401、478、495、499、502、506、508、514、523、653、657、660 | §3 表逐行回原文 |
| └ 展开的动画组数 | 20 | 19 条产生动画的声明中，401 行为 2 组（`mblink` + `glowbreath`），其余 18 条各 1 组 | 脚本按顶层逗号拆组求和 |
| └ 其中 `animation: none` 覆盖声明 | 2 | 523（reduce 规则）、657（`body.perf-low` 降级） | 原文 |
| └ 产生动画的声明 | 19 | 上列 21 行减去 523、657 | 21 − 2 |
| └ 长写 `animation-*` 属性 | 0 | 全文件扫描 0 行命中 | 补充脚本 |
| └ 厂商前缀 `-webkit-/-moz-/-o-/-ms-animation` | 0 | 全文件扫描 0 行命中 | 补充脚本 |
| `@keyframes` 定义处数 | **18** | 108、111、114、117、137、140、170、207、375、404、406、479、497、503、505、507、516、661 | §4 表逐行回原文 |
| └ 唯一名字数 | 17 | `atkpulse` 在 479 与 503 各定义 1 次（重复 2 次），其余 16 名各 1 次 | 脚本对名字去重 |
| └ 被引用（无孤儿 keyframes） | 17 | §4「被谁引用」列，17 个唯一名全部有引用 | 脚本交叉引用，孤儿 0 处 |
| └ 引用了未定义名字（缺失） | 0 | 19 条产生动画的声明共 20 组，名字全部命中 §4 定义 | 脚本交叉引用，缺失 0 处 |
| `@media (prefers-reduced-motion: reduce)` 处数 | **1** | 519（全文件 `@media` 与 `prefers-reduced-motion` 均仅此 1 行命中） | 全文件扫描 |
| └ reduce 内规则条数 | 3 | 520–523（选择器组 + `animation: none !important`）、524（`transform: none`）、525（`transform: var(--fan)`） | 脚本按 `{` 分块 |
| └ reduce 的 `animation: none !important` 选择器数 | 12 | 520–523 行逗号列表，见 §5.1 | 脚本按顶层逗号拆分 |
| └ **reduce 覆盖数**（命中带动画声明的规则） | **10** | 110、113、116、139、206、401、506、508、514、660 | 脚本选择器精确比对 |
| └ reduce 无效覆盖（选择器无 `animation` 声明） | 2 | `#toast`（413 行为 `transition`）、`#phase-banner.show`（151/153 行为 `transition`） | 脚本比对 |
| └ reduce 内 `transition: none` | 0 | 519–526 行无该声明 | 脚本 |
| └ reduce 内 `transform` 覆盖选择器数 | 4 | 524 行 3 个 + 525 行 1 个 | 脚本按逗号拆分 |
| **遗漏数**：未被 reduce 覆盖的产生动画声明 | **9** | 107、136、167、374、478、495、499、502、653 | 19 − 10，见 §6.1 |
| └ 其中 `infinite` 无限循环 | 5 | 478、495、499、502、653 | 脚本解析 `iteration-count` |
| **遗漏数**：未被 `transition:none` 禁用的过渡声明 | **10** | 25、52、151、202、382、402、413、490、491、500 | reduce 内 `transition:none` 为 0，见 §6.2 |
| CSS 区外 `transition`/`animation` 声明 | 0 | 7–830 行之外全文件扫描 0 行命中 | 补充脚本 |
| JS `style.transition`/`style.animation`/`setProperty`/WAAPI `.animate(`/`animationend`/`transitionend`/`matchMedia` | 各 0 | 全文件扫描 0 行命中 | 补充脚本 |
| JS `classList` 触发动画类的静态命中行 | 33 | 见 §6.4（含 `world-dream`/`float`/`turnline.new` 等补扫行共 42 处） | 补充脚本，行号可复核 |

---

## 2. `transition` 声明清单（11 处 / 16 组）

> 「时长 / 缓动 / 延迟」列中，多组按 `/` 顺序与「属性」列一一对应；`0s（默认）` 表示简写未显式给出延迟，按 CSS 初值 `0s` 记；`ease（默认）` 表示未显式给出缓动，按 CSS 初值 `ease` 记。每格均填，不留空。

| # | 选择器 | 行号 | 简写原值（可复核） | 属性 | 时长 | 缓动 | 延迟 | 分类 | 用途 / 依据 |
|---|---|---|---|---|---|---|---|---|---|
| T1 | `body` | 25 | `transition: background-color .4s ease;` | `background-color` | `.4s` | `ease` | `0s（默认）` | 装饰 | 全局背景色渐变；`body` 规则 18–26 行，无专属注释；世界切换见 490/491 与 7126/8228 行 JS |
| T2 | `.classface` | 52 | `transition: transform .15s ease, border-color .15s ease, box-shadow .15s ease;` | `transform` / `border-color` / `box-shadow` | `.15s` / `.15s` / `.15s` | `ease` / `ease` / `ease` | `0s（默认）` ×3 | 装饰 | 选人职业卡 hover 上浮；56 行 `.classface:hover` 的 `transform: translateY(-4px)` |
| T3 | `#phase-banner` | 151 | `transition: opacity .3s;` | `opacity` | `.3s` | `ease（默认）` | `0s（默认）` | 反馈 | 阶段横幅淡入；153 行 `#phase-banner.show { opacity: 1; }`，7249/8188 行 JS 加 `.show` |
| T4 | `.card` | 202 | `transition: transform .15s ease, border-color .15s ease, box-shadow .15s ease;` | `transform` / `border-color` / `box-shadow` | `.15s` / `.15s` / `.15s` | `ease` / `ease` / `ease` | `0s（默认）` ×3 | 装饰 | 卡牌 hover 上浮；201 行注释「可出的卡：hover 上浮 4px」、203 行 `#flow-cards .card...:hover`、247 行 `#hand .card:hover` |
| T5 | `#hand .card.dragging` | 254 | `transition: none !important;` | 无（禁用覆盖） | 不适用（禁用） | 不适用（禁用） | 不适用（禁用） | 覆盖声明（非动效） | 拖拽态禁用过渡；254 行原文，`!important` 覆盖 202 行 `.card` 声明；归类为覆盖声明 |
| T6 | `.relicrow .relic` | 382 | `transition: transform .15s ease, border-color .15s ease;` | `transform` / `border-color` | `.15s` / `.15s` | `ease` / `ease` | `0s（默认）` ×2 | 装饰 | 遗物 hover 上浮；383 行 `.relicrow .relic:hover` |
| T7 | `.mnode.pickable` | 402 | `transition: transform .15s ease;` | `transform` | `.15s` | `ease` | `0s（默认）` | 装饰 | 地图可走节点 hover 上浮；403 行 `.mnode.pickable:hover` |
| T8 | `#toast` | 413 | `transition: opacity .2s;` | `opacity` | `.2s` | `ease（默认）` | `0s（默认）` | 反馈 | 提示条淡入；415 行 `#toast.show { opacity: 1; }`，7837 行 JS 加 `.show` |
| T9 | `#screen-combat.world-dream` | 490 | `transition: background .4s ease;` | `background` | `.4s` | `ease` | `0s（默认）` | 装饰 | 梦境世界背景渐变；489 行注释「苍民双世界：醒（冷灰蓝）/ 梦（暗红脉动）」；7126/8228 行 JS 切换 `world-dream` |
| T10 | `#screen-combat.world-wake` | 491 | `transition: background .4s ease;` | `background` | `.4s` | `ease` | `0s（默认）` | 装饰 | 清醒世界背景渐变；489 行注释；7127/8229/8240 行 JS 切换 `world-wake` |
| T11 | `.enemy` | 500 | `transition: opacity .4s ease, filter .4s ease;` | `opacity` / `filter` | `.4s` / `.4s` | `ease` / `ease` | `0s（默认）` ×2 | 反馈 | 敌人死亡变淡变灰；131 行 `.enemy.dead`、501 行 `.enemy.dead { opacity: .25; }` |

**长写 / 简写变体核查**：全文件 `transition-property` / `transition-duration` / `transition-timing-function` / `transition-delay` 命中 **0** 处；`-webkit-` 等厂商前缀命中 **0** 处；`transition: all ...` 命中 **0** 处。上表 11 处均为 `transition` 简写（含 1 处 `none` 覆盖）。

---

## 3. `animation` 声明清单（21 处 / 20 组）

> 「迭代」列中 `1（默认）` 表示简写未显式给出 `animation-iteration-count`、按初值 1 记；`0s（默认）` 表示未显式给出延迟。A18、A20 为 `animation: none` 覆盖声明，本身不产生动画，各列均按「覆盖声明」填满。

| # | 选择器 | 行号 | `animation` 原值（可复核） | keyframes 名 | 时长 | 缓动 | 迭代 | 分类 | 用途 / 触发依据 | reduce 状态 |
|---|---|---|---|---|---|---|---|---|---|---|
| A1 | `#hud #gaze-val.flash` | 107 | `gazeblink .4s steps(2) 2` | `gazeblink` | `.4s` | `steps(2)` | `2` | 反馈 | 凝视值上升闪烁；108 行 keyframes 改 `color`；8087 行 JS `gz.classList.add('flash')`（`run.gaze > prev.gaze` 时） | **遗漏**（不在 520–523 选择器列表） |
| A2 | `#hud-block-wrap .ic.block.pulse` | 110 | `blockpulse .4s ease` | `blockpulse` | `.4s` | `ease` | `1（默认）` | 反馈 | 获得格挡脉冲；109 行注释「获得格挡：盾形符号脉冲（T37）」；8046 行 JS 移除后重加 `.pulse` 重触发 | 已覆盖（523 行列表第 9 项） |
| A3 | `#pile-draw.pulse` | 113 | `pilepulse .4s ease` | `pilepulse` | `.4s` | `ease` | `1（默认）` | 反馈 | 牌堆洗回数字重置；112 行注释「牌堆洗回：抽牌堆数字重置动画（T37）」；8248 行 JS 重触发 `.pulse` | 已覆盖（523 行列表第 10 项） |
| A4 | `#log div.turnline.new` | 116 | `turnflash .6s ease` | `turnflash` | `.6s` | `ease` | `1（默认）` | 反馈 | 新回合行提示；115 行注释「新回合行：600ms 提示（T37 时序表）」；8262 行 JS 在 `li === lastLine` 时拼 `' new'` 类 | 已覆盖（523 行列表第 11 项） |
| A5 | `.enemy .intent.flash` | 136 | `intentblink .2s ease` | `intentblink` | `.2s` | `ease` | `1（默认）` | 反馈 | 敌人意图刷新闪烁；137 行 keyframes 由 `opacity:0` 到 `1`；8142 行 JS 意图变化时加 `.flash` | **遗漏**（不在 520–523 选择器列表） |
| A6 | `.enemy.hitflash` | 139 | `ehit .12s ease` | `ehit` | `.12s` | `ease` | `1（默认）` | 反馈 | 敌人受击闪红；138 行注释「敌人受击：120ms 闪红」；8166 行 JS 加 `.hitflash`、8168 行 130ms 后移除 | 已覆盖（523 行列表第 12 项） |
| A7 | `.float` | 167 | `floatup .4s ease-out forwards` | `floatup` | `.4s` | `ease-out` | `1（默认）` | 反馈 | 伤害/治疗数字上浮消失；170 行 keyframes `translate(-50%,-34px); opacity:0`；7984 行（治疗）、8169 行（伤害）JS 创建 `.float` | **遗漏**（不在 520–523 选择器列表） |
| A8 | `.card.shakeit` | 206 | `shakeit .3s ease` | `shakeit` | `.3s` | `ease` | `1（默认）` | 反馈 | 卡牌不可用/费用不足抖动；207 行 keyframes `translateX(±4px)`；8270 行 JS 移除后重加 `.shakeit`、8271 行 320ms 后移除 | 已覆盖（523 行列表第 8 项） |
| A9 | `body.eggflash #app` | 374 | `eggflash .4s ease` | `eggflash` | `.4s` | `ease` | `1（默认）` | 装饰 | 彩蛋金色微闪（一次性、纯氛围、无数值语义）；373 行注释「彩蛋触发的微闪：金色，与共振闪红区分」；7254 行 JS 加 `eggflash`、7255 行 450ms 后移除 | **遗漏**（不在 520–523 选择器列表） |
| A10-1 | `.mnode.pickable`（第 1 组） | 401 | `mblink 1s steps(2) infinite` | `mblink` | `1s` | `steps(2)` | `infinite` | 装饰 | 地图可走节点边框闪烁；404 行 keyframes 改 `border-color`；6827 行 JS 加 `.pickable` | 已覆盖（523 行列表第 4 项 `.mnode.pickable`） |
| A10-2 | `.mnode.pickable`（第 2 组） | 401 | `glowbreath 2s ease-in-out infinite` | `glowbreath` | `2s` | `ease-in-out` | `infinite` | 装饰 | 可走节点外层光晕呼吸；405 行注释「可走节点的外层光晕呼吸（T37：一眼能分辨能点）」、406 行 keyframes | 已覆盖（523 行列表第 4 项 `.mnode.pickable`） |
| A11 | `.intent.atk-hot` | 478 | `atkpulse 1.4s ease-in-out infinite` | `atkpulse` | `1.4s` | `ease-in-out` | `infinite` | 装饰 | 敌人高攻意图持续脉动；477 行注释「反馈：受击震屏、出牌飞出」（该段注释）；8139 行 JS 攻击意图时加 `.atk-hot` | **遗漏**（不在 520–523 选择器列表） |
| A12 | `#screen-combat.world-dream::before` | 495 | `dreampulse 2s ease-in-out infinite` | `dreampulse` | `2s` | `ease-in-out` | `infinite` | 装饰 | 梦境世界暗红脉动光晕；489 行注释「梦（暗红脉动）」、497 行 keyframes；7126/8228 行 JS 切换 `world-dream` | **遗漏**（不在 520–523 选择器列表） |
| A13 | `.v.clarity-low` | 499 | `atkpulse 1.2s ease-in-out infinite` | `atkpulse` | `1.2s` | `ease-in-out` | `infinite` | 装饰 | 清醒度过低数值持续脉动；6802/8070 行 JS `classList.toggle('clarity-low', ... < 3)` | **遗漏**（不在 520–523 选择器列表） |
| A14 | `.intent.atk-hot` | 502 | `atkpulse 1.4s ease-in-out infinite` | `atkpulse` | `1.4s` | `ease-in-out` | `infinite` | 装饰 | 与 478 行**重复声明**（相同选择器、相同值）；479/503 行 `@keyframes atkpulse` 亦重复定义，见 §8 | **遗漏**（不在 520–523 选择器列表） |
| A15 | `body.shake #app` | 506 | `shake .22s linear 1` | `shake` | `.22s` | `linear` | `1` | 反馈 | 受击震屏；477 行注释「反馈：受击震屏、出牌飞出」、505 行 keyframes `translateX(±7px)`；8038 行 JS 加 `shake`、8036 行先移除 | 已覆盖（523 行列表第 1 项） |
| A16 | `.card.ghost-fly` | 508 | `cardfly .22s ease-in forwards` | `cardfly` | `.22s` | `ease-in` | `1（默认）` | 反馈 | 出牌飞出；477 行注释「反馈：受击震屏、出牌飞出」、507 行 keyframes；7964 行 JS 加 `.ghost-fly` | 已覆盖（523 行列表第 2 项） |
| A17 | `body.dying #app::after` | 514 | `dyingpulse 1.6s ease-in-out infinite` | `dyingpulse` | `1.6s` | `ease-in-out` | `infinite` | 装饰 | 濒血屏幕边缘红光渗入（持续氛围）；510 行注释「濒血：红光从屏幕边缘往里渗」；8034 行 JS `toggle('dying', hp <= maxHp*0.3)` | 已覆盖（523 行列表第 3 项） |
| A18 | 12 个选择器组（520–523） | 523 | `animation: none !important` | 无（禁用覆盖） | 不适用（禁用） | 不适用（禁用） | 不适用（禁用） | 覆盖声明（非动效） | 该声明即 reduce 规则本体，见 §5.1；含 `!important` | 自身为 reduce 规则（不计入覆盖数） |
| A19 | `body.perf-low .mnode.pickable` | 653 | `mblink 1s steps(2) infinite` | `mblink` | `1s` | `steps(2)` | `infinite` | 装饰 | 性能降级后仅保留节点边框闪烁（去掉 `glowbreath` 光晕）；652 行注释「帧耗时超标自动降级：关光晕和上浮，只留颜色变化（T37 性能保护）」；8022 行 JS 加 `perf-low` | **遗漏**（选择器不在 520–523 列表；且仅在 `body.perf-low` 时生效） |
| A20 | 3 个 `body.perf-low` 选择器（656–657） | 657 | `animation: none` | 无（禁用覆盖） | 不适用（禁用） | 不适用（禁用） | 不适用（禁用） | 覆盖声明（非动效） | `body.perf-low` 下禁用 `.card.shakeit` / `.ic.block.pulse` / `#pile-draw.pulse`；652 行注释 | 自身为 perf-low 降级（不计入覆盖数） |
| A21 | `body.resflash #app` | 660 | `resflash .5s steps(2) 2` | `resflash` | `.5s` | `steps(2)` | `2` | 反馈 | 共振阈值屏幕边框闪红；659 行注释「共振阈值：屏幕边框闪红」、661 行 keyframes；7980 行 JS 加 `resflash`、7981 行 1100ms 后移除 | 已覆盖（523 行列表第 6 项） |

**长写 / 前缀核查**：全文件 `animation-name` / `animation-duration` / `animation-timing-function` / `animation-delay` / `animation-iteration-count` / `animation-direction` / `animation-fill-mode` / `animation-play-state` 命中 **0** 处；`-webkit-` 等厂商前缀命中 **0** 处。上表 21 处均为 `animation` 简写（含 2 处 `none` 覆盖）。

---

## 4. `@keyframes` 清单（18 处定义 / 17 个唯一名）

> 「被谁引用」列格式为 `选择器@行号`，来自 §3 的 `animation` 声明交叉引用；「分类」按引用它的动效口径填。

| # | 名字 | 定义行 | 关键帧内容（原文） | 被谁引用（选择器@行号） | 分类 | 备注 |
|---|---|---|---|---|---|---|
| K1 | `gazeblink` | 108 | `50% { color: var(--red-hi); }` | `#hud #gaze-val.flash@107` | 反馈 | 唯一定义，1 处引用 |
| K2 | `blockpulse` | 111 | `50% { transform: scale(1.5); }` | `#hud-block-wrap .ic.block.pulse@110` | 反馈 | 唯一定义，1 处引用 |
| K3 | `pilepulse` | 114 | `50% { transform: scale(1.3); color: var(--red-hi); }` | `#pile-draw.pulse@113` | 反馈 | 唯一定义，1 处引用 |
| K4 | `turnflash` | 117 | `0% { color: var(--red-hi); opacity: 0; }` | `#log div.turnline.new@116` | 反馈 | 唯一定义，1 处引用 |
| K5 | `intentblink` | 137 | `from { opacity: 0; } to { opacity: 1; }` | `.enemy .intent.flash@136` | 反馈 | 唯一定义，1 处引用 |
| K6 | `ehit` | 140 | `40% { border-color: var(--red-hi); background: #2a0d0e; }` | `.enemy.hitflash@139` | 反馈 | 唯一定义，1 处引用 |
| K7 | `floatup` | 170 | `to { transform: translate(-50%, -34px); opacity: 0; }` | `.float@167` | 反馈 | 唯一定义，1 处引用 |
| K8 | `shakeit` | 207 | `25% { transform: translateX(-4px); } 75% { transform: translateX(4px); }` | `.card.shakeit@206` | 反馈 | 唯一定义，1 处引用 |
| K9 | `eggflash` | 375 | `30% { box-shadow: inset 0 0 60px rgba(201, 163, 90, .4); }` | `body.eggflash #app@374` | 装饰 | 唯一定义，1 处引用 |
| K10 | `mblink` | 404 | `50% { border-color: var(--red); }` | `.mnode.pickable@401`、`body.perf-low .mnode.pickable@653` | 装饰 | 唯一定义，2 处引用（401 组 1、653） |
| K11 | `glowbreath` | 406 | `0%,100% { box-shadow: 0 0 0 rgba(200,60,60,0); } 50% { box-shadow: 0 0 16px rgba(200,60,60,.55); }` | `.mnode.pickable@401`（第 2 组） | 装饰 | 唯一定义，1 处引用 |
| K12 | `atkpulse` | 479 | `50% { border-color: var(--red-hi); color: var(--red-hi); }` | `.intent.atk-hot@478`、`.v.clarity-low@499`、`.intent.atk-hot@502` | 装饰 | **重复定义**：479 与 503 行各 1 次，内容相同；3 处引用 |
| K13 | `dreampulse` | 497 | `50% { box-shadow: inset 0 0 40px rgba(150, 25, 30, .18); }` | `#screen-combat.world-dream::before@495` | 装饰 | 唯一定义，1 处引用 |
| K14 | `atkpulse` | 503 | `50% { border-color: var(--red-hi); color: var(--red-hi); }` | `.intent.atk-hot@478`、`.v.clarity-low@499`、`.intent.atk-hot@502` | 装饰 | **重复定义**（与 479 行同名同内容），运行时后定义覆盖前定义，见 §8 |
| K15 | `shake` | 505 | `25% { transform: translateX(-7px); } 75% { transform: translateX(7px); }` | `body.shake #app@506` | 反馈 | 唯一定义，1 处引用 |
| K16 | `cardfly` | 507 | `to { transform: translateY(-80px) scale(.65) rotate(6deg); opacity: 0; }` | `.card.ghost-fly@508` | 反馈 | 唯一定义，1 处引用 |
| K17 | `dyingpulse` | 516 | `50% { box-shadow: inset 0 0 60px rgba(160, 20, 25, .3); }` | `body.dying #app::after@514` | 装饰 | 唯一定义，1 处引用 |
| K18 | `resflash` | 661 | `50% { box-shadow: inset 0 0 40px var(--red); }` | `body.resflash #app@660` | 反馈 | 唯一定义，1 处引用 |

**交叉引用结论**：17 个唯一名全部被引用（孤儿 **0** 个）；20 组 `animation` 引用的名字全部有定义（缺失 **0** 个）；`@-webkit-keyframes` 等前缀形式 **0** 处。

---

## 5. `@media (prefers-reduced-motion: reduce)` 规则（全文件唯一 1 处，519–526 行）

原文（按行）：

```
519  @media (prefers-reduced-motion: reduce) {
520    body.shake #app, .card.ghost-fly, body.dying #app::after,
521    .mnode.pickable, #toast, body.resflash #app, #phase-banner.show,
522    .card.shakeit, #hud-block-wrap .ic.block.pulse, #pile-draw.pulse,
523    #log div.turnline.new, .enemy.hitflash { animation: none !important; }
524    #flow-cards .card:not(.dimmed):hover, .mnode.pickable:hover, .relicrow .relic:hover { transform: none; }
525    #hand .card:hover:not(.dimmed):not(.dragging) { transform: var(--fan); }
526  }
```

注释在 518 行：「尊重系统「减少动态效果」设置」。全文件 `@media` 仅此 1 处（519 行），`prefers-reduced-motion` 仅此 1 处（519 行）。

### 5.1 `animation: none !important` 的 12 个选择器（520–523 行）

| # | 选择器（按列表顺序） | 是否命中带 `animation` 声明的规则 | 命中的声明行 | reduce 对该选择器的处置 | 备注 |
|---|---|---|---|---|---|
| 1 | `body.shake #app` | 命中 | 506（A15 `shake`） | `animation: none !important` 禁用 | 已覆盖 |
| 2 | `.card.ghost-fly` | 命中 | 508（A16 `cardfly`） | `animation: none !important` 禁用 | 已覆盖 |
| 3 | `body.dying #app::after` | 命中 | 514（A17 `dyingpulse`） | `animation: none !important` 禁用 | 已覆盖 |
| 4 | `.mnode.pickable` | 命中 | 401（A10 两组 `mblink` + `glowbreath`） | `animation: none !important` 禁用 | 已覆盖；1 条声明含 2 组动画 |
| 5 | `#toast` | **未命中**（该选择器无 `animation` 声明） | 无（413 行是 `transition: opacity .2s`） | `animation: none !important` 落在无动画元素上 | 无效覆盖；其 `opacity` 过渡未被禁用，见 §6.2 |
| 6 | `body.resflash #app` | 命中 | 660（A21 `resflash`） | `animation: none !important` 禁用 | 已覆盖 |
| 7 | `#phase-banner.show` | **未命中**（该选择器无 `animation` 声明） | 无（151 行 `#phase-banner` 是 `transition: opacity .3s`；153 行 `.show` 只改 `opacity`） | `animation: none !important` 落在无动画元素上 | 无效覆盖；其 `opacity` 过渡未被禁用，见 §6.2 |
| 8 | `.card.shakeit` | 命中 | 206（A8 `shakeit`） | `animation: none !important` 禁用 | 已覆盖 |
| 9 | `#hud-block-wrap .ic.block.pulse` | 命中 | 110（A2 `blockpulse`） | `animation: none !important` 禁用 | 已覆盖 |
| 10 | `#pile-draw.pulse` | 命中 | 113（A3 `pilepulse`） | `animation: none !important` 禁用 | 已覆盖 |
| 11 | `#log div.turnline.new` | 命中 | 116（A4 `turnflash`） | `animation: none !important` 禁用 | 已覆盖 |
| 12 | `.enemy.hitflash` | 命中 | 139（A6 `ehit`） | `animation: none !important` 禁用 | 已覆盖 |

**覆盖数 = 10**（命中项 1、2、3、4、6、8、9、10、11、12；对应声明行 110、113、116、139、206、401、506、508、514、660）。**无效覆盖 = 2**（项 5 `#toast`、项 7 `#phase-banner.show`）。12 − 2 = 10，与脚本一致。

### 5.2 reduce 内 `transform` 覆盖（524–525 行）

| 行 | 选择器 | 声明 | 作用 | 是否覆盖全部 transform 位移 |
|---|---|---|---|---|
| 524 | `#flow-cards .card:not(.dimmed):hover` | `transform: none` | 抵消 203 行卡牌 hover 上浮 | 仅覆盖该 1 个 hover 选择器 |
| 524 | `.mnode.pickable:hover` | `transform: none` | 抵消 403 行地图节点 hover 上浮 | 仅覆盖该 1 个 hover 选择器 |
| 524 | `.relicrow .relic:hover` | `transform: none` | 抵消 383 行遗物 hover 上浮 | 仅覆盖该 1 个 hover 选择器 |
| 525 | `#hand .card:hover:not(.dimmed):not(.dragging)` | `transform: var(--fan)` | 把 247 行手牌 hover 重置回扇形原位 | 仅覆盖该 1 个 hover 选择器 |

未列入的 transform 位移：`.classface:hover`（56 行 `translateY(-4px)`，依赖 52 行 `transition`）、`#hand .card.selected`（250–251 行上浮，依赖 202 行 `transition`）。二者在 reduce 下未被 `transform` 覆盖，见 §6.2。

### 5.3 reduce 内 `transition` 处置

reduce（519–526 行）内 **`transition: none` 命中 0 处**，也没有针对任何 `transition` 声明的 `transition-property: none` 或 `transition-duration: 0s`。对 `transition` 的唯一间接处置是 524/525 行把 4 个 hover 的 `transform` 终值改掉，使 52/202/382/402 行的 `transform` 过渡不再产生位移变化；但 `border-color` / `box-shadow` / `background-color` / `background` / `opacity` / `filter` 这些过渡的终值变化未受影响。

---

## 6. 遗漏清单（独立节）

### 6.1 未被 reduce 覆盖的 `animation` 声明（9 条）

> 判定口径：产生动画的 19 条声明（§3）减去 reduce 精确命中的 10 条（§5.1）。选择器字符串与 520–523 行列表逐项比对，无一项命中者即遗漏。

| # | 选择器 | 行号 | 动画名 | 迭代 | 分类 | JS 触发点（静态行号） | 对晕动症用户的影响（按声明属性推断） |
|---|---|---|---|---|---|---|---|
| M1 | `#hud #gaze-val.flash` | 107 | `gazeblink` | `2`（有限） | 反馈 | 8087（凝视上升加 `.flash`） | `steps(2)` 两次颜色突变；reduce 未禁用，系统设为减少动效时仍会闪 2 次 |
| M2 | `.enemy .intent.flash` | 136 | `intentblink` | `1（默认）` | 反馈 | 8142（意图变化加 `.flash`） | `opacity` 0→1 的亮度突变；战斗每次意图刷新触发，reduce 未禁用 |
| M3 | `.float` | 167 | `floatup` | `1（默认）` | 反馈 | 7984（治疗）、8169（伤害） | `translate(-50%,-34px)` 位移 + `opacity` 淡出，属任务书点名的「漂浮」类；每次伤害/治疗出现，reduce 未禁用 |
| M4 | `body.eggflash #app` | 374 | `eggflash` | `1（默认）` | 装饰 | 7254（加 `eggflash`）、7255（450ms 移除） | 全屏 `box-shadow` 内发光突变；一次性但覆盖整个 `#app`，reduce 未禁用 |
| M5 | `.intent.atk-hot` | 478 | `atkpulse` | **`infinite`** | 装饰 | 8139（攻击意图加 `.atk-hot`） | **1.4s 周期的 `border-color`/`color` 持续脉动**；敌人进入攻击意图后一直循环，reduce 未禁用 |
| M6 | `#screen-combat.world-dream::before` | 495 | `dreampulse` | **`infinite`** | 装饰 | 7126、8228（切换 `world-dream`）、8239/8240（切回） | **2s 周期的全屏内阴影呼吸**；苍民梦境世界期间持续循环，reduce 未禁用 |
| M7 | `.v.clarity-low` | 499 | `atkpulse` | **`infinite`** | 装饰 | 6802、8070（`clarity < 3` 时 toggle） | **1.2s 周期的数值颜色脉动**；清醒度低期间持续循环，reduce 未禁用 |
| M8 | `.intent.atk-hot` | 502 | `atkpulse` | **`infinite`** | 装饰 | 8139（同 M5） | 与 478 行重复声明（相同选择器、值），运行时后者生效；同为 1.4s 无限脉动，reduce 未禁用 |
| M9 | `body.perf-low .mnode.pickable` | 653 | `mblink` | **`infinite`** | 装饰 | 8022（`slow >= 3` 加 `perf-low`）、6827（加 `.pickable`） | **1s `steps(2)` 无限闪烁**；仅在 `body.perf-low` 时生效，且该选择器不在 reduce 列表；若用户同时命中 reduce 与 perf-low，闪烁仍播放 |

**按迭代类型**：9 条中 **`infinite` 无限循环 5 条**（478、495、499、502、653），有限次 4 条（107、136、167、374）。5 条无限循环是持续、不可自行停止的周期性视觉变化，是本节影响最重的一类。

**按分类**：装饰 5 条（374、478、495、499、502）+ 1 条（653）= 装饰 6 条；反馈 3 条（107、136、167）。合计 9 条。

### 6.2 未被 reduce 禁用的 `transition` 声明（10 条）

reduce 内 `transition: none` 为 0 处（§5.3），因此 10 条产生过渡的声明全部**未被禁用**：

| 选择器 | 行号 | 过渡属性 | reduce 是否处置 | 说明 |
|---|---|---|---|---|
| `body` | 25 | `background-color .4s` | 未处置 | 背景色渐变保留 |
| `.classface` | 52 | `transform` / `border-color` / `box-shadow .15s` | 部分 | `transform` 的 hover 位移（56 行 `.classface:hover`）**未**列入 524 行覆盖列表，仍上浮 |
| `#phase-banner` | 151 | `opacity .3s` | 未处置 | 523 行列的是 `#phase-banner.show` 且只给 `animation:none`；`opacity` 淡入保留 |
| `.card` | 202 | `transform` / `border-color` / `box-shadow .15s` | 部分 | 524 行只抵消 `#flow-cards .card...:hover`、525 行只重置 `#hand .card:hover`；`.card.selected`（250–251 行）上浮未列，`border-color`/`box-shadow` 过渡未处置 |
| `.relicrow .relic` | 382 | `transform` / `border-color .15s` | 部分 | 524 行抵消 `:hover` 位移；`border-color` 过渡未处置 |
| `.mnode.pickable` | 402 | `transform .15s` | 部分 | 524 行抵消 `:hover` 位移；仅此 1 个 hover 选择器被覆盖 |
| `#toast` | 413 | `opacity .2s` | 未处置 | 523 行 `#toast` 的 `animation:none` 是无效覆盖；`opacity` 淡入保留 |
| `#screen-combat.world-dream` | 490 | `background .4s` | 未处置 | 世界切换背景渐变保留 |
| `#screen-combat.world-wake` | 491 | `background .4s` | 未处置 | 世界切换背景渐变保留 |
| `.enemy` | 500 | `opacity` / `filter .4s` | 未处置 | 敌人死亡变淡变灰保留 |

补充说明：524 行 `transform: none` 覆盖 3 个 hover 选择器、525 行覆盖 1 个（共 4 个，§5.2），抵消了 202/382/402 行 `transform` 过渡在这些 hover 态的位移变化；但这 3 条 `transition` 声明本身仍在，且未列入覆盖的 transform 位移（56 行 `.classface:hover`、250–251 行 `#hand .card.selected`）继续依赖 52/202 行过渡生效。

### 6.3 对晕动症用户的影响（按 CSS 声明静态推断）

1. **唯一的系统级开关不完整**：全文件只有 519 行 1 处 `prefers-reduced-motion`，其 `animation: none !important` 只覆盖 10 条带动画声明的规则（19 条中的 10 条），遗漏 9 条；`transition` 侧一处 `transition: none` 都没有。
2. **持续循环动画无法关闭**：5 条 `infinite` 遗漏（478/495/499/502/653）分别是攻击意图脉动、梦境全屏呼吸、低清醒度数值脉动、降级节点闪烁，周期 1s–2s，满足条件后持续播放，reduce 不生效。按 WCAG 2.3.3 / 减动效惯例，持续周期性运动与大面积光晕是对前庭敏感用户风险最高的一类；此处结论按 `iteration-count: infinite` 与 `box-shadow`/`border-color` 关键帧内容静态判定，未开浏览器实测。
3. **全屏大面积光效**：A12 `dreampulse`（495 行 `#screen-combat.world-dream::before` 覆盖 `inset:0`）、A9 `eggflash`（374 行 `#app` 内阴影）、A17 `dyingpulse`（514 行）作用范围是整个战斗屏；其中 495、374 未被 reduce 覆盖。
4. **位移类动效**：A7 `floatup`（167 行 `translate(-50%,-34px)`）每次伤害/治疗出现，未被 reduce 覆盖；A15 `shake`、A16 `cardfly` 已被覆盖，但 `.classface:hover`（56 行）与 `#hand .card.selected`（250–251 行）的位移过渡仍生效。
5. **JS 侧无兜底**：全文件 `matchMedia` / `prefersReduced` / `reducedMotion` 命中 **0** 处，JS 不会因系统减动效设置而跳过类切换；reduce 之外没有第二条降级路径。`body.perf-low`（652–657 行）是**帧耗时降级**，不是动效偏好降级，且它本身还保留 1 条 `infinite` 闪烁（653 行）。

### 6.4 JS 触发点（静态扫描，非 CSS 声明，仅作复核线索）

补充脚本在 833–9489 行命中 `classList` 切换动画类 33 行，另有 `world-dream`/`float`/`turnline.new` 补扫行；以下列出与 §3 各动画可对应的触发行号（均为静态命中，**运行时时序未验证**）：

| 动画 / 状态 | JS 触发行号 |
|---|---|
| `clarity-low`（A13） | 6802、8070 |
| `.pickable`（A10/A19） | 6827 |
| `world-dream` / `world-wake`（A12、T9/T10） | 7126、7127、8228、8229、8239、8240 |
| `.show` → `#phase-banner`（T3）、`#toast`（T8） | 7249、7251、7837、7839、8188、8190 |
| `eggflash`（A9） | 7252、7254、7255 |
| `.ghost-fly`（A16） | 7964 |
| `resflash`（A21） | 7980、7981 |
| `perf-low`（A19、A20） | 8022 |
| `dying`（A17） | 8034 |
| `shake`（A15） | 8036、8038 |
| `.pulse`（A2/A3） | 8046、8047、8248 |
| `.flash` 凝视（A1） | 8087 |
| `.atk-hot` / 意图 `.flash`（A11/A14/A5） | 8139、8142 |
| `.hitflash`（A6） | 8166、8168 |
| `.float`（A7） | 7984、8169 |
| `turnline` + `' new'`（A4） | 8261、8262 |
| `.shakeit`（A8） | 8270、8271 |

**未验证**：`.new` 类的显式添加行未在本次扫描中单独定位，8261–8262 行是在 `el()` 创建时按 `li === lastLine` 条件把 `' new'` 拼进类名字符串（`index.html:8262`），运行时是否触发 `turnflash` 未跑浏览器确认。

---

## 7. 装饰 / 反馈 分类汇总

| 类别 | animation 声明（19 条产生动画的） | transition 声明（11 条中） | 依据 |
|---|---|---|---|
| 装饰（呼吸 / 闪烁 / 漂浮 / 氛围 / hover 位移 / 背景渐变） | 8 条：374、401（2 组）、478、495、499、502、514、653 | 7 条：25、52、202、382、402、490、491 | `infinite` 循环、`box-shadow`/`border-color` 光效、489 行「梦（暗红脉动）」、405 行「光晕呼吸」、510 行「濒血」等注释；hover 位移与背景渐变 |
| 反馈（受击 / 禁用 / 状态变化 / 数值变化 / 出牌 / 新回合） | 11 条：107、110、113、116、136、139、167、206、506、508、660 | 3 条：151、413、500 | 109「获得格挡」、112「牌堆洗回」、115「新回合行」、138「敌人受击」、477「受击震屏、出牌飞出」、659「共振阈值」等注释；`opacity` 出现/消失、`filter` 死亡变灰 |
| 覆盖声明（非动效） | 2 条：523、657 | 1 条：254 | `animation: none` / `transition: none !important`，按口径单列 |

校验：animation 8 + 11 + 2 = 21（与 §1「21 处」一致，其中 2 条为 none 覆盖不计入 19 条产生动画）；transition 7 + 3 + 1 = 11（与 §1「11 处」一致）。分类口径见 §0。

---

## 8. 「代码有、运行时不保证」清单

| # | 位置 | 现象 | 标注 |
|---|---|---|---|
| 1 | 478 与 502 行 | `.intent.atk-hot` 同一选择器、同一 `animation: atkpulse 1.4s ease-in-out infinite` 重复声明 2 次 | 代码有 2 条，运行时后声明覆盖前声明；因值相同，视觉结果一致但计数为 2 条 |
| 2 | 479 与 503 行 | `@keyframes atkpulse` 同名同内容重复定义 2 次 | 代码有 2 个定义，运行时后定义覆盖前定义；§1「18 处定义 / 17 个唯一名」即由此而来 |
| 3 | 401 与 653 行 | `body.perf-low .mnode.pickable`（653）优先级高于 `.mnode.pickable`（401），把 `mblink + glowbreath` 覆盖为仅 `mblink` | 运行时取决于 `body.perf-low` 类是否存在（8022 行按帧耗时添加）；未跑游戏，条件是否命中未验证 |
| 4 | 523 行 reduce 列表项 5、7 | `#toast`、`#phase-banner.show` 被 `animation: none !important` 覆盖，但二者无 `animation` 声明 | 无效覆盖；这两个元素的 `opacity` 过渡（413、151 行）未被 `transition: none` 禁用，reduce 对它们的抑制「代码有、运行时不保证」 |
| 5 | 524 行 `transform` 覆盖 | 只覆盖 3 个 hover 选择器，未覆盖 `.classface:hover`（56 行）、`#hand .card.selected`（250–251 行） | reduce 对 transform 位移的抑制不是全集，未列入者仍按 52/202 行过渡生效 |
| 6 | 519 行 `@media` 优先级 | reduce 规则带 `!important`，但 A18（523 行）与 A20（657 行 `animation: none` 无 `!important`）、A5/T5（254 行 `!important`）分属不同触发条件 | 最终生效集合按 CSS 优先级与 DOM 类状态决定；本次仅静态比对选择器，未验证浏览器匹配结果 |

---

## 9. 边界声明

- **没开浏览器**：本文所有结论均为按 `web/index.html` 第 7–830 行 CSS 源码的**静态清点**（逐字符解析 + 全文件正则补充扫描），不是实际渲染结果，也不是运行时动画播放结果。
- **数字可复核**：§1 每个统计数字附行号清单或「脚本口径 + 0 命中结论」；§2–§4 表格行号列即原文位置；简写的属性/时长/缓动/延迟/迭代为按 CSS 简写语法静态拆解（原文值同时列出），未显式给出的项按 CSS 初值标注「默认」。
- **CSS 优先级打架**：凡重复声明、重复 `@keyframes`、条件覆盖（§8）均标「代码有、运行时不保证」——代码里存在该声明，但运行时是否生效、哪条生效取决于浏览器优先级计算与 DOM 类状态，本次未验证。
- **未验证项**（按要求逐条写明原因）：
  - 未验证：`prefers-reduced-motion: reduce` 在真实浏览器中是否匹配、以及 523 行 `!important` 相对其它声明的最终生效结果 —— 原因：无浏览器，仅做静态选择器比对。
  - 未验证：JS `classList` 切换的运行时时序、触发频率与动画实际播放次数 —— 原因：仅静态定位到行号（§6.4），未跑游戏。
  - 未验证：§8 各优先级冲突的最终生效集合 —— 原因：同上，未跑浏览器。
  - 未验证：6620 行 `const RAW`（187571 字符卡牌 JSON）逐字段内容 —— 原因：该行是数据不是代码；全文件 `transition`/`animation` 字样在 CSS 区（7–830 行）外 0 行命中，故判定其不含过渡/动画声明，未逐字段解析数据。
  - 未验证：`.new` 类的显式 `classList.add` 行 —— 原因：扫描仅在 8262 行定位到 `el()` 创建时拼接 `' new'` 字符串，未定位到独立 add 调用。
- **只读**：本次未修改 `web/index.html`、`engine/`、`cards/*.json` 或任何现有文件；项目内仅新建本文件 `docs/design/ui/x3_motion.md`；按本次任务指令未写 `_HY4_PROGRESS.md`。
