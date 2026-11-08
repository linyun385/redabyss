# G07 · 百条结论清单（按重要性排序）

> 来源：本夜 94 篇产出（每条带出处文件）。排序为人工判读的重要性序：引擎实证 > 玩家可见问题 > 结构性发现 > 数据事实。

## 一、引擎实证（会改代码结论的）

1. 脆弱（frail）是死状态：全引擎只有施加与递减两处，`dealToEnemy` 从不读它——两张卡的白挂件。（dead_card_check.md）
2. u_0009 倒转圣痕的 special 码 `resonance_gain` 无 case，落 default 红字，共振+3 不生效。（dead_card_check.md）
3. u_0016 越权的批文不是废卡：`anmin_mark` 激活 purge 协议真实生效（每回合自伤2/敌我攻+3），问题是 effect 字段空导致卡面零描述。（dead_card_check.md）
4. engine/core.js 与 web 内联副本 41 个函数一一对应，5 处分歧——core 是过期副本且被 tools/sim.js 等 10 个工具 require。（engine_diff.md）
5. sim 世界的能量=3、特殊值按默认结算——**历史上所有基于 sim 的平衡结论与实跑游戏不是同一套参数**。（engine_diff.md）
6. BASE_ENERGY：core=3 / web=4，T400 §2.4 的 3→4 只改了 web。（all_numbers.md）
7. weak（虚弱）真实生效：敌人带 weak 时攻击 ×0.75（core.js:745）。（natural_combos.md）
8. 灼烧引擎语义是**覆盖不叠加**（core.js:494 取后值）——铺火牌互相盖，多铺不等于更疼。（natural_combos.md）
9. 敌人意图是**固定循环**（`pat[idx % len]`，无随机），换阶段时 idx 归零——145 只全部机械可算。（intent_predictability.md）
10. 凝视门槛（gaze_cost）只查不扣（web:5709），是「资格制」而非消耗——这是自己的定价发明。（all_numbers.md）

## 二、玩家可见问题（明天可修的）

11. 五脉是唯一「必须懂但零解释」的词组——五个脉名在游戏里从未被定义。（game_terms_full.md）
12. 连携提示（onceHint chain）在 D11 里规划了但**至今未实装**。（tutorial_gaps.md）
13. 威胁等级零解释：只有拆解那一秒的 log，全局难度开关全程隐身。（tutorial_gaps.md）
14. 正向层规则无提示：L4 光脉+2 没有任何告知，负向层规则（cold/dry/no_light）有红字——同一条通道只发坏消息。（game_terms.md）
15. 敌人穿透攻击（pierce）在意图显示上无标记，第一次撞震喉阶段 3 会被当成 bug。（tutorial_gaps.md）
16. 共振/凝视被偷（steal）无预告，第一次是纯惊吓。（game_terms.md）
17. anevent_06「追查消耗去向」result_text 说「没有推门」却扣 4 血——代价来源与文本脱节，玩家信任问题。（event_rewrite.md）
18. 事件选项文本普遍不带结果信号：44 个事件全部实质选项是盲/暗示选。（event_rewrite.md/event_info.md）
19. u_0016 的 purge 激活全程无 UI 状态显示，玩家不知道自己每回合为什么掉血。（dead_card_check.md）
20. 卡面写「共鸣」、日志写「共振」——同一屏两个名字。（term_audit.md）

## 三、脉象系统（重构的核心输入）

21. 下潜者水脉 2 张是全池最大缺口（T400 点名，数据证实）。（vein_audit_matrix.md）
22. 「过牌位挂错脉」是最大的标签问题：光脉 25 张纯抽牌、矿脉 10 张抽牌/共振——抽牌是水的味道。（vein_audit_matrix.md T406）
23. 热脉 15 张只改自己（无伤害无挂敌状态）——热被写成了第二条矿。（vein_audit_matrix.md T406 V1）
24. 震脉 5 张要花共振（resonance_cost）——违反「震不许要铺垫」判据。（vein_audit_matrix.md T406 V4）
25. 跨角色同脉同效果 28 组，其中 17 组是复合效果撞配方（真想法撞车）。（vein_audit_matrix.md T404）
26. 与通用牌完全撞 4 次/近似撞 21 次（dup_check 口径）；扩到全 219 张是 32 组完全撞/24 组近似分量。（vein_audit_matrix.md T402）
27. 近似撞的误报主因=查重不含 cost_type（付生命的直伤被当成白给直伤）。（vein_dup_review.md）
28. 通用池 11 张方案 C 红线零违反（没有核心卡混入）。（shared_pool_audit.md）
29. 脉象等级纯生态进项下峰值 1-2、寿命 2-3 层、上限 5 摸不到——与「保底成长」意图不匹配。（vein_curve.md）
30. 等级曲线形状由「生态↔脉映射表」决定，那是设计者下一张要拍的表。（vein_curve.md）
31. 五脉费用形状与时间轴定义吻合：水全 ≤1 费、震 2/3 费占比最高。（vein_cost_curve.md）
32. 3+ 费全池仅 7 张——能量改 4 后 3 费卡从鸡肋变可用（T400 预判成立）。（vein_cost_curve.md）
33. 共振经济事实上是双角色系统：引擎 19 张集中在下潜者/震语者。（what_it_fills/00_INDEX.md）
34. 凝视的主动进项轴只有 2 张 gaze_gain——凝视经济「进项靠被动」，主动权极低。（keyword_frequency.md）
35. resonance_drain（泄压阀）只有 5 张，而 L6 起共振必然过载——泄压不足是结构性的。（keyword_frequency.md/resource_curve.md）
36. 正例样本库成立：光=用资源换超额、水=流转主体、热=状态主体、震=零铺垫、矿=无条件改自己。（vein_positive_examples.md）

## 四、卡池结构（重构的取舍依据）

37. 219 张里 196 张「与谁重复」列非空——卡池高度同质化。（vein_audit_matrix.md T402）
38. 纯格挡基准牌连成 23 张的近似撞大分量——防御基准位严重超编。（vein_audit_matrix.md）
39. 最没人拿的 20 张里 17 张的病根是同池内部重复。（least_picked_20.md）
40. 备用电源（1 费抽 3 无限制）是下潜者池的隐形天花板，压住了同池所有过牌位。（least_picked_20.md）
41. 0 费位对 1 费同效果位是碾压关系——0 费抽牌的存在本身就是问题。（least_picked_20.md）
42. 升级覆盖 216/219，缺的 3 张全是无脉普通卡（后补填充位没走完流程）。（upgrade_coverage.md）
43. 稀有度大体按强度分：高稀平 0 命中；「特殊」14 张全是机制展示位。（rarity_dist.md）
44. 全池 18 格里空格 3 个、单卡格 2 个——2+ 费位是结构性缺口。（pool_3d.md）
45. 每个角色池有 10+ 个 ≤2 张的薄组合，痛点击中「2 费攻击稀有」与「0 费能力」。（pool_thickness.md）
46. 断头协同：灼烧/中毒只有施加端没有兑现端；虚弱有兑现端（×0.75）。（natural_combos.md）
47. 自然组合的主力是数值堆叠（力量/敏捷/荆棘/再生）和共振循环——不用设计就有配合。（natural_combos.md）
48. 散牌局现实预期：打到 L5-L6，死于 L7 的 30 点尖峰；矿脉在散牌局天然好用，热脉最惨。（scatter_plan.md）
49. 力量堆叠链（3 张 ×2）+多段卡=全池最高性价比组合。（natural_combos.md）
50. 通用池本身是「每缺口 1 张」的补丁池形态。（what_it_fills/00_INDEX.md）

## 五、敌人与难度

51. L2→L3 血量断崖 +70% 是全曲线最危险跳变（玩家最弱时间点+强制精英+回复变贵三重叠加）。（enemy_power_curve.md）
52. L6→L7 攻击 +88%（单发 16→30）是形态切换：血厚层换尖峰层。（enemy_power_curve.md）
53. 最容易死的层是 L3（不是敌人最猛的 L7/L8）——玩家最弱与敌人变强的交点。（death_causes.md）
54. L7 穹顶之影 buff×2 后单发 30 点，全游戏最高单发。（death_causes.md）
55. 必躲敌人 18 只（期望承伤 ≥20 的普通敌）——普通敌奖励与强弱无关，多挨全是净亏。（enemy_avoid.md）
56. 敌人攻击意图占比中位约 6 成，100% 纯攻击型只有 3 只——「节奏敌人」是低层教学设计。（intent_coverage.md）
57. debuff 在普通敌零出现——减益应对（锁定/清除）前期没有练兵场。（intent_coverage.md）
58. L5 热泉层敌人几乎不玩火：14 只仅 1 只施加灼烧——层主题与敌人行为脱节。（enemy_layer_fit.md）
59. 敌人全名零重名，家族靠词干（震喉/震喉·空腔独奏）——GLOSSARY 家族命名规则执行良好。（layer_composition.md）
60. 敌名五式齐全，核心反差装置=「非人在做人的工作」。（enemy_naming_guide.md）

## 六、事件

61. 事件总供给：102 个事件、306 个选项、全程期望遇到 ~6 次。（event_table.md/event_density.md）
62. 事件密度两头高中间低：L2-L5 每层期望仅 0.5 次——build 成型期事件供给最少。（event_density.md）
63. L4-L8 连续五层无商店——中段经济断供。（event_density.md）
64. 事件回血选项泛滥：83/306（27%）——事件的紧张感被「歇一会儿」稀释。（healing_check.md）
65. 事件选项信息量：明示 39.9% / 暗示 36.6% / 纯随机 23.5%。（event_info.md）
66. 必选选项 20 个（净值 ≥25 且零损失）——零风险高收益位偏多。（event_rr.md）
67. 同事件被支配选项 59 个——收益差 ≥10 且代价不增的坏按钮比想象多。（bad_event_options.md）
68. 「净收益」口径下事件是大血库：中位恢复 ~300 vs 损耗 ~150-400。（healing_check.md）
69. 难度来自尖峰不是消耗——死亡来自失误而非资源枯竭，这是健康形态。（healing_check.md）
70. 事件的文学水准全池最高，重写需求在「信号」不在文笔。（event_rewrite.md）

## 七、经济与资源

71. 金币全程收入 ~550 vs 商店消费 2~3 次——**过剩**，瓶颈是出货口。（resource_curve.md）
72. 零件越打越多（击杀制），全程可改 15~25 次——上限远超需求。（resource_curve.md）
73. 凝视只进不出：20 结局线被参数决定，「控制凝视」当前不可逆。（resource_curve.md）
74. 共振 L6 起必然过载（自动 +6/回合 vs 消费端 7 张）。（resource_curve.md）
75. 卡组获取 +12~18 vs 删牌 1~3——获取速度偏肥一个数量级。（deck_size.md）
76. 回复供给中位 ~300/局——够且偏多；疯先知按 30 血口径反而成了最不需要回复的职业。（healing_check.md）
77. 商店最贵 320 vs 第一局金币峰值 ~450——第一局只能买小件。（first_run_flow.md）
78. 四种资源三种失衡形态，全是「出口不够」不是「入口不够」。（resource_curve.md）

## 八、引导与术语

79. onceHint 现役 6 条覆盖了任务书点名的六缺口中的三个——牌堆循环已有全覆盖。（tutorial_gaps.md）
80. 任务书点名的「锁死」在游戏里不叫锁死（卡面=本层只能用一次）——术语只在设计文档里存在。（tutorial_gaps.md）
81. 玩家体验总图：教学全在 L1-L2、考试在 L3/L7-L8、三条暗坑埋在中段。（experience_map.md）
82. 新手 10 错的共性根因=「代价 invisible」——长期后果不显示在决策时刻。（newbie_mistakes.md）
83. 术语冲突 7 组：最大的是共鸣/共振（250 vs 1289 处）、「层」vs「深度带」（正名失守）。（term_audit.md）
84. 术语统一到「共振」代价最低（改 GLOSSARY 1 行+内容表 112 行；反向要改 1083 行+引擎 log）。（term_unify_plan.md）
85. 入梦/切世/梦栖三词竞争且 GLOSSARY 无裁决。（term_audit.md）
86. 开发词（素卡/素品/深度带）零泄漏进玩家视野——GLOSSARY 的隔离功能是成功的。（game_terms_full.md）
87. 疯先知池是唯一大量用「我」的池——「梦=主观」被写进了人称语法。（layer_literary.md）

## 九、文案与世界观

88. 八层八种文体（规程/遗物/配给/家宅/值班/剂量/告别/值班体）呈同心圆结构，首尾押韵。（layer_literary.md）
89. 贯穿全游戏的意象系统是「记录」：清单→拓片→账簿→剂量条→班表——红渊=一个把一切都记下来的地方。（layer_literary.md）
90. 全部 107 件遗物都有风味且质量高；风味-效果连接靠「使用痕迹」隐喻成立，真弱连接仅 6 件。（relic_lore.md）
91. 卡名第一印象：可判定名 75 张相符 21 张猜错——「物件名效果分裂」（灯/碑/符系）是真问题，纯意象名信息量=0 是风格。（first_impression.md）
92. 事件文案与遗物文案的写作纪律（证据感/使用痕迹）值得固化成规范。（flavor_rewrite.md/relic_lore.md）
93. 与密教模拟器的气质最近（档案体+凝视+梦境组合），防撞建议=把脉象/共振层反应/凝视门槛三件自有设计放门面位。（inspiration_log.md）

## 十、文档健康与结构

94. 旧文档零回写是全部矛盾的共同根因：剪枝（267→219）与 T400 定稿后没有一篇旧文档被标注。（_CONFLICTS.md）
95. 失效卡 id 波及 ≥20 个文档（ART_MAP/FINAL_MANIFEST/T321/T340 各 58 个）。（vein_doc_conflicts.md）
96. master/05_TERMS 早已独立裁决「共鸣→共振」——与本夜 F2 殊途同归，说明该裁决是可靠的。（_THIN_DOCS_AUDIT.md）
97. 170 篇 <100 行文档零「内容缺失型薄弱」——短是操作单/索引/数据密集的结构性形态。（_THIN_DOCS_AUDIT.md）
98. 层数与敌人种数不成正比：L1-3 各 22-27 只、L4+ 每层 14-15 只——前期多而杂、后期少而精。（layer_composition.md）
99. 一局时长两档 25-30 / 60-75 分钟；新手真实体感是 20 分钟死局循环。（playtime_estimate.md）
100. 全部数字类结论可复算——复算脚本集中在 data/audit/（约 30 个生成器），每份文档文末带算法说明。（全队列）

## 使用建议

- 明天只想看 10 分钟 → 读 1-10（引擎）、11-20（玩家可见）、51-53（难度）。
- 要动卡池 → 读 21-50。
- 要动文案/术语 → 读 83-93。
- 修复清单 → _BUGS.md（本表的 1-20 已在那里转成可执行项）。
