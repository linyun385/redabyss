# P06 · 费用与能量的即时反馈

## 现状
能量不足的牌有 `.dimmed`（opacity .35）+ `cursor: not-allowed`。`playBlockReason()` 返回「能量不足」。拖到 #btn-end 时 `.shakeit` 动画。

## 玩家在这里会遇到什么
牌变暗了但**不知道还差多少能量**——需要自己算（手牌费用总和 vs 剩余能量）。

## 方案
- **A dimmed 牌显示差量**：`.dimmed` 的 `.cost` 圆圈改为红色 + 显示「差 X」——render() 里已有差量计算逻辑。
- **B 能量条变色**：能量 ≤1 时能量图标变灰/闪烁——暗示「快没了」。
- **C dimmed 牌显示锁图标**：cost 圆圈变 🔒——视觉暗示「打不了」。

## 推荐
**A**。`render()` 构建手牌时已经调 `playBlockReason(card)`——在返回「能量不足」时把 `.cost` 的文本从费用数字改为「差 X」即可。约 5 行 JS。

## 落地成本
A=5 行 JS。B=3 行 CSS。C=3 行 JS + 1 个 SVG。
