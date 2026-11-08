# 04 · 一张卡的一生：从 json 那一行到屏幕上那一下

> 这篇盯住一张真实的卡——下潜者的 `dive_0002`「聚能枪」——从它在 `cards/diver.json` 里的第一行，追到它被抽出、画在手上、打出、扣血、进弃牌堆的全过程。看完你会知道 `effect` 里每个字段被谁读走，以及**自己加一张新卡、改一个数值**最少要动哪几个地方。

## 1. 起点：json 里的一行行

`cards/diver.json` 第 28 行，聚能枪的对象开始：

```
  "id": "dive_0002",
```

（[cards/diver.json:28]。）往下到第 43 行左右是它的全部字段；效果段在第 36-39 行，其中伤害是：

```
   "damage": 10,
```

（[cards/diver.json:38]。）同一对象里还有 `"hits": 1`（段数）、`"target": "single"`（单体）、`"veins": ["light"]`（光脉）、`"energy": 1`（费用）、`"upgrade": {"effect": {"damage": 14}}`（升级后伤害变 14）。此刻它只是磁盘上的文本——浏览器还没加载它。

## 2. 进内存：RAW、CLASS_POOL 与 adaptCard

构建脚本 `tools/_t46_wire.js` 干的事是把 json 拼进页面：它用正则定位 `const RAW = {...};\n`（[tools/_t46_wire.js:9]），再把最新数据 `JSON.stringify` 后整行替换回去（[tools/_t46_wire.js:18]）。所以页面里才有那行 300 多 KB 的 `RAW`（[index.html:6391]）。页面加载、这行执行时，聚能枪就以普通 JS 对象的身份进了内存。

下一步是入池。`CLASS_POOL`（[index.html:6420]）把四个职业的池子各拼上通用池，然后**逐张过一遍 `adaptCard`**（[index.html:6396]）：

```js
function adaptCard(src) {
  const c = JSON.parse(JSON.stringify(src));
  const e = c.effect = c.effect || {};
  const sps = e.special || [];
  const out = [];
  sps.forEach(sp => {
    const s = { code: sp.code };
    const v = (sp.value === undefined ? sp.v : sp.value);
```

（[index.html:6396]。）第一行 `JSON.parse(JSON.stringify(src))` 是**深拷贝**——后续所有战斗都改这个副本，json 原数据永远干净。后面在把 special 数组的字段名归一（`value`/`v` 二选一的兼容，`exhaust`/`retain` 两个特殊码提升成 effect 顶层标志）。聚能枪没有 special，原样通过。**从这一刻起，内存里有了这张卡的「可战斗形态」。**

## 3. 进牌库：三条路

聚能枪不在初始牌库里（初始牌只有「一击/缩起/签名牌」，`buildStarterDeck`，[index.html:5457]），它进玩家牌库只有几条路，每条都停在同一个动作上——往 `run.deck` 里塞一个带 uid 的副本。战斗奖励这条路：`weightedCards`（[index.html:7172]）按稀有度权重（普通 6/罕见 3/稀有 1，[index.html:7174]）从 `CLASS_POOL[run.classId]` 抽 3 张，玩家选中后 `showCardChoice` 的回调把卡放进牌库。商店那条路在 [index.html:6849]：`run.deck.push(Object.assign({}, item.card, { uid: 's' + run.deck.length }))`——注意每个副本都发一个唯一 `uid`，这是后面「同一张卡的两份拷贝能被区分」的根据。

## 4. 战斗开始：从牌库到抽牌堆

`startCombat`（[index.html:5507]）建战斗容器后，把整个牌库**再拷贝一遍**并洗乱：

```js
      C.drawPile = shuffle(run.deck.map(c => Object.assign({}, c)), C.rng);
```

（[index.html:5570]。）为什么战斗内还要拷：战斗里卡会被打上临时标记（`_locked` 锁死、`_salvaged` 改装），这些标记只该活在「这一场」——下个复制周期自然消失。洗牌 `shuffle`（[index.html:5408]）用的随机数来自局种子（03 篇第 7 节）。

## 5. 抽牌：数组顶端的弹出

抽牌函数 `draw`（[index.html:5679]）每次循环只做两件事：手牌满 10 张就停（`HAND_LIMIT`，[index.html:5373]），否则 `C.hand.push(C.drawPile.pop())`——从抽牌堆**末尾**弹一张进手牌（数组末尾弹出是 O(1)，这就是「堆顶选在末尾」的原因）。抽牌堆空了就把弃牌堆洗回去（[index.html:5685]）。聚能枪此刻以对象身份躺进 `C.hand`。

## 6. 卡面是怎么画出来的

`render`（[index.html:7703]）对手牌逐张建 DOM（[index.html:7874] 起）。聚能枪的卡面上每一块都对应一次字段读取：费用块读 `uiCost(card)`（[index.html:7883]；该函数 [index.html:7575] 现算干旱层加价与遗物改费）；类型字读 `card.type`——`attack` 显示「攻」（[index.html:7884]）；卡面图查 `cardArtId`（[index.html:7311]）→ 素材表 `window.ART`，查不到回落剪影；脉标签读 `card.veins`（[index.html:7888]）；**描述文字**来自 `cardDesc`（[index.html:8108]）——它把 effect 翻译成人话：`if (e.damage) parts.push('伤害 ' + e.damage + (e.hits > 1 ? '×' + e.hits : '') ...)`，所以卡面上那句「伤害 10」不是 json 里存的文案，是引擎**当场从字段算出来**的。风味文字读 `card.flavor` 原样显示（[index.html:7892]）。

## 7. 打出：effect 字段被逐条执行的现场

玩家把聚能枪拖到敌人身上松手 → `doPlay`（[index.html:6966]）→ 引擎 `playCard`（[index.html:5694]）。六道门里聚能枪会走的是能量门（`cardCost` [index.html:5765] 算出 1）。随后 `applyCardEffect`（[index.html:5807]）逐条消费 effect：

| effect 字段 | 谁读 | 在哪行 | 怎么解释 |
|---|---|---|---|
| `damage` | 伤害段 | [index.html:5823] | `if (e.damage)` 为真才进伤害逻辑；数值进 `dmgEach` 公式 |
| `hits` | 同上 | [index.html:5824] | `e.hits \|\| 1`——没写段数就按 1 段 |
| `target` | 同上 | [index.html:5826] | `'all'` 取全部活敌，否则取玩家指定的那只 |
| `veins` | 层规则+连携 | [index.html:5813]、[index.html:5787] | 断光层光脉牌整张作废；主脉计数吃连携加成 |
| `special` | applySpecial | [index.html:5849] | 聚能枪没有，跳过；有的话按 code 分发（[index.html:5852]） |
| `energy`（费用） | cardCost | [index.html:5766] | 出牌前算钱用，不是效果 |

聚能枪的具体一击：`dmgEach = 10 + 连携加成×2 + 力量 + 协议加成`（[index.html:5825]），1 段，打向玩家指定的敌人，`dealToEnemy`（[index.html:5923]）先扣对方格挡再扣血。打完，`playCard` 把它移出手牌、推入弃牌堆（[index.html:5756]-[index.html:5758]），`checkCombatEnd` 看是否全灭（[index.html:5761]）。

升级形态也在这条链上：营火升级选它时 `upgradeCard`（[index.html:6330]）把 `upgrade.effect` 的 `damage: 14` 当**最终值**覆盖（[index.html:6341] 附近），名字加后缀「·改」——之后它卡面描述当场变成「伤害 14」，因为描述是现算的（第 6 节）。

## 8. 加一张新卡：最少要动的地方

按顺序五步，前两步必须，后三步可选：

1. **写数据**：在 `cards/diver.json` 的数组里加一个对象（照抄相邻卡的字段结构，`id` 用未占用的 `dive_XXXX`）。json 是唯一真源。
2. **重建页面**：跑 `node tools/_t46_wire.js`（它把 json 重拼进 [index.html:6391] 的 `RAW`）。卡牌字段与 `_t46_wire.js` 同步的那段在其文件尾部的职业循环里（[tools/_t46_wire.js:20]）。不重建的话，改 json 对游戏**无效**——页面读的是内联的 RAW。
3. （可选）**卡面图**：放一张 `web/assets/art/dive_XXXX.webp`，并在 `window.ART` 表（[index.html:3945] 附近，由 `tools/art_embed.py` 生成）加键。不加也能玩：`appendArt`/`cardArtId` 查不到会回落脉色剪影（[index.html:7321]）。
4. （可选）**开局/商店可见性**：新卡默认就在职业池里，战斗奖励与商店自动可抽（`weightedCards` [index.html:7172] 不需要改）；`special` 稀有度除外（奖励池过滤它，[index.html:7173]）。
5. （可选）**彩蛋/引用**：想让两张卡有组合彩蛋，往 `EASTER_EGGS` 表（[index.html:6994]）加一对 id。

## 9. 只改一个数值呢

把聚能枪伤害从 10 改成 12：**唯一必须改的是 [cards/diver.json:38]** 的 `"damage": 10` → `12`，然后重跑第 8 节第 2 步的重建脚本、刷新页面。如果想临时试数值而不动 json，可以直接改 [index.html:6391] RAW 行里这张卡的 `"damage":10` 字样——但那行是产物，下次重建会被覆盖，试完记得回 json 落账。改完怎么验证：战斗里打出它，飘字会显示 12（飘字数值 = 12 + 连携×2 + 力量，01 篇第 4 节的公式），或先看卡面描述块显示「伤害 12」（[index.html:8108] 现算）。

## 自测题

1. `adaptCard` 第一行为什么要 `JSON.parse(JSON.stringify(src))`？不拷贝直接用原对象会污染什么？
2. 聚能枪不在初始牌库，玩家最早能从哪两个渠道拿到它？
3. 战斗开始时为什么还要把 `run.deck` 再拷贝一遍（[index.html:5570]）？不拷贝会怎样？
4. 卡面上「伤害 10」这行字是从 json 里的哪个字段读的？改了 json 里的伤害但没重建，卡面会变吗？
5. 给新卡起名 `dive_9999`，但 RAW 行里找不到它——最可能是漏了哪一步？

**答案**：1）深拷贝让 `CLASS_POOL` 里的对象与 json 原数据脱钩；不拷的话战斗中打的 `_locked`/改装标记会写进池子，下周目、甚至同局第二次拿到的还是「被改过的卡」。2）战斗奖励三选一（[index.html:7172]）与商店货架（[index.html:6804]）。3）战斗内会有临时标记（锁死/改装），拷贝保证这些标记不回流牌库；不拷的话「本层锁死」会永久粘在这张卡上。4）不直接读字段——是 `cardDesc`（[index.html:8108]）从 `effect.damage` **现算**出来的文字；不重建的话 RAW 没变，卡面不会变。5）漏了重建（第 8 节第 2 步），页面还在用旧的 RAW。

## 决定记录

- 示例卡选 dive_0002 的原因：字段最少且无 special，链路上每个读者（cardCost/applyCardEffect/cardDesc）都能干净地指到行号。
- 「加新卡」步骤中 `_t46_wire.js` 的职责边界按其源码（[tools/_t46_wire.js:9]-[tools/_t46_wire.js:18] 与文件尾职业循环）如实描述；该脚本头部注释自称「T46 一次性 wire」，实际是可重复执行的重建入口，本文按其实际行为表述。
- 卡面回落行为的依据是 `appendArt`/`cardArtId`（[index.html:7311]-[index.html:7340]）与敌人素材的同类回落（[index.html:7802]），未逐像素验证美术缺失时的视觉效果，只断言「查不到会回落」这一代码事实。

## 10. effect 字段读者全表：每个字段被谁读、被怎么解释

把散在主文的「字段 → 读者」收拢成一张总表。同一个字段通常有**三个读者**：引擎（执行）、界面（显示）、文案（翻译）——三个读者读到的字段相同，解释各司其职。

| 字段 | 引擎读者（执行） | 界面读者（显示/校验） | 文案读者（翻译） |
|---|---|---|---|
| `damage` | 伤害段 [index.html:5823] | 拖拽是否需要目标 [index.html:7598] | 「伤害 N」[index.html:8111] |
| `hits` | 段数 [index.html:5824] | —（不参与目标判定） | 「×N」[index.html:8111] |
| `target` | 目标集 [index.html:5826] | 是否拖拽 [index.html:7597] | 「（全体）」[index.html:8112] |
| `block` | 格挡段 [index.html:5834] | — | 「格挡 N」[index.html:8113] |
| `draw` | 抽牌段 [index.html:5838] | — | 「抽 N」[index.html:8114] |
| `resonance_gain` | [index.html:5840] | — | 「共振 +N」[index.html:8115] |
| `resonance_cost` | 出牌门槛+扣费 [index.html:5713]、[index.html:5733] | 拦截文案 [index.html:7591] | 「消耗共振 N」[index.html:8116] |
| `resonance_drain` | [index.html:5841] | — | 「共振 -N」[index.html:8120] |
| `gaze_cost` | 门槛 [index.html:5709] | 拦截文案 [index.html:7589] | 「需要凝视 N」[index.html:8117] |
| `gaze_gain` | [index.html:5843] | — | 「凝视 +N」[index.html:8118] |
| `heal` | [index.html:5846] | — | 「回复 N」[index.html:8119] |
| `special[].code` | 分发 [index.html:5849] → [index.html:5852] | 目标判定 [index.html:7599] | 中文映射 [index.html:8122] |
| `special[].value/v` | 各 case 内 | — | 「N」[index.html:8126] |
| `exhaust`（adapt 后） | 进消耗堆 [index.html:5757] | — | 「消耗」[index.html:8128] |
| `retain`（adapt 后） | 回合末保留 [index.html:5596] 附近 | — | 「保留」[index.html:8129] |
| `energy`（费用） | `cardCost` [index.html:5766] | `uiCost` [index.html:7575] | 费用角标 [index.html:7883] |
| `veins` | 连携 [index.html:5789]、层规则 [index.html:5813] | 脉标签 [index.html:7888]、脉色 [index.html:7371] | 脉字 [index.html:7888] |
| `cost_type` | 代价结算 [index.html:5749] | costly 样式 [index.html:7878]、悬停 [index.html:7893] | 代价文字 `cost_text` [index.html:7892] |
| `upgrade` | 合并 [index.html:6330] | 升级预览 [index.html:6750] | 「·新」后缀 [index.html:6333] 附近 |

这张表的用法是**双向的**：想改显示 → 从文案列查行号；想加新字段 → 三列都要接（只接引擎列，卡面上就不显示；只接文案列，就没有效果）。

## 11. RAW 的全部消费者清单

`RAW`（[index.html:6391]）是数据的总入口，谁在读它、读哪一段，一张表列全（这是「改数据牵动谁」的第一层）：

| 消费者 | 行号 | 读的段 |
|---|---|---|
| `CLASS_POOL` | [index.html:6419]-[index.html:6424] | `RAW.diver/tremor/anmin/cangmin` + `RAW.shared` |
| `layerRows` | [index.html:6511] | `RAW.layers.layers` |
| 旧图节点分发 `resolveNode` | [index.html:6622]-[index.html:6637] | `RAW.anminEvents/cngEvents/events/enemies` |
| 商店抽遗物 `pickRelics` | [index.html:7205] | `RAW.relics/anminRelics/cngRelics` |
| 事件遗物 `pickEventRelics` | [index.html:7194] | `RAW.relics` 的 event 子集 |
| 回响局敌人 `echoEnemyPool` | [index.html:7487] | `RAW.anminEnemies` |
| 二周目赠卡 | [index.html:6480] | `RAW[classId]` 直查 dive_0056 |
| 静态层骨架 `layerRows` 的 fallback | [index.html:6513] | `RAW.layers` 的 nodes |

加上卡面素材的 `window.ART`（[index.html:3945]）与绑定表 `MAPGEN_BINDINGS`（[index.html:974]），数据入口一共三份、消费点十来个。**改任何一段数据前先过这张表**：改动会不会让某个消费者拿到意外形状？最典型的例子是卡池：改 `cards/diver.json` 会同时影响战斗奖励（[index.html:7173]）、商店（[index.html:6806]）、事件发牌（[index.html:7430]）三个消费者——它们共享同一个 CLASS_POOL。

## 12. 一张卡进商店的路线（逐行）

以聚能枪被刷进商店为例：进店时 `resolveNode`/`dispatch` 调 `buildShopStock`（[index.html:6804]）。内部顺序：

1. `weightedCards(2 + (run.rng() < 0.5 ? 1 : 0))`（[index.html:6806]）——决定货架 2 张还是 3 张卡，掷骰用的是**局随机序列**（不是地图种子）。
2. `weightedCards`（[index.html:7172]）内部：池过滤 [index.html:7173]（去 special）→ 按权重表累加 [index.html:7178] → 轮盘抽 n 次、每抽从 bag 移除（无放回，[index.html:7187]）。
3. 抽到的每张按稀有度定价（[index.html:6807]-[index.html:6809]），`shopPrice`（[index.html:6802]）再用一次局随机。
4. 塞进货架数组并配 `desc: cardDesc(c)`（[index.html:6810]）——商店里的描述与战斗内卡面出自同一个翻译器。
5. 玩家点购买：`run.deck.push(Object.assign({}, item.card, { uid: ... }))`（[index.html:6849]）——**这是聚能枪进入 run.deck 的那一刻**，第 4 节的战斗流程从这条路径接上。

这条路线上有两个随机消耗点（第 1 步与第 3 步），所以「商店卖什么」也是局可复现的一部分——但它在局序列上的位置取决于玩家几步进店，重放时要连操作一起重放。这是事件式随机（先到先消耗）与流式随机（序列逐个取）的区别，顺带解释了「种子相同但操作不同则后续完全不同」。

## 13. 改一个字段会牵动谁：传播表

| 你改的字段 | 立即生效的读者 | 需要重建才生效 | 可能被破坏的假设 |
|---|---|---|---|
| `damage`/`block` 数值 | 引擎公式 [index.html:5825]、卡面描述 [index.html:8111] | RAW 行（_t46_wire） | 平衡审计的功率表（`tools/card_power.js` 的历史结论作废） |
| `hits` | 段数循环 [index.html:5829] | 同上 | 力量乘区强度（段数 × 力量） |
| `target` | 目标集 [index.html:5826]、拖拽判定 [index.html:7597] | 同上 | 单体→全体会绕过目标选择（[index.html:8027]） |
| `energy` | `cardCost` [index.html:5766]、角标 [index.html:7883] | 同上 | 冷洞/干旱加价的相对值 |
| `cost_type` | 代价结算 [index.html:5882] | 同上 | cost_redirect 遗物交互（[index.html:5884] 附近） |
| `special.code` | `applySpecial` 分发 [index.html:5855] | 同上 | 未知 code 走 default 红字（[index.html:5874] 附近）——先确认 case 存在 |
| `veins` | 连携主脉 [index.html:5789]、层规则 [index.html:5813]、卡面脉标 [index.html:7888] | 同上 | no_light/dry 层的强弱（光脉换震脉会躲开第 1 层惩罚） |
| `rarity` | 抽卡权重 [index.html:7178]、商店定价 [index.html:6807] | 同上 | `special` 会被奖励池过滤（[index.html:7173]）——改 rarity 是改可见性 |
| `flavor`/`cost_text` | 仅显示 [index.html:7892]-[index.html:7893] | 同上 | 无机制风险，唯一要小心的是 json 引号 |
| `upgrade.effect` | `upgradeCard` 合并 [index.html:6341] | 同上 | special 是**追加**不是替换（[engine/core.js:981]）；空数组清空 |

表的最后一列是每一行真正的重点：**数值可以随便试，牵动「假设」的改动要先想清楚**。第三批施工包（T340-T343）的删卡清单就是在批量处理这张表的最后一列。

## 14. 加新卡的四个常见坑

坑一：**id 撞车**。新卡的 `id` 必须全池唯一——验收脚本 `tools/check_design_refs.py` 与设计文档引用都以 id 为锚；起名前先 grep `cards/*.json`。坑二：**改了 json 忘了重建**。页面读的是 [index.html:6391] 的 RAW 行，不跑 `tools/_t46_wire.js` 的话，json 改得再对页面也不认（04 篇第 8 节的第 2 步）。坑三：**rarity 误写成 special**。special 会被奖励池过滤（[index.html:7173]）、商店也用同一个 `weightedCards`——新卡「做出来了但永远刷不出」几乎都是这个原因。坑四：**special 的 value 字段名写 `value` 还是 `v` 都行但别混用语义**——adaptCard（[index.html:6400]）做了兼容，但 `turns` 只有 burn/weak/frail 认（[index.html:5856]-[index.html:5859]），给 strength 写 turns 是无效数据。

## 15. 你改这里会发生什么（本篇三个修改点）

**修改点一：把 [index.html:7178] 的 `weight[c.rarity] || 1` 改成 `weight[c.rarity] || 0`。**
会发生的连锁：权重表未登记的稀有度从「按 1 处理」变成「按 0 处理」——乘到轮盘 `roll -= 0` 永不减值，等于该稀有度完全抽不到。表面是收紧，实际是**把静默兜底变成静默丢弃**：错拼的稀有度从「莫名其妙地常见」变成「永不出现」，更隐蔽。验证：把某张卡的 rarity 改成 `uncommon `（尾带空格）再看商店——不再出现即复现。教训写在 02 篇第 9 节反例：兜底要放在预期缺失处，不是可能拼错处。

**修改点二：把 [index.html:8111] 的 `'伤害 ' + e.damage` 改成 `'伤害 ' + (e.damage + 1)`。**
会发生的连锁：卡面显示比实际伤害大 1（引擎读原字段，[index.html:5825]）——**显示与执行分家**，玩家按卡面算的连携永远差一点。这是「文案读者」列被单独篡改的示范：三读者表（第 10 节）里只改一列，制造的是最难查的「明明是对的但不对」类 bug。验证：任何一张伤害牌，卡面数字比飘字基值大 1。

**修改点三：把 [index.html:6397] 的深拷贝 `JSON.parse(JSON.stringify(src))` 换成浅拷贝 `{...src}`。**
会发生的连锁：CLASS_POOL 里所有同源卡共享嵌套的 `effect` 对象——`upgradeCard`（[index.html:6341]）对 `c.effect` 的写入、adaptCard 对 `e.special` 的重写都会穿透到 RAW 原对象。下一局（不刷新页面重开）拿到的卡带着上一局的升级状态。验证：升级一张卡后 restart 重开（不刷新页面），开局再拿同名卡看它是否已带后缀。这是 02 篇第 9 节例 C「判据是要改的深度」的事故版。

## 16. 自测补充（五题，接原自测）

6. `resonance_cost` 与 `resonance_drain` 都是「让共振变少」，引擎处理它们的时机有什么不同？（提示：一个在出牌校验段 [index.html:5713]/[index.html:5733]，一个在效果段 [index.html:5841]）
7. 一张 `target: "single"` 但既无 `damage` 也无异常 special 的卡，拖拽时会要目标吗？根据 [index.html:7595]-[index.html:7599] 推导。
8. 商店货架上「删牌服务 75 金」的定价写死在哪一行？它为什么不走 `shopPrice`？
9. 二周目赠送的 dive_0056 是从哪个数据段查到的？（看 [index.html:6480]）
10. `cardDesc` 对 `resonance_lock` 显示什么？若想让它显示「共振锁定（本层）」，要改哪个函数的哪个映射？

**答案**：6）cost 是校验+扣费（不足则拒出牌），drain 是效果（打出去才扣、下限 0）——语义一个是「付费门槛」一个是「效果内的自减」。7）不会——`needsTarget` 要求 damage 或 four 异常码之一（[index.html:7598]-[index.html:7599]），都没有就返回 false，上甩即出。8）[index.html:6817] 的固定 `price: 75`；固定价是服务不是商品，不走稀有度随机。9）从 `RAW[classId]`（[index.html:6480]）——注意它是从**当前职业池**查的，所以二周目赠卡 id 写死为 dive_0056 但对象随职业不同（若该职业池没有此 id 则静默不送，[index.html:6481] 的 `if (ng)`）。10）显示「共振锁定」——映射在 [index.html:8122]-[index.html:8125] 的 `m` 对象，加括号说明改这一处即可（所有卡面同步生效，因为都是现算的）。

## 17. 一场战斗的数据流：从哪进、到哪出

把 01 篇的函数链换成数据视角，一张图看清「什么数据、从哪来、到哪去」：

    输入侧
      cards/*.json ──(tools/_t46_wire.js)──> RAW [index.html:6391]
      RAW ──(CLASS_POOL+adaptCard)──> 职业池 [index.html:6420]
      职业池 ──(奖励/商店/事件三条路)──> run.deck
      run.deck ──(startCombat 拷贝+洗牌 [index.html:5570])──> C.drawPile
      C.drawPile ──(draw 弹栈 [index.html:5691])──> C.hand
    状态侧（战斗容器 C，[index.html:5512] 起）
      C.energy / C.resonance / C.block / C.buffs / C.enemies[].hp
      每次出牌被 playCard 改写，每次回合被 beginTurn/endTurn 改写
    输出侧
      C.hand ──(出牌 [index.html:5756])──> C.discardPile 或 C.exhaustPile
      C.discardPile ──(抽空时洗回 [index.html:5685])──> C.drawPile
      C.enemies[].hp 到 0 ──(checkCombatEnd [index.html:6163])──> C.over
      C.over ──(finishCombat [index.html:6178])──> 金币/零件 → run
      run ──(restart [index.html:6494])──> 全部丢弃（无持久化）

三个观察：① **牌的旅程是一个环**（deck → drawPile → hand → discard → drawPile），exhaust 是环上唯一的出口，memory 代价是环外直接删；② **run 是唯一的跨战斗持久层**，且只持久到刷新页面（输出侧最后一条）——没有存档这件事在数据流上就是「restart 丢弃一切」；③ 敌人数据不进环——每场从 `RAW.enemies`（经绑定表）现场实例化（[index.html:5543] 附近），打完即弃。

## 18. uid 与双份对象：改手牌要不要同步牌库

04 篇主文讲过战斗开始时的第二次拷贝（[index.html:5570]），这里把「同一张卡的三份实体」讲透：池子里一份（CLASS_POOL，只读真源）、牌库一份（run.deck，会带改装）、战斗内一份（C.drawPile/hand，带临时标记）。三份靠 `uid` 认亲——`salvageUpgrade` 改装手牌时，靠 uid 找回 run.deck 里的原件同步改（[index.html:5870] 的 `find` 在引擎侧 [engine/core.js:870]），否则战斗结束手牌销毁、改装白费。

推论：**改「手牌内」的临时属性不用同步，改「永久」属性必须找原件**。`_locked` 是临时的（战斗容器销毁即消失），改装是永久的（要同步 run.deck）。你以后写任何「战斗中改变卡」的功能，第一个要回答的问题就是：这个改变是本场还是永久？——答案决定你要不要写同步。

## 19. 导出侧：docs/content 是谁产的

json 还有第三个方向的消费者：导出脚本把数据变成人类可读的 md（`docs/content/cards_*.md` 等，README 写明「脚本生成勿手改」）。这一层的意义是**给非程序员的你一份可检索的卡表**——它与游戏的关系是「同一份数据的两种呈现」，所以永远以 json 为准、md 只读。验收脚本（`tools/check_design_refs.py`）核对卡 id 时直接读 json（[tools/check_design_refs.py:57] 附近的 `real_card_ids`），绕过了所有呈现层——这也是「md 可能滞后、json 不会」这句话的出处。

## 20. 你改这里会发生什么（第二批修改点）

**修改点四：把 [index.html:5596] 附近回合末保留判断里的 special 检查删掉一半（只认 `effect.retain`）。**
会发生的连锁：adaptCard 把 special 里的 retain 提升成 `effect.retain`（[index.html:6405] 附近），所以引擎只看顶层标志也没错——但 buildStarterDeck 现造的基础牌若手写了 `special:[{code:'retain'}]` 而没走 adapt（[index.html:5457] 的对象是原样进牌库的），保留就失效。这个修改点演示「兼容层的存在允许了两种数据形态并存」，删一半防御要看另一形态还有没有生产者。

**修改点五：把 [index.html:6489] 的 `run.gold = 0;` 删掉。**
会发生的连锁：看起来金币要变成 undefined——实际什么都不会变，因为 `newRun` 建局对象时已经写了 `gold: 0`（[index.html:5443]），startRun 这行是**对同一份初始化的第二次书写**。这个修改点教的是「冗余初始化的识别」：两处赋值一前一后、值相同，删掉前一处零影响；但若哪天有人改了 newRun 的初始金币而忘了这里还有一行 0，startRun 会把它静默盖掉——冗余的真正风险不是现在坏，是未来某次单边修改时坏。验证：删行后开局看金币仍为 0；再临时把 [index.html:5443] 改成 `gold: 50` 试「哪一层生效」——结果是 0（startRun 后写），答案就在赋值顺序里。

## 21. 加新卡检查单（打印版）

- [ ] id 在全池唯一（grep `cards/*.json`）
- [ ] 字段齐全：id/name/class/type/rarity/veins/energy/effect/cost_type/flavor
- [ ] special 用对象形态 `{code, value}`（兼容层虽在，别依赖裸字符串）
- [ ] rarity 不是 special（除非明确要它不可获取）
- [ ] upgrade 写了「最终值」语义（special 追加语义想清楚，[engine/core.js:981]）
- [ ] 跑 `node tools/_t46_wire.js` 重建
- [ ] 刷新后：商店/奖励能刷出、卡面描述正确、拖拽目标判定正确（needsTarget 三条件，[index.html:7595]）
- [ ] 文档同步：`docs/content/` 重导出，设计文档引用补 id

## 22. 第三条入手路：事件发牌的 follow 循环

主文讲了奖励与商店，第三条路是事件。事件选项的 `result.card_reward` 只存**稀有度字符串**（如 event_d2_1 的 uncommon），结算在 `chooseEventOption`（[index.html:7388]）：先按 `heal/damage/gaze/gold/maxhp` 顺序结清即时资源（[index.html:7392]-[index.html:7399]），再把 `card_reward`/`relic` 推进 follow 队列（[index.html:7400]-[index.html:7402]），然后 `doFollow`（[index.html:7411]）逐项消费——发牌走 `cardsOfRarity`（[index.html:7429]），它按稀有度**精确匹配**职业池（[index.html:7430] 的 `filter(c => c.rarity === rar)`），池子空了才回退到非 special 全集（[index.html:7431]）。

与商店路线的差异有两处值得记住：其一，事件发牌**不花局随机在权重上**（稀有度是选项写死的），随机只花在同稀有度内选哪张（[index.html:7434]-[index.html:7436] 的 splice 抽取）；其二，事件卡是 `mustPick`（[index.html:7419] 的 `showCardChoice(..., true, ...)`）——不给放弃选项，这是事件作为「强 encounter」的规则表达。

## 23. 数据校验清单：加载时没人替你检查什么

`JSON.parse` 只保证「语法合法」，不保证「游戏能跑」。以下错误全部能通过语法检查、在游戏里以各种姿势爆炸——每一类都给出它实际会炸的位置：

| 数据错误 | 会炸的位置 | 症状 |
|---|---|---|
| `effect` 整个漏写 | [index.html:7596] `card.effect` 读 target | 详情面板空白、出牌直接进效果零段 |
| `rarity` 拼错 | [index.html:7178] 权重兜底 | 该卡按权重 1 混入，且三选一永不匹配稀有度（[index.html:7430]） |
| `veins` 写了非五脉字符串 | [index.html:5789] 过滤后空 | 无连携、脉标签显示「?」（[index.html:7888] 的 `VEIN_CN[v] || '?'`） |
| `upgrade.effect` 写了增量而非最终值 | [index.html:6341] | 数值错但无报错（升级后伤害变成「基础+增量」语义错乱） |
| special 的 code 拼错 | [index.html:5874] 附近 default | 红字「这一版还没做」——唯一会大声说话的错误 |
| `id` 重复 | 任何按 id 反查的代码 | 后者覆盖前者（对象字面量同键覆盖，数组则并存但引用混乱） |

这张表的写法值得学：**每行都是「错误 → 首个受害者 → 玩家可见症状」**。自己扩展数据时照表自查一遍，比跑游戏穷举快得多。

## 24. 三份数据的生命周期对照

卡、敌人、事件三类数据的生命周期并不同构，对照着看能防止「想当然迁移经验」：

| | 卡 | 敌人 | 事件 |
|---|---|---|---|
| 真源 | `cards/*.json` | `enemies/all.json` | `events/all.json`（+职业事件池） |
| 进入内存 | RAW → CLASS_POOL（adaptCard 深拷贝） | RAW → 绑定表 → startCombat 实例化 | RAW → showEvent 直读 |
| 战斗中的形态 | 三份实体（池/牌库/战斗内，靠 uid 认亲） | 实例带 `status`/`intent` 运行时字段（[index.html:5543] 附近） | 无战斗形态——结算完即弃 |
| 持久化 | 进 run.deck 跨战斗 | 不持久（每场重新实例化） | 不持久（选项结果一次性写进 run） |
| 刷新页面后 | 从 json 重来 | 同左 | 同左 |

最大的不对称在「持久化」一行：卡是唯一跨战斗存活的数据，这就是为什么改卡的连锁最大（第 13 节传播表的复杂度远超敌人/事件）——**持久的东西才有累积效应**。事件数据的改动连锁最小（改 option 文案与数值只影响一次结算），适合作为你第一次改数据的练习对象。

## 25. 跨战斗的三个数：金币、零件、凝视去哪了

牌的旅程之外，三个数值横跨战斗与流程层，去向各不相同——这是「改数据牵动谁」的进阶案例：

| 数值 | 产生点 | 消费点 | 刷新后 |
|---|---|---|---|
| 金币 run.gold | 战斗掉落 [index.html:623]（引擎 finishCombat）、boss 奖励 [index.html:7155]、事件 [index.html:7395] | 商店 [index.html:6846]、黯民折算零件 [index.html:7119] | 清零（startRun 重置 [index.html:6489]） |
| 零件 run.parts | 击杀掉落 [index.html:5937]、金币折算 [index.html:7119] | 改装 [index.html:6221]、拆解 [index.html:6238] | 清零；但战斗内的 C.parts 要手动写回（[index.html:6886]） |
| 凝视 run.gaze | mark 代价 [index.html:5887]、事件 [index.html:7394]、敌人 gift [index.html:6152] | 出牌门槛 [index.html:5709]、敌人伤害放大 [index.html:6093]、结局 [index.html:6211] | 清零；但决定结局与回响解锁（[index.html:7463]）的是当局值 |

三个数值共同点是**双容器问题**：金币/零件在 run 与 C 各有一份（战斗内掉落先记在 C.parts，战斗结束写回 run），凝视只在 run。双容器就要同步——[index.html:6886] 与 [index.html:7119]-[index.html:7120] 的写回就是同步点，漏掉的话「本场捡的零件」在结算时蒸发。凝视没有这个问题，因为它从不进战斗容器——引擎通过 `C.run.gaze` 直接读写 run（[index.html:5843] 附近）。**放哪个容器」是一个真实的设计决策**：跨战斗的放 run，战斗内的放 C，两端都要动的要写同步。

## 26. 把本篇读薄

一张卡的一生压缩成四句话：json 是唯一真源；`_t46_wire.js` 把它搬进页面；`adaptCard` 深拷贝后进池；三条入手路（奖励/商店/事件）把它送进 run.deck，战斗内再拷两道、打完回弃牌堆、刷新一切归零。effect 的每个字段有三个读者（引擎执行、界面校验、文案翻译），加字段三处都要接，删字段三处都要拆——第 10 节的总表就是这句口号的展开。

## 27. 决定记录补遗

- 第 12 节商店路线中「掷骰用局随机序列」的判断依据是 `buildShopStock` 与 `shopPrice` 直接调用 `run.rng`（[index.html:6802]、[index.html:6806]），未实测重放验证（需要记录种子并重放操作序列），断言的是代码路径而非端到端实测。
- 第 23 节「症状」列来自对相应读者代码的静态推导，未逐条人为构造坏数据验证；风险最高的一条（id 重复）建议真机复现一次再依赖该结论。
- 第 24 节对照表的事件池维度：主池 82 个事件之外还有 cangmin/anmin 两个 10 事件的职业池（[index.html:6622]-[index.html:6630]），表中「不持久」的结论对三者一致。

## 28. 常见问答：改数据前的四个高频疑问

**问一：我可以把一张卡从一个职业的 json 挪到另一个吗？**
文件层面可以（`class` 字段与所在文件一致即可，CLASS_POOL 按文件组装），但三处连锁要跟：卡面美术键 `cardArtId`（[index.html:7311]）按 id 查表与职业无关，无需改；卡面描述 [index.html:8108] 无职业概念，无需改；设计文档与验收引用（`docs/content/cards_*.md`）要重导出。真正的成本在设计层——职业卡池的机制语言差异（T320 的骨架分析）会被一张挪动的卡破坏。

**问二：`cost_text` 什么时候显示？**
悬停提示与出牌音效的组合：`d.title` 在 [index.html:7893] 拼 `card.cost_text`，出牌时 [index.html:6976] 检测有代价则补一声代价音效。它**不进卡面描述**（cardDesc 不读它）——因为代价由引擎统一结算（[index.html:5882]），显示层只在悬停时提醒。改 cost_text 纯文案，零机制风险。

**问三：为什么有的卡没有 upgrade 字段也能玩？**
upgrade 是可选的：`upgradeCard` 遇到无 upgrade 的卡直接返回 null（[index.html:6331] 的 `if (!up ...) return null`），营火升级选牌池的过滤条件 [index.html:6735]（`c.upgrade && !c.upgraded`）会自动把它排除。所以「没有 upgrade」=「不能在营火强化」，不是错误——全池有 6 张这样的收官卡（04 篇主文 T321 提过 dive_0081-0083/trem_0081-0083）。

**问四：veins 能写两个脉吗？**
json 层能写，引擎**只认第一个**：连携取主脉 `vs[0]`（[index.html:5789]），层规则检查用 `indexOf`（只要包含就命中，[index.html:5813]）——所以双脉卡在「层规则」上是两脉全占（no_light 层会拦、dry 层会加价），在「连携」上只算首脉。这个不对称是当前引擎的真实行为，也是 T331 设计桥梁牌时声明的引擎改动点（[engine/core.js:429]）——在设计文档里读到「双脉」三个字时，记得它现在的真实含义是「层规则双脉、连携单脉」。

## 29. 决定记录补遗（第二批）

- 第 28 节问四的双脉行为是本次扩写时逐行复核的结果，与 T331 的设计声明有意区分——「引擎现状」与「设计意图」在文档里用不同措辞，避免读者把草案当实现。
- 第 25 节表格的三行「刷新后清零」结论来自 startRun 的全量重置（[index.html:6484]-[index.html:6490]），凝视行「当局值决定结局」另见引擎 `pickEnding`（[engine/core.js:849]）。
- 本篇两次提到「T321 的六张无升级卡」，其准确成员清单以第一包 T321 的决定记录为准（dive_0081-0083、trem_0081-0083），本篇只引结论不重抄清单。

## 30. 最后一个思维工具：改数据前先问「它在哪个容器」

本篇出现过四个容器：池（CLASS_POOL）、牌库（run.deck）、战斗（C）、页面显示（render 现算）。任何一次改动的第一步都是回答「我要改的东西在哪个容器里」——

- 改**效果与数值** → 真源 json（三容器重建时都会跟上）；
- 改**本场行为** → 战斗容器 C（不用动数据）；
- 改**获取概率** → 消费者层（weightedCards/shopPrice/事件表）；
- 改**显示** → cardDesc/render（现算层）。

答错容器的典型事故：想给某张卡「只在这一层加强」，却去改了 json 数值——结果是全局加强。正确位置在引擎的层规则段（[index.html:5820] bright 的写法就是现成模板）。这个思维工具与 00 篇第五节的检索表配合：检索表找到函数，容器判断找到数据落点，两者对上才动手。

四句话的版本：**数值去 json，时机去引擎，概率去消费者，样子去渲染**。四句对上，加卡改卡的每一步都在正确的容器里发生——这也是教学包用四篇（01 函数链、02/03 语法、04 数据）围住同一个游戏的原因：同一个「改一次伤害」的动作，在每一篇里都会以不同的容器视角再走一遍，走到第四遍时它就是你的肌肉记忆了。

（本篇完。下一页 05 是动手练习——到这里，你已经具备把练习二做到「知道每一步为什么」的程度。）
（本篇完。下一页 05 是动手练习——到这里，你已经具备把练习二做到「知道每一步为什么」的程度。）
