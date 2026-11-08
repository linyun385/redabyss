# P02 · 出牌到命中的轨迹

## 现状
出牌时 `.ghost-fly` 从手牌位置飞向 `translateY(-80px) scale(.65) rotate(6deg)`——**向上飞**（远离敌人）。敌人区在手牌上方。ghost-fly 不追踪目标位置。

## 玩家在这里会遇到什么
牌往上飞——但敌人就在上面。视觉上牌「飞向天花板」而不是「飞向敌人」。多敌时更困惑：哪张飞向哪个？

## 方案
- **A 固定上飞（现状）**：不改。优点=零成本；缺点=与目标无关。
- **B 飞向目标**：计算 target 敌人的 `getBoundingClientRect`，ghost-fly 的终点改为该坐标。需要 JS 计算终点。优点=因果最清晰。
- **C 飞向屏幕上沿**：不改终点但改角度——所有 ghost-fly 统一 `translateY(-200px)`，让飞行距离更长更醒目。

## 推荐
**B（如果改 doPlay 传 targetIdx）或 C（不改引擎）**。B 需要 `doPlay` 把 targetIdx 传给渲染层——引擎已有 `targetIdx` 参数，只改 CSS 的 `@keyframes cardfly` 为 JS 动态计算终点。约 15 行 JS。
C 是一行 CSS 改动（改 translateY 值），零风险。

## 落地成本
C=1 行 CSS；B=~15 行 JS（在 doPlay 后计算坐标并设置 CSS custom property）。
