# G14 · 待修 bug 清单（可执行版）

> 来源：_FINDINGS.md（G02）六项发现 + 两个同级的呈现缺陷。每条：问题 / 证据 / 影响 / **修法建议（只建议，本清单不改任何文件）** / 优先级。
> 排序原则：玩家可见的功能错误 > 口径污染 > 呈现缺陷 > 文档漂移。

## BUG-1 · frail（脆弱）施加后零结算 —— **P0**

- 问题：敌人被挂脆弱后，受击结算完全不读该状态。
- 证据：全库 `status.frail` 仅 4 处（core.js:497 施加/:675 递减；web:5866/:6047）——`dealToEnemy` 无读取点。
- 影响：dive_0022 / trem_0034 的脆弱挂件是假效果；玩家打了脆弱看不到任何变化。
- **修法建议（三选一，需拍板）**：
  1. `dealToEnemy` 加一行：`if (enemy.status.frail) dmg = Math.ceil(dmg * 1.5);`（尖塔语义：脆弱+50% 承伤）
  2. 换成有效状态（如易伤标记下回合伤害）
  3. 删两张卡的 frail 挂件（改卡数据，不走引擎）
- 优先级：**今天**（两行代码 + 一次 check_web 全绿）。

## BUG-2 · special 码 `resonance_gain` 无 case —— **P0**

- 问题：u_0009 的 `{code:"resonance_gain",value:3}` 落入 applySpecial default，每次打出红字警告且效果不生效。
- 证据：`grep "case 'resonance_gain'" → 0`；default 分支（core.js:515 附近）。
- 影响：u_0009 半边效果失效 + 每次打出弹报错式反馈。
- **修法建议（二选一）**：
  1. applySpecial 补 case：`case 'resonance_gain': C.resonance += (V !== undefined ? V : 3); break;`（web 与 core 两处同步）
  2. 改卡数据：把该 special 移到 effect 键 `resonance_gain: 3`（键路径已实现，改动最小）
- 优先级：**今天**（推荐方案 2——只动 cards/shared.json 一个文件，无引擎同步负担）。注意：改 cards/*.json 需按项目规矩走备份流程。

## BUG-3 · engine/core.js 过期，且 sim/test 跑在它上面 —— **P1（口径污染）**

- 问题：core=能量 3+旧 applySpecial；web=能量 4+value 归一化。10 个工具（sim.js/test_engine.js/econ_sim.js 等）require core。
- 证据：engine_diff.md（函数级 MD5 对比：36 同 5 分歧）+ `tools/sim.js:7` + node require 实测。
- 影响：所有 sim/平衡历史结论与实跑游戏不同参；未来任何模拟继续产出错口径数据。
- **修法建议（两步）**：
  1. 立即：core.js 两处同步（`BASE_ENERGY = 4`；applySpecial 补 value 归一化段——从 web:5860-5862 拷贝）
  2. 结构性：写 `tools/sync_engine.js`（core.js → web 内联区段的单向生成器）或在 check_web.js 里加「两副本 hash 对比」断言，防再漂移
- 优先级：**今天**（第一步十分钟；第二步半天）。

## BUG-4 · 共鸣/共振方言并存（玩家可见） —— **P1**

- 问题：GLOSSARY:11 正名「共鸣」，但运行时日志（core.js:307/web:5669）与设计文档（1289 处）全用「共振」；卡面（cards_*.md 112 处）用「共鸣」——玩家同屏见两名。
- 证据：term_audit.md（实测计数）/ _TERMS_MERGED.md（终表）。
- 影响：玩家困惑 + text_lint 永久误报 + 新文档无所适从。
- **修法建议**：拍板「统一到共振」→ ① GLOSSARY:11 改裁决 ② cards_*.md 112 行批量替换 ③ term_unify_plan U1 有完整清单。反向方案代价 ×6，不推荐。
- 优先级：**拍板即可执行**（半天内含回归检查）。

## BUG-5 · u_0016 生效但卡面零描述 —— **P1（呈现）**

- 问题：effect 字段空 → cardDesc 无文本；anmin_mark 激活 purge 的功能玩家不可见。
- 证据：dead_card_check.md 更正版；web:5754 activateProtocol。
- 影响：rare 位卡打出去「什么都没发生」的体感 + purge 全程无状态显示。
- **修法建议**：给 u_0016 补 effect 层展示（cardDesc 特判 anmin_mark，或 effect 加一个展示用键）；激活时补一条 log「清剿协议运行中：你每回合 −2，它们攻击 +3」（与 T451 #8 同一条）。
- 优先级：**本周**（与 T451 引导补丁同批）。

## BUG-6 · anevent_06 选项文本与数值脱节 —— **P1（信任）**

- 问题：「追查消耗去向」扣 4 血，result_text 却写「门是温的，你没有推」——代价来源不明。
- 证据：event_rewrite.md §6；RAW events。
- 影响：玩家对事件系统的信任损耗（以为是 bug）。
- **修法建议**：改 result_text 让 4 血有着落（「门后扫过来的热浪」类），或把 damage 挪到有代价暗示的另一选项。
- 优先级：**本周**（改一行事件文本，走事件文案流程）。

## BUG-7 · 连携 onceHint 规划未实装 —— **P2**

- 问题：D11 规划的 `onceHint('chain', ...)` 与 `onceHint('gaze_cost', ...)` 不在代码里。
- 证据：tutorial_gaps.md（onceHint 现役清单 grep）。
- 影响：脉系统的核心机制（连携）无引导。
- **修法建议**：按 D11 原案插两行（落点 index.html:6987 / :7589 附近）。
- 优先级：**本周**（与 BUG-5 同批，都是两行）。

## BUG-8 · 旧文档失效引用（≥20 文档 / 58+ 失效 id） —— **P2（文档债）**

- 问题：剪枝与 T400 定稿后旧文档零回写；ART_MAP/T321 等大量引用已删卡。
- 证据：_CONFLICTS.md B1-B6；data/audit/stale_ids.txt。
- 影响：误导任何按文档工作的人（包括未来的自己）。
- **修法建议**：两选一——① 给 6 篇高影响文档加头注（半小时）；② 建立事实单源（all_numbers.md 扩为唯一数字引用）+ 头注双管齐下。
- 优先级：**本周**（不做会持续产生新的引用错误）。

## 执行顺序建议

```
今天：  BUG-1（2 行）→ BUG-2（1 行/改 1 文件）→ BUG-3 第一步（2 处同步）
本周：  BUG-4（拍板后半天）→ BUG-5+7（同批 4 行）→ BUG-6（1 行文本）→ BUG-8（头注）
结构性：BUG-3 第二步（sync_engine 或 hash 断言）
```

全部为**建议**——本清单不改任何文件；修复时按项目规矩（备份/两副本同步/check_web 全绿）执行。
