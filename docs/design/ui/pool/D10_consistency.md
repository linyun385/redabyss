# D10 · 一致性（10 区域 × 按钮/面板/间距/字重是不是同一套语言）

| # | 区域 | 按钮 | 面板 | 间距 | 字重 | 一致？ |
|---|---|---|---|---|---|---|
| 1 | 选人 | 无按钮（卡面即按钮） | #class-modal-box 独立样式 | gap 26px | h1 30px / cname 17px | ⚠ 与战斗按钮样式不同（ border-radius 6 vs 4） |
| 2 | HUD | 无按钮 | #hud 独立样式 | gap 18px + 3px | k 10px / v 14px | ✅ |
| 3 | 敌人 | 无按钮 | .enemy 独立样式 | gap 20px | ename 继承 / hpnum 12px | ✅ |
| 4 | 手牌 | #btn-end / #btn-help / #btn-world | #hand 独立 | gap 16px | 14px | ⚠ #btn-help 30px 圆形 vs #btn-end 矩形——形状不一致 |
| 5 | 卡详情 | #cd-play / #cd-cancel / .cd-close | #card-detail 独立 | gap 10px | 12.5px / 14px | ✅ 按钮样式统一（#1a0d0e bg / --red-hi text） |
| 6 | 日志 | 无按钮 | #log-wrap 独立 | padding 8px 14px | 12px | ✅ |
| 7 | 地图 | #btn-fullmap / #fm-close / #fm-zbar buttons | #minimap / #fullmap-box 独立 | gap 4px | 11-12px | ⚠ #fm-zbar 按钮样式与 #btn-end 不同（background:none vs #1a0d0e） |
| 8 | 事件 | .optbtn（纸片） | #flow-panel 共用 | gap 12px | 15px | ✅ T76 统一 |
| 9 | 奖励 | .btnrow button | #flow-panel 共用 | gap 12px | 14px | ✅ |
| 10 | 全局 | .fontbtns（11px 小按钮） | 独立 | gap 4px | 11px | ⚠ .fontbtns 与 #btn-help 尺寸接近但样式不同 |

**不一致 4 处**：#btn-help 圆形 vs 其他矩形 / #fm-zbar 按钮无底色 vs #btn-end 有底色 / .fontbtns 11px vs 按钮标准 14px / 选人模态 border-radius 6 vs 其他 4。均为 P2 级不一致——不影响功能但影响「同一套语言」的感觉。
