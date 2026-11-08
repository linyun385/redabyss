# D12 · 术语与命名一致性

> 扫描范围：docs/*.md、docs/design/**/*.md、TASK_DONE.md、GLOSSARY.md、DESIGN.md、cards/*.json 的 flavor 字段。判定：同一概念出现 ≥2 种叫法 = 冲突。

## 冲突清单

| # | 概念 | 冲突 | 裁决建议 | 严重度 |
|---|---|---|---|---|
| 1 | 凝视 vs 共鸣 | 两套资源各有多种叫法 | 凝视（任务书/glossary）、被看的痕迹（叙事）、gaze（代码键）——gaze 统一，叙事层允许别名但 glossary 需立「凝视=唯一的玩家侧资源名」条目；共鸣（mechanisms.md 表头）vs 共振（引擎/glossary）——**冲突实锤**：glossary [GLOSSARY.md:11] 写「共鸣｜红光的回应（C.resonance）｜共振值／回响值」，但引擎变量是 resonance、任务书全用「共振」。裁决：统一为「共振」，mechanisms.md 表头的「共鸣」是 T320 时代遗留，重导出时修正。 | 高（glossary 是唯一写法来源，表头不一致=每个新文档都可能选错） |

| 2 | 黯民 vs 维护者 vs anmin | 同一职业三种叫法 | anmin=代码键、维护者=glossary 正名、黯民=部分文档（DLC_CANGMIN.md 用「黯民」指 cangmin？！）——实查：DLC_CANGMIN.md 的文件名说 cangmin 但内容指「黯民」，与 anmin 混淆。裁决：cangmin=苍民（glossary [GLOSSARY.md:15] 已立）、anmin=黯民（维护者）；DLC_CANGMIN.md 文件名是**历史错误**（内容讲的是苍民）——改名或加头注。 | 高（文件名误导检索） |

| 3 | 苍民 vs 疯先知 | 同职业双名 | glossary 用「苍民」作种族名、「疯先知」作职业名——两词并行不冲突（种族≠职业）但新文档常混用。裁决：glossary 立对照表行「苍民（种族）→ 疯先知（职业）」，新文档按职业名引用。 | 中 |

| 4 | 震语者 vs 深渊震语者 | 职业名与叙事名 | tremor=glossary「深渊震语者」——但 tasks/和引擎全用「震语者」。裁决：正文用「震语者」，glossary 补一行全称对照。 | 低 |

| 5 | 卡池 266 vs 267 | 数量不一致 | T320-T335 的设计文档写 266（不含 share_0001），T335/T330 写 267（含 shared）。实数：cards/*.json 共 267（shared 1）。裁决：统一 267（含 shared），旧文档加注。 | 中（数字分歧影响引用） |

| 6 | sell_concept 通用牌 vs 无色牌 vs share 牌 | 同一设计概念三种叫法 | T331 叫「通用牌」、任务书原话「通用的牌组」、代码叫 RAW.shared。裁决：文档统一「通用牌」，代码保持 shared（改名成本>收益）。 | 低 |

| 7 | 本层 vs 深度带 vs layer vs band | 同一空间概念四名 | 引擎 layer=带号（LAYERS 表）、T56 模块 band=节点深度带、UI 显示「第 X 层」。裁决：**保留双轨**——layer（引擎层，8 层规则）与 band（地图带，同值但来源不同）在数据上同值，文档统一用「层」，band 仅在地图代码语境使用。 | 中 |

## 决定记录

- 冲突 #2（DLC_CANGMIN.md 文件名）是本篇最大的发现：文件名与内容不一致的「历史错误」在全项目文档里可能不止一处——建议下一轮全文扫。
- 裁决原则：**代码键不改**（改名成本>收益）、**glossary 为唯一正名来源**（新文档查 glossary 而非抄旧文档）、**叙事别名允许但须在 glossary 有条目**。

## 扫描方法

本篇的扫描范围覆盖 docs/ 下全部 md 文件（含 design/、stream/、delivery/、lesson/ 子目录）与 cards/*.json 的 flavor 字段。判定流程：提取每个文件中出现的职业名/资源名/系统名词 → 同一概念的不同写法分组 → 与 GLOSSARY.md 的基准写法对照 → 不一致即记入冲突清单。

## glossary_check.md 的自我定位

本文件在 docs/design/ 根目录（而非子目录），因此会被 `python tools/check_design_refs.py --dir docs/design` 的默认检查范围覆盖——它与 T320-T324 一起验收。

## 裁决优先级

| 优先级 | 冲突 | 理由 |
|---|---|---|
| 高 | 共鸣 vs 共振（glossary 自身不一致） | glossary 是唯一写法来源，自身不一致=每个新文档都会传染 |
| 高 | DLC_CANGMIN.md 文件名误导 | 文件名含职业 id，检索时直接命中错误内容 |
| 中 | 266 vs 267 | 数字分歧影响所有引用「全池 X 张」的设计文档 |
| 中 | layer vs band | 引擎双轨不改，文档层统一 |
| 低 | 苍民 vs 疯先知 | glossary 已有对照，新文档查表即可 |
| 低 | 通用牌 vs 无色牌 vs shared | 设计概念统一为「通用牌」，代码不改 |

## 下一轮全文扫的方向

1. enemy 名字在 events/flavor 中的引用是否与 enemies/all.json 一致（专有名词拼写）
2. 卡面 mechanic 键在文档中的中文翻译是否统一（同一 special:code 是否有两种中文名）
3. 层名（地表死寂区等 8 个）在美术提示词中的使用是否与 layers/layers.json 的 name 字段一致

## 扫描实例：三份文档的同一概念对照

| 概念 | GLOSSARY.md | TASKS/T320 | tasks/QUEUE_20261104 | 裁决 |
|---|---|---|---|---|
| 凝视 | 无条目（需新增） | 凝视 | 凝视 | 统一「凝视」，glossary 补条目 |
| 共振 | 共鸣（[GLOSSARY.md:11]） | 共振 | 共振 | 统一「共振」，修正 glossary 表头 |
| 通用牌 | 无条目（需新增） | 未提及 | 通用牌 | glossary 补条目 |
| 维护者 | 维护者 | 维护者 | 维护者/黯民 | 维护者=正名，黯民=别名需 glossary 对照 |
| 苍民/疯先知 | 苍民+疯先知分立 | 疯先知 | 疯先知 | 按场合使用（种族/职业） |
| 震语者 | 深渊震语者 | 震语者 | 震语者 | 震语者=正名，深渊震语者=全称 |

## D12 与 glossary.md 的关系

D12（本篇）不改 glossary.md——它只发现冲突并给出裁决建议。改 glossary.md 是一个独立任务（需要逐条更新条目、重导出关联文档、确认 downstream 引用不破）。建议的执行顺序：① 白天裁决本篇的冲突清单 → ② 按裁决改 glossary.md → ③ 重跑 `node tools/_t46_wire.js` 同步 → ④ 重跑全部验收脚本确认不破。

## D12 的可重复性

本篇的扫描基于文本 grep（与 T270 的 rule_coverage.py 同一思路）——写一个 `tools/name_consistency.py` 脚本对 glossary.md 的正名列表做全文档交叉检查是下一步的工程化动作。本篇先手工完成第一轮，后续轮次可脚本化。
