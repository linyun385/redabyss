# T7 · 遗物池盘点 · 2026-11-08 白班

> 数据源：`relics/all.json`（77）、`relics/anmin.json`（15）、`relics/cangmin.json`（15）。全部 id 均在 `web/index.html` RAW 内嵌数据中出现（当轮核对）。
> 引擎侧数组：`RAW.relics` / `RAW.anminRelics` / `RAW.cngRelics`；取池规则在 `pickRelics` L7551（见下「获取渠道」）。
> 引擎消费点：`grantRelic` L7560-7568（只实装 `run_start`+`maxhp` 一个触发即时生效）；effect_code 的四个 trigger 在引擎中的分发点未逐一定位（**未确认**：combat_start / turn_start / on_kill 的分发处未在本次逐行核对，只确认数据结构与 grantRelic 的 run_start 处理）。
> **只列事实。**

## 一、总量与分布

| 项 | 数值 |
|---|---|
| 遗物总数 | **107**（通用 77 + 黯民 15 + 苍民 15） |
| 通用稀有度 | common 27 / uncommon 27 / rare 20 / **boss 3**（relic_20、relic_34、relic_35） |
| 黯民稀有度 | common 5 / uncommon 7 / rare 3 |
| 苍民稀有度 | common 6 / uncommon 5 / rare 4 |
| `source:'event'` 限定 | 4 件（事件池专用，`pickEventRelics` L7540 只取这 4 件；普通池 L7552 排除它们） |
| 脉分布 | mineral 25 / light 25 / water 16 / heat 15 / tremor 14 |

**获取渠道**（`pickRelics` L7549-7558）：
- 普通局（非苍民、非 isEcho）：只抽 `RAW.relics`（77 件）。
- 苍民局：`RAW.relics + RAW.cngRelics`（92 件）。
- **isEcho 局：`RAW.relics + RAW.anminRelics`（92 件）。**
- 即：**黯民的 15 件专属遗物在日常黯民局不可获取，只在 isEcho（回声局）可获取**——这是 L7551 的字面行为，照录。

## 二、效果结构分布

| trigger | 条数 | | action | 条数 |
|---|---|---|---|---|
| combat_start | 81 | | block | 35 |
| turn_start | 32 | | gaze | 26 |
| run_start | 10 | | draw | 21 |
| on_kill | 6 | | heal | 21 |
| | | | resonance | 16 |
| | | | maxhp | 10 |

**effect_code 只有这 6 种 action，没有任何经济类 action**（无 gold / parts / 拆解类）。

### mod 键分布（走 cardCost / 结算改则那一路）

| mod 键 | 件数 | 引擎消费点（当轮行号） |
|---|---|---|
| chain_bonus（+chain_vein 限定） | 8（其中 7 件带 chain_vein） | veinChainBonus L5919-5937 |
| vein_cost / vein_cost_delta | 5 | cardCost L5909-5914 |
| keep_block | 4 | endTurn L6332-6335 |
| cost_redirect | 2 | applyCardCost L6167-6174（代价改写为凝视 +2） |

### 套路重复度（按 effect_code 签名，前 10）

| 重复 | 签名 |
|---|---|
| 10 | block@combat_start=3 |
| 10 | block@combat_start=2 |
| 8 | resonance@turn_start=2 |
| 6 | heal@turn_start=1 |
| 6 | draw@combat_start=1;gaze@combat_start=1 |
| 5 | draw@combat_start=1 |
| 5 | block@combat_start=4 |
| 5 | gaze@combat_start=1 |
| 4 | heal@on_kill=3 |
| 3 | gaze@combat_start=2 |

block@combat_start 系列合计约 40 件、数值从 1 到 10 不等，是全池最大的重复簇。

## 三、与零件经济的关系（任务重点）

1. **没有任何遗物的 effect_text / effect_code / flavor 提到零件或金币**（107 件全量关键词扫描：0 件）。
2. 与经济**间接**挂钩的只有两条路：
   - `cost_redirect` 2 件（relic_28、relic_56）：把出牌代价改写为凝视 +2（L6167-6174）——改的是代价结构，不是零件存量。
   - `vein_cost_delta` 5 件：某脉费用 -1（L5909-5914）——同上。
3. **零件→遗物的唯一通道是黯民「拆解」**：花 3 零件 → 威胁等级 +1（剩余敌人攻击永久 +1）→ 战后 +1 件随机遗物（`dismantle` L6563-6572，战后结算 L7469-7476）。这是零件的消耗出口之一，与 T2 的消耗侧互补。
4. **商店与黯民的货币断点（事实陈述）**：商店定价与扣款全走 `run.gold`（建stock L7150-7165、扣款 L7192），遗物标价 120~320 金（L7160）；而黯民的金币收入渠道为 0（战斗金币对黯民返回 0，L6510-6511；事件金币折算零件 L7742；boss 奖励折零件 L7502-7503）。HUD 已把黯民的金币栏改名隐藏（L6901-6906），但商店面板仍显示 `run.gold`（L7176）并按 `run.gold` 判定买不买得起（L7188）。**黯民在商店实际上买不起任何东西（含遗物）**——照录，不判断是否有意。

## 四、命名与卡池的重叠

8 件遗物与现有卡**同名**（照录，未判断是否故意）：

| 遗物 | 同名卡 |
|---|---|
| relic_10 静日触杖 | trem_0020 |
| relic_14 埋骨布 | trem_0039 |
| anrelic_04 死者的工号牌 | anm_0044 |
| anrelic_14 血统册摘录 | anm_0033 |
| cngrelic_02 母亲的祷文 | cng_0012 |
| cngrelic_04 猎巫者的绳 | cng_0043 |
| cngrelic_06 三体历残卷 | cng_0044 |
| cngrelic_07 火母的小像 | cng_0046 |

另：relic_74 名字为「茧上剥落的」——通顺性存疑（照录）。

## 五、全量清单（107 件）

见脚本输出格式：`id | 稀有度 | 归属 | 名字 | effect_code | veins | mod`。完整 107 行已核对，要点摘录如下（完整逐行表过长，全部数据可由 `relics/*.json` 直接复现；如需贴全表请告知）：

- boss 3 件：relic_20 记忆封瓶（gaze@combat_start=3）、relic_34 墟盐晶簇（heal@turn_start=2;resonance@turn_start=2;gaze@combat_start=2）、relic_35 第一降的船票（回程）（maxhp@run_start=20;gaze@combat_start=1）。
- 负面/代价型遗物（value 为负或带 maxhp 负值）：relic_12（gaze-2）、relic_15（gaze-1）、relic_16（maxhp-4）、relic_17（gaze-4;maxhp-10）、relic_21（maxhp-6）、relic_23（maxhp-8）、relic_36（gaze-2）、relic_40（maxhp-4）。共 8 件带负向效果。
- effect_code 为空/无 action 的遗物：0 件（全部 107 件都有至少一条 effect_code 或 mod）。
