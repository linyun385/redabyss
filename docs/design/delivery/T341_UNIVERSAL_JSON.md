# T341 · 通用牌数据草案（可直接贴进 cards/shared.json）

> 字段结构照抄 cards/*.json 真实卡（267 张字段普查见 §一）；id 用 u_0001–u_0017，与现有 539 个 id（cards 267 + enemies 113 + events 82 + relics 77）零撞车（脚本核对）。
> 引擎判定先说结论：**17 张里 10 张零引擎改动**（只用 applyCardEffect/applySpecial 已实现字段；越权的批文走 anmin_mark 既有读点 [index.html:5726]/[engine/core.js:364]）；**7 张需要改引擎**（§三，只列不实现）。

## 一、真实字段结构与职业间差异

全池 267 张字段普查：id/name/class/type/rarity/veins/energy/effect/cost_type/cost_text/flavor 各 267；upgrade 261（dive_0081-0083、trem_0081-0083 六张没有）；dream 50（全部 cangmin）。通用牌按「全字段照抄 + class=shared」构造——class=shared 是引擎现成路径：CLASS_POOL 把 RAW.shared concat 进四职业（[index.html:6419]-[index.html:6424]），放 cards/shared.json 即四职业通用，无需新键。

三处注意：① 费用字段名是 `energy` 不是 `cost`（任务书示例的 cost 在真实卡里不存在）；② cost_type 写 "none"，非 none 四种（memory/vitality/mark/lock）引擎全支持（[engine/core.js:520] 的 applyCardCost 四分支）；③ upgrade 数值是**最终值**、special 是**追加**（[engine/core.js:980]），升级草案按此语义写。

## 二、十张零引擎改动的草案

### u_0003 虹吸管
```json
{
 "id": "u_0003",
 "name": "虹吸管",
 "class": "shared",
 "type": "attack",
 "rarity": "common",
 "veins": [],
 "energy": 1,
 "effect": {
  "damage": 5,
  "hits": 1,
  "target": "single",
  "heal": 2
 },
 "cost_type": "none",
 "cost_text": "",
 "flavor": "管子一头插在伤口里，另一头插在你嘴里。",
 "upgrade": {
  "name_suffix": "·顺",
  "effect": {
   "damage": 7,
   "heal": 3
  },
  "flavor_add": "抽出来的东西比上一次干净。"
 }
}
```
补弱路：T332「疯先知×再生续航」中格与爆发流杂兵回复位（attack+heal 同卡全池 0 张）

### u_0006 风险合同
```json
{
 "id": "u_0006",
 "name": "风险合同",
 "class": "shared",
 "type": "attack",
 "rarity": "common",
 "veins": [],
 "energy": 1,
 "effect": {
  "damage": 9,
  "hits": 1,
  "target": "single"
 },
 "cost_type": "vitality",
 "cost_text": "签约的手指失去了指纹。",
 "flavor": "第三条写：不保证返程。你签得太快，没看是谁替你担保。",
 "upgrade": {
  "name_suffix": "·续",
  "effect": {
   "damage": 12
  },
  "flavor_add": "续约不需要再看第三条。"
 }
}
```
补弱路：爆发流低成本位；把 vitality 代价带给震语者（1 张）/疯先知（0 张）

### u_0008 灰烬测振仪
```json
{
 "id": "u_0008",
 "name": "灰烬测振仪",
 "class": "shared",
 "type": "attack",
 "rarity": "uncommon",
 "veins": [
  "heat",
  "tremor"
 ],
 "energy": 1,
 "effect": {
  "damage": 6,
  "hits": 1,
  "target": "single",
  "resonance_gain": 2,
  "special": [
   {
    "code": "burn",
    "value": 2,
    "turns": 2
   }
  ]
 },
 "cost_type": "none",
 "cost_text": "",
 "flavor": "灰烬落进刻度盘的那一刻，岩层说了一个字。",
 "upgrade": {
  "name_suffix": "·敏",
  "effect": {
   "damage": 8,
   "resonance_gain": 3
  },
  "flavor_add": "它连你没听清的那一句都测出来了。"
 }
}
```
补弱路：灼烧×共振双读；下潜×灼烧、维护×灼烧两格的低配供给

### u_0009 倒转圣痕
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
补弱路：凝视控制→共振积累转换；疯先知×凝视格的白嫖通道

### u_0010 谐振垫层
```json
{
 "id": "u_0010",
 "name": "谐振垫层",
 "class": "shared",
 "type": "skill",
 "rarity": "uncommon",
 "veins": [
  "tremor",
  "mineral"
 ],
 "energy": 1,
 "effect": {
  "block": 7,
  "target": "self",
  "resonance_drain": 2
 },
 "cost_type": "none",
 "cost_text": "",
 "flavor": "把震动能垫在身下，你就成了地面的一部分。",
 "upgrade": {
  "name_suffix": "·厚",
  "effect": {
   "block": 10,
   "resonance_drain": 2
  },
  "flavor_add": "垫层旧了。你反而站得更稳。"
 }
}
```
补弱路：共振→格挡转换；维护者×共振（弱但有趣格）的消费端缺口；anm_0017 同结构需按 T334 重估定位

### u_0011 活水引泉
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
补弱路：回复×敏捷交叉（heal+dexterity 同卡全池 0）；震语者×再生（heal 0 职业的第一张直接回复）

### u_0012 双芯灯管
```json
{
 "id": "u_0012",
 "name": "双芯灯管",
 "class": "shared",
 "type": "attack",
 "rarity": "uncommon",
 "veins": [
  "light",
  "heat"
 ],
 "energy": 1,
 "effect": {
  "damage": 7,
  "hits": 1,
  "target": "single",
  "special": [
   {
    "code": "burn",
    "value": 1,
    "turns": 2
   }
  ]
 },
 "cost_type": "none",
 "cost_text": "",
 "flavor": "一根芯给你照亮，一根芯给你点火。厂里说这叫冗余。",
 "upgrade": {
  "name_suffix": "·并",
  "effect": {
   "damage": 10,
   "special": [
    {
     "code": "burn",
     "value": 2,
     "turns": 2
    }
   ]
  },
  "flavor_add": "两根芯烧成了一根。亮得更狠。"
 }
}
```
补弱路：灼烧流下潜侧供给 + bright 层双吃；§四修正：no_light 层整卡失效，「第 1 层替身」说法作废

### u_0013 散落的铅字
```json
{
 "id": "u_0013",
 "name": "散落的铅字",
 "class": "shared",
 "type": "attack",
 "rarity": "rare",
 "veins": [
  "tremor",
  "mineral"
 ],
 "energy": 1,
 "effect": {
  "damage": 4,
  "hits": 1,
  "target": "all",
  "special": [
   {
    "code": "weak",
    "turns": 2
   }
  ]
 },
 "cost_type": "none",
 "cost_text": "",
 "flavor": "报馆塌了以后，字比人先落地。踩到一个，你就慢半拍。",
 "upgrade": {
  "name_suffix": "·重",
  "effect": {
   "damage": 6,
   "special": [
    {
     "code": "weak",
     "turns": 3
    }
   ]
  },
  "flavor_add": "标题字最重。砸中最响。"
 }
}
```
补弱路：AoE+debuff 双空白（全体攻击 0 张带 debuff；weak 全池仅 2 张单体）

### u_0016 越权的批文
```json
{
 "id": "u_0016",
 "name": "越权的批文",
 "class": "shared",
 "type": "power",
 "rarity": "rare",
 "veins": [],
 "energy": 1,
 "effect": {
  "target": "self"
 },
 "cost_type": "none",
 "cost_text": "",
 "flavor": "签发栏是空的。你把名字签了上去，协议就开始执行。",
 "upgrade": {
  "name_suffix": "·Ⅱ",
  "effect": {
   "target": "self"
  },
  "flavor_add": "第二张批文用的是同一个章。章不问次数。"
 },
 "anmin_mark": {
  "kind": "protocol",
  "protocol": "purge"
 }
}
```
补弱路：协议流（幽灵流派）首个激活卡：purge 协议引擎全链路在案（自伤 2/回合、双方攻 +3）

### u_0007 传声钢缆
```json
{
 "id": "u_0007",
 "name": "传声钢缆",
 "class": "shared",
 "type": "skill",
 "rarity": "uncommon",
 "veins": [
  "light",
  "tremor"
 ],
 "energy": 1,
 "effect": {
  "block": 5,
  "draw": 1,
  "target": "self"
 },
 "cost_type": "none",
 "cost_text": "",
 "flavor": "一头接在灯上，一头接在岩层里。两边都以为对方在说话。",
 "upgrade": {
  "name_suffix": "·并联",
  "effect": {
   "block": 7,
   "draw": 1
  },
  "flavor_add": "第二根缆是多余的。多余的东西最结实。"
 }
}
```
补弱路：光脉染色×盾语循环互桥；降级说明：连携只计首脉（[engine/core.js:429] 未改前），层规则侧双脉全占

## 三、七张需要改引擎的（只列不实现）

| 草案名 | 缺的引擎能力 | 缺口位置 | 改动量 |
|---|---|---|---|
| u_0001 空的手（弃1抽2） | `discard` 键：弃手牌 | applyCardEffect 无此分支（[index.html:5807] 起） | 小：手牌选择 + splice |
| u_0002 守夜人的钟（格挡半保留） | keep_block 只查遗物 mod | endTurn [index.html:6042] 附近只遍历 run.relics | 小：同循环加 effect 标记检查 |
| u_0004 深井的回声（scry） | 看牌堆顶并重排 | 牌堆无 scry 概念 | 中：新 UI + 逻辑 |
| u_0005 预支的氧（能量时序） | effect 改 energy + 跨回合债务 | 能量只在 beginTurn 重置（[index.html:5620] 附近） | 小-中：beginTurn 一行 + 债务字段 |
| u_0014 共鸣腔（连携跨回合） | chain_keep：跳过回合清零 | beginTurn 的 veinChain={}（[index.html:5624] 附近） | 极小：豁免标记 |
| u_0015 借来的凝视（凝视转力量） | turn_start 的卡牌触发点 | turn_start 只遍历遗物（[index.html:6903]） | 中：power 的回合开始结算位 |
| u_0017 减压舱（解 debuff） | clear_debuffs | C.debuffs 无清除分支（[engine/core.js:655] 附近只 tick） | 极小：一行清空 |

## 四、对 T331 设计稿的两条诚实修正

1. **u_0012 的 no_light 保险丝说法不成立**：断光拦截是整卡 return（[index.html:5817]），双脉不能让 heat 端幸免。它在 no_light 层价值归零，真实价值是 bright 层 +2 双吃与灼烧流下潜侧供给；T332「下潜×灼烧」格判断不受影响，「第 1 层替身」一条作废。
2. **双脉连携是降级体验**：[engine/core.js:429] 改动前连携只计首脉。五张双脉草案（u_0007/0008/0010/0012/0013）上架都要带这条注记。

## 五、汇总表

| 项 | 数值 |
|---|---|
| 草案总数 | 17（10 零引擎改动 + 7 需改引擎） |
| id 区间 | u_0001–u_0017（与 539 现有 id 零撞车） |
| 费用分布 | 0 费 6 / 1 费 10 / 2 费 1（按 T331 原设计） |
| 稀有度分布 | common 3 / uncommon 9 / rare 5 |
| 无脉 | 6（环境免疫）；双脉 | 5（层规则双占、连携首脉） |
| 覆盖 T332 弱路 | 14 条中 9 条有直接供给（其余见 T342 的放弃/降级判断） |
| 引擎改动需求 | 极小 2 / 小 2 / 小-中 1 / 中 2（§三） |

## 决定记录

- class 取 shared 而非任务书示例的 universal：shared 是引擎现成通道（RAW.shared 已并入四职业），universal 需要新类别接入——按「不破坏已有数据」取前者。
- u_0016 越权的批文使用 anmin_mark 字段：全池 0 张卡带它、引擎两处读点在案（[index.html:5726]/[index.html:5754]），属于「已支持但卡池未用」的最优 case；协议效果强度在 T342 的协议流行里做风险标注。
- effect 字段全部落在引擎已实现集合（damage/hits/target/block/draw/heal/resonance_gain/resonance_drain/gaze_reduce/special:burn/weak/dexterity）——未发明任何新键；需新键的 7 张按任务书要求单独列出标「不实现」。
