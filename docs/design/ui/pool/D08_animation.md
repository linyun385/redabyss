# D8 · 动效时机（10 区域 × 该有的没有/不该有的太多）

| # | 区域 | 现有动效 | 缺的 | 多余的 |
|---|---|---|---|---|
| 1 | 选人 | hover 上浮+阴影+focus 双阴影 | 卡面入场动画（首次加载瞬间闪现） | 无 |
| 2 | HUD | block pulse / gaze blink / parts float / hp shake | **共振临界闪烁（P08 提案）** | 无 |
| 3 | 敌人 | hitflash 0.12s / intent pulse 1.4s / float-up 0.4s | **死亡淡出后消失动画（现在是直接 opacity 变低）** | 无 |
| 4 | 手牌 | hover 上浮+scale / drag / shake / ghost-fly / costly 变色 | **能量不足时 cost 圈闪红** | 无 |
| 5 | 卡详情 | 无动效（瞬间显示/隐藏） | **打开/关闭 transition（0.15s slide-in）** | 无 |
| 6 | 日志 | turnline 闪现 0.6s | 新行从底部滑入 | 无 |
| 7 | 地图 | pick 脉冲+光晕 / here 粗框 / hover 上浮 | 无 | 无 |
| 8 | 事件 | 无（选项瞬间出现） | 选项依次淡入（stagger 0.1s） | 无 |
| 9 | 奖励 | 无（卡瞬间出现） | 卡依次翻入（flip 0.2s） | 无 |
| 10 | 全局 | shake 0.22s / dying 红光 / resflash 0.5s / eggflash 0.4s / cardfly 0.22s | 层切换过渡（当前瞬间切屏） | 无 |

全部动效都有 `@media (prefers-reduced-motion: reduce)` 覆盖（:517-524）和 `body.perf-low` 自动降级（:651-655）。
