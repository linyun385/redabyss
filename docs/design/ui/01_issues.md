# UI 问题清单（28 条，全量）

> 来源=00_inventory.md 十区域的「已知问题」段。每条一行。排序：P0 先，同级按影响界面数降序。
> 严重度定义：**P0**=卡住/看不懂该做什么/操作不了；**P1**=困惑/多操作一次/误读；**P2**=观感或不一致。

| ID | 区域 | 问题 | 证据 | 严重度 | 修法方向 |
|---|---|---|---|---|---|
| UI-001 | 2 HUD | `overflow:hidden` + `flex-wrap:wrap` 在 <1000px 视口下第二行 HUD 被裁切，生命/能量不可见 | :88 `overflow:hidden` + :90 `flex-wrap:wrap` | **P0** | 去 `overflow:hidden`，改 `overflow:visible` 或 min-height 自适应 |
| UI-002 | 3 敌人 | 穿透/镜像/drain_discard 意图无视觉区分——与普通攻击同一 `.i-atk` 红色样式 | :139-140 CSS 只有 `.i-atk`/`.i-def` 两色；render() 敌人构建无 pierce/mirror class | **P0** | 按 intent 附加属性（pierce/mirror/drain）加独立 CSS class + 图标 |
| UI-003 | 4 手牌 | 带目标牌无键盘路径——pending 态敌人有 `.targetable` 但键盘不可达 | :7977 startCardPointer 仅绑 pointer 事件；UI.md T28 #17 | **P0** | pending 态下数字键 1-5 转发给敌人索引 |
| UI-004 | 8 营火 | 升级预览走 `d.title` 属性——移动端不可达、键盘不可达 | :6763 `d.title = '升级预览：…'` | **P0** | 升级预览渲染进 DOM（overlay 面板或 card-detail） |
| UI-005 | 2 HUD | 零件值 `cursor:pointer` 无视觉指示——玩家不知道可点击 | :843 inline `cursor:pointer` 无其他样式 | P1 | 悬停时加下划线/变色，或首次 >0 时加一次提示 |
| UI-006 | 3 敌人 | weak/frail/burn/poison 状态无可视化——只有文本拼接在 intent 行内 | :7837 `(e.status.weak ? '　虚弱' : '')` 文本拼接 | P1 | 为每种状态加图标+颜色 span |
| UI-007 | 4/5 卡详情 | 升级后效果预览缺失——只写「可以在营火升级」不显示差量 | :8095 `osub` 一行 vs :6760-6765 营火有完整 `upgradeCard()` 预览 | P1 | 在 `#cd-lines` 里追加 `upgradeCard()` 的差量文本 |
| UI-008 | 5 卡详情 | needsTarget 说明缺键盘路径信息——只写「拖到敌人身上」不提键盘 | :8090 needsTarget osub 文本 | P1 | 与 UI-003 联动：修完键盘选目标后更新说明文本 |
| UI-009 | 6 日志 | 无自动滚动到底——renderLog 重建后无 scrollTop=scrollHeight | :8540-8560 renderLog 函数体无 scrollTop 操作 | P1 | renderLog 末尾加 `wrap.scrollTop = wrap.scrollHeight` |
| UI-010 | 6 日志 | 引擎「效果未实现」红字走普通 log 行——与普通信息行无视觉区别 | applySpecial default 分支的 log 不带 type 参数 | P1 | default 分支 log 加 type='blocked'（复用 .blocked 样式） |
| UI-011 | 8 事件 | 禁用选项的 requires 说明走 title——移动端/键盘不可达 | :7395-7398 `b.title = '该脉的牌不够…'` | P1 | disabled 时在 .osub 里显示原因而非 title |
| UI-012 | 8 商店 | .cant/.sold 无 disabled 属性——键盘 Tab 可聚焦但 Enter 无反应 | :6847-6860 click handler JS return，无 disabled | P1 | 加 `disabled` attribute 或 `tabindex=-1` |
| UI-013 | 9 奖励 | 跳过按钮无确认——误触即放弃三选一 | :7285-7287 skip.addEventListener 直接 onDone | P1 | 加二次确认 toast 或按住 1s |
| UI-014 | 10 全局 | 字号缩放只改 body fontSize 百分比——卡牌/敌人/地图用 px 固定，缩放不影响它们 | :8373-8381 body.style.fontSize + grep data-fs CSS=0 处 | P1 | 卡牌字号改用 `em`/`rem` 或加 `.card { font-size: inherit }` |
| UI-015 | 1 选人 | 模态 max-height 86vh 在 720p 下 detail 区可能出滚动条 | :63 max-height:86vh + :68 overflow-y:auto | P2 | 无需修——滚动是正确行为 |
| UI-016 | 1 选人 | 职业卡无方向键导航——只有 Tab 原生 | DOM 顺序即焦点顺序 | P2 | 可加 ArrowLeft/Right 循环 |
| UI-017 | 2 HUD | 层数行 #hud-layer 无分隔样式——与 10 个数值混排 | :849 无独立 class | P2 | 加 `border-left` 或 `margin-left: auto` |
| UI-018 | 3 敌人 | 6+ 敌人时 overflow-x 出滚动条（当前最大 5 只不会触发） | :121-124 .enemy width 230px 固定 | P2 | .enemy 可加 `flex-shrink: 1; min-width: 180px` |
| UI-019 | 4 手牌 | #hand 高度 238px 硬编码 | :189 | P2 | 可改 `height: auto; min-height: 238px` |
| UI-020 | 4/5 手牌 | hover 卡牌 z-index 99 覆盖 #card-detail z-55 | :246 vs :258 | P2 | 设计意图（悬停卡比详情重要）——维持 |
| UI-021 | 7 地图 | 小图只在地图选择态显示 | :679-681（T74.1 设计决定） | P2 | 维持 |
| UI-022 | 9 奖励 | 三选一卡无 hover 效果差异 | :201 `:not(.dimmed)` 条件覆盖 ✅ | P2 | 无需修 |
| UI-023 | 10 全局 | --lane 1240px 硬编码 | :41 | P2 | 可改 `min(1240px, 95vw)` |
| UI-024 | 10 全局 | z-index 100（dragging）> 95（modal） | :252 vs :60 | P2 | 战斗中 exclusive——维持 |
| UI-025 | 10 全局 | prefers-reduced-motion 覆盖 glowbreath 遗漏 | :517-524 未列 `.mnode.pickable` 的 glowbreath | P2 | 追加到 reduce 列表 |
| UI-026 | 1 选人 | 模态 max-height 86vh 720p 下可能出滚动条 | :63 | P2 | 滚动是正确行为 |
| UI-027 | 4/5 卡详情 | needsTarget 说明缺键盘信息 | :8090 | P2 | 与 UI-008 重复 → 合并 |
| UI-028 | 5 卡详情 | cd-close z-index 无声明但安全 | :262-265 | P2 | 无需修 |
