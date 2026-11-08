# D7 · 状态提示（10 区域 × 每种状态能不能看出来）

| # | 区域 | 状态数 | 每种能看出来吗 |
|---|---|---|---|
| 1 | 选人 | 2（hover/focus） | ✅ 两者都有独立视觉 |
| 2 | HUD | 6（hp-low/dying/pulse/flash/clarity-low/normal） | ⚠ hp-low 和 dying 都变红但 dying 有动画 |
| 3 | 敌人 | 6（targetable/dead/hitflash/atk-hot/drop-hot/normal） | ✅ 每种有独立视觉（但 debuff 状态无可视化——UI-006） |
| 4 | 手牌 | 8（dimmed/costly/wrongworld/selected/upgraded/dragging/shakeit/normal） | ✅ 每种有独立 CSS |
| 5 | 卡详情 | 3（open/closed/play-disabled） | ✅ hidden class 切换 |
| 6 | 日志 | 4（turnline/hurt/blocked/normal） | ✅ 每种有独立颜色+样式 |
| 7 | 地图 | 8（pick/here/near/unseen/btrack/hl/cursor/fog） | ✅ 每种有独立 stroke/fill |
| 8 | 事件 | 3（normal/disabled/hover） | ✅ |
| 9 | 奖励 | 2（normal/dimmed） | ✅ |
| 10 | 全局 | 5（shake/eggflash/resflash/dying/perf-low） | ✅ 每种有独立动画 |
