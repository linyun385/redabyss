# U09 · 倒转圣痕（u_0009）设计书

> T331 通用牌 u_0009 的逐张设计书。四段：名字来由 / 费用依据 / 效果与引擎落点 / 补哪条弱路与不该被选的条件。数值以 T341 草案为准。

## 一、名字来由

圣痕是「被红光选中」的印记（敌人 gift 意图给凝视的叙事对应物）；倒转是玩家第一次主动把印记翻面——从「被看」转成「听见」。凝视减 2 加共振 3，是全池第一张资源转换卡。

## 二、费用依据

1 费。依据：gaze_reduce 2 + resonance_gain 3。定价锚：凝视的市场价在 mark 代价（每张卡凝视+1）与 gazeMul（每 10 点敌人 +10% 伤害）之间；减 2 的防御价值 + 共振 3 的进攻价值合成 1 费是「双小效应合一费」的常规打包价。共振 3 是上限（T331 纪律：通用牌 resonance_gain ≤3）。

## 三、效果与引擎落点

effect: {"target": "self", "special": [{"code": "gaze_reduce", "value": 2}, {"code": "resonance_gain", "value": 3}]}，veins: ["light"]。引擎落点：零改动——gaze_reduce [index.html:5063] 附近与 resonance_gain [index.html:5840] 都已实现。

## 四、它补哪条弱路

疯先知×凝视（唯一的凝视减法入口）；凝视冲「长审」结局路上的刹车片；共振积累的补燃料位。

## 五、什么情况下它不该被选

不该被选：① 凝视 ≤2 时（gaze_reduce 打空气，只剩共振 3——那不如拿 dive_0025）；② 共振已过 20 且本层 mode 是 overload 的过载层（+3 是给敌人喂燃料）；③ 高凝视流派成型后（凝视是你的资产，减它等于拆自己的 engine）。

## 六、效果字段速览（T341 草案原样）

```json
{
 "id": "u_0009",
 "name": "倒转圣痕",
 "class": "shared",
 "type": "skill",
 "rarity": "uncommon",
 "veins": [
  "light"
 ],
 "energy": 1,
 "effect": {
  "target": "self",
  "special": [
   {
    "code": "gaze_reduce",
    "value": 2
   },
   {
    "code": "resonance_gain",
    "value": 3
   }
  ]
 },
 "cost_type": "none",
 "cost_text": "",
 "flavor": "正面的字是警告，背面的是邀请。你看的是哪一面？",
 "upgrade": {
  "name_suffix": "·深",
  "effect": {
   "special": [
    {
     "code": "gaze_reduce",
     "value": 2
    },
    {
     "code": "resonance_gain",
     "value": 4
    }
   ]
  },
  "flavor_add": "背面比正面更像正面。"
 }
}
```

## 七、池内对照（共享机制键的现存卡，按重合度取前 6）

| 卡 | 名称 | 费 | 稀有度 | 共享机制 |
|---|---|---|---|---|
| trem_0027 | 震语：明目 | 1 | uncommon | special,special:gaze_reduce |
| trem_0029 | 观红（深相） | 2 | rare | special,special:gaze_reduce |
| anm_0027 | 协议：静默段·延长 | 0 | rare | special |
| dive_0056 | 死亡合同（增补条款） | 0 | uncommon | special |
| dive_0081 | 气闸的规程 | 0 | common | special |
| trem_0015 | 触温 | 0 | common | special |

对照读法：上表是这张通用牌要「插队」的现有卡——它的定价（§二）是否成立，取决于它在这些邻居之间是否有独立生态位（§五 的不该被选条件就是生态位边界）。

## 八、获取途径与稀有度

| 途径 | 说明 |
|---|---|
| 商店 | 商店主渠道（普通 40-60 / 罕见 75-110 / 稀有 150-200 金，[index.html:6807]） |
| 事件奖励 | card_reward=universal 档候选（[index.html:7430] 的分支需 T333 改法一落地） |
| 战斗奖励 | weightedCards 混入通用池后按稀有度权重出现（普通 6/罕见 3/稀有 1，[index.html:7174]） |
| 稀有度 | uncommon |
| 开局 | 不进 STARTER_EXTRA——开局补位是职业牌专属位（[index.html:6465]），通用牌刻意不占 |

## 九、脉与层规则

light（层规则交互：光脉受 no_light 拦截 [index.html:5813] 与 bright 加成 [index.html:5820]；水脉受 dry 加价 [index.html:5768]；连携按首脉 light 计 [index.html:5789]）

## 十、同费用带对照（全池 1 费卡 158 张，抽 6 张）

| 卡 | 名称 | 类型 | 稀有度 | 机制 |
|---|---|---|---|---|
| anm_0001 | 现场回收 | skill | common | block |
| anm_0033 | 血统册摘录 | skill | common | draw |
| cng_0017 | 地下学院讲义 | skill | special | draw |
| dive_0014 | 震髓探测器 | skill | common | draw+resonance_gain |
| dive_0066 | 曜元（高浓） | skill | common | heal |
| trem_0027 | 震语：明目 | skill | uncommon | draw+special+special:gaze_reduce |

对照读法：这张通用牌在 1 费位要与上述卡竞争同一个能量预算——§五 的不该被选条件就是它在这个价格带里的存活边界。

## 十一、T331 三纪律核对

| 纪律 | 核对 |
|---|---|
| 做别的卡做不到的事 | 是——机制键组合在全池无第二张（§七 对照表的重合度可证）。 |
| 不碰资源量级 | resonance_gain 3 = 纪律上限，未越界。 |
| 稀有度贴合获取 | uncommon（桥梁层，商店主渠道（普通 40-60 / 罕见 75-110 / 稀有 150-200 金，[index.html:6807]）） |

## 十二、执行链路（从本篇到进游戏）

| 步 | 动作 | 依据 |
|---|---|---|
| 1 | 确认引擎前提：零引擎改动，可直接贴 cards/shared.json。 | 本篇 §三；T341 §三汇总 |
| 2 | 贴入 cards/shared.json（class=shared，四职业自动可用） | [index.html:6419] 的 CLASS_POOL concat RAW.shared |
| 3 | 重建内联数据 | node tools/_t46_wire.js |
| 4 | 平衡验证 | 模拟器（需先修 docs/BALANCE_T29.md §六 的三建模缺口）+ 玩感记录到 T342 对应格 |

## 十三、名义对照（世界观锚点回查）

| 锚 | 出处 |
|---|---|
| 圣痕 | 敌人 gift 意图 [engine/core.js:788] |
## 十四、协同搭档（同回合/相邻回合组合，机械推导）

| 搭档 | 机制依据 |
|---|---|
| u_0012 双芯灯管 | 同脉 light——连携链相邻位（[engine/core.js:429] 首脉口径） |
| u_0007 传声钢缆 | 同脉 light——连携链相邻位（[engine/core.js:429] 首脉口径） |

搭档不是「必拿」——组合强度要等模拟器修好（docs/BALANCE_T29.md §六）；本表只证明协同的机制通路存在，不证明数值成立。


## 十五、系统接口（本卡每个机制键的引擎落点）

| 机制键 | 行为 | 引擎位置 |
|---|---|---|

## 十六、机制键稀缺度（全池 267 张里有多少张带同一个键）

| 机制键 | 全池卡数 | 本卡的选择价值 |
|---|---|---|
| special | 76 | 常见（>30）——它的价值在结构不在稀缺 |
| special:gaze_reduce | 2 | 稀缺（<10 张）——构筑独特性高 |
| special:resonance_gain | 0 | 稀缺（<10 张）——构筑独特性高 |

## 十七、八层对话（层规则 × 本卡）

| 层 | 规则 | 与本卡的关系 |
|---|---|---|
| L1 地表死寂区 | no_light：光脉牌整卡失效（[index.html:5813]） | 有交互 |
| L2 外层冷洞 | cold：每回合首张 +1 费（[index.html:5772] 附近） | 有交互 |
| L3 干旱空洞区 | dry：水脉牌 +1 费（[index.html:5768]） | 无特殊交互 |
| L4 稳定空洞海 | bright：光脉效果 +2（[index.html:5820]） | 有交互 |
| L5 热泉裂带 | heat_tick：每 3 回合灼 2（[engine/core.js:274]） | 无特殊交互 |
| L6 辐射矿石区 | rad_tick：每回合 1 伤换 1 抽（[engine/core.js:279]） | 有交互 |
| L7 核心高热区 | burn_hand：每回合烧一张手牌（[engine/core.js:284]） | 无特殊交互 |
| L8 红渊核心 | void：脉锁死，连携恒 0（[engine/core.js:36]） | 有交互 |

读法：「有交互」的层是这张卡价值波动的位置——组牌时把它当成随层浮动的资产，而不是恒定强度。三张无脉过渡卡在全部 8 层等强，这正是 T331 把它们定成过渡层的依据。

## 决定记录

- 引擎注记：见 T341 §三。
- 定价来源：cards/*.json 全池数值（2026-11-04 实测）与 T331/T332/T341 交叉引用；模拟器建模缺口未修（docs/BALANCE_T29.md §六），定价为静态推断非模拟验证。
