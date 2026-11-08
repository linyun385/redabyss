# 00 · 代码地图：东西都在哪儿

> 这篇是索引，不是教材。看完你会知道：`web/index.html` 这个 9137 行的文件里，样式、界面骨架、数据、引擎、界面逻辑各占哪几行；全项目 180 个顶层函数每一个叫什么、在第几行、干什么；以及打一局牌时代码按什么顺序被调用。后面 5 篇的所有行号都以这篇为地图。

## 一、`index.html` 的六个区（按行号）

| 区 | 行号范围 | 里面是什么 |
|---|---|---|
| 样式 | [index.html:6] 到 [index.html:829] | `<style>` 标签，全部 CSS：卡牌扇形、手牌拖拽、地图主题色（[index.html:6526] 的 `LAYER_THEME` 也在这一区之后才定义，见下） |
| 界面骨架 | [index.html:831] 到 [index.html:969] | `<body>` 的 HTML：四个屏幕容器（选职业/战斗/流程面板）、HUD、手牌区 `#hand`、敌人区 `#enemy-area`、弹层 |
| 绑定数据 | [index.html:972] 到 [index.html:3942] | 第一个 `<script>`：`MAPGEN_BINDINGS`（T58 生态×深度的敌人/事件绑定表，由 `tools/_t56_wire.js` 注入，头部注释见 [index.html:973]） |
| 素材表 | [index.html:3943] 到 [index.html:3949] | 第二个 `<script>`：`window.ART` 素材路径表（T67，`art_embed.py` 生成） |
| 地图生成库 | [index.html:3950] 到 [index.html:5359] | 第三个 `<script>` 的上半：MAPGEN-LIB（`tools/mapgen.js` 的内联副本，结束标记在 [index.html:5359]），含 `makeRng`（[index.html:3980]）到 `generate`（[index.html:5299]） |
| 战斗引擎副本 | [index.html:5362] 到 [index.html:6390] | 同一个 `<script>` 的下半：与 `engine/core.js` 同源的战斗引擎（函数一一对应，行号不同），结尾是 `RAW` 数据行（[index.html:6391]，一整行 JSON：卡/敌/事件/遗物/层 全部内联） |
| 界面与流程 | [index.html:6396] 到 [index.html:9137] | 全部 UI 逻辑：从 `adaptCard`（[index.html:6396]）到文件尾，含 T56 新地图模块（[index.html:8303] 起的 IIFE） |

为什么数据不放在单独文件里：`RAW` 那一行（[index.html:6391]）是构建脚本把 `cards/*.json`、`enemies/*.json` 等拼进来的产物——游戏双击 HTML 就能跑，不需要服务器和 fetch。

## 二、顶层函数清单（`function` 开头、缩进 0–2，共 180 个）

### 地图生成库（内联副本，23 个）

| 行 | 函数 | 职责 |
|---|---|---|
| [index.html:3967] | loadBindings | 读生态×深度绑定表 |
| [index.html:3980] | makeRng | 造一个种子化随机数发生器 |
| [index.html:4057] | bandRowsOf | 每个深度带占几行 |
| [index.html:4058] | bandOfY | 把格子 y 坐标换算成带号 |
| [index.html:4059] | bandRange | 带号→行区间（闭区间） |
| [index.html:4062] | lineCells | 线段栅格化成格子序列 |
| [index.html:4076] | Heap | 二叉堆（生长算法的优先队列） |
| [index.html:4108] | buildWeightTable | 生成生态×深度的出现权重表 |
| [index.html:4142] | componentsOf | 数连通分量 |
| [index.html:4162] | growEcos | 生态区生长主循环 |
| [index.html:4505] | effectiveQuota | 生态配额折算 |
| [index.html:4520] | dispSet | 位移方向集合 |
| [index.html:4525] | dispOkD | 单步位移合法性检查 |
| [index.html:4529] | shuffleInPlace | 原地洗牌 |
| [index.html:4543] | growDAG | 地图节点与边的主生长算法 |
| [index.html:5002] | byIdOf | 节点 id→节点对象 |
| [index.html:5007] | markBands | 给节点标注所属深度带 |
| [index.html:5024] | resolveBinding | 把节点类型绑定到具体敌人/事件 id |
| [index.html:5085] | validate | 生成结果的总校验（不合格就抛错重来） |
| [index.html:5253] | pruneForFrontend | 按访问进度裁剪发给前端的数据 |
| [index.html:5280] | bfsMaxDepth | 算最深可达深度 |
| [index.html:5299] | generate | 生成入口（带重试循环） |
| [index.html:5334] | resolveParams | 合并调用方参数与默认值 |

### 战斗引擎副本（40 个；`engine/core.js` 里同名函数一一对应）

| 行 | 函数 | 职责 |
|---|---|---|
| [index.html:5401] | makeRng | 战斗侧的种子随机发生器 |
| [index.html:5408] | shuffle | Fisher-Yates 洗牌 |
| [index.html:5415] | randInt | [a,b] 闭区间随机整数 |
| [index.html:5416] | parseHp | 把 "8-10" 这类血量串解析成数字 |
| [index.html:5423] | newRun | 开一局（生命/金币/牌库/清醒度初始化） |
| [index.html:5457] | buildStarterDeck | 造初始牌库 |
| [index.html:5507] | startCombat | 进战斗（实例化敌人/洗牌/遗物结算） |
| [index.html:5591] | beginTurn | 回合开始（弃手牌/抽5/共振/能量） |
| [index.html:5631] | tickStartOfTurn | 层环境与玩家状态结算 |
| [index.html:5663] | checkResonance | 共振跨 10/20/30 阈值反应 |
| [index.html:5679] | draw | 抽 n 张（含弃牌堆洗回） |
| [index.html:5694] | playCard | 出牌总入口（校验/扣费/结算） |
| [index.html:5765] | cardCost | 算这张牌现在的能量费 |
| [index.html:5787] | veinChainBonus | 同脉连携加成 |
| [index.html:5807] | applyCardEffect | 把 effect 字段逐条执行 |
| [index.html:5852] | applySpecial | special 数组的分发表 |
| [index.html:5882] | applyCardCost | 代价结算（memory/vitality/mark/lock） |
| [index.html:5915] | deleteRandomCard | 从牌库随机删一张 |
| [index.html:5923] | dealToEnemy | 对敌人扣血（先扣格挡） |
| [index.html:5944] | gainBlock | 玩家加格挡 |
| [index.html:5948] | damagePlayer | 对玩家扣血（含梦境分支） |
| [index.html:5997] | healPlayer | 回血 |
| [index.html:6006] | addGaze | 凝视加值 |
| [index.html:6011] | endTurn | 回合结束（敌人行动/状态/清格挡） |
| [index.html:6055] | nextIntent | 敌人轮转到下一条意图 |
| [index.html:6063] | currentPattern | 按血量相位取出招表 |
| [index.html:6075] | applyPhase | 相位切换检查 |
| [index.html:6090] | enemyAct | 敌人按意图行动 |
| [index.html:6163] | checkCombatEnd | 胜负判定 |
| [index.html:6178] | finishCombat | 战后结算（金币/清醒度） |
| [index.html:6211] | pickEnding | 按凝视选结局 |
| [index.html:6221] | salvageUpgrade | 黯民：零件改装手牌 |
| [index.html:6238] | dismantle | 黯民：拆解换遗物 |
| [index.html:6250] | rebuildWorldPiles | 疯先知：按世界重建牌堆 |
| [index.html:6263] | switchWorld | 疯先知：入梦/醒来 |
| [index.html:6286] | forceWake | 强制苏醒 |
| [index.html:6305] | tickOmens | 疯先知：预兆倒计时 |
| [index.html:6321] | activateProtocol | 激活协议（lockdown/purge/silence） |
| [index.html:6330] | upgradeCard | 卡牌升级合并 |
| [index.html:6355] | log | 往战斗日志推一行（`\u0001` 前缀=警告行） |

### 界面与流程（80 个）

| 行 | 函数 | 职责 |
|---|---|---|
| [index.html:6396] | adaptCard | 给池里的卡补运行时字段（uid/已升级标记等） |
| [index.html:6461] | startRun | 开新局（含开局补位与二周目赠卡） |
| [index.html:6494] | restart | 回到选人界面 |
| [index.html:6505] | showScreen | 三屏切换 |
| [index.html:6510] | layerRows | 读当前层的静态行数据（奖励类型判定仍用它） |
| [index.html:6517] | progressText | HUD 上的「第 X 层 第 Y 行」文案 |
| [index.html:6536] | applyLayerTheme | 按层换背景主题色 |
| [index.html:6545] | showMap | 老地图面板（被 T56 模块接管后先绘后覆盖） |
| [index.html:6612] | resolveNode | 旧图节点点击分发 |
| [index.html:6649] | advanceNode | 旧图推进/换层 |
| [index.html:6671] | showCampfire | 篝火三选一 |
| [index.html:6681] | campOpt | 篝火选项的 DOM 构造 |
| [index.html:6721] | campfireResult | 篝火结果面板 |
| [index.html:6728] | showUpgradePick | 升级选牌界面 |
| [index.html:6763] | removeCardPick | 删牌选牌界面 |
| [index.html:6802] | shopPrice | 商店随机定价 |
| [index.html:6804] | buildShopStock | 组货架（2-3 卡+1 遗物+删牌+合剂） |
| [index.html:6822] | showShop | 商店界面 |
| [index.html:6883] | startCombatFlow | 进战斗的前端准备 |
| [index.html:6903] | applyRelicTurnStart | 遗物 turn_start 触发 |
| [index.html:6966] | doPlay | 出牌的前端入口（动画/音效/重画） |
| [index.html:7012] | showEgg | 彩蛋浮层 |
| [index.html:7025] | checkEasterEggs | 卡组组合彩蛋判定 |
| [index.html:7051] | relicBadge | 遗物小图标 HTML |
| [index.html:7061] | runMemoryLine | 结算页的一句「回忆」文案 |
| [index.html:7079] | deathHint | 死亡页提示 |
| [index.html:7101] | finishCombatFlow | 战斗结束的奖励队列组装 |
| [index.html:7145] | nextReward | 逐个发奖励 |
| [index.html:7172] | weightedCards | 按稀有度权重抽 n 张职业卡 |
| [index.html:7192] | pickEventRelics | 事件专属遗物池抽取 |
| [index.html:7203] | pickRelics | 普通遗物池抽取 |
| [index.html:7214] | grantRelic | 遗物入包（含 run_start 结算） |
| [index.html:7225] | showFlowPanel | 流程面板通用容器 |
| [index.html:7240] | showCardChoice | 三选一卡牌 |
| [index.html:7268] | showRelicChoice | 三选一遗物 |
| [index.html:7306] | veinArt | 按脉取卡面美术 |
| [index.html:7311] | cardArtId | 卡→素材表键名 |
| [index.html:7321] | appendArt | 往卡面 DOM 挂图 |
| [index.html:7341] | renderCardStatic | 画一张不可交互的卡（面板用） |
| [index.html:7359] | showEvent | 事件界面 |
| [index.html:7388] | chooseEventOption | 事件选项结算 |
| [index.html:7411] | doFollow | 事件后续奖励的发牌循环 |
| [index.html:7429] | cardsOfRarity | 按稀有度从职业池抽 n 张 |
| [index.html:7441] | showGameOver | 死亡结算页 |
| [index.html:7473] | startEchoRun | 黯星回响短局 |
| [index.html:7487] | echoEnemyPool | 回响局敌人池 |
| [index.html:7489] | addStat | 结算页加一行统计 |
| [index.html:7501] | markCleared | 记录通关结局（localStorage） |
| [index.html:7508] | showVictory | 胜利结算页 |
| [index.html:7563] | intentKey | 意图对象→比较键 |
| [index.html:7564] | intentHtml | 意图→界面文字 |
| [index.html:7575] | uiCost | 界面侧算显示费用 |
| [index.html:7584] | playBlockReason | 出牌阻挡原因文案 |
| [index.html:7595] | needsTarget | 这张牌要不要指定目标 |
| [index.html:7601] | toast | 底部浮出提示 |
| [index.html:7609] | onceHint | 一次性教学提示（localStorage 记账） |
| [index.html:7623] | playSfx | 音效钩子（只记 log，未真正发声） |
| [index.html:7629] | setLayerAmbience | 层环境音钩子（空实现） |
| [index.html:7633] | flyCard | 出牌飞出残影 |
| [index.html:7647] | flash | 给元素加一个限时 class |
| [index.html:7653] | resFlash | 共振跨阈值的全屏闪 |
| [index.html:7657] | floatText | 飘字（伤害/回复数字） |
| [index.html:7670] | enqueueAnim | 动作入动画队列 |
| [index.html:7671] | pumpAnim | 动画队列泵 |
| [index.html:7682] | floatOffsetFor | 多段伤害飘字错开 |
| [index.html:7693] | tick | 动画帧回调 |
| [index.html:7703] | render | 战斗界面总重画（手牌/敌人/HUD/日志） |
| [index.html:7943] | shakeCard | 卡牌不可用的抖动 |
| [index.html:7949] | layoutFan | 手牌扇形排布 |
| [index.html:7966] | startCardPointer | 手牌按下/拖拽/松手的主逻辑 |
| [index.html:8059] | dropEnemy | 指针落点→命中的敌人 |
| [index.html:8073] | openCardDetail | 右侧卡牌详情面板 |
| [index.html:8108] | cardDesc | effect 字段→卡面描述文字 |
| [index.html:8135] | showSalvagePanel | 黯民改装面板 |
| [index.html:8174] | showPile | 牌堆浏览 |
| [index.html:8195] | hideOverlay | 关弹层 |
| [index.html:8229] | openClassModal | 选职业详情弹窗 |
| [index.html:8244] | closeClassModal | 关闭选职业弹窗 |

### T56 新地图模块内部（IIFE 起 [index.html:8303]，37 个）

| 行 | 函数 | 职责 |
|---|---|---|
| [index.html:8359] | esc | HTML 转义 |
| [index.html:8363] | placeName | 节点所在生态的地名 |
| [index.html:8394] | effTypeOf | 节点的生效类型（回溯覆盖后可能变 boss） |
| [index.html:8397] | visible | 节点对玩家是否可见（迷雾） |
| [index.html:8400] | nodeById | id→节点 |
| [index.html:8403] | bandOfNode | 节点所在深度带 |
| [index.html:8405] | pickableIds | 当前可走的节点 id 集 |
| [index.html:8410] | drawMap | 画节点图（SVG） |
| [index.html:8483] | renderMiniMap | 左侧小地图 |
| [index.html:8512] | renderLog | 行程日志渲染 |
| [index.html:8538] | paintHl | 高亮当前路径 |
| [index.html:8547] | fullMapSvg | 总图 SVG |
| [index.html:8553] | buildFullMap | 建/刷新总图 |
| [index.html:8564] | openFullMap | 开总图 |
| [index.html:8570] | centerOnCurrent | 总图居中到当前位置 |
| [index.html:8576] | closeFullMap | 关总图 |
| [index.html:8580] | fmSetZoom | 总图缩放 |
| [index.html:8596] | fmWheel | 总图滚轮缩放 |
| [index.html:8604] | fmPan | 总图拖拽平移 |
| [index.html:8627] | wireClicks | 总图/小图点击接线 |
| [index.html:8649] | dataProvider | 给生成器提供每带敌人/事件池 |
| [index.html:8660] | initRun | 生成一局的地图区域（懒初始化） |
| [index.html:8680] | pendEntry | 进入格子时开一条行程记录 |
| [index.html:8689] | markResolved | 行程记录标记类型 |
| [index.html:8695] | finalizeLog | 到达时结算这段路的收获 |
| [index.html:8738] | isDeadEnd | 死路判定 |
| [index.html:8743] | pickEnemies | 从绑定池选敌人 |
| [index.html:8753] | pickEventFor | 从绑定池选事件 |
| [index.html:8766] | dispatch | 按节点类型分发到战斗/事件/商店 |
| [index.html:8781] | enterNode | 进入节点 |
| [index.html:8803] | arriveAtNode | 到达节点（结算+发奖励） |
| [index.html:8818] | r_edgesIn | 某节点的入边 |
| [index.html:8819] | backtrackTargets | 可回溯的目标列表 |
| [index.html:8824] | resolveEncounter | 回溯遭遇判定（坏事件45/战斗30/精英15/BOSS8/空手2） |
| [index.html:8869] | backtrackTo | 执行回溯 |
| [index.html:8882] | doRescue | 死路救援按钮逻辑 |
| [index.html:8959] | currentPicks | 当前可走节点（出边终点） |
| [index.html:8962] | paintCursor | 键盘光标绘制 |
| [index.html:8967] | moveCursor | 方向键移动光标 |

另有三个不是 `function` 声明但承担函数职责的点：`window.showMap` 的接管（[index.html:8914]）、`window.progressText` 的接管（[index.html:8910] 附近）、动画队列的 `requestAnimationFrame`（[index.html:7674] 附近）。

## 三、三条主链路（只写「从哪进、经过谁、到哪出」）

1. **开一局**：选职业弹窗「下潜」按钮（`openClassModal` [index.html:8229] 建，确认在 [index.html:8248] 附近的监听里）→ `startRun` [index.html:6461] → 引擎 `newRun` [index.html:5423] + `buildStarterDeck` [index.html:5457] + 补位卡 [index.html:6465] → `showMap` [index.html:6545] → 被 T56 接管版 [index.html:8914] 接住 → 懒初始化 `initRun` [index.html:8660] → `MG.generate` [index.html:5299] → 节点图出现在屏幕（`drawMap` [index.html:8410]）。
2. **打一回合**：点「结束回合」（按钮监听 [index.html:6956]）→ 引擎 `endTurn` [index.html:6011]（敌人逐个 `enemyAct` [index.html:6090] → 状态结算 [index.html:666] 附近 → 清格挡）→ 自动进下一回合 `beginTurn` [index.html:5591] → 前端补一发遗物 `applyRelicTurnStart` [index.html:6903] → `render` [index.html:7703] 全屏重画，玩家看到新回合。
3. **生成一张地图**：URL 里的 `?mapseed=` 或随机数（[index.html:8661]）→ `makeRng` [index.html:3980] → `growEcos` [index.html:4162]（生态区）→ `growDAG` [index.html:4543]（节点+边）→ `markBands` [index.html:5007] → `resolveBinding` [index.html:5024]（绑定敌人/事件 id）→ `validate` [index.html:5085]（不合格整次重来）→ `generate` [index.html:5299] 返回 region → `drawMap` [index.html:8410] 画成屏幕上的节点图。失败会重试多次（[index.html:5303] 的 attempt 循环），全失败才报错（[index.html:5331]）。

## 四、`engine/core.js` 与 `index.html` 的分工

`engine/core.js`（1026 行）是**纯逻辑**：不碰 DOM，从 `newRun` 到 `pickEnding` 的 40 个函数构成游戏的规则内核，头部注释（[engine/core.js:2]）写明「纯逻辑，无 DOM 依赖，浏览器与 node 均可加载」。文件末尾的导出表（[engine/core.js:999]）把 API 挂到 `window.RedAbyss` 上。

`index.html` 里 [index.html:5362] 到 [index.html:6390] 是它的**内联副本**——同样的函数、同样的逻辑、不同的行号。为什么要复制一份：页面要双击即玩、不发请求，所以引擎必须内联；单独留 core.js 文件是为了让 `tools/` 下的 node 脚本（测试、模拟器）也能 `require` 同一套规则。

分工上的实际效果是：**规则改动要同时改两处**（core.js 与内联副本），界面改动只动 [index.html:6396] 之后的部分。这个双份结构本身就是理解这个项目的第一课——它不是一个「引擎被引用」的项目，而是一个「引擎被誊抄」的项目。

## 五、想改某个功能时，从哪个函数进去（检索表）

这一节是地图的用法。左栏是「你想干的事」，右栏是第一刀该切进去的位置——先读它，再顺着它往上下游走。所有行号在 00 篇第二节的大清单里都能查到职责。

| 你想改 / 想查的事 | 第一入口 | 路径提示 |
|---|---|---|
| 某张卡的数值不对 | 数据源 [cards/diver.json:28] 这类对象 | 改 json → 重建（04 篇第 8 节）；卡面文字是现算的，改完即生效 |
| 出牌的费用规则 | `cardCost` [index.html:5765] | 上面是界面侧的镜像 `uiCost` [index.html:7575]，两处要一起改 |
| 出牌的合法性（能不能打） | `playCard` [index.html:5694] | 前端拦截文案在 `playBlockReason` [index.html:7584]，两边规则必须一致 |
| 伤害公式 | `applyCardEffect` 伤害段 [index.html:5823] | 公式在 [index.html:5825]，格挡吸收在 `dealToEnemy` [index.html:5923] |
| 状态效果（灼烧/中毒…） | `applySpecial` 分发表 [index.html:5852] | 敌人侧结算在 `endTurn` 的状态段 [index.html:666] |
| 回合流程（抽几张/共振/能量） | `beginTurn` [index.html:5591] | 常量 `DRAW_PER_TURN` [index.html:5374]、`BASE_ENERGY` [index.html:5375] |
| 共振阈值反应 | `checkResonance` [index.html:5663] | 反应表 `MODE_REACTION` [index.html:5390] 附近，层模式定义 [index.html:5378] |
| 敌人行为 | `enemyAct` [index.html:6090] | 意图轮转 `nextIntent` [index.html:6055]、相位 `applyPhase` [index.html:6075] |
| 代价类型（memory/vitality/mark/lock） | `applyCardCost` [index.html:5882] | lock 的解锁点在 `startCombat` 里重建战斗容器时（`_locked` 不复制，[index.html:5570] 的拷贝会丢掉下划线字段） |
| 升级规则 | `upgradeCard` [index.html:6330] | 合并语义注释在 [index.html:6329]，营火入口 `showUpgradePick` [index.html:6728] |
| 遗物触发 | `applyRelicTurnStart` [index.html:6903]、战斗开始 [index.html:5567] 附近 | mod 改则散在 `cardCost` [index.html:5717] 与 `veinChainBonus` [index.html:5795] 附近 |
| 地图长什么样 | `growDAG` [index.html:4543] | 配额表 [index.html:4035]-[index.html:4042]，校验 [index.html:5085] |
| 地图上的敌人/事件分配 | `resolveBinding` [index.html:5024] | 绑定数据本体在 [index.html:973] 起的 `MAPGEN_BINDINGS` |
| 节点点击后发生什么 | T56 模块 `enterNode` [index.html:8781] → `dispatch` [index.html:8766] | 旧四行图路径是 `resolveNode` [index.html:6612]（仅回退模式走） |
| 商店 | `buildShopStock` [index.html:6804] | 定价 [index.html:6802]、界面 [index.html:6822] |
| 事件 | `showEvent` [index.html:7359] | 结算 `chooseEventOption` [index.html:7388]，后续奖励 `doFollow` [index.html:7411] |
| 篝火 | `showCampfire` [index.html:6671] | 回血量在 [index.html:6689] 的 `healN` |
| 奖励队列 | `finishCombatFlow` [index.html:7101] | 队列消费 `nextReward` [index.html:7145]，抽卡权重 `weightedCards` [index.html:7172] |
| 死亡 / 胜利画面 | `showGameOver` [index.html:7441] / `showVictory` [index.html:7508] | 结局选择引擎侧 `pickEnding` [index.html:6211] |
| 手牌拖拽手感 | `startCardPointer` [index.html:7966] | 落点宽容度 `dropEnemy` [index.html:8059]（单敌 170px / 多敌 70px） |
| 卡面描述文字 | `cardDesc` [index.html:8108] | 它是 effect → 人话的翻译器，加新字段要在这里补显示 |
| 音效 | `playSfx` [index.html:7623] | 空钩子；调用点已全部接好，发声器未实现 |
| HUD 数值 | `render` 开头段 [index.html:7705] 起 | 全部是「与 prev 差分 → 加 class」的套路 |
| 选职业界面 | `openClassModal` [index.html:8229] | 文案表 `CLASS_INFO` [index.html:8211] 附近 |
| 黯民零件 | `dealToEnemy` 掉落段 [index.html:5735] | 改装 `salvageUpgrade` [index.html:6221]、拆解 `dismantle` [index.html:6238] |
| 疯先知双世界 | `switchWorld` [index.html:6263] | 牌堆重建 `rebuildWorldPiles` [index.html:6250]、预兆 `tickOmens` [index.html:6305] |
| 结局门槛 | `pickEnding` [index.html:6211] | 阈值 20/5 写死在函数里，死亡回响入口 [index.html:7463] |

用法提醒：这张表的行号指向**内联副本**（index.html）。如果你要在 node 里跑测试（`tools/sim.js` 那一类），同一批函数在 `engine/core.js` 里，行号不同、内容相同——两边都要改，见第 4 节。

## 六、你改这里会发生什么（三个真实修改点）

**修改点一：把 [index.html:5374] 的 `DRAW_PER_TURN` 从 5 改成 6。**
会发生的连锁反应：每回合多抽一张 → `beginTurn` [index.html:5591] 的抽牌行自动跟随（它引用常量）→ 手牌节奏整体加快，灼烧流、过牌流强度上浮；冷洞层的「首张 +1 费」惩罚相对变轻。验证：进战斗连续结束两个回合，数手牌数（上限仍是 [index.html:5373] 的 10）。注意只改 index.html 不改 `engine/core.js` 的话，node 模拟器（`tools/sim.js`）跑出来的还是 5 抽——两处常量不一致是最容易埋的雷。

**修改点二：把 [index.html:5825] 伤害公式里的 `+ (C.activeProtocol === 'purge' ? 3 : 0)` 删掉。**
会发生的连锁反应：清剿协议的「双方攻击 +3」只剩敌方侧（[index.html:5734] 敌方 `+3` 在 `enemyAct` 里），玩家侧输出不再被协议放大——协议流（T330 诊断的幽灵流派）彻底变成纯亏。验证：激活清剿协议后打一张伤害牌，飘字不再多 3。这个修改点说明「引擎里的一个小三元表达式就是一个流派的存在方式」。

**修改点三：把 [index.html:7173] 的 `c.rarity !== 'special'` 过滤去掉。**
会发生的连锁反应：`weightedCards` 的权重表里没有 `special` 键（[index.html:7174] 只有 common/uncommon/rare），`weight[c.rarity] || 1` 回落到 1——special 卡以每张 1 份权重混进奖励池。表面上「只是让 15 张 special 卡可获取」，实际上这些卡（如 dive_0010）当初就是按不可获取设计的数值，等于偷跑一批未平衡内容。验证：商店刷新若干次，出现 special 卡即改成功；改回来时记得这张过滤是 T324 诊断里「特殊卡不可获取」结论的代码出处。

## 七、按数据走的第三条线索

除了「函数线索」，这个项目还有一条「数据线索」可以反向走：**屏幕上任何一个字，都能找到产生它的数据字段**。对照表：

| 屏幕上看到的 | 产生的字段 | 消费代码 |
|---|---|---|
| 卡面「伤害 10」 | [cards/diver.json:38] 的 `"damage": 10` | `cardDesc` [index.html:8108] 现算文案 |
| 敌人头上的「意图 攻 5×2」 | 敌人 json 的 `intent_pattern`（如 [enemies/all.json:1] 起的首个敌人） | `intentHtml` [index.html:7564] |
| HUD「第 3 层」 | `run.depth`，由地图节点带号推进（[index.html:8687] `run.depth = ...band`） | `progressText` [index.html:6517] |
| 结算页「凝视 17（同行）」 | `run.gaze`（`addGaze` [index.html:6006] 累计） | `pickEnding` [index.html:6211] 分档 |
| 行程日志地名 | 生成器节点的生态 id | `placeName` [index.html:8363] 查表 `ECO_PLACES` [index.html:8350] 附近 |

顺着这条线查问题往往比顺着函数快：先在页面上指认「这个字是从哪来的」，再反查消费它的代码——两张表（第五节、本节）配合使用。

## 八、`engine/core.js` 本体的行号对照（node 测试侧）

第二节给的是内联副本的行号。在 node 里跑规则（`require('./engine/core.js')` 的那些 `tools/` 脚本）用的是另一套行号——同一批函数，逐个对照如下，改规则时拿这张表找 core.js 侧的落刀点：

| 函数 | core.js 行 | 函数 | core.js 行 |
|---|---|---|---|
| 常量 VEINS/HAND_LIMIT 等 | [engine/core.js:10] | dealToEnemy | [engine/core.js:561] |
| LAYERS 八层表 | [engine/core.js:17] | gainBlock | [engine/core.js:582] |
| MODE_REACTION 七模式 | [engine/core.js:29] | damagePlayer | [engine/core.js:586] |
| makeRng | [engine/core.js:40] | healPlayer | [engine/core.js:635] |
| shuffle | [engine/core.js:47] | addGaze | [engine/core.js:644] |
| randInt | [engine/core.js:54] | endTurn | [engine/core.js:649] |
| parseHp | [engine/core.js:55] | nextIntent | [engine/core.js:693] |
| newRun | [engine/core.js:62] | currentPattern | [engine/core.js:701] |
| buildStarterDeck | [engine/core.js:96] | applyPhase | [engine/core.js:713] |
| startCombat | [engine/core.js:146] | enemyAct | [engine/core.js:728] |
| beginTurn | [engine/core.js:229] | checkCombatEnd | [engine/core.js:801] |
| tickStartOfTurn | [engine/core.js:269] | finishCombat | [engine/core.js:816] |
| checkResonance | [engine/core.js:301] | pickEnding | [engine/core.js:849] |
| draw | [engine/core.js:317] | salvageUpgrade | [engine/core.js:859] |
| playCard | [engine/core.js:332] | dismantle | [engine/core.js:876] |
| cardCost | [engine/core.js:403] | rebuildWorldPiles | [engine/core.js:888] |
| veinChainBonus | [engine/core.js:425] | switchWorld | [engine/core.js:901] |
| applyCardEffect | [engine/core.js:445] | forceWake | [engine/core.js:924] |
| applySpecial | [engine/core.js:490] | tickOmens | [engine/core.js:943] |
| applyCardCost | [engine/core.js:520] | activateProtocol | [engine/core.js:959] |
| deleteRandomCard | [engine/core.js:553] | upgradeCard | [engine/core.js:968] |
| — | — | log | [engine/core.js:993] |

共振阈值反应的七种模式也值得单独一张小表（它们是层规则之外唯一的「引擎级事件」）：休眠层无事发生（[engine/core.js:30]）、稳定层回血 3（[engine/core.js:31]）、脉冲层全体敌人 5 伤（[engine/core.js:32]）、共振层抽 2（[engine/core.js:33]）、过载层敌人攻 +3（[engine/core.js:34]）、锁定层能量 −1（[engine/core.js:35]）、虚空层锁脉（[engine/core.js:36]）。想给某一层「换个性格」，改的就是这几行 apply 函数体。

改 core.js 时的铁律再说一遍：**这里改完，[index.html:5362] 到 [index.html:6390] 的内联副本要同步**。目前没有自动同步脚本管这一段（绑定表与 RAW 有 `_t56_wire.js`/`_t46_wire.js` 管，引擎副本没有）——靠人脑同步，这也是为什么改动前要先想清楚是否值得。

## 九、index.html 之外还有什么（外围地图）

读代码时会反复撞见 index.html 之外的文件，一并列出各自的地位：

| 文件 / 目录 | 地位 | 什么时候要碰它 |
|---|---|---|
| `engine/core.js` | 规则内核的独立副本（见第 4、8 节） | node 侧测试与模拟；页面不加载它 |
| `cards/*.json` | 四职业 + 通用卡池的唯一真源 | 改卡必改这里（04 篇第 8 节） |
| `enemies/all.json`、`events/all.json`、`relics/all.json` | 敌人/事件/遗物真源 | 同上，经 `_t46_wire.js` 拼进 RAW |
| `layers/layers.json` | 旧四行图与层主题的静态数据 | 奖励类型判定与主题色仍消费它（[index.html:6510]） |
| `web/assets/art/*.webp` | 461 张定稿图（清单在 `data/final_manifest.json`） | 换图/加图时；键名规则见 [index.html:7802] 的敌人回落逻辑 |
| `tools/_t46_wire.js` | RAW 重建脚本（数据 → 页面） | 每次改卡后跑 |
| `tools/_t56_wire.js` | 绑定表与 mapgen 库的注入脚本 | 改 `tools/mapgen.js` 或绑定表后跑 |
| `tools/sim.js` | node 战斗模拟器（引用 core.js） | 批量验证平衡时；它的行号体系见第 8 节 |
| `tools/check_lesson_refs.py`、`tools/check_design_refs.py` | 文档验收脚本 | 交付 md 后自检 |
| `docs/content/*.md` | 从 json 导出的卡表/敌表（只读产物） | 快速查卡用，改数据别改这里 |

这份外围地图的用途：当你顺着第五节找到该改的函数、发现要动的是数据而不是代码时，这张表告诉你数据的真源在哪一层——**永远改真源（json），不改产物（RAW 行、导出表）**。

到这里，这张地图的全部用法可以压缩成三句话：先查第五节下刀，再查第六节预演后果，最后查第九节确认改的是真源。三查之后才动手，动手之后照第六节的方法验证。
