# 04 · 支柱 C · 零件经济（8 张）

> 零件是维护者唯一的职业货币。本支柱只做两件事：**花钱**（把零件换成即时数值/持续收益）和**给花钱一个理由**（收入卡在支柱 A，本支柱不重复铺）。
> 汇率分三档（对齐核心卡既定价位，见 `05_curves.md`）：
> - 低档：**1 零件 ≈ 6 点即时数值 或 1.5 张牌**（救急，对照 0056 重铸：1零件=抽1+1能量）
> - 中档：**2~3 零件 → 一份当轮收益**（对照 0054 试验：3零件→永久1+3伤）
> - 高档：**4~6 零件 → 持续性/爆发性收益**（对照 0055 发电：5零件→永久虚弱脆弱+双钩子）
> 全部走引擎已实测的字段与 code：`part_cost` 不足时拒出牌（第一轮落地第 4 项）、`energy_gain`/钩子/`random_effect` 都在 5966 起的 switch 里。

---

## anm_0074 快换钻头

```json
{
  "id": "anm_0074", "name": "快换钻头", "class": "anmin", "type": "attack",
  "rarity": "common", "veins": ["mineral"], "energy": 0, "part_cost": 1,
  "effect": {
    "damage": 6, "hits": 1, "target": "single"
  },
  "cost_type": "none",
  "cost_text": "零件 -1。",
  "flavor": "钻头型号跟伤口腔径对得上。对不上就换，一秒。",
  "upgrade": {
    "name_suffix": "·利",
    "effect": { "damage": 8 },
    "flavor_add": "换上的这根不是配发给你的。没人问来路。"
  }
}
```

- pillar: **C** ｜ rate: 1零件+0费 → 6 伤（低档基准：1 零件 ≈ 6 即时数值）｜ why_vein: 矿。
- 设计说明：零件的「零钱」用法：能量不够时用零件补攻击。0费位对照 0002（1费9）：本卡省 1 费、花 1 零件、少 3 伤。

## anm_0075 临时装甲板

```json
{
  "id": "anm_0075", "name": "临时装甲板", "class": "anmin", "type": "skill",
  "rarity": "common", "veins": ["mineral"], "energy": 0, "part_cost": 1,
  "effect": {
    "block": 6, "target": "self"
  },
  "cost_type": "none",
  "cost_text": "零件 -1。",
  "flavor": "板是临时的。挡下来的那一下是真的。",
  "upgrade": {
    "name_suffix": "·厚",
    "effect": { "block": 8 },
    "flavor_add": "「临时」两个字被划掉了。没写改成什么。"
  }
}
```

- pillar: **C** ｜ rate: 1零件+0费 → 6 挡（低档，与 0074 对称的防御侧）｜ why_vein: 矿。
- 设计说明：与 0074 成对，让「零件换挡」和「零件换伤」共用同一条低档汇率，玩家学一次就会用两向。

## anm_0076 液压猛冲

```json
{
  "id": "anm_0076", "name": "液压猛冲", "class": "anmin", "type": "attack",
  "rarity": "uncommon", "veins": ["mineral"], "energy": 1, "part_cost": 2,
  "effect": {
    "damage": 15, "hits": 1, "target": "single"
  },
  "cost_type": "none",
  "cost_text": "零件 -2。",
  "flavor": "压力表进红区的那半秒，正好够撞穿一扇门。",
  "upgrade": {
    "name_suffix": "·爆",
    "effect": { "damage": 19 },
    "flavor_add": "第二次冲撞没留门。门也没了。"
  }
}
```

- pillar: **C** ｜ rate: 2零件+1费 → 15 伤（中档：1费基准 9 + 2 零件买 6）｜ why_vein: 矿。
- 设计说明：中档伤害购买件。2 零件的增量是 +6 伤，比低档（1零件=6伤）严格一半——多买不优惠，防止零件无限堆伤害。

## anm_0077 预载料斗

```json
{
  "id": "anm_0077", "name": "预载料斗", "class": "anmin", "type": "skill",
  "rarity": "common", "veins": ["water"], "energy": 0, "part_cost": 1,
  "effect": {
    "draw": 3, "target": "self"
  },
  "cost_type": "none",
  "cost_text": "零件 -1。",
  "flavor": "料斗先装满。装什么后面再说。",
  "upgrade": {
    "name_suffix": "·Ⅱ",
    "effect": { "draw": 4 },
    "flavor_add": "斗沿加高了一截。加高用的料也是斗里的。"
  }
}
```

- pillar: **C** ｜ rate: 1零件+0费 → 抽 3（低档：1 零件 ≈ 1.5 张牌；对照 0009 料仓取件 0费抽2，本卡贵 1 零件多 1 张）｜ why_vein: 水——抽牌是流动本体。
- 设计说明：把零件倒进牌的流量口。0费+抽3 是「这回合想做事但没能量」的通用答案。

## anm_0078 寄生电路

```json
{
  "id": "anm_0078", "name": "寄生电路", "class": "anmin", "type": "power",
  "rarity": "rare", "veins": ["mineral"], "energy": 1, "part_cost": 4,
  "effect": {
    "target": "self",
    "special": [
      { "code": "energy_on_enemy_attack", "value": 1 },
      { "code": "enemy_defend_draw", "value": 1 }
    ]
  },
  "cost_type": "none",
  "cost_text": "零件 -4。",
  "flavor": "电路接进它的供电回路。它每次出手，都替你发电。",
  "upgrade": {
    "name_suffix": "·密",
    "part_cost": 3,
    "flavor_add": "接线改了隐蔽走线。它到现在没发现电少了。"
  }
}
```

- pillar: **C** ｜ rate: 4零件+1费 → 敌方每次攻击回 1 能量、每次防御抽 1 张（高档：按敌方行为的持续收益）｜ why_vein: 矿。
- 设计说明：0055 发电的「只留钩子」版：不带虚弱/脆弱，所以零件从 5 降到 4、能量从 3 降到 1。两个钩子 code 与 0055 完全相同，行为已被 45 项实测覆盖。升级只降零件。

## anm_0079 临时功率上调

```json
{
  "id": "anm_0079", "name": "临时功率上调", "class": "anmin", "type": "skill",
  "rarity": "uncommon", "veins": ["mineral"], "energy": 0, "part_cost": 3,
  "effect": {
    "target": "self",
    "special": [ { "code": "strength", "value": 2 } ]
  },
  "cost_type": "none",
  "cost_text": "零件 -3。超幅部分本战斗有效。",
  "flavor": "功率上调不问设备的意见。设备就是你的意见。",
  "upgrade": {
    "name_suffix": "·Ⅱ",
    "part_cost": 2,
    "flavor_add": "第二次上调，表针跳过了中间那格。"
  }
}
```

- pillar: **C** ｜ rate: 3零件+0费 → 本场力量 2（中档：1.5 零件/点本场力量，对照永久力量的 2 零件/点——当场 buff 必须便宜过永久，否则没人买短命的）｜ why_vein: 矿。
- 设计说明：0015 主控授权（1费 力量2 无零件）的零件付费版：省 1 费、花 3 零件。升级只降零件（不追加 strength，避免叠加语义问题）。

## anm_0080 原型机点火

```json
{
  "id": "anm_0080", "name": "原型机点火", "class": "anmin", "type": "attack",
  "rarity": "rare", "veins": ["mineral"], "energy": 2, "part_cost": 5,
  "effect": {
    "damage": 28, "hits": 1, "target": "single"
  },
  "cost_type": "none",
  "cost_text": "零件 -5。",
  "flavor": "点火程序跳过了自检。自检是给要重复用的机器准备的。",
  "upgrade": {
    "name_suffix": "·轰",
    "effect": { "damage": 34 },
    "flavor_add": "点完火它就没打算再点。所以这次烧的是全部。"
  }
}
```

- pillar: **C** ｜ rate: 5零件+2费 → 28 伤（高档：对照 2费≈18 伤基准，5 零件买 +10 伤，2 数值/零件——高档件按「战略一击」定价，单价低于低档是刻意的：多买不优惠）｜ why_vein: 矿。
- 设计说明：单回合「能量+零件一起砸」的终点卡。与支柱 A 的收入卡形成闭环：前面存的零件，最后在这里变现。

## anm_0081 抽检轮盘

```json
{
  "id": "anm_0081", "name": "抽检轮盘", "class": "anmin", "type": "skill",
  "rarity": "rare", "veins": ["tremor"], "energy": 0, "part_cost": 2,
  "effect": {
    "target": "self",
    "special": [ { "code": "random_effect" } ]
  },
  "cost_type": "none",
  "cost_text": "零件 -2。",
  "flavor": "抽检合格率百分之百。抽到什么，什么就是合格品。",
  "upgrade": {
    "name_suffix": "·转",
    "part_cost": 1,
    "flavor_add": "转盘修过一次。修完好像更准了，没人证实。"
  }
}
```

- pillar: **C** ｜ rate: 2零件+0费 → 随机 5 选 1（回3血/3伤/5挡/抽1/1能量；期望约 1.9 点泛用价值，方差就是价格的一部分）｜ why_vein: **震**——震判据「拿到就能用、用在哪都不亏、但都不顶尖」：5 选 1 正是不保证最好也不落空。本批唯一一张非矿水卡。
- 设计说明：复用 0053 悬浮体的随机池（`random_effect`，6036 行，5 项已实测）。定位是「不粘手的零食」：对比悬浮体（3 零件买一个每回合的随机），本卡 2 零件买一次性的，不占「势」位。

---

## 支柱 C 一览

| id | 名字 | 稀有度 | 脉 | 一句话 |
|---|---|---|---|---|
| anm_0074 | 快换钻头 | common | 矿 | 0费1零件：伤6 |
| anm_0075 | 临时装甲板 | common | 矿 | 0费1零件：挡6 |
| anm_0077 | 预载料斗 | common | 水 | 0费1零件：抽3 |
| anm_0076 | 液压猛冲 | uncommon | 矿 | 1费2零件：伤15 |
| anm_0079 | 临时功率上调 | uncommon | 矿 | 0费3零件：本场力量2 |
| anm_0078 | 寄生电路 | rare | 矿 | 1费4零件：敌攻回能1+敌防抽1 |
| anm_0080 | 原型机点火 | rare | 矿 | 2费5零件：伤28 |
| anm_0081 | 抽检轮盘 | rare | 震 | 0费2零件：随机5选1 |

稀有度分布 3C/2U/3R（派单参考值 4/3/2；高档件按经济设计需要占了 3 个 R 位）。
脉分布：6 矿 / 1 水 / 1 震。
