# T263 小分辨率布局审计（docs/LAYOUT_AUDIT.md）

> 审计日期：2026-11-03　审计对象：`web/index.html`（634,119 B，样式块 7–824 行）
> **口径声明：本审计是静态口径** —— 逐条读 CSS/JS 源码推演布局行为，未起浏览器实测。
> - 1280×720 档引用 TASK_DONE.md 里 T71 / T74 / T74.1 / T76 的既有浏览器实测记录（下文 §5）；
> - **1024×640 档全部为静态推定，实测留给人工**（§6 清单）；
> - 1920×1080 档为静态推定（该档所有定宽都小于视口，风险最低）。
> 本任务只审计不改码；未修复项见 §7。

---

## 1. 全局自适应机制盘点

| 机制 | 现状 | 位置 |
|---|---|---|
| 宽度媒体查询 | **没有**。唯一的 `@media` 是 `prefers-reduced-motion`（:513） | 无断点，桌面三档靠流式约束吃下去 |
| `min()` 钳制 | `#class-modal-box` min(940px,92vw)、`#help-page` min(600px,92vw)、`#overlay .panel` min(720px,90vw)、`#mm-dock.big` min(980px,94vw)×min(60vh,470px)、`#fm-svg` 高 min(70vh,780px) | 浮层全部双钳制 ✓ |
| vw/vh | `#app` 100vh；toast/phase-banner max-70vw；protocol-banner max-60vw；fm-svg max-88vw | 无字体级 vw（字号全部固定 px，桌面游戏可接受） |
| 内容梁 | `--lane: 1240px`，select/combat/flow 三屏共用 `max-width: var(--lane)` | 1024/1280 下被视口压到满宽，1920 下居中收 1240 ✓ |
| overflow 链 | body `overflow:hidden` → `#app` 100vh+hidden → `#screen-flow` `overflow-y:auto` → `#log-wrap`/`#mm-log-rows`/`#cd-lines`/`#fm-svg`/`#help-page`/`#overlay .panel` 各自内部滚动 | **整页滚动条在结构上不可能出现**；战斗链有 `flex:1 1 0; min-height:0`（HANDOFF_D2 修复，在案） |
| JS 自适应 | 手牌扇形 `span=min(66,max(38,(clientWidth-170)/(n-1)))`（:7905，随容器宽度缩）；小图 resize 后 120ms 重绘（:8993）；格子 <10px 只画当前带（T74 实测） | ✓ |
| 字体 | 系统等宽栈（ui-monospace/Consolas），无 @font-face、无网络字体 | 不参与布局风险 |

## 2. 1024px 宽下的固定像素尺寸表现

| 定宽项 | 尺寸 | 1024 下表现 |
|---|---|---|
| `--lane` 1240 | max-width 钳制 | 收满 1024，不溢出 ✓ |
| 职业卡面 `.classface` | 200×4 + gap 26×3 = 878 | < 1024 ✓（且 flex-wrap 兜底） |
| 敌人卡 `.enemy` | 230 宽 | 4 敌 = 920+gap+padding ≈ 1008 ≤ 1024；5 敌起 `#enemy-area overflow-x:auto` 内滚（有意设计）✓ |
| 手牌 `.card` 150×210 / 奖励卡 190×267 | 扇形 span 随 clientWidth 收；奖励卡 flex-wrap | ✓ |
| `#card-detail` | **定宽 304px、absolute right:2 top:92** | 1024 下覆盖战斗梁约 30% 宽，压在日志/敌人区右缘上（遮盖非溢出）→ §6 人工复核 |
| `#hand` 高 238 / 手牌脚一行 | 固定 | 640 高下战斗最小纵向和 ≈ 530–570px < 640，日志仍剩 ~100px ✓ |
| `#mm-dock.big` | min(980px,94vw)=962.6 × min(60vh,470)=384 @640 | 顶边 ≈ 242px；与标题/救援文案静态间距 ~40px，紧但不叠 → §6 人工复核 |
| 旧图 `.maprow` gap150 + `.mnode` 140 | 单行 5 节点 = 5×140+4×150+80 = 1380 | **> 1024，横向被 body hidden 裁切**（仅 `?map=old` 回退通道，新图默认）→ 风险判定 |
| 商店 `.shopgrid` | auto-fill minmax(200px,1fr) max 880 | 1024 下 4 列 ✓ |

## 3. 三档判定总表（计数：自适应 ✓ 7 / 风险 1 / 需人工复核 2）

| 档位 | 总判定 | 依据 |
|---|---|---|
| 1920×1080 | **✓（静态推定）** | 所有定宽 ≤ 980 < 1920；lane 收 1240 居中；浮层全部 min() 双钳制 |
| 1280×720 | **✓（实测背书）** | T71/T74/T74.1/T76 浏览器实测：多屏 pageScrollbar=false，见 §5 |
| 1024×640 | **需人工复核**（静态推定主体成立，2 个疑点 + 1 个明确风险） | §4 逐屏 + §6 清单 |

## 4. 逐屏审计（选择/地图/事件/战斗/奖励/商店/营火/结算 + 浮层）

### 4.1 选择屏 #screen-select（含 T78 职业详情模态）—— **自适应 ✓**
- 机制：max-width lane + margin auto 垂直居中；卡面 flex-wrap；模态 min(940px,92vw)×86vh、详情列 overflow-y auto、立绘列 40%+min-height 460。
- 1024×640 静态推算：卡面行 878 < 1024；纵向 430 < 640；模态高 550 ≥ 立绘 460。
- 风险点：无。640 高下模态详情区长文本走内滚。
- 实测：T78 在 1280×720 首屏探针全过（TASK_DONE :627 段：cardfaces=4、立绘全部加载成功、modalInDom=false）。

### 4.2 地图选择屏（#screen-flow map-mode + #mm-dock.big）—— **需人工复核（1024×640）**
- 机制：dock 固定 bottom14、宽 min(980px,94vw)、高 min(60vh,470px)；面板 grid `minmax(190px,250px) 1fr`（行程左列/地图右区）；window resize 重绘；格子 <10px 自动收窗口只画当前带；flow-panel.map-mode 顶对齐让位。
- 风险点：**1024×640** 下 dock 高收缩到 384px、顶边 ~242px；死路时「必须回返」文案+按钮+概率行静态累计 ~200px，间距仅 ~40px——不叠但很紧；且行程列表只剩 ~300px 高（内滚兜底）。**无实测，留人工**。
- 实测：1280×720 下 T74.1 实测 dock {left:150, top:274, bottom:706, 980×432}、标题完整（titleBottom 101 < 274）、pageScrollbar=false；T74 实测选择态 top96 不遮标题。

### 4.3 事件屏（#flow-panel .opts）—— **自适应 ✓**
- 机制：选项列 max-width 760 居中、块级按钮纵排、`#screen-flow overflow-y:auto` 兜底；长文本换行（.osub 12px）。
- 风险点：无。选项再多也只是内滚。T76 实测三主题渲染正常（1280×720）。

### 4.4 战斗屏 #screen-combat —— **需人工复核（1024×640 的 #card-detail 遮盖）**
- 机制：flex 列 + `min-height:0`（HANDOFF_D2 修复），日志 `flex:1 1 0; min-height:60px; overflow-y:auto`；敌人区 `overflow-x:auto`（5 敌起横向内滚，有意设计）；手牌扇形 span 随 clientWidth 收（10 牌 @1024 总宽 ≈ 744 < 996）；hover 上浮是 absolute 定位不撑容器。
- 风险点：**#card-detail 定宽 304px、absolute right、max-height calc(100%-112px)** —— 1024 宽下覆盖战斗梁右缘约 30%，压住日志右侧与敌人区右端（T53 设计前提是 1240 梁「不遮战斗」，1024 下前提变窄）。**不产生滚动条，但遮挡程度需实测**；1280×720 已实测 10 手牌+信息区同屏无整页滚动条（T71）。
- 640 高静态纵向核算：HUD ~51 + 敌区 ≥150 + 日志 ≥60 + 手牌区 ~300 ≈ 561–594 < 640 ✓（协议横幅出现再 +33 仍放得下）。

### 4.5 奖励屏（#flow-cards）—— **自适应 ✓**
- 机制：flex-wrap wrap、卡 190×267 固定；1024 下 5 张起换行，`#screen-flow` 内滚兜底。
- 风险点：无（换行 + 内滚双兜底）。

### 4.6 商店屏（.shopgrid）—— **自适应 ✓**
- 机制：`repeat(auto-fill, minmax(200px,1fr))` + max-width 880；1024 下 4 列；条目多走 `#screen-flow` 内滚。
- 风险点：无。

### 4.7 营火屏（.campopt）—— **自适应 ✓**
- 机制：块级选项 max-width 640 居中、纵排；`#screen-flow` 内滚。T76 实测三主题色条/对比度正常（1280×720）。
- 风险点：无。

### 4.8 结算屏（.ending / .statline / .relicrow）—— **自适应 ✓**
- 机制：ending 盒 pre-wrap 左对齐、relic 徽记 inline-block 自动换行；`#screen-flow` 内滚；立绘 .ending-art 210×300 固定（< 640 可容）。
- 风险点：无。

### 4.9 浮层组（总图 #fullmap-layer / 速查 #help-page / 通用 #overlay / toast / phase-banner）—— **自适应 ✓**
- 机制：全部 `position:fixed + min()/max-vw/vh 双钳制 + 内部滚动`（总图 fm-svg 88vw×min(70vh,780)、缩放 0.6–2×、拖拽平移）；toast/banner max-60~70vw。
- 风险点：无。T71 实测总图滚动/缩放三法全过（1280×720）。

### 4.10 旧图回退通道（`?map=old`）—— **风险（1024 档横向裁切）**
- 机制：老版 #map 纵向 column-reverse + `.maprow` 横排 gap150、节点 140px 定宽；**无 overflow-x 兜底**（#screen-flow 只有 overflow-y）。
- 风险点：**1024×640**：单行 5 节点需 1380px，横向被 body `overflow:hidden` 裁切，右端节点不可达。1280 档单行 5 节点 1380 > 1280 同样裁切（此通道在 1280×720 也未实测过）。**依据**：纯 CSS 定宽算术；缓解事实：默认新图，此通道仅回退用，且 T71 记录 `?map=old` 回退「老图渲染、新模块不注入」只验证过能渲染，未验证过窄视口。

## 5. 引用的既有实测证据（TASK_DONE.md，全部 1280×720 · IAB）

- **T71**（:591-598）：居中态格子 43×26.6/节点 Ø22.4、`fillsDock=true、blankPct=0、pageScrollbar=false`（10 手牌+小图+右侧信息区同屏 1280×720 精确）；总图滚动/缩放 0.6–2× 截图 6 张（docs/shots_t71/）。
- **T74**（:599-602）：选择态 dock top96 不遮标题、战斗态 10 手牌+右上小图+行程列表同屏 `pageScrollbar=false`（截图 docs/shots_t74/）；`renderMiniMap` 格子 <10px 只显当前带的自适应在案。
- **T74.1**（:603-607）：最终版布局实测——选择态 dock {left:150, top:274, right:1130, bottom:706, 980×432}、titleBottom 101 < 274、`pageScrollbar=false`；事件屏 dockVisible=false；战斗屏 dockMode=hidden 无整页滚动条；奖励/战斗中 Tab 呼出总图 + Esc 关闭（截图 04–06）。
- **T76**（:621-）：事件/营火 × off/A/B 三主题截图（docs/shots_t76/），选项纸片与暗底对比度全过。

## 6. 留人工的 1024×640 实测清单（本审计未做，静态推定不等价于实测）

1. **战斗屏**：选一张牌看 #card-detail 在 1024 宽下盖住日志/敌人区的实际面积，确认可接受或需要让路方案。
2. **地图选择屏**：确认 dock（962×384）与标题、死路救援文案/按钮在 640 高下不相叠；行程列表内滚可用。
3. 常规回归：三档各走一遍 选择→地图→事件→战斗(10 手牌)→奖励→商店→营火→结算，核对无整页滚动条（可复用 T74.1 的 pageScrollbar 探针）。

## 7. 未解决

- 上表 §6 三项：本任务为只读审计不改码，1024×640 无实测手段，**未解决，留人工实测**。
- 旧图回退通道窄视口横向裁切（§4.10）：属回退通道的已知局限，本次未修（修需动 web/，超出只读审计边界）。
