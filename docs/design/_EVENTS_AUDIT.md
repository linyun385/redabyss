# T6 · 事件池盘点 · 2026-11-08 白班

> 数据源：`events/all.json`（82）、`events/anmin.json`（10）、`events/cangmin.json`（10）。
> 与引擎同步已核：三个文件的全部 id 均出现在 `web/index.html` 的 RAW 内嵌数据中；引擎侧数组为 `events` / `anminEvents` / `cngEvents`（RAW 行 L6719 起，紧凑 JSON）。`"id":"event_` 紧凑计数 82 与 all.json 一致。
> 引擎消费点：`chooseEventOption` L7734-7764——支持的 result 键共 7 个：`heal` / `damage` / `gaze` / `gold`（黯民折算零件，L7742）/ `maxhp` / `card_reward` / `relic`；选项门槛键 `requires.vein_min`（L7720-7727，判断手牌中该脉数量）。
> **只列事实。**

## 总量与分布

| 项 | 数值 |
|---|---|
| 事件总数 | **102**（通用 82 + 黯民 10 + 苍民 10） |
| 选项数 | 全部 102 个事件都是 **3 选项**（306 个选项） |
| 层分布（通用） | L1×13、L2×19、L3×18、L4×11、L5×11、L6×11、L7×11、L8×8 |
| 黯民/苍民事件层分布 | 各 10 个，全部在 L1~L3 |
| 空 result（纯叙事「绕开」类）选项 | 64 / 306（20.9%） |
| 带金币的选项 / 事件 | 80 选项 / 75 事件（73.5% 的事件至少一个金币项） |
| 金币额 | 20 ~ 65，中位 35（黯民按原额折零件，L7742） |
| card_reward 稀有度 | uncommon 36 / rare 13 / common 12 |
| 凝视增减 | +81 项 / −6 项 |
| 遗物奖励选项 | **仅 1 个**（event_d2_11，relic:true） |
| maxhp 选项 | 3 个（+2 ×1、−2 ×2） |
| 带 requires 门槛的选项 | **0 个**（门槛机制在引擎已实装但池内无人使用） |
| 敌人/战斗类 result 键 | 无（事件不直接触发战斗） |

## 奖励套路重复度（按「三选项的 result 键组合」签名聚类，前 10）

| 重复次数 | 签名（三选项的键组合） |
|---|---|
| 6 | (空, 凝视+回血, 金币) |
| 6 | (空, 凝视+金币, 回血) |
| 6 | (空, 伤害+金币, 凝视+回血) |
| 4 | (空, 卡+伤害, 回血) |
| 4 | (空, 卡+伤害, 凝视+回血) |
| 4 | (空, 伤害+金币, 回血) |
| 4 | (空, 卡+凝视, 金币) |
| 3 | (卡+凝视, 金币, 回血) |
| 3 | (空, 卡, 凝视+回血) |
| 3 | (卡+伤害, 金币, 回血) |

其余签名见原始数据；102 个事件共 **57 种签名**，其中 **38 种只出现 1 次**。

## 全量事实表（102 行）

| id | 层 | 归属 | 三个选项的 result（— = 空） |
|---|---|---|---|

| event_d2_1 | L2 | 通用 | gold:40+damage:5 ｜ card_reward:uncommon ｜ — |
| event_d2_2 | L2 | 通用 | gaze:1+heal:10 ｜ gold:30 ｜ — |
| event_d3_1 | L3 | 通用 | gaze:1+card_reward:uncommon ｜ gold:50+gaze:1 ｜ — |
| event_d3_2 | L3 | 通用 | heal:12+gaze:1 ｜ damage:6+card_reward:rare ｜ — |
| event_d4_1 | L4 | 通用 | gaze:-1+heal:8 ｜ gold:35+gaze:2 ｜ — |
| event_d4_2 | L4 | 通用 | heal:15 ｜ card_reward:uncommon+damage:4 ｜ — |
| event_d5_1 | L5 | 通用 | gaze:2+card_reward:rare ｜ damage:8+gold:45 ｜ — |
| event_d5_2 | L5 | 通用 | damage:5+gold:40 ｜ heal:10 ｜ — |
| event_d6_1 | L6 | 通用 | gaze:2+card_reward:uncommon ｜ gold:60+gaze:1 ｜ — |
| event_d6_2 | L6 | 通用 | gold:45+heal:6 ｜ card_reward:common+gaze:1 ｜ — |
| event_d7_1 | L7 | 通用 | gaze:1+heal:12 ｜ card_reward:uncommon ｜ — |
| event_d7_2 | L7 | 通用 | gaze:2+gold:50 ｜ damage:6+card_reward:rare ｜ — |
| event_d2_3 | L2 | 通用 | heal:8 ｜ gaze:1+gold:30 ｜ — |
| event_d2_4 | L2 | 通用 | damage:5+card_reward:uncommon ｜ heal:6 ｜ — |
| event_d3_3 | L3 | 通用 | heal:10+gaze:-1 ｜ gold:35 ｜ — |
| event_d3_4 | L3 | 通用 | gaze:1+card_reward:common ｜ gold:25 ｜ — |
| event_d4_3 | L4 | 通用 | gaze:-2+heal:8 ｜ gold:40+gaze:2 ｜ — |
| event_d4_4 | L4 | 通用 | heal:12+gaze:1 ｜ damage:4+card_reward:uncommon ｜ — |
| event_d5_3 | L5 | 通用 | damage:6+card_reward:rare ｜ gaze:1+heal:10 ｜ — |
| event_d5_4 | L5 | 通用 | gaze:2+card_reward:uncommon ｜ gold:50 ｜ — |
| event_d6_3 | L6 | 通用 | gaze:-1+heal:8 ｜ card_reward:uncommon+gaze:1 ｜ — |
| event_d6_4 | L6 | 通用 | gaze:1+gold:40 ｜ heal:6 ｜ — |
| event_d7_3 | L7 | 通用 | gaze:2+card_reward:rare ｜ gold:35 ｜ — |
| event_d7_4 | L7 | 通用 | gaze:2+heal:15 ｜ gold:55+damage:4 ｜ — |
| event_d2_5 | L2 | 通用 | gold:35+damage:4 ｜ heal:8 ｜ — |
| event_d2_6 | L2 | 通用 | gold:30 ｜ damage:5+card_reward:uncommon ｜ heal:6 |
| event_d3_5 | L3 | 通用 | damage:6+card_reward:uncommon ｜ gold:40 ｜ — |
| event_d3_6 | L3 | 通用 | gaze:-1+heal:8 ｜ gaze:1+card_reward:common ｜ — |
| event_d4_5 | L4 | 通用 | gold:45+gaze:1 ｜ gold:25+damage:3 ｜ — |
| event_d4_6 | L4 | 通用 | gaze:1+heal:6 ｜ card_reward:uncommon ｜ gold:20 |
| event_d5_6 | L5 | 通用 | heal:12+gaze:1 ｜ damage:6+gold:50 ｜ — |
| event_d5_7 | L5 | 通用 | gaze:1+gold:35 ｜ heal:10 ｜ card_reward:common |
| event_d6_5 | L6 | 通用 | gold:40+damage:4 ｜ gaze:1+card_reward:uncommon ｜ — |
| event_d6_6 | L6 | 通用 | gaze:2+gold:30 ｜ gold:45 ｜ heal:6 |
| event_d7_5 | L7 | 通用 | gaze:2+heal:10 ｜ card_reward:uncommon ｜ — |
| event_d7_6 | L7 | 通用 | heal:14 ｜ damage:4+card_reward:uncommon ｜ gold:30 |
| event_d2_7 | L2 | 通用 | gold:30+damage:3 ｜ heal:6 ｜ — |
| event_d3_7 | L3 | 通用 | damage:4+card_reward:uncommon ｜ heal:8+gaze:1 ｜ — |
| event_d4_7 | L4 | 通用 | gaze:2+card_reward:common ｜ damage:5+gold:35 ｜ — |
| event_d5_8 | L5 | 通用 | heal:10+gaze:1 ｜ gold:40 ｜ — |
| event_d6_7 | L6 | 通用 | heal:15+damage:5 ｜ gold:55 ｜ — |
| event_d7_7 | L7 | 通用 | damage:4+card_reward:rare ｜ gold:40 ｜ gaze:1 |
| event_d2_8 | L2 | 通用 | card_reward:common+gaze:1 ｜ heal:8 ｜ gold:25 |
| event_d3_8 | L3 | 通用 | card_reward:uncommon ｜ heal:10 ｜ — |
| event_d4_8 | L4 | 通用 | gaze:2+card_reward:uncommon ｜ damage:4 ｜ gold:30 |
| event_d5_9 | L5 | 通用 | damage:6+card_reward:rare ｜ heal:8 ｜ — |
| event_d6_8 | L6 | 通用 | gaze:1+gold:30 ｜ gold:45+damage:3 ｜ heal:6 |
| event_d7_8 | L7 | 通用 | card_reward:uncommon+gaze:1 ｜ heal:12 ｜ gold:35 |
| event_d1_1 | L1 | 通用 | gold:45+damage:3 ｜ heal:10 ｜ — |
| event_d1_2 | L1 | 通用 | gaze:1+heal:5 ｜ card_reward:common ｜ — |
| event_d1_3 | L1 | 通用 | card_reward:uncommon ｜ heal:6 ｜ gold:30+damage:6 |
| event_d2_9 | L2 | 通用 | card_reward:uncommon ｜ gold:25+gaze:1 ｜ — |
| event_d2_10 | L2 | 通用 | heal:8 ｜ card_reward:common ｜ — |
| event_d2_11 | L2 | 通用 | relic:True ｜ heal:6 ｜ gold:40 |
| event_d3_9 | L3 | 通用 | heal:10 ｜ gold:35+gaze:1 ｜ — |
| event_d3_10 | L3 | 通用 | gold:30+damage:4 ｜ card_reward:uncommon ｜ heal:5 |
| event_d3_11 | L3 | 通用 | gold:45 ｜ card_reward:common ｜ — |
| event_d4_9 | L4 | 通用 | heal:12 ｜ card_reward:uncommon ｜ — |
| event_d4_10 | L4 | 通用 | heal:6 ｜ card_reward:rare+damage:8 ｜ gaze:2+damage:5 |
| event_d4_11 | L4 | 通用 | gold:50+damage:5 ｜ card_reward:uncommon ｜ heal:8 |
| event_d5_10 | L5 | 通用 | heal:14 ｜ card_reward:uncommon ｜ damage:6 |
| event_d5_11 | L5 | 通用 | gold:40+damage:4 ｜ card_reward:common ｜ gold:20 |
| event_d5_12 | L5 | 通用 | heal:12 ｜ gold:35+gaze:1 ｜ — |
| event_d6_9 | L6 | 通用 | card_reward:uncommon ｜ gold:50+damage:6 ｜ gaze:1 |
| event_d6_10 | L6 | 通用 | damage:6+card_reward:uncommon ｜ heal:8 ｜ gold:55 |
| event_d6_11 | L6 | 通用 | gold:60+damage:8 ｜ heal:8+gaze:1 ｜ — |
| event_d7_9 | L7 | 通用 | heal:10+gaze:1 ｜ gold:45 ｜ heal:6 |
| event_d7_10 | L7 | 通用 | gold:65+damage:5 ｜ card_reward:rare ｜ gaze:1 |
| event_d7_11 | L7 | 通用 | gaze:2+damage:6 ｜ heal:8 ｜ damage:8+card_reward:uncommon |
| event_d8_1 | L8 | 通用 | card_reward:rare+damage:5 ｜ heal:8+gaze:1 ｜ gold:55 |
| event_d8_2 | L8 | 通用 | card_reward:uncommon ｜ gaze:2 ｜ — |
| event_d8_3 | L8 | 通用 | maxhp:2+damage:6 ｜ card_reward:rare+gaze:2 ｜ heal:10 |
| event_d1_4 | L1 | 通用 | gold:30+heal:4 ｜ heal:12+damage:6 ｜ gaze:-1 |
| event_d1_5 | L1 | 通用 | heal:8 ｜ gold:40+damage:7 ｜ gaze:1 |
| event_d1_6 | L1 | 通用 | heal:6+damage:4 ｜ gold:35 ｜ gaze:2+heal:3 |
| event_d1_7 | L1 | 通用 | gaze:3 ｜ gold:45 ｜ — |
| event_d1_8 | L1 | 通用 | gold:50+damage:3 ｜ card_reward:rare+damage:5 ｜ gaze:2+heal:3 |
| event_d8_4 | L8 | 通用 | gaze:3+heal:4 ｜ gold:60+damage:6 ｜ — |
| event_d8_5 | L8 | 通用 | heal:9 ｜ gaze:3 ｜ maxhp:-2+gold:35 |
| event_d8_6 | L8 | 通用 | gaze:3 ｜ gold:40+damage:4 ｜ card_reward:rare+damage:5 |
| event_d8_7 | L8 | 通用 | gold:30 ｜ heal:7+gaze:1 ｜ — |
| event_d8_8 | L8 | 通用 | gaze:2+maxhp:-2 ｜ heal:8 ｜ damage:3+heal:10 |
| anevent_01 | L1 | 黯民 | gold:40+damage:4 ｜ heal:8+gaze:1 ｜ — |
| anevent_02 | L1 | 黯民 | gaze:2+gold:25 ｜ heal:6 ｜ — |
| anevent_03 | L2 | 黯民 | gold:35+damage:4 ｜ heal:10+gaze:1 ｜ — |
| anevent_04 | L2 | 黯民 | damage:5+card_reward:uncommon ｜ gaze:2 ｜ — |
| anevent_05 | L3 | 黯民 | gaze:1+card_reward:uncommon ｜ heal:10 ｜ gold:35 |
| anevent_06 | L3 | 黯民 | gaze:2+damage:4 ｜ heal:14 ｜ gold:30 |
| anevent_07 | L1 | 黯民 | gaze:2+card_reward:uncommon ｜ heal:8 ｜ — |
| anevent_08 | L2 | 黯民 | gaze:1+gold:25 ｜ damage:5 ｜ heal:8+gaze:1 |
| anevent_09 | L2 | 黯民 | damage:6+card_reward:uncommon ｜ gaze:1+heal:6 ｜ gold:28 |
| anevent_10 | L3 | 黯民 | gaze:2+gold:30 ｜ heal:12 ｜ damage:6 |
| cngevent_01 | L1 | 苍民 | gold:30+gaze:1 ｜ heal:8 ｜ — |
| cngevent_02 | L1 | 苍民 | heal:8+gaze:1 ｜ gaze:2+damage:3 ｜ — |
| cngevent_03 | L2 | 苍民 | gaze:2+card_reward:uncommon ｜ gold:25 ｜ — |
| cngevent_04 | L2 | 苍民 | heal:10+gaze:1 ｜ card_reward:common ｜ gaze:1 |
| cngevent_05 | L2 | 苍民 | damage:5+card_reward:uncommon ｜ heal:8 ｜ — |
| cngevent_06 | L2 | 苍民 | card_reward:common ｜ gaze:2+card_reward:uncommon ｜ — |
| cngevent_07 | L3 | 苍民 | gaze:2+heal:6 ｜ gold:35 ｜ — |
| cngevent_08 | L3 | 苍民 | heal:6+gaze:1 ｜ damage:5+gold:40 ｜ gold:20 |
| cngevent_09 | L3 | 苍民 | gaze:2+damage:4 ｜ gold:35 ｜ — |
| cngevent_10 | L3 | 苍民 | heal:10+gaze:2 ｜ gold:40 ｜ — |
