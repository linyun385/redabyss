# T323 · 规则说明书（从代码提取）

> 本文只写**代码里实际生效的规则**。战斗规则以 `engine/core.js`（1026 行）为准，流程规则以 `web/index.html` 里的流程函数为准（文档如 `docs/BALANCE.md` 一律不作为依据）。每条规则都给 `[文件:行号]`。读不懂的地方直说没看懂。

## 〇、总表

| # | 规则 | 代码位置 |
|---|---|---|
| 1 | 一局结构：开档、初始牌库、地图、层推进 | [engine/core.js:62]、[web/index.html:6461]、[web/index.html:6510]、[web/index.html:6649] |
| 2 | 战斗流程：回合开始→出牌→回合结束→敌人行动 | [engine/core.js:146]、[engine/core.js:229]、[engine/core.js:332]、[engine/core.js:649]、[engine/core.js:728] |
| 3 | 能量与费用 | [engine/core.js:14]、[engine/core.js:403] |
| 4 | 共振 | [engine/core.js:301]、[engine/core.js:29] |
| 5 | 凝视 | [engine/core.js:644]、[engine/core.js:731]、[engine/core.js:849] |
| 6 | 脉（veins）与连携 | [engine/core.js:10]、[engine/core.js:425] |
| 7 | 代价类型 cost_type | [engine/core.js:520] |
| 8 | 升级 | [engine/core.js:968]、[web/index.html:6728] |
| 9 | 遗物触发 | [engine/core.js:215]、[web/index.html:6903]、[web/index.html:7106]、[web/index.html:7214] |
| 10 | 战斗结束与结算 | [engine/core.js:801]、[engine/core.js:816]、[web/index.html:7101]、[web/index.html:7145] |

## 1. 一局的结构

**开档**：`newRun(classId)` 按职业定初始生命——下潜者 80、维护者 76、震语者 72、疯先知 30（[engine/core.js:65]）。疯先知额外带清醒度 clarity=3/上限 5 与梦境生命 60（[engine/core.js:82]）。初始牌库：疯先知是 10 张「醒/梦」双世界牌（清醒侧石矛×2+缩进岩洞×3，梦境侧火母的低语×3+火母的注视×2，[engine/core.js:113]）；其余三职业是「一击」×5 +「缩起」×4 + 职业签名牌×1（[engine/core.js:123]）。前端在开局后额外补 2 张池牌（每周目固定 id，如 diver 补 dive_0053、dive_0019；[web/index.html:6465]），通关过一次后补 1 张并赠送 dive_0056（[web/index.html:6477]）。

**地图**：实际生效的是**运行时程序生成**。T56 新地图模块（一个从 [web/index.html:8303] 开始的 IIFE）在 [web/index.html:8913] 接管了 `window.showMap`：老面板（`showMap`，[web/index.html:6545]）先照常绘制，随后被替换为 `initRun()`（[web/index.html:8660]）调用程序化生成器 `generate()`（[web/index.html:5299]，生态带、DAG 生长、绑定表校验，参数默认值 [web/index.html:4035]）产出的节点图（drawMap，[web/index.html:8410]），玩家在节点间沿**出边**走（可走 = 当前节点的出边终点，[web/index.html:8960]），死路触发回溯救援（[web/index.html:8938]）。旧的静态行数据 `layerRows()`（[web/index.html:6510]，读 `RAW.layers`）没有退役：它仍决定奖励结算的节点类型与进度文案。种子默认随机，URL 带 `?mapseed=` 可复现（[web/index.html:8661]）。

**层推进**：每走完一行 `advanceNode()` 把 row 归 -1、depth +1（[web/index.html:6649]）；depth 超过 8 触发 `showVictory()`（[web/index.html:6655]）。8 层的定义表在 [engine/core.js:17]：每层有名称、共振资源量 res（1→8 线性）、模式 mode（共振阈值反应用）与规则 rule（no_light/cold/dry/bright/heat_tick/rad_tick/burn_hand/final）。层规则对卡牌的影响在引擎里四处生效：no_light 使光脉牌整张无效（能量照扣，[engine/core.js:451]）、dry 使水脉牌 +1 费（[engine/core.js:406]）、cold 使每回合第一张牌 +1 费（[engine/core.js:408]）、bright 给光脉牌效果 +2（[engine/core.js:458]）、heat_tick 每 3 回合灼 2 血、rad_tick 每回合 1 伤换 1 抽、burn_hand 每回合随机烧掉一张手牌进消耗堆（[engine/core.js:274]）。

## 2. 战斗流程

**进入战斗**：`startCombat` 实例化敌人（血量按 "8-10" 这种区间随机，[engine/core.js:55]）、洗牌（疯先知把牌库拆成醒/梦两堆，抽牌堆先取清醒堆，[engine/core.js:202]）、给每个敌人设初始相位与第一张意图（[engine/core.js:210]）、结算遗物 combat_start（[engine/core.js:215]），然后 `beginTurn`。

**回合开始**（[engine/core.js:229]）：① 未保留的手牌全部进弃牌堆（`retain` 的牌留下，[engine/core.js:234]）；② 抽 5 张（静默协议下少抽 1，[engine/core.js:241]）；③ 共振 += 当前层 res（[engine/core.js:243]）；④ 疯先知在梦中每 3 回合扣 1 清醒度，归零强制醒来（[engine/core.js:246]），并 roll 一个 3 回合后结算的预兆（[engine/core.js:952]）；⑤ 层环境 tick（灼烧/辐射/烧手牌，[engine/core.js:269]）；⑥ 共振阈值检查；⑦ 能量回满 = 3 + 遗物加成 − 惩罚（[engine/core.js:258]）；⑧ 连携计数清零（[engine/core.js:263]）。

**出牌**（[engine/core.js:332]）：校验顺序是能量→凝视门槛→共振消耗→锁死→（疯先知）世界匹配→（黯民）协议重复，全过则扣能量、扣共振、算连携加成、结算效果、结算代价、牌进弃牌堆（消耗牌进消耗堆，[engine/core.js:394]）。手牌上限 10（[engine/core.js:12]），抽牌时弃牌堆空了就把弃牌堆洗回抽牌堆（[engine/core.js:321]）。

**回合结束**（[engine/core.js:649]）：记录本回合出牌数供 mirror 意图参考（[engine/core.js:652]）→ 依次敌人行动（[engine/core.js:728]）→ 结算敌人身上的灼烧/中毒/虚弱/脆弱倒计时（[engine/core.js:666]）→ 格挡清零（遗物 keep_block 时留一半，[engine/core.js:680]）→ 回合数 +1 → 检查敌人相位切换与发新意图 → 回到回合开始。

**敌人行动**（[engine/core.js:728]）：攻击值 = 意图值 + 自身 buffAtk，乘凝视系数（见 §5），weak 状态乘 0.75（[engine/core.js:745]）；`pierce` 意图无视格挡直扣生命（[engine/core.js:749]）；玩家荆棘按次反弹（[engine/core.js:766]）。defend 加敌方格挡；buff 给自己叠 buffAtk（静默协议可驳回，[engine/core.js:772]）；debuff 分四种：偷玩家手牌进弃牌堆（steal）、给玩家抽 1 牌+凝视 1（gift）、给玩家上 weak/poison/burn（[engine/core.js:794]）。

## 3. 能量与费用

基础能量 3（[engine/core.js:14]），每回合回满。动态费用只有三处：干旱层水脉 +1（[engine/core.js:406]）、冷洞层每回合首张 +1（[engine/core.js:408]）、遗物对特定脉的费率修正（[engine/core.js:416]）。没有「本回合能量随 X 增长」之类的动态模型——能量是常数加常数修正。

## 4. 共振是什么

**涨**：每回合开始自动 +当前层 res（1-8，[engine/core.js:243]）；卡牌 resonance_gain（[engine/core.js:478]）。**花**：卡牌 resonance_cost 在出牌校验时扣（[engine/core.js:371]）。**减**：resonance_drain 卡（[engine/core.js:479]）。

**跨阈值**：共振到 10/20/30 各触发一次当层模式的反应（[engine/core.js:301]，反应表 [engine/core.js:29]）——休眠层无反应；稳定层回 3 血；脉冲层全体敌人 5 伤；共振层抽 2 张；过载层敌人攻 +3；锁定层本回合能量 −1；虚空层脉锁死（之后连携归零，[engine/core.js:36]）。已触发的档数记录在 resonanceFired，不重复触发。**共振超过 30 后每回合按层 res 自伤**（[engine/core.js:311]）——共振是「想攒但攒过头会烧自己」的资源。

**没生效的部分**：special `resonance_lock` 只把 `C.resonanceLock` 写成 true（[engine/core.js:502]），全代码（引擎与前端）没有任何地方读这个标志——dive_0016、dive_0023、dive_0073、trem_0019、anm_0020、anm_0027 六张卡的「锁定共振」目前是空操作。这不是猜测，是 grep 全量核对的结果。

## 5. 凝视是什么

**涨**：mark 代价 +1（[engine/core.js:542]）；敌人 gift 意图 +1（[engine/core.js:788]）；遗物 combat_start 的 gaze 动作（[engine/core.js:219]）；卡牌 gaze_gain（[engine/core.js:481]）。**花**：gaze_cost 是出牌门槛而非扣减——出牌时只检查 `run.gaze >= gaze_cost`（[engine/core.js:347]），不消耗；唯一扣凝视的是 gaze_reduce（[engine/core.js:503]）。

**后果**：每 10 点凝视让所有敌人伤害 +10%（[engine/core.js:731]）——凝视是全局负债。**与结局的关系**：通关时按凝视分三种结局：≥20「长审」、≤5「背身」、其余「同行」（[engine/core.js:849]）；另有前端「回头」按钮主动放弃（[web/index.html:7541]）与死亡时凝视 ≥15 解锁黯民短局「静默段」（[web/index.html:7463]）。

## 6. 脉（veins）系统

五种脉：light/water/heat/tremor/mineral（[engine/core.js:10]）。卡的 `veins` 数组取第一个合法脉为「主脉」。**连击**：同回合同主脉的第 1 张加成 0、第 2 张 +1、第 3 张起 +2，遗物可加固定值（[engine/core.js:440]）；连携加成 ×2 后直接折进伤害与格挡（[engine/core.js:448]）。脉锁死（虚空层反应或每回合重置，[engine/core.js:426]）时连携恒 0。无脉牌不参与连携且会把 lastVein 置空（[engine/core.js:428]）。连携计数每回合清零（[engine/core.js:263]）——脉没有跨回合状态。

## 7. 代价类型

`cost_type` 实际生效四种（[engine/core.js:520]）：**memory**——从牌库随机删除一张（[engine/core.js:533]，真删 run.deck）；**vitality**——最大生命 −1（不可恢复，[engine/core.js:537]）；**mark**——凝视 +1（[engine/core.js:542]）；**lock**——本层只能用一次（打完打上 `_locked`，[engine/core.js:546]，进入下一层才解除）。遗物的 cost_redirect 改则可以把非 lock 代价整体改写成凝视 +2（[engine/core.js:522]）。

## 8. 升级

入口只有营火「修整装备」：可选池 = 牌库里**有 upgrade 字段且未升级**的卡（[web/index.html:6735]），选后调 `upgradeCard` 替换牌库里的卡对象（[web/index.html:6755]）。合并语义（[engine/core.js:968]）：`upgrade.effect` 的数值为**最终值**（不是增量）；顶层键直接覆盖；`special` 数组是**追加**，升级里写空数组则清空原 special（[engine/core.js:980]）；`cost_type` 可被改写；flavor_add 拼接。没有升级费、没有升级次数限制（除每张卡一次）。

## 9. 遗物怎么触发

遗物带 `effect_code` 数组，trigger 实际被消费的有四种：**combat_start**（战斗开始，引擎处理 draw/gaze/block 三种动作，[engine/core.js:215]）、**turn_start**（玩家回合开始，前端处理 heal/resonance/draw，[web/index.html:6906]）、**on_kill**（战斗结束按击杀数回血，[web/index.html:7107]）、**run_start**（获得遗物时加最大生命，[web/index.html:7216]）。另一套 `mod` 改则被引擎五处消费：vein_cost 费率（[engine/core.js:416]）、chain_bonus 连携（[engine/core.js:436]）、keep_block 半保留格挡（[engine/core.js:680]）、cost_redirect 代价改写（[engine/core.js:523]）。

## 10. 战斗结束与结算

**胜负判定**：全敌死→win，玩家 hp≤0→lose（[engine/core.js:801]）。**引擎侧结算**（[engine/core.js:816]）：疯先知在梦中胜利则清醒度 +2；胜利发 20-40 金币，黯民除外（黯民用零件：击杀即按 tier 掉落 1/2/4/10，[engine/core.js:573]）。**前端结算**（[web/index.html:7101]）：on_kill 遗物结算、黯民零件写回与金币折算、拆解奖励的随机遗物；然后按节点类型发奖励——普通战→3 选 1 卡（稀有度权重 6/3/1，[web/index.html:7174]）、精英→卡+遗物、boss→必选遗物（8 层前再加 50-80 金，[web/index.html:7155]）。**事件结算**（[web/index.html:7388]）支持 heal/damage/gaze/gold/maxhp/card_reward/relic 七种结果字段，黯民把金币折算成零件（[web/index.html:7396]）。**篝火**三选一：静日回 50% 最大生命（疯先知附加清醒 +1，[web/index.html:6689]）、升级一张卡（无可升时给遗物或 50 金，[web/index.html:6697]）、删一张牌（[web/index.html:6713]）。**商店**（[web/index.html:6804]）：2-3 张按稀有度定价的卡（普通 40-60 / 罕见 75-110 / 稀有 150-200）、1 件遗物（120-160 或 250-320）、删牌服务 75、回 35% 生命的合剂 60。**死亡**（[web/index.html:7441]）统计并展示 hint；**胜利**（[web/index.html:7508]）按 §5 结局表出文案并记录通关。

## 附：本文没看懂 / 未展开的三处

1. `salvageUpgrade` 的 `origin` 卡查找用 uid 在 run.deck 里匹配（[engine/core.js:870]），但战斗中的手牌是 `Object.assign({}, c)` 拷贝（[engine/core.js:208]），uid 虽随拷贝保留，若同名牌被补位/购买产生重复 uid 的路径我没看懂——不影响规则描述，仅备注。
2. ~~程序化 mapgen 如何与静态 rows 共存，我没看懂~~ 初版时没看懂；补查 [web/index.html:8913] 后已查明：T56 模块用猴子补丁覆盖 `window.showMap`，默认显示链路走程序化生成，静态 rows 只服务奖励类型判定——§1「地图」段已按此改写。
3. `threatLevel` 字段在 dismantle 里 +1（[engine/core.js:880]），但我没找到它被读取并产生实际效果的位置，注释里说「威胁等级上调」的实际效果是给剩余敌人 buffAtk +1（[engine/core.js:881]）——字段本身疑似只作展示。

## 决定记录

- 本文的「实际生效」判定标准：引擎/前端代码中被读取并产生效果的才写；只写不读的（resonanceLock、traits 空数组）单独标注为未生效，不当作规则描述。
- 文档类材料（docs/BALANCE.md、docs/FEEL.md、docs/ENDINGS.md）一律未引用；ENDINGS 文案以 [engine/core.js:831] 的常量表为准。
- 敌人意图的 `times`（多段）与 `mirror`/`drain_discard`/`pierce` 修饰字段在 enemies/all.json 的 intent_pattern 内出现，其消费逻辑在 [engine/core.js:728] 一并描述，未单列一节。
- 三处没看懂的地方按任务要求如实列出（见「附」），未做任何推测性补全。
