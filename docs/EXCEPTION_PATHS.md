# EXCEPTION_PATHS — T265 异常路径审计（2026-11-03 夜班）

范围：`web/index.html`（9087 行，内含引擎副本）+ `engine/core.js`（993 行）。
方法：逐条找处理代码（防抖 / disabled / guard / try / 引擎重校验），只读不改。
计数：**已防护 17 / 部分 1 / 缺失 2**（共 20 条）。

结论一句话：UI 层靠「同步重绘销毁旧按钮」挡住了几乎所有连点；漏掉的两处正好都是**不被重绘销毁的常驻元素**（`#btn-end` 静态按钮、刷新行为本身）。

| # | 异常操作 | 处理位置 | 机制 | 判定 |
|---|---|---|---|---|
| 1 | 连点出牌 | index.html:6922 `doPlay`；:8050 `cd-play.onclick`；:7783 敌人点击；core.js:329 `playCard` | 单击手牌只开详情（:7960 `if (!dragging) { openCardDetail(i); return; }`），打出须拖拽或经 `cd-play`；`cd-play` 首次点击即 `box.classList.add('hidden')`；选目标态敌人点击有 `pending !== null` guard 且打出后 `pending=null`；引擎 `playCard` 对 over/牌存在/能量/凝视/共振/锁死逐条重校验并返回 `{ok:false}` | 已防护 |
| 2 | 连点结束回合 | index.html:6912 `#btn-end` click；core.js:617 `endTurn` | 仅 `if (!C || C.over) return`。`endTurn` 同步跑完整敌方回合，处理完才回来，**无防抖、无 disabled、无 busy 位**；`#btn-end` 是 HTML 静态按钮（:891），重绘不销毁它，双击=连跳两个玩家回合（敌方出手两次）。Enter/E（:8239）同路径 | **缺失** |
| 3 | 空手牌结束回合 | core.js:617-659 `endTurn`→`beginTurn`:229；`draw`:314 | 空手牌时弃牌循环为空操作，`draw` 里 `if (!C.drawPile.length) { if (!C.discardPile.length) break; }` 兜底，弃牌堆再洗回；无任何崩溃路径 | 已防护 |
| 4 | 0 血继续 | core.js:594-601 `damagePlayer`、:729 敌方攻击、:769 `checkCombatEnd`；index.html:7357 事件伤害；:7057 `finishCombatFlow` | 所有扣血路径统一在 hp≤0 时置 `C.over/result/dead` 并钳 0；战斗内全部入口（btn-end:6913、doPlay→playCard:330、pointerdown:7917、敌人点击:7782、键盘:8238）都查 `C.over`；`finishCombatFlow` 用 `phase !== 'combat'` 挡重复结算（:7058）；回返扣血 `Math.max(1, ...)`（:8787）不杀人 | 已防护 |
| 5 | 满手牌再抽牌 | core.js:317 `draw`（index 内联副本 :5633 同） | `if (C.hand.length >= HAND_LIMIT) break;`（HAND_LIMIT=10）；抽不下时牌留在抽牌堆，不丢失 | 已防护 |
| 6 | 地图死路点已访问格 | index.html:8731 `enterNode`、:8819 `backtrackTo`、:8832 `doRescue`；旧图 :6549-6554 仅 nextRow±1 挂 click | 新图：点已访问邻格=回返机制（T75，必触发遭遇、扣血钳 1 不杀人）；`backtrackTo` 三重 guard：`st._pendingNode` 防重入、必须已访问、必须当前格直接入邻（否则静默忽略）；`.pick` 只画在未访问出边终点（:8356）；死路救援按钮有 `isDeadEnd()+_pendingNode` 双 guard | 已防护 |
| 7 | 双击事件选项 | index.html:7323-7340 选项按钮→:7342 `chooseEventOption` | 结算与面板重建在同一同步任务内完成（结果屏覆盖事件屏）；第二击落在新 DOM 上，旧按钮已 detach；门控不足的选项 `b.disabled=true`（:7332） | 已防护 |
| 8 | 选项连点（接着看/继续/跳过/营火/奖励卡） | index.html:7365 `doFollow`（follow.shift）、:6642 营火、:6709 升级、:6740 删牌、:7207 奖励卡、:7236 遗物 | 全部是「点击→同步重绘」模式；二次点击命中的是重建后的面板，旧元素已 detach；`doFollow` 用 `follow.shift()` 天然幂等 | 已防护 |
| 9 | 战斗中刷新 | 无处理（全库无 beforeunload/pagehide/状态落盘；localStorage 只存 `redabyss_cleared`/endings/hint/death 标记，:6428、:7455-7460、:7050、:7566） | 刷新即整局丢失，静默回到选职业屏（不脏、不报错，但无任何警告与续局能力） | **缺失** |
| 10 | 商店金币不足购买 | index.html:6795-6801 | 点击时 `if (item.sold) return;` + `if (run.gold < item.price) { toast(...); return; }`；满血买合剂也挡（:6797）；渲染层补 `.sold/.cant` 置灰（:6829-6834）；买后 `item.sold=true` 防复买 | 已防护 |
| 11 | 遗物满再捡 | index.html:7159 `pickRelics`（owned Set 去重）、:7107-7109 空池跳过、:6658-6666 营火兜底转金币 | 遗物无上限设计：`pickRelics` 按 `owned` 过滤，池空返回 `[]` → 奖励步骤自动跳过；营火无卡可升时遗物池空再转 +50 金；`grantRelic` 不会重复 | 已防护 |
| 12 | 卡牌详情开着切换屏 | index.html:8023 `openCardDetail`、:8043 `closePanel`、:6908 Esc；`startCombatFlow`:6839 **未重置** `#card-detail` | 详情面板在 `#screen-combat` 内（:896），切屏随父隐藏；但 `startCombatFlow` 不把它藏回——上一场拖牌打出（拖起即开详情 :7937）击杀收尾时详情仍开着，**下一场开场残留旧卡内容，`cd-play` 仍绑旧索引 i**，点「打出」会对新牌库手牌第 i 张出手（引擎重校验兜底不炸，但属误操作面）。Esc/收回/×可手动清 | **部分** |
| 13 | Tab 狂按 | index.html:8985-8991 | `if (!st.region \|\| st.runRef !== run) return` 只在局内接管；`e.preventDefault()` 防焦点逃逸；开/关总图幂等（classList + `fm.open` 翻转），狂按只是每次重建 SVG（性能开销，无状态破坏）；选人屏 Tab 走原生焦点 | 已防护 |
| 14 | Esc 连按 | index.html:6905（帮助+详情+pending）、:8205（职业模态）、:8226（overlay+地图光标）、:8971（总图） | 四个监听全部幂等（`classList.add('hidden')`、`modalClass` 已空即跳过、`hideOverlay` 加类）；pending 复位带 `phase==='combat'` 条件才 render | 已防护 |
| 15 | 非战斗屏按 1-9 | index.html:8238 `if (phase !== 'combat' \|\| !C \|\| C.over) return;` | 地图态走方向键分支（:8227），其余屏早退；战斗内 1-9 还要求非 `dimmed` | 已防护（但见备注 ①） |
| 16 | 日志滚动中结束回合 | index.html:7879-7889（每次 render 全量重建 log 并 `scrollTop=0`）；core.js:960-963 `log` 上限 300 条 | 日志无滚动动画、无异步追加；endTurn→render 同步重建，滚动中结束回合只会被重置到顶（最新在最上，2026-10-30 定版），无竞态 | 已防护 |
| 17 | 奖励屏连点跳过 | index.html:7217-7219 跳过、:7246-7248 不拿、:7101 `nextReward` 队列 shift | 与 #8 同模式：skip→`onDone`→队列 shift→同步重绘；二次点击落空；`mustPick` 时不渲染跳过按钮 | 已防护 |
| 18 | NG+ 重开 | index.html:6450 `restart`、:8208-8211 `btn-dive-confirm`（`modalClass` 防双开）、:6428/6435 `redabyss_cleared` | restart 幂等（重复置空+回选人屏）；开局确认按钮依赖 `modalClass` 非空，第二次点击直接被 guard 掉；通关标记 localStorage 读写全部 try/catch | 已防护 |
| 19 | 结算屏连点 | index.html:7395 `showGameOver`、:7462 `showVictory`、:7497「回头」重建面板、:7420 静默段 | 重新开始=幂等 restart；「回头」点击后整面板重建（旧按钮 detach）；`markCleared` 重复写同值无害；战斗→结算的 450ms 延迟窗口由 `phase !== 'combat'`（:7058）与 btn-end `C.over` guard 双重封死 | 已防护 |
| 20 | 断网打开 | 全部 `<script>` 内联（:968/:3939/:3945/:5357/:6353/:6356/:8247），无 CDN/无 fetch/XHR（全库 grep 为零）；素材为同源相对路径 webp，`ART` 表内联（:3941） | 纯本地可玩；缺图降级：职业立绘 `pt.onerror` 隐藏图回落首字（:6898），卡面/敌人图查 `ART` 表命中则藏符号占位——**若 webp 存在但加载失败会留空块**（仅外观） | 已防护 |

备注：
- ① #15 的相邻缺陷：战斗**内**按 1-9 出牌实际失效——:8243 `cardEl.click()` 触发的是 click 事件，而手牌只绑了 `pointerdown`（:7847），没有任何 click 监听，等于死输入。guard 写对了，动作没接上。
- 判定口径：「已防护」= 异常输入不会产生错误状态或重复结算；「部分」= 有 guard 但存在残留/失效面；「缺失」= 无任何处理，异常输入改变游戏状态。

## 缺失/部分项最小修复建议（不改代码，仅建议）

| 项 | 最小修复 |
|---|---|
| #2 连点结束回合 | `#btn-end` click 头部加时间戳防抖：`if (now - btn._last < 400) return; btn._last = now;`（endTurn 同步完成，两次 click 是两个独立事件，busy 位无效，必须按时间窗挡）。同时可给 `C` 记 `_endLockTurn`，render 后解锁 |
| #9 战斗中刷新 | 最小成本：`window.addEventListener('beforeunload', e => { if (phase === 'combat' \|\| run) { e.preventDefault(); e.returnValue = ''; } })`；进阶：把 `run`/`C` 关键字段序列化进 localStorage，启动时有存档则弹「继续/放弃」 |
| #12 详情残留 | `startCombatFlow` 开头补一行 `document.getElementById('card-detail').classList.add('hidden')`，并在 `render()` 重建手牌时同步清空 `#cd-card` |
| ① 1-9 失效 | render() 里给手牌 `d.addEventListener('click', () => startCardPointer 的单击分支)`，或把 :8243 改为直接调 `openCardDetail(n-1)` / `doPlay(n-1)`（按是否 needsTarget 分流） |

## 未解决
无（本次为只读审计，未发现修不了的项；四条建议均未落码）。
