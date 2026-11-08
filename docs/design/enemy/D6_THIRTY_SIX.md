# D6 · 敌人行为设计（36 个新敌人，按层分布）

> 口径：全部使用引擎已实现的意图类型（attack/defend/buff/debuff）与修饰（times/mirror/pierce/drain_discard/steal/gift，消费逻辑在 [engine/core.js:728]-[engine/core.js:799]）；与现有 113 只零重名（脚本对 enemies/all.json 全量核对）；行为/变强/反制三段必填。

## L1（本层 5 个新设计）

### 悬盐线虫（normal · hp 5-7）

| 项 | 内容 |
|---|---|
| intent_pattern | `[{"type": "attack", "value": 2}, {"type": "debuff", "status": "weak", "value": 1}]` |
| 怎么行动 | 挂在盐晶之间的一条细线虫，攻击后下一轮必定吐一次弱化盐雾——行动循环是「打一下、吐一下」的两拍。 |
| 什么情况下变强 | 不单独变强；与悬盐线虫×2 同场时第二只的 weak 值 +1（成对加成，intent_pattern 由绑定侧替换）。 |
| 玩家怎么反制 | weak 只影响玩家攻击（×0.75），不影响格挡——高格挡回应即可无视；先杀一只解除成对加成。 |

### 倒挂的警示灯（normal · hp 6-8）

| 项 | 内容 |
|---|---|
| intent_pattern | `[{"type": "attack", "value": 3}, {"type": "defend", "value": 2}, {"type": "attack", "value": 3, "times": 2}]` |
| 怎么行动 | L2 倒吊串的前身：一盏还在闪的警示灯倒挂在矿道顶。三拍循环，第三拍双段。 |
| 什么情况下变强 | 血量低于 40% 时闪灯频率加快——第三拍变 times=3（phase 条件 hp_above=0.4 换 pattern）。 |
| 玩家怎么反制 | 双段/三段攻击吃满格挡的单段减免——每段分开算；在它 defend 拍打穿透伤害无效（引擎无玩家 pierce），用 burn 让它在 defend 拍也在掉血。 |

### 记名的雾（normal · hp 7-9）

| 项 | 内容 |
|---|---|
| intent_pattern | `[{"type": "debuff", "status": "steal"}, {"type": "attack", "value": 4}]` |
| 怎么行动 | 一团带编号的雾。第一拍从手里偷走一张牌（进弃牌堆），第二拍用它偷来的心情打你。 |
| 什么情况下变强 | 偷到的牌在它体内「记名」：偷过 2 张后攻击值 +2（替代式成长，用 buff 意图实现：偷两次后自动插入一次 buff）。 |
| 玩家怎么反制 | 偷牌只进弃牌堆不消失——下回合洗回来；在它 attack 拍前把弃牌堆清空（多打牌）可以稀释它的输出。 |

### 管底吸盘垫（elite · hp 14-18）

| 项 | 内容 |
|---|---|
| intent_pattern | `[{"type": "defend", "value": 5}, {"type": "attack", "value": 6}, {"type": "buff", "value": 2}]` |
| 怎么行动 | 吸附在管道底部的垫状精英：先上盾、再吸、再给自己上攻。它 defend 的那一拍是玩家换位的窗口。 |
| 什么情况下变强 | buff 叠到 3 层后进入「吸食态」：attack 值 +4 且附带 drain_discard（吸食玩家的弃牌）。 |
| 玩家怎么反制 | silent 协议直接驳回它的 buff（[engine/core.js:772]）；burn 让它的 defend 拍也亏血；在 buff 第 2 层前集火。 |

### 熄灯人（normal · hp 8-11）

| 项 | 内容 |
|---|---|
| intent_pattern | `[{"type": "attack", "value": 3}, {"type": "debuff", "status": "burn", "value": 2}]` |
| 怎么行动 | 把倒挂警示灯一颗颗拧灭的人形剪影。它的 burn 是「把灯的余烬塞给你」。 |
| 什么情况下变强 | 每熄灭一盏同场敌人（任意敌人死亡时），它的下次 attack +1——L1 的「死亡加速器」。 |
| 玩家怎么反制 | 别用它当输出跳板：先杀熄灯人，再清其余；它的 burn 2×2 可用 L5 前唯一的解法硬吃（血量换）。 |

## L2（本层 5 个新设计）

### 冷凝鳃筒（normal · hp 12-15）

| 项 | 内容 |
|---|---|
| intent_pattern | `[{"type": "attack", "value": 5}, {"type": "defend", "value": 6}]` |
| 怎么行动 | 一节从洞顶垂下来的鳃筒，鳃片开合=攻击/防御交替。两拍循环，节奏极稳。 |
| 什么情况下变强 | 每次 defend 后下一拍 attack 临时 +2（防御转攻，用镜像式替换：defend 后追加一次 attack 2）。 |
| 玩家怎么反制 | 节奏稳=可预判：defend 拍攒连携、attack 拍交盾；frail（[index.html:5858]）让它的高 defend 变得可破。 |

### 倒吊的排班表（elite · hp 16-22）

| 项 | 内容 |
|---|---|
| intent_pattern | `[{"type": "attack", "value": 4, "mirror": true}, {"type": "defend", "value": 4}, {"type": "debuff", "status": "gift"}]` |
| 怎么行动 | 一张会自己改写的排班表：mirror 拍复刻玩家上一回合的出牌数（每张 +3 伤）、defend 拍贴条、gift 拍给玩家 1 抽+1 凝视（诱饵）。 |
| 什么情况下变强 | mirror 的伤害与玩家节奏同步：玩家打得越多它打得越疼——它变强的条件就是玩家的勤奋。 |
| 玩家怎么反制 | 反制是「反节奏」：mirror 拍前一手空过或只打 0 费牌；gift 的凝视 +1 要算进长审账（[engine/core.js:849]）。 |

### 结霜的祷文（normal · hp 11-14）

| 项 | 内容 |
|---|---|
| intent_pattern | `[{"type": "buff", "value": 2}, {"type": "attack", "value": 5}]` |
| 怎么行动 | 一页冻在冰里的祷文。buff 拍给自己上攻，attack 拍兑现——两拍蓄力型。 |
| 什么情况下变强 | buff 拍若未被 silence 驳回，连续叠加不设上限（第 N 层 buff 后 attack = 5+2N）——它是 L2 的「限时压力源」。 |
| 玩家怎么反制 | silence 协议/禁声令（D2 设计 13）直接废掉它的全部成长；没有协议时它是第一击杀目标。 |

### 废靴搬运体（normal · hp 13-17）

| 项 | 内容 |
|---|---|
| intent_pattern | `[{"type": "attack", "value": 4}, {"type": "attack", "value": 4}, {"type": "defend", "value": 7}]` |
| 怎么行动 | 拖着一只巨大废靴的搬运残骸，三拍「走、走、歇」。 |
| 什么情况下变强 | 不主动变强；每承受一次 burn 结算，defend 值 +1（烧伤让它学会防御——环境适应型）。 |
| 玩家怎么反制 | burn 打它反而养盾——换 weak（×0.75 对 4 伤的两拍）或直接堆穿透输出；frail 同样被适应机制抵消，纯堆伤害最优。 |

### 半埋的钟摆（elite · hp 20-26）

| 项 | 内容 |
|---|---|
| intent_pattern | `[{"type": "attack", "value": 7, "pierce": false}, {"type": "defend", "value": 5}, {"type": "attack", "value": 7, "pierce": true}]` |
| 怎么行动 | 半埋在碎石里的钟摆残骸，第三拍是 pierce（贯骨振动，无视格挡）。前两拍是给玩家的准备期。 |
| 什么情况下变强 | 血量 ≤50% 后钟摆加速：三拍循环变两拍（pierce 拍紧跟 defend 拍）——准备期消失。 |
| 玩家怎么反制 | pierce 只无视格挡、不无视 thorns/血量——护盾无效但反伤有效；半血前把它的血压进斩杀线是唯一稳法。 |

## L3（本层 4 个新设计）

### 悬浮矿尘核（normal · hp 16-20）

| 项 | 内容 |
|---|---|
| intent_pattern | `[{"type": "attack", "value": 7}, {"type": "buff", "value": 3}, {"type": "defend", "value": 4}]` |
| 怎么行动 | L3 的悬浮体之一：粉尘聚成的核。三拍「打-充-盾」，充的那拍是它悬空的原因（被自己的力场托住）。 |
| 什么情况下变强 | buff 与 defend 同场时交替叠加：核的防御随时间线性变厚——拖得越久越硬。 |
| 玩家怎么反制 | resonance_drain 类卡与它的 buff 拍对冲（它充我抽）；不需要跟它耗——核的血薄，先杀。 |

### 无影攀附者（normal · hp 17-22）

| 项 | 内容 |
|---|---|
| intent_pattern | `[{"type": "attack", "value": 8}, {"type": "debuff", "status": "steal"}, {"type": "attack", "value": 5, "times": 2}]` |
| 怎么行动 | L3 的悬浮无影体：影子投在天花板上，本体贴墙走。偷一张、打两段小伤——「先摸口袋再动手」。 |
| 什么情况下变强 | 偷牌成功后获得该牌的类型加成（偷到攻击牌 → attack +2；偷到技能牌 → defend +3），一次性。 |
| 玩家怎么反制 | 偷牌进弃牌堆可洗回；手里只留低价值牌让它偷=废掉它的加成（机制读懂后的白嫖）。 |

### 泉眼的守灵（elite · hp 24-30）

| 项 | 内容 |
|---|---|
| intent_pattern | `[{"type": "defend", "value": 8}, {"type": "attack", "value": 9}, {"type": "debuff", "status": "burn", "value": 3}, {"type": "attack", "value": 9}]` |
| 怎么行动 | 干裂泉眼旁的四拍守灵体：盾-打-烧-打。四拍循环是 L3 的节奏考试。 |
| 什么情况下变强 | burn 3 若未被玩家清除，第三拍追加一次自愈（burn 未清除 = 它在喝玩家的血）。 |
| 玩家怎么反制 | D2 的清剿令/减压舱在 L3 开始有战略价值；四拍循环在 intent 序列里可预测——第三拍前必清 burn 或必交盾。 |

### 影子掘进机（normal · hp 18-23）

| 项 | 内容 |
|---|---|
| intent_pattern | `[{"type": "attack", "value": 6, "drain_discard": true}, {"type": "attack", "value": 6, "drain_discard": true}]` |
| 怎么行动 | 在天花板影子里掘进的机械残骸：两拍连挖，每拍吃掉玩家弃牌堆一张牌当燃料。 |
| 什么情况下变强 | 弃牌堆越厚它越强（每吃一张，当次 attack +1，结算在吃之后）——它是「惩罚过度弃牌」的敌人。 |
| 玩家怎么反制 | 空过一回合让弃牌堆清零（洗回抽牌堆）= 断它的粮；它的血不厚，两拍循环的间隙够打两轮输出。 |

## L4（本层 4 个新设计）

### 红腔鱼群（normal · hp 20-26）

| 项 | 内容 |
|---|---|
| intent_pattern | `[{"type": "attack", "value": 6}, {"type": "attack", "value": 6}, {"type": "attack", "value": 9}]` |
| 怎么行动 | 三只红腔鱼同场（resolveNode 的多敌抽取）：每条两拍小循环，合起来是「6/6/9 的齐射」。 |
| 什么情况下变强 | 任意一条死后，其余两条的 attack +3（群体悲鸣，一次性）——先杀反而触发总攻。 |
| 玩家怎么反制 | AoE（通·散落的铅字/lead 字类）在鱼群里价值翻倍：均匀压血比逐条点杀少触发一次悲鸣。 |

### 菌幕巡行体（elite · hp 26-33）

| 项 | 内容 |
|---|---|
| intent_pattern | `[{"type": "attack", "value": 8}, {"type": "defend", "value": 8}, {"type": "debuff", "status": "poison", "value": 3}]` |
| 怎么行动 | 沿菌幕横着走的巡行者：打-盾-毒三拍。poison 3 是持续伤害（[engine/core.js:673] 每回合结算）。 |
| 什么情况下变强 | poison 不会被它自己刷新但会一直存在（每回合掉 v 点）——它的威胁是「留下来的东西」，不是本体。 |
| 玩家怎么反制 | T341 的减压舱（u_0017）在此首次成为刚需；无减压舱时用 heal 对冲——但毒不叠加不清除，越早解越好。 |

### 脉动共生对（normal · hp 18-24 ×2）

| 项 | 内容 |
|---|---|
| intent_pattern | `[{"type": "attack", "value": 5}, {"type": "defend", "value": 6}]` |
| 怎么行动 | 两只共生的腔体同场：一只攻击一只防御，交替掩护。R3 同形族（same family 共图）的敌人版。 |
| 什么情况下变强 | 一只死亡时另一只立刻继承死者 buffAtk（共生继承，一次性）——杀顺序有讲究。 |
| 玩家怎么反制 | 先杀持盾那只（继承 attack 无意义），后杀攻击那只（继承盾无意义）——顺序对了继承就白给。 |

### 老浮标（normal · hp 22-28）

| 项 | 内容 |
|---|---|
| intent_pattern | `[{"type": "debuff", "status": "gift"}, {"type": "attack", "value": 10}]` |
| 怎么行动 | 被菌幕缠住的旧浮标还在工作：gift 拍给玩家 1 抽 1 凝视，attack 拍 10 伤重锤。诱饵与惩罚交替。 |
| 什么情况下变强 | gift 每触发一次，attack +1（它给得越多，欠得越多——浮标的账本逻辑）。 |
| 玩家怎么反制 | 长审流玩家会故意吃 gift（凝视是燃料）；背身流玩家在 gift 拍全力输出打断节奏——这张卡是凝视观的照妖镜。 |

## L5（本层 4 个新设计）

### 盐晶共鸣柱（elite · hp 28-35）

| 项 | 内容 |
|---|---|
| intent_pattern | `[{"type": "defend", "value": 10}, {"type": "attack", "value": 8, "times": 2}, {"type": "buff", "value": 3}]` |
| 怎么行动 | 倒挂盐晶的共鸣柱精英：盾-双段打-充。三拍里两次要求玩家换应对方式。 |
| 什么情况下变强 | buff 3 层后柱体共振：每次 attack 额外 +1×当前连携数（它借用玩家的连携规则反打）。 |
| 玩家怎么反制 | 它借用连携 → 玩家连携越高它越疼 → 在它面前**断掉自己的连携**（换脉打）是最优解——T331 通用牌的无脉特性在此反直觉地成为优势。 |

### 热泉啸声体（normal · hp 24-30）

| 项 | 内容 |
|---|---|
| intent_pattern | `[{"type": "attack", "value": 9}, {"type": "debuff", "status": "weak", "value": 2}, {"type": "attack", "value": 9}]` |
| 怎么行动 | 热泉口的啸声体：打-弱-打的循环。weak 拍夹在两个 9 伤之间——中拍的弱化是为下一轮的两拍服务。 |
| 什么情况下变强 | 每次 weak 命中未满回合时（玩家已 weak），本次直接跳过并追加一次 attack 9（不浪费回合）。 |
| 玩家怎么反制 | T332 的 weak 只能 ×0.75 一次——玩家侧防 weak 重复的手段就是尽快清（解 debuff 体系）；无解时扛过中拍。 |

### 静底的回访者（normal · hp 25-31）

| 项 | 内容 |
|---|---|
| intent_pattern | `[{"type": "attack", "value": 7}, {"type": "debuff", "status": "burn", "value": 3}, {"type": "defend", "value": 8}]` |
| 怎么行动 | 静底家族的回访体：打-烧-盾。它带来的 burn 3×3 是全池最大单发烧（并列 trem_0024）。 |
| 什么情况下变强 | burn 每次结算时它回复等量生命（烧谁谁回血——静底的「让伤口自己长好」的敌版）。 |
| 玩家怎么反制 | 立即清 burn（减压舱/点火反制）否则它在白嫖；它 defend 值 8 但打 7——输出窗口在第三拍。 |

### 裂带巡听者（elite · hp 30-38）

| 项 | 内容 |
|---|---|
| intent_pattern | `[{"type": "attack", "value": 10, "times": 2}, {"type": "buff", "value": 4}, {"type": "debuff", "status": "weak", "value": 2}]` |
| 怎么行动 | 裂带精英：双段 10 伤开场、给自己 +4、再弱化玩家——一轮比一轮重的三拍。 |
| 什么情况下变强 | double attack 命中同一目标时，第二段 +3（贯骨余震，无 pierce 但伤害叠加）。 |
| 玩家怎么反制 | 它的三拍全部有解：双段吃满盾、buff 靠 silence、weak 靠清 debuff——这一只就是 L5 的期末考试（T342 里三条弱路的交汇点）。 |

## L6（本层 4 个新设计）

### 辐射灯串（normal · hp 28-34）

| 项 | 内容 |
|---|---|
| intent_pattern | `[{"type": "attack", "value": 8}, {"type": "attack", "value": 8}, {"type": "buff", "value": 5}]` |
| 怎么行动 | 倒挂灯串的一节：两拍 8 伤 + 一拍大 buff。rad_tick 环境已每回合磨玩家 1 血，灯串的职责是放大磨血。 |
| 什么情况下变强 | buff 5 全部转 attack（灯串没有防御概念，攒的全是输出）——从第三轮起 8 伤变 13。 |
| 玩家怎么反制 | 它的 buff 不可驳回（非 silence 可及的自身强化）——只能靠斩杀线压缩它发挥的轮数；L6 是速攻流的主场。 |

### 同位素双生体（elite · hp 30-36 ×2）

| 项 | 内容 |
|---|---|
| intent_pattern | `[{"type": "attack", "value": 7}, {"type": "defend", "value": 7}]` |
| 怎么行动 | 两只完全同构的双生体（R3 极端案例：同族同图同数值）。单只两拍循环。 |
| 什么情况下变强 | 双生同步：任一只受击，另一只立即获得等量格挡（共享防御，引擎外行为→需绑定侧实现）。 |
| 玩家怎么反制 | AoE 对双生是半废（同步加盾把分散伤害补回）——单体爆发连击（在加盾结算前打完）是唯一解；这一只的存在证明「通用 AoE 万能论」是错的。 |

### 矿脉灯剪（normal · hp 29-35）

| 项 | 内容 |
|---|---|
| intent_pattern | `[{"type": "attack", "value": 12}, {"type": "debuff", "status": "burn", "value": 4}]` |
| 怎么行动 | 剪断灯串的机械剪：一拍 12 伤重击 + 一拍 burn 4。两拍都是重拳，没有防御——L6 的玻璃大炮。 |
| 什么情况下变强 | 无成长；它的强是静态的。rad_tick 的 1 伤/回合由环境代打。 |
| 玩家怎么反制 | 无盾=纯输出对轰；玩家 2 费换 12 伤的汇率在 L6 环境伤下要重新算——它逼玩家承认「防御也是资源」。 |

### 错位罗盘（elite · hp 32-40）

| 项 | 内容 |
|---|---|
| intent_pattern | `[{"type": "debuff", "status": "steal"}, {"type": "attack", "value": 8, "pierce": true}, {"type": "defend", "value": 9}, {"type": "attack", "value": 8, "pierce": true}]` |
| 怎么行动 | 方向失效的罗盘精英：偷-贯-盾-贯的四拍。两个 pierce 拍让格挡流失效一半。 |
| 什么情况下变强 | steal 偷到的牌如果是攻击牌，下一拍 pierce +3（它用你的牌打穿你）。 |
| 玩家怎么反制 | L6 的破解不在格挡在血量经济：pierce 段必吃，能把 steal 的牌压到攻击牌以外（手牌管理）就赢一半。 |

## L7（本层 4 个新设计）

### 融态旧光者（elite · hp 36-44）

| 项 | 内容 |
|---|---|
| intent_pattern | `[{"type": "attack", "value": 11}, {"type": "attack", "value": 11, "mirror": true}, {"type": "buff", "value": 5}]` |
| 怎么行动 | 旧光者的融态：自身 11 伤 + mirror 11 伤（复刻玩家节奏）+ 大 buff。三拍全是重拳。 |
| 什么情况下变强 | mirror 拍的加成基数是玩家上回合出牌数×3（[engine/core.js:735]）——玩家 5 张牌回合后它打 11+15=26。 |
| 玩家怎么反制 | mirror 的反制是反节奏（空过/低费回合）；它的 buff 是全池最大单笔 +5——silence 或集火的窗口只有 buff 拍之前。 |

### 手牌焗炉（normal · hp 34-40）

| 项 | 内容 |
|---|---|
| intent_pattern | `[{"type": "attack", "value": 9}, {"type": "debuff", "status": "burn", "value": 5}]` |
| 怎么行动 | L7 环境的具象化：一拍 9 伤 + 一拍 burn 5（环境烧手牌，它烧血量）。 |
| 什么情况下变强 | 玩家的手牌数 ≥8 时它的 attack +3（手越满炉越旺——逼玩家出牌）。 |
| 玩家怎么反制 | 手牌控制在 6 张以下可以拆它的加成；D2 的「空的手」类效果在此从可选变刚需——L7 的教学敌人。 |

### 贴地红流（normal · hp 35-42）

| 项 | 内容 |
|---|---|
| intent_pattern | `[{"type": "attack", "value": 7, "times": 3}, {"type": "defend", "value": 12}]` |
| 怎么行动 | 贴地流动的红的三段体：7×3=21 的三连小段 + 一拍大盾。多段小伤对格挡的消耗方式不同（三段吃三次盾判定）。 |
| 什么情况下变强 | thorns 对三段的反弹也×3（[engine/core.js:766] 每段结算）——它打三段就挨三次刺。 |
| 玩家怎么反制 | thorns 流（T342 弱路之一）在它面前首次成立：三段=三倍反弹；没有 thorns 就用大盾硬吃三段。 |

### 熔心残响（elite · hp 40-48）

| 项 | 内容 |
|---|---|
| intent_pattern | `[{"type": "attack", "value": 13, "pierce": true}, {"type": "buff", "value": 6}, {"type": "attack", "value": 13, "pierce": true}]` |
| 怎么行动 | L7 精英：双 pierce 13 伤夹一个大 buff。三拍里两拍无视格挡——格挡流在这里被摊开检验。 |
| 什么情况下变强 | 两段 pierce 之间若玩家格挡 >15，第二段 pierce 追加 +6（「你盾越厚我越疼」的读盾机制）。 |
| 玩家怎么反制 | 读盾机制的反制是「格挡正好」：把盾控在 15 以下、用血量吸收差值——这是全游戏第一次要求玩家「少挡一点」。 |

## L8（本层 5 个新设计）

### 无面的记录员（normal · hp 42-50）

| 项 | 内容 |
|---|---|
| intent_pattern | `[{"type": "attack", "value": 12}, {"type": "debuff", "status": "steal"}, {"type": "attack", "value": 12, "mirror": true}]` |
| 怎么行动 | L8 的普通体：记录玩家的一切然后原样奉还。偷-打-复刻的三拍。 |
| 什么情况下变强 | 它偷过的每张牌都被「记录」：第三次循环时 mirror 的基数 +1/每张已记录牌——越拖越不可打。 |
| 玩家怎么反制 | 速战是唯一解；它的 hp 是 L8 normal 最低档（42-50）——设计意图就是「这一只不配拖」。 |

### 塌落的钟乳阵（normal · hp 45-52）

| 项 | 内容 |
|---|---|
| intent_pattern | `[{"type": "attack", "value": 10, "times": 2}, {"type": "attack", "value": 10, "times": 2}]` |
| 怎么行动 | void 层掉下来的钟乳石阵：四段 10 伤，没有防御——纯输出型的最后形态。 |
| 什么情况下变强 | 无成长。它代表 L8 的基本盘：四段 40 总伤，你有一回合准备。 |
| 玩家怎么反制 | thorns 3 即可反弹 30（四次×thorns）；没有 thorns 的构筑在这里要用全部格挡预算——最后的教学：资源分配无标准答案。 |

### 静默的见证者（elite · hp 50-58）

| 项 | 内容 |
|---|---|
| intent_pattern | `[{"type": "debuff", "status": "gift"}, {"type": "attack", "value": 14, "pierce": true}, {"type": "defend", "value": 14}]` |
| 怎么行动 | L8 精英：gift 给玩家 1 抽 1 凝视（最后的诱饵）、pierce 14、大盾。三拍是全游戏所有机制的縮影。 |
| 什么情况下变强 | gift 触发时它自己 +2 攻（凝视对它也是燃料——双方共用同一个资源池的敌人版）。 |
| 玩家怎么反制 | 吃 gift 的凝视同时喂它和自己——长审流在它面前会 explicitly 打平；背身流玩家对 gift 拍全力输出即可。 |

### 墟蛹的守宫（elite · hp 52-60）

| 项 | 内容 |
|---|---|
| intent_pattern | `[{"type": "defend", "value": 16}, {"type": "attack", "value": 13, "times": 2}, {"type": "buff", "value": 6}, {"type": "attack", "value": 13}]` |
| 怎么行动 | 墟蛹（enemy_d8_01）的守宫精英：盾-双段-充-段的四拍，每拍都在考一种应对。 |
| 什么情况下变强 | 四拍循环第二轮起，defend 值 +4（16→20）——它记得你上一轮怎么打。 |
| 玩家怎么反制 | 循环记忆 = 每轮用不同的解（盾拍换伤害、伤害拍换盾）——「换着打」是 L8 精英的通用答案。 |

### 渊底的回签人（boss 配角 · hp 55-65）

| 项 | 内容 |
|---|---|
| intent_pattern | `[{"type": "attack", "value": 15, "mirror": true}, {"type": "debuff", "status": "burn", "value": 6}, {"type": "debuff", "status": "steal"}, {"type": "attack", "value": 15}]` |
| 怎么行动 | 墟蛹前的最后守门：mirror 15、burn 6、steal、plain 15——四拍把 L2-L7 的全部机制各还一遍。 |
| 什么情况下变强 | 四拍各记一分「应对正确度」：mirror 拍玩家低费、burn 拍玩家清除、steal 拍玩家护牌、plain 拍玩家硬吃——全对则第四拍 attack -5（它承认你毕业了）。 |
| 玩家怎么反制 | 它不是考倒玩家的敌人，是「给毕业证的敌人」——设计意图是让玩家在最终 boss 前确认自己学会了整个游戏。 |

### 渊底的回签人·另一半（boss 配角 · hp 55-65）

| 项 | 内容 |
|---|---|
| intent_pattern | `[{"type": "defend", "value": 18}, {"type": "attack", "value": 15, "mirror": true}, {"type": "debuff", "status": "burn", "value": 6}, {"type": "attack", "value": 15, "times": 2}]` |
| 怎么行动 | 与「渊底的回签人」成对出场（同 hp 池拆成两个半体）：本半体是防御+镜像侧。两半的 intent 循环互补，合起来才是完整考卷 |
| 什么情况下变强 | 另一半死亡时，本半体继承其全部未结算 burn 与 steal 记录（孤半之怒，一次性继承） |
| 玩家怎么反制 | 两半的血池独立但考卷互补——先杀防御侧会让攻击侧的镜像无处反弹，先杀攻击侧会让防御侧孤守；对称杀是正解，也是「毕业证」的最后一题 |


## 校验

| 项 | 结果 |
|---|---|
| 数量 | 36（L1×5 / L2×5 / L3×4 / L4×4 / L5×4 / L6×4 / L7×4 / L8×6，其中 L8 含成对 boss 配角 2） |
| 重名 | 0（对 enemies/all.json 113 个名字全量比对） |
| 引擎类型 | 全部落在 enemyAct 已实现集合（[engine/core.js:728]） |
| 分布 | 5+5+4+4+4+4+4+6=36，L8 的 6 个里含成对 boss 配角（同考卷拆两半） |

## 决定记录

- 「36 个」按队列字面取；分布不均是因为 L8 的叙事密度高（5 个含 boss 配角）而 L3/L4 各 4 个——层叙事优先于机械均分。
- 「变强条件」里 4 个需绑定侧替换 intent_pattern（成对加成/镜像加速/吸收成长/循环记忆）——实现走 T58 绑定表的替换机制，不碰引擎。
- 贴地红流（L7）与脉动共生对（L4）是给 T342 弱路的正面反馈设计（thorns 流、AoE 例外论）——敌人也是弱路的教具。
