# D4 · 小屏适配（10 区域 × 1024×768）

| # | 区域 | 1024×768 会怎样 | 最先崩的元素 |
|---|---|---|---|
| 1 | 选人 | 4×200+3×26=878px < 1024 ✅ | 无 |
| 2 | HUD | 10 项 ~962px < 1024 ✅（勉强）；<960 换行被裁（UI-001） | #hud overflow:hidden |
| 3 | 敌人 | 3×230+2×20=730px ✅；5 只=1190px>1024 → overflow-x 滚动条 | .enemy 固定 230px |
| 4 | 手牌 | layoutFan span=min(66,max(38,(1024-170)/9))=38px → 9×38+150=492px ✅ | hover 上浮 46px 可能遮住敌人区 |
| 5 | 卡详情 | 304px right:2px + 手牌 492px = 798px < 1024 ✅ | 无 |
| 6 | 日志 | flex 1 1 0 弹性 ✅ | 无 |
| 7 | 地图 | #mm-dock.big min(980,94vw)=962px > 1024-20 ✅ 勉强 | #mm-body 高度 60vh=460px，剩余给日志 76px——刚好 |
| 8 | 事件 | .opts max-width 760px ✅；.shopgrid 4 列→4×200+36=836px ✅ | 无 |
| 9 | 奖励 | 3×190+2×18=606px ✅ | 无 |
| 10 | 全局 | --lane 1240 > 1024 → 内容梁被 95vw 限制？❌ `max-width: var(--lane)` = 1240px，**1024 viewport 下内容梁为 1240px → 溢出** | --lane 需要 min(1240, 100vw) |

结论：**1024px 下最先崩的是 --lane 超宽**——需要 `max-width: min(var(--lane), 100vw)`。其次 HUD overflow（UI-001）。
