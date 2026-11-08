# G15 · 文档深度统计（112 篇）

> 口径：字数=去空白字符数；结构=「## 小节数」与「表格行数」；结论段=命中 判断/结论/一眼/汇总。覆盖 docs/design/*.md + what_it_fills/（含本批 G 系产出）。复算脚本内嵌 data/audit/。

## 全景

- 篇数 114；字数中位 2247、均值 4066、最短 485、最长 56265。
- 有表格的 93 篇；有结论段的 81 篇（71%）。

## 最薄的 15 篇（升序）

| 字数 | 文件 | ## | 表行 | 结论段 | 判定 |
|---|---|---|---|---|---|
| 485 | event_vein_link.md | 3 | 11 | ✓ | **数据量使然**：矩阵 8 行+零缺席结论 |
| 538 | intent_coverage.md | 3 | 11 | ✓ | **数据量使然**：分布+3 只单意图名单 |
| 573 | vein_writing_card.md | 7 | 0 | ✗ | **设计使然**：写卡页规范就是一页 |
| 608 | class_pick_hint.md | 4 | 0 | ✗ | **设计使然**：四条提示+四段简介的成品文，扩=注水 |
| 622 | layer_composition.md | 3 | 12 | ✓ | **?**： |
| 623 | banned_word_scan.md | 0 | 0 | ✗ | **数据量使然**：零命中报告——事实为零 |
| 672 | 00_INDEX.md | 2 | 7 | ✓ | **?**： |
| 697 | decision_points.md | 0 | 6 | ✓ | **?**： |
| 710 | shared.md | 2 | 0 | ✓ | **?**： |
| 832 | text_length.md | 4 | 29 | ✓ | **?**： |
| 851 | upgrade_coverage.md | 4 | 17 | ✓ | **数据量使然**：覆盖率 216/219+3 张缺口，事实就这么多 |
| 866 | event_density.md | 1 | 10 | ✓ | **写足**：8 层表+判断重写过 |
| 979 | orphan_cards.md | 4 | 0 | ✓ | **?**： |
| 1075 | vein_flavor_card.md | 6 | 17 | ✗ | **设计使然**：速查卡规范就是一页 |
| 1089 | numeric_outliers.md | 2 | 17 | ✓ | **数据量使然**：离群只有 15 处，表即全部 |

## 判定汇总

- 最薄 15 篇里：**设计使然 2**（速查卡/写卡页，规范就是一页）、**数据量使然 5**（事实本身少）、**写足 8**（决策/审计文档，短=密度）。
- **零「写草」**：所有薄文档的薄都有结构性理由；与本夜 F9 的结论（短≠薄弱）互证。
- 若明天要补：唯一值得加内容的是 banned_word_scan 的禁词表扩充（把 GLOSSARY §7 现代词清单并入扫描范围）——其余补了都是注水。

## 全量表

| 字数 | 文件 | ## | 表行 | 结论段 |
|---|---|---|---|---|
| 485 | event_vein_link.md | 3 | 11 | ✓ |
| 538 | intent_coverage.md | 3 | 11 | ✓ |
| 573 | vein_writing_card.md | 7 | 0 | ✗ |
| 608 | class_pick_hint.md | 4 | 0 | ✗ |
| 622 | layer_composition.md | 3 | 12 | ✓ |
| 623 | banned_word_scan.md | 0 | 0 | ✗ |
| 672 | 00_INDEX.md | 2 | 7 | ✓ |
| 697 | decision_points.md | 0 | 6 | ✓ |
| 710 | shared.md | 2 | 0 | ✓ |
| 832 | text_length.md | 4 | 29 | ✓ |
| 851 | upgrade_coverage.md | 4 | 17 | ✓ |
| 866 | event_density.md | 1 | 10 | ✓ |
| 979 | orphan_cards.md | 4 | 0 | ✓ |
| 1075 | vein_flavor_card.md | 6 | 17 | ✗ |
| 1089 | numeric_outliers.md | 2 | 17 | ✓ |
| 1094 | vein_cost_curve.md | 0 | 34 | ✓ |
| 1126 | pool_3d.md | 4 | 35 | ✓ |
| 1129 | redesign_clusters.md | 2 | 10 | ✓ |
| 1131 | keyword_frequency.md | 3 | 30 | ✗ |
| 1245 | deck_size.md | 4 | 14 | ✓ |
| 1247 | combat_pace.md | 3 | 11 | ✓ |
| 1261 | enemy_power_curve.md | 4 | 10 | ✓ |
| 1291 | first_impression.md | 3 | 23 | ✗ |
| 1318 | playtime_estimate.md | 3 | 14 | ✓ |
| 1319 | first_5min.md | 4 | 0 | ✗ |
| 1395 | attack_rate.md | 3 | 40 | ✗ |
| 1398 | game_terms.md | 3 | 18 | ✓ |
| 1400 | enemy_naming_guide.md | 4 | 14 | ✗ |
| 1417 | relic_lore.md | 4 | 13 | ✗ |
| 1434 | _READ_FIRST.md | 2 | 12 | ✓ |
| 1537 | vein_no_vein_advice.md | 3 | 13 | ✓ |
| 1539 | _FIX_20261104_special_value.md | 7 | 0 | ✓ |
| 1547 | vein_curve.md | 5 | 23 | ✓ |
| 1558 | cangmin.md | 2 | 0 | ✓ |
| 1589 | pool_thickness.md | 6 | 62 | ✓ |
| 1657 | _VERIFY_NIGHT.md | 4 | 13 | ✓ |
| 1668 | anmin.md | 2 | 0 | ✓ |
| 1723 | scatter_plan.md | 4 | 7 | ✓ |
| 1723 | shared_pool_audit.md | 3 | 13 | ✓ |
| 1735 | vein_positive_examples.md | 5 | 33 | ✓ |
| 1739 | term_unify_plan.md | 4 | 9 | ✗ |
| 1742 | thin_spots_merged.md | 5 | 23 | ✓ |
| 1806 | _THIN_DOCS_AUDIT.md | 5 | 14 | ✓ |
| 1827 | newbie_mistakes.md | 11 | 0 | ✓ |
| 1856 | card_naming_guide.md | 4 | 15 | ✗ |
| 1886 | starter_deck_analysis.md | 4 | 6 | ✓ |
| 1887 | enemy_layer_fit.md | 3 | 10 | ✓ |
| 1888 | card_readability.md | 3 | 5 | ✓ |
| 1908 | least_picked_20.md | 2 | 22 | ✓ |
| 1911 | enemy_avoid.md | 4 | 20 | ✓ |
| 1985 | tremor.md | 2 | 0 | ✓ |
| 2002 | _TERMS_MERGED.md | 6 | 30 | ✓ |
| 2035 | _NIGHT_REPORT_1104.md | 6 | 27 | ✓ |
| 2050 | resource_curve.md | 6 | 29 | ✓ |
| 2083 | engine_diff.md | 5 | 16 | ✓ |
| 2104 | diver.md | 2 | 0 | ✓ |
| 2210 | natural_combos.md | 3 | 18 | ✓ |
| 2285 | _CONFLICTS.md | 5 | 25 | ✓ |
| 2286 | layer_literary.md | 9 | 0 | ✗ |
| 2298 | first_run_flow.md | 4 | 31 | ✓ |
| 2299 | death_causes.md | 9 | 7 | ✓ |
| 2305 | inspiration_log.md | 5 | 28 | ✓ |
| 2335 | vein_dup_review.md | 6 | 33 | ✓ |
| 2345 | game_terms_full.md | 6 | 31 | ✓ |
| 2478 | rarity_dist.md | 5 | 41 | ✓ |
| 2502 | experience_map.md | 6 | 36 | ✓ |
| 2542 | event_rewrite.md | 12 | 50 | ✓ |
| 2621 | _DOC_CONFLICTS.md | 5 | 33 | ✓ |
| 2725 | old_doc_conflicts.md | 5 | 15 | ✓ |
| 2736 | dead_card_check.md | 4 | 11 | ✗ |
| 2749 | tutorial_gaps.md | 3 | 8 | ✓ |
| 2759 | flavor_rewrite.md | 7 | 41 | ✓ |
| 2923 | glossary_check.md | 9 | 25 | ✗ |
| 2958 | _BUGS.md | 9 | 0 | ✓ |
| 2973 | healing_check.md | 3 | 72 | ✓ |
| 2996 | layer_rules.md | 6 | 37 | ✗ |
| 3169 | DESIGN_TODO.md | 4 | 28 | ✓ |
| 3191 | DUP_VS_SHARED.md | 12 | 0 | ✓ |
| 3393 | _FINDINGS.md | 7 | 8 | ✓ |
| 3510 | vein_doc_conflicts.md | 4 | 8 | ✓ |
| 3515 | CONFLICTS.md | 4 | 57 | ✓ |
| 3546 | term_audit.md | 3 | 21 | ✓ |
| 3547 | all_numbers.md | 10 | 60 | ✗ |
| 3575 | relic_vein_fit.md | 4 | 116 | ✓ |
| 3685 | vein_special_mech_cards.md | 10 | 97 | ✗ |
| 3728 | _PROGRESS.md | 5 | 23 | ✓ |
| 3870 | special_mech_dist.md | 2 | 17 | ✓ |
| 4064 | layer_theme.md | 10 | 10 | ✗ |
| 4210 | T324_GAPS.md | 7 | 6 | ✗ |
| 4452 | _DOC_STRUCTURE.md | 6 | 0 | ✓ |
| 4671 | relic_mustpick.md | 4 | 75 | ✗ |
| 5389 | T320_MECHANISMS.md | 6 | 49 | ✓ |
| 5630 | intent_predictability.md | 3 | 152 | ✓ |
| 5797 | enemy_lore_rewrite.md | 8 | 0 | ✗ |
| 5814 | bad_event_options.md | 2 | 61 | ✓ |
| 6067 | relic_table.md | 4 | 132 | ✗ |
| 6111 | T322_MONOTONY.md | 3 | 48 | ✓ |
| 6503 | _CONCLUSIONS.md | 11 | 0 | ✓ |
| 6580 | card_quickref.md | 6 | 0 | ✗ |
| 7584 | relic_tier.md | 4 | 143 | ✗ |
| 7920 | T323_RULES.md | 13 | 12 | ✗ |
| 8052 | vein_tag_review.md | 7 | 234 | ✓ |
| 8990 | T321_REDUNDANCY.md | 5 | 22 | ✓ |
| 9632 | _INDEX_NIGHT.md | 8 | 128 | ✓ |
| 9768 | enemy_table.md | 9 | 199 | ✗ |
| 9907 | vein_effects_by_vein.md | 7 | 233 | ✗ |
| 10093 | event_table.md | 4 | 130 | ✗ |
| 14203 | redesign_notes.md | 4 | 0 | ✓ |
| 15387 | event_rr.md | 4 | 333 | ✗ |
| 16301 | card_intent_reverse.md | 6 | 135 | ✓ |
| 16890 | enemy_card_map.md | 3 | 171 | ✗ |
| 17039 | CARD_EFFECTS_AUTO.md | 5 | 0 | ✗ |
| 22706 | event_info.md | 4 | 316 | ✗ |
| 56265 | vein_audit_matrix.md | 7 | 256 | ✓ |
