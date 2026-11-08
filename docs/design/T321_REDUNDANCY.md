# T321 · 冗余诊断：换了名字的同一张牌

> 口径说明（全文统一）：
> **结构同构** = 把 `effect` 里所有数字抹成 0 后 JSON 仍然相同（键、嵌套、`target`、`special` 的 `code`/`turns` 全一致，只有数值可以不同）。
> **机制家族** = 机制签名（`damage`/`block`/`draw`/`special:xxx`… 的集合）+ `target` 相同。
> 数字全部直接从 `cards/*.json` 算出，不含任何目测。

## A. 效果完全重复

**49 个同构组，覆盖 210 张卡 —— 全池 79% 的卡在同职业内有一张「换了名字的自己」。**

### A1. effect 字段一字不差的 4 对

| 对 | 差异 |
|---|---|
| dive_0017「星髓矿业·深地车」↔ dive_0040「重力训练舱」 | effect 完全相同（strength1+dexterity1）。只有费用 1↔2 |
| trem_0020「静日触杖」↔ trem_0077「五脉符（浮位）」 | effect 完全相同（dexterity2），费用同为 1、代价同为 none、稀有度同为 uncommon。**除 id 和名字外没有任何区别** |
| trem_0040「五脉符」↔ trem_0067「五脉符（缺位）」 | effect 完全相同（strength1+dexterity1）。费用 2↔1，代价 none↔mark，稀有度 uncommon↔rare —— 同一张牌，一张是另一张的完全上位 |
| anm_0015「主控授权·工程线」↔ anm_0035「超频保养」 | effect 完全相同（strength2），费用同为 1。代价 none↔vitality，稀有度 rare↔uncommon |

### A2. 规模最大的同构组（各组全部成员与数值）

**下潜者·单体伤害，14 张**——同一张「打一炮」，从 2 伤到 24 伤排成一条价格阶梯：

| id | 名字 | 费用/代价 | 伤害 |
|---|---|---|---|
| dive_0049 | 硬矿钻（手持） | 0/none | 4 |
| dive_0062 | 凿屑袋 | 0/none | 2×2段 |
| dive_0013 | 硬矿钻 | 0/none | 5 |
| dive_0072 | 星髓矿业·二号钻台 | 1/none | 5×2段 |
| dive_0002 | 聚能枪 | 1/none | 10 |
| dive_0027 | 星髓矿业·钻杆 | 1/none | 9 |
| dive_0015 | 星髓矿业·爆破执照 | 1/lock | 12 |
| dive_0031 | 聚能枪（过热） | 1/vitality | 11 |
| dive_0074 | 黑曜采掘·计件工资 | 1/vitality | 8 |
| dive_0054 | 聚能枪（超载） | 1/vitality | 16 |
| dive_0009 | 聚能枪（双管） | 2/none | 8×2段 |
| dive_0069 | 聚能枪（三管） | 2/none | 7×3段 |
| dive_0012 | 轨道炮支援 | 3/none | 24 |
| dive_0078 | 红渊研究院·频谱印章 | 2/none | 11 |

这组里连「稀有度阶梯」都排好了（com→unc→rar），说明冗余是**有意的生成策略**，不是事故。其余大组：疯先知纯格挡 11 张（cng_0001 块4 费0 → cng_0003/cng_0045 块6/5 费1 → cng_0020 块14 费2）、震语者单体伤害 10 张（trem_0004 11 伤…trem_0005 4 伤）、疯先知单体伤害 10 张（cng_0021 9 伤 费1 → cng_0018 13 伤 费2）、维护者纯格挡 9 张（anm_0037…anm_0046）、维护者单体伤害 8 张（anm_0002 9 伤…anm_0038 11 伤）、下潜者纯抽牌 8 张（dive_0001 抽1 费0 → dive_0083 抽2 费1）、震语者纯格挡 8 张、疯先知纯抽牌 7 张、下潜者纯共振 6 张（dive_0025 +2…dive_0047 +6 费2）。清单不逐组展开，全表见 `docs/content/cards_*.md`（本文只下判断）。

### A3. 「灼烧攻击」模板：8 张一个模子

trem_0017（7伤+burn2×2，费1）、trem_0023（12伤+burn4×3+共振费5，费2）、trem_0024（12伤+burn6×3，费3/memory）、trem_0065（6伤+burn3×2，费1）、trem_0080（9伤+burn4×3，费2）、dive_0033（6伤+burn3×2，费1）、dive_0034（全体 burn5×3，费2）、anm_0011（6伤+burn3×2，费1）、cng_0034（10伤+burn3×3，费2）。同一模板「伤害+灼烧」跨四个职业铺了 9 张，数值不同、结构相同。

### A4. 为什么会这样：势力换皮

带「势力·」前缀的卡共 **57 张，来自 19 个前缀**：星髓矿业 7、抗共振司 7、渊光重工 6、红渊研究院 5、深红资源集团 5、涌喉 4、相石 4、静底 4、黑曜采掘 3、红渊贸易局 2、主控授权 2、反走私局 1 等。A1 里的 dive_0017「星髓矿业·深地车」与 dive_0040「重力训练舱」、anm_0015「主控授权·工程线」与 anm_0035「超频保养」都是换皮的直接产物：**同一效果发给了不同势力人设，各领一个名字**。

### A5. 一个诚实的注意点

21 个同构组内部 `cost_type` 不一致（如 anm_0015 none ↔ anm_0035 vitality）。vitality 要扣血，严格说打出去的付出不同；但效果字段本身仍是同构的，本文按 A 类计入，此处存档差别。

## B. 功能重复（效果不同但打出来感觉一样）

把口径放宽到「机制家族」（签名+目标一致，数值与费用自由）后，家族数量比结构组少不了多少——**因为 A 类把 B 类基本吞掉了**。同职业内「签名+目标+费用+代价类型」完全一致、但结构（段数/全体）不同的组只剩 3 个，全是伤害牌的段数/目标变体：

- 疯先知费2 纯伤害：cng_0018、cng_0022（单段单体）、cng_0038（多段单体）、cng_0024、cng_0035（全体）
- 下潜者费2 纯伤害：dive_0009、dive_0069（多段）、dive_0078（单段）、dive_0010、dive_0055（全体）
- 震语者费2 伤害+凝视费：trem_0010（多段）、trem_0060（全体）

这三组内部互换确实会变打法——单体打精英、全体清杂是不同决策，所以它们只是**弱重复**。真正符合「互换两局打法不变」的，全在 A 类里：A2 那张 14 行的表里任何两行互换，玩家的回合计划一字不用改。**结论：本卡池的重复不是「感觉像」，是字段级相同；「功能重复」作为独立类别在这里几乎不存在，因为它已经被效果重复覆盖。**

## C. 升级没有质变

引擎语义先说清（[engine/core.js:968]）：`upgrade.effect` 的数值是**最终值**，`special` 数组是**追加**（[engine/core.js:981]），`cost_type` 可被改写。据此把 267 张卡分成：

- **255 张纯数值升级**（97 种模式）——升级前后机制签名完全不变，玩法一字不变；
- **4 张代价改写**：dive_0008、dive_0064、trem_0009、trem_0038，全部是 memory→none（升级免掉记忆代价，算半个质变）；
- **2 张真质变**：trem_0001「震语：听骨」升级追加 `special:[{code:"retain"}]`（新增保留机制）；dive_0003「曜元」升级把 `special` 写成空数组——按 [engine/core.js:981] 空数组会**清空**原 special，即升级后不再是消耗牌（顺带它的 draw 2→2 分量是空转，见下）。除这两张外，没有任何升级改变机制；
- **6 张没有 upgrade 字段**：dive_0081、dive_0082、dive_0083、trem_0081、trem_0082、trem_0083（各职业末尾三张），根本无法升级。

**假升级率：255 / 261 = 97.7%。**

### 纯数值升级全清单（256 张，按变化模式分组）

- **draw 1→2**（15 张）：dive_0001、dive_0037、dive_0039、dive_0048、trem_0025、trem_0046、trem_0055、trem_0070、anm_0003、anm_0033、anm_0044、anm_0045、cng_0002、cng_0006、cng_0044
- **special:strength追加+(1)**（15 张）：dive_0017、dive_0020、dive_0035、dive_0040、dive_0056、dive_0057、dive_0075、trem_0040、trem_0044、trem_0058、trem_0067、anm_0015、anm_0035、anm_0050、cng_0019
- **block 6→9**（11 张）：dive_0016、dive_0036、trem_0016、trem_0019、trem_0022、trem_0068、trem_0074、anm_0019、anm_0031、anm_0046、cng_0003
- **draw 2→3**（11 张）：trem_0007、trem_0043、trem_0066、trem_0078、anm_0009、anm_0018、anm_0023、cng_0007、cng_0017、cng_0033、cng_0047
- **block 8→12**（9 张）：dive_0004、dive_0038、trem_0018、trem_0041、trem_0063、trem_0079、anm_0017、anm_0024、anm_0034
- **block 5→7**（8 张）：dive_0019、dive_0044、trem_0006、trem_0028、trem_0039、trem_0073、cng_0005、cng_0045
- **special:dexterity追加+(1)**（7 张）：dive_0007、dive_0052、dive_0060、trem_0020、trem_0077、anm_0016、cng_0050
- **special:regenerate追加+(2)**（7 张）：dive_0032、dive_0059、trem_0014、trem_0033、trem_0035、anm_0040、cng_0042
- **damage 10→14**（6 张）：dive_0002、dive_0011、dive_0030、anm_0025、cng_0024、cng_0034
- **damage 8→11**（6 张）：dive_0009、dive_0074、trem_0072、anm_0047、cng_0022、cng_0027
- **damage 12→17**（6 张）：dive_0015、trem_0023、trem_0024、trem_0030、trem_0042、trem_0060
- **damage 6→8**（6 张）：dive_0033、trem_0065、trem_0076、anm_0011、anm_0039、cng_0038
- **block 4→6**（6 张）：dive_0061、dive_0073、trem_0015、trem_0054、anm_0001、cng_0001
- **damage 7→10**（6 张）：dive_0067、dive_0069、trem_0017、anm_0030、cng_0026、cng_0035
- **block 7→10**（6 张）：dive_0079、trem_0003、trem_0032、anm_0004、cng_0011、cng_0043
- **damage 9→12**（5 张）：trem_0010、trem_0080、anm_0002、cng_0037、cng_0048
- **heal 3→5**（5 张）：anm_0032、cng_0010、cng_0016、cng_0032、cng_0046
- **block 3→5**（4 张）：dive_0006、dive_0050、trem_0026、cng_0014
- **resonance_gain 2→3**（4 张）：dive_0014、dive_0025、trem_0036、trem_0071
- **damage 9→13**（4 张）：dive_0027、trem_0052、trem_0062、cng_0021
- **damage 12→16**（3 张）：dive_0010、anm_0014、cng_0029
- **block 9→13**（3 张）：dive_0018、trem_0059、anm_0010
- **damage 14→19**（3 张）：dive_0026、dive_0055、trem_0034
- **resonance_gain 4→6**（3 张）：dive_0028、dive_0043、trem_0047
- **damage 11→15**（3 张）：dive_0031、dive_0078、anm_0038
- **resonance_gain 3→5**（3 张）：dive_0041、dive_0045、trem_0037
- **damage 4→6**（3 张）：dive_0049、trem_0005、trem_0048
- **heal 6→9**（3 张）：dive_0066、anm_0022、cng_0012
- **block 10→14**（3 张）：trem_0011、anm_0037、anm_0043
- **damage 5→7**（2 张）：dive_0013、dive_0072
- **damage 10→13**（2 张）：dive_0024、trem_0013
- **draw 3→4; resonance_cost 8→6**（2 张）：dive_0029、trem_0012
- **resonance_gain 5→7**（2 张）：dive_0042、trem_0057
- **draw 3→4**（2 张）：dive_0053、dive_0080
- **damage 2→3**（2 张）：dive_0062、trem_0049
- **special:thorns追加+(2)**（2 张）：dive_0065、cng_0025
- **resonance_gain 3→4**（2 张）：dive_0077、trem_0002
- **special:regenerate追加+(1)**（2 张）：trem_0031、anm_0041
- **heal 5→8**（2 张）：anm_0029、cng_0004
- **heal 8→12**（2 张）：anm_0042、cng_0041
- **block 8→11**（2 张）：cng_0009、cng_0039
- **block 9→12**（2 张）：cng_0015、cng_0030
- **block 5→7; special:regenerate追加+(1)**（1 张）：dive_0005
- **damage 24→34**（1 张）：dive_0012
- **damage 26→36**（1 张）：dive_0021
- **damage 13→18; special:frail追加+(—)**（1 张）：dive_0022
- **block 12→17**（1 张）：dive_0023
- **special:burn追加+(2)**（1 张）：dive_0034
- **damage 36→48**（1 张）：dive_0046
- **resonance_gain 6→9**（1 张）：dive_0047
- **resonance_gain 1→2**（1 张）：dive_0051
- **damage 16→22**（1 张）：dive_0054
- **damage 30→42**（1 张）：dive_0058
- **block 13→18**（1 张）：dive_0063
- **block 6→9; heal 4→6**（1 张）：dive_0068
- **block 5→7; resonance_drain 5→7**（1 张）：dive_0070
- **draw 1→1; resonance_gain 1→2**（1 张）：dive_0071
- **heal 4→6**（1 张）：dive_0076
- **damage 11→14**（1 张）：trem_0004
- **damage 13→17**（1 张）：trem_0008
- **block 14→20**（1 张）：trem_0021
- **special:gaze_reduce追加+(2)**（1 张）：trem_0027
- **block 8→12; special:gaze_reduce追加+(1)**（1 张）：trem_0029
- **block 18→26**（1 张）：trem_0045
- **damage 3→4**（1 张）：trem_0050
- **block 2→4**（1 张）：trem_0051
- **damage 13→16**（1 张）：trem_0053
- **draw 3→4; gaze_cost 5→4**（1 张）：trem_0056
- **block 3→5; resonance_gain 2→2**（1 张）：trem_0061
- **draw 4→5; resonance_cost 10→8**（1 张）：trem_0064
- **damage 15→20**（1 张）：trem_0069
- **draw 3→4; resonance_cost 6→5**（1 张）：trem_0075
- **block 5→8**（1 张）：anm_0005
- **resonance_gain 2→4**（1 张）：anm_0006
- **damage 4→5**（1 张）：anm_0007
- **block 4→6; resonance_drain 5→7**（1 张）：anm_0008
- **heal 7→10**（1 张）：anm_0012
- **damage 5→7; resonance_gain 4→5**（1 张）：anm_0013
- **block 6→10**（1 张）：anm_0020
- **block 4→6; draw 1→1**（1 张）：anm_0021
- **block 5→5; heal 5→8**（1 张）：anm_0026
- **block 3→6**（1 张）：anm_0027
- **damage 14→18**（1 张）：anm_0028
- **block 4→5; heal 4→6**（1 张）：anm_0036
- **block 5→7; resonance_gain 3→4**（1 张）：anm_0048
- **resonance_drain 6→8**（1 张）：anm_0049
- **block 4→7**（1 张）：cng_0008
- **heal 4→7**（1 张）：cng_0013
- **damage 13→18**（1 张）：cng_0018
- **block 14→19**（1 张）：cng_0020
- **block 12→16**（1 张）：cng_0023
- **block 10→13**（1 张）：cng_0028
- **damage 16→21**（1 张）：cng_0031
- **heal 10→14**（1 张）：cng_0036
- **damage 18→24**（1 张）：cng_0040
- **block 6→8**（1 张）：cng_0049
- **special:rule_bypass追加+(—)**（1 张）：share_0001

### 空转升级分量（升级里混着不变的数值）

5 处升级分量是「原值→原值」：dive_0071 的 draw 1→1、trem_0001 的 draw 1→1、trem_0061 的 resonance_gain 2→2、anm_0021 的 draw 1→1、anm_0026 的 block 5→5。玩家点下升级，这部分承诺了变化却什么都没给。

## 结论：不可替代的有多少张

按严格程度给两个数：

1. **同职业口径（效果结构去重）**：267 张 → **106 张**。即 **161 张（60%）是同职业内另一张卡的换皮**，删掉它们不损失任何效果结构；剩下 106 张承载了全部 49 种结构。
2. **池级口径（结构+费用+代价类型跨职业去重）**：267 张 → **121 种设计**。其中最大的一族「费1·none·纯格挡·self」横跨四个职业共 22 张（cng 11 张 + anm 7 张 + trem 3 张 + dive 1 张之外还有几组），第二族「费1·none·单体伤害」17 张。四个职业在很大程度上**共用同一副骨架的同一批价格档**。

升级维度再加一刀：261 个升级位里 255 个是纯数值（内含 5 处空转分量），**玩家在整个周目里能从升级获得的「新玩法」只有 2 张卡**（trem_0001 追加保留、dive_0003 移除消耗），外加 4 张免记忆代价。如果用户的体感是「卡牌设计太单调」，这就是它的算术形式：**六成卡是换皮，九成八升级是加数**。

## 决定记录

- 「结构同构」把 `hits` 归入数值（抹零），因此「10×1 段」与「8×2 段」算同构——多段与单段在力量成长下收益不同，这是同构口径内残留的真实差异，已在 A2 表中标注段数。
- cost_type 不同的同构成员（21 组）仍计入重复，差别存档于 A5；若按「连代价都要一样」的更严口径，不可替代数最多上浮约 21 张到 127 张，不改变「六成换皮」的量级结论。
- 升级分类按 [engine/core.js:977] 的合并语义执行：顶层键覆盖（数值为最终值）、special 追加（空数组清空，见 [engine/core.js:981]）、cost_type 可改写。cost_type 改写单列为「半个质变」而非纯数值；dive_0003 因清空 exhaust 归入真质变，从纯数值表中剔除。
- 4 对 effect 完全相同的卡、6 张无 upgrade 字段的卡、6 处空转升级，只记录不改动（本任务禁改 json）。
