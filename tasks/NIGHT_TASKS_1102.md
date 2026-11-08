# 今晚任务清单（2026-11-02 23:00 → 11-03 09:00）

> 共 0 条。**做不完是正常的**，按顺序往下做，不要跳着挑简单的做。

> 共 200 条。**做不完是正常的**，按顺序往下做，不要跳着挑简单的做。

## 现状（脚本从磁盘算出来的，不是估计）

| 项 | 数 |
|---|---|
| 素材总数 | 461 |
| 已有图 | 461 |
| 缺图 | 0 |
| 待按规则重写的提示词 | 150 |
| 提示词里仍有高风险词的条目 | 105 |

## A 段 · 逐张图质检（每 20 张一组，产出 Markdown 台账）

每组做法：对每组每张图，打开 `web/assets/art/<id>.webp` 看，逐条判：
① 画面里有没有可读文字；② 有没有现代电器外形（屏幕/按钮/收音机/音响）；
③ 有没有白画框或边框；④ 主体是否占画面中部三分之二；⑤ 有没有明显偏绿/偏蓝；
⑥ 像不像纸/书/册；⑦ 一句话说主体是什么。

产出：`data/qa/QA_<组号>.md`，表格一行一张，末尾写「本组不合格：id, id …」。

（47 组，见下方任务条目）

## B 段 · 待重写提示词（每 10 条一组）

规则（必须照做，不许自创）：
- 只改「主体段」（`洞底是一整片深红的光` 之前的部分），尾部光照/画法段原样保留
- 主体只能是：厚铁皮铆成的方斗 / 铸成的铁管 / 铸成整块的铁盖板 / 粗陶罐 / 骨管 / 铁链挂钩
- 必须写工艺痕迹：锈穿的洞、歪斜的焊缝、砸扁的边角、铆钉头、锈水淌地
- 不许出现：装置 设备 仪器 开关 仪表 面板 屏幕 机器 编号 标签 刻度 刻字 铭文 字
- 必须写镜头位置（贴地仰视 / 斜俯 / 斜侧），平面物体一律斜放
- 80–140 字，一段，不分行
- 事件卡额外要求：任何牌子/告示 → 写成「一块被反复划过的铁面」，画面里不出现可读的字

产出：`data/rewrite/RW_<组号>.json`，格式 `[{"id":"...","prompt":"<主体段>"}]`（只写主体段）

（30 组）

## C 段 · 高风险词清理报告

把上面「提示词里仍有高风险词的条目」逐条读主体段，判断这个词是**真风险**还是误报（例如「铁片」里的片不算），产出 `data/risky_audit.md`：一条一行，写 id / 命中词 / 判定（改/不改）/ 理由。

（4 组）

## D 段 · 图鉴文案（每 20 条一组，纯写作，最耗时间的一段）

每条写三段，共 120–180 字：
① 画面里实际画了什么（看 `web/assets/art/<id>.webp`，照实写，不许编）
② 它在这个世界里的用途/来历（查 `data/art_catalog.json` 的 name/desc）
③ 为什么这样画（对应世界规则：红光从地底升、万物倒挂、取食器官长在下侧）

产出：`data/lore/LORE_<组号>.md`，每条一节，标题 `## <id> <卡名>`

（47 组）

## E 段 · 工具化（写脚本，以后每晚都能复用）

## F 段 · 游戏本体（T 系列剩下的）

（11 条）

## G 段 · 回归与健壮性

## H 段 · 统计与分析（把主观判断变成数字）

## I 段 · 文案（纯写作，这一段最容易耗时间）

为什么写：游戏里卡面要一句副标题、敌人图鉴要一句战斗台词、事件卡要一句开场句。
现在 `desc` 只有一行，太单薄。

统一要求：每条 20–35 字，一句，不分行，不用感叹号堆砌，语气要冷、像记录不像宣传。
不许和 `desc` 原文重复，要往前推一步（写后果、写来源、写它对人做了什么）。

（卡牌 14 组 / 敌人 6 组 / 事件 5 组）

## J 段 · 第二轮复检（换一套判据，专挑第一轮放过的）

第一轮看的是「有没有违规物件」。这一轮看三件第一轮不看的事：
① 材质读得出来吗（是铁、是陶、是骨，还是「一坨红色」）；
② 厚度与透视对不对（有没有被红光糊成一块平板）；
③ 和卡名对不对得上（名字说的和画面画的是不是冤家）。
每条给 1–5 分 + 一句理由。产出：`data/qa2/QA2_<组号>.md`

（12 组，先做前 120 张；做完再按「自我扩写」往后扩）

## I 段 · 自繁殖（这一段最重要，永远不许空转）

做完上面任何一段的 10 条，就回到这一段做一次「滚动检查」，然后再回去继续。

## 任务条目

### N001 图质检 第 01 组（10 张）
输入：`web/assets/art/<id>.webp`
产出：`data/qa/QA_001.md`
本组 id：
```
enemy_d1_01 enemy_d1_02 enemy_d2_01 enemy_d2_02 enemy_d2_03 enemy_d2_04 enemy_d2_05 enemy_d3_01 enemy_d3_02 enemy_d3_03
```

### N002 图质检 第 02 组（10 张）
输入：`web/assets/art/<id>.webp`
产出：`data/qa/QA_002.md`
本组 id：
```
enemy_d3_04 enemy_d3_05 enemy_d4_01 enemy_d4_02 enemy_d4_03 enemy_d4_04 enemy_d4_05 enemy_d4_06 enemy_d5_01 enemy_d5_02
```

### N003 图质检 第 03 组（10 张）
输入：`web/assets/art/<id>.webp`
产出：`data/qa/QA_003.md`
本组 id：
```
enemy_d5_03 enemy_d5_04 enemy_d5_05 enemy_d5_06 enemy_d6_01 enemy_d6_02 enemy_d6_03 enemy_d6_04 enemy_d6_05 enemy_d7_01
```

### N004 图质检 第 04 组（10 张）
输入：`web/assets/art/<id>.webp`
产出：`data/qa/QA_004.md`
本组 id：
```
enemy_d7_02 enemy_d7_03 enemy_d7_04 enemy_d7_05 enemy_d7_06 enemy_d8_01 enemy_d8_02 enemy_d8_03 enemy_d1_03 enemy_d1_04
```

### N005 图质检 第 05 组（10 张）
输入：`web/assets/art/<id>.webp`
产出：`data/qa/QA_005.md`
本组 id：
```
enemy_d2_06 enemy_d2_07 enemy_d3_06 enemy_d3_07 enemy_d4_07 enemy_d4_08 enemy_d5_07 enemy_d5_08 enemy_d6_06 enemy_d6_07
```

### N006 图质检 第 06 组（10 张）
输入：`web/assets/art/<id>.webp`
产出：`data/qa/QA_006.md`
本组 id：
```
enemy_d7_07 enemy_d7_08 enemy_d8_04 enemy_d8_05 enemy_d1_05 enemy_d8_06 enemy_d1_e1 enemy_d1_e2 enemy_d1_b1 enemy_d2_e1
```

### N007 图质检 第 07 组（10 张）
输入：`web/assets/art/<id>.webp`
产出：`data/qa/QA_007.md`
本组 id：
```
enemy_d2_e2 enemy_d2_b1 enemy_d3_e1 enemy_d3_e2 enemy_d3_b1 enemy_d4_e1 enemy_d4_e2 enemy_d4_b1 enemy_d5_e1 enemy_d5_e2
```

### N008 图质检 第 08 组（10 张）
输入：`web/assets/art/<id>.webp`
产出：`data/qa/QA_008.md`
本组 id：
```
enemy_d5_b1 enemy_d6_e1 enemy_d6_e2 enemy_d6_b1 enemy_d7_e1 enemy_d7_e2 enemy_d7_b1 enemy_d8_e1 enemy_d8_e2 enemy_d8_b1
```

### N009 图质检 第 09 组（10 张）
输入：`web/assets/art/<id>.webp`
产出：`data/qa/QA_009.md`
本组 id：
```
enemy_d1_06 enemy_d1_07 enemy_d1_08 enemy_d1_e3 enemy_d1_e4 enemy_d1_b2 enemy_d2_08 enemy_d2_09 enemy_d2_e3 enemy_d2_b2
```

### N010 图质检 第 10 组（10 张）
输入：`web/assets/art/<id>.webp`
产出：`data/qa/QA_010.md`
本组 id：
```
enemy_d3_08 enemy_d3_09 enemy_d3_e3 enemy_d3_b2 enemy_d4_09 enemy_d4_10 enemy_d4_e3 enemy_d5_09 enemy_d5_10 enemy_d5_e3
```

### N011 图质检 第 11 组（10 张）
输入：`web/assets/art/<id>.webp`
产出：`data/qa/QA_011.md`
本组 id：
```
enemy_d6_08 enemy_d6_09 enemy_d6_e3 enemy_d6_b2 enemy_d7_09 enemy_d7_10 enemy_d7_e3 enemy_d8_07 enemy_d8_08 enemy_d8_09
```

### N012 图质检 第 12 组（10 张）
输入：`web/assets/art/<id>.webp`
产出：`data/qa/QA_012.md`
本组 id：
```
enemy_d8_10 enemy_d8_11 enemy_d8_12 event_d2_1 event_d2_2 event_d3_1 event_d3_2 event_d4_1 event_d4_2 event_d5_1
```

### N013 图质检 第 13 组（10 张）
输入：`web/assets/art/<id>.webp`
产出：`data/qa/QA_013.md`
本组 id：
```
event_d5_2 event_d6_1 event_d6_2 event_d7_1 event_d7_2 event_d2_3 event_d2_4 event_d3_3 event_d3_4 event_d4_3
```

### N014 图质检 第 14 组（10 张）
输入：`web/assets/art/<id>.webp`
产出：`data/qa/QA_014.md`
本组 id：
```
event_d4_4 event_d5_3 event_d5_4 event_d6_3 event_d6_4 event_d7_3 event_d7_4 event_d2_5 event_d2_6 event_d3_5
```

### N015 图质检 第 15 组（10 张）
输入：`web/assets/art/<id>.webp`
产出：`data/qa/QA_015.md`
本组 id：
```
event_d3_6 event_d4_5 event_d4_6 event_d5_6 event_d5_7 event_d6_5 event_d6_6 event_d7_5 event_d7_6 event_d2_7
```

### N016 图质检 第 16 组（10 张）
输入：`web/assets/art/<id>.webp`
产出：`data/qa/QA_016.md`
本组 id：
```
event_d3_7 event_d4_7 event_d5_8 event_d6_7 event_d7_7 event_d2_8 event_d3_8 event_d4_8 event_d5_9 event_d6_8
```

### N017 图质检 第 17 组（10 张）
输入：`web/assets/art/<id>.webp`
产出：`data/qa/QA_017.md`
本组 id：
```
event_d7_8 event_d1_1 event_d1_2 event_d1_3 event_d2_9 event_d2_10 event_d2_11 event_d3_9 event_d3_10 event_d3_11
```

### N018 图质检 第 18 组（10 张）
输入：`web/assets/art/<id>.webp`
产出：`data/qa/QA_018.md`
本组 id：
```
event_d4_9 event_d4_10 event_d4_11 event_d5_10 event_d5_11 event_d5_12 event_d6_9 event_d6_10 event_d6_11 event_d7_9
```

### N019 图质检 第 19 组（10 张）
输入：`web/assets/art/<id>.webp`
产出：`data/qa/QA_019.md`
本组 id：
```
event_d7_10 event_d7_11 event_d8_1 event_d8_2 event_d8_3 event_d1_4 event_d1_5 event_d1_6 event_d1_7 event_d1_8
```

### N020 图质检 第 20 组（10 张）
输入：`web/assets/art/<id>.webp`
产出：`data/qa/QA_020.md`
本组 id：
```
event_d8_4 event_d8_5 event_d8_6 event_d8_7 event_d8_8 anm_0001 anm_0002 anm_0003 anm_0004 anm_0005
```

### N021 图质检 第 21 组（10 张）
输入：`web/assets/art/<id>.webp`
产出：`data/qa/QA_021.md`
本组 id：
```
anm_0006 anm_0007 anm_0008 anm_0009 anm_0010 anm_0011 anm_0012 anm_0013 anm_0014 anm_0015
```

### N022 图质检 第 22 组（10 张）
输入：`web/assets/art/<id>.webp`
产出：`data/qa/QA_022.md`
本组 id：
```
anm_0016 anm_0017 anm_0018 anm_0019 anm_0020 anm_0021 anm_0022 anm_0023 anm_0024 anm_0025
```

### N023 图质检 第 23 组（10 张）
输入：`web/assets/art/<id>.webp`
产出：`data/qa/QA_023.md`
本组 id：
```
anm_0026 anm_0027 anm_0028 anm_0029 anm_0030 anm_0031 anm_0032 anm_0033 anm_0034 anm_0035
```

### N024 图质检 第 24 组（10 张）
输入：`web/assets/art/<id>.webp`
产出：`data/qa/QA_024.md`
本组 id：
```
anm_0036 anm_0037 anm_0038 anm_0039 anm_0040 anm_0041 anm_0042 anm_0043 anm_0044 anm_0045
```

### N025 图质检 第 25 组（10 张）
输入：`web/assets/art/<id>.webp`
产出：`data/qa/QA_025.md`
本组 id：
```
anm_0046 anm_0047 anm_0048 anm_0049 anm_0050 cng_0001 cng_0002 cng_0003 cng_0004 cng_0005
```

### N026 图质检 第 26 组（10 张）
输入：`web/assets/art/<id>.webp`
产出：`data/qa/QA_026.md`
本组 id：
```
cng_0006 cng_0007 cng_0008 cng_0009 cng_0010 cng_0011 cng_0012 cng_0013 cng_0014 cng_0015
```

### N027 图质检 第 27 组（10 张）
输入：`web/assets/art/<id>.webp`
产出：`data/qa/QA_027.md`
本组 id：
```
cng_0016 cng_0017 cng_0018 cng_0019 cng_0020 cng_0021 cng_0022 cng_0023 cng_0024 cng_0025
```

### N028 图质检 第 28 组（10 张）
输入：`web/assets/art/<id>.webp`
产出：`data/qa/QA_028.md`
本组 id：
```
cng_0026 cng_0027 cng_0028 cng_0029 cng_0030 cng_0031 cng_0032 cng_0033 cng_0034 cng_0035
```

### N029 图质检 第 29 组（10 张）
输入：`web/assets/art/<id>.webp`
产出：`data/qa/QA_029.md`
本组 id：
```
cng_0036 cng_0037 cng_0038 cng_0039 cng_0040 cng_0041 cng_0042 cng_0043 cng_0044 cng_0045
```

### N030 图质检 第 30 组（10 张）
输入：`web/assets/art/<id>.webp`
产出：`data/qa/QA_030.md`
本组 id：
```
cng_0046 cng_0047 cng_0048 cng_0049 cng_0050 dive_0001 dive_0002 dive_0003 dive_0004 dive_0005
```

### N031 图质检 第 31 组（10 张）
输入：`web/assets/art/<id>.webp`
产出：`data/qa/QA_031.md`
本组 id：
```
dive_0006 dive_0007 dive_0008 dive_0009 dive_0010 dive_0011 dive_0012 dive_0013 dive_0014 dive_0015
```

### N032 图质检 第 32 组（10 张）
输入：`web/assets/art/<id>.webp`
产出：`data/qa/QA_032.md`
本组 id：
```
dive_0016 dive_0017 dive_0018 dive_0019 dive_0020 dive_0021 dive_0022 dive_0023 dive_0024 dive_0025
```

### N033 图质检 第 33 组（10 张）
输入：`web/assets/art/<id>.webp`
产出：`data/qa/QA_033.md`
本组 id：
```
dive_0026 dive_0027 dive_0028 dive_0029 dive_0030 dive_0031 dive_0032 dive_0033 dive_0034 dive_0035
```

### N034 图质检 第 34 组（10 张）
输入：`web/assets/art/<id>.webp`
产出：`data/qa/QA_034.md`
本组 id：
```
dive_0036 dive_0037 dive_0038 dive_0039 dive_0040 dive_0041 dive_0042 dive_0043 dive_0044 dive_0045
```

### N035 图质检 第 35 组（10 张）
输入：`web/assets/art/<id>.webp`
产出：`data/qa/QA_035.md`
本组 id：
```
dive_0046 dive_0047 dive_0048 dive_0049 dive_0050 dive_0051 dive_0052 dive_0053 dive_0054 dive_0055
```

### N036 图质检 第 36 组（10 张）
输入：`web/assets/art/<id>.webp`
产出：`data/qa/QA_036.md`
本组 id：
```
dive_0056 dive_0057 dive_0058 dive_0059 dive_0060 dive_0061 dive_0062 dive_0063 dive_0064 dive_0065
```

### N037 图质检 第 37 组（10 张）
输入：`web/assets/art/<id>.webp`
产出：`data/qa/QA_037.md`
本组 id：
```
dive_0066 dive_0067 dive_0068 dive_0069 dive_0070 dive_0071 dive_0072 dive_0073 dive_0074 dive_0075
```

### N038 图质检 第 38 组（10 张）
输入：`web/assets/art/<id>.webp`
产出：`data/qa/QA_038.md`
本组 id：
```
dive_0076 dive_0077 dive_0078 dive_0079 dive_0080 dive_0081 dive_0082 dive_0083 trem_0001 trem_0002
```

### N039 图质检 第 39 组（10 张）
输入：`web/assets/art/<id>.webp`
产出：`data/qa/QA_039.md`
本组 id：
```
trem_0003 trem_0004 trem_0005 trem_0006 trem_0007 trem_0008 trem_0009 trem_0010 trem_0011 trem_0012
```

### N040 图质检 第 40 组（10 张）
输入：`web/assets/art/<id>.webp`
产出：`data/qa/QA_040.md`
本组 id：
```
trem_0013 trem_0014 trem_0015 trem_0016 trem_0017 trem_0018 trem_0019 trem_0020 trem_0021 trem_0022
```

### N041 图质检 第 41 组（10 张）
输入：`web/assets/art/<id>.webp`
产出：`data/qa/QA_041.md`
本组 id：
```
trem_0023 trem_0024 trem_0025 trem_0026 trem_0027 trem_0028 trem_0029 trem_0030 trem_0031 trem_0032
```

### N042 图质检 第 42 组（10 张）
输入：`web/assets/art/<id>.webp`
产出：`data/qa/QA_042.md`
本组 id：
```
trem_0033 trem_0034 trem_0035 trem_0036 trem_0037 trem_0038 trem_0039 trem_0040 trem_0041 trem_0042
```

### N043 图质检 第 43 组（10 张）
输入：`web/assets/art/<id>.webp`
产出：`data/qa/QA_043.md`
本组 id：
```
trem_0043 trem_0044 trem_0045 trem_0046 trem_0047 trem_0048 trem_0049 trem_0050 trem_0051 trem_0052
```

### N044 图质检 第 44 组（10 张）
输入：`web/assets/art/<id>.webp`
产出：`data/qa/QA_044.md`
本组 id：
```
trem_0053 trem_0054 trem_0055 trem_0056 trem_0057 trem_0058 trem_0059 trem_0060 trem_0061 trem_0062
```

### N045 图质检 第 45 组（10 张）
输入：`web/assets/art/<id>.webp`
产出：`data/qa/QA_045.md`
本组 id：
```
trem_0063 trem_0064 trem_0065 trem_0066 trem_0067 trem_0068 trem_0069 trem_0070 trem_0071 trem_0072
```

### N046 图质检 第 46 组（10 张）
输入：`web/assets/art/<id>.webp`
产出：`data/qa/QA_046.md`
本组 id：
```
trem_0073 trem_0074 trem_0075 trem_0076 trem_0077 trem_0078 trem_0079 trem_0080 trem_0081 trem_0082
```

### N047 图质检 第 47 组（1 张）
输入：`web/assets/art/<id>.webp`
产出：`data/qa/QA_047.md`
本组 id：
```
trem_0083
```

### N048 重写提示词 第 01 组（5 条）
输入：`data/zh_prompts_full.json` 里这些 id 的 `prompt`
产出：`data/rewrite/RW_001.json`
id：
```
event_d2_1 event_d3_2 event_d4_1 event_d4_2 event_d5_1
```

### N049 重写提示词 第 02 组（5 条）
输入：`data/zh_prompts_full.json` 里这些 id 的 `prompt`
产出：`data/rewrite/RW_002.json`
id：
```
event_d5_2 event_d6_2 event_d7_1 event_d7_2 event_d2_3
```

### N050 重写提示词 第 03 组（5 条）
输入：`data/zh_prompts_full.json` 里这些 id 的 `prompt`
产出：`data/rewrite/RW_003.json`
id：
```
event_d2_4 event_d3_3 event_d4_3 event_d4_4 event_d5_3
```

### N051 重写提示词 第 04 组（5 条）
输入：`data/zh_prompts_full.json` 里这些 id 的 `prompt`
产出：`data/rewrite/RW_004.json`
id：
```
event_d6_3 event_d6_4 event_d7_3 event_d7_4 event_d3_5
```

### N052 重写提示词 第 05 组（5 条）
输入：`data/zh_prompts_full.json` 里这些 id 的 `prompt`
产出：`data/rewrite/RW_005.json`
id：
```
event_d4_5 event_d4_6 event_d5_6 event_d6_6 event_d7_5
```

### N053 重写提示词 第 06 组（5 条）
输入：`data/zh_prompts_full.json` 里这些 id 的 `prompt`
产出：`data/rewrite/RW_006.json`
id：
```
event_d2_7 event_d3_7 event_d4_7 event_d5_8 event_d6_7
```

### N054 重写提示词 第 07 组（5 条）
输入：`data/zh_prompts_full.json` 里这些 id 的 `prompt`
产出：`data/rewrite/RW_007.json`
id：
```
event_d7_7 event_d2_8 event_d5_9 event_d6_8 event_d7_8
```

### N055 重写提示词 第 08 组（5 条）
输入：`data/zh_prompts_full.json` 里这些 id 的 `prompt`
产出：`data/rewrite/RW_008.json`
id：
```
event_d1_1 event_d1_3 event_d2_10 event_d2_11 event_d3_9
```

### N056 重写提示词 第 09 组（5 条）
输入：`data/zh_prompts_full.json` 里这些 id 的 `prompt`
产出：`data/rewrite/RW_009.json`
id：
```
event_d3_10 event_d3_11 event_d4_9 event_d4_10 event_d4_11
```

### N057 重写提示词 第 10 组（5 条）
输入：`data/zh_prompts_full.json` 里这些 id 的 `prompt`
产出：`data/rewrite/RW_010.json`
id：
```
event_d5_11 event_d5_12 event_d6_9 event_d6_10 event_d6_11
```

### N058 重写提示词 第 11 组（5 条）
输入：`data/zh_prompts_full.json` 里这些 id 的 `prompt`
产出：`data/rewrite/RW_011.json`
id：
```
event_d7_9 event_d7_10 event_d7_11 event_d8_1 event_d8_3
```

### N059 重写提示词 第 12 组（5 条）
输入：`data/zh_prompts_full.json` 里这些 id 的 `prompt`
产出：`data/rewrite/RW_012.json`
id：
```
event_d1_4 event_d1_6 event_d1_8 event_d8_8 anm_0002
```

### N060 重写提示词 第 13 组（5 条）
输入：`data/zh_prompts_full.json` 里这些 id 的 `prompt`
产出：`data/rewrite/RW_013.json`
id：
```
anm_0003 anm_0006 anm_0008 anm_0009 anm_0010
```

### N061 重写提示词 第 14 组（5 条）
输入：`data/zh_prompts_full.json` 里这些 id 的 `prompt`
产出：`data/rewrite/RW_014.json`
id：
```
anm_0013 anm_0014 anm_0015 anm_0017 anm_0018
```

### N062 重写提示词 第 15 组（5 条）
输入：`data/zh_prompts_full.json` 里这些 id 的 `prompt`
产出：`data/rewrite/RW_015.json`
id：
```
anm_0019 anm_0023 anm_0024 anm_0028 anm_0029
```

### N063 重写提示词 第 16 组（5 条）
输入：`data/zh_prompts_full.json` 里这些 id 的 `prompt`
产出：`data/rewrite/RW_016.json`
id：
```
anm_0031 anm_0034 anm_0037 anm_0038 anm_0039
```

### N064 重写提示词 第 17 组（5 条）
输入：`data/zh_prompts_full.json` 里这些 id 的 `prompt`
产出：`data/rewrite/RW_017.json`
id：
```
anm_0041 anm_0044 anm_0045 anm_0046 anm_0047
```

### N065 重写提示词 第 18 组（5 条）
输入：`data/zh_prompts_full.json` 里这些 id 的 `prompt`
产出：`data/rewrite/RW_018.json`
id：
```
cng_0001 cng_0002 cng_0007 cng_0008 cng_0011
```

### N066 重写提示词 第 19 组（5 条）
输入：`data/zh_prompts_full.json` 里这些 id 的 `prompt`
产出：`data/rewrite/RW_019.json`
id：
```
cng_0035 cng_0041 cng_0044 cng_0045 cng_0046
```

### N067 重写提示词 第 20 组（5 条）
输入：`data/zh_prompts_full.json` 里这些 id 的 `prompt`
产出：`data/rewrite/RW_020.json`
id：
```
cng_0049 dive_0001 dive_0003 dive_0004 dive_0006
```

### N068 重写提示词 第 21 组（5 条）
输入：`data/zh_prompts_full.json` 里这些 id 的 `prompt`
产出：`data/rewrite/RW_021.json`
id：
```
dive_0007 dive_0011 dive_0013 dive_0016 dive_0018
```

### N069 重写提示词 第 22 组（5 条）
输入：`data/zh_prompts_full.json` 里这些 id 的 `prompt`
产出：`data/rewrite/RW_022.json`
id：
```
dive_0019 dive_0022 dive_0025 dive_0041 dive_0046
```

### N070 重写提示词 第 23 组（5 条）
输入：`data/zh_prompts_full.json` 里这些 id 的 `prompt`
产出：`data/rewrite/RW_023.json`
id：
```
dive_0047 dive_0049 dive_0050 dive_0054 dive_0057
```

### N071 重写提示词 第 24 组（5 条）
输入：`data/zh_prompts_full.json` 里这些 id 的 `prompt`
产出：`data/rewrite/RW_024.json`
id：
```
dive_0058 dive_0069 dive_0078 dive_0080 trem_0007
```

### N072 重写提示词 第 25 组（5 条）
输入：`data/zh_prompts_full.json` 里这些 id 的 `prompt`
产出：`data/rewrite/RW_025.json`
id：
```
trem_0010 trem_0013 trem_0015 trem_0020 trem_0022
```

### N073 重写提示词 第 26 组（5 条）
输入：`data/zh_prompts_full.json` 里这些 id 的 `prompt`
产出：`data/rewrite/RW_026.json`
id：
```
trem_0024 trem_0026 trem_0027 trem_0028 trem_0029
```

### N074 重写提示词 第 27 组（5 条）
输入：`data/zh_prompts_full.json` 里这些 id 的 `prompt`
产出：`data/rewrite/RW_027.json`
id：
```
trem_0030 trem_0031 trem_0032 trem_0034 trem_0035
```

### N075 重写提示词 第 28 组（5 条）
输入：`data/zh_prompts_full.json` 里这些 id 的 `prompt`
产出：`data/rewrite/RW_028.json`
id：
```
trem_0036 trem_0038 trem_0040 trem_0044 trem_0051
```

### N076 重写提示词 第 29 组（5 条）
输入：`data/zh_prompts_full.json` 里这些 id 的 `prompt`
产出：`data/rewrite/RW_029.json`
id：
```
trem_0052 trem_0053 trem_0054 trem_0056 trem_0058
```

### N077 重写提示词 第 30 组（5 条）
输入：`data/zh_prompts_full.json` 里这些 id 的 `prompt`
产出：`data/rewrite/RW_030.json`
id：
```
trem_0060 trem_0061 trem_0063 trem_0064 trem_0067
```

### N078 风险词审计 第 01 组（30 条）
产出：`data/risky_audit_001.md`
id：
```
enemy_d7_07 enemy_d5_b1 enemy_d8_e1 enemy_d1_e3 enemy_d1_b2 enemy_d2_09 enemy_d6_e3 enemy_d8_07 enemy_d8_10 enemy_d8_11 event_d2_2 event_d5_4 event_d5_7 event_d6_5 event_d3_8 event_d6_11 event_d7_10 event_d1_5 event_d8_7 anm_0002 anm_0003 anm_0004 anm_0006 anm_0008 anm_0009 anm_0010 anm_0013 anm_0014 anm_0015 anm_0017
```

### N079 风险词审计 第 02 组（30 条）
产出：`data/risky_audit_002.md`
id：
```
anm_0018 anm_0019 anm_0020 anm_0022 anm_0023 anm_0024 anm_0025 anm_0026 anm_0028 anm_0029 anm_0031 anm_0032 anm_0033 anm_0034 anm_0035 anm_0036 anm_0037 anm_0038 anm_0039 anm_0040 anm_0041 anm_0042 anm_0044 anm_0045 anm_0046 anm_0047 anm_0048 cng_0001 cng_0002 cng_0003
```

### N080 风险词审计 第 03 组（30 条）
产出：`data/risky_audit_003.md`
id：
```
cng_0006 cng_0007 cng_0008 cng_0009 cng_0010 cng_0011 cng_0012 cng_0014 cng_0016 cng_0017 cng_0019 cng_0021 cng_0023 cng_0024 cng_0028 cng_0030 cng_0031 cng_0032 cng_0033 cng_0035 cng_0036 cng_0039 cng_0040 cng_0041 cng_0043 cng_0044 cng_0045 cng_0046 cng_0047 cng_0049
```

### N081 风险词审计 第 04 组（15 条）
产出：`data/risky_audit_004.md`
id：
```
cng_0050 dive_0003 dive_0017 dive_0039 dive_0041 dive_0046 dive_0061 dive_0064 trem_0006 trem_0012 trem_0018 trem_0054 trem_0064 trem_0070 trem_0078
```

### N082 图鉴文案 第 01 组（10 条）
输入：图 + `data/art_catalog.json`
产出：`data/lore/LORE_001.md`
id：
```
enemy_d1_01 enemy_d1_02 enemy_d2_01 enemy_d2_02 enemy_d2_03 enemy_d2_04 enemy_d2_05 enemy_d3_01 enemy_d3_02 enemy_d3_03
```

### N083 图鉴文案 第 02 组（10 条）
输入：图 + `data/art_catalog.json`
产出：`data/lore/LORE_002.md`
id：
```
enemy_d3_04 enemy_d3_05 enemy_d4_01 enemy_d4_02 enemy_d4_03 enemy_d4_04 enemy_d4_05 enemy_d4_06 enemy_d5_01 enemy_d5_02
```

### N084 图鉴文案 第 03 组（10 条）
输入：图 + `data/art_catalog.json`
产出：`data/lore/LORE_003.md`
id：
```
enemy_d5_03 enemy_d5_04 enemy_d5_05 enemy_d5_06 enemy_d6_01 enemy_d6_02 enemy_d6_03 enemy_d6_04 enemy_d6_05 enemy_d7_01
```

### N085 图鉴文案 第 04 组（10 条）
输入：图 + `data/art_catalog.json`
产出：`data/lore/LORE_004.md`
id：
```
enemy_d7_02 enemy_d7_03 enemy_d7_04 enemy_d7_05 enemy_d7_06 enemy_d8_01 enemy_d8_02 enemy_d8_03 enemy_d1_03 enemy_d1_04
```

### N086 图鉴文案 第 05 组（10 条）
输入：图 + `data/art_catalog.json`
产出：`data/lore/LORE_005.md`
id：
```
enemy_d2_06 enemy_d2_07 enemy_d3_06 enemy_d3_07 enemy_d4_07 enemy_d4_08 enemy_d5_07 enemy_d5_08 enemy_d6_06 enemy_d6_07
```

### N087 图鉴文案 第 06 组（10 条）
输入：图 + `data/art_catalog.json`
产出：`data/lore/LORE_006.md`
id：
```
enemy_d7_07 enemy_d7_08 enemy_d8_04 enemy_d8_05 enemy_d1_05 enemy_d8_06 enemy_d1_e1 enemy_d1_e2 enemy_d1_b1 enemy_d2_e1
```

### N088 图鉴文案 第 07 组（10 条）
输入：图 + `data/art_catalog.json`
产出：`data/lore/LORE_007.md`
id：
```
enemy_d2_e2 enemy_d2_b1 enemy_d3_e1 enemy_d3_e2 enemy_d3_b1 enemy_d4_e1 enemy_d4_e2 enemy_d4_b1 enemy_d5_e1 enemy_d5_e2
```

### N089 图鉴文案 第 08 组（10 条）
输入：图 + `data/art_catalog.json`
产出：`data/lore/LORE_008.md`
id：
```
enemy_d5_b1 enemy_d6_e1 enemy_d6_e2 enemy_d6_b1 enemy_d7_e1 enemy_d7_e2 enemy_d7_b1 enemy_d8_e1 enemy_d8_e2 enemy_d8_b1
```

### N090 图鉴文案 第 09 组（10 条）
输入：图 + `data/art_catalog.json`
产出：`data/lore/LORE_009.md`
id：
```
enemy_d1_06 enemy_d1_07 enemy_d1_08 enemy_d1_e3 enemy_d1_e4 enemy_d1_b2 enemy_d2_08 enemy_d2_09 enemy_d2_e3 enemy_d2_b2
```

### N091 图鉴文案 第 10 组（10 条）
输入：图 + `data/art_catalog.json`
产出：`data/lore/LORE_010.md`
id：
```
enemy_d3_08 enemy_d3_09 enemy_d3_e3 enemy_d3_b2 enemy_d4_09 enemy_d4_10 enemy_d4_e3 enemy_d5_09 enemy_d5_10 enemy_d5_e3
```

### N092 图鉴文案 第 11 组（10 条）
输入：图 + `data/art_catalog.json`
产出：`data/lore/LORE_011.md`
id：
```
enemy_d6_08 enemy_d6_09 enemy_d6_e3 enemy_d6_b2 enemy_d7_09 enemy_d7_10 enemy_d7_e3 enemy_d8_07 enemy_d8_08 enemy_d8_09
```

### N093 图鉴文案 第 12 组（10 条）
输入：图 + `data/art_catalog.json`
产出：`data/lore/LORE_012.md`
id：
```
enemy_d8_10 enemy_d8_11 enemy_d8_12 event_d2_1 event_d2_2 event_d3_1 event_d3_2 event_d4_1 event_d4_2 event_d5_1
```

### N094 图鉴文案 第 13 组（10 条）
输入：图 + `data/art_catalog.json`
产出：`data/lore/LORE_013.md`
id：
```
event_d5_2 event_d6_1 event_d6_2 event_d7_1 event_d7_2 event_d2_3 event_d2_4 event_d3_3 event_d3_4 event_d4_3
```

### N095 图鉴文案 第 14 组（10 条）
输入：图 + `data/art_catalog.json`
产出：`data/lore/LORE_014.md`
id：
```
event_d4_4 event_d5_3 event_d5_4 event_d6_3 event_d6_4 event_d7_3 event_d7_4 event_d2_5 event_d2_6 event_d3_5
```

### N096 图鉴文案 第 15 组（10 条）
输入：图 + `data/art_catalog.json`
产出：`data/lore/LORE_015.md`
id：
```
event_d3_6 event_d4_5 event_d4_6 event_d5_6 event_d5_7 event_d6_5 event_d6_6 event_d7_5 event_d7_6 event_d2_7
```

### N097 图鉴文案 第 16 组（10 条）
输入：图 + `data/art_catalog.json`
产出：`data/lore/LORE_016.md`
id：
```
event_d3_7 event_d4_7 event_d5_8 event_d6_7 event_d7_7 event_d2_8 event_d3_8 event_d4_8 event_d5_9 event_d6_8
```

### N098 图鉴文案 第 17 组（10 条）
输入：图 + `data/art_catalog.json`
产出：`data/lore/LORE_017.md`
id：
```
event_d7_8 event_d1_1 event_d1_2 event_d1_3 event_d2_9 event_d2_10 event_d2_11 event_d3_9 event_d3_10 event_d3_11
```

### N099 图鉴文案 第 18 组（10 条）
输入：图 + `data/art_catalog.json`
产出：`data/lore/LORE_018.md`
id：
```
event_d4_9 event_d4_10 event_d4_11 event_d5_10 event_d5_11 event_d5_12 event_d6_9 event_d6_10 event_d6_11 event_d7_9
```

### N100 图鉴文案 第 19 组（10 条）
输入：图 + `data/art_catalog.json`
产出：`data/lore/LORE_019.md`
id：
```
event_d7_10 event_d7_11 event_d8_1 event_d8_2 event_d8_3 event_d1_4 event_d1_5 event_d1_6 event_d1_7 event_d1_8
```

### N101 图鉴文案 第 20 组（10 条）
输入：图 + `data/art_catalog.json`
产出：`data/lore/LORE_020.md`
id：
```
event_d8_4 event_d8_5 event_d8_6 event_d8_7 event_d8_8 anm_0001 anm_0002 anm_0003 anm_0004 anm_0005
```

### N102 图鉴文案 第 21 组（10 条）
输入：图 + `data/art_catalog.json`
产出：`data/lore/LORE_021.md`
id：
```
anm_0006 anm_0007 anm_0008 anm_0009 anm_0010 anm_0011 anm_0012 anm_0013 anm_0014 anm_0015
```

### N103 图鉴文案 第 22 组（10 条）
输入：图 + `data/art_catalog.json`
产出：`data/lore/LORE_022.md`
id：
```
anm_0016 anm_0017 anm_0018 anm_0019 anm_0020 anm_0021 anm_0022 anm_0023 anm_0024 anm_0025
```

### N104 图鉴文案 第 23 组（10 条）
输入：图 + `data/art_catalog.json`
产出：`data/lore/LORE_023.md`
id：
```
anm_0026 anm_0027 anm_0028 anm_0029 anm_0030 anm_0031 anm_0032 anm_0033 anm_0034 anm_0035
```

### N105 图鉴文案 第 24 组（10 条）
输入：图 + `data/art_catalog.json`
产出：`data/lore/LORE_024.md`
id：
```
anm_0036 anm_0037 anm_0038 anm_0039 anm_0040 anm_0041 anm_0042 anm_0043 anm_0044 anm_0045
```

### N106 图鉴文案 第 25 组（10 条）
输入：图 + `data/art_catalog.json`
产出：`data/lore/LORE_025.md`
id：
```
anm_0046 anm_0047 anm_0048 anm_0049 anm_0050 cng_0001 cng_0002 cng_0003 cng_0004 cng_0005
```

### N107 图鉴文案 第 26 组（10 条）
输入：图 + `data/art_catalog.json`
产出：`data/lore/LORE_026.md`
id：
```
cng_0006 cng_0007 cng_0008 cng_0009 cng_0010 cng_0011 cng_0012 cng_0013 cng_0014 cng_0015
```

### N108 图鉴文案 第 27 组（10 条）
输入：图 + `data/art_catalog.json`
产出：`data/lore/LORE_027.md`
id：
```
cng_0016 cng_0017 cng_0018 cng_0019 cng_0020 cng_0021 cng_0022 cng_0023 cng_0024 cng_0025
```

### N109 图鉴文案 第 28 组（10 条）
输入：图 + `data/art_catalog.json`
产出：`data/lore/LORE_028.md`
id：
```
cng_0026 cng_0027 cng_0028 cng_0029 cng_0030 cng_0031 cng_0032 cng_0033 cng_0034 cng_0035
```

### N110 图鉴文案 第 29 组（10 条）
输入：图 + `data/art_catalog.json`
产出：`data/lore/LORE_029.md`
id：
```
cng_0036 cng_0037 cng_0038 cng_0039 cng_0040 cng_0041 cng_0042 cng_0043 cng_0044 cng_0045
```

### N111 图鉴文案 第 30 组（10 条）
输入：图 + `data/art_catalog.json`
产出：`data/lore/LORE_030.md`
id：
```
cng_0046 cng_0047 cng_0048 cng_0049 cng_0050 dive_0001 dive_0002 dive_0003 dive_0004 dive_0005
```

### N112 图鉴文案 第 31 组（10 条）
输入：图 + `data/art_catalog.json`
产出：`data/lore/LORE_031.md`
id：
```
dive_0006 dive_0007 dive_0008 dive_0009 dive_0010 dive_0011 dive_0012 dive_0013 dive_0014 dive_0015
```

### N113 图鉴文案 第 32 组（10 条）
输入：图 + `data/art_catalog.json`
产出：`data/lore/LORE_032.md`
id：
```
dive_0016 dive_0017 dive_0018 dive_0019 dive_0020 dive_0021 dive_0022 dive_0023 dive_0024 dive_0025
```

### N114 图鉴文案 第 33 组（10 条）
输入：图 + `data/art_catalog.json`
产出：`data/lore/LORE_033.md`
id：
```
dive_0026 dive_0027 dive_0028 dive_0029 dive_0030 dive_0031 dive_0032 dive_0033 dive_0034 dive_0035
```

### N115 图鉴文案 第 34 组（10 条）
输入：图 + `data/art_catalog.json`
产出：`data/lore/LORE_034.md`
id：
```
dive_0036 dive_0037 dive_0038 dive_0039 dive_0040 dive_0041 dive_0042 dive_0043 dive_0044 dive_0045
```

### N116 图鉴文案 第 35 组（10 条）
输入：图 + `data/art_catalog.json`
产出：`data/lore/LORE_035.md`
id：
```
dive_0046 dive_0047 dive_0048 dive_0049 dive_0050 dive_0051 dive_0052 dive_0053 dive_0054 dive_0055
```

### N117 图鉴文案 第 36 组（10 条）
输入：图 + `data/art_catalog.json`
产出：`data/lore/LORE_036.md`
id：
```
dive_0056 dive_0057 dive_0058 dive_0059 dive_0060 dive_0061 dive_0062 dive_0063 dive_0064 dive_0065
```

### N118 图鉴文案 第 37 组（10 条）
输入：图 + `data/art_catalog.json`
产出：`data/lore/LORE_037.md`
id：
```
dive_0066 dive_0067 dive_0068 dive_0069 dive_0070 dive_0071 dive_0072 dive_0073 dive_0074 dive_0075
```

### N119 图鉴文案 第 38 组（10 条）
输入：图 + `data/art_catalog.json`
产出：`data/lore/LORE_038.md`
id：
```
dive_0076 dive_0077 dive_0078 dive_0079 dive_0080 dive_0081 dive_0082 dive_0083 trem_0001 trem_0002
```

### N120 图鉴文案 第 39 组（10 条）
输入：图 + `data/art_catalog.json`
产出：`data/lore/LORE_039.md`
id：
```
trem_0003 trem_0004 trem_0005 trem_0006 trem_0007 trem_0008 trem_0009 trem_0010 trem_0011 trem_0012
```

### N121 图鉴文案 第 40 组（10 条）
输入：图 + `data/art_catalog.json`
产出：`data/lore/LORE_040.md`
id：
```
trem_0013 trem_0014 trem_0015 trem_0016 trem_0017 trem_0018 trem_0019 trem_0020 trem_0021 trem_0022
```

### N122 图鉴文案 第 41 组（10 条）
输入：图 + `data/art_catalog.json`
产出：`data/lore/LORE_041.md`
id：
```
trem_0023 trem_0024 trem_0025 trem_0026 trem_0027 trem_0028 trem_0029 trem_0030 trem_0031 trem_0032
```

### N123 图鉴文案 第 42 组（10 条）
输入：图 + `data/art_catalog.json`
产出：`data/lore/LORE_042.md`
id：
```
trem_0033 trem_0034 trem_0035 trem_0036 trem_0037 trem_0038 trem_0039 trem_0040 trem_0041 trem_0042
```

### N124 图鉴文案 第 43 组（10 条）
输入：图 + `data/art_catalog.json`
产出：`data/lore/LORE_043.md`
id：
```
trem_0043 trem_0044 trem_0045 trem_0046 trem_0047 trem_0048 trem_0049 trem_0050 trem_0051 trem_0052
```

### N125 图鉴文案 第 44 组（10 条）
输入：图 + `data/art_catalog.json`
产出：`data/lore/LORE_044.md`
id：
```
trem_0053 trem_0054 trem_0055 trem_0056 trem_0057 trem_0058 trem_0059 trem_0060 trem_0061 trem_0062
```

### N126 图鉴文案 第 45 组（10 条）
输入：图 + `data/art_catalog.json`
产出：`data/lore/LORE_045.md`
id：
```
trem_0063 trem_0064 trem_0065 trem_0066 trem_0067 trem_0068 trem_0069 trem_0070 trem_0071 trem_0072
```

### N127 图鉴文案 第 46 组（10 条）
输入：图 + `data/art_catalog.json`
产出：`data/lore/LORE_046.md`
id：
```
trem_0073 trem_0074 trem_0075 trem_0076 trem_0077 trem_0078 trem_0079 trem_0080 trem_0081 trem_0082
```

### N128 图鉴文案 第 47 组（1 条）
输入：图 + `data/art_catalog.json`
产出：`data/lore/LORE_047.md`
id：
```
trem_0083
```

### N129 写 `tools/art_qa.py`
要求：批量图质检器：`python tools/art_qa.py --dir web/assets/art --limit 20`，输出每张图的尺寸/红占比/亮度/冷色占比/是否近黑，存 `data/qa_auto.json`。不做主观判断，只做可复算的数字。
约束：只读不写原始素材；输出到 `data/` 或 `docs/`
验收：能跑通，产物真实落盘

### N130 写 `tools/prompt_lint.py`
要求：提示词合规扫描：扫 `data/zh_prompts_full.json`，按规则 VIII/IX/X 的禁用词表逐条报命中，输出 `data/lint.json` + 控制台摘要。
约束：只读不写原始素材；输出到 `data/` 或 `docs/`
验收：能跑通，产物真实落盘

### N131 写 `tools/job_builder.py`
要求：出图任务生成器：读 `data/rewrite/*.json` + `data/qa/*.md` 里判不合格的 id，合成 `data/jobs_night.json`（wanx_gen 能直接吃）。
约束：只读不写原始素材；输出到 `data/` 或 `docs/`
验收：能跑通，产物真实落盘

### N132 写 `tools/artctl.py`
要求：把 build_families / _make_jobs / wanx_gen / art_sync 串成一个入口：`python tools/artctl.py gen card --limit 30`。只做编排，不复制它们的逻辑。
约束：只读不写原始素材；输出到 `data/` 或 `docs/`
验收：能跑通，产物真实落盘

### N133 写 `tools/qa_report.py`
要求：把 `data/qa/*.md` 汇总成一张总表 `data/qa_report.md`：不合格总数、按缺陷类型分布、按卡组分布。
约束：只读不写原始素材；输出到 `data/` 或 `docs/`
验收：能跑通，产物真实落盘

### N134 写 `tools/lore_index.py`
要求：把 `data/lore/*.md` 汇总成一个 `data/lore_index.json`（id → 文案）。
约束：只读不写原始素材；输出到 `data/` 或 `docs/`
验收：能跑通，产物真实落盘

### N135 写 `tools/dup_finder.py`
要求：图重复度：对 461 张算感知哈希，输出相似度 >0.9 的组到 `data/dups.json`。
约束：只读不写原始素材；输出到 `data/` 或 `docs/`
验收：能跑通，产物真实落盘

### N136 写 `tools/art/*.md 索引`
要求：写 `docs/ART_PIPELINE.md`：把今晚所有脚本的用途、参数、产出写清楚，要求后来的人只看这一页就能跑。
约束：只读不写原始素材；输出到 `data/` 或 `docs/`
验收：能跑通，产物真实落盘

### N137 T27：读 `tasks/T27.md` 并严格照做
做完跑 `node tools/check_web.js`，通过后写进 `TASK_DONE.md`

### N138 T28：读 `tasks/T28.md` 并严格照做
做完跑 `node tools/check_web.js`，通过后写进 `TASK_DONE.md`

### N139 T29：读 `tasks/T29.md` 并严格照做
做完跑 `node tools/check_web.js`，通过后写进 `TASK_DONE.md`

### N140 T30：读 `tasks/T30.md` 并严格照做
做完跑 `node tools/check_web.js`，通过后写进 `TASK_DONE.md`

### N141 T31：读 `tasks/T31.md` 并严格照做
做完跑 `node tools/check_web.js`，通过后写进 `TASK_DONE.md`

### N142 T32：读 `tasks/T32.md` 并严格照做
做完跑 `node tools/check_web.js`，通过后写进 `TASK_DONE.md`

### N143 T33：读 `tasks/T33.md` 并严格照做
做完跑 `node tools/check_web.js`，通过后写进 `TASK_DONE.md`

### N144 T34：读 `tasks/T34.md` 并严格照做
做完跑 `node tools/check_web.js`，通过后写进 `TASK_DONE.md`

### N145 T68：先补任务书再做
`tasks/T68.md` 不存在。先按游戏当前状态写一份任务书，再照做，写进 `TASK_DONE.md` 时注明「任务书为本夜补写」

### N146 T79：读 `tasks/T79.md` 并严格照做
做完跑 `node tools/check_web.js`，通过后写进 `TASK_DONE.md`

### N147 T81：读 `tasks/T81.md` 并严格照做
做完跑 `node tools/check_web.js`，通过后写进 `TASK_DONE.md`

### N148 全量回归
要求：依次跑 `node tools/check_web.js` / `node tools/test_engine.js` / `node tools/pack_check.js all` / `node tools/sim.js --class diver --runs 300`，把每条的输出落盘到 `data/regress/`，失败的**逐个修**，修完复跑。
产出必须落盘，不许只在对话里说

### N149 存档健壮性
要求：写 `tools/_save_stress.js`：连续存/读 200 次、在中途塞入损坏 JSON、在空存档上读，验证不崩且有兜底。产出 `data/regress/save.md`。
产出必须落盘，不许只在对话里说

### N150 小分辨率适配
要求：把 `web/index.html` 在 1024×640 / 1280×720 / 1920×1080 三档下检查布局（可用 `tools/check_web.js` 的现有能力，或写一个纯文本断点审查），产出 `docs/LAYOUT_AUDIT.md` 列出会溢出的元素。
产出必须落盘，不许只在对话里说

### N151 首屏体积
要求：统计 `web/index.html` + 首屏必需素材的字节数，找出 >200KB 的单项，产出 `docs/PERF.md` 并给三条可行优化（不必实施）。
产出必须落盘，不许只在对话里说

### N152 异常路径
要求：列出玩家可能触发的 20 个异常操作（连点、空手牌、0 血、满手牌、退出重进…），逐个在 `web/index.html` 里找对应处理，缺的记下来，产出 `docs/EDGE_CASES.md`。
产出必须落盘，不许只在对话里说

### N153 色调分布
要求：统计 461 张的 R/G/B 均值与红占比分位数，产出 `data/stat_tone.json` + 一段结论（哪一段偏暗/偏暖，按 anm/cng/dive/trem/event/enemy 分组）。
数字必须可复算，脚本一起交

### N154 雷同分组
要求：用 `tools/dup_finder.py` 的结果，把相似度高的图按组列出，产出 `docs/DUP_GROUPS.md`，并给「哪一张保留、哪几张要重画」的建议。
数字必须可复算，脚本一起交

### N155 母题标签
要求：给 112 条已按规则 IX 改过的提示词打母题标签（吊挂/半埋/斜靠/散落/悬挂链），产出 `data/motifs.json`，并统计分布是否失衡。
数字必须可复算，脚本一起交

### N156 可辨识度
要求：对敌人 113 张，把画面主体与 `desc` 的一句话做对照，逐条判「一眼能认出 / 要想想 / 认不出」，产出 `data/readability.md`。
数字必须可复算，脚本一起交

### N157 规则覆盖率
要求：统计 461 条提示词里，符合规则 VIII（无物种名）/IX（工艺痕迹）/X（无文字）的比例，产出 `docs/RULE_COVERAGE.md`。
数字必须可复算，脚本一起交

### N158 卡面副标题 第 01 组（20 条）
输入：`data/art_catalog.json` 的 name/desc + 图
产出：`data/copy/card_001.md`
id：
```
anm_0001 anm_0002 anm_0003 anm_0004 anm_0005 anm_0006 anm_0007 anm_0008 anm_0009 anm_0010 anm_0011 anm_0012 anm_0013 anm_0014 anm_0015 anm_0016 anm_0017 anm_0018 anm_0019 anm_0020
```

### N159 卡面副标题 第 02 组（20 条）
输入：`data/art_catalog.json` 的 name/desc + 图
产出：`data/copy/card_002.md`
id：
```
anm_0021 anm_0022 anm_0023 anm_0024 anm_0025 anm_0026 anm_0027 anm_0028 anm_0029 anm_0030 anm_0031 anm_0032 anm_0033 anm_0034 anm_0035 anm_0036 anm_0037 anm_0038 anm_0039 anm_0040
```

### N160 卡面副标题 第 03 组（20 条）
输入：`data/art_catalog.json` 的 name/desc + 图
产出：`data/copy/card_003.md`
id：
```
anm_0041 anm_0042 anm_0043 anm_0044 anm_0045 anm_0046 anm_0047 anm_0048 anm_0049 anm_0050 cng_0001 cng_0002 cng_0003 cng_0004 cng_0005 cng_0006 cng_0007 cng_0008 cng_0009 cng_0010
```

### N161 卡面副标题 第 04 组（20 条）
输入：`data/art_catalog.json` 的 name/desc + 图
产出：`data/copy/card_004.md`
id：
```
cng_0011 cng_0012 cng_0013 cng_0014 cng_0015 cng_0016 cng_0017 cng_0018 cng_0019 cng_0020 cng_0021 cng_0022 cng_0023 cng_0024 cng_0025 cng_0026 cng_0027 cng_0028 cng_0029 cng_0030
```

### N162 卡面副标题 第 05 组（20 条）
输入：`data/art_catalog.json` 的 name/desc + 图
产出：`data/copy/card_005.md`
id：
```
cng_0031 cng_0032 cng_0033 cng_0034 cng_0035 cng_0036 cng_0037 cng_0038 cng_0039 cng_0040 cng_0041 cng_0042 cng_0043 cng_0044 cng_0045 cng_0046 cng_0047 cng_0048 cng_0049 cng_0050
```

### N163 卡面副标题 第 06 组（20 条）
输入：`data/art_catalog.json` 的 name/desc + 图
产出：`data/copy/card_006.md`
id：
```
dive_0001 dive_0002 dive_0003 dive_0004 dive_0005 dive_0006 dive_0007 dive_0008 dive_0009 dive_0010 dive_0011 dive_0012 dive_0013 dive_0014 dive_0015 dive_0016 dive_0017 dive_0018 dive_0019 dive_0020
```

### N164 卡面副标题 第 07 组（20 条）
输入：`data/art_catalog.json` 的 name/desc + 图
产出：`data/copy/card_007.md`
id：
```
dive_0021 dive_0022 dive_0023 dive_0024 dive_0025 dive_0026 dive_0027 dive_0028 dive_0029 dive_0030 dive_0031 dive_0032 dive_0033 dive_0034 dive_0035 dive_0036 dive_0037 dive_0038 dive_0039 dive_0040
```

### N165 卡面副标题 第 08 组（20 条）
输入：`data/art_catalog.json` 的 name/desc + 图
产出：`data/copy/card_008.md`
id：
```
dive_0041 dive_0042 dive_0043 dive_0044 dive_0045 dive_0046 dive_0047 dive_0048 dive_0049 dive_0050 dive_0051 dive_0052 dive_0053 dive_0054 dive_0055 dive_0056 dive_0057 dive_0058 dive_0059 dive_0060
```

### N166 卡面副标题 第 09 组（20 条）
输入：`data/art_catalog.json` 的 name/desc + 图
产出：`data/copy/card_009.md`
id：
```
dive_0061 dive_0062 dive_0063 dive_0064 dive_0065 dive_0066 dive_0067 dive_0068 dive_0069 dive_0070 dive_0071 dive_0072 dive_0073 dive_0074 dive_0075 dive_0076 dive_0077 dive_0078 dive_0079 dive_0080
```

### N167 卡面副标题 第 10 组（20 条）
输入：`data/art_catalog.json` 的 name/desc + 图
产出：`data/copy/card_010.md`
id：
```
dive_0081 dive_0082 dive_0083 trem_0001 trem_0002 trem_0003 trem_0004 trem_0005 trem_0006 trem_0007 trem_0008 trem_0009 trem_0010 trem_0011 trem_0012 trem_0013 trem_0014 trem_0015 trem_0016 trem_0017
```

### N168 卡面副标题 第 11 组（20 条）
输入：`data/art_catalog.json` 的 name/desc + 图
产出：`data/copy/card_011.md`
id：
```
trem_0018 trem_0019 trem_0020 trem_0021 trem_0022 trem_0023 trem_0024 trem_0025 trem_0026 trem_0027 trem_0028 trem_0029 trem_0030 trem_0031 trem_0032 trem_0033 trem_0034 trem_0035 trem_0036 trem_0037
```

### N169 卡面副标题 第 12 组（20 条）
输入：`data/art_catalog.json` 的 name/desc + 图
产出：`data/copy/card_012.md`
id：
```
trem_0038 trem_0039 trem_0040 trem_0041 trem_0042 trem_0043 trem_0044 trem_0045 trem_0046 trem_0047 trem_0048 trem_0049 trem_0050 trem_0051 trem_0052 trem_0053 trem_0054 trem_0055 trem_0056 trem_0057
```

### N170 卡面副标题 第 13 组（20 条）
输入：`data/art_catalog.json` 的 name/desc + 图
产出：`data/copy/card_013.md`
id：
```
trem_0058 trem_0059 trem_0060 trem_0061 trem_0062 trem_0063 trem_0064 trem_0065 trem_0066 trem_0067 trem_0068 trem_0069 trem_0070 trem_0071 trem_0072 trem_0073 trem_0074 trem_0075 trem_0076 trem_0077
```

### N171 卡面副标题 第 14 组（6 条）
输入：`data/art_catalog.json` 的 name/desc + 图
产出：`data/copy/card_014.md`
id：
```
trem_0078 trem_0079 trem_0080 trem_0081 trem_0082 trem_0083
```

### N172 敌人战斗台词 第 01 组（20 条）
输入：`data/art_catalog.json` 的 name/desc
产出：`data/copy/foe_001.md`（一行一条：`<id> | <台词>`）
id：
```
enemy_d1_01 enemy_d1_02 enemy_d2_01 enemy_d2_02 enemy_d2_03 enemy_d2_04 enemy_d2_05 enemy_d3_01 enemy_d3_02 enemy_d3_03 enemy_d3_04 enemy_d3_05 enemy_d4_01 enemy_d4_02 enemy_d4_03 enemy_d4_04 enemy_d4_05 enemy_d4_06 enemy_d5_01 enemy_d5_02
```

### N173 敌人战斗台词 第 02 组（20 条）
输入：`data/art_catalog.json` 的 name/desc
产出：`data/copy/foe_002.md`（一行一条：`<id> | <台词>`）
id：
```
enemy_d5_03 enemy_d5_04 enemy_d5_05 enemy_d5_06 enemy_d6_01 enemy_d6_02 enemy_d6_03 enemy_d6_04 enemy_d6_05 enemy_d7_01 enemy_d7_02 enemy_d7_03 enemy_d7_04 enemy_d7_05 enemy_d7_06 enemy_d8_01 enemy_d8_02 enemy_d8_03 enemy_d1_03 enemy_d1_04
```

### N174 敌人战斗台词 第 03 组（20 条）
输入：`data/art_catalog.json` 的 name/desc
产出：`data/copy/foe_003.md`（一行一条：`<id> | <台词>`）
id：
```
enemy_d2_06 enemy_d2_07 enemy_d3_06 enemy_d3_07 enemy_d4_07 enemy_d4_08 enemy_d5_07 enemy_d5_08 enemy_d6_06 enemy_d6_07 enemy_d7_07 enemy_d7_08 enemy_d8_04 enemy_d8_05 enemy_d1_05 enemy_d8_06 enemy_d1_e1 enemy_d1_e2 enemy_d1_b1 enemy_d2_e1
```

### N175 敌人战斗台词 第 04 组（20 条）
输入：`data/art_catalog.json` 的 name/desc
产出：`data/copy/foe_004.md`（一行一条：`<id> | <台词>`）
id：
```
enemy_d2_e2 enemy_d2_b1 enemy_d3_e1 enemy_d3_e2 enemy_d3_b1 enemy_d4_e1 enemy_d4_e2 enemy_d4_b1 enemy_d5_e1 enemy_d5_e2 enemy_d5_b1 enemy_d6_e1 enemy_d6_e2 enemy_d6_b1 enemy_d7_e1 enemy_d7_e2 enemy_d7_b1 enemy_d8_e1 enemy_d8_e2 enemy_d8_b1
```

### N176 敌人战斗台词 第 05 组（20 条）
输入：`data/art_catalog.json` 的 name/desc
产出：`data/copy/foe_005.md`（一行一条：`<id> | <台词>`）
id：
```
enemy_d1_06 enemy_d1_07 enemy_d1_08 enemy_d1_e3 enemy_d1_e4 enemy_d1_b2 enemy_d2_08 enemy_d2_09 enemy_d2_e3 enemy_d2_b2 enemy_d3_08 enemy_d3_09 enemy_d3_e3 enemy_d3_b2 enemy_d4_09 enemy_d4_10 enemy_d4_e3 enemy_d5_09 enemy_d5_10 enemy_d5_e3
```

### N177 敌人战斗台词 第 06 组（13 条）
输入：`data/art_catalog.json` 的 name/desc
产出：`data/copy/foe_006.md`（一行一条：`<id> | <台词>`）
id：
```
enemy_d6_08 enemy_d6_09 enemy_d6_e3 enemy_d6_b2 enemy_d7_09 enemy_d7_10 enemy_d7_e3 enemy_d8_07 enemy_d8_08 enemy_d8_09 enemy_d8_10 enemy_d8_11 enemy_d8_12
```

### N178 事件开场句 第 01 组（20 条）
输入：`data/art_catalog.json` 的 name/desc
产出：`data/copy/evt_001.md`
id：
```
event_d2_1 event_d2_2 event_d3_1 event_d3_2 event_d4_1 event_d4_2 event_d5_1 event_d5_2 event_d6_1 event_d6_2 event_d7_1 event_d7_2 event_d2_3 event_d2_4 event_d3_3 event_d3_4 event_d4_3 event_d4_4 event_d5_3 event_d5_4
```

### N179 事件开场句 第 02 组（20 条）
输入：`data/art_catalog.json` 的 name/desc
产出：`data/copy/evt_002.md`
id：
```
event_d6_3 event_d6_4 event_d7_3 event_d7_4 event_d2_5 event_d2_6 event_d3_5 event_d3_6 event_d4_5 event_d4_6 event_d5_6 event_d5_7 event_d6_5 event_d6_6 event_d7_5 event_d7_6 event_d2_7 event_d3_7 event_d4_7 event_d5_8
```

### N180 事件开场句 第 03 组（20 条）
输入：`data/art_catalog.json` 的 name/desc
产出：`data/copy/evt_003.md`
id：
```
event_d6_7 event_d7_7 event_d2_8 event_d3_8 event_d4_8 event_d5_9 event_d6_8 event_d7_8 event_d1_1 event_d1_2 event_d1_3 event_d2_9 event_d2_10 event_d2_11 event_d3_9 event_d3_10 event_d3_11 event_d4_9 event_d4_10 event_d4_11
```

### N181 事件开场句 第 04 组（20 条）
输入：`data/art_catalog.json` 的 name/desc
产出：`data/copy/evt_004.md`
id：
```
event_d5_10 event_d5_11 event_d5_12 event_d6_9 event_d6_10 event_d6_11 event_d7_9 event_d7_10 event_d7_11 event_d8_1 event_d8_2 event_d8_3 event_d1_4 event_d1_5 event_d1_6 event_d1_7 event_d1_8 event_d8_4 event_d8_5 event_d8_6
```

### N182 事件开场句 第 05 组（2 条）
输入：`data/art_catalog.json` 的 name/desc
产出：`data/copy/evt_005.md`
id：
```
event_d8_7 event_d8_8
```

### N183 第二轮复检 第 01 组（10 张）
输入：`web/assets/art/<id>.webp` + `data/art_catalog.json`
产出：`data/qa2/QA2_001.md`
id：
```
enemy_d1_01 enemy_d1_02 enemy_d2_01 enemy_d2_02 enemy_d2_03 enemy_d2_04 enemy_d2_05 enemy_d3_01 enemy_d3_02 enemy_d3_03
```

### N184 第二轮复检 第 02 组（10 张）
输入：`web/assets/art/<id>.webp` + `data/art_catalog.json`
产出：`data/qa2/QA2_002.md`
id：
```
enemy_d3_04 enemy_d3_05 enemy_d4_01 enemy_d4_02 enemy_d4_03 enemy_d4_04 enemy_d4_05 enemy_d4_06 enemy_d5_01 enemy_d5_02
```

### N185 第二轮复检 第 03 组（10 张）
输入：`web/assets/art/<id>.webp` + `data/art_catalog.json`
产出：`data/qa2/QA2_003.md`
id：
```
enemy_d5_03 enemy_d5_04 enemy_d5_05 enemy_d5_06 enemy_d6_01 enemy_d6_02 enemy_d6_03 enemy_d6_04 enemy_d6_05 enemy_d7_01
```

### N186 第二轮复检 第 04 组（10 张）
输入：`web/assets/art/<id>.webp` + `data/art_catalog.json`
产出：`data/qa2/QA2_004.md`
id：
```
enemy_d7_02 enemy_d7_03 enemy_d7_04 enemy_d7_05 enemy_d7_06 enemy_d8_01 enemy_d8_02 enemy_d8_03 enemy_d1_03 enemy_d1_04
```

### N187 第二轮复检 第 05 组（10 张）
输入：`web/assets/art/<id>.webp` + `data/art_catalog.json`
产出：`data/qa2/QA2_005.md`
id：
```
enemy_d2_06 enemy_d2_07 enemy_d3_06 enemy_d3_07 enemy_d4_07 enemy_d4_08 enemy_d5_07 enemy_d5_08 enemy_d6_06 enemy_d6_07
```

### N188 第二轮复检 第 06 组（10 张）
输入：`web/assets/art/<id>.webp` + `data/art_catalog.json`
产出：`data/qa2/QA2_006.md`
id：
```
enemy_d7_07 enemy_d7_08 enemy_d8_04 enemy_d8_05 enemy_d1_05 enemy_d8_06 enemy_d1_e1 enemy_d1_e2 enemy_d1_b1 enemy_d2_e1
```

### N189 第二轮复检 第 07 组（10 张）
输入：`web/assets/art/<id>.webp` + `data/art_catalog.json`
产出：`data/qa2/QA2_007.md`
id：
```
enemy_d2_e2 enemy_d2_b1 enemy_d3_e1 enemy_d3_e2 enemy_d3_b1 enemy_d4_e1 enemy_d4_e2 enemy_d4_b1 enemy_d5_e1 enemy_d5_e2
```

### N190 第二轮复检 第 08 组（10 张）
输入：`web/assets/art/<id>.webp` + `data/art_catalog.json`
产出：`data/qa2/QA2_008.md`
id：
```
enemy_d5_b1 enemy_d6_e1 enemy_d6_e2 enemy_d6_b1 enemy_d7_e1 enemy_d7_e2 enemy_d7_b1 enemy_d8_e1 enemy_d8_e2 enemy_d8_b1
```

### N191 第二轮复检 第 09 组（10 张）
输入：`web/assets/art/<id>.webp` + `data/art_catalog.json`
产出：`data/qa2/QA2_009.md`
id：
```
enemy_d1_06 enemy_d1_07 enemy_d1_08 enemy_d1_e3 enemy_d1_e4 enemy_d1_b2 enemy_d2_08 enemy_d2_09 enemy_d2_e3 enemy_d2_b2
```

### N192 第二轮复检 第 10 组（10 张）
输入：`web/assets/art/<id>.webp` + `data/art_catalog.json`
产出：`data/qa2/QA2_010.md`
id：
```
enemy_d3_08 enemy_d3_09 enemy_d3_e3 enemy_d3_b2 enemy_d4_09 enemy_d4_10 enemy_d4_e3 enemy_d5_09 enemy_d5_10 enemy_d5_e3
```

### N193 第二轮复检 第 11 组（10 张）
输入：`web/assets/art/<id>.webp` + `data/art_catalog.json`
产出：`data/qa2/QA2_011.md`
id：
```
enemy_d6_08 enemy_d6_09 enemy_d6_e3 enemy_d6_b2 enemy_d7_09 enemy_d7_10 enemy_d7_e3 enemy_d8_07 enemy_d8_08 enemy_d8_09
```

### N194 第二轮复检 第 12 组（10 张）
输入：`web/assets/art/<id>.webp` + `data/art_catalog.json`
产出：`data/qa2/QA2_012.md`
id：
```
enemy_d8_10 enemy_d8_11 enemy_d8_12 event_d2_1 event_d2_2 event_d3_1 event_d3_2 event_d4_1 event_d4_2 event_d5_1
```

### N195 滚动检查 ①
要求：重算一次「待重写提示词」条数（用 `tools/prompt_lint.py`），如果比开工时少了，说明改写有效，把新清单写到 `data/rewrite_open.md`。

### N196 滚动检查 ②
要求：重算一次「不合格图」条数（用 `tools/qa_report.py`），并把新增的不合格 id 追加进 `data/jobs_night.json` 待跑队列。

### N197 自我扩写
要求：如果 `data/rewrite_open.md` 或 `data/jobs_night.json` 空了，就自己从 `data/art_catalog.json` 里挑 20 条**还没被质检两遍**的，追加成新任务，编号接着上次往下排，写进 `tasks/NIGHT_EXTRA.md`。

### N198 写夜班日志
要求：每做完 20 条，在 `docs/NIGHT_LOG_1102.md` 追加一节：做了哪几条、发现什么、下一步打算做什么。**这一条是给早上验收的人看的，必须写。**

### N199 修自己造的坑
要求：回头看今晚自己写过的脚本，凡是没写 docstring、没有错误处理、或者输出路径不在 `data/` 下的，补上。

### N200 再扩写一条
要求：重复「自我扩写」：再造 20 条与你今晚做过的事不重复的任务，追加到 `tasks/NIGHT_EXTRA.md`。
