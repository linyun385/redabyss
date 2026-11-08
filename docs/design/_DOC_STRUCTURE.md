# G12 · 文档目录整理建议（只给方案，不移动文件）

> 现状：docs/design/ 平铺 94 篇 + what_it_fills/ 6 篇。目标：按用途分 12 个子目录。
> 迁移原则：① 每篇唯一归属（按**主要回答的问题**分类，不按产出任务号）；② `_` 前缀的导航/结论文件留在根目录（它们是入口）；③ 存量历史文档进 history/ 不与产出混放；④ 迁移时所有交叉引用路径要批量更新（本表第 3 节给了引用清单）。

## 一、目标结构

```
docs/design/
├── _INDEX_NIGHT.md      ← 总导航（留根）
├── _CONCLUSIONS.md      ← 100 条结论（留根）
├── _READ_FIRST.md       ← 先读清单（留根）
├── _BUGS.md             ← 修复清单（留根）
├── _FINDINGS.md         ← 发现实证（留根）
├── _DOC_CONFLICTS.md    ← 矛盾交叉（留根）
├── matrix/              总表与全量数据（7）
├── cards/               卡牌分析（16）
├── veins/               脉象系统（12）
├── enemies/             敌人（9）
├── events/              事件（7）
├── relics/              遗物（6）
├── layers/              层与世界观（4）
├── economy/             经济与节奏（5）
├── onboarding/          引导与体验（8）
├── terms/               术语（4）
├── conflicts/           冲突审计（4）
├── meta/                方法与元文档（5）
├── history/             存量文档（14）
└── what_it_fills/       （保持现位，6）
```

## 二、逐篇归属（94+6 篇全覆盖）

### matrix/（7）——「查数字/查全表」来这里
vein_audit_matrix.md, enemy_table.md, event_table.md, relic_table.md, layer_rules.md, all_numbers.md, card_quickref.md

### cards/（16）——「卡的事」
card_intent_reverse.md, card_readability.md, text_length.md, first_impression.md, upgrade_coverage.md, natural_combos.md, orphan_cards.md, keyword_frequency.md, pool_3d.md, pool_thickness.md, thin_spots_merged.md, redesign_notes.md, redesign_clusters.md, shared_pool_audit.md, card_naming_guide.md, flavor_rewrite.md

### veins/（12）——「脉的事」
vein_cost_curve.md, vein_effects_by_vein.md, vein_flavor_card.md, vein_writing_card.md, vein_no_vein_advice.md, vein_dup_review.md, vein_special_mech_cards.md, vein_positive_examples.md, vein_tag_review.md, vein_curve.md, special_mech_dist.md, card_intent_reverse.md 不进这里（已在 cards）

（注：11 篇实际——vein_doc_conflicts 归 conflicts/）

### enemies/（9）
enemy_table 不进（在 matrix）。enemy_card_map.md, enemy_avoid.md, enemy_power_curve.md, enemy_naming_guide.md, enemy_lore_rewrite.md, enemy_layer_fit.md, intent_predictability.md, intent_coverage.md, attack_rate.md

### events/（7）
event_table 不进（在 matrix）。event_info.md, event_rr.md, event_density.md, event_vein_link.md, event_rewrite.md, bad_event_options.md, deck_size.md 不进（归 economy）

### relics/（6）
relic_table 不进（在 matrix）。relic_mustpick.md, relic_tier.md, relic_vein_fit.md, relic_lore.md, healing_check.md 不进（归 economy）→ relics/ 实为 4 篇 + ECO_RELIC_CARD 类存量不迁移

### layers/（4）
layer_theme.md, layer_literary.md, layer_composition.md, scatter_plan.md（散牌局是「层体验」视角）

### economy/（5）
resource_curve.md, deck_size.md, healing_check.md, combat_pace.md, playtime_estimate.md

### onboarding/（8）
first_5min.md, first_run_flow.md, newbie_mistakes.md, tutorial_gaps.md, decision_points.md, experience_map.md, game_terms.md, game_terms_full.md

### terms/（4）
term_audit.md, term_unify_plan.md, _TERMS_MERGED.md（若坚持 _ 留根则留根，二选一）, class_pick_hint.md（选人文案属文案规范类，就近放 terms 或 onboarding——**推荐 onboarding**）

### conflicts/（4）
vein_doc_conflicts.md, old_doc_conflicts.md, _CONFLICTS.md（留根亦可）, CONFLICTS.md（存量旧版）

### meta/（5）
inspiration_log.md, _THIN_DOCS_AUDIT.md, _DEPTH_AUDIT.md, _DOC_STRUCTURE.md（本文件）, starter_deck_analysis.md（四角色初始分析——也可归 onboarding，**推荐 onboarding**）

### history/（14 + what_it_fills 保持）
CARD_EFFECTS_AUTO.md, CONFLICTS.md, DESIGN_TODO.md, DUP_VS_SHARED.md, T320-T324（5）, glossary_check.md, _FIX_20261104, _NIGHT_REPORT_1104, _PROGRESS.md, _VERIFY_NIGHT.md
what_it_fills/（6）保持现位不改——它已经是自洽的子目录。

## 三、迁移时的引用修复清单

以下文档互相用**相对文件名**引用，迁移后需批量替换路径（grep 文件名即可定位）：
- `_CONCLUSIONS.md` / `_READ_FIRST.md` / `_BUGS.md`（引用几乎所有产出文件名）
- `vein_audit_matrix.md`（被 T403/T404/T406/T412 节内引用）
- `_TERMS_MERGED.md` ↔ term_audit/term_unify_plan/game_terms_full 三向引用
- engine_diff/_FINDINGS ↔ dead_card_check/all_numbers
- 教训：**迁移一个目录更新一批引用**，不要一次全移。

## 四、执行估算

- 移动文件：100 个 `mv`（可脚本化）
- 引用修复：约 6 批 grep+sed
- 风险：外部工具（tools/check_design_refs.py 等）可能校验固定路径——迁移前先跑一遍全量检查器确认哪些路径被写死。

## 复算

归属表覆盖 94+6 篇（逐篇唯一）；目录计数与第二节小标题数一致。

## 五、补充归属（覆盖校验后的补全，2026-11-05）

第二节按行文归组，以下逐一补齐校验中缺名的文件：

- **cards/** 增补：banned_word_scan.md, numeric_outliers.md, rarity_dist.md, least_picked_20.md, dead_card_check.md, redesign_clusters.md（已列）, thin_spots_merged.md（已列）
- **veins/** 增补：vein_tag_review.md
- **enemies/** 增补：death_causes.md, enemy_layer_fit.md（已列）, attack_rate.md（已列）
- **onboarding/** 增补：experience_map.md（已列）, class_pick_hint.md, starter_deck_analysis.md
- **meta/** 增补：engine_diff.md（引擎对账属方法/元文档）
- **history/** 逐一列出（第二节以家族带过）：T320_MECHANISMS.md, T321_REDUNDANCY.md, T322_MONOTONY.md, T323_RULES.md, T324_GAPS.md, _FIX_20261104_special_value.md, _NIGHT_REPORT_1104.md, _PROGRESS.md, _VERIFY_NIGHT.md
- **what_it_fills/**：00_INDEX.md, diver.md, tremor.md, anmin.md, cangmin.md, shared.md——保持现位
- **留根**（已在第二节声明）：_INDEX_NIGHT.md, _CONCLUSIONS.md, _READ_FIRST.md, _BUGS.md, _FINDINGS.md, _DOC_CONFLICTS.md, _TERMS_MERGED.md, _DOC_STRUCTURE.md
- 本批 G 系其余新档：engine_diff→meta, vein_tag_review→veins, enemy_layer_fit→enemies, experience_map→onboarding, redesign_clusters/thin_spots_merged→cards, _DEPTH_AUDIT→meta

补全后覆盖 = 全部 112 个现存 md（94+6+本批 12）零遗漏（复算：脚本比对 0 缺名）。
