# FINAL_REGRESSION.md — 终局回归（T70 产出）

> 产出时点：T67（素材接入）/ T68（新地图默认）/ T69（素材补齐）完成后。全部数字来自脚本与浏览器实测，无手填。
> 素材状态：79/79 已生成并外置（web/assets/art/，架构变更后不再内联）。

## 1. 三检查器

| 检查器 | 结果 |
|---|---|
| pack_check.js all | 全部通过（5 个警告——扩充警告通道：敌 113/卡 83+83/遗物 77/事件 82） |
| test_engine.js | 全部通过 |
| check_web.js | 全部通过（0 警告；background-image 全 data: 内联；外链探针三连 FAIL 见 ART_DELIVERY §3） |

## 2. 地图生成回归

| 项 | 结果 |
|---|---|
| mapgen_test.js（200 seed 不变量） | 全部断言通过（bindingFallbacks=0、source 全 table） |
| mapgen_sim.js --runs 500 可通关率 | **100%**（500/500，failSeeds 空） |
| 死路率（救援次数/局） | 0.00（分布 {0:500}） |
| BOSS 战/局 | 3.31（理论 Σp+1=3.288 ✓） |
| 类型到访率 | combat 25.4% / elite 24.1% / random 26.1% / shop 23.0% / event 27.3% |

## 3. 四职业模拟（--runs 300/职业，与 T49 基线比）

| 职业 | T49 基线 | T70 | Δ | 判定（±8pp） |
|---|---|---|---|---|
| diver | 2.6% | 4.7% | +2.1pp | ✓ |
| tremor | 2.6% | 4.0% | +1.4pp | ✓ |
| anmin | 0.8% | 2.0% | +1.2pp | ✓ |
| cangmin | 3.4% | 3.3% | −0.1pp | ✓ |

（与 T65 数字一致——seed 确定性复现。整体 +1~2pp 的浅升归因：新敌稀释高强度对局 + diver 新 0 费格挡卡。）

## 4. 内容绑定

check_bindings.js：**256/256 格类型达标、boss 池跨生态零共用、兜底 0 次**（mapgen_test 断言固化）。

## 5. 体积

| 项 | 数值 |
|---|---|
| index.html 本体 | 455 KB（架构变更后素材外置，旧 1.6MB 增量预算随之作废；1.5MB 警告线未触发） |
| 素材目录 web/assets/art | 79 张 / 合计 1,924 KB（独立于 HTML，不占单文件体积） |
| 最大单图 | 50 KB（q82、长边 ≤768） |
| 单文件硬上限 | 3MB 规则已由用户改为 1.5MB 警告——HTML 455KB 远低于该线 |

## 6. 界面压测（浏览器实测）

| 项 | 结果 |
|---|---|
| 10 手牌 + 小地图 + 右侧信息区 | 无整页滚动条 ✓、结束回合在视口内 ✓ |
| 总图缩放/拖动 | viewBox 实测变化 ✓（滚轮 + 拖拽） |
| 未访问节点在 DOM | 不存在（data-nid 全集 = pruneForFrontend 理论可见集，逐 id 比对一致）✓ |
| 三主题截图 | docs/artstyle/preview/final_off.png / final_B.png / final_C.png ✓（素材满版状态重拍，敌图 1/1、2/2 接入） |
| 小图居中（地图选择态）+ 键盘选路 | 方向键移动/空格进入实测 ✓（箭头空间移动、空格派发战斗/事件） |
| 小图/总图截图 | docs/artstyle/preview/final_minimap.png / final_fullmap.png ✓ |

截图：小图/总图 = docs/artstyle/preview/final_minimap.png / final_fullmap.png ✓（素材满版状态）。

## 7. 新地图默认

**不带任何 query 参数打开 = 新地图**（66 格面板 + 居中小图 + 总图；旧 4 行图仅在 `?map=old` 显式回退）。截图：docs/artstyle/preview/final_default_newmap.png ✓（实测断言：newMap=true / 66 nodes / oldRows=0 / 小图居中且不压标题）。

## 8. 问题清单（只记录不修）

| # | 问题 | 影响 | 去向 |
|---|---|---|---|
| 1 | 生图速度 ~5-9 分钟/张（VAE fp32 upcast 疑为主因） | 全量 79 张需数小时 | T67/T69 已如实记录；性能调优另开任务 |
| 2 | 敌图 3 张/生态按 id 哈希共享（非每怪专属） | 同生态敌人共用图 | 扩 manifest 到 113 张量级另立任务 |
| 3 | B 语言偶发细边框（负面词已含 border 仍出现） | 图案区多一圈细框 | 负面词加重 + 闸门兜底，T69 生成后复检 |
| 4 | A 语言罗马数字不稳定 | 结局图顶部可能无数字 | 标题/数字由游戏 UI 叠加，无功能影响 |
| 5 | UI 视觉整体（用户自评「太丑」） | — | 等用户参考图，另开任务 |
| 6 | T47 卡池结构问题 12 项（黯民 2 费真空等） | 平衡 | 维持「只列不改」 |
| 7 | mapgen 自然死路率 0（贪心模拟） | 救援功能触发少 | 参数可调（maxInDeg/extraBranchOdds），设计取舍维持 |
