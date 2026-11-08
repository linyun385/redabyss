# G02 · 本夜六项关键发现复核（证据 / 影响面 / 严重度）

> 复核方法：全部重新 grep 实证（行号为 2026-11-05 本夜快照），不引用记忆。每条：证据位置 / 影响面 / 严重度。
> 严重度分级：**P0 玩家可见的功能错误** / P1 数据与表现不一致或误导 / P2 文档与代码漂移 / P3 记录在案待拍板。

## 发现 1 · frail（脆弱）是死状态 —— P0

- **证据**：
  - 施加点：`engine/core.js:497` / `web/index.html:5866`（applySpecial case 'frail'，写入 `t.status.frail`）
  - 递减点：`engine/core.js:675` / `web/index.html:6047`（回合结束减到 0 删除）
  - **全文件 grep `status.frail` 仅上述 4 处**——玩家→敌人伤害结算 `dealToEnemy`（core.js:490 附近）只扣格挡与血，从不读 `status.frail`；敌方受击路径无任何 frail 乘区。
- **影响面**：2 张卡（dive_0022 硬矿钻（重型）、trem_0034 震语：断流）的脆弱挂件零结算——挂件占用了卡牌定价的一部分价值；玩家打了「脆弱」看不到任何效果变化。
- **严重度**：**P0**——玩家可见的功能静默失效（不是文案问题，是结算缺失）。
- **关联**：dead_card_check.md #3/#4、natural_combos.md 断头协同 #2、_BUGS.md。

## 发现 2 · u_0009 的 special 码 `resonance_gain` 无 case —— P0

- **证据**：
  - 卡数据：`cards/shared.json` u_0009 倒转圣痕 `special:[{code:"gaze_reduce",value:2},{code:"resonance_gain",value:3}]`
  - 引擎 switch：`grep "case 'resonance_gain'" engine/core.js web/index.html → 0 处`；u_0009 打出时落入 applySpecial 的 default 分支（core.js:515 附近），红字「这张牌有个效果这一版还没做（resonance_gain）」，共振 +3 不生效。
  - 对照：效果键 `resonance_gain` 本身有实现（core.js:478 `if (e.resonance_gain)`）——修法就是换入口或补 case。
- **影响面**：1 张卡（u_0009）的一半效果失效且每次打出弹红字警告；它同时是「凝视管理+共振」通用件（rarity uncommon，进奖励池）。
- **严重度**：**P0**——玩家每次打出都看到报错式反馈。

## 发现 3 · u_0016 靠 anmin_mark 激活协议，effect 字段为空 —— P1

- **证据**：
  - 卡数据：u_0016 越权的批文 `effect:{target:"self"}` 空，但带 `anmin_mark:{kind:"protocol",protocol:"purge"}`
  - 引擎读取：`web/index.html:5754`（activateProtocol）、`:5726`（协议去重判断）；purge 结算 `engine/core.js:291`（每回合自伤 2）、`:463`（玩家攻击 +3）、`:734`（敌方攻击 +3）
  - 表现层：effect 空 → cardDesc 无效果文本（`web/index.html:8126` 的 cardDesc 只遍历 effect 键）——卡面上看不到任何说明。
- **影响面**：1 张卡功能正常但零描述 + rare 位；purge 的自伤/加攻全程无 UI 状态显示（T451 #8）。
- **严重度**：**P1**——不是功能错误，是「生效但玩家看不见」的呈现缺陷 + 一次性红字缺失。
- **备注**：本夜初版曾误判它「完全空转」，已在中途更正（TASK_DONE 有更正条）；master/03_ENGINE.md 早就写了「u_0016 通过 json 赋值解决」——本夜实读与此互证。

## 发现 4 · engine/core.js 是过期副本，且**它是活的** —— P1（升级判断）

- **证据**：
  - BASE_ENERGY：`engine/core.js:14` = 3 vs `web/index.html:5375` = 4（T400 §2.4 记录 3→4 只改了 web）
  - value 归一化：`web/index.html:5860-5862` 有 2026-11-04 的 `const V = sp.value ?? sp.v` 修复（_FIX_20261104_special_value.md 记录），`engine/core.js` 的 applySpecial **没有**这段——core 副本里 strength/dexterity/regenerate/thorns/burn 全按默认值结算
  - **它是活的**：`tools/sim.js:7` `require('engine/core.js')`；node 实测 require 成功导出——模拟器、feel_check 等工具都跑在过期副本上
- **影响面**：所有基于 sim.js 的数值结论（BALANCE_T29 等）用的是「能量 3 + 特殊值按默认」的引擎，与实跑游戏（能量 4 + 正确 value）**不是同一个游戏**；本夜所有「玩家 DPS=15」口径按能量 4 算，与 sim 旧结论不可直接比。
- **严重度**：**P1**——不影响实跑玩家，但污染一切模拟/平衡结论；修复方式要么同步副本，要么让 sim 明确标注口径。

## 发现 5 · 「共鸣 / 共振」两个方言并存 —— P1

- **证据**：
  - 权威裁决：`docs/GLOSSARY.md:11`「唯一写法=共鸣（C.resonance）；禁用：共振值／回响值」
  - 运行时文案：`engine/core.js:307` / `web/index.html:5669` 玩家实际看到的日志是 `〔共振 10〕`；HUD tooltip（web:840）也写「共鸣」——**同一屏两个名字**
  - 体量：全库「共鸣」250 处 / 68 文件 vs 「共振」1289 处 / 168 文件（T444 实测）；内容表 cards_*.md 用共鸣（112 处），设计文档用共振
- **影响面**：玩家侧=卡面写共鸣、日志写共振（可见混乱）；开发侧=GLOSSARY 与 94 篇文档半数违宪；text_lint 永久误报。
- **严重度**：**P1**——玩家可见的术语分裂；修法方向已给（term_unify_plan.md U1：统一到共振代价最低）。

## 发现 6 · L2→L3 血量断崖 +70% —— P2

- **证据**：145 只敌人逐层平均血（区间中值）：L2=27.6 → L3=46.9（`enemy_power_curve.md` 逐层表，脚本输出 `data/audit/power_curve.txt`）；同期攻击 +0%。断崖叠加强制节点（L3 第 4 行必精英，RAW.layers rows）与 L3 dry 层规则（水脉回复 +1 费）。
- **影响面**：难度节奏——L3 是玩家 build 未成型期遭遇的最大数值跳变；`death_causes.md` 将 L3 判为最容易死层、`first_run_flow.md` 卡点 2 均由此而来。
- **严重度**：**P2**——不是 bug，是**难度曲线设计问题**；是否压平（如 L3 平均血降到 ~40）是设计者拍板项，本清单只报告曲线事实。

## 复核总结

| # | 发现 | 验证方式 | 严重度 |
|---|---|---|---|
| 1 | frail 死状态 | 全库 grep status.frail=4 处，无读点 | **P0** |
| 2 | resonance_gain 无 case | grep case=0，default 分支红字 | **P0** |
| 3 | u_0016 anmin_mark 生效但无描述 | 卡数据+引擎读取点+cardDesc 遍历范围 | P1 |
| 4 | core.js 过期且被 sim.js 引用 | BASE_ENERGY 两处对比 + require 实测 | P1 |
| 5 | 共鸣/共振方言 | GLOSSARY:11 vs 运行时 log + 全库计数 | P1 |
| 6 | L2→L3 +70% | 逐层均值表（可复算） | P2 |

修复动作见 `_BUGS.md`（G14）。
