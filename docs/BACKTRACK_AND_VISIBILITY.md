# BACKTRACK_AND_VISIBILITY — T75 两机制交付说明

> 2026-10-31。任务书 `tasks/T75.md`。改动范围：`web/index.html` ==T56-MAP-CSS== / ==T56-MAP-MODULE==
> 两段 + `tools/mapgen_spec.json`（rescue.backtrack）+ `tools/mapgen_test.js`（同步断言）
> + 新增 `tools/check_backtrack.js`。mapgen 生成逻辑零改动。

## 1. 可见性规则（问题 1）

「不应该隐藏还未走过但显示的路径的实际块是什么」——可见的节点直接亮真身：

| 节点状态 | 渲染 | DOM |
|---|---|---|
| **可见** = 已访问 ∪ 邻接已访问（`pruneForFrontend(region, visited, 1)` 口径） | 真实类型图标 ⚔☠✧◈✉⌂◆◉，全亮（已访问）/近亮（邻接未访问，`.near`） | **带 `data-type`**（combat/elite/…），aria 含类型词 |
| **可见范围外** | 一律 `?`，半透明（`.unseen`），边与外圈压暗（`.fog`） | **不带 `data-type`**，aria 只报「未探明，深度带Dn」 |

- 渲染从「只画可见子图」改为**全图渲染**：不可见节点以 `?` 出现在图上（结构可见、类型保密），
  不可见边压暗——玩家看得见路通向哪儿，走近才知道是什么。
- **图例**写在小图面板里（选择态大图顶部横条）：`⚔敌袭 ☠头目 ✧变数 ◈补给 ✉遭遇 ⌂休整 ◆跨带BOSS
  ◉最终BOSS ?未探明`，右侧红字提示「**看得到的地方，就知道是什么**」；总图 hint 行带同一图例。
- 实测（1280×720，mapseed=1234，走 2 格后）：窗口内 50 节点 = 可见 6（全部带 data-type、无一个 `?`）
  + 不可见 44（全部 `?`、data-type 泄漏 0）；禁字扫描 clean。
- 截图：`docs/shots_t75/07_visible_types_legend.png`（可见真身 + 图例 + 结构全景）。

## 2. 回返（问题 2）

「你可以直接走回这个分支，但会遭遇坏的事件或战斗，乃至可能遇见 boss」：

- **入口**：小图/总图上，**已访问且是当前格直接入邻**的节点带虚线圈（`.btrack`），点击即回返；
  死路时流程面板出现「**必须回返**」按钮（同一逻辑）。
- **每次回退 1 格**（只允许直接入邻，不能跳回起点）；回走不记新的行进边、不重复记行程。
- **必定触发一次遭遇**（`rescue.backtrack` 表，与死路救援共用同一套判定 `backtrackRoll`）：

| 判定 | 概率 | 内容 |
|---|---|---|
| 坏事件 | 45% | 扣血（当前生命 8–15%）或扣金币（15–25%）各半，带一句文本 |
| 战斗 | 30% | 该带普通池随机 **2–3** 只 |
| 精英 | 15% | 该带精英池 |
| 跨带 BOSS | 8% | 该带 BOSS 池（实测真的遇到了） |
| 空手而归 | 2% | 无事发生 |

- **参数位置**：`tools/mapgen_spec.json → rescue.backtrack`（badEvent/combat/elite/boss/none/hpPct/goldPct，
  v1.8 changelog 在案）；web 运行时 `P.rescue.backtrack` 与之同步（`check_backtrack.js` 对拍）。
- **共用判定**：死路救援（旧「另寻一路」伏击/惩罚二选一）废弃，改为同一 `backtrackRoll` 表 + 同一
  `resolveEncounter`——「你走到死路了必须回返也是相同的逻辑」。
- 回返不杀人（生命扣到 1 保底，与死路救援同一取舍）；回返战斗照常走奖励链（赢了有奖励）。
- 防刷保护：`pickableIds` 排除已访问格、`enterNode` 对已访问格转回返——重进已访问格不再重触发内容。

## 3. 实测证据

**分布（`node tools/check_backtrack.js`，500 次，发货代码抽取评测）**：

```
判定      次数   实测%   目标%   偏差
badEvent   217   43.4     45   -1.6pp  ✓
combat     163   32.6     30   +2.6pp  ✓
elite       71   14.2     15   -0.8pp  ✓
boss        36    7.2      8   -0.8pp  ✓
none        13    2.6      2   +0.6pp  ✓
```

**持久回返日志（跨战斗不丢，`NewMap.debug.backtrackLog()`）实测 4 条**：

```
回返的代价：暗处的一记冷手，生命 -12。        （坏事件·扣血）
回返惊动了大家伙——跨带的它转过头来。          （跨带BOSS 遭遇）
死路回返：退回 冻井站台（D1）。               （死路必须回返）
回返的代价：碎屑在暗处散了一路，金币 -52。    （坏事件·扣金币）
```

对应状态变化：生命 80→68、金币 173（-52 那次）。

**死路**：`debug.forceDeadEnd()`（固定 seed）→ 流程面板出「必须回返」按钮 + 概率提示 → 点击 →
退回上一格 + 共用遭遇。截图 `docs/shots_t75/09_deadend_backtrack.png`、`10_deadend_must_backtrack.png`。

## 4. 截图索引（docs/shots_t75/）

| 文件 | 内容 |
|---|---|
| 07_visible_types_legend.png | 可见节点真身 + 图例条 + `?` 只在视野外 |
| 08_backtrack_after.png | 回返后（生命 80→72，日志在案） |
| 09_deadend_backtrack.png | 死路提示「必须回返」+ 概率行 |
| 10_deadend_must_backtrack.png | 必须回返按钮特写（验收 #5） |

## 5. 复核方式

```bash
node tools/check_backtrack.js     # 分布表 + web 参数对拍 + 确定性（exit 0）
node tools/mapgen_test.js         # spec 同步（rescue.backtrack 断言）+ 200/200 + <2s
node tools/check_web.js && node tools/test_engine.js && node tools/pack_check.js all
```
浏览器（1280×720）：选择态大图 → 走 2 格 → DOM 探针（data-type/无类型/?计数）→ 点虚线圈回返 →
看遭遇面板与日志 → `forceDeadEnd` → 「必须回返」。
