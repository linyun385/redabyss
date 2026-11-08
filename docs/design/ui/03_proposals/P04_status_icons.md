# P04 · 状态图标系统

## 现状
敌人状态（weak/frail/burn/poison）只有文本拼接在 intent 行内（UI-006）。玩家自身状态（strength/dexterity/regenerate/thorns）在 HUD 无显示——只有 cardDesc 的文本输出。

## 玩家在这里会遇到什么
不知道自己有多少力量/敏捷加成——这些数值影响每张牌的伤害/格挡产出，但 HUD 不显示。敌人的 debuff 也不知道还剩几回合。

## 方案
- **A 玩家 buff 行**：HUD 加一行（或 emoji 行）显示力量+X/敏捷+X/再生 X/荆棘 X——从 `C.buffs` 读。
- **B 敌人状态图标**：UI-006 已写（icon + 剩余回合数）。
- **C 全局状态栏**：战斗屏底部加一条状态行（自己 buff + 敌人 debuff）——新增区域。

## 推荐
**A + B 组合**。A=HUD 追加一行 `div.hud-buffs`（render() 已有 C.buffs 数据）；B=UI-006 已写。A 约 10 行 JS + 5 行 CSS。

## 落地成本
A=15 行；B=20 行（UI-006 已写）。合计 ~35 行，不改引擎。
