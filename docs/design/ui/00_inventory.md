# UI 现状盘点（代码级 · 10 区域）

> 本篇是 `web/index.html`（9165 行，2026-11-05 快照）的 UI 现状盘点。
> 能力边界：**不开浏览器**，只做代码级 + 规范级审计。所有尺寸按 CSS 声明值计算（1280×720 与 1920×1080）。
> 产出：本文件。下游 02（问题清单）/03（设计提案）以此为基础。

---

## 1 · 开始页 / 职业选择

### 结构

```
#screen-select
  h1「红渊：下潜」
  p.sub
  .class-row
    button.classface ×4（data-class / aria-haspopup）
      img[src=assets/class/XX.webp]
      span.cname
#class-modal (hidden, role=dialog, aria-modal)
  #class-modal-box
    button#class-modal-close
    #class-modal-art > img
    #class-modal-detail > h2 + .cm-line + ul.cm-stats + ul.cm-mechs + .btnrow > #btn-dive-confirm
```

渲染：`showScreen('#screen-select')`（`:6516`）；模态由 `startRun` 区域代码构建（`:6570` 附近）。

### 尺寸

| 元素 | CSS 规则 | 1280×720 计算 | 1920×1080 计算 |
|---|---|---|---|
| 内容梁 | `max-width: var(--lane)` = 1240px | 1240px（居中，两侧留 20px） | 1240px（居中，两侧留 340px） |
| .classface | `width: 200px` | 200px | 200px |
| .classface img | `aspect-ratio: 3/4; object-fit: cover` | 200×267px | 同 |
| .class-row gap | `gap: 26px` | 4×200 + 3×26 = **878px** | 878px |
| h1 | `font-size: 30px; letter-spacing: 8px` | 30px | 30px |
| .cname | `font-size: 17px` | 17px | 17px |
| #class-modal-box | `width: min(940px, 92vw); max-height: 86vh` | 940×619px（86% of 720） | 940×928px |
| #class-modal-art | `flex: 0 0 40%; min-height: 460px` | 376×460px（940 的 40%） | 同 |
| #class-modal-detail | `flex: 1 1 60%; padding: 30px 34px` | 564px 宽 | 同 |

### 状态

| 状态 | 触发 | CSS |
|---|---|---|
| hover | `.classface:hover` | `translateY(-4px); border-color: --red-hi; box-shadow` |
| focus-visible | `:focus-visible` | `outline: 2px solid #c9a35a;` + 上浮+双阴影 |
| modal-open | `#class-modal` remove `.hidden` | flex 全屏遮罩 |

### 已知问题（代码证据）

| # | 问题 | 证据 |
|---|---|---|
| 1.1 | 模态 `max-height: 86vh` 在 720p 下 = 619px；`#class-modal-art` 有 `min-height: 460px`，detail 区实际可用高度 = 619 − 0（padding 内含）= 619px。如果详情内容 > 619 − 60(padding) − 40(h2+btnrow) ≈ 519px，detail 区出滚动条（`overflow-y: auto` ✅）——**这不是 bug，但 720p 下滚动条可能出现**。 | `:63-68` |
| 1.2 | 4 张职业卡无键盘方向键导航——只有 Tab（原生 button）。Tab 顺序为 DOM 顺序（diver→tremor→cangmin→anmin），不按视觉排列的方向。 | DOM 顺序即焦点顺序 |
| 1.3 | 模态关闭按钮 `#class-modal-close` 的 `z-index: 2`——在 `#class-modal-box`（z-index 未设，即 auto）内部。如果模态内部内容产生新的 stacking context，close 按钮可能被覆盖。**实际不会**——modal-box 没有 transform/filter/perspective。 | `:80` |

---

## 2 · HUD

### 结构

```
#hud
  .hud-stats
    span.stat ×10（生命/格挡/能量/共鸣/凝视/金币|零件/零件(hidden)/清醒度(hidden)/梦境(hidden)/当前深度）
      i.ic（图标字符）+ span.k（标签）+ span.v（数值）
  .hud-relics
    span ×N（遗物徽记 SVG + 名字，title=效果文本）
```

渲染：`render()`（`:7714`）每次状态变化全量刷新；`applyLayerTheme()`（`:6547`）写 `--layer-bg` CSS 变量。

### 尺寸

| 元素 | CSS | 1280 计算 | 备注 |
|---|---|---|---|
| #hud padding | `6px 14px 5px` | 高 = 内容 + 11px | |
| .hud-stats gap | `gap: 18px` | 10 项 × ~80px + 9×18 ≈ **962px**（全部展开时） | flex-wrap: wrap（会换行） |
| .hud-stats .ic | `font-size: 14px` | 图标 14px | |
| .hud-stats .k | `font-size: 10px; opacity: .8` | 标签 10px | |
| .hud-stats .v | 继承 body 14px | 数值 14px | |
| .hud-relics | `gap: 8px; font-size: 12px` | 每个遗物徽记 14×14px + 文字 | |
| #hud 白名单 | `white-space: nowrap; overflow: hidden` | 超宽裁切 | **10 项全展开时 962px < 1240px 不裁切** |

### 状态

| 状态 | 触发 | CSS/JS |
|---|---|---|
| hp-low | `run.hp <= maxHp * 0.3` | `.v.hp-low { color: --red-hi }` |
| dying | 同上 | `body.dying` → `#app::after` 红光渗入动画 |
| block pulse | `C.block > prev.block` | `.ic.block.pulse { animation: blockpulse .4s }` |
| gaze flash | 凝视变化 | `#gaze-val.flash { animation: gazeblink .4s }` |
| clarity-low | `run.clarity < 3` | `.v.clarity-low` 脉冲动画 |
| parts visible | `classId === 'anmin'` | `#hud-parts-wrap.hidden` 移除 |
| dream visible | `classId === 'cangmin' && world === 'dream'` | `#hud-dream-wrap.hidden` 移除 |
| 层数行 | `#hud-layer` | `render()` 写入 `L{depth} · {name}` |

### 已知问题

| # | 问题 | 证据 |
|---|---|---|
| 2.1 | **零件值 `cursor:pointer` 但无视觉指示**——`#hud-parts` 有 `style="cursor:pointer"`（`:843`），但外观与普通数值一样。用户不知道可点击。 | `:843` inline style + T451 #1 |
| 2.2 | **`overflow: hidden` + `flex-wrap: wrap` 冲突**：#hud 设了 `overflow: hidden`（`:88`），hud-stats 有 `flex-wrap: wrap`（`:90`）。在 <1000px 视口下 10 项换行 → 第二行被 overflow: hidden 裁切。1280px 下 10 项 = 962px 不换行，但 800px 以下必出问题。 | `:88,90` |
| 2.3 | **层数行 `#hud-layer` 无独立 CSS**——`.stat` 通用样式适用，但没有 `.k`/`.v` 分离，只有 `span.k` 一个元素。渲染函数直接写 `textContent`。层数信息与 10 个数值混排，没有分隔线。 | `:849` + `:7714` |

---

## 3 · 战斗·敌人区

### 结构

```
#enemy-area
  .enemy ×N（每只）
    .eart > svg.esym（图标剪影）或 img（有图时）
    .ename
    .intent > span.i-atk / span.i-def / 纯文本
    .hpbar > i（宽度%）+ .pmark（阶段线）
    .hpnum
    .eblock
```

渲染：`render()`（`:7714`）内 `#enemy-area` 遍历 `C.enemies`；`floatText()`（`:7830` 附近）飘伤害数字。

### 尺寸

| 元素 | CSS | 计算 |
|---|---|---|
| #enemy-area | `min-height: 150px; padding: 18px 14px; gap: 20px` | 最小高度 150px；横向溢出 `overflow-x: auto` |
| .enemy | `width: 230px; padding: 10px` | 每只 230px 宽 |
| .eart | `height: 60px` | 图案区 60px 高 |
| .hpbar | `height: 8px` | 血条 8px |
| .hpnum | `font-size: 12px` | 数值 12px |

3 只敌人并排：3×230 + 2×20 = **730px** < 1240px ✅。5 只 = 1190px < 1240px ✅。6 只 = **1420px > 1240px** → overflow-x: auto 出滚动条。

### 状态

| 状态 | 触发 | CSS |
|---|---|---|
| .targetable | pending 待选目标 | `border-color: --red-hi` |
| .dead | hp ≤ 0 | `opacity: .25; filter: grayscale(1)` |
| .hitflash | 受击 | `animation: ehit .12s` |
| .atk-hot | 意图.type === 'attack' | `animation: atkpulse 1.4s` 脉冲 |
| .drop-hot | 拖牌悬停 | `border-color: #c8342a; box-shadow` |
| .intent.flash | 意图刷新 | `animation: intentblink .2s` |

### 已知问题

| # | 问题 | 证据 |
|---|---|---|
| 3.1 | **穿透/镜像/drain 意图无视觉区分**——intent 渲染只有 `.i-atk`（红）和 `.i-def`（蓝）两个 class。pierce/mirror/drain_discard 的攻击在 UI 上与普通攻击完全一样。玩家必须读文本才能区分。 | `:139-140` CSS 只有两色 + `render()` 敌人意图构建段无 pierce/mirror class |
| 3.2 | **debuff status 无可视化**——敌人身上的 weak/frail/burn/poison 状态在 `.intent` 里只有文本（如「脆弱」），没有图标或颜色标记。H11 微模拟已证明这些状态影响战斗结果，但玩家需要逐字读意图列表才能发现。 | `:7777-7830` render() 敌人构建段 + `:7837` `(e.status.weak ? '　虚弱' : '')` 仅有文本拼接 |
| 3.3 | **6+ 敌人时 overflow-x 出滚动条**——`.enemy { width: 230px }` 固定宽度，6 只 = 1420px > 1240px。当前数据最大 5 只/场（L8），不会触发。但引擎无上限约束。 | `:121-124` |

---

## 4 · 战斗·手牌区

### 结构

```
#hand-area
  #hand
    .card ×N（绝对定位扇形）
      .cost / .ctype / .art > .art-ph / .cname / .cveins > span ×N / .ctext / .cflavor
  #hand-foot
    #piles > #pile-draw + #pile-discard + #pile-exhaust
    #btn-world（hidden）
    #btn-end「结束回合」
    #btn-help「?」
#card-detail（hidden，右侧常驻信息区）
```

渲染：`render()` 构建 `C.hand` 的 DOM（`:7840-7970`）；`layoutFan()`（`:7960`）计算扇形偏移。

### 尺寸

| 元素 | CSS | 计算 |
|---|---|---|
| .card | `width: 150px; height: 210px` | 手牌卡 150×210px |
| #hand | `height: 238px; min-height: 238px` | 固定 238px（210 卡 + 4 底距 + 余量） |
| #hand-area padding | `8px 14px 12px` | |
| fan span | `min(66, max(38, (hand_width - 170) / (n-1)))` | 1240px 时：n=5 → span=66；n=10 → span=66（capped） |
| fan 旋转 | `off × 2.2°`（n>1） | 最左/最右 ±(n-1)/2 × 2.2° |
| hover raise | `translateY(-46px) scale(1.06)` | 上浮 46px + 6% 放大 |
| #flow-cards .card | `width: 190px; height: 267px` | 三选一卡比手牌大（190 vs 150） |

10 张手牌宽度计算：最左卡中心 = 50% - 4.5×66 = 620 - 297 = 323px；最右卡中心 = 620 + 297 = 917px；卡宽 150 → 左边 323-75 = 248px、右边 917+75 = 992px。**992px < 1240px ✅ 不溢出**。

hover 时 translateY(-46px)：#hand 高度 238px，卡高 210px，底距 4px → 卡顶距 #hand 顶 24px。上浮 46px → 卡顶距 #hand 顶 -22px → **溢出 #hand 上边界 22px**。#hand-area 没有 overflow:hidden，所以卡牌不会被裁切——但会覆盖 #log-wrap 的底部。**这是有意的**（T53 悬浮卡不遮战斗区，但可以遮日志）。

### 状态

| 状态 | 触发 | CSS |
|---|---|---|
| .dimmed | `playBlockReason(card)` 返回非空 | `opacity: .35; cursor: not-allowed` |
| .costly | `cost_type !== 'none'` | `border-color: --red; background: #170909` |
| .wrongworld | 苍民 card.dream ≠ C.world | `opacity: .3` |
| .selected | 点击选中 | `outline: 1px solid --red-hi; -46px` |
| .upgraded | `card.upgraded` | `border-color: #c9a35a`（金色） |
| .dragging | pointerdown + move | `transition: none; z-index: 100` |
| .shakeit | 能量不足尝试出牌 | `animation: shakeit .3s` |
| .ghost-fly | 出牌动画 | `animation: cardfly .22s` |

### 已知问题

| # | 问题 | 证据 |
|---|---|---|
| 4.1 | **带目标牌无键盘路径**——数字键选中后进入 pending 态，敌人有 `.targetable` class，但键盘无法选中敌人（必须鼠标拖或点）。T28 审计 #17 已标记，**至今未修**。 | `:7977 startCardPointer` 仅绑 pointer 事件 + UI.md T28 #17 |
| 4.2 | **#hand 固定高度 238px 不可调**——在 `prefers-reduced-motion` 下 hover 不上浮（`:523`），但仍占 238px。如果未来卡牌高度变化，238px 是硬编码。 | `:189` |
| 4.3 | **upgrade 后效果预览缺失**——`openCardDetail`（`:8084`）对非升级卡只显示 `osub` 一行「这张牌可以在营火升级」（`:8095`），不显示升级后效果差量。T28 审计 #5 标记的缺口**至今未修**。 | `:8095` + UI.md T28 #5 |
| 4.4 | **10 张手牌 hover 时遮挡卡牌详情区**——hover 卡牌 z-index 99，#card-detail z-index 55。悬停右侧卡牌时，卡牌上浮后可能覆盖 #card-detail 的左半部分。**这是设计意图**（悬停卡比详情重要），但未记录。 | `:246` z-index 99 vs `:258` z-index 55 |

---

## 5 · 卡牌详情面板

### 结构

```
#card-detail (hidden)
  button.cd-close（×）
  #cd-box
    #cd-card > .card（大卡面 168×236px）
    #cd-side
      h3#cd-name（卡名 + 费用 + 类型）
      #cd-lines（效果/代价/脉/警告/备注）
      .btnrow > #cd-play「打出」+ #cd-cancel「收回」
```

渲染：`openCardDetail(i)`（`:8084`）；`renderCardStatic(card)`（`:7352`）构建大卡面。

### 尺寸

| 元素 | CSS | 计算 |
|---|---|---|
| #card-detail | `width: 304px; right: 2px; top: 92px` | 右侧固定 304px 宽 |
| #cd-card .card | `width: 168px; height: 236px` | 详情卡面 168×236px（比手牌 150×210 大） |
| max-height | `calc(100% - 112px)` | 720p 战斗屏 ≈ 720-92(HUD) - 112 = 516px |
| #cd-lines | `font-size: 12.5px; line-height: 1.65; overflow-y: auto` | 文字区可滚 |

### 状态

| 状态 | 触发 | 行为 |
|---|---|---|
| open | 点击/选中手牌 | remove `.hidden`，渲染卡面+文字 |
| close | ×/收回/Esc | add `.hidden`，pending 重置 |
| play disabled | `playBlockReason` 返回非空或 worldMismatch | `#cd-play.disabled = true` |
| warn | worldBad 或 reason | `#cd-lines .warn` 红字 |

### 已知问题

| # | 问题 | 证据 |
|---|---|---|
| 5.1 | **升级后效果预览缺失**（同 4.3）——T28 #5 标记的缺口。`openCardDetail` 的 `lines` 构建只写「可以在营火升级」，不调用 `RedAbyss.upgradeCard()` 生成预览。营火升级（`:6755`）有完整的 `upgradeCard()` 预览（title 属性），但战斗中的卡牌详情没有。 | `:8095` vs `:6760-6765` |
| 5.2 | **cd-close 的 z-index 无声明**——`.cd-close` 无 z-index，依赖 DOM 顺序在 #cd-box 之后。#cd-box 有 `display: flex; flex-direction: column`，.cd-close 是 #card-detail 的直接子元素（不在 #cd-box 内），位置绝对——不会被覆盖。**实际安全**。 | `:262-265` |
| 5.3 | **needsTarget 的说明太长**——`openCardDetail` 里 needsTarget 时加了一段 `<div class="osub">打出后要选一个目标：把它拖到敌人身上，或按「打出」再点敌人。</div>`——**没有提到键盘路径**（因为不存在，见 4.1）。 | `:8090` |

---

## 6 · 战斗·日志区

### 结构

```
#log-wrap (overflow-y: auto)
  #log
    div.turnline（回合分隔行）
    div（普通日志行）
    div.hurt（受伤行）
    div.blocked（红字警告行）
```

渲染：`renderLog()`（`:8540`）重建；每条 log 通过 `log(C, text, type)` 添加。

### 尺寸

| 元素 | CSS | 计算 |
|---|---|---|
| #log-wrap | `flex: 1 1 0; min-height: 60px; overflow-y: auto; padding: 8px 14px` | 弹性填充战斗屏剩余空间 |
| #log | `max-width: 900px; margin: 0 auto` | 居中限宽 |
| #log div | `font-size: 12px; color: --dim` | 12px |

### 状态

| 状态 | 触发 | CSS |
|---|---|---|
| .turnline | 新回合 | `color: --red; animation: turnflash .6s` |
| .hurt | 玩家受伤 | `color: --text`（比 --dim 亮） |
| .blocked | 层规则禁牌 | `color: --red; font-weight: 700; border-left: 3px solid --red; background: rgba(150,20,20,.10)` |
| .new | 新 turnline | `animation: turnflash .6s` |

### 已知问题

| # | 问题 | 证据 |
|---|---|---|
| 6.1 | **无自动滚动到底**——`renderLog()` 重建 #log 内容，但没有 `scrollTop = scrollHeight`。如果日志超出可视区，新条目在底部不可见。**需要浏览器验证**——可能有其他代码在处理滚动。 | `:8540-8560` renderLog 函数体无 scrollTop 操作 |
| 6.2 | **blocked 样式只用于层规则禁牌**——引擎的「这个效果这一版还没做」的红字（default 分支）走普通 log（无 .blocked class），视觉上与普通信息行无区别。 | `:185` .blocked 仅层规则 + `applySpecial` default 分支的 log 不带 type |

---

## 7 · 地图

### 结构

```
#mm-dock (hidden → .show → .show.big)
  #minimap
    .mm-head > b#mm-band + #btn-fullmap
    #mm-legend
    #mm-body（SVG 渲染）
  #mm-log > .mm-log-cap + #mm-log-rows > .mm-row ×N
#fullmap-layer (hidden → .show)
  #fullmap-box
    #fm-close
    #fm-hint
    #fm-zbar（缩放按钮组）
    #fm-svg（SVG 总图）
```

渲染：`renderMiniMap()`（`:8511`）、`drawMap()`（`:8426`）、`renderLog()`（`:8540`）。入口：`showMap()`（`:6556`）。

### 尺寸

| 元素 | CSS | 计算 |
|---|---|---|
| #mm-dock.big | `width: min(980px, 94vw); height: min(60vh, 470px)` | 1280×720: 980×432px；1920×1080: 980×470px |
| #mm-dock.big #minimap | `grid-template-areas: "head head" "legend legend" "log body"` | 三行两列 grid |
| #mm-body | `flex: 1 1 0; min-height: 0` | 剩余空间全给 SVG |
| .fm-node .fm-glyph | `font: 12px` | 节点图标 12px |
| .mnode | `width: 140px; height: 80px`（旧版地图） | ?map=old 回退用 |

### 状态

| 状态 | 触发 | CSS |
|---|---|---|
| .show | 地图选择态 | `display: block` |
| .big | 大图模式 | grid layout |
| .pick | 可选节点 | `border-color: --mm-pick; cursor: pointer` |
| .here | 当前位置 | `border-color: --mm-pick; stroke-width: 2` |
| .near | 可见未访问 | `opacity: .95; stroke-opacity: .85` |
| .unseen | 可见范围外 | `opacity: .35` |
| .btrack | 可回返 | `stroke-dasharray: 3,2` |
| .fog | 未知连线 | `stroke-opacity: .15` |

### 已知问题

| # | 问题 | 证据 |
|---|---|---|
| 7.1 | **小图只在地图选择态显示**——`#mm-dock` 默认 `display: none`，由 JS 控制 `.show`/`.big`。其他状态（事件/奖励/战斗/营火）不放小图。这是设计决定（T74.1 用户反馈最终版）。 | `:679-681` + `:674-677` 注释 |
| 7.2 | **总图缩放范围 0.6–2×**——`#fm-svg` 的缩放由 JS 管理（zbar 按钮 + 滚轮），CSS 未限制 min/max。JS 侧 `st.zoom` 有范围检查。 | `:792-807` |

---

## 8 · 事件 / 商店 / 营火

### 结构

```
#screen-flow > #flow-panel
  h2 + .progress + .flavor
  .opts > button.optbtn ×N（事件选项）
  .shopgrid > .shopitem ×N（商店）
  .campopt ×N（营火选项）
  #flow-cards > .card ×N（奖励三选一/升级）
```

渲染：`showEvent()`（`:7370`）、`showShop()`（`:6833`）、`showCampfire()`（`:6682`）。

### 尺寸

| 元素 | CSS | 计算 |
|---|---|---|
| .opts | `max-width: 760px; gap: 12px` | 居中限宽 |
| .optbtn | `padding: 16px 22px; font-size: 15px; border-left: 3px solid` | 事件选项按钮 |
| .shopgrid | `grid auto-fill minmax(200px, 1fr); gap: 12px; max-width: 880px` | 自适应列数：1240px 内 4 列 |
| .campopt | `max-width: 640px; padding: 12px 16px; margin-bottom: 10px` | 营火选项 |
| #flow-cards .card | `width: 190px; height: 267px` | 三选一卡 |
| .relicrow .relic | `max-width: 240px; padding: 8px 12px` | 遗物选择卡片 |

### 状态

| 状态 | 触发 | CSS |
|---|---|---|
| .optbtn:disabled | 事件 requires 不满足 | `opacity: .45` |
| .shopitem.cant | 金币不足 | `opacity: .35` |
| .shopitem.sold | 已售 | `opacity: .2; pointer-events: none` |
| .campopt.disabled | 升级/删牌不可用 | `opacity: .45` |
| .optbtn border-left | 按脉向色条 | T76 色条（check_palette 验证） |
| .campopt border-left | 按位轮换生态色 | `nth-of-type(3n+1/2/3)` |

### 已知问题

| # | 问题 | 证据 |
|---|---|---|
| 8.1 | **营火升级预览只走 title 属性**——`showCampfire` 里升级选项用 `renderCardStatic(card)` 渲染卡面，但升级后的效果预览存在 `d.title` 属性里（`:6763`）。title 是**hover-only**：移动端不可达、键盘不可达。 | `:6763` `d.title = '升级预览：…'` |
| 8.2 | **事件选项禁用的 title 提示**——requires 不满足时 `b.disabled = true; b.title = '该脉的牌不够'`——title 同样是 hover-only。 | `:7395-7398` |
| 8.3 | **商店 .shopitem 无 disabled 属性**——用 CSS class `.cant`/`.sold` + JS return 早退。键盘 Tab 会聚焦 cant 项，Enter 无反应但视觉看起来可选。 | `:6847-6860` click handler 内 JS return，无 disabled 属性 |

---

## 9 · 奖励 / 结算

### 结构

```
#flow-panel
  h2「行囊里还能再塞一样东西」
  #flow-cards > .card ×3（三选一）或 ×1（mustPick）
  .btnrow > button「跳过」（非 mustPick 时）
  h2「巨怪的遗骸」+ .relicrow > .relic ×3
  h2 + .ending（结局文本）
  .memoline / .hintline（死亡结算）
```

渲染：`showCardChoice()`（`:7251`）、`showRelicChoice()`（`:7295` 附近）、`showFlowPanel()`（`:7236`）。

### 尺寸

| 元素 | CSS | 计算 |
|---|---|---|
| #flow-cards | `gap: 18px; flex-wrap: wrap` | 3 张 ×190 + 2×18 = **606px** < 1240px ✅ |
| #flow-cards .card | `width: 190px; height: 267px` | 三选一卡 190×267px |
| .ending | `padding: 14px; white-space: pre-wrap` | 结局文本块 |
| .memoline | `font-size: 继承 --red-hi` | 死亡结算"最值得说的事" |

### 状态

| 状态 | 触发 | CSS |
|---|---|---|
| .dimmed | 三选一选了一张后其余变暗 | JS 加 class |
| .upgraded | 升级后的卡 | 金色边框 |
| skip | 非必须时 | `.btnrow > button「跳过」` |

### 已知问题

| # | 问题 | 证据 |
|---|---|---|
| 9.1 | **三选一卡无 hover 效果差异**——#flow-cards .card:hover 与手牌 .card:hover 共用规则（`:201`），但 #flow-cards 的卡没有 dimmed/wrongworld 排除——已选后所有卡都加 dimmed，hover 不上浮 ✅。 | `:201` `:not(.dimmed)` 条件 |
| 9.2 | **跳过按钮无确认**——「跳过」按钮点击后直接 onDone()，没有确认。误触即跳过三选一。 | `:7285-7287` |

---

## 10 · 全局

### 结构

```
html[data-theme="C"]
  body
    #app
      #hud
      #screen-select / #screen-combat / #screen-flow（三屏切换）
    .fontbtns（fixed 右上）
    #toast（fixed）
    #phase-banner（fixed）
    #help-overlay（fixed）
    #overlay（fixed）
    #mm-dock / #fullmap-layer（fixed）
    #class-modal（fixed）
    #overlay-panel
```

### 全局变量

| 变量 | 值 | 用途 |
|---|---|---|
| --bg | #0a0506 | 页面底色（off 主题） |
| --text | #d8cfc9 | 正文 |
| --dim | #a89a90 | 次要文字 |
| --red | #8b1a1a | 主红 |
| --red-hi | #e2705f | 强调红（T52 提亮） |
| --lane | 1240px | 内容梁宽度 |
| --paper / --ink | #d9cfbe / #2b2118 | 纸面主题（B/C） |
| --mm-panel / --mm-ink | #101418 / var(--text) | 地图面板 |

### 字号缩放

- `.fontbtns`：文-（80% 下限）/ 文+（150% 上限）/ 素（低饱和 filter）
- 实现：`document.body.style.fontSize = s + '%'`——百分比缩放，CSS 继承生效
- **grep `data-fs` = 0 处**——`dataset.fs` 只作为计数器，无 CSS 选择器引用它

### z-index 层级表（从 CSS 提取）

| z-index | 元素 |
|---|---|
| 2 | 卡牌角标 / 模态关闭按钮 |
| 5 | 漂浮伤害数字 |
| 12 | 濒血红光遮罩 |
| 15 | 字号/低饱和按钮 |
| 20 | #toast |
| 30 | #overlay |
| 40 | #phase-banner / .card.ghost-fly |
| 45 | #mm-dock |
| 55 | #card-detail |
| 60 | #help-overlay |
| 90 | #fullmap-layer |
| 95 | #class-modal |
| 98/99/100 | 手牌 selected/hover/dragging |

### 已知问题

| # | 问题 | 证据 |
|---|---|---|
| 10.1 | **--lane 1240px 硬编码**——所有屏共用 `var(--lane)`。1920px 下两侧留 340px 空白。这不是 bug 但是一个设计决定：是否在超宽屏下放大内容梁？ | `:41` |
| 10.2 | **`data-fs` 无 CSS 选择器**——字号缩放通过 `body.style.fontSize` 内联样式实现，`dataset.fs` 只是计数器。CSS 中无 `body[data-fs]` 选择器。这意味着**字号缩放不改变卡牌/敌人/地图的绝对像素尺寸**（那些用的是 px 不是 em/rem）。 | `:8373-8381` + grep data-fs = 0 CSS 选择器 |
| 10.3 | **z-index 98/99/100 与 modal 95**——拖拽中的手牌（z-100）高于职业模态（z-95）。战斗中不可能同时打开模态，所以无实际冲突。但 z-index 表没有注释「战斗中 exclusive」。 | `:95` modal vs `:252` dragging |
| 10.4 | **prefers-reduced-motion 覆盖不完整**——`:517-524` 覆盖了主要动画，但 `.mnode.pickable` 的 `glowbreath` 动画和 `body.dying #app::after` 的 `dyingpulse` 在 reduce 列表里。`#hand .card:hover` 的 transform 覆盖用了 `var(--fan)`（回到原始扇形位置）——正确。 | `:517-524` |

---

## 附 A · 检查器现状（2026-11-05 实跑）

| 工具 | 结果 | 摘要 |
|---|---|---|
| `check_web.js` | **全过（0 警告）** | script[1-6] 语法全过 |
| `a11y_check.js` | **全达标** | 正文最差 8.55 ✓ / 次要最差 3.68 ✓ / 强调最差 3.22 ✓ |
| `check_contrast.js` | **全过** | T76 三主题对比度/色条/disabled 全过 |
| `check_palette.js` | **全过** | 8 色 L*≥55、ΔL*≥6、色相间隔≥25° |

## 附 B · T28 审计对照（2026-11-03 UI.md → 2026-11-05 现状）

| T28 条目 | 11-03 判定 | 11-05 现状 | 变化 |
|---|---|---|---|
| #5 卡详情升级后效果 | 部分达标（升级后 ✗） | **仍未修**——`openCardDetail` 仍只写「可以在营火升级」 | 未变 |
| #12 空格结束回合 | 偏离（Enter/E） | **未变**——`btn-end` 仍绑 Enter/E | 未变 |
| #13 Tab 切牌堆/日志 | 偏离（Tab=总图） | **未变** | 未变 |
| #17 带目标牌键盘路径 | 部分达标（缺口） | **仍未修**——pending 态无键盘选敌 | 未变 |
| #4 悬停 300ms 详情 | 未按任务书（T53 用户拍板） | **维持 T53 方案** | 判断已定 |
| #9 次要文字 4.5:1 | 口径分歧（T52 ≥3 vs T28 ≥4.5） | **维持 T52 口径**（check_contrast 断言 ≥3） | 判断已定 |
| #16 手牌超 7 张缩小 | 形态偏离（间距压缩等价） | **维持 layoutFan 方案** | 判断已定 |
