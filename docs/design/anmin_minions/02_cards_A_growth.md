# 02 · 支柱 A · 局外成长（8 张）

> 「局外」= 一场战斗之外、一局之内。引擎真有的载体只有两个（已核对）：
> `run.strength`（`perm_strength` 写入，战斗结束写回，5988/6408 行）和 `run.parts`（零件库跨战斗持久，7119/7351 行）。
> 所以支柱 A 的三条路是：**① 零件结转（赚了带出场）② 零件买永久力量 ③ 用牌库质量换永久力量**。
> 需要新 run 字段的点子（永久上限、开场格挡、开场零件）全部在 `06_needs.md`，没混进来。

## 设计规则（本支柱专用）

- **永久力量基准价 = 2 零件/点**，与核心卡 0054（3 零件+1费 → 永久1+3伤）同档。本支柱所有 perm_strength 卡都按这个价定价，不破。
- **升级不写同 code 的 special**。引擎 `upgradeCard`（6559 行）对 special 是**追加**语义（空数组才清空），同 code 数值升级依赖叠加行为，除 `perm_strength`（5988 行实测累加）外未逐一验证 → 本支柱升级只改标量（damage/block/draw/part_cost）或追加不同 code。
- `mech_grow` 是**赋值不是累加**（6025 行 `C.buffs.mechGrow = V`）。本支柱两张 mech_grow 卡统一 `value:1`，与 0051 基础形态（1）互相覆盖是无操作；与 0051·Ⅱ（2）同回合时后打者会把速率压回 1——冲突矩阵见 `05_curves.md` 第二节。

---

## anm_0058 加班申报

```json
{
  "id": "anm_0058", "name": "加班申报", "class": "anmin", "type": "skill",
  "rarity": "common", "veins": ["mineral"], "energy": 0,
  "effect": {
    "target": "self",
    "special": [
      { "code": "mech_grow", "value": 1 },
      { "code": "exhaust" }
    ]
  },
  "cost_type": "none", "cost_text": "",
  "flavor": "加班费是没有的。申报通过，零件照计。",
  "upgrade": {
    "name_suffix": "·勤",
    "effect": { "draw": 1 },
    "flavor_add": "第二份申报批得更快。他们开始不看内容。"
  }
}
```

- pillar: **A** ｜ rate: 0费一次性 → 本回合每张牌 +1 零件（约 3~4 零件/次，收入低档）｜ why_vein: 矿——零件产出变厚是「我这边的数字变大」。
- 设计说明：0051 增生（势，永久在场）的低配单回合版，0费+消耗。给新档一个「第一回合就能摸到零件」的入口。升级加抽 1 补偿消耗的手感。
- 已知交互：与 0051 同回合先后打出互不叠加（赋值语义，值同为 1 无感）；见 `05_curves.md`。

## anm_0059 批量报废

```json
{
  "id": "anm_0059", "name": "批量报废", "class": "anmin", "type": "skill",
  "rarity": "common", "veins": ["water"], "energy": 1,
  "effect": {
    "target": "self",
    "special": [
      { "code": "discard_hand" },
      { "code": "parts_from_discard", "value": 2 }
    ]
  },
  "cost_type": "none", "cost_text": "",
  "flavor": "修不好的全折价。折出来的都是零件。",
  "upgrade": {
    "name_suffix": "·清",
    "effect": { "special": [ { "code": "energy_gain", "value": 1 } ] },
    "flavor_add": "清到最后一件，电表倒转了一格。"
  }
}
```

- pillar: **A** ｜ rate: 1费 → 手牌数×2 零件（约 6~10，爆发收入，代价是当回合空手）｜ why_vein: 水——把牌换成零件，是库内明列的水职责（「把零件换成牌 / 把牌换成零件」）。
- 设计说明：0057 更新换代（抽1+每张1零件）的姊妹卡：不抽牌、单价翻倍、手里清空。和 0057 构成「换一带一 / 报废清仓」两档。升级追加 `energy_gain`（不同 code，追加安全）。

## anm_0060 余量入库

```json
{
  "id": "anm_0060", "name": "余量入库", "class": "anmin", "type": "attack",
  "rarity": "common", "veins": ["mineral"], "energy": 1,
  "effect": {
    "damage": 5, "hits": 1, "target": "single",
    "special": [ { "code": "mech_grow", "value": 1 } ]
  },
  "cost_type": "none", "cost_text": "",
  "flavor": "打下来的东西先别扔。过秤，入册。",
  "upgrade": {
    "name_suffix": "·Ⅱ",
    "effect": { "damage": 7 },
    "flavor_add": "过秤的精度上去了。秤是它自己的骨头。"
  }
}
```

- pillar: **A** ｜ rate: 1费 → 5 伤 + 本回合每张牌 +1 零件（攻击里掺一份收入）｜ why_vein: 矿——伤害与零件产出都是自己变厚。
- 设计说明：让「进攻回合」也能产零件，收入路线不占额外卡位。升级只加伤害（不追加 mech_grow，避免叠加语义）。
- 已知交互：同 0058，赋值语义，见 `05_curves.md` 第二节。

## anm_0061 力量标定

```json
{
  "id": "anm_0061", "name": "力量标定", "class": "anmin", "type": "power",
  "rarity": "uncommon", "veins": ["mineral"], "energy": 2, "part_cost": 4,
  "effect": {
    "target": "self",
    "special": [ { "code": "perm_strength", "value": 2 } ]
  },
  "cost_type": "lock",
  "cost_text": "零件 -4，这张牌本场锁死。",
  "flavor": "标定仪走过全身。多出来的力气，当场转正。",
  "upgrade": {
    "name_suffix": "·精",
    "part_cost": 3,
    "flavor_add": "第二次标定免了手续费。"
  }
}
```

- pillar: **A** ｜ rate: 4零件+2费 → 永久力量 2（=2 零件/点，基准价，无伤害补贴）｜ why_vein: 矿。
- 设计说明：0054 武器试验（3零件+1费 → 永久1+3伤）的「纯标定」版：单价一样、去掉伤害、一次买两份、付 2 费。lock 代价与 0054 对齐，防止同场刷多张。

## anm_0062 固定资产

```json
{
  "id": "anm_0062", "name": "固定资产", "class": "anmin", "type": "power",
  "rarity": "uncommon", "veins": ["mineral"], "energy": 1, "part_cost": 3,
  "effect": {
    "target": "self",
    "special": [
      { "code": "perm_strength", "value": 1 },
      { "code": "strength", "value": 1 }
    ]
  },
  "cost_type": "none",
  "cost_text": "零件 -3。",
  "flavor": "记在你名下的部分不参与折旧。其余部分参与。",
  "upgrade": {
    "name_suffix": "·Ⅱ",
    "part_cost": 2,
    "flavor_add": "评估报告少了一页。少的那页写着折旧年限。"
  }
}
```

- pillar: **A** ｜ rate: 3零件+1费 → 永久力量 1 + 本场力量 1（永久按基准价、当场找零 1 点）｜ why_vein: 矿。
- 设计说明：三支柱里「两档变强」的直接样本：同一笔零件同时落在本场（便宜短命）和一局（贵但永久）。本场部分走 `strength`（战斗结束清），永久部分走 `perm_strength`，两个通道引擎都已实测（5971/5988 行）。

## anm_0063 编制扩充

```json
{
  "id": "anm_0063", "name": "编制扩充", "class": "anmin", "type": "attack",
  "rarity": "uncommon", "veins": ["mineral"], "energy": 2, "part_cost": 3,
  "effect": {
    "damage": 8, "hits": 1, "target": "single",
    "special": [ { "code": "perm_strength", "value": 1 } ]
  },
  "cost_type": "none",
  "cost_text": "零件 -3。",
  "flavor": "名额批下来了。干活的手多了一只，长在你身上。",
  "upgrade": {
    "name_suffix": "·满",
    "effect": { "damage": 11 },
    "flavor_add": "编制表背面还有一行。那一行没有名字。"
  }
}
```

- pillar: **A** ｜ rate: 3零件+2费 → 8 伤 + 永久力量 1（伤害侧按 0054 的 3 点补贴，本卡把补贴换成了更大的一拳）｜ why_vein: 矿。
- 设计说明：0054 的重攻击版：同价（3零件+永久1），把 1费3伤 换成 2费8伤。给「想赢这一场、也顺便变强」的回合一个选择。

## anm_0064 转正名额

```json
{
  "id": "anm_0064", "name": "转正名额", "class": "anmin", "type": "power",
  "rarity": "rare", "veins": ["mineral"], "energy": 1, "part_cost": 6,
  "effect": {
    "target": "self",
    "special": [ { "code": "perm_strength", "value": 3 } ]
  },
  "cost_type": "lock",
  "cost_text": "零件 -6，这张牌本场锁死。",
  "flavor": "试用期结束了。从今天起你是设备的一部分，设备也是。",
  "upgrade": {
    "name_suffix": "·批",
    "part_cost": 5,
    "flavor_add": "加急件。章还是热的。"
  }
}
```

- pillar: **A** ｜ rate: 6零件+1费 → 永久力量 3（2 零件/点，单卡最大笔）｜ why_vein: 矿。
- 设计说明：零件经济的「奢侈品」上限：一把存够 6 零件，可以一次换 3 点永久力量。lock 代价防止同场多张。定价严格 2 零件/点，不加码。

## anm_0065 清仓入库

```json
{
  "id": "anm_0065", "name": "清仓入库", "class": "anmin", "type": "skill",
  "rarity": "rare", "veins": ["water"], "energy": 1,
  "effect": {
    "draw": 2, "target": "self",
    "special": [
      { "code": "discard_hand" },
      { "code": "parts_from_discard", "value": 1 }
    ]
  },
  "cost_type": "none", "cost_text": "",
  "flavor": "仓库满了。满的仓库不发工资。清。",
  "upgrade": {
    "name_suffix": "·净",
    "effect": { "special": [ { "code": "energy_gain", "value": 1 } ] },
    "flavor_add": "清完最后一批，灯自己亮了。"
  }
}
```

- pillar: **A** ｜ rate: 1费 → 抽2后弃光全手、每张 1 零件（手牌上限 10 + 抽2，理论峰值 12 零件；常态 6~9。爆发收入，代价是本回合两手空空）｜ why_vein: 水——抽牌+弃牌+换零件，全是流动。
- 设计说明：零件收入的爆发口，R 位。执行顺序与 0057 相同（先 draw 后 discard_hand，0057 已实测，抽上来的牌也会被弃——这是既定行为，见 `_VERIFY_anmin_core_cards.md` 第五节第 3 条）。升级追加 `energy_gain`（不同 code）。

---

## 支柱 A 一览

| id | 名字 | 稀有度 | 脉 | 一句话 |
|---|---|---|---|---|
| anm_0058 | 加班申报 | common | 矿 | 0费消耗：本回合每张牌 +1 零件 |
| anm_0059 | 批量报废 | common | 水 | 1费：弃光手牌，每张 2 零件 |
| anm_0060 | 余量入库 | common | 矿 | 1费 伤5：本回合每张牌 +1 零件 |
| anm_0061 | 力量标定 | uncommon | 矿 | 2费4零件 lock：永久力量 2 |
| anm_0062 | 固定资产 | uncommon | 矿 | 1费3零件：永久力量 1 + 本场力量 1 |
| anm_0063 | 编制扩充 | uncommon | 矿 | 2费3零件 伤8：永久力量 1 |
| anm_0064 | 转正名额 | rare | 矿 | 1费6零件 lock：永久力量 3 |
| anm_0065 | 清仓入库 | rare | 水 | 1费：抽2，弃光全手每张 1 零件 |

稀有度分布 3C/3U/2R（派单参考值 4/3/2，「大致即可」；A 柱的永久力量天然偏 U/R，多压了一张 C）。
