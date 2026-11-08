# docs/design 全量索引（机械摘要 + 权威地图）

> 2026-11-06 夜班 · 兜底任务 3。**摘要为脚本机械抽取**（每个 md 的首个标题 + 首个正文行截 70 字），不是逐篇精读——机械摘要失真的，以文件本体为准。
> 由 `tools/_design_index_1106.py` 生成，可重跑刷新。共 362 个 md。

## 权威文件地图（手工维护，先看这里）

| 要查什么 | 去哪 | 备注 |
|---|---|---|
| 世界观名词（生物/族群） | glossary.json（仓库根） | 自述「所有命名从这里取」 |
| 五脉判据 | docs/design/vein_flavor_card.md | 提炼自 T400_master §2.1 |
| 引擎行为基准（能量/手牌/结局分档等） | docs/design/all_numbers.md + engine_diff.md | 含 web 与 core.js 双副本差异 |
| 规则机制总览 | docs/design/T323_RULES.md | 注意：引 core.js 行号，core.js 是过期副本（见 _CONFLICTS_1106 第 5 条） |
| 维护者核心卡实测 | docs/design/_VERIFY_anmin_core_cards.md | 45 项实测 + 自作主张三处待确认 |
| 附属卡设计（2026-11-06 夜班） | docs/design/anmin_minions/00_README.md | 8 文件入口 |
| 敌人全量 roster 与战斗台词 | docs/design/enemies/_roster_full.tmp.md + battle_lines.md | 113 只 |
| 数值曲线 | docs/design/curves/curve_report.md + parts_economy.md | 脚本 tools/_curve_audit_1106.py、tools/_parts_economy_1106.py |
| 音效钩子 | docs/audio/SFX_LIST.md（docs 根，不在 design/ 下） | 19 钩子 + 8 氛围 |
| 术语一致性 | docs/design/glossary_audit.md | 15 条 + 排除项 |
| 矛盾追踪（本夜班版） | docs/design/_CONFLICTS_1106.md | 旧账见 _CONFLICTS.md / old_doc_conflicts.md |
| 引导文案 | docs/design/tutorial/first_3_battles.md |  |
| 结局文本 | docs/design/endings/ten_endings.md |  |
| 商店/回收文案 | docs/design/shops/shop_and_recycle.md |  |
| 卡面文案审查 | docs/design/copy/flavor_audit.md + name_audit.md | 40 条 flavor + 11 条名字 |

## 全量文件（机械摘要）
- `CARD_EFFECTS_AUTO.md` — 全卡池效果总表（自动生成）：读法：费 = 能量消耗；〔〕 里是数据和引擎对不上的地方（真 bug，不是笔误）。
- `CONFLICTS.md` — CONFLICTS · 设计文档矛盾清单：文档  结论
- `DESIGN_TODO.md` — 设计待办（非 GLM 任务，DSH 会话与用户的账）：---
- `DUP_VS_SHARED.md` — 通用牌 × 职业专属牌 查重对照：两种撞法：
- `T320_MECHANISMS.md` — T320 · 机制骨架分析
- `T321_REDUNDANCY.md` — T321 · 冗余诊断：换了名字的同一张牌
- `T322_MONOTONY.md` — T322 · 单调性诊断与方向建议：全池 267 张卡的效果由 12 个顶层键（block/damage/hits/draw/resonance_gain/heal/gaze_
- `T323_RULES.md` — T323 · 规则说明书（从代码提取）：#  规则  代码位置
- `T324_GAPS.md` — T324 · 设计空白清单：内容都在，但没有被连起来：机制在职业间的分布极度偏斜（T320 已证通用语言只有 7 种），以下机制是事实上的单职业财产，但它们每一个都能在别的职业找到宿主叙事：
- `_BUGS.md` — G14 · 待修 bug 清单（可执行版）：- 问题：敌人被挂脆弱后，受击结算完全不读该状态。
- `_CONCLUSIONS.md` — G07 · 百条结论清单（按重要性排序）：1. 脆弱（frail）是死状态：全引擎只有施加与递减两处，dealToEnemy 从不读它——两张卡的白挂件。（dead_card_che
- `_CONFIDENCE_A.md` — K02 · A 级结论一页纸（设计师可直接用）：结论  数字
- `_CONFLICTS.md` — F1 · 全局文档矛盾扫描（_CONFLICTS）：#  概念  A 处  B 处  哪个对
- `_CONFLICTS_1106.md` — 矛盾清单 · 2026-11-06 夜班第二轮：---
- `_DEPTH_AUDIT.md` — G15 · 文档深度统计（112 篇）：- 篇数 114；字数中位 2247、均值 4066、最短 485、最长 56265。
- `_DOC_CONFLICTS.md` — G08 · 新产出互相矛盾交叉检查（94 篇内部）：#  A  B  矛盾点  裁定
- `_DOC_STRUCTURE.md` — G12 · 文档目录整理建议（只给方案，不移动文件）：docs/design/
- `_FINDINGS.md` — G02 · 本夜六项关键发现复核（证据 / 影响面 / 严重度）：- 证据：
- `_FIX_20261104_special_value.md` — 引擎修复记录 · 2026-11-04 · special 字段名不一致：用户玩的时候察觉到「有些牌的效果数字不对」，追查确认是 bug，用户拍板改引擎。
- `_FIX_REWARD_RATE.md` — I01 · 主脉率为什么只有 41%——参数敏感度扫描：情形  主脉率  10/90 分位  达标（≥45%）？
- `_HY4_Y1_sync.md` — HY4 · Y1 数据一致性：cards/anmin.json ↔ RAW.anmin：完全一致。差异清单为空。
- `_HY4_Y2_parts_economy.md` — HY4 · Y2 零件经济核算：变量  值  出处
- `_HY4_Y3_codes.md` — HY4 · Y3 新 special code 使用率审计：项  值
- `_HY4_Y4_carddesc.md` — HY4 · Y4 卡面描述映射完整性
- `_HY4_Y5_class_shape.md` — HY4 · Y5 黯民 54 张卡的结构分布：维度  黯民  下潜者  震语者  苍民
- `_HY4_Y7_regression.md` — HY4 · Y7 回归：公共路径五条：项  结果
- `_INDEX_NIGHT.md` — G01 · 夜班总索引（100 篇导航）：文件  内容  回答什么问题  任务号
- `_NIGHT_REPORT_1104.md` — 夜班报告（2026-11-03 23:00 → 11-04 04:52）：---
- `_PROGRESS.md` — T320–T324 设计包 · 夜班收尾：---
- `_READ_FIRST.md` — G13 · 明天先看的 10 篇（按「设计师明早最该先看」排序）：#  文件  为什么排这个位置  看完能做的决定
- `_RELIC_RECALC.md` — K01 · 遗物价值重算（修复后模拟器 + mod 计分口径）
- `_RELIC_TRIAGE.md` — I02 · 94 件「亏」遗物分诊（A 设计使然 / B 被低估 / C 真的废）：类  件数  占 94 的
- `_SIM_BUGFAMILY.md` — J01 · 模拟器 bug 家族全面排查：#  bug  位置（修复前）  类别  影响的结论  状态
- `_SIM_BUGFAMILY_CROSS.md` — K03 · J01 自查的交叉验证（人工读代码 vs 实际跑）：#  脚本  人工读码的预言  实跑验证  判定
- `_SIM_CONFIDENCE.md` — J03 · 模拟结论置信度分级（A / B / C）：结论  数字  依据链
- `_SIM_RECALC.md` — J02 · 所有 sim 结论重新验算（修复后全量重跑对账）：数字  污染期旧值  修复后文档现值  本次复跑  判定
- `_SIM_REPORT.md` — H15 · 模拟总报告（H01–H14 汇总）
- `_SIM_SELFCHECK.md` — I03 · 模拟脚本自检（可复现性 / 硬编码 / 除零）：剥离计时行（0.0s/0.1s 来自 run_all 的耗时打印，与模拟无关）后，两次输出逐行一致：
- `_SIM_TABLES.md` — I04 · 模拟结果六张表（纯整理，不重跑）：指标  值
- `_TASKDONE_AUDIT_1106.md` — TASK_DONE 产出存在性审计（自动生成，勿手改）：项  数
- `_TERMS_MERGED.md` — G11 · 术语三合一终版表：词  现状叫法  建议统一成  影响面  玩家推得出？
- `_THIN_DOCS_AUDIT.md` — F9 · 薄弱文档审计（结论：短 ≠ 薄弱，扩写会破坏文档）
- `_TLDR.md` — K04 · 30 秒速览（今晚 7 批、150+ 篇产出的结论级总结）：模拟器搭好了也修干净了（A 级结论可直接引用）；静态盘点确认卡池「结构性重复多、供给薄位集中」；三个 P0 引擎 bug 和三个数值拍板项在
- `_TOP3_TUNING.md` — I05 · 三个最该调的数值（综合全部模拟）：- 现状：可达水牌仅 3 张（dive_0037/0038 + u_0011）——占下潜者可抓池 4.4%。
- `_VERIFY_NIGHT.md` — 夜班验收记录（2026-11-04 01:05）：python tools/check_design_refs.py --dir docs/design 与 --dir docs/desig
- `_VERIFY_anmin_core_cards.md` — 维护者核心卡 · 落地与实测记录：---
- `_WATER_SLOW.md` — I06 · 水脉为什么「60 场才成型」——答案：它不是：层  bug  效果
- `all_numbers.md` — T514 · 游戏内数字全清单：项  数值  来源
- `anmin_core_cards_review.md` — 维护者核心卡 · 核对结果与落地状态
- `attack_rate.md` — T531 · 敌人攻击频率（每回合期望承伤）：层  档  只数  攻击回合占比均值  平均单发  期望承伤/回合
- `bad_event_options.md` — D2 · 事件的明显坏选择（同事件被兄弟选项支配）：事件  池  被支配选项  收益/代价  压过它的选项  后者收益/代价  为什么玩家不会选
- `banned_word_scan.md` — T445 · 卡面文案禁词扫描：零命中：扫描 219 张卡 × flavor/cost_text/flavor_add 共 475 个字段，禁词表 6 个词全部零命中。
- `card_intent_reverse.md` — T500 · 每张卡的设计意图反推
- `card_naming_guide.md` — T414 · 卡牌命名风格指南：模式  张数  说明
- `card_quickref.md` — F11 · 读卡速查（每条 ≤30 字）：- dive_0001 光导透镜（残）：抽1张牌
- `card_readability.md` — T508 · 卡面描述可读性分级：档  张数  占比
- `class_pick_hint.md` — T449 · 四角色选择界面提示：- 选择提示：公司的设备一件件发给你。先学会站住。（18 字）
- `combat_pace.md` — D11 · 战斗节奏粗估（4 能量 / 平均费 1.09）
- `dead_card_check.md` — T447 · 空转卡检查（效果可能是空的卡）
- `death_causes.md` — T528 · 每层「死法」清单（结合敌人数据推演）：- 怎么死：只有一种可能——把「辐射弹（未爆）」（上限 −6 遗物）当纪念品拿着再挨几刀。敌人攻击 1~3，血 8~13。
- `decision_points.md` — T506 · 每回合决策点数量（4 能量 / 抽 5 张粗估）：角色  手牌类别数 A  可打张数 B  资源决策数 C  决策广度 D=A+C  判定
- `deck_size.md` — T529 · 卡组厚度分析（一局会多肥，删不动删不删）
- `enemy_avoid.md` — T510 · 敌人里的「必躲」：id  名字  层  池  血量  平均攻击  期望回合  期望承伤  为什么躲
- `enemy_card_map.md` — T501 · 敌人 ↔ 卡牌对应（每只敌人在考什么、罚什么）：id  名字  等级  池  血量  主考验（罚什么）  附加  该带的牌
- `enemy_layer_fit.md` — G04 · 敌人与层的匹配度审查：层  主题匹配  数值适配  机制联动  判定
- `enemy_lore_night.md` — W2 · 敌人描述（夜班版 · 闭眼听）：- 嗜热古菌（普通）：轻得像在试探。空管里的嗡鸣，一下轻一下。偶尔停下来 hardened。节奏 3 拍。
- `enemy_lore_rewrite.md` — F4 · 敌人描述文案提案（145 只逐只，≤60 字）：- 嗜热古菌（通用池，普通）：攻击 2、2；会防御。循环 3 拍。
- `enemy_naming_guide.md` — D13 · 敌人命名风格指南：式  数量  例子
- `enemy_power_curve.md` — T453 · 敌人强度曲线：层  只数  平均血量  最高单发攻击  期望回合数  血量增速  攻击增速  回合增速
- `enemy_table.md` — T440 · 敌人全表：id  名字  等级  池  血量  攻击值  意图序列  垫底机制
- `engine_diff.md` — G05 · 引擎双副本差异全清单（engine/core.js vs web/index.html 内联副本）：项  值
- `event_density.md` — T512 · 每层事件密度：层  层名  行数  事件行  商店行  精发行  期望事件数  期望商店数  几个节点遇一次事件
- `event_info.md` — T505 · 事件结果的信息量（选之前能看出多少）：事件  池  选项  选项原文  档  证据  result
- `event_rewrite.md` — F5 · 事件文案重写提案（10 个事件，选项文本带结果信号）：---
- `event_rewrite_night.md` — W3 · 事件选项改写（夜班版 · 60 个）：事件  选项  原文  改写  信号
- `event_rr.md` — T524 · 事件风险收益比表：事件  池  选项  原文  收益  损失  净值
- `event_table.md` — T441 · 事件全表：id  层  标题  选项数  选项明细（veins 标签 → 结果）
- `event_vein_link.md` — D9 · 事件与脉的关联度：层  光  水  热  震  矿
- `experience_map.md` — G06 · 玩家体验地图（开局 → 终局全时间线）：里程碑  内容  来源锚点
- `first_5min.md` — T521 · 四角色开局 5 分钟体验脚本：---
- `first_impression.md` — F12 · 每张卡的「第一印象」测试：- 可判定名 96 张：相符 75（78%），猜错 21。
- `first_run_flow.md` — T507 · 第一局前 3 层完整推演
- `flavor_rewrite.md` — F3 · 卡牌风味文本重写提案（30 张）
- `game_terms.md` — D12 · 游戏内专有名词表（按玩家接触顺序）：序  玩家在何时撞到  词  有没有解释  缺口
- `game_terms_full.md` — F10 · 游戏内专有名词全表（玩家视角）：词  首次出现  游戏内解释  要推吗  推得出来吗
- `glossary_audit.md` — 术语一致性审计 · 15 条：---
- `glossary_check.md` — D12 · 术语与命名一致性：#  概念  冲突  裁决建议  严重度
- `healing_check.md` — T527 · 恢复机制检查（一局能回多少血，够不够）：id  角色  名字  回血
- `hints_night.md` — W9 · 引导点清单（夜班版）：#  懵的时刻  玩家在想  建议提示  落点
- `inspiration_log.md` — F8 · 设计溯源记录（防撞参考用，只记录不评判）：#  项  哪里像  哪里不同
- `intent_coverage.md` — D8 · 敌人意图覆盖检查：意图种类数  只数
- `intent_predictability.md` — T522 · 敌人意图可预测性：体感档  只数
- `keyword_frequency.md` — D5 · 卡牌关键词频次表：键  次数  备注
- `layer_composition.md` — D3 · 每层敌人构成分析：层  总数  普通/精英/boss  池构成
- `layer_literary.md` — F7 · 逐层文学分析（纯文学角度）：- 语域：全套官僚文书腔——对答、编号、清单、坠轨清单、五百年水箱、坠轨的清单「签收人那栏都是空的」。敌人名是物件名（空服的壳、晒裂的软管、
- `layer_literary_night.md` — W5 · 逐层文学分析（夜班版 · 深化）：层  密度  沉默方式  称呼转换  层内互文
- `layer_rules.md` — T443 · 层规则全表（引擎实现逐条对账）
- `layer_theme.md` — T502 · 每层主题一致性：层  层名  eco
- `least_picked_20.md` — T523 · 卡池里最没人拿的 20 张（逻辑推断）：#  卡  池  被谁占优  推理
- `natural_combos.md` — T513 · 卡牌之间的自然组合（不靠核心卡）：#  组合  需要的牌  强度  容易凑吗
- `newbie_mistakes.md` — T534 · 新手会犯的 10 个错误（推演）：- 为什么：零件计数器藏在 HUD 角落，功能只在悬停 title 里（web/index.html:843）；维护者的成长路径完全不在卡组
- `numeric_outliers.md` — T446 · 数值离群扫描：id  名字  角色  桶（类型/稀有度/费）  主种类  数值  同类中位数  偏离
- `old_doc_conflicts.md` — T450 · 旧文档与新定义冲突清单（§2.1 五脉 + §2.2 角色 + 整局永久）：T415 编号  一句话  位置
- `orphan_cards.md` — D10 · 孤儿卡清单：- share_0001 强行供能（通用）：无任何钩子——effect={"special": {"code": "rule_bypass"
- `pace_night.md` — W8 · 战斗节奏逐层细化（夜班版 · 节奏谱）：回合  敌人意图  玩家动作  能量分配  掉血
- `player_timeline_night.md` — W6 · 玩家体验时间线（夜班版 · 逐层逐节点）：- 会看到：12 张初始卡、5 张手牌、第一张意图列表
- `playtime_estimate.md` — T533 · 游戏时长估算（熟练 / 新手两档）：环节  数量  熟练（秒/次）  新手（秒/次）  熟练合计  新手合计
- `pool_3d.md` — T511 · 卡池三维分布（费用 × 类型 × 稀有度）：费用  类型  普通  精良  稀有  合计
- `pool_thickness.md` — D14 · 卡池厚度体检（按角色 × 类型 × 稀有度 × 费用）：费  类型  普通  精良  稀有  特殊  合计
- `rarity_dist.md` — T504 · 稀有度分布合理性：角色  普通  精良  稀有  特殊  合计
- `redesign_clusters.md` — G09 · 重设计建议聚类（T520 的 219 条 → 根因群）：群  张数  典型例子  共同根因
- `redesign_notes.md` — T520 · 每张卡「如果重设计」的建议：- dive_0022 硬矿钻（重型）（下潜者）：挂的脆弱（frail）引擎从不结算（dealToEnemy 不读 status.frail
- `relic_lore.md` — F6 · 遗物文案审计与来历补写提案
- `relic_lore_night.md` — W4 · 遗物来历（夜班版 · 107 件）：- relic_01 上一任的矿牌（普通）：来历没有记载。但它的磨损方式说明它被某种手握了很长时间——手的形状决定了它现在的样子。
- `relic_mustpick.md` — T509 · 遗物里的「必拿」：入选线：无副作用 ∧ 自动触发 ∧ 主收益比同稀有度同动作中位数 高 ≥1（或该动作在同稀有度里 ≤2 件，属稀缺位）。
- `relic_table.md` — T442 · 遗物全表：id  名字  稀有度  来源  效果  偏向
- `relic_tier.md` — T525 · 遗物强度分级（S/A/B/C）：档  件数
- `relic_vein_fit.md` — D4 · 遗物与流派的匹配度：id  名字  池  直接支持  间接支持  无关？
- `resource_curve.md` — T532 · 资源曲线（金币 / 零件 / 凝视 / 共振，逐层收支）
- `round2_night.md` — W 池第二轮（换角度）· 全 10 篇合一：---
- `scatter_plan.md` — D7 · 「散牌局」预案（什么体系都没成型时，玩家靠什么撑）
- `shared_pool_audit.md` — T416 · 通用池 11 张逐张审查
- `sim_build_speed.md` — H04 · 卡组成型速度（拿牌通道，目标 5 张同脉）
- `sim_combat.md` — H02 · 战斗回合数与生存模拟
- `sim_combo_damage.md` — H08 · 常见组合期望伤害（单回合，4 能量）：排名  组合  来源  费用和  同回合？  单回合伤害  灼烧附加
- `sim_decision_load.md` — H10 · 决策负担量化（每回合要比较几个选择）：角色  可行子集数中位  均值  10/90 分位  资源决策/回合  合成决策广度
- `sim_economy.md` — H03 · 一局资源流模拟（1000 局，seed=42）
- `sim_event_value.md` — H06 · 事件期望收益（价值分模型）：事件  选项  文本  收益  损失  净值
- `sim_full_run.md` — H14 · 整局抽卡序列模拟（200 局）
- `sim_relic_value.md` — H07 · 遗物长期收益与性价比（20 场累计）：性价比（收益金当量/价格中位）  件数
- `sim_reward.md` — H01 · 抽卡加权蒙特卡洛（奖励三选一）
- `sim_sensitivity.md` — H05 · 数值敏感度（敌人血量/攻击 ±10/20%）：情形  平均回合  Δ回合  期望承伤  Δ承伤
- `sim_starter_survival.md` — H11 · 初始卡组生存推演（真回合制微模拟）：角色  L1 回合  L1 掉血  L2 回合  L2 掉血  L3 回合  L3 掉血  80/72/76/30 血能连打几场（L3）
- `sim_tuning_suggestions.md` — H13 · 反推数值调整建议（基于 H01–H11 模拟结果）：- 现状：主脉出现率 41.1%（H01，1000 玩家×20 场，10/90 分位 36.7~46.7%）。
- `sim_vein_level.md` — H09 · 脉象等级成长模拟（T526 规则 + 事件随机性）
- `special_mech_dist.md` — T503 · lock / 凝视 / 共振 三种特殊机制的使用分布：- lock（本层一次）：9 张卡用到（去重 id 数 9）；按角色：下潜者 5、维护者 1、震语者 3
- `starter_deck_analysis.md` — T452 · 四角色初始卡组分析：角色  张数  费用曲线  脉分布  4 能量平均出牌  牌组明细
- `term_audit.md` — T444 · 术语一致性核对：概念  GLOSSARY 正名  实际高频词  正名出现  高频词出现  状态
- `term_exec_night.md` — W10 · 术语统一执行单（等用户拍板才执行）：文件：docs/GLOSSARY.md
- `term_unify_plan.md` — F2 · 术语统一建议书（基于 T444，只给方案不执行）：#  概念  现状  建议统一成  影响面  改动清单  代价评估
- `text_length.md` — D6 · 卡面文字长度分布：档  张数  占比
- `thin_directions_night.md` — W7 · 卡池薄位补牌方向（第一轮）：- 方向 1：给震语者和疯先知各补一张 0 费攻击（普通档），费用 0/伤 3~5——对标 dive_0013 硬矿钻
- `thin_spots_merged.md` — G10 · 薄位合并视图（「卡池的洞」总表）：#  洞  证据  来源
- `tutorial_gaps.md` — T451 · 引导缺口清单（没有任何文字解释的机制）：- 现状：HUD title「零件：黯民的回收货币，用于改造与拆解」+ 计数器可点击（title「点击打开回收面板」，:843）。但都只在悬
- `upgrade_coverage.md` — T530 · 升级覆盖率：项  数值
- `vein_audit_matrix.md` — T401 · 全卡脉象矩阵：id  职业  名字  脉  类型  费  稀有度  效果一句话  与谁重复
- `vein_cost_curve.md` — T407 · 每条脉的费用曲线：脉  0 费  1 费  2 费  3+ 费  合计  平均费
- `vein_curve.md` — T526 · 脉象等级成长曲线建议：层  期望事件数  层规则
- `vein_doc_conflicts.md` — T415 · 旧文档与 §2.1 新定义冲突清单
- `vein_dup_review.md` — T409 · 近似撞人工复核（dup_check.py 报的 21 条）：对手  差  判定  理由
- `vein_effects_by_vein.md` — T410 · 每脉效果全集：---
- `vein_flavor_card.md` — T405 · 五脉速查卡：---
- `vein_no_vein_advice.md` — T408 · 无脉牌归属建议：id  名字  角色  效果  建议  理由一句
- `vein_positive_examples.md` — T413 · 每脉正例样本库：id  名字  效果  为什么是正例
- `vein_special_mech_cards.md` — T411 · 特殊机制卡清单（lock / gaze / resonance）：id  名字  角色  数值
- `vein_tag_review.md` — G03 · 脉归属合理性复审（219 张三档）：档  张数
- `vein_writing_card.md` — T448 · 五脉写卡速查卡（写卡时放在旁边）：- 该长：无条件高效；直接改自己数值（力量/格挡/上限）

### anmin_minions

- `00_README.md` — T-ANM · 维护者附属卡设计 · 总览：---
- `01_audit.md` — 01 · 黯民现有卡池逐张判定：---
- `02_cards_A_growth.md` — 02 · 支柱 A · 局外成长（8 张）
- `03_cards_B_buffs.md` — 03 · 支柱 B · 自身加成（8 张）：对照旧卡（含判定保留的 20 张）：力量有 0015、敏捷有 0016、再生有 0040、格挡有 0004/0010/0017/0024——
- `04_cards_C_parts.md` — 04 · 支柱 C · 零件经济（8 张）
- `05_curves.md` — 05 · 零件经济曲线：收入 / 支出 / 汇率：---
- `06_needs.md` — 06 · 需要新引擎能力的东西：---

### classes

- `opening.md` — 四职业的开局体验：---

### combo

- `D8_COMBOS.md` — D8 · 卡牌组合技（20 组，含 2 组反例）：项  内容

### copy

- `_flavor_dump.tmp.md` — _flavor_dump.tmp.md：== diver (57) ==
- `flavor_audit.md` — 卡面 flavor 去 AI 味审查 · 40 条
- `name_audit.md` — 卡牌名字 AI 味审查：---

### copy2

- `T340_D4_subtitles.md` — D4-a · 新卡副标题与卡面 flavor（20 张）：#  暂名  职业  副标题  flavor

### curves

- `_triage.tmp.md` — _triage.tmp.md：== 绿 (22) ==
- `curve_report.md` — 卡牌数值曲线 · 分析报告：---
- `curve_report_auto.md` — 卡牌数值曲线 · 脚本产出（自动生成，勿手改）：档  伤害卡数  伤中位数  伤/能量中位  格挡卡数  挡中位数  挡/能量中位
- `parts_economy.md` — 零件经济曲线 · 蒙特卡洛模拟分析（第二轮）：---
- `parts_economy_auto.md` — 零件经济 · 蒙特卡洛模拟产出（自动生成，勿手改）

### death

- `D10_DEATH.md` — D10 · 失败与死亡设计：步  行为  行号

### delivery

- `T340_DELETE_OPS.md` — T340 · 删卡施工单（58 条逐条可执行）：步  动作  之后跑什么  通过标准
- `T341_UNIVERSAL_JSON.md` — T341 · 通用牌数据草案（可直接贴进 cards/shared.json）：全池 267 张字段普查：id/name/class/type/rarity/veins/energy/effect/cost_type/c
- `T342_WEAK_PATHS.md` — T342 · 弱流派补牌清单（14 条逐条裁决）：项  内容
- `T343_ACCEPTANCE.md` — T343 · 验收单（写给不是程序员的人：照着核，每条都说清在哪、找什么、看到什么算对）：#  搜什么  在哪个文件  通过标准

### ending

- `D9_ENDINGS_NG.md` — D9 · 结局与多周目：项  内容

### endings

- `ten_endings.md` — 结局扩充 · 10 个新结局：---

### enemies

- `L1_L3_rework.md` — L1–L3 敌人重做：把「倒吊」写进前三层：---
- `L4_L8.md` — L4–L8 敌人：更亮、更红、更少眼睛：---
- `_roster_full.tmp.md` — _roster_full.tmp.md：enemy_d1_01嗜热古菌norm它们贴在余温上。管道凉了三十年，它们还在等。
- `battle_lines.md` — 敌人战斗台词 · 全量 113 只（攻击 / 受击 / 死亡 各一句）：---

### enemy

- `D6_THIRTY_SIX.md` — D6 · 敌人行为设计（36 个新敌人，按层分布）：项  内容

### event

- `D7_EVENT_BRANCHES.md` — D7 · 事件分支扩展（16 个代表事件 × 1-2 分支）：现有选项：

### events

- `new_events_20.md` — 事件池扩充 · 20 个新事件：---

### guides

- `anmin_onepage.md` — 维护者（黯民）单页攻略：一句话爽点：把别人当垃圾的东西拆成零件，再拿零件把自己改成一台越打越狠的机器（0051 机械增生 / 0054 武器试验 / 0057 更新

### layers

- `scene_depth1.md` — 第一层 · 地表死寂区：光从脚下来。这是全世界唯一一个光的方向不需要适应的地方——它太弱了，弱到只是岩缝里的一线暗红，像有人在地底深处划了一根很久没熄的火柴。
- `scene_depth2.md` — 第二层 · 外层冷洞：下去的第一件事是发现呼出的气白了。冷洞的冷不是旷野那种冷，是洞的冷——空气从洞壁里渗出来，渗一层，冷一层。岩壁上凝着薄霜，霜的下面是活的：青
- `scene_depth3.md` — 第三层 · 干旱空洞区：这一层的空气是粉的。不是雾——是磨碎的岩粉悬浮在空气里，红光从地核方向斜着穿上来，穿过粉尘，把整个洞照成一种旧照片的颜色。光有角度：它不从窗
- `scene_depth4.md` — 第四层 · 稳定空洞海：下到最后一段竖井，脚下忽然没有石头了。
- `scene_depth5.md` — 第五层 · 热泉裂带：热是看得见的。这一层的空气自己会流动——从每一道地缝、每一个泉眼里往上顶，把硫雾顶成一根根半透明的柱子，柱子不散，笔直地上去，撞到洞顶才摊成
- `scene_depth6.md` — 第六层 · 辐射矿石区：这一层的红不用光描述。矿石自己红——晶簇从巷道的壁和顶上长出来，红的、暗红的、红得发黑的，每一簇都在缓慢地吐着自己的光。你手上的计量器一直在
- `scene_depth7.md` — 第七层 · 核心高热区：这一层没有巷道了。矿道到这里就断了，断口整齐得像按图纸断的——往下的路全是从岩层里烧出来的空腔，一个接一个，腔和腔之间只有短的、烧斜的连接段
- `scene_depth8.md` — 第八层 · 红渊核心：最后一层的入口是一段隧道，走过去之后，脚下的岩层没有了。
- `sound_design.md` — 八层声音设计：---

### lore2

- `D4_illustrated_entries.md` — D4-b · 新卡图鉴三段（20 张）：副标题：把说出去的话刻在墙上，墙替你记着——你要的那一句，它会还。

### master

- `00_INDEX.md` — 00_INDEX · 总索引（95 篇）：路径  一句话结论  字数  可信度  标记
- `01_CARDS.md` — 01_CARDS · 卡池怎么改：删 58 张（T335 清单）→ 贴 17 张通用牌草案（T341，10 张零引擎改动 + 7 张需改引擎）→ 加 D2 的 19 张补牌（
- `02_STREAMS.md` — 02_STREAMS · 流派与职业：10 条弱路有明确补法（通用牌 + 职业牌），4 条「弱但有趣」是设计价值的核心载体，2 条不可行正式结案。通用牌的三种三卡组合原型（无脉生
- `03_ENGINE.md` — 03_ENGINE · 引擎要改什么：6 处引擎改动，其中 1 处是全盘成败前提（双脉连携 engine/core.js:429），2 处极小（一行），2 处小，1 处中。全部改
- `04_CONTENT.md` — 04_CONTENT · 内容与叙事：八层世界观按「倒吊+红光」双弧线推演完成（D5）；36 个新敌人按引擎意图类型设计完成（D6）；16 个事件加了分支（D7）；四结局+多周目
- `05_TERMS.md` — 05_TERMS · 术语与命名裁决：7 条冲突全部有执行方案，全部不碰代码。最高优先：「共鸣→共振」（glossary 自身不一致，203 处别名出现）。最低优先：「震语者全称
- `06_RISKS.md` — 06_RISKS · 风险与已知坑：9 条设计文档矛盾（CONFLICTS.md）中 3 条是初稿错误已修正、4 条已裁决、2 条待人工确认。8 篇可信度中等的文档全部是文案/
- `MASTER_PLAN.md` — MASTER_PLAN · 红渊总纲：卡池 267 张里六成是换皮、九成八升级是加数、疯先知对核心资源参与度为零（T320/T321）。用户要自己重做卡牌设计。本方案把 120 

### master/cards

- `card_01.md` — card_01：备份四份 cards/*.json：改哪个文件：cards/diver.json, cards/tremor.json, cards/anmin.json, cards/can
- `card_02.md` — card_02：删 58 张卡：改哪个文件：cards/diver.json（26处）、cards/tremor.json（26处）、cards/anmin.json（3处
- `card_03.md` — card_03：贴 10 张零引擎改动通用牌：改哪个文件：cards/shared.json（追加 10 个卡对象）
- `card_04.md` — card_04：改 GLOSSARY 共鸣→共振：改哪个文件：docs/GLOSSARY.md 第 11 行
- `card_05.md` — card_05：加 2 条新手引导：改哪个文件：web/index.html（两处）
- `card_06.md` — card_06：收编 2 组新彩蛋：改哪个文件：web/index.html EASTER_EGGS 表（index.html:6994 附近）
- `card_07.md` — card_07：双脉连携改写：改哪个文件：engine/core.js engine/core.js:429 + web/index.html 内联副本 index.ht
- `card_08.md` — card_08：clear_debuffs 分支：改哪个文件：engine/core.js engine/core.js:655 附近 + web/index.html 内联副本 index
- `card_09.md` — card_09：chain_keep 豁免：改哪个文件：engine/core.js engine/core.js:263 附近 + web/index.html 内联副本
- `card_10.md` — card_10：energy_debt 字段：改哪个文件：engine/core.js beginTurn engine/core.js:258 附近 + web/index.html 
- `card_11.md` — card_11：keep_block_half 特效：改哪个文件：engine/core.js endTurn engine/core.js:682 附近 + web/index.html 内联
- `card_12.md` — card_12：discard 分支：改哪个文件：engine/core.js applyCardEffect engine/core.js:445 附近 + web/index

### onboard

- `D11_ONBOARD.md` — D11 · 新手前 10 分钟（逐分钟）：分  玩家在做什么  应该产生什么  现有引导

### patch

- `01_diver_gaze.md` — D2 · 下潜者×凝视控制 —— 补牌设计（2 张）：项  内容
- `02_cangmin_gaze.md` — D2 · 疯先知×凝视控制 —— 补牌设计（2 张）：项  内容
- `03_anmin_resonance.md` — D2 · 维护者×共振积累 —— 补牌设计（2 张）：项  内容
- `04_tremor_regen.md` — D2 · 震语者×再生续航 —— 补牌设计（2 张）：项  内容
- `05_cangmin_resonance.md` — D2 · 疯先知×共振积累 —— 补牌设计（1 张）：项  内容
- `06_diver_burn.md` — D2 · 下潜者×灼烧流 —— 补牌设计（1 张）：项  内容
- `07_anmin_burn.md` — D2 · 维护者×灼烧流 —— 补牌设计（1 张）：项  内容
- `08_cangmin_burn.md` — D2 · 疯先知×灼烧流 —— 补牌设计（1 张）：项  内容
- `09_cangmin_strength.md` — D2 · 疯先知×力量成长 —— 补牌设计（2 张）：项  内容
- `10_diver_memory.md` — D2 · 下潜者×记忆代价流 —— 补牌设计（1 张）：项  内容
- `11_anmin_memory.md` — D2 · 维护者×记忆代价流 —— 补牌设计（1 张）：项  内容
- `12_diver_protocol.md` — D2 · 下潜者×协议流 —— 补牌设计（2 张）：项  内容
- `13_tremor_protocol.md` — D2 · 震语者×协议流 —— 补牌设计（1 张）：项  内容

### recycle

- `_DISPOSAL.md` — 处置清单：未进入回收的 44 张：被删卡  卡面  版本  处置
- `_INDEX.md` — D3 · 删卡美术回收展开（索引）：通用牌  承接的被删卡  设计书
- `传声钢缆.md` — 回收设计书 · 通·传声钢缆 ← dive_0077（抗共振司·导波索（并联））：项  内容
- `倒转圣痕.md` — 回收设计书 · 通·倒转圣痕 ← cng_0029（耀斑记忆）：项  内容
- `借来的凝视.md` — 回收设计书 · 通·借来的凝视 ← cng_0022（卫星轨道）：项  内容
- `共鸣腔.md` — 回收设计书 · 通·共鸣腔 ← dive_0045（红渊研究院·共振采样）：项  内容
- `减压舱.md` — 回收设计书 · 通·减压舱 ← dive_0057（重力训练舱（极限负重））：项  内容
- `双芯灯管.md` — 回收设计书 · 通·双芯灯管 ← dive_0009（聚能枪（双管））：项  内容
- `守夜人的钟.md` — 回收设计书 · 通·守夜人的钟 ← dive_0078（红渊研究院·频谱印章）：项  内容
- `散落的铅字.md` — 回收设计书 · 通·散落的铅字 ← trem_0062（震语：叩问）：项  内容
- `活水引泉.md` — 回收设计书 · 通·活水引泉 ← trem_0051（震语：润喉）：项  内容
- `深井的回声.md` — 回收设计书 · 通·深井的回声 ← trem_0012（历法刻盘）：项  内容
- `空的手.md` — 回收设计书 · 通·空的手 ← anm_0038（运料井下坠）：项  内容
- `虹吸管.md` — 回收设计书 · 通·虹吸管 ← dive_0043（曜元（共振型））：项  内容
- `越权的批文.md` — 回收设计书 · 通·越权的批文 ← cng_0031（光父的审判）：项  内容
- `风险合同.md` — 回收设计书 · 通·风险合同 ← dive_0031（聚能枪（过热））：项  内容

### relics

- `new_relics_24.md` — 遗物池扩充 · 24 个新遗物

### round2

- `R2_D10_death_rhythm.md` — R2-D10 · 死亡的叙事节奏：死亡次数  结算页文案  静默段  遗言牌  玩家心态
- `R2_D11_onboard_metrics.md` — R2-D11 · 新手引导的量化验证：#  指标  定义  收集方式  健康范围
- `R2_D12_resolution.md` — R2-D12 · 文档矛盾的裁决执行：#  冲突  执行方案  验证命令  影响面
- `R2_D1_deck_strategy.md` — R2-D1 · 通用牌组牌策略（拿 3 张通用牌怎么配）：通用牌的三条获取路（商店 index.html:6806 / 事件 index.html:7419 / 二周目开局 index.html:6
- `R2_D2_weak_path_experience.md` — R2-D2 · 弱流派补牌的玩家体验：玩家拿着通·借来的凝视（u_0015）走进第一场战斗：凝视 0 → 什么都不发生。前 3 回合这张 power 是废卡——这是故意的。玩家需
- `R2_D3_post_prune.md` — R2-D3 · 删卡后的卡池余像：职业  删前  删后  骨架变化
- `R2_D4_copy_round2.md` — R2-D4 · 新卡文案的第二轮（历史/社会/语言三段深化）：新卡  势力  同代既有卡
- `R2_D5_layer_transitions.md` — R2-D5 · 层与层之间的过渡设计：信号  来源  玩家感知
- `R2_D6_enemy_dialogue.md` — R2-D6 · 敌人行为与玩家构筑的对话：新敌人  考的是哪条构筑  考题内容  通过标准
- `R2_D7_event_economy.md` — R2-D7 · 事件分支的流派经济：资源  金币等价  依据
- `R2_D8_discovery_paths.md` — R2-D8 · 组合技的发现路径：路径  玩家行为  对应组合  例子
- `R2_D9_ng_narrative.md` — R2-D9 · 多周目的叙事弧线：叙事序  结局  故事线
- `R3_D1_layer_matrix.md` — R3-D1 · 通用牌 × 层规则交互矩阵：通用牌  L1 no_light  L2 cold  L3 dry  L4 bright  L5 heat_tick  L6 rad_tic
- `R3_D2_sim_verification.md` — R3-D2 · 弱路补牌的模拟验证方案：docs/BALANCE_T29.md §六已诊断：① AI 不堆凝视（凝视流的卡全被低估）② 苍民永梦（dream 侧的卡全被高估）③ 黯
- `R3_D4_art_prompts.md` — R3-D4 · 新卡出图提示词草案（19 张）：一只摊开的矿工手套掌心朝上放在锈蚀的铁板边沿，一把小扳手正从指缝间滑落，半空中的扳手上还挂着一线机油，铁板的边缘磨出了亮色的金属光泽。
- `R3_D5_world_timeline.md` — R3-D5 · 八层的世界观事件史：层  过去
- `R3_D7_event_universal.md` — R3-D7 · 事件分支与通用牌的联动：事件（层）  最适配的通用牌  为什么
- `R3_D9_ending_universal.md` — R3-D9 · 结局与通用牌的交叉：通用牌  对凝视的影响  推向的结局  与结局的配合度
- `R3_roadmap.md` — R3 · 跨方向综合：实施路线图：序  事项  来源  工作量  验证

### shops

- `shop_and_recycle.md` — 商店与回收点 · 对话文案：---

### stream

- `T330_STREAMS_TODAY.md` — T330 · 流派现状诊断：现在到底有没有流派？：流派  卡数  机制核心  互斥性
- `T331_UNIVERSAL_POOL.md` — T331 · 通用牌池设计：任务要求先找「光脉卡同时给震脉充能」的现存例子。找了，结论是不存在：
- `T332_MATRIX.md` — T332 · 角色 × 流派矩阵：流派 \ 职业  下潜者  震语者  维护者  疯先知
- `T333_EVENTS.md` — T333 · 事件层与通用牌：为什么「没有通用牌」对事件层不合理：三个事件池的全量统计（events/all.json 82 个 + events/cangmin.json 10 个 + events/an
- `T334_COST.md` — T334 · 改动的代价（诚实评估）：T332 的矩阵是 10 流派 × 4 职业 = 40 格。职业牌只需在自己职业的 10 个格子里成立，通用牌每一张都要在 40 个格子里自
- `T335_PRUNE.md` — T335 · 通用池落地：裁掉同质化卡 + 卡面回收：职业  删前  删  删后

### tutorial

- `first_3_battles.md` — 新手引导文案 · 前 3 场战斗

### ui

- `00_inventory.md` — UI 现状盘点（代码级 · 10 区域）：---
- `01_issues.md` — UI 问题清单（28 条，全量）：ID  区域  问题  证据  严重度  修法方向
- `04_css_audit.md` — K04 兜底 · CSS 机器级审计：指标  值  说明
- `07_card_pool_shape.md` — A · 卡池结构画像（219 张）：费  类型  普通  精良  稀有  特殊  合计
- `08_proposals.md` — B · 设计提案（10 条，从 28 条问题里挑出）：---
- `09_sfx_touchpoints.md` — C · 音效触点时序表：#  code  wav 文件  SFX_LIST 定义  playSfx 调用  调用点行号  分类
- `10_sfx_wiring_spec.md` — A · 音效接线施工单：---
- `11_card_numbers_audit.md` — B · 卡牌数值审计（219 张）：费  张数  最小  P25  中位  P75  P90  最大  均值
- `12_p0_buildsheets.md` — C · P0 施工单（4 条，可粘 diff）：---
- `_HY4_PROGRESS.md` — HY4 队列进度：完成时间  文件  一句话结论
- `h1_invisible_status.md` — H1 · 隐形状态实证：---
- `h2_keyboard.md` — H2 · 键盘可达性实证：---
- `h3_spec_drift.md` — H3 · 规格漂移对账：---
- `h4_interaction_states.md` — H4 · 交互态矩阵：---
- `x1_sizes.md` — X1 · 实际尺寸核算（1280×720 / 1920×1080）
- `x2_css_vars.md` — X2 · CSS 变量清点
- `x3_motion.md` — X3 · 动画与过渡清点：---
- `x4_breakpoints.md` — X4 · 响应式断点清点
- `x5_layers.md` — X5 · 浮层层级清点
- `x6_sfx_wiring.md` — X6 · 音效三方对照（wav 文件 / SFX_LIST 定义 / index.html 调用）：---

### ui/02_buildsheets

- `UI-001_HUD_overflow.md` — UI-001 HUD overflow 裁切：web/index.html:88
- `UI-002_intent_visual.md` — UI-002 穿透/镜像/drain 意图无视觉区分：web/index.html:139-140
- `UI-003_keyboard_target.md` — UI-003 带目标牌无键盘路径：web/index.html:7977 startCardPointer 只绑 pointer 事件（mousedown/mousemove
- `UI-004_campfire_preview.md` — UI-004 营火升级预览走 title 属性：web/index.html:6763
- `UI-005_parts_indicator.md` — UI-005 零件值 cursor:pointer 无视觉指示：web/index.html:843
- `UI-006_status_visual.md` — UI-006 敌人 debuff 状态无可视化：web/index.html:7837 附近
- `UI-007_upgrade_preview.md` — UI-007_upgrade_preview.md%.md 升级后效果预览缺失：见 00_inventory.md 对应区域。
- `UI-008_needsTarget_kb.md` — UI-008_needsTarget_kb.md%.md needsTarget 说明补键盘路径：见 00_inventory.md 对应区域。
- `UI-009_log_scroll.md` — UI-009_log_scroll.md%.md 日志自动滚动到底：见 00_inventory.md 对应区域。
- `UI-010_unimpl_red.md` — UI-010_unimpl_red.md%.md 效果未实现红字走 blocked 样式：见 00_inventory.md 对应区域。
- `UI-011_event_disabled_osub.md` — UI-011_event_disabled_osub.md%.md 事件禁用选项原因写进 osub：见 00_inventory.md 对应区域。
- `UI-012_shop_disabled.md` — UI-012_shop_disabled.md%.md 商店 cant/sold 加 disabled：见 00_inventory.md 对应区域。
- `UI-013_skip_confirm.md` — UI-013_skip_confirm.md%.md 跳过三选一加确认：见 00_inventory.md 对应区域。
- `UI-014_font_em.md` — UI-014_font_em.md%.md 字号缩放改 em/rem：见 00_inventory.md 对应区域。

### ui/03_proposals

- `P01_damage_feedback.md` — P01 · 伤害与受击的反馈序列：出牌→扣血→飘字→敌人闪红。序列=1 拍：doPlay 内同步调 dealToEnemy（core.js），render() 刷新血条，fl
- `P02_trajectory.md` — P02 · 出牌到命中的轨迹：出牌时 .ghost-fly 从手牌位置飞向 translateY(-80px) scale(.65) rotate(6deg)——向上飞（
- `P03_intent_readability.md` — P03 · 敌人意图的可读性：意图=文字行（如「攻 8」「防 6」「增益」）+ 攻击类脉冲动画。多段攻击显示「10×3」。穿透/镜像/drain 无视觉区分（UI-002
- `P04_status_icons.md` — P04 · 状态图标系统：敌人状态（weak/frail/burn/poison）只有文本拼接在 intent 行内（UI-006）。玩家自身状态（strength/
- `P05_hand_layout.md` — P05 · 手牌 10 张的布局：.card 150×210px；layoutFan() 间距 span=min(66, max(38, (w-170)/(n-1)))；n=
- `P06_energy_feedback.md` — P06 · 费用与能量的即时反馈：能量不足的牌有 .dimmed（opacity .35）+ cursor: not-allowed。playBlockReason() 返回
- `P07_layer_rule_visual.md` — P07 · 层规则触发的视觉提示：8 条层规则触发时的提示方式：
- `P08_res_gaze_critical.md` — P08 · 共振与凝视的临界感：HUD 共鸣/凝视是静态数字。共振 10/20/30 阈值触发时 body.resflash（0.5s 屏幕边框闪红）。凝视无临界视觉。
- `P09_card_detail_hierarchy.md` — P09 · 卡牌详情面板的信息层级：想看「这张牌升级后变什么」→ 只看到「可以在营火升级」。想看「这张牌的脉标签」→ 要看小卡面上的 .cveins（字号 10px）。
- `P10_combat_guidance.md` — P10 · 战斗节奏引导：战斗中玩家「该做什么」完全靠自学。出牌阶段/待选目标阶段/结束阶段没有视觉状态指示。
- `P11_map_presence.md` — P11 · 地图的「我在哪」：地图四种节点状态：.pick（可选，红框脉冲）、.here（当前位置，红框粗）、.near（可见未访问，半透明）、.unseen（范围外，更
- `P12_ending_presentation.md` — P12 · 结算页的信息呈现：死亡/通关结算：标题→结局文本（.ending，pre-wrap）→「这一局最值得说的事」（.memoline）→ 死因提示（.hintli

### ui/pool

- `D01_first_glance.md` — D1 · 第一眼（10 区域 ×「最先看到的是不是最该看的」）：#  区域  实际最先看到  该先看到的  判定  依据
- `D02_misops.md` — D2 · 误操作（10 区域 ×「最容易点错/拖错/看错什么」）：#  区域  最容易犯的误操作  UI 有没有拦  建议
- `D03_keyboard.md` — D3 · 键盘路径（10 区域 ×「不用鼠标能不能走完」）：#  区域  无鼠标能走完吗  缺什么
- `D04_small_screen.md` — D4 · 小屏适配（10 区域 × 1024×768）：#  区域  1024×768 会怎样  最先崩的元素
- `D05_colorblind.md` — D5 · 色盲可辨（10 区域 × 灰度想象）：#  区域  灰度后分得清吗  分不清的是
- `D06_info_density.md` — D6 · 信息密度（10 区域 × 一屏塞了多少条）：#  区域  一屏信息条数  可砍  必须加
- `D07_states.md` — D7 · 状态提示（10 区域 × 每种状态能不能看出来）：#  区域  状态数  每种能看出来吗
- `D08_animation.md` — D8 · 动效时机（10 区域 × 该有的没有/不该有的太多）：#  区域  现有动效  缺的  多余的
- `D09_edge_cases.md` — D9 · 空/错状态（10 区域 × 数据为空/失败/零时显示什么）：#  区域  空/零时会怎样  会不会崩
- `D10_consistency.md` — D10 · 一致性（10 区域 × 按钮/面板/间距/字重是不是同一套语言）：#  区域  按钮  面板  间距  字重  一致？
- `D11_art_cohesion.md` — D11 · 美术协调（10 区域 × 质感和卡牌版画是不是一件事）：#  区域  质感  和卡牌版画协调吗
- `D12_first_time.md` — D12 · 新手第一次（10 区域 × 没看过说明的人会先做什么）：#  区域  新手会先做什么  会不会走错
- `second_axis.md` — D 池第二轴 · 8 状态机 × 12 切法（96 条）：---

### universal

- `U01_01_kong_de_shou.md` — U01 · 空的手（u_0001）设计书：「空的手」来自世界观里矿工的日常动作：把不想要的东西放回岩壁的凹槽。它是全池第一张带选择弃牌的卡——起手烂牌在红渊里有了一个体面的去处，而不
- `U02_02_shouye_ren_de_zhong.md` — U02 · 守夜人的钟（u_0002）设计书：禁声日的钟在换班时敲，敲过就不许再敲——「留一半」的意象直接来自世界观（CAMPFIRE_TEXTS 的静日传统，index.html:66
- `U03_03_hong_xi_guan.md` — U03 · 虹吸管（u_0003）设计书：井下的输液管是矿工之间传东西的日常物件；「虹吸」是它把伤害转成回复的物理隐喻——你从它身上抽走的，顺管子流回你身体。
- `U04_04_shen_jing_de_hui_sheng.md` — U04 · 深井的回声（u_0004）设计书：深井里的回声会把你的话还给你，但不一定按你说的顺序——scry（看牌堆顶、自由排列）的井底叙事化。名字刻意避开「占卜/预知」这类出戏词，留在
- `U05_05_yu_zhi_de_yang.md` — U05 · 预支的氧（u_0005）设计书：矿工把下一班次的氧气提前吸掉——「能量 +2 现在用，下回合 -1 还」。氧气在红渊里就是命，预支氧气是字面意义的借命。
- `U06_06_feng_xian_he_tong.md` — U06 · 风险合同（u_0006）设计书：「死亡合同」的世界观核心物件（dive_0056 是二周目赠卡，开局那句「不保证返程」是全游戏第一句台词）；风险合同是它的民用版——不赌命，
- `U07_07_chuan_sheng_gang_lan.md` — U07 · 传声钢缆（u_0007）设计书：抗共振司的导波索（dive_0044/0077）是把振动引走的物件；传声钢缆反过来——不是消音，是把光脉的声音传给震脉听。它的名字里没有「通
- `U08_08_hui_jin_ce_zhen_yi.md` — U08 · 灰烬测振仪（u_0008）设计书：灼烧会震动——烧过的岩层在冷却时发出细响。测振仪把「火」和「听」连在一起，这是灼烧流与共振流第一次共用一张卡的语言学基础。
- `U09_09_dao_zhuan_sheng_hen.md` — U09 · 倒转圣痕（u_0009）设计书：圣痕是「被红光选中」的印记（敌人 gift 意图给凝视的叙事对应物）；倒转是玩家第一次主动把印记翻面——从「被看」转成「听见」。凝视减 2 
- `U10_10_xie_zhen_dian_ceng.md` — U10 · 谐振垫层（u_0010）设计书：把震动能垫在身下——维护者的共振管理叙事（drain 3 张）第一次有了「收益端」：压掉的共振不再是损失，是垫层。
- `U11_11_huo_shui_yin_quan.md` — U11 · 活水引泉（u_0011）设计书：泉眼在红渊是稀罕物（水脉 31 张全池最少）；「引泉」是维护者与震语者都会做的动作——一个引给管道，一个引给喉咙。heal+dexterit
- `U12_12_shuang_xin_deng_guan.md` — U12 · 双芯灯管（u_0012）设计书：渊光重工的产品目录里真有双芯灯（双芯=冗余=安全）；「一根照明一根点火」是它的黑幽默——厂里的安全冗余变成了矿工的武器。light+heat
- `U13_13_san_luo_de_qian_zi.md` — U13 · 散落的铅字（u_0013）设计书：报馆塌了——世界观里「城邦」的地面部分已经死了一段时间，铅字从上面落下来，比骨头还硬。AoE+weak 的组合是「字砸下来所有人都被砸得迟钝
- `U14_14_gong_ming_qiang.md` — U14 · 共鸣腔（u_0014）设计书：dive_0045 的空陶瓮在洞口共鸣——把它做成一张 power：连携不再每回合清零。「腔」是物理学的共鸣容器，也是「憋着一口气」的矿工隐
- `U15_15_jie_lai_de_ning_shi.md` — U15 · 借来的凝视（u_0015）设计书：凝视本来是红渊看你的方式；「借来的」意味着你主动去借——每回合开始，凝视每 5 点给你 1 力量。负债变抵押贷款，这是凝视体系从惩罚资源变成
- `U16_16_yue_quan_de_pi_wen.md` — U16 · 越权的批文（u_0016）设计书：维护者世界观的核心是「批文」（anm_0036 保运行批文、anm_0015 主控授权）；越权的批文是你自己签的——签发栏是空的。「越权」点
- `U17_17_jian_ya_cang.md` — U17 · 减压舱（u_0017）设计书：dive_0057 的重力训练舱是加压的，减压舱反过来——从红渊的压力里出来喘一口气。clear_debuffs 是「解除 weak/poi
- `_README.md` — D1 · 通用牌逐张设计书（17 份索引）：牌  设计书

### what_it_fills

- `00_INDEX.md` — D1 · 每张卡「它在补什么」· 总索引：角色  Top1  Top2  Top3  明显空缺
- `anmin.md` — 维护者 · 每张卡「它在补什么」：- anm_0001 现场回收 —— 格挡
- `cangmin.md` — 疯先知 · 每张卡「它在补什么」：- cng_0001 守夜 —— 格挡
- `diver.md` — 下潜者 · 每张卡「它在补什么」：- dive_0001 光导透镜（残） —— 过牌
- `shared.md` — 通用 · 每张卡「它在补什么」：- share_0001 强行供能 —— 机制解
- `tremor.md` — 震语者 · 每张卡「它在补什么」：- trem_0001 震语：听骨 —— 过牌

### world

- `D5_EIGHT_LAYERS.md` — D5 · 八层世界观补全（按「倒吊 + 红光」推演）：项  内容
