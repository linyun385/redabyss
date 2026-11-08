# ART_LINK_AUDIT — T68 素材接线体检（catalog↔文件↔web 三方对账）

- 生成：2026-11-04 03:02　脚本：`tools/_audit_art_links.py`（可重跑刷新本报告）
- 性质：**只读体检**。未改动 `web/`、`web/assets/art/`、`data/`；发现断链只记录不修。

## 一、三方数量

| 登记 | 数量 |
|---|---|
| data/art_catalog.json id | 461（含重复 0，实际唯一 461） |
| web/assets/art/*.webp | 610 |
| web/index.html ART 表 key | 552 |

差额定性：文件 610 = catalog 461（**全部有文件**）+ ART 表 543（**全部有文件**）+ 未登记文件 67。

## 二、判定口径（宁可宽判不误报）

1. **引用判定**：id 字符串出现在 `web/index.html` 的 ART 表段**或**正文任意位置，或出现在任一现行 web 文本文件（`web/**/*.{html,js,css}`，排除 `assets/`、`sfx/` 与 `*.bak*`/`*.corrupt`/`*.recovered` 备份），即算「有引用」。只做子串判定，不解析语法。
2. **断链定义**：登记/引用侧要求某 id 可用而文件缺位，或 ART 表值路径错位 —— 会造成运行时空卡面。
3. **不算断链的两类**（只记录）：① 文件存在但三方均无登记（多余文件）；② catalog id 无字面引用 —— 运行时经 `cardArtId(card)` / 敌人 `foe_<eco>_<n>` 派生 id 查 ART 表，catalog id 本身不进运行时查表，属生成侧登记，需人工判断是否登记漂移。
4. **范围**：对账以现行 `web/index.html` 为准；catalog 重复 id、ART 表值路径约定 `assets/art/<key>.webp`（`data:` URI 内联亦通过）一并核查。

## 三、断链清单（登记↔文件）

| 类别 | 条数 | 明细 |
|---|---|---|
| catalog 有 id、无文件 | 0 | — |
| ART 表有 key、无文件 | 9 | anmin_sign、basic_atk、basic_def、cng_d_atk、cng_d_def、cng_w_atk、cng_w_def、diver_sign、tremor_sign |
| ART 表值路径错位 | 9 | anmin_sign 值 assets/art/sym_sign.webp ≠ 约定 assets/art/anmin_sign.webp；basic_atk 值 assets/art/sym_atk.webp ≠ 约定 assets/art/basic_atk.webp；basic_def 值 assets/art/sym_def.webp ≠ 约定 assets/art/basic_def.webp；cng_d_atk 值 assets/art/sym_atk.webp ≠ 约定 assets/art/cng_d_atk.webp；cng_d_def 值 assets/art/sym_def.webp ≠ 约定 assets/art/cng_d_def.webp；cng_w_atk 值 assets/art/sym_atk.webp ≠ 约定 assets/art/cng_w_atk.webp；cng_w_def 值 assets/art/sym_def.webp ≠ 约定 assets/art/cng_w_def.webp；diver_sign 值 assets/art/sym_sign.webp ≠ 约定 assets/art/diver_sign.webp；tremor_sign 值 assets/art/sym_sign.webp ≠ 约定 assets/art/tremor_sign.webp |
| catalog 重复 id | 0 | — |

**断链率：18 / 552 登记位 = 3.3%**

## 四、多余清单（文件无任何登记）

共 67 个文件不在 catalog 也不在 ART 表，且无任何现行 web 文本字面引用（无人认领，仅记录不清理）：

- `foe_zh2_*` ×10：`foe_zh2_cave_amphibian`、`foe_zh2_eyeless_eel`、`foe_zh2_gap_mite`、`foe_zh2_jumping_spider`、`foe_zh2_lungfish`、`foe_zh2_moss_mat`、`foe_zh2_salt_formation`、`foe_zh2_saprophyte`、`foe_zh2_thermophile`、`foe_zh2_waste_crab`
- `foe_zh3_*` ×10：`foe_zh3_cave_amphibian`、`foe_zh3_eyeless_eel`、`foe_zh3_gap_mite`、`foe_zh3_jumping_spider`、`foe_zh3_lungfish`、`foe_zh3_moss_mat`、`foe_zh3_salt_formation`、`foe_zh3_saprophyte`、`foe_zh3_thermophile`、`foe_zh3_waste_crab`
- `foe_zh3b_*` ×10：`foe_zh3b_cave_amphibian`、`foe_zh3b_eyeless_eel`、`foe_zh3b_gap_mite`、`foe_zh3b_jumping_spider`、`foe_zh3b_lungfish`、`foe_zh3b_moss_mat`、`foe_zh3b_salt_formation`、`foe_zh3b_saprophyte`、`foe_zh3b_thermophile`、`foe_zh3b_waste_crab`
- `card_zh2_*` ×6：`card_zh2_battery_lamp`、`card_zh2_energy_gun`、`card_zh2_inspection_board`、`card_zh2_noose_rope`、`card_zh2_oxygen_rig`、`card_zh2_tremor_meter`
- `card_zh3_*` ×6：`card_zh3_battery_lamp`、`card_zh3_energy_gun`、`card_zh3_inspection_board`、`card_zh3_noose_rope`、`card_zh3_oxygen_rig`、`card_zh3_tremor_meter`
- `card_zh3b_*` ×6：`card_zh3b_battery_lamp`、`card_zh3b_energy_gun`、`card_zh3b_inspection_board`、`card_zh3b_noose_rope`、`card_zh3b_oxygen_rig`、`card_zh3b_tremor_meter`
- `evt_zh2_*` ×4：`evt_zh2_body_in_suit`、`evt_zh2_red_fern`、`evt_zh2_rubble`、`evt_zh2_self_switch_lamp`
- `evt_zh3_*` ×4：`evt_zh3_body_in_suit`、`evt_zh3_red_fern`、`evt_zh3_rubble`、`evt_zh3_self_switch_lamp`
- `evt_zh3b_*` ×4：`evt_zh3b_body_in_suit`、`evt_zh3b_red_fern`、`evt_zh3b_rubble`、`evt_zh3b_self_switch_lamp`
- `foe_zh_*` ×4：`foe_zh_eyeless_eel`、`foe_zh_salt_column`、`foe_zh_thermophile`、`foe_zh_waste_crab`
- `anm`：`anm_0011.old`
- `card_zh`：`card_zh_inspection_board`
- `evt_zh`：`evt_zh_body_in_suit`

## 五、引用覆盖（catalog → web，宽判）

- catalog 461 个 id 中 461 个在 web 现行文本有字面出现（多为内嵌卡牌/敌人/事件数据）。
- 无字面引用 0 个（文件均在，非断链；逐条列出供人工判断登记漂移）：

- 仅在 ART 表段出现、正文没有：dive_0081、dive_0082、dive_0083、trem_0081、trem_0082、trem_0083
- ART 表 79 个运行时 id（face_eco_*/foe_eco_*/class_*/end_ending_*）与 catalog **零交集**，属两套命名体系：web 侧走派生 id，catalog 是生成侧目录；此为 T67 接线的设计现状，非缺陷。

## 六、结论

**断链率 3.3%（18 条），需按上表逐条修复后复跑本脚本归零。**
