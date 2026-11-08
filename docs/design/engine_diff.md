# G05 · 引擎双副本差异全清单（engine/core.js vs web/index.html 内联副本）

> 方法：从两份文件按函数级抽取（括号配对取函数体）→ 空白规范化 → MD5 对比。**只读对比，不改任何文件。**
> 数据：`data/audit/engine_diff.json`（机器结果）；行号为 2026-11-05 快照。

## 一、结构总账

| 项 | 值 |
|---|---|
| core.js 函数数 | 41 |
| web 内联引擎区段函数数 | 41 |
| **完全一致** | **36** |
| **有分歧** | **5**（applyCardCost / applySpecial / endTurn / playCard / startCombat） |
| 仅 core 有 / 仅 web 有 | **0 / 0**（函数集合一一对应） |
| 常量 | BASE_ENERGY：core **3** vs web **4**；HAND_LIMIT 10=10；DRAW_PER_TURN 5=5 |

## 二、五处分歧逐条

| # | 函数 | 谁新 | 差异内容 | 影响 |
|---|---|---|---|---|
| D1 | **applySpecial** | **web 新**（2026-11-04 修） | web 有 `const V = sp.value ?? sp.v` 归一化（`web/index.html:5860-5862`，_FIX_20261104_special_value.md 记录）；core 仍只读 `sp.v` → strength/dexterity/regenerate/thorns/burn/gaze_reduce/poison/weak/frail 全按**默认值**结算 | **core 副本的特殊效果数值全部失真**（力量 2 变 1 这类） |
| D2 | **applyCardCost** | **web 新**（2026-11-04） | memory 代价分支 web 多了「告诉玩家删了哪张牌」的 log（原注释：玩家只会觉得牌库莫名少一张）；core 无此 log | core/sim 的 memory 体验与实跑不同（纯 log，不影响数值） |
| D3 | **endTurn** | **web 新**（2026-10-29 对齐） | keep_block「只留一半」规则两侧都在，但 core 多一段旧注释且 log 措辞不同 | 数值行为一致；仅注释/文案漂移 |
| D4 | **playCard** | 文案分叉 | 锁死提示：core「这张牌已锁死」vs web「这张牌本场已锁死」 | 纯文案 |
| D5 | **startCombat** | **web 多** | web 开头调 `applyLayerTheme(run.depth)`（UI 层主题染色）；core 无此函数（UI 职责，本不该在 core） | 预期内差异：UI 挂载点 |
| — | 常量 BASE_ENERGY | **web 新**（T400 §2.4） | core=3 / web=4 | **core 世界能量少 1**——见下节影响 |

## 三、core.js 现在还有没有被用到（结论：**有，而且是活的**）

引用 `engine/core.js` 的文件（grep 实测 10 个）：
`tools/sim.js`、`tools/test_engine.js`、`tools/econ_sim.js`、`tools/_feel_check.js`、`tools/_t24_engine.js`、`tools/_t48_check.js`、`tools/_t61_check.js`、`tools/_t63_check.js`、`tools/_t63_data.js` 等——`tools/sim.js:7` `const RA = require('engine/core.js')`，node 实测 require 成功。

**含义**：
1. `web/index.html` 不引用 core.js（游戏实跑走内联副本）——玩家不受影响。
2. **所有模拟与测试工具跑在过期引擎上**：sim.js 世界里能量=3、特殊效果数值=默认值（力量+2 当 +1 结算）。基于 sim 的历史结论（BALANCE_T29 的胜率/使用率等）与实跑游戏不是同一套参数——**引用旧 sim 结论时必须标注口径**。
3. 本夜所有 DPS=15 口径按能量 4 算（与 web 一致），与 sim 旧数据不可直接混合比较。

## 四、同步建议（只建议，不改）

1. 最小修：把 D1（value 归一化）与 BASE_ENERGY=4 同步进 core.js——sim 立刻与实跑同参数。
2. 结构修：web 内联副本改为「构建时从 core.js 注入」或反向「core.js 从 web 抽取生成」，消灭手工双誊抄（master/00 篇第 4 节铁律的自动化版）。
3. 文案级分歧（D2/D4）同步与否不影响数值，随批处理。

## 复算

```bash
python data/audit/… # 函数抽取脚本内嵌于本篇来源（engine_diff.json 为机器结果）
grep -c "case '" engine/core.js  # applySpecial case 数对照
grep -rln "require.*core" tools/ | wc -l  # 引用工具数
```
