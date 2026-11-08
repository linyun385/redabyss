# 遗物池扩充 · 24 个新遗物

> 2026-11-06 夜班 · 方向池 4。派单：`tasks/INBOX/08_overnight_1106.md` 方向 4。
> 数据来源：`RAW.relics` 现有 77 个（relic_01–77，只读核对）。id 顺延 **relic_78–relic_101**。
> **effect_code 白名单（全部经引擎实现点核实，不是照抄数据）**：
>
> | trigger | action | 引擎实现点 |
> |---|---|---|
> | `combat_start` | `draw` / `gaze` / `block` | startCombat 内，5588–5594 行 |
> | `turn_start` | `heal` / `resonance` / `draw` | `applyRelicTurnStart()`，7137 行起 |
> | `on_kill` | `heal` | 7341 行（on_kill 只实现了 heal，**没有 block/draw**） |
> | `run_start` | `maxhp` | 7450 行 |
> | （mod） | `cost_redirect: true` / `keep_block: true` / `vein_cost`+`vein_cost_delta` / `chain_bonus`(+`chain_vein`) | 6076 / 6240 / 5881 / 5901 行 |
>
> ⚠️ 数据里有 1 个 `turn_start + gaze`（77 个里仅此一处），引擎的 turn_start handler **不认 gaze**——静默不生效。本批不使用该组合，也不模仿。
> `keep_block` 的真实语义是**回合结束格挡减半保留**（6242 行 `Math.floor(C.block/2)`），不是不清零——effect_text 按真实语义写。

---

## 一、数值类（6 个）

### relic_78 · 顶板螺栓
- rarity: common ｜ veins: [mineral]
- effect_text: 每场战斗开始时，获得 4 点格挡。
- effect_code: `[{"trigger":"combat_start","action":"block","value":4}]`
- flavor: 拧在顶上的螺栓，比拧在墙上的多扛一半。掉下来的时候你最好不在正下方。

### relic_79 · 叠层镜片
- rarity: rare ｜ veins: [light]
- effect_text: 每回合开始时，抽 1 张牌。
- effect_code: `[{"trigger":"turn_start","action":"draw","value":1}]`
- flavor: 五层镜片叠出一种没有名字的颜色。看久了，你只看得见那种颜色。
- 注：现有池已有 2 个同 trigger/action 遗物（turn_start/draw），三张同放后每回合 +3 抽，强度需实测观测。

### relic_80 · 工装内衬
- rarity: common ｜ veins: [mineral]
- effect_text: 一局开始时，最大生命 +4。
- effect_code: `[{"trigger":"run_start","action":"maxhp","value":4}]`
- flavor: 内衬缝了四层。缝的人说这叫余量，不叫怕死。

### relic_81 · 备用电池组
- rarity: uncommon ｜ veins: [water]
- effect_text: 每场战斗开始时，抽 2 张牌。
- effect_code: `[{"trigger":"combat_start","action":"draw","value":2}]`
- flavor: 三节电池用胶布缠着。胶布是新的，电池不是。

### relic_82 · 静脉桥
- rarity: uncommon ｜ veins: [water]
- effect_text: 每回合开始时，回复 2 点生命。
- effect_code: `[{"trigger":"turn_start","action":"heal","value":2}]`
- flavor: 管子一头接在循环液上，另一头接在你身上。接口处没有麻醉。

### relic_83 · 共振增音壳
- rarity: rare ｜ veins: [tremor]
- effect_text: 每回合开始时，共振 +2。
- effect_code: `[{"trigger":"turn_start","action":"resonance","value":2}]`
- flavor: 壳内衬着骨粉。共振到 30 之后会发生什么，壳比你先知道。

## 二、代价类（6 个）——力量都标着价，价写在另一行 effect_code 里

### relic_84 · 相石的另一半
- rarity: uncommon ｜ veins: [light]
- effect_text: 每场战斗开始时，获得 8 点格挡；凝视 +2。
- effect_code: `[{"trigger":"combat_start","action":"block","value":8},{"trigger":"combat_start","action":"gaze","value":2}]`
- flavor: 另一半在更深的地方，也被谁攥着。两边隔着一层岩层互相看。

### relic_85 · 呼吸阀
- rarity: uncommon ｜ veins: [heat]
- effect_text: 每回合开始时，回复 2 点生命；每场战斗开始时，凝视 +1。
- effect_code: `[{"trigger":"turn_start","action":"heal","value":2},{"trigger":"combat_start","action":"gaze","value":1}]`
- flavor: 阀门每开一次，红光就顺着管子看你一眼。看得多了，它会记住你。

### relic_86 · 深潜配重
- rarity: rare ｜ veins: [mineral]
- effect_text: 一局开始时，最大生命 +12；每场战斗开始时，凝视 +1。
- effect_code: `[{"trigger":"run_start","action":"maxhp","value":12},{"trigger":"combat_start","action":"gaze","value":1}]`
- flavor: 配重挂在你的骨头上。沉，但沉得踏实。下面的东西喜欢有分量的。

### relic_87 · 抽采泵
- rarity: rare ｜ veins: [water]
- effect_text: 每场战斗开始时，抽 2 张牌；凝视 +2。
- effect_code: `[{"trigger":"combat_start","action":"draw","value":2},{"trigger":"combat_start","action":"gaze","value":2}]`
- flavor: 泵抽的不是水。你每多看一张牌，泵就把你的位置多上报一次。

### relic_88 · 旧契约的复本
- rarity: common ｜ veins: [light]
- effect_text: 一局开始时，最大生命 +6；每场战斗开始时，抽 1 张牌。
- effect_code: `[{"trigger":"run_start","action":"maxhp","value":6},{"trigger":"combat_start","action":"draw","value":1}]`
- flavor: 复本没有效力。但正本上写的东西，复本也都要兑现。

### relic_89 · 超标徽章
- rarity: uncommon ｜ veins: [heat]
- effect_text: 每场战斗开始时，获得 6 点格挡；一局开始时，最大生命 -4。
- effect_code: `[{"trigger":"combat_start","action":"block","value":6},{"trigger":"run_start","action":"maxhp","value":-4}]`
- flavor: 徽章的剂量读数是刻上去的，不是测出来的。挂上它的人通常走得深。

## 三、条件类（6 个）——条件写在触发器里，引擎没有「若…则…」

### relic_90 · 拆解工的指虎
- rarity: common ｜ veins: [mineral]
- effect_text: 每次击杀敌人后，回复 2 点生命。
- effect_code: `[{"trigger":"on_kill","action":"heal","value":2}]`
- flavor: 指虎上有个凹槽，专门用来刮。刮下来的东西去哪了，没人问。

### relic_91 · 战地清创包
- rarity: uncommon ｜ veins: [water]
- effect_text: 每次击杀敌人后，回复 3 点生命。
- effect_code: `[{"trigger":"on_kill","action":"heal","value":3}]`
- flavor: 包是配给三线以下人员的。三线的意思是：离出口三条层。
- 注：与 relic_90 同 trigger/action，数值 2→3 构成同位两档（现有池 on_kill/heal 已有 5 个，数值带 1–3，本批贴上限）。

### relic_92 · 冷洞通行证
- rarity: uncommon ｜ veins: [water]
- effect_text: 水脉牌的费用 -1。
- effect_code: 无（mod 写法）：`"mod": {"vein_cost":"water","vein_cost_delta":-1}`
- flavor: 盖章的地方是空的。章在盖章的人手里，人不在了。

### relic_93 · 矿脉偏好
- rarity: uncommon ｜ veins: [mineral]
- effect_text: 矿脉连携的加成 +1。
- effect_code: 无（mod 写法）：`"mod": {"chain_bonus":1,"chain_vein":"mineral"}`
- flavor: 矿脉认熟脸。你用矿脉牌连得越多，它给你的越多。这是偏心，不是公平。

### relic_94 · 重链钩
- rarity: rare ｜ veins: [tremor]
- effect_text: 所有脉的连携加成 +2。
- effect_code: 无（mod 写法）：`"mod": {"chain_bonus":2}`
- flavor: 钩子不挑链子。链子挑钩子的时候，通常已经晚了。

### relic_95 · 卸力锚座
- rarity: rare ｜ veins: [mineral]
- effect_text: 回合结束时，保留一半格挡。
- effect_code: 无（mod 写法）：`"mod": {"keep_block":true}`
- flavor: 力从上面来，锚座把一半卸进岩层。剩下一半你自己消化。

## 四、剧情类（6 个）——机制简单，账都记在世界观上

### relic_96 · 半张合影
- rarity: common ｜ veins: [light]
- effect_text: 每回合开始时，回复 1 点生命。
- effect_code: `[{"trigger":"turn_start","action":"heal","value":1}]`
- flavor: 照片上的人都在笑。没有人看着镜头。撕掉的另一半上是拍照片的人。

### relic_97 · 停摆的怀表
- rarity: uncommon ｜ veins: [tremor]
- effect_text: 每回合开始时，共振 +1。
- effect_code: `[{"trigger":"turn_start","action":"resonance","value":1}]`
- flavor: 表针停在两秒之间。这里的时间对它没有意义，对你的牙齿开始有了。

### relic_98 · 最后一份工资条
- rarity: common ｜ veins: [mineral]
- effect_text: 一局开始时，最大生命 +3。
- effect_code: `[{"trigger":"run_start","action":"maxhp","value":3}]`
- flavor: 金额栏是空的。签字栏签了两遍，第二遍是别人的笔迹。

### relic_99 · 地图册的残页
- rarity: uncommon ｜ veins: [light]
- effect_text: 每场战斗开始时，抽 1 张牌。
- effect_code: `[{"trigger":"combat_start","action":"draw","value":1}]`
- flavor: 残页只画到第三层。往下的部分是手补的，笔迹越来越乱，最后一层是一团黑。

### relic_100 · 借据
- rarity: rare ｜ veins: [water]
- effect_text: 每场战斗开始时，凝视 -2。
- effect_code: `[{"trigger":"combat_start","action":"gaze","value":-2}]`
- flavor: 上面写着「欠红渊一次」。落款是空的，字不是空的。

### relic_101 · 婴儿鞋
- rarity: uncommon ｜ veins: [water]
- effect_text: 每回合开始时，回复 1 点生命。
- effect_code: `[{"trigger":"turn_start","action":"heal","value":1}]`
- flavor: 一双，很小，鞋底磨穿了。这个深度不该有这个尺寸。鞋里塞着一张字条，字条是干的。

---

## 自查

| 项 | 结果 |
|---|---|
| 数量与分组 | 24 = 数值 6 + 代价 6 + 条件 6 + 剧情 6 |
| id | relic_78–101，与现有 77 个零撞车 |
| effect_code 词表 | 只用引擎核实过的组合（见文首白名单表）；**未用** turn_start+gaze（存量数据里有一处，但引擎不认）；**未用** on_kill+非 heal（引擎只实现 heal） |
| 数值带 | block 4–8（现有 1–10）、heal 1–3（现有 1–3）、draw 1–2（现有 1–2）、resonance 1–2（现有同款）、maxhp -4～+12（现有 -10～+20）、gaze -2～+2（现有 -4～+3）——全部在现有带内 |
| rarity 分布 | common 6 / uncommon 11 / rare 7（现有池 27/27/20/3boss，本批不设 boss） |
| flavor | 全部冷短工业风，无感叹号，无第二人称安慰 |

## 未验证

- **未验证**：一个 relic 挂多条 effect_code 的叠加行为——引擎对每条独立 forEach（5588/7137/7340/7449 处均为列表遍历），机制上成立；但「同 relic 双条目」在现有 77 个里是否存在未逐个核对，若存在样式冲突由维护者定夺。
- **未验证**：`chain_bonus`/`vein_cost` 两个 mod 的实际数值手感（读取点已核，收益大小未模拟）。
- **未验证**：relic_79（turn_start 抽 1）与现有 2 个同类叠放后的抽牌压力（relic_87 已改为 combat_start 抽 2，避免本批内部再叠一份）。
- **存疑**：relic_89 用了负 maxhp 作为代价——现有池 maxhp 负值全部是「事件/代价」语境（-4～-10），本批照用；若维护者认为遗物不应带负开局，把它改成 combat_start gaze 2 即可。
