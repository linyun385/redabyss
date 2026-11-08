# 03_ENGINE · 引擎要改什么

> 这一章解决：四处改动 + 为什么非改不可。来源：R3_roadmap 阶段二 / CONFLICTS / T341 §三。

## 结论

6 处引擎改动，其中 1 处是全盘成败前提（双脉连携 [engine/core.js:429]），2 处极小（一行），2 处小，1 处中。全部改动都在 engine/core.js 或 index.html 内联副本——需要**两处同步**（00 篇第 4 节的铁律）。

## 六处改动

| # | 改什么 | 位置 | 改动量 | 为什么非改不可 | 来源 |
|---|---|---|---|---|---|
| 1 | 双脉各计连携 | [engine/core.js:429] `const primary = vs[0]` | 一行：改为遍历 vs 数组 | 不改则 5 张双脉牌退化成普通牌，桥梁层全部失效 | T331/T341 |
| 2 | clear_debuffs 分支 | [engine/core.js:655] 附近 | 一行：C.debuffs = {} | 减压舱（u_0017）的核心效果 | T341 |
| 3 | chain_keep 豁免 | [index.html:5624] veinChain={} | 一行：加豁免判断 | 共鸣腔（u_0014）的核心效果 | T341 |
| 4 | energy_debt 字段 | beginTurn [index.html:5620] 附近 | 一行 + 新状态位 | 预支的氧（u_0005） | T341 |
| 5 | keep_block_half 特效 | endTurn [index.html:6042] 附近 | 扩展遗物循环 | 守夜人的钟（u_0002） | T341 |
| 6 | discard 分支 | applyCardEffect [index.html:5807] | 一段手牌选择 | 空的手（u_0001） | T341 |

## 已发现的引擎死代码（不修但要知道）

| 死代码 | 位置 | 影响 |
|---|---|---|
| resonanceLock 只写不读 | [engine/core.js:502] 写、无读点 | 6 张 resonance_lock 卡空操作 |
| frail 无结算点 | [engine/core.js:728] enemyAct 只处理 weak | trem_0034 的 frail 效果无效 |
| anmin_mark 只读不写 | [engine/core.js:364] 读、无赋值 | 协议流幽灵（u_0016 通过 json 赋值解决） |

## 引擎双份誊抄

engine/core.js（1026 行）与 index.html 内联副本（[index.html:5362]-[index.html:6390]）函数一一对应但行号不同。**改引擎必须两处同步**。00 篇第八节有完整行号对照表。

⚠ CONFLICTS C1：T331 原稿说双芯灯管在 no_light 层「仍有灼烧端可打」——[index.html:5817] 的整卡 return 证明这不对。T341 已修正。

## 本章待确认

| # | 事项 | 倾向 |
|---|---|---|
| 1 | 双脉连携改写（[engine/core.js:429]）的优先级 | 最高——全盘成败前提 |
| 2 | resonanceLock 死代码是否修复 | 低——6 张卡在 T335 删卡中已处理 2 张（trem_0019 未删），修复优先级低于双脉 |
| 3 | frail 无结算点是否补实现 | 低——frail 全池仅 2 张，影响面小 |
| 4 | 引擎改动是否两处同步的自动化 | 建议写一个同步脚本（当前无自动同步机制） |
