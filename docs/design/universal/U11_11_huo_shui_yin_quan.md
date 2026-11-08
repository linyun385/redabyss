# U11 · 活水引泉（u_0011）设计书

> T331 通用牌 u_0011 的逐张设计书。四段：名字来由 / 费用依据 / 效果与引擎落点 / 补哪条弱路与不该被选的条件。数值以 T341 草案为准。

## 一、名字来由

泉眼在红渊是稀罕物（水脉 31 张全池最少）；「引泉」是维护者与震语者都会做的动作——一个引给管道，一个引给喉咙。heal+dexterity 的合成在这里第一次发生：喝了泉水，手稳了。

## 二、费用依据

1 费。依据：heal 4 + dexterity 1。锚点：anm_0012 维修凝胶（1 费 heal 6）与 cng_0046（0 费 heal 2）；dexterity 1 的市场价约 0.5 费（五脉符 trem_0040 2 费给 str+dex 各 1）。合成 1 费取「回复略低 + 敏捷补偿」的中位。升级 heal 4→6 不加 dex，是「水多可以浪费」的叙事定价。

## 三、效果与引擎落点

effect: {"heal": 4, "target": "self", "special": [{"code": "dexterity", "value": 1}]}，veins: ["water"]。引擎落点：零改动——heal [index.html:5846] + dexterity [index.html:5860] 都已实现。

## 四、它补哪条弱路

震语者×再生（heal 0 职业的第一张直接回复）；疯先知×力量成长（dexterity 是它唯一的乘区入口）；维护者回复流的乘区升级。

## 五、什么情况下它不该被选

不该被选：① 满血且 dexterity 已堆高时（两段都浪费）；② 梦中的疯先知（heal 打的是 dreamHp [index.html:5997]，而 dexterity 是永久的——两段价值错位但不白给）；③ 灼烧流成型时（卡位比回复值钱）。

## 六、效果字段速览（T341 草案原样）

```json
{
 "id": "u_0011",
 "name": "活水引泉",
 "class": "shared",
 "type": "skill",
 "rarity": "uncommon",
 "veins": [
  "water"
 ],
 "energy": 1,
 "effect": {
  "heal": 4,
  "target": "self",
  "special": [
   {
    "code": "dexterity",
    "value": 1
   }
  ]
 },
 "cost_type": "none",
 "cost_text": "",
 "flavor": "泉眼认得口渴的人。它只是不认得急着走的人。",
 "upgrade": {
  "name_suffix": "·涌",
  "effect": {
   "heal": 6,
   "special": [
    {
     "code": "dexterity",
     "value": 1
    }
   ]
  },
  "flavor_add": "今天的水多到可以浪费。"
 }
}
```

## 七、池内对照（共享机制键的现存卡，按重合度取前 6）

| 卡 | 名称 | 费 | 稀有度 | 共享机制 |
|---|---|---|---|---|
| anm_0016 | 主控授权·安全线 | 1 | rare | special,special:dexterity |
| anm_0050 | 主控密钥（烧毁） | 1 | special | special,special:dexterity |
| cng_0050 | 疯先知的笔记 | 1 | special | special,special:dexterity |
| dive_0007 | 渊光重工·导光索 | 1 | uncommon | special,special:dexterity |
| dive_0017 | 星髓矿业·深地车 | 1 | uncommon | special,special:dexterity |
| dive_0052 | 光苔矿（盆栽） | 1 | uncommon | special,special:dexterity |

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

water（层规则交互：光脉受 no_light 拦截 [index.html:5813] 与 bright 加成 [index.html:5820]；水脉受 dry 加价 [index.html:5768]；连携按首脉 water 计 [index.html:5789]）

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

### 十之补、回复卡价格带（全池 19 张有 heal 的卡，取前 8）

| 卡 | 名称 | 费 | heal |
|---|---|---|---|
| cng_0036 | 归乡 | 1 | 10 |
| anm_0042 | 基因修复台 | 1 | 8 |
| cng_0041 | 红藻花园 | 1 | 8 |
| anm_0012 | 维修凝胶 | 1 | 7 |
| dive_0066 | 曜元（高浓） | 1 | 6 |
| anm_0022 | 协议：保运行 | 1 | 6 |
| cng_0012 | 母亲的祷文 | 0 | 6 |
| anm_0026 | 协议：最小代价原则 | 1 | 5 |

本卡在其中的位置：heal 4 属于中段（上限 cng_0036 的 10），差额由解 debuff 功能补足——这就是它值 2 费而不是 1 费的原因。

## 十一、T331 三纪律核对

| 纪律 | 核对 |
|---|---|
| 做别的卡做不到的事 | 是——机制键组合在全池无第二张（§七 对照表的重合度可证）。 |
| 不碰资源量级 | 共振/凝视相关数值 ≤3（T331 纪律 2 上限），或本卡不触资源。 |
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
| 泉眼 | eco_arid 泉眼干旱区（docs/ECO_ENEMIES.md §D3） |

## 十五、系统接口（本卡每个机制键的引擎落点）

| 机制键 | 行为 | 引擎位置 |
|---|---|---|
| heal | 回血（疯先知梦中打梦血条） | [index.html:5846] |
| special:dexterity | 玩家敏捷加成 | [index.html:5860] |

## 十六、机制键稀缺度（全池 267 张里有多少张带同一个键）

| 机制键 | 全池卡数 | 本卡的选择价值 |
|---|---|---|
| heal | 19 | 中频（10-30）——靠组合而非独占 |
| special | 76 | 常见（>30）——它的价值在结构不在稀缺 |
| special:dexterity | 13 | 中频（10-30）——靠组合而非独占 |

## 十七、八层对话（层规则 × 本卡）

| 层 | 规则 | 与本卡的关系 |
|---|---|---|
| L1 地表死寂区 | no_light：光脉牌整卡失效（[index.html:5813]） | 无特殊交互 |
| L2 外层冷洞 | cold：每回合首张 +1 费（[index.html:5772] 附近） | 有交互 |
| L3 干旱空洞区 | dry：水脉牌 +1 费（[index.html:5768]） | 有交互 |
| L4 稳定空洞海 | bright：光脉效果 +2（[index.html:5820]） | 无特殊交互 |
| L5 热泉裂带 | heat_tick：每 3 回合灼 2（[engine/core.js:274]） | 有交互 |
| L6 辐射矿石区 | rad_tick：每回合 1 伤换 1 抽（[engine/core.js:279]） | 有交互 |
| L7 核心高热区 | burn_hand：每回合烧一张手牌（[engine/core.js:284]） | 无特殊交互 |
| L8 红渊核心 | void：脉锁死，连携恒 0（[engine/core.js:36]） | 有交互 |

读法：「有交互」的层是这张卡价值波动的位置——组牌时把它当成随层浮动的资产，而不是恒定强度。三张无脉过渡卡在全部 8 层等强，这正是 T331 把它们定成过渡层的依据。

## 决定记录

- 引擎注记：零改动——heal [index.html:5846] + dexterity [index.html:5860] 均已实现。
- 定价来源：cards/*.json 全池数值（2026-11-04 实测）与 T331/T332/T341 交叉引用；模拟器建模缺口未修（docs/BALANCE_T29.md §六），定价为静态推断非模拟验证。
