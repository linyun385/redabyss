# X5 · 浮层层级清点

> 对象：`web/index.html`（`node` 按行读，共 9490 行；`<style>` 区段 6–831 行，CSS 规则 7–830 行）
> 基准：`docs/UI.md` §1「层级（z-index）表」（22–37 行）
> 方法：`node -e` 按行扫描全文，匹配 `z-?index`（含 `zIndex`）、`position:(fixed|absolute|sticky)`、
> `classList.add/remove/toggle`、`style.zIndex`、`style.display`、浮层 id 字面量。
> 6620 行为超长数据行 `const RAW = {...}`，长度 187571 字符，实测**不含** `z-index`，不参与本清点。
> 本文所有行号均指 `web/index.html`；`docs/UI.md` 的行号单独标注为 `UI.md:NN`。
> **只读**产出：未修改任何现有文件，仅新建本文件；未写 `_HY4_PROGRESS.md`（按本轮指令由主代理统一追加）。

---

## 0. 统计总览（数字均可复核，详见 §6）

| 指标 | 数字 | 复核依据 |
|---|---|---|
| 浮层个数 | 18 | §1 主表 L1–L18 |
| 附表：点名但非浮层的对照项 | 4 | §1 附表 A1–A4 |
| 含 `z-index` 字样的行数（声明处数） | 22 | §2 表：18 处 CSS + 4 处 JS |
| 其中「声明一个值」的处数 | 20 | 18 处 CSS + 8289、8320 两处 JS 赋值 |
| 其中「清空」的处数 | 2 | 8334、8372 `d.style.zIndex = ''` |
| 不同取值个数（静态 CSS 固定值） | 15 | §2 阶梯表第 1–15 行：2/5/12/15/20/30/40/45/55/60/90/95/98/99/100 |
| JS 动态表达式 | 1 | 8289 `i + 1`，产生 1..N，无固定值，不计入 15 |
| JS 值与静态重复 | 1 | 8320 `= 100`，与 254 重复，不新增取值 |
| 风险组合数 | 8 | §3 表 R1–R8 |
| 其中「倒置或相等」 | 5 | R1、R2、R3、R4、R5 |
| 失效/隔离项 | 12 | §4 表 F1–F12 |
| 其中真正导致不生效或倒置 | 4 | F9、F10、F11、F12 |
| 自身无 `position` 的失效 | 0 | 18 处静态声明逐一核对，见 §1 表 position 列与 §4 结论 |
| 对账：一致 | 14 | §5 表 #1、#2、#4–#15 |
| 对账：不一致 | 1 | §5 表 #3 |
| 对账：规范写了但代码没有 | 1 | §5 表 #3（层主题 vignette 遮罩） |
| 原生 `title=` 提示（tooltip）行数 | 27 | 行号清单见 §6 |

---

## 1. 浮层全清单

### 1.1 主表：18 个浮层 / 层叠层（L1–L18）

| # | 类别 | 选择器 | CSS 行号 | DOM 行号 | z-index 值 | position 值 | 谁把它显示出来（JS add/remove class 行号） |
|---|---|---|---|---|---|---|---|
| L1 | toast | `#toast` | 409–413 | 933 | 20 | `fixed`（410） | 7834–7840 `function toast`：7837 `t.classList.add('show')`；7839 `remove('show')`（1600ms） |
| L2 | overlay 面板 | `#overlay` | 416–418 | 959 | 30 | `fixed`（417） | 8510、8530 `$('#overlay').classList.remove('hidden')`；8535 `hideOverlay()` `add('hidden')`；8532–8534 牌堆按钮入口 |
| L3 | 帮助层 | `#help-overlay` | 310–311 | 920 | 60 | `fixed`（310） | 7158–7162 `o.classList.toggle('hidden')`；7164、7167、7184 `add('hidden')`；7182–7188 Esc 监听 |
| L4 | 职业详情模态 | `#class-modal` | 60 | 876 | 95 | `fixed`（60） | 8581 `remove('hidden')`；8585 `add('hidden')`；8591、8592、8596 关闭入口；62 行 `#class-modal.hidden{display:none}` |
| L5 | 总图层 | `#fullmap-layer` | 783–784 | 965 | 90 | `fixed`（784） | 8918 `add('show')`；8929 `remove('show')`；784 行默认 `display:none`，787 行 `.show{display:flex}` |
| L6 | 阶段横幅 | `#phase-banner` | 146–151 | 939 | 40 | `fixed`（147） | 7247–7251 `showEgg`：7249 `add('show')`、7251 `remove('show')`（2400ms）；8185–8190 boss 换阶段：8188 `add('show')`、8190 `remove('show')`（2000ms） |
| L7 | 卡详情 | `#card-detail` | 257–260 | 902 | 55 | `absolute`（258） | 8431 `box.classList.remove('hidden')`；8420、8427、7185、8337 `add('hidden')`；8313 拖拽时 `openCardDetail(i)` 打开 |
| L8 | 地图小图停靠 | `#mm-dock` | 680–681 | 8651 动态创建 | 45 | `fixed`（681） | 8651 `dock.id='mm-dock'`、8653 `insertBefore`、8654 `appendChild(mini0)`；9252 `toggle('show',big)`、9284 `add('show','big')`、9251 `toggle('big')`；683 `#mm-dock.show{display:block}` |
| L9 | 手牌 hover | `#hand .card:hover:not(...)` | 246–248 | 889（`#hand`） | 99 | `absolute`（继承 241 `#hand .card`） | 无 JS add/remove；由 CSS `:hover`（246）触发；525、655 行在 reduce / perf-low 下只覆盖 `transform`，不改 z-index |
| L10 | 手牌 selected | `#hand .card.selected` | 250–252 | 8208 渲染 | 98 | `absolute`（继承 241） | 无 classList 调用；8203–8208 渲染 HTML 时 `(pending === i ? ' selected' : '')` 直接写入 class |
| L11 | 手牌 dragging | `#hand .card.dragging` | 254 | 8311 加类 | 100 | `absolute`（继承 241） | 8311 `d.classList.add('dragging')`；8332、8370 `remove('dragging')`；8320 内联 `d.style.zIndex=100`；8334、8372 清空内联 |
| L12 | 出牌飞出残影 | `.card.ghost-fly` | 508 | 7963 克隆 / 7970 追加 | 40 | `fixed`（508） | 7959–7972 `flyCard`：7964 `g.classList.add('ghost-fly')`；7970 `document.body.appendChild(g)`；7971 `g.remove()`（320ms） |
| L13 | 漂浮伤害数字 | `.float` | 163–167 | 7984 动态 | 5 | `absolute`（164） | 7983–7991 `floatText`：7984 `el('div','float'...)`、7989 `container.appendChild(f)`、7990 `f.remove()`（450ms）；调用点 7216、8061、8169 |
| L14 | 濒血红光（占 z=12 的装饰） | `body.dying #app::after` | 511–512 | 伪元素 | 12 | `fixed`（512） | 8034 `document.body.classList.toggle('dying', ...)`；伪元素随 body 类出现，无独立 class |
| L15 | 字号/低饱和按钮 | `.fontbtns` | 466 | 934 | 15 | `fixed`（466） | 无显隐控制（常驻）；935–937 三个按钮；8614 `#lowsat` `body.classList.toggle('lowsat')` 只改主题，不改本层 |
| L16 | 卡内角标·费用 | `.card .cost` | 211–212 | 8209 渲染 | 2 | `absolute`（212） | 无显隐；8209 `d.appendChild(el('div','cost', uiCost(card)))` 随卡渲染 |
| L17 | 卡内角标·类型 | `.card .ctype` | 233 | 8210 渲染 | 2 | `absolute`（233） | 无显隐；8210 `d.appendChild(el('div','ctype', ...))` 随卡渲染 |
| L18 | 模态关闭按钮 | `#class-modal-close` | 79–80 | 878 | 2 | `absolute`（79） | 无独立显隐（随 L4）；8591 绑定 `closeClassModal`；878 行 `title="关闭（Esc / 点遮罩）"` |

### 1.2 附表：任务点名、但源码里不构成独立浮层的 4 项（每格仍填实，不留空）

| # | 类别 | 选择器 / 载体 | CSS 行号 | DOM 行号 | z-index 值 | position 值 | 显示控制与依据 |
|---|---|---|---|---|---|---|---|
| A1 | tooltip | 原生 `title=` 属性（27 行） | 无（无 CSS 浮层规则） | 839–848、878、898、903、935–937、962、967 等 | 无（未声明） | 无（UA 渲染，非页面元素） | 浏览器 UA 控制，无 JS add/remove；全文件 `data-tip`/`tooltip`/`role="tooltip"`/`\.tip` 命中 0 处；UI.md:17 提到的遗物悬停说明即此机制 |
| A2 | 结算层 | `#screen-flow` | 329–330 | 915 | 无（未声明） | `static`（无定位，普通 section） | 6738–6741 `showScreen`：6739 全部 `add('hidden')`、6740 `$(id).classList.remove('hidden')`；结算入口 7677、7745 `showScreen('#screen-flow')`；7676 `phase='gameover'`、7744 `phase='victory'`；结算内容 7673 注释、7757/7781 `el('div','ending',...)` 写进 `#flow-panel`（916） |
| A3 | 小地图本体 | `#minimap` | 714–720 | 961 | 无（未声明） | `static`（无定位） | 无 JS 直接显隐；8653–8654 被移入动态 `#mm-dock`；722 `#mm-dock.show:not(.big) #minimap{display:flex}`、683 `#mm-dock.show{display:block}` 间接受控 |
| A4 | 协议横幅 | `#protocol-banner` | 481–484 | 885 | 无（未声明） | `static`（无定位，普通流内） | 8077–8082：8081 `pb.classList.remove('hidden')`、8082 `pb.classList.add('hidden')`；27 行 `.hidden{display:none !important}` |

**判定依据**：浮层 = 脱离正常流、以覆盖方式出现（`position:fixed/absolute`）或规范表登记为层的元素。A1（UA tooltip）、A2（整屏切换）、A3（靠父显示、自身 static）、A4（普通流内横幅）均不满足，单列以免漏项。

---

## 2. 完整 z-index 阶梯表（按值排序，含内联与 JS 动态设置）

| 序 | z-index 值 | 声明处（行号 / 选择器） | 处数 | position | 类别 | 显示/写入来源 |
|---|---|---|---|---|---|---|
| 1 | 2 | 80 `#class-modal-close`；212 `.card .cost`；233 `.card .ctype` | 3 | `absolute` | 局部层 | CSS 静态；无 JS 写入 |
| 2 | 5 | 167 `.float` | 1 | `absolute` | 局部层 | CSS 静态 |
| 3 | 12 | 512 `body.dying #app::after` | 1 | `fixed` | 装饰 | CSS 静态；8034 `toggle('dying')` |
| 4 | 15 | 466 `.fontbtns` | 1 | `fixed` | 常驻 | CSS 静态 |
| 5 | 20 | 413 `#toast` | 1 | `fixed` | 反馈 | CSS 静态；7837 `add('show')` |
| 6 | 30 | 418 `#overlay` | 1 | `fixed` | 面板 | CSS 静态；8510/8530 `remove('hidden')` |
| 7 | 40 | 151 `#phase-banner`；508 `.card.ghost-fly` | 2 | `fixed` | 反馈 / 横幅 | CSS 静态；7249/8188、7964 |
| 8 | 45 | 681 `#mm-dock` | 1 | `fixed` | 小图 | CSS 静态；9252/9284 |
| 9 | 55 | 260 `#card-detail` | 1 | `absolute` | 信息区 | CSS 静态；8431 `remove('hidden')` |
| 10 | 60 | 311 `#help-overlay` | 1 | `fixed` | 帮助 | CSS 静态；7161 `toggle('hidden')` |
| 11 | 90 | 784 `#fullmap-layer` | 1 | `fixed` | 总图 | CSS 静态；8918 `add('show')` |
| 12 | 95 | 60 `#class-modal` | 1 | `fixed` | 模态 | CSS 静态；8581 `remove('hidden')` |
| 13 | 98 | 252 `#hand .card.selected` | 1 | `absolute`（241） | 手牌 | CSS 静态；8208 写入 class |
| 14 | 99 | 248 `#hand .card:hover:not(...)` | 1 | `absolute`（241） | 手牌 | CSS 静态；`:hover`（246） |
| 15 | 100 | 254 `#hand .card.dragging` | 1 | `absolute`（241） | 手牌 | CSS 静态；8311 加类 |
| 16 | 动态 1..N | 8289 `el.style.zIndex = i + 1`（`layoutFan` 8275） | 1 | `absolute`（241） | JS 动态 | 8223、8335、8373 调用 `layoutFan()` |
| 17 | 动态 100 | 8320 `d.style.zIndex = 100` | 1 | `absolute`（241） | JS 动态 | 8307–8323 `onMove` 内 |
| 18 | 清空 `''`（非值） | 8334、8372 `d.style.zIndex = ''` | 2 | `absolute`（241） | JS 清空 | 8334（onUp）、8372（onCancel）；随后 8335/8373 重跑 `layoutFan()` 复原为第 16 行 |

**口径说明**：第 1–15 行为静态 CSS，共 18 处声明、15 个不同取值；第 16–18 行为 JS 运行时写入，共 4 行 `z-index` 字样（2 处赋值、2 处清空）。8320 的值 100 与第 15 行重复，不新增取值；8289 是表达式，产生 1..N（N = 手牌张数，8284 `cards.forEach`），无固定值，故不计入「不同取值个数」。全文 `z-index` 字样共 22 行，即 18 + 4。

---

## 3. 互相盖住的风险

**静态数值基准**：把 §2 第 1–15 行按 `docs/UI.md` §1 表顺序（UI.md:26–35）排列，代码值严格递增
`2 < 5 < 12 < 15 < 20 < 30 < 40 < 45 < 55 < 60 < 90 < 95 < 98 < 99 < 100`，
与 UI.md:37「反馈 < 面板 < 总图 < 模态 < 拖拽中的牌」一致，**纯数值层面 0 组倒置**。
以下风险来自同值、优先级覆盖、DOM 顺序与运行时层叠上下文。

| # | 组合 | 本该盖住谁（依据） | 实际值比较 | 判定 | 行号证据 |
|---|---|---|---|---|---|
| R1 | `#phase-banner`(40) vs `.card.ghost-fly`(40) | 规范只把 40 给横幅（UI.md:29），二者谁盖谁无规范定义 | 相等（40 = 40） | **同值风险**：按 DOM 顺序定，ghost-fly 由 7970 `document.body.appendChild(g)` 追加到 body 末尾，晚于 939 的 `#phase-banner`，故 ghost-fly 压住横幅；标「代码有、运行时不保证」 | 151、508、939、7970 |
| R2 | `layoutFan` 内联 `zIndex=i+1` vs CSS 248(99)/252(98)/254(100) | UI.md:35 要求 hover/selected/dragging 依次 99/98/100「拖牌永远在最上」 | 内联样式 > 类规则；98/99/100 被 1..N 覆盖 | **层级倒置（优先级打架）**：hover 卡实际 z = i+1（可能仅 3），会被后面 i 更大的牌盖住；254 的 `!important` 只作用于 `transition`（254 同行），不给 z-index；标「代码有、运行时不保证」 | 8289、8223、248、252、254、UI.md:35 |
| R3 | `.card .cost`(2) vs `.card .ctype`(2) | 二者同为卡内角标（UI.md:26），规范未分先后 | 相等（2 = 2） | **同值**：同一张卡内按 DOM 顺序，8209 `cost` 先、8210 `ctype` 后 → ctype 压 cost；但 212 `left:5px`、233 `right:6px` 分列两侧不重叠，无实际遮挡。另 80 `#class-modal-close` 同为 2，被 60（z95）层叠上下文隔离，不与二者比较 | 212、233、8209、8210、80、60 |
| R4 | CSS 254(100) vs JS 8320(100) | 同一元素 `#hand .card.dragging` | 相等（100 = 100） | **同值**：两处写同一值，内联 8320 优先；实际生效值是 JS 内联，非 CSS 254；8334/8372 清空后由 8335/8373 `layoutFan()` 复原为 i+1。不冲突，但「CSS 声明本身不生效」 | 254、8320、8334、8372、8335、8373 |
| R5 | `#app` 内浮层 vs `#app` 外浮层（运行时） | UI.md:37 要求拖牌(100) > 总图(90) > 模态(95) > 帮助(60) | 默认 100>90>60 成立；条件成立时全倒置 | **运行时倒置**：`body.lowsat #app { filter }`（472，8614 触发）或 `body.shake #app { animation:shake }`（506，8038 触发，@keyframes shake 505 含 `transform`）使 `#app` 创建层叠上下文、自身 `z-index:auto`，内部 `#class-modal`(95)/`#card-detail`(55)/手牌(98/99/100) 被隔离，盖不住 `#app` 外 `#toast`(20)~`#fullmap-layer`(90)；标「代码有、运行时不保证」 | 834、919、472、8614、506、8038、505、60、260、248、252、254、784、311 |
| R6 | `#class-modal`(876，在 `#app` 内) vs `#help-overlay`(920)/`#fullmap-layer`(965，在 `#app` 外) | 95 > 90 > 60 | 数值成立，但依赖 `#app` 不创建层叠上下文 | **结构依赖**：919 `</div>` 关闭 `#app`；一旦 R5 条件成立，95/90/60 不再可比。默认 28 行 `#app` 仅 `overflow:hidden`，不创建层叠上下文，故默认无倒置 | 834、876、919、920、965、28、60、784、311 |
| R7 | `.card.ghost-fly`(40) vs `#fullmap-layer`(90) | 总图应盖住反馈（UI.md:33/37） | 90 > 40 | **对照判定，非风险**：ghost-fly 虽在 7970 追加到 body 末尾（DOM 最晚），但 z 值 40 < 90，总图仍盖住残影，无倒置 | 508、7970、784、UI.md:33 |
| R8 | `body.dying #app::after`(12) vs `#toast`(20)/`.fontbtns`(15)/`#card-detail`(55)/手牌(98/99/100) | UI.md:27 定义 12 为「纯装饰，pointer-events:none」 | 12 < 15/20/55/98/99/100 | **对照判定，非风险**：红光盖不住任何带正 z 的浮层与手牌，符合「装饰在底」；512 `inset:0` 全屏但 `pointer-events:none` | 512、466、413、260、248、252、254、UI.md:27 |

风险组合数 = 8（R1–R8 逐行）；其中「层级倒置或相等」5 组（R1、R2、R3、R4、R5），结构依赖 1 组（R6），判定符合规范 2 组（R7、R8）。

---

## 4. 失效的 z-index

**结论 A（自身无 position）**：18 处静态 `z-index` 声明的元素**自身均有非 static 的 position**，失效 **0 处**：
`fixed` —— 60、147（151 所属规则）、310（311）、410（413）、417（418）、466、508、512、681、784；
`absolute` —— 79（80）、164（167）、212、233、258（260）；
248/252/254 三条规则自身不写 position，但作用对象 `#hand .card` 由 241 行 `position: absolute` 提供（另有 195 行 `.card{position:relative}`），故元素仍非 static。
2 处 JS 赋值目标同为 `#hand .card`（8289、8320），同样有 241 行的 `absolute`。
→ 「用了 z-index 但元素自身 static」= **0 处**。

**结论 B（层叠上下文隔离）**：逐项列于下表 F1–F12。

| # | 项 | 行号 | 依据（为何被隔离 / 为何不生效） | 是否影响意图 | 类别 |
|---|---|---|---|---|---|
| F1 | `#class-modal-close` z=2 | 80 | 父 `#class-modal`（60，`fixed`+z95）创建层叠上下文 → close 的 z 只在模态内比较 | 不影响：仅需盖住 `#class-modal-box`（63，`position:relative` 无 z-index）内容 | 静态隔离 |
| F2 | `.card .cost` z=2 | 212 | 父 `#hand .card` 有 `transform: var(--fan)`（243），每张卡创建层叠上下文 → 角标 z 被隔离在卡内 | 不影响：意图就是卡内角标 | 静态隔离 |
| F3 | `.card .ctype` z=2 | 233 | 同 F2（243） | 不影响：同 F2 | 静态隔离 |
| F4 | `#toast` z=20 | 413 | 自身 `transform: translateX(-50%)`（410）创建层叠上下文 | 不失效：叶子元素，z 仍作用于根层叠上下文 | 自身上下文 |
| F5 | `#phase-banner` z=40 | 151 | 自身 `transform: translateX(-50%)`（147）创建层叠上下文 | 不失效：同 F4 | 自身上下文 |
| F6 | `.float` z=5 | 167 | 自身 `transform`（165）+ `@keyframes floatup` 中 `opacity:0`（170）创建层叠上下文 | 不失效：叶子元素，z 生效 | 自身上下文 |
| F7 | `.card.ghost-fly` z=40 | 508 | `position:fixed` + 运行时 7970 `appendChild(body)` | 不失效：直接参与根层叠上下文 | 自身上下文 |
| F8 | `#minimap`（无 z-index） | 961 / 714–720 | 被动态 `#mm-dock`（8651，681 `fixed`+z45）包裹；`#mm-dock.big` 有 `transform`（685）创建层叠上下文 | 不适用：本身未声明 z-index，靠父定位（722、683） | 派生 |
| F9 | `#hand .card:hover` z=99 / `.selected` z=98 | 248 / 252 | `layoutFan` 8289 `el.style.zIndex = i + 1` 是内联样式，优先级高于选择器规则；248/252 无 `!important`（254 的 `!important` 只给 `transition`）→ 两条 CSS 声明被覆盖 | **失效**：hover/selected 达不到 99/98；标「代码有、运行时不保证」 | 优先级覆盖 |
| F10 | `#hand .card.dragging` z=100 | 254 | 同 F9 被 8289 内联覆盖；仅 8307–8323 的 8320 `d.style.zIndex = 100` 把内联改回 100 才生效，值来自 JS 而非 CSS 254 | **失效（CSS 声明）**：254 本身不生效；标「代码有、运行时不保证」 | 优先级覆盖 |
| F11 | `body.lowsat #app` 运行时隔离 | 472 / 8614 | `filter: saturate(.55) contrast(.95)` ≠ none → `#app` 创建层叠上下文、自身 `z-index:auto`；8614 `toggle('lowsat')` 触发 | **运行时倒置**：隔离内部 95/55/98/99/100，盖不住外部 20–90；标「代码有、运行时不保证」 | 条件失效 |
| F12 | `body.shake #app` 运行时隔离 | 506 / 8038 / 505 | `animation: shake` 的 `@keyframes shake`（505）含 `transform: translateX` → 运行时（.22s）`#app` 创建层叠上下文；8038 `add('shake')` 触发 | **运行时倒置**：同 F11；标「代码有、运行时不保证」 | 条件失效 |

**补充对照（不计入 F1–F12，逐项有据）**：
- `body.eggflash #app`（374）的 `@keyframes eggflash`（375）只改 `box-shadow`；`body.resflash #app`（660）的 `@keyframes resflash`（661）只改 `box-shadow` → 两者均不创建层叠上下文，不影响层级。
- `#screen-combat`（37，`position:relative`，`z-index:auto`）、`#hand`（191，`position:relative`，`z-index:auto`）不创建层叠上下文 → 默认 `#card-detail`(55)、手牌(98/99/100) 参与根层叠上下文。
- `#toast`（412 `opacity:0` → 415 `opacity:1`）、`#phase-banner`（151 `opacity:0` → 153 `opacity:1`）在 `transition`（413、151）期间 0<opacity<1 会临时创建层叠上下文；二者为叶子，无内部 z-index 比较需求，不影响。
- 失效/隔离项合计 **12**（F1–F12）；其中真正导致不生效或倒置 **4**（F9–F12），静态隔离不影响意图 3（F1–F3），不失效/不适用 5（F4–F8）。

---

## 5. 与 `docs/UI.md` §1 z-index 规范表逐条对账

规范表原文 `UI.md:24–35` 共 11 行，其中「2 / 5」「20 / 30 / 40」「98 / 99 / 100」为多值行，
拆成 **15 条**逐条核对。

| # | 规范 z（UI.md 行） | 规范元素 | 代码对应 | 代码行号 | 判定 |
|---|---|---|---|---|---|
| 1 | 2（UI.md:26） | 卡内角标 | `.card .cost` / `.card .ctype` | 212 / 233 | 一致 |
| 2 | 5（UI.md:26） | 漂浮伤害数字 | `.float` | 167 | 一致 |
| 3 | 12（UI.md:27） | 层主题 vignette 遮罩（纯装饰、pointer-events:none） | 无该元素；z=12 唯一声明是 `body.dying #app::after`（濒血红光） | 512；`vignette/暗角` 全文仅注释 532、600 | **不一致** |
| 4 | 15（UI.md:28） | `.fontbtns` 字号/低饱和按钮 | `.fontbtns` | 466 | 一致 |
| 5 | 20（UI.md:29） | `#toast` | `#toast` | 413 | 一致 |
| 6 | 30（UI.md:29） | `#overlay`（牌堆·结算面板） | `#overlay` | 418 | 一致（值）；用途描述另注，见下 |
| 7 | 40（UI.md:29） | `#phase-banner` | `#phase-banner` | 151 | 一致 |
| 8 | 45（UI.md:30） | `#mm-dock` 小图 | `#mm-dock` | 681 | 一致 |
| 9 | 55（UI.md:31） | `#card-detail` | `#card-detail` | 260 | 一致 |
| 10 | 60（UI.md:32） | `#help-overlay` | `#help-overlay` | 311 | 一致 |
| 11 | 90（UI.md:33） | `#fullmap-layer` | `#fullmap-layer` | 784 | 一致 |
| 12 | 95（UI.md:34） | `#class-modal` | `#class-modal` | 60 | 一致 |
| 13 | 98（UI.md:35） | 手牌 `selected` | `#hand .card.selected` | 252 | 一致（值）；实际被 8289 内联覆盖，见 §4 F9 |
| 14 | 99（UI.md:35） | 手牌 `hover` | `#hand .card:hover` | 248 | 一致（值）；实际被 8289 内联覆盖，见 §4 F9 |
| 15 | 100（UI.md:35） | 手牌 `dragging` | `#hand .card.dragging` | 254 | 一致（值）；CSS 声明被覆盖，实际值来自 8320，见 §4 F10 |

**对账结果**：一致 **14** 条（#1、#2、#4–#15）；不一致 **1** 条（#3）；规范写了但代码没有 **1** 条（#3 的元素）。14 + 1 = 15，与规范拆分条数相符。

**#3 判定依据**：全文件 `vignette` / `暗角` 仅出现于注释 532（「叠纸纹与暗角」）、600（「纹理与暗角画在背景层」）；
z=12 的唯一声明是 512 `body.dying #app::after`（濒血红光，8034 `toggle('dying')` 触发），不是层主题遮罩；
`html[data-theme="C"] body`（599–607）的 `radial-gradient` 暗角是 `background-image` 背景层，无独立元素、无 z-index。
→ 规范中的「层主题 vignette 遮罩」在代码中**不存在**；z=12 被另一个元素占用。

**#6 用途描述备注（不影响值一致性）**：UI.md:18、UI.md:29 把 `#overlay` 称为「牌堆·结算面板」。
代码里 `#overlay` 的两个显示点是 8510（`showSalvagePanel` 回收面板，8496 注释）与 8530（`showPile` 牌堆查看，8513 注释），
8532–8534 绑定抽/弃/消耗牌堆按钮；结算走 `#screen-flow`（915，7677、7745 `showScreen('#screen-flow')`，7676 `phase='gameover'`、7744 `phase='victory'`）。
→ 值 30 一致，但「结算面板」这一用途在 `#overlay` 上代码中不存在。

**代码有、规范未登记的额外项（单列，不计入 15 条对账）**：
| 项 | 行号 | 说明 |
|---|---|---|
| `#class-modal-close` z=2 | 80 | 规范 2 只写「卡内角标」 |
| `.card.ghost-fly` z=40 | 508 | 规范 40 只写 `#phase-banner`；与 R1 同值 |
| `body.dying #app::after` z=12 | 512 | 占用规范 12 的值，元素不是 vignette |
| JS 动态 `zIndex = i+1` | 8289 | 内联覆盖 CSS 手牌层级 |
| JS 动态 `zIndex = 100` | 8320 | 与 254 同值，来源为 JS |
| JS 清空 `zIndex = ''` | 8334、8372 | 非值声明 |
| `#minimap` / `#protocol-banner` / `#screen-flow` | 961 / 885 / 915 | 无 z-index，见 §1 附表 A2–A4 |
| 原生 `title=` tooltip | 27 行，见 §6 | 无 CSS 浮层，见 §1 附表 A1 |

---

## 6. 统计数字复核表

| 指标 | 数字 | 复核依据（行号 / 选择器） |
|---|---|---|
| 文件总行数 | 9490 | `node` `split(/\r?\n/)` 结果；6620 行 `len=187571` 且 `含z-index=false` |
| 含 `z-index` 字样的行数 | 22 | 60、80、151、167、212、233、248、252、254、260、311、413、418、466、508、512、681、784（18 CSS）+ 8289、8320、8334、8372（4 JS） |
| CSS 静态声明处数 | 18 | 上列前 18 个行号，§2 表第 1–15 行的「处数」列合计 3+1+1+1+1+1+2+1+1+1+1+1+1+1+1 = 18 |
| JS 写入行数 | 4 | 8289、8320、8334、8372 |
| 「声明值」处数 | 20 | 18 CSS + 8289、8320；8334、8372 是赋空串清空 |
| 「清空」处数 | 2 | 8334、8372 `d.style.zIndex = ''` |
| 不同取值个数（静态固定值） | 15 | 2、5、12、15、20、30、40、45、55、60、90、95、98、99、100（§2 第 1–15 行） |
| JS 动态表达式个数 | 1 | 8289 `i + 1`（1..N，8284 `cards.forEach`，N = 手牌数） |
| JS 与静态重复值 | 1 | 8320 = 100，与 254 重复 |
| 浮层个数 | 18 | §1 主表 L1–L18 |
| 非浮层对照项 | 4 | §1 附表 A1–A4 |
| 风险组合数 | 8 | §3 表 R1–R8（倒置或相等 5：R1–R5；结构依赖 1：R6；符合规范 2：R7–R8） |
| 失效 / 隔离项 | 12 | §4 表 F1–F12（真正不生效/倒置 4：F9–F12） |
| 自身无 position 的失效 | 0 | 18 处静态声明逐一核对：fixed 60/147/310/410/417/466/508/512/681/784；absolute 79/164/212/233/258/241 |
| 对账一致 | 14 | §5 表 #1、#2、#4–#15 |
| 对账不一致 | 1 | §5 表 #3 |
| 规范写了但代码没有 | 1 | §5 表 #3「层主题 vignette 遮罩」；依据 512、532、600、599–607 |
| 代码有但规范未登记的额外项 | 8 类 | §5「额外项」表 8 行 |
| `title=` 原生 tooltip 行数 | 27 | 839、840、841、842、843、844、845、846、847、848、878、898、903、935、936、937、962、967、6984、7111、7612、7698、7775、8665、8669、8670、8870 |
| `classList.add/remove/toggle` 行数 | 未验证：本清点只统计与浮层相关的控制行（§1 表「显示控制」列逐行给出），未对全文所有 classList 调用做去重计数，故不给总数 | — |

---

## 边界声明

- **没开浏览器**。以上结论均按 `web/index.html` 的 CSS / JS 源码**静态清点**得出，不是实际渲染结果；行号、选择器、数值可用 `node -e` 按行复现。
- **优先级打架标「代码有、运行时不保证」**：R1（同值 40，最终前后依赖 7970 运行时 `appendChild` 的 DOM 顺序）、R2 / R4 / F9 / F10（8289 内联 `zIndex` 覆盖 CSS 98/99/100）、R5 / R6 / F11 / F12（`body.lowsat` / `body.shake` 时 `#app` 条件性创建层叠上下文）——这些项在源码中有声明，但运行时是否生效、谁压谁，取决于类状态与 DOM 顺序，静态源码不保证。
- **未验证**：实际层叠绘制顺序、opacity 过渡瞬间（413、151 的 `transition`）的层叠上下文、`filter`（472）与 `animation`（506）触发时的真实渲染、`#mm-dock`（8651 动态创建）在 `?map=old` 回退通道（8645 `return`）下是否注入 —— 均标「未验证：未开浏览器 / 运行时条件不在静态源码内」。
- 同值 `z-index` 的最终前后关系由 DOM 顺序决定，本文只对静态 DOM（834–971 行）与已知的运行时追加点（7970）给条件判断，不对实际渲染下结论。
- 本文**只读**：未修改 `web/index.html`、`docs/UI.md` 或任何现有文件；仅新建 `docs/design/ui/x5_layers.md`；未写 `_HY4_PROGRESS.md`（按本轮指令由主代理统一追加）。
