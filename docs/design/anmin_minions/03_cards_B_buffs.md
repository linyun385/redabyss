# 03 · 支柱 B · 自身加成（8 张）

> 「本场立刻变强，便宜、短命」：buff 全部走引擎已实测的加法通道——`strength` / `dexterity` / `regen` / `thorns` 都是 `+=` 累加（5971–5974 行），战斗结束随 C 清空。
> 与支柱 A 的关系是**两档**：本场变厚（本支柱，便宜）vs 一局变厚（支柱 A，2 零件/点永久力量）。同一张卡不应同时主打两档——例外是 0062（固定资产），它就是用来示范两档怎么拼的。
> 升级规则同支柱 A：不写同 code special（`regen`/`thorns`/`dex` 虽已证实累加，但升级一律改标量或追加不同 code，把语义风险压到零）。

## 设计缺口（为什么是这几张）

对照旧卡（含判定保留的 20 张）：力量有 0015、敏捷有 0016、再生有 0040、格挡有 0004/0010/0017/0024——**荆棘是零**。维护者的「外壳/锚定」题材下荆棘是空位，本支柱 4 张荆棘把它立成小体系：挂上之后「敌人打你=拆它自己」，配合再生（0072）变成磨损战打法。

---

## anm_0066 外挂装甲

```json
{
  "id": "anm_0066", "name": "外挂装甲", "class": "anmin", "type": "skill",
  "rarity": "common", "veins": ["mineral"], "energy": 1,
  "effect": {
    "block": 6, "target": "self",
    "special": [ { "code": "thorns", "value": 2 } ]
  },
  "cost_type": "none", "cost_text": "",
  "flavor": "装甲不挑来向。谁撞上来，谁留下点东西。",
  "upgrade": {
    "name_suffix": "·厚",
    "effect": { "block": 9 },
    "flavor_add": "第二层装甲焊死了。焊枪顺手也焊了袖口。"
  }
}
```

- pillar: **B** ｜ rate: 1费 → 6 挡 + 荆棘 2（挡低于基准 0004 的 7，差额换 2 点常驻反伤）｜ why_vein: 矿——格挡和荆棘都是自己的数字变厚。
- 设计说明：荆棘体系的入门件。升级只加挡。

## anm_0067 衬层加固

```json
{
  "id": "anm_0067", "name": "衬层加固", "class": "anmin", "type": "skill",
  "rarity": "common", "veins": ["mineral"], "energy": 1,
  "effect": {
    "block": 4, "target": "self",
    "special": [ { "code": "dexterity", "value": 1 } ]
  },
  "cost_type": "none", "cost_text": "",
  "flavor": "衬层装上就不拆。这不是加固，是长死。",
  "upgrade": {
    "name_suffix": "·Ⅱ",
    "effect": { "block": 6 },
    "flavor_add": "第二次加固的时候，衬层先裹住了手。"
  }
}
```

- pillar: **B** ｜ rate: 1费 → 4 挡 + 敏捷 1（敏捷复利起点：之后每张格挡牌永久 +1）｜ why_vein: 矿。
- 设计说明：把「一次性挡」换成「挡的斜率」。当场挡很少（4），但剩下的战斗里每张格挡牌都厚 1 点。升级加挡不加敏捷（敏捷是 0073 的主线）。

## anm_0068 静态防御

```json
{
  "id": "anm_0068", "name": "静态防御", "class": "anmin", "type": "power",
  "rarity": "common", "veins": ["mineral"], "energy": 1,
  "effect": {
    "target": "self",
    "special": [ { "code": "thorns", "value": 2 } ]
  },
  "cost_type": "none", "cost_text": "",
  "flavor": "不还手。你打我的部分，归我。",
  "upgrade": {
    "name_suffix": "·Ⅱ",
    "effect": { "special": [ { "code": "dexterity", "value": 1 } ] },
    "flavor_add": "外壳通上了地线。打上来的劲会漏走一半。"
  }
}
```

- pillar: **B** ｜ rate: 1费 → 荆棘 2 常驻（纯反伤引擎件，无即时数值）｜ why_vein: 矿。
- 设计说明：与 0066 拆开：这张是「势」，不带当场格挡，纯给反伤。升级追加 `dexterity`（不同 code，追加安全；`dex` 累加语义已在 5972 行证实）。

## anm_0069 循环液补给

```json
{
  "id": "anm_0069", "name": "循环液补给", "class": "anmin", "type": "skill",
  "rarity": "common", "veins": ["water"], "energy": 1,
  "effect": {
    "heal": 5, "draw": 1, "target": "self"
  },
  "cost_type": "none", "cost_text": "",
  "flavor": "循环液是新配的。配比表上有一栏写着：不必知道。",
  "upgrade": {
    "name_suffix": "·新",
    "effect": { "heal": 7 },
    "flavor_add": "新的这批更稠。说明里多了一行：请勿搅拌。"
  }
}
```

- pillar: **B** ｜ rate: 1费 → 5 血 + 抽 1（续航+过牌双份小收益）｜ why_vein: 水——**沿用库内惯例**：现有治疗牌（0012/0029/0032 等）全部标水，本卡跟标。严格按速查卡判据（去掉「抽」后还剩完整治疗）这不是纯水；库内现状如此，本卡不带头改，此标注供维护者裁定。
- 设计说明：0012 维修凝胶删除后的 U 位以下治疗补位（C 位，带 1 抽）。

## anm_0070 双层甲板

```json
{
  "id": "anm_0070", "name": "双层甲板", "class": "anmin", "type": "skill",
  "rarity": "uncommon", "veins": ["mineral"], "energy": 1,
  "effect": {
    "block": 7, "target": "self",
    "special": [ { "code": "retain" } ]
  },
  "cost_type": "none", "cost_text": "",
  "flavor": "外层挡冲击。内层挡清点。",
  "upgrade": {
    "name_suffix": "·Ⅲ",
    "effect": { "block": 10 },
    "flavor_add": "第三层是空的。空的那层最挡。"
  }
}
```

- pillar: **B** ｜ rate: 1费 → 7 挡 + 保留（可以捏在手里当底牌，留到需要的回合）｜ why_vein: 矿。
- 设计说明：0043 静默段徵章（挡10+保留，special 位）的 U 位前置版。retain 由 beginTurn 处理（5608 行认 effect.retain 或 special code，两种写法引擎都收；本卡用 special code 与 0043 同款）。

## anm_0071 主承重结构

```json
{
  "id": "anm_0071", "name": "主承重结构", "class": "anmin", "type": "skill",
  "rarity": "rare", "veins": ["mineral"], "energy": 2,
  "effect": {
    "block": 16, "target": "self"
  },
  "cost_type": "none", "cost_text": "",
  "flavor": "这根柱子接手之后，塌不塌轮不到你操心。",
  "upgrade": {
    "name_suffix": "·固",
    "effect": { "block": 20 },
    "flavor_add": "验收章盖上去的时候，柱子响了一声。谁也没提。"
  }
}
```

- pillar: **B** ｜ rate: 2费 → 16 挡（每能量 8 挡，高于 0004 基准的 7，无附加纯大盾）｜ why_vein: 矿。
- 设计说明：R 位大盾，给「这一回合硬吃大招」一个明确答案。对照 0017（改后挡10+排共振8）：本卡更贵更厚、无共振操作。

## anm_0072 自修复框架

```json
{
  "id": "anm_0072", "name": "自修复框架", "class": "anmin", "type": "power",
  "rarity": "rare", "veins": ["mineral"], "energy": 2,
  "effect": {
    "target": "self",
    "special": [
      { "code": "regenerate", "value": 3 },
      { "code": "thorns", "value": 2 }
    ]
  },
  "cost_type": "none", "cost_text": "",
  "flavor": "框架自己在补。补的材料从哪来，别问。",
  "upgrade": {
    "name_suffix": "·活",
    "effect": { "special": [ { "code": "dexterity", "value": 1 } ] },
    "flavor_add": "框架补得比拆得快了。头一回有这种事。"
  }
}
```

- pillar: **B** ｜ rate: 2费 → 每回合回 3 + 荆棘 2（磨损战引擎：敌人打你掉自己血，你每回合往回长）｜ why_vein: 矿。
- 设计说明：再生 3 对齐 0040 例外条款的量级（0040 是 1费 纯再生 R），加荆棘 2 和 1 费构成差异。荆棘+再生是维护者「设备肉盾」打法的上限件。升级追加 `dexterity`（不同 code）。

## anm_0073 液压助力

```json
{
  "id": "anm_0073", "name": "液压助力", "class": "anmin", "type": "skill",
  "rarity": "uncommon", "veins": ["mineral"], "energy": 1,
  "effect": {
    "block": 5, "target": "self",
    "special": [ { "code": "dexterity", "value": 2 } ]
  },
  "cost_type": "none", "cost_text": "",
  "flavor": "助力来自液体。液体来自管道。管道通向哪，表盘不显示。",
  "upgrade": {
    "name_suffix": "·压",
    "effect": { "block": 8 },
    "flavor_add": "表针过了红线，停住了。它自己停的。"
  }
}
```

- pillar: **B** ｜ rate: 1费 → 5 挡 + 敏捷 2（敏捷路线主件：一次给 2 点斜率）｜ why_vein: 矿。
- 设计说明：0016 安全线（R 势，敏捷2）的 skill 位同款：当场挡 5 补偿非「势」形态。与 0067（挡4+敏1）构成敏捷斜率的 1/2 两档。

---

## 支柱 B 一览

| id | 名字 | 稀有度 | 脉 | 一句话 |
|---|---|---|---|---|
| anm_0066 | 外挂装甲 | common | 矿 | 1费：挡6 + 荆棘2 |
| anm_0067 | 衬层加固 | common | 矿 | 1费：挡4 + 敏捷1 |
| anm_0068 | 静态防御 | common | 矿 | 1费 势：荆棘2 |
| anm_0069 | 循环液补给 | common | 水 | 1费：回5 + 抽1 |
| anm_0070 | 双层甲板 | uncommon | 矿 | 1费：挡7，保留 |
| anm_0073 | 液压助力 | uncommon | 矿 | 1费：挡5 + 敏捷2 |
| anm_0071 | 主承重结构 | rare | 矿 | 2费：挡16 |
| anm_0072 | 自修复框架 | rare | 矿 | 2费 势：再生3 + 荆棘2 |

稀有度分布 4C/2U/2R（派单参考值 4/3/2，U 位让给了 0073 的敏捷主件）。
