# P07 · 层规则触发的视觉提示

## 现状
8 条层规则触发时的提示方式：
- no_light/cold/dry：红字 log（一次性警告）
- heat_tick/rad_tick：**无提示**（每回合默默扣血）
- burn_hand：**无提示**（每回合默默烧手牌）
- bright：**无提示**（正向 buff 也无声）
- void/lock/overload：通过 MODE_REACTION 文本 log

## 玩家在这里会遇到什么
heat_tick/rad_tick 是**每回合持续发生**的——玩家不知道为什么在掉血。burn_hand 也是。只有进入层时的那一条红字警告，之后就没有了。

## 方案
- **A HUD 常驻层规则图标**：HUD 加一个「当前层规则」图标（如 ☀️=heat_tick / ☢=rad_tick / 🔥=burn_hand）——常驻提醒。
- **B 每次 tick 时飘字**：heat_tick 每次触发时飘「-2 🔥」——rad_tick 飘「-1 ☢ +1牌」。
- **C 层进入时全屏 banner**（复用 #phase-banner）：进入层时显示层规则 3 秒——之后靠玩家记忆。

## 推荐
**B（每次 tick 飘字）+ A（HUD 图标）组合**。B 让玩家知道「现在在扣血」，A 让玩家知道「为什么」。B 约 5 行 JS（tick 处加 floatText）；A 约 10 行 JS + 3 行 CSS。

## 落地成本
B=5 行 JS；A=15 行。合计 ~20 行，不改引擎。
