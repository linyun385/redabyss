# DUP_GROUPS · 雷同分组与保留/重画建议（T267）

## 结论（5 行）

1. 461 张图 dHash（8×8，阈值 0.90）两两比对：**109 对超阈、成 6 组**；其中相似度 ≥0.95 的「近孪生对」**8 对**，是真正要处理的对象。
2. 组 1 是 48 张的暗红基调聚堆（全池 P50 red=0.333 / luma=20.1，组内成员全都贴着基线）——dHash 8×8 只看明度梯度，它反映的是**基调趋同**，不是主体雷同；按 near_black 与极端度排序后建议重画 9 张、复核 21 张，不必整组处理。
3. 6 组合计建议：**保留 20 / 重画 15 / 复核 24 / 已在 T335 删卡清单 4**（trem_0036、trem_0041、trem_0062、dive_0072、dive_0074、trem_0082 中 4 张在删卡内，随 T340 施工自然消化，不投入重画）。
4. 重画优先级第一梯 = 相似度 1.00 的 8 对成员（hist 分桶 `1.0` 有 8 对，近似逐像素相同）；这 8 对的全部成员已在组表标 redo。
5. 全部结论可复算：`python tools/dup_groups.py`（读 dups.json / qa_auto.json / stat_tone.json / rewrite 清单 / T335_PRUNE.csv），两次运行逐字节一致。

## 分组表

### 组 1（48 张，基调聚堆）

keep 15：anm_0003、anm_0014、anm_0017、cng_0050、dive_0028、dive_0066 等（keep_score = |red−P50|+|luma−P50| 最低的 1/3）。
redo 9：cng_0001、cng_0045、dive_0007、event_d3_8、event_d4_8、event_d5_3 等（≥0.95 对成员 + 组内最极端者）。
review 21：anm_0008、anm_0040、cng_0002、dive_0016、dive_0035、enemy_d4_b1 等（中间带，人工抽检 10%）。
pruned 3：trem_0036、trem_0041、trem_0062（已在 T335_PRUNE.csv）。

### 组 2（9 张）

keep 3：enemy_d3_08、enemy_d5_06、trem_0024。
redo 3：enemy_d8_03、event_d2_10、event_d2_6（全部落在 ≥0.95 对上）。
review 3：anm_0013、enemy_d7_e3、event_d7_2。

### 组 3-6（各 2 张）

| 组 | keep | redo | 备注 |
|---|---|---|---|
| 3 | event_d6_11 | anm_0044 | sim 0.9x，两者均不在删卡清单 |
| 4 | —（成员之一被删） | anm_0041 | dive_0072 在 T335 删卡内，重画任务归零，只处理 anm_0041 |
| 5 | dive_0063 | cng_0047 | — |
| 6 | —（成员之一被删） | trem_0082 | dive_0074 在 T335 删卡内 |

## 口径与复算

```powershell
python tools/dup_finder.py     # 基础数据（已有 data/dups.json，重跑应得同分布）
python tools/dup_groups.py     # 本表与 data/dup_groups.json
```

- keep_score = |red_ratio − 全池P50| + |luma − 全池P50| + 2×near_black；P50 取自 `data/stat_tone.json` 的全池口径（red 0.333 / luma 20.1）。
- 组内升序排，前 ⌈n/3⌉ 为 keep；≥0.95 相似对的成员强制 redo；T335_PRUNE.csv 内的 id 标 pruned（重画投入归零，随删卡施工消失）。
- 两次运行 diff 为空（2026-11-04 已验证）。

## 口径注记

1. dHash 8×8 只有 64 位，看到的是明度梯度不是主体形状——组 1 的 48 张「雷同」实为暗红基调趋同，**不能**据此断定主体画面重复；主体级判断归 QA 人工复核（review 列的存在理由）。
2. hist 分桶里 `1.0` 桶有 8 对——这 8 对是逐像素级近似，重画优先级最高；`0.9` 桶 984 对未到阈值不进本表。
3. 与 rewrite 清单（147 条）的关系：redo 成员若同时在 rewrite 清单内，重画前应先按 rewrite 后的新提示词执行（jobs 链路），避免旧词重画。
