# 交付清单核对 · 2026-11-06 夜班全部产出

> 2026-11-06 夜班 · 第三轮任务 3。核对方式：`tools/_delivery_check_1106.py` 逐文件 `os.path.exists` + 行数统计（脚本在本班产出清单上运行，total=49 missing=0）。
> 行数为 UTF-8 文本行（含表格与空行）；「一句话内容」为作者自述，正确性以文件本体为准。
> **TASK_DONE 记录 vs 实际文件**：`_TASKDONE_AUDIT_1106.md` 已核 401 条记录、164 条带可核路径、真缺失 0（两处脚本误报已人工复核）。本清单是它的补充：只覆盖 2026-11-06 本班产出，按批次归类。

## 一、主任务（T-ANM · 维护者附属卡，8+1 文件）

| 文件 | 行数 | 一句话内容 | 归属 |
|---|---|---|---|
| docs/design/anmin_minions/00_README.md | 59 | 设计主张 + 目录 + 合规自查 | 主任务 |
| docs/design/anmin_minions/01_audit.md | 120 | 54 张逐张判定（保留27/改9/删18）+ 退场前提 | 主任务 |
| docs/design/anmin_minions/02_cards_A_growth.md | 233 | 支柱 A 局外成长 8 张（含 JSON 块） | 主任务 |
| docs/design/anmin_minions/03_cards_B_buffs.md | 213 | 支柱 B 自身加成 8 张（荆棘小体系） | 主任务 |
| docs/design/anmin_minions/04_cards_C_parts.md | 218 | 支柱 C 零件经济 8 张（三档汇率） | 主任务 |
| docs/design/anmin_minions/05_curves.md | 130 | 零件收支静态汇率表 + mech_grow 冲突矩阵 | 主任务 |
| docs/design/anmin_minions/06_needs.md | 66 | 4 条新 code 提案 + 0052/0053 需求 + 引擎语义待确认 | 主任务 |
| docs/design/anmin_minions/cards_draft.json | 549 | 24 张新卡数据（可直接被脚本吃） | 主任务 |
| docs/design/anmin_minions/07_paper_test.md | 99 | 24 卡纸上推演：三支柱回合线 + 准循环检查 | 第二批4 |

## 二、方向池（12 个方向）

| 文件 | 行数 | 一句话内容 | 归属 |
|---|---|---|---|
| docs/design/enemies/L1_L3_rework.md | 240 | L1–L3 倒吊重做（17 条 + 退场复核撤销 3 条） | 方向1+第二批1 |
| docs/design/enemies/L4_L8.md | 332 | L4–L8 更亮更红更少眼睛（28 条 + 退场复核撤销 4 条） | 方向2+第二批1 |
| docs/design/enemies/battle_lines.md | 175 | 113 只敌人 × 攻/受/亡 台词 | 第二轮R1 |
| docs/design/enemies/_roster_full.tmp.md | 113 | 全量 roster 原文转存 | R1 素材 |
| docs/design/events/new_events_20.md | 463 | 20 个新事件（引擎格式 JSON 块） | 方向3 |
| docs/design/relics/new_relics_24.md | 192 | 24 个新遗物（四组各 6） | 方向4 |
| docs/design/layers/scene_depth1.md ～ scene_depth8.md | 29/29/29/29/27/29/29/31 | 八层场景文（每篇 600–900 字） | 方向5 |
| docs/design/layers/sound_design.md | 115 | 八层声音规格 + 缺口清单 6 条 | 第二轮R4 |
| docs/design/copy/flavor_audit.md | 227 | flavor AI 味审查 40 条 + 特征 8 条 | 方向6 |
| docs/design/copy/name_audit.md | 88 | 卡名审查 11 条 + 特征 6 条 | 第二轮R2 |
| docs/design/copy/_flavor_dump.tmp.md | 236 | 226 张 flavor 全量转存 | 方向6 素材 |
| docs/design/glossary_audit.md | 131 | 术语一致性 15 条 + 排除项 10 组 | 方向7 |
| docs/design/endings/ten_endings.md | 183 | 10 个结局（300–500 字逐条达标） | 方向8 |
| docs/design/tutorial/first_3_battles.md | 78 | 前 3 场引导文案（17 条 ≤25 字） | 方向9 |
| docs/design/shops/shop_and_recycle.md | 92 | 掌柜背景 + 40 条台词（状态分组） | 方向10 |
| docs/design/classes/opening.md | 78 | 四职业开局体验 | 方向11 |
| docs/design/curves/curve_report_auto.md | 82 | 曲线审计脚本产出（128 样本/48 离群） | 方向12 |
| docs/design/curves/curve_report.md | 87 | 曲线分析（三色分拣 + 净改 4 张） | 方向12 |
| docs/design/curves/_triage.tmp.md | 51 | 48 条三色分拣名单 | 方向12 素材 |

## 三、第二轮 + 兜底 + 第三轮

| 文件 | 行数 | 一句话内容 | 归属 |
|---|---|---|---|
| docs/design/curves/parts_economy_auto.md | 37 | 零件经济蒙特卡洛产出（3 场景×2 策略） | 第二轮R3 |
| docs/design/curves/parts_economy.md | 45 | 经济模拟分析（random 净存中位 1 的发现） | 第二轮R3 |
| docs/design/_CONFLICTS_1106.md | 89 | 文档矛盾清单 12 条 | 兜底1 |
| docs/design/_TASKDONE_AUDIT_1106.md | 30 | TASK_DONE 401 条存在性审计（缺失 0） | 兜底2 |
| docs/design/_INDEX_1106.md | 490 | docs/design 362 个 md 索引 + 权威地图 | 兜底3 |
| docs/design/_NEWCOMER_PATH.md | 82 | 新人路线图（7 节 + 7 坑 + 6 题自测） | 兜底4 |
| docs/design/_STALE_NUMBERS_1106.md | 35 | 「219/53」8 文件逐个判定 | 第二批2 |
| docs/design/_CROSSCHECK_1106.md | 80 | 五批新内容交叉检查 10 项 | 第二批3 |
| docs/design/_SELFAUDIT_1106.md | 45 | 15 条结论回验（成立12/不成立2/无法验证1） | 第三轮1 |
| docs/design/_DECISIONS_1106.md | 47 | 明早决策清单 14 条（P0/P1/P2） | 第三轮2 |

## 四、脚本（4 个，全部只读数据、只写 docs/）

| 文件 | 行数 | 一句话内容 | 归属 |
|---|---|---|---|
| tools/_curve_audit_1106.py | 128 | 卡牌伤/挡曲线审计（分档+分稀有度中位数） | 方向12 |
| tools/_parts_economy_1106.py | 173 | 零件经济蒙特卡洛（双策略夹逼、固定种子） | 第二轮R3 |
| tools/_taskdone_audit_1106.py | 75 | TASK_DONE 存在性核验 | 兜底2 |
| tools/_design_index_1106.py | 78 | docs/design 索引生成 | 兜底3 |

## 五、「说写了但不存在」专项

**0 条。** 两层核验都干净：
1. 全历史层：`_TASKDONE_AUDIT_1106.md` 核 401 条记录的 164 条带路径条目，真缺失 0（2 处脚本误报已人工复核：区间简写、data/ 前缀漏白名单）。
2. 本班层：本清单 49 个文件 `total=49 missing=0`。

## 六、数字小记

- 交付文件 49 个（文档 45 + 脚本 4），总行数约 **4,900 行**。
- TASK_DONE 本班累计追加 **26 条**（主任务 1 + 方向 12 + 收工 1 + 第二批 4 + 第三轮 3 + 更正 3 + 各批内记录）——以文件尾部实际为准。
- 未计入本清单：TASK_DONE.md 的追加（属记录不属于产出）、`_INDEX_1106.md` 索引到的历史文件。
