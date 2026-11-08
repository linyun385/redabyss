# D2 · 误操作（10 区域 ×「最容易点错/拖错/看错什么」）

| # | 区域 | 最容易犯的误操作 | UI 有没有拦 | 建议 |
|---|---|---|---|---|
| 1 | 选人 | 双击职业卡直接开局（跳过详情） | ✅ 拦了——T78 要求点「以此身份下潜」才开局 | 维持 |
| 2 | HUD | 点零件以为有弹窗（cursor:pointer 但弹出面板无确认） | ❌ 直接弹 | 加弹窗标题 |
| 3 | 敌人 | 点已死敌人（.dead opacity .25 但 cursor:pointer 未禁） | ❌ 无拦截 | .dead 加 `pointer-events: none` |
| 4 | 手牌 | 拖牌拖到空白处（未到敌人区域）→ 牌回手但无提示 | ❌ 静默回手 | toast「未命中目标」 |
| 5 | 卡详情 | 按 Esc 关详情但 pending 未清 → 牌回到手但选中态残留 | ✅ closePanel 清 pending | 维持 |
| 6 | 日志 | 误以为日志可点击展开（视觉上像链接但不是） | N/A | 日志文字去 underline |
| 7 | 地图 | 点未访问格（.unseen opacity .35 仍可点？）| ✅ cursor: default（不可点）| 维持 |
| 8 | 事件 | 双击选项（第一次 click 走了，第二次弹到已消失的 DOM）| ❌ 无 debounce | click 后立即 removeEventListener |
| 9 | 奖励 | 三选一里双击两张卡（都塞进卡组）| ❌ 无防重入 | 选第一张后 removeEventListener |
| 10 | 全局 | 按空格想结束回合 → 无反应（Tab=总图，Enter/E=结束）| ❌ 无提示 | 空格也绑结束回合 |
