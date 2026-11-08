# P10 · 战斗节奏引导

## 现状
战斗中玩家「该做什么」完全靠自学。出牌阶段/待选目标阶段/结束阶段没有视觉状态指示。

## 玩家在这里会遇到什么
打出一张 needsTarget 的牌 → 进入 pending → 屏幕上没有任何状态变化（敌人只是加了 .targetable 边框）——新手不知道「现在要选目标」。

## 方案
- **A 状态横幅**：复用 #phase-banner 显示「选择目标」/「打出阶段」——半秒出现。
- **B 光标变化**：pending 态改 body cursor 为 crosshair——暗示「要选目标」。
- **C toast**：pending 时 toast('选择一个目标')——已有（`:8117`）。

## 推荐
**A + B**。A 复用已有 #phase-banner（10 行 JS）；B 一行 CSS（`body.pending { cursor: crosshair }`）。C 已有但 toast 3 秒消失，不够持久。

## 落地成本
A+B=~12 行。
