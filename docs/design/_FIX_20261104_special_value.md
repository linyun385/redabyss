# 引擎修复记录 · 2026-11-04 · special 字段名不一致

> 作者：DSH 会话（不是 GLM）。**这份是记录，不是任务单** —— GLM 看到请勿重复修。
> 改动文件：`web/index.html`（同日备份 `index.html.bak-20261104-*-spvfix`）

## 起因

用户玩的时候察觉到「有些牌的效果数字不对」，追查确认是 bug，用户拍板**改引擎**。

## 问题 1：special 里数量字段名对不上（主 bug）

- 卡片数据写的是 `{"code":"strength","value":2}`
- `applySpecial` 读的是 `sp.v` → 读不到 → 全部退回**默认值**

受影响：`strength` `dexterity` `regenerate` `thorns` `gaze_reduce` `frail`。
结果举例：超频保养标称力量 +2，实际只有 +1；沉默权柄荆棘 4，实际 3。

### 修法（`applySpecial`，约 5855 行）

```js
const V = (sp.value !== undefined ? sp.value : sp.v);
```

`value` 优先，其次 `v`，都没有才用默认值。六个 case 全部改成用 `V`。
`weak` / `frail` 的回合数也从「只读 turns」改成「turns → value → 2」。

## 问题 2：special 里的 exhaust 不生效

- 卡片把「消耗」写在 `special:[{code:'exhaust'}]` 里
- `playCard` 只判断 `card.effect.exhaust` → 这类牌打完**照样回弃牌堆**，从没真被消耗
- `applySpecial` 里 `case 'exhaust': break; // 由 playCard 处理` —— 注释是错的，playCard 根本没处理

### 修法（`playCard`，约 5757 行）

```js
if (card.effect && (card.effect.exhaust ||
    (card.effect.special || []).some(sp => sp && sp.code === 'exhaust'))) C.exhaustPile.push(card);
```

和 `retain` 已有的写法保持一致（`retain` 早就是两种都认）。

## 顺带：卡面描述 `cardDesc` 一并对齐

游戏内卡面原来也只读 `s.v`，所以修了引擎之后卡面还是不显示数字（「力量」后面空着）。
现在 `cardDesc` 也用 `value` 优先，`weak`/`frail` 会显示回合数，`special` 里的 `exhaust` 也显示「消耗」。

## 验证

- `node tools/check_web.js` → **全部通过，0 个警告**（7 个 script 块全部语法可解析）
- `node tools/pack_check.js cards` → 全部通过（2 个警告是 57 张 vs 基础 40，长期存在，无关）
- 卡牌数据 `cards/*.json` **一个字没改**，只改引擎

## 副作用（用户已知悉）

这批效果现在按标称值生效，所以**部分卡牌变强**了：力量 / 敏捷 / 再生 / 荆棘 / 减凝视
这几类牌的数值普遍从「默认值」回到「标注值」。需要重新感受平衡。

## 相关工具

- `tools/card_desc.py` —— 按引擎代码把 effect 翻译成人话（本次一并新增）
- `tools/gen_card_effects.py` —— 生成 `docs/design/CARD_EFFECTS_AUTO.md`（219 张全表）
- `tools/card_studio.py` —— 卡牌设计工作台（`python tools/card_studio.py` → http://127.0.0.1:8771）
