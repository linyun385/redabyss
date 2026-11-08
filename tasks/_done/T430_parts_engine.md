# T430 · 零件进战斗 · 引擎改造单（DSH 执行）

> 这是**给我自己（DSH）的施工单**，不是给 GLM 的。GLM 不许碰 `web/`。
> 上位设计：`tasks/T400_vein_system_master.md` §2.2「维护者的零件体系」
> 前置已做：`BASE_ENERGY = 4`（2026-11-04）、工作台已加 `core` / `play_idea` 字段

---

## 现状（2026-11-04 实测，非推断）

| 项 | 位置 | 现状 |
|---|---|---|
| 零件库存 | `run.parts` | 战斗结束时 **`run.parts = C.parts`（覆盖）** |
| 战斗内零件 | `C.parts` | `startCombat` 初始化为 0，击杀时 `+= drop`（boss 10 / elite 4 / 普通 1~2） |
| 代价结算 | `applyCardCost(C, card)` | 纯 `switch`，只扣不检查；已有 memory / vitality / mark / lock |
| 代价改写遗物 | `applyCardCost` 开头 | `cost_redirect` 把代价改成凝视，**只排除 lock** |
| 初始卡组 | `newRun` 里按 classId 硬编码 | 维护者分支：`add(atk,5); add(def,4); add(anmin_sign,1)` |
| 商店 | `showShop` / `buildShopStock` | 纯金币，**无零件分支** |

---

## 改动 1 · 零件跨战斗累积

**问题**：现在 `run.parts = C.parts` 是覆盖，每场清零，「战后改造」攒不起来。

**改法**：把「战斗内产出」和「库存」分开记账。

```js
// 战斗开始时记下库存
C.partsStockAtStart = run.parts;

// 战斗中 C.parts 只记本场掉落
// 战斗结束时：
const gained = C.parts - C.partsStockAtStart;   // 本场净增
run.parts = Math.max(0, run.parts + gained);
```

或者更简单：**战斗中直接写 `run.parts`**，`C.parts` 只做显示。但要注意 `startCombat` 会把 `C.parts` 重置，需要一并改。

**验收**：打两场普通战斗，第二场结束后 `run.parts` 应 ≈ 两场掉落之和，不是只等于最后一场。

---

## 改动 2 · `cost_type` 加第六种：`part`

**数据结构**：卡牌加一个数值字段 `cost_part`（整数），不放 `cost_text` 里。

```json
{
  "cost_type": "part",
  "cost_part": 6,
  "cost_text": "六个零件，从你身上拆下来。"
}
```

**改三处**：

### 2a. 打出前检查够不够

`applyCardCost` 只扣不检查，所以要**在 `playCard` 的合法性检查里**加一条：

```js
if (card.cost_type === 'part' && (C.parts || 0) < (card.cost_part || 0)) {
  return { ok: false, msg: '零件不足（需要 ' + (card.cost_part||0) + '）' };
}
```

⚠️ 位置：要在**扣能量之前**。现在 `playCard` 里 `C.energy -= cost` 早于 `applyCardCost`，检查必须更早。

面板上也要能看见：费用不足时卡面置灰（现有 `cant` 类可复用）。

### 2b. `applyCardCost` 加 case

```js
case 'part': {
  const need = card.cost_part || 0;
  C.parts -= need;
  log(C, '「' + card.name + '」' + (card.cost_text || '零件入库。') + '（零件 -' + need + '）');
  break;
}
```

### 2c. `cost_redirect` 遗物要排除 `part`

现有一行：

```js
if (card.cost_type !== 'lock') { ...redirect... }
```

改成：

```js
if (card.cost_type !== 'lock' && card.cost_type !== 'part') { ...redirect... }
```

**理由**：如果零件代价被改写成凝视，那「用零件付大代价」这个设计的核心就失效了。零件是维护者独占的支付方式，不该被别的遗物改写。

---

## 改动 3 · 定价基准（写进卡牌，不进代码）

| 原本的代价 | 零件价 |
|---|---|
| 失去 8 生命 | 6 |
| 弃 1 张牌 | 8 |
| 锁死（本场不能用） | 5 |

**这条不写进代码**，写进 `docs/design/` 的写卡规范，由写卡人遵守。
代码只负责「有多少扣多少」。

---

## 改动 4 · 维护者的金币初始牌

**问题**：维护者拿不到金币（战斗 / 遗物 / 事件的金币全部折算成零件），商店对他无用。

**解法**：专属初始牌。参数：

| 项 | 值 |
|---|---|
| id | `anm_00xx`（下一个可用号，工作台的 `nextId` 会算） |
| 名字 | 自拟，建议和「兑换 / 结算 / 工分」有关 |
| 类 | 技能 |
| 费 | 1 |
| 稀有度 | 特殊（`special`，不进奖励池） |
| 代价 | `lock`（本场战斗限一次） |
| 效果 | 生成 **20 金币** |
| 用后 | **回牌库**（不消耗，下一场还能用） |

**效果实现**：现有 effect 键里如果没有「给金币」，要新增。

```js
// applyEffect 里
if (eff.gold) { run.gold += eff.gold; log(C, '「' + card.name + '」兑换成 ' + eff.gold + ' 金。'); }
```

⚠️ 要先确认现有 effect 有没有 `gold` 键，没有就新增。**新增前先查全池使用次数**（工作台会显示），避免和别的卡撞。

**初始卡组注入**：`newRun` 的维护者分支加一行 `add(新卡id, 1)`。

**数据落位**：`cards/anmin.json` 加卡 → 跑 `_sync_cards.js` → 内联 `RAW` 同步。

---

## 改动 5 · 商店（待定，不阻塞）

维护者商店收零件的方案还没定（收零件 / 专属商品 / 保持现状）。

现状下维护者拿 200 金左右，能买最便宜的（60 金回血）但买不起稀有的（320 金）。

**先不做**，等核心卡写完、实测过金币够不够再定。

---

## 改动 6 · 工作台支持

`card_studio.py` 的 `E.cost_type` 加一项：

```python
'part': '零件'
```

编辑区加一个「零件数」输入框，**只在 `cost_type === 'part'` 时值得填**。

导出补丁时保留 `cost_part` 字段（`clean()` 只剥 `_` 开头，这个不受影响）。

---

## 执行顺序（每步可独立验证）

| # | 改什么 | 验证方式 |
|---|---|---|
| 1 | 零件累加 | 打两场，看 `run.parts` 是不是两场之和 |
| 2 | 工作台加 `part` 代价 | 能新建一张零件代价的卡，草稿里字段完整 |
| 3 | `playCard` 加零件检查 | 零件不够时打不出去，有提示 |
| 4 | `applyCardCost` 加 case | 打出去扣零件，日志有记录 |
| 5 | `cost_redirect` 排除 part | 带批文遗物时零件代价不被改写 |
| 6 | 金币 effect + 初始牌 | 开局手牌里有它，打出去金币 +20，本场不能再打 |

**每步都要**：`node tools/check_web.js` 0 警告 + 改前备份 `web/index.html`。

---

## 不做的事（写在这，免得以后误加）

| 不做 | 原因 |
|---|---|
| 场上零件 / 场外零件双池 | 用户 2026-11-04 定：单池，本局内跨战斗累积 |
| 其他三个角色加跨局成长 | 他们的成长路径是「拿新牌」，不需要 |
| 零件代价被遗物改写 | 会架空整个设计 |
| 花零件的牌 0 费 | 能量约束会失效，见 T400 §2.2 |
