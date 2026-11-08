# T360 · 通用牌池扩充（17 → 40+，全部可落地）

> 委托人：用户。原话：「就整了 10 张通用牌吗？这不合理吧，那有通用牌数量远少于角色牌的卡牌游戏……这里还是得排任务」。
> 现状：`cards/shared.json` 11 张（share_0001 + u_0003/0006/0007/0008/0009/0010/0011/0012/0013/0016），
> 另有 7 张（u_0001/0002/0004/0005/0014/0015/0017）需要改引擎，暂不上架。
> 工作目录：`C:\Users\Administrator\Desktop\杂七杂八\红渊\game`

---

## 目标

**通用牌从 17 张设计扩到 40 张可落地**（不含需要改引擎的）。

对标：每职业 57 张，40 张通用牌 = 每个职业的 70%，任何一局都能频繁见到通用牌，「通用牌支撑弱流派」这个设计才立得住。

---

## 三条硬约束（违反即作废）

### 1. 只许用引擎已实现的字段

动笔前**必须**先读：
- `engine/core.js` 的 `applyCardEffect` 和 `applySpecial`（哪些 effect 键真被读）
- `cards/*.json` 全池 209 张，统计**哪些 effect 键已经被用过**（用过的必然支持）

**不许**发明新字段。如果某个想法必须新字段，列进「需要改引擎」小节，不进主表。

### 2. 不许和现有 209 张撞效果

每张新牌写完后，用脚本或在脑内核对：`type + rarity + energy + effect 键组合` 不能与现有卡**完全相同**。
（T321 已经证明六成卡是换皮，这次不许再造换皮。）

### 3. 必须填满覆盖矩阵

40 张要按这个矩阵分布，**每格至少 1 张，空格直接判不通过**：

| 费用 \ 类型 | attack | skill | power |
|---|---|---|---|
| 0 费 | 4 | 4 | — |
| 1 费 | 8 | 8 | 2 |
| 2 费 | 6 | 4 | 2 |
| 3 费 | 2 | — | — |

合计 40 张。稀有度也不许全挤在一档：common ≈ 45%、uncommon ≈ 35%、rare ≈ 20%。

---

## 设计原则

1. **每张牌必须服务一个具体目标**，写在这张牌的 `notes` 里，只能从这三类选：
   - 「补弱路」——对应 T332 的 14 条弱路之一（写清是哪一条）
   - 「补空档」——某个费用/类型格子在此前只有 0–1 张
   - 「补机制」——引擎有某 effect 但全池 0–2 张在用（先统计出来）
2. **通用牌要真的通用**：不许有强职业倾向。判断标准——四职业都能用它赢一局。
3. **代价系统要散开**：`cost_type` 在所有通用牌里要有 memory / vitality / mark / lock / none 五种分布，别全是 none。
4. 文风照 `data/copy/new_cards.md` 已有的那批（冷、短、像记录）。

---

## 分批做（做完一批立刻自检）

### 第 1 批：0 费 + 1 费（16 张）
- 产出到 `docs/design/universal2/B1.json`（纯 JSON 数组，字段结构照抄现有 shared.json）
- 自检：`python tools\_check_universal.py docs/design/universal2/B1.json`

### 第 2 批：2 费 + 3 费（12 张）
- `docs/design/universal2/B2.json`

### 第 3 批：power 类（6 张）
- `docs/design/universal2/B3.json`

### 第 4 批：补足覆盖矩阵 + 查重（6 张）
- `docs/design/universal2/B4.json`
- 本批必须跑一遍全池查重，输出一张「新牌 vs 旧牌 效果指纹」对照表，证明零重复

每批完成追加 `TASK_DONE.md` 一条。

---

## 自检脚本（先写它，再写牌）

写 `tools/_check_universal.py`，检查：
1. JSON 能解析、字段齐全（id/name/class/type/rarity/veins/energy/effect/cost_type/cost_text/flavor/upgrade）
2. `class` 必须是 `shared`
3. id 不撞现有（读 cards/*.json + 全部 enemies/events/relics 的 id）
4. effect 的每个键都在「已被全池用过」的名单里（名单从 cards/*.json 统计）
5. 和现有卡的效果指纹不重复
6. 稀有度/费用分布符合矩阵

脚本输出 `通过 N / 不通过 M`，不通过必须列清原因。

---

## 做完之后

四批齐了，把 B1–B4 合并成 `docs/design/universal2/ALL.json`，跑一次最终自检，然后**停下等验收**——
贴进游戏由 DSH 侧做，你只交 JSON。

## 禁止

- 不许改 `cards/*.json`、`engine/*`、`web/*`（只写 `docs/design/universal2/` 和那个自检脚本）
- 不许写「参考现有牌」而不给具体设计
- 不许凑数：每张都要能说清它补什么
