# HY4 任务：卡牌特效需求清单（纯统计）

## 一、任务是什么

项目 `C:\Users\Administrator\Desktop\杂七杂八\红渊\game` 的卡牌数据在：

```
cards\*.json
```

每张卡都是一个 JSON 对象，主要字段：

```json
{
  "id": "anm_0054",
  "name": "武器试验",
  "type": "attack",              // attack | skill | power
  "veins": ["mineral"],          // light | mineral | tremor | heat | water，可能为空数组
  "energy": 1,
  "effect": {
    "damage": 3, "hits": 1,      // 伤害与段数，可能没有
    "block": 0,                  // 护甲，可能没有
    "heal": 0,                   // 治疗，可能没有
    "draw": 0,                   // 抽牌，可能没有
    "special": [ { "code": "perm_strength", "value": 1 } ]   // 可能没有
  },
  "cost_type": "lock"            // none | memory | vitality | lock | mark
}
```

## 二、你要产出什么

一张 CSV，一行一张卡，列固定为这 9 列，顺序不许变：

```
id,name,type,veins,damage,hits,block,heal,special_codes
```

各列填法：

| 列 | 怎么填 |
|---|---|
| `id` | 卡片 id 原样 |
| `name` | 卡名原样 |
| `type` | attack / skill / power 原样 |
| `veins` | 全部脉，多个用 `+` 连（如 `light+heat`）；为空就留空 |
| `damage` | `effect.damage` 的数字；**没有就填 0** |
| `hits` | `effect.hits` 的数字；**没有就填 1** |
| `block` | `effect.block` 的数字；没有填 0 |
| `heal` | `effect.heal` 的数字；没有填 0 |
| `special_codes` | `effect.special` 里所有 `code`，用 `+` 连；没有就留空 |

## 三、硬规矩

1. **只读不写**。`cards\` 下任何文件一个字都不许改。
2. **只统计不判断**。不要写「这张卡应该配什么特效」「建议加什么效果」——那些是我的活。
3. **不许猜**。字段缺失就按上表填默认值（0 / 1 / 空），不要从卡名反推。
4. 覆盖**全部** class（diver / tremor / cangmin / anmin），一个都不能漏。
5. 如果某个 json 文件解析失败，记下来告我，不要跳过装没看见。

## 四、交付

存到：

```
tasks\hy4_vfx_inventory.csv
```

UTF-8 无 BOM，逗号分隔。字段里若出现逗号（比如卡名），用双引号包住。

存完回我三行：

1. 一共多少张卡
2. 有没有解析失败的文件
3. 有没有哪张卡缺 `effect` 字段

## 五、我会怎么验收

随机抽 5 张，自己去 `cards\` 里核对数字。**只要有一个数字对不上，整批退回。**
