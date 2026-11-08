# H4 · 交互态矩阵

> 输入：`C:\Users\Administrator\Desktop\杂七杂八\红渊\game\web\index.html`（冻结版本）
> 输出口径：代码级事实，只写能数、能指回行号的东西。

---

## 1. 口径与检索方法

**五态判据**：

| 列 | 判定依据 |
|---|---|
| 默认 | 存在该元素的基础 CSS 选择器（含 `cursor:pointer` 等） |
| `:hover` | 存在 `:hover` 选择器（含 `:hover:not(...)` 形式） |
| `:active` | 存在 `:active` 选择器 |
| 禁用 | `:disabled` / `.disabled` / `[disabled]`，或语义等价的自定义禁用类（`.dimmed` / `.cant` / `.sold` / `.wrongworld` / `.dead` / `.done` / `.unseen`） |
| 选中 | `.selected` / `.on` / `[aria-selected="true"]`，或语义等价的 `.here` / `.cursor` / `.active` / `.hl` / `.targetable` |

扩展口径已在表内逐格注明，**不把「默认样式里的普通类名」算作状态**。

**检索式**：`:hover`、`:active|:disabled|\.disabled|\[disabled\]|aria-disabled|:focus-visible|:focus\b`、`.selected|.on\b|aria-selected|aria-pressed|.active\b`、`classList\.(add|toggle|remove)\(`、`role="tab"|tablist|\.tab\b|\.btn\b`、`<button|el\('button'`、状态颜色/尺寸词。

**三条全局事实（先列出，表中不再重复）**：

1. **`:active` 全文 0 处**。以 `:active` 检索 `index.html` 无匹配，因此下表 25 类元素的「按下」态**全部缺失**。
2. **没有标签页组件**：`role="tab"` / `tablist` / `aria-selected` / `aria-pressed` / `.tab` / `.tabs` / `.on` / `.current` 全文 **0 处**。任务书提到的「标签页」在本代码中不存在，故不占表行。
3. **没有 `.btn` 类和全局 `button {}` 规则**：`.btn` 全文 0 处；唯一的全局 `button` 选择器是 471 的 `button:focus-visible`（焦点态，非五态之一）。所有按钮样式都按容器/ID 单独写，因此每个按钮组必须单独占一行。

**焦点态（非五态，附加）**：471–472 `button:focus-visible, .mnode:focus-visible, .campopt:focus-visible, .card:focus-visible { outline: 2px solid #c9a35a }`；职业卡另有 56、58 的 `:focus-visible` 上浮+双阴影。

---

## 2. 主表：交互态矩阵（25 类元素）

单元格格式：`有（行号）` / `无`。「缺哪几态」列只数五态。

| 元素类 | 选择器 | 默认 | `:hover` | `:active` | 禁用 | 选中 | 缺哪几态 |
|---|---|---|---|---|---|---|---|
| `.classface` 职业卡（`<button>` 855/859/863/867） | `.classface` | 有（49–53） | 有（56，与 `:focus-visible` 合并） | 无 | 无 | 无 | `:active`、禁用、选中（3） |
| `#btn-dive-confirm` 确认开局（8256） | `#btn-dive-confirm` | 有（78，仅 padding / font-size / letter-spacing） | 无 | 无 | 无 | 无 | `:hover`、`:active`、禁用、选中（4） |
| `#class-modal-close`（876） | `#class-modal-close` | 有（79–80） | 有（81） | 无 | 无 | 无 | `:active`、禁用、选中（3） |
| `#btn-end` 结束回合（895） | `#btn-end` | 有（293–297） | 有（298） | 无 | 无 | 无 | `:active`、禁用、选中（3） |
| `#btn-help` 机制速查（896） | `#btn-help` | 有（301–306） | 有（307） | 无 | 无 | 无 | `:active`、禁用、选中（3） |
| `#btn-world` 入梦/醒（894） | —（**全文 0 处 CSS 规则**） | **无** | 无 | 无 | **无**（JS 7919 设 `bw.disabled`，但无 `:disabled` 规则） | 无 | 默认、`:hover`、`:active`、禁用、选中（**5**） |
| `#piles span` 牌堆计数（890–892） | `#piles span` | 有（291） | 有（292） | 无 | 无 | 无 | `:active`、禁用、选中（3） |
| `#cd-side button` 打出/收回（907） | `#cd-side button` | 有（277） | 有（279，`:hover:not(:disabled)`） | 无 | 有（278 `:disabled`；JS 8103 设置） | 无 | `:active`、选中（2） |
| `#card-detail .cd-close`（901） | `#card-detail .cd-close` | 有（262–265） | 有（266） | 无 | 无 | 无 | `:active`、禁用、选中（3） |
| `#flow-panel .btnrow button` 继续/跳过/重开等（7245、7272、7301、7434、7471、7567…） | `#flow-panel .btnrow button` | 有（358–361） | 有（363） | 无 | 无 | 无 | `:active`、禁用、选中（3） |
| `#help-page .btnrow button`（928） | `#help-page .btnrow button` | 有（319–322） | 有（324） | 无 | 无 | 无 | `:active`、禁用、选中（3） |
| `#overlay .panel button` 改造/拆解/关闭/合上（8162、8173、8183、8203） | `#overlay .panel button` | 有（425–429） | 无 | 无 | 无 | 无 | `:hover`、`:active`、禁用、选中（4） |
| `.optbtn` 事件选项（7381） | `.optbtn` | 有（342–347） | 有（348） | 无 | 有（349 `:disabled`；JS 7389 设置） | 无 | `:active`、选中（2） |
| `.campopt` 营火选项（6693） | `.campopt` | 有（432–437） | 有（438） | 无 | 有（441 `.disabled`、442 `.disabled:hover`；JS 6693 加类） | 无 | `:active`、选中（2） |
| `.shopitem` 商店格（6845） | `.shopitem` | 有（450） | 有（451） | 无 | 有（455 `.cant`、457 `.sold`、456 `.cant:hover`；JS 6887–6888 加类） | 无 | `:active`、选中（2） |
| `.relicrow .relic` 奖励遗物（7286、7291） | `.relicrow .relic` | 有（375–379、380） | 有（381） | 无 | 无 | 无 | `:active`、禁用、选中（3） |
| `.mnode` 地图节点（6597） | `.mnode` | 有（391–395） | 有（401 `.pickable:hover`；可选态另见 398–400） | 无 | 有（396 `.done` 已走过） | 有（397 `.here` 当前所在；485、545 主题覆写） | `:active`（1） |
| `#hand .card` 战斗手牌（7888） | `#hand .card` | 有（192–197、238–243） | 有（198 全局 `.card:hover`、244–247 专用） | 无 | 有（207 `.dimmed`、496 `.wrongworld`） | 有（208 `.card.selected`、248 `#hand .card.selected`；另 252 `.dragging`） | `:active`（1） |
| `#flow-cards .card` 奖励卡 / `renderCardStatic()`（7353、7262） | `#flow-cards .card` | 有（192–197、352–356） | 有（198、201、202–203） | 无 | 有（207 `.dimmed`、496 `.wrongworld`） | 有（208 `.card.selected`，**但 JS 7262 点击后直接 `onDone()`，未加 `selected` 类** → CSS 有、JS 不用） | `:active`（1） |
| `#cd-card .card` 详情大卡（269–270） | `#cd-card .card` | 有（192–197、269–270） | 有（198 全局；269 把 `cursor` 设为 `default`） | 无 | 无 | 无 | `:active`、禁用、选中（3） |
| `.enemy` 敌人目标（7801、7839） | `.enemy` | 有（126–129） | **无**（全文无 `.enemy:hover`） | 无 | 有（131 `.dead`、499 主题覆写） | 有（130 `.targetable`、286 `.drop-hot`；JS 7801、7997、8007 加类） | `:hover`、`:active`（2） |
| `.fm-node` 总图节点（8500） | `.fm-node` | 有（735–736） | 有（747 `.btrack:hover`、751 `.pick:hover`） | 无 | 有（740 `.unseen`） | 有（817–820 `.cursor`、752 `.here`、753–754 `.hl`；JS 8567、8569、8993 加类） | `:active`（1） |
| `.mm-row` 小图行程行（8555） | `.mm-row` | 有（769–772） | 有（773） | 无 | 无 | 有（774 `.active`；JS 8561 加类） | `:active`、禁用（2） |
| `.fontbtns button` 字号/低饱和（933–935） | `.fontbtns button` | 有（465–468） | 有（469） | 无 | 无 | 无（`lowsat` 加在 `document.body` 8290，不是按钮自身） | `:active`、禁用、选中（3） |
| 地图控制按钮组 `#hud-mapbtn`(8340) / `#btn-fullmap`(960) / `#fm-zbar button`(8345–8346) / `#fm-close`(965) | 各自 ID 选择器 | 有（707–710 / 723–726 / 795–796 / 811–812） | 有（711 / 727 / 797 / 813） | 无 | 无 | 无 | `:active`、禁用、选中（3） |

---

## 3. 汇总计数

25 类元素 × 5 态 = **125 个状态位**。

| 状态 | 已定义 | 缺失 | 缺失率 |
|---|---|---|---|
| 默认 | 24 | 1（`#btn-world`） | 1/25 |
| `:hover` | 21 | 4（`#btn-dive-confirm`、`#btn-world`、`#overlay .panel button`、`.enemy`） | 4/25 |
| `:active` | **0** | **25** | **25/25** |
| 禁用 | 9 | 16 | 16/25 |
| 选中 | 6 | 19 | 19/25 |
| **合计** | **60** | **65** | 65/125 |

**按下态（`:active`）是唯一全表 0 覆盖的一态**；其余缺口集中在「禁用」「选中」两态——绝大多数普通按钮只有「默认 + 悬停」两态。

**缺 4–5 态的 4 类**：`#btn-world`（5 态全缺）、`#btn-dive-confirm`（4）、`#overlay .panel button`（4）、`.classface` 等 15 类缺 3 态。
**只缺 `:active` 的 4 类**：`.mnode`、`#hand .card`、`#flow-cards .card`、`.fm-node`——它们反而是状态最完整的（默认/悬停/禁用/选中都有）。

---

## 4. 「有类名但没样式」专项核查（任务书特别要求）

逐一比对 `classList.add / toggle / remove` 的全部调用点（Grep 共 103 行，范围 6508–8993）与 CSS 区（6–829），结果如下：

| JS 加的类 | JS 行号 | CSS 行号 | 有无样式 |
|---|---|---|---|
| `pickable` | 6605 | 398–400 | 有 |
| `sold` / `cant` | 6887 / 6888 | 457 / 455–456 | 有 |
| `world-dream` / `world-wake` | 6904–6905、7913–7914、7924–7925 | 488–495 / 489 | 有 |
| `dragging` | 7996 | 252 | 有 |
| `targetable` / `drop-hot` | 7801、7997、8007 | 130 / 286 | 有 |
| `hitflash` | 7851 | 137 | 有 |
| `flash` / `atk-hot` / `pulse` | 7772、7824、7827、7731、7933 | 107 / 476、500 / 110、113 | 有 |
| `show` / `hidden` / `big` | 7027、7615、8594、8927–8928、6517–6518 等 | 413、151、785 / 27 / 681 | 有 |
| `dimmed` / `wrongworld` / `costly` / `upgraded` / `selected` | 7892、7891、7889、7890、7893 | 207 / 496 / 206 / 460–461 / 208、248 | 有 |
| `disabled`（营火） | 6693 | 441–442 | 有 |
| `active`（小图行） | 8561 | 774 | 有 |
| `cursor` / `hl` | 8993 / 8569 | 817–820 / 753–754 | 有 |
| `panning` / `map-mode` / `has-art` | 8635 / 8950 / 7346、7818 | 804 / 815 / 822 | 有 |
| `eggflash` / `hp-low` / `dying` / `perf-low` / `clarity-low` / `lowsat` / `resflash` | 7032、7718、7719、7707、6580、8290、7665 | 372–373 / 106 / 509–514 / 651–655 / 497 / 470 / 658–659 | 有 |
| `ghost-fly` / `shakeit` | 7649 / 7955 | 506 / 204 | 有 |

**结论：交互相关的 `classList` 类名共 0 个「JS 加了、CSS 完全没写」**。这不是说状态齐全，而是说缺口以另一种形式存在：

1. **`#btn-world` 的 `disabled` 属性无 CSS 承接**：JS 7919 会设 `bw.disabled`，但全文没有 `#btn-world` 选择器，也没有 `#btn-world:disabled`；该按钮连默认样式都没有（894 只有 `class="hidden"`）。这是唯一一处「有状态、无样式」。
2. **反向缺口**：`.card.selected`（208）在 CSS 里写了，但奖励卡路径（7262）点击后直接 `onDone()`，从不加 `selected` 类 —— 属于「CSS 有、JS 不用」。
3. **`:active` 全表 0 处**（§1），以及 `aria-selected` / `aria-pressed` / `role="tab"` 全表 0 处 —— 这类是「根本没写选择器」，不是「类名没样式」。

---

## 5. 未验证项

- **未验证：CSS 优先级 / 运行时生效值**。例如 198 `.card:hover` 与 244 `#hand .card:hover` 同时命中手牌、200 与 238 同时设 `transition`、131 与 499 同时设 `.enemy.dead` 的 `opacity`；本报告只记「代码写了什么」，不判断最终渲染。这类统一标注「代码有、运行时不保证」。
- **未验证：浏览器原生 `<button>` 的默认外观**。本表把「无 CSS 规则」记为默认态缺失，不推断浏览器默认样式算不算「已定义」。
- **未验证：`#flow-cards .card` 是否在其他路径被加上 `.selected`**。本次检索 `classList` 调用与 7262 的点击处理，未见该类；未逐行追踪 `showCardChoice()` 之外的调用者。
- **未验证：`const RAW`（6401，184653 字符）、`window.ART`（3945，23442 字符）未解析**。它们是数据行，与 CSS 状态无关；检索工具已折叠。
- **未验证：任务书提到的「标签页」是否以其它名称存在**。按 `role="tab"|tablist|aria-selected|aria-pressed|\.tab\b|\.tabs\b|\.on\b` 检索全文 0 命中，故判定不存在。

---

## 6. 边界声明

- 我没开浏览器，所有结论是**代码级**的，不是视觉判断；文中不含「看起来」「感觉」「可能有点」这类描述。
- 我读到的是 `web/index.html` 的**当前冻结版本**（641927 B / 本地实测 9165 行；任务书标 8930 行，差异原因未查明）。如果之后代码变了，行号会漂移，结论要重跑。
- 我数的是**代码里写了什么**，不是**运行时实际渲染成什么**（比如 CSS 优先级打架时，写了也可能不生效）。这类情况已标「代码有、运行时不保证」。
- 只读审计：未修改 `web/`、`engine/`、`cards/`、`docs/` 下任何既有文件；本文件是 `docs/design/ui/` 下新建的产出。
