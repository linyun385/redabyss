# T320 · 机制骨架分析

> 数据源：`cards/*.json`（diver 83 + tremor 83 + anmin 50 + cangmin 50 + shared 1，共 267 张，id 无重复）。
> 统计口径：每张卡的 `effect` 顶层键（去掉 `target`、`hits` 这两个承载字段）+ `special` 数组里的 `code`，去重后算作「该卡用到的机制」。
> 结果与 `docs/content/mechanisms.md` 的 22 行对照表逐项核对一致；对照表之外还发现了第 23 种机制 `special:rule_bypass`（仅 share_0001 使用），对照表没有收录它。

## 1. 各职业的机制骨架

### 下潜者（diver，83 张，平均每卡 1.80 种机制）

| 机制 | 卡数 | 占比 |
|---|---|---|
| damage | 27 | 32.5% |
| block | 19 | 22.9% |
| draw | 17 | 20.5% |
| resonance_gain | 14 | 16.9% |
| special:strength | 7 | 8.4% |
| special:dexterity | 5 | 6.0% |
| gaze_cost / resonance_cost | 各 4 | 各 4.8% |
| special:regenerate | 8 | 9.6% |

骨架 = 「伤害 + 格挡 + 抽牌」三件套（61 张卡至少占其中一样，73.5%），再挂一条攒共振的支线（14 张 resonance_gain）。它的身份机制本应是「用共振做资源、用凝视做代价」：resonance_cost 有 4 张（dive_0021、dive_0026、dive_0029、dive_0046），gaze_cost 有 4 张（dive_0011、dive_0024、dive_0030、dive_0082），合计不到 10%，两条资源线都只是点缀。代价端倒是全职业最重：10 张 vitality 代价卡、6 张 lock（每层一次），典型的「拿身体换东西」。

### 震语者（tremor，83 张，平均每卡 2.11 种机制）

| 机制 | 卡数 | 占比 |
|---|---|---|
| block | 29 | 34.9% |
| damage | 25 | 30.1% |
| draw | 25 | 30.1% |
| resonance_gain | 17 | 20.5% |
| gaze_cost | 10 | 12.0% |
| resonance_cost | 6 | 7.2% |
| special:burn | 5 | 6.0% |
| special:retain | 4 | 4.8% |

四职业里唯一把共振（17 张攒 + 6 张花）和凝视（10 张花 + 2 张涨：trem_0055、trem_0066）当主动语言用的职业，代价端的 memory 类型 10 张，是其他职业（下潜 2、维护 2）的五倍。机制密度也最高（2.11 种/卡），全池 7 张 4 机制顶配卡里有 6 张在这职业：trem_0014、trem_0023、trem_0034、trem_0058、trem_0070、trem_0082。它最接近「设计完成态」，其他三个职业是在它的骨架上做了减法。

### 维护者（anmin，50 张，平均每卡 1.58 种机制）

| 机制 | 卡数 | 占比 |
|---|---|---|
| block | 19 | 38.0% |
| draw | 11 | 22.0% |
| damage | 11 | 22.0% |
| heal | 7 | 14.0% |
| resonance_gain | 3 | 6.0% |
| resonance_drain | 3 | 6.0% |
| special:resonance_lock | 2 | 4.0% |
| special:strength | 4 | 8.0% |

骨架 = 格挡为大头的「维稳」结构，heal 7 张 + special:regenerate 2 张构成它的回复线（疯先知 heal 更多有 9 张，但维护者的回复跟 block 天然同轴）。它对共振的态度是「管理」而不是「使用」：resonance_gain 3 张（anm_0006、anm_0013、anm_0048）小幅生产，resonance_drain 3 张（anm_0008、anm_0017、anm_0049）大幅压掉，resonance_lock 2 张（anm_0020、anm_0027）上锁，而 resonance_cost 为 0 —— 也就是说维护者会生产和压制共振，但**从不消费**：攒共振对它没有出口。费用表 0/1/2 三档，没有 3 费卡（这点与疯先知相同，其余两职业都有 3 费档）。

### 疯先知（cangmin，50 张，平均每卡 1.34 种机制）

| 机制 | 卡数 | 占比 |
|---|---|---|
| block | 17 | 34.0% |
| damage | 14 | 28.0% |
| draw | 13 | 26.0% |
| heal | 9 | 18.0% |
| special:regenerate | 2 | 4.0% |
| special:burn / thorns / weak / strength / dexterity | 各 1 | 各 2.0% |

**这个职业没有任何资源机制。**（资源卡指读/写共振或凝视的卡） resonance_gain、resonance_cost、resonance_drain、resonance_lock、gaze_cost、gaze_gain、gaze_reduce 全部为 0；cost_type 里 49/50 张是 none，唯一的例外是 cng_0050「疯先知的笔记」（mark 代价）。它的 50 张卡全部由「伤害/格挡/抽牌/治疗」四个基础动作构成，机制组合签名只有 14 种（下潜者 31 种、震语者 36 种、维护者 21 种），其中 12 张纯伤害、11 张纯格挡、7 张纯抽牌、6 张纯治疗 —— 单机制卡占了 72%。它名字里带「疯」，卡池却是四职业里最规矩的。

## 2. 通用语言与专属语言

**四职业通用（7 种）**：block（84）、damage（77）、draw（66）、special:regenerate（19）、special:strength（16）、special:dexterity（13）、special:burn（9）。这 7 种占全池机制使用总量（472 卡次）的 60.2%，是所有人都会说的普通话。

**三职业通用**：resonance_gain（缺疯先知）、heal（缺震语者——震语者一张 heal 都没有）、gaze_cost（缺疯先知，且维护者只有 1 张）。

**两职业**：resonance_cost（下潜+震语）、resonance_drain（下潜+维护）、special:weak（dive_0030、cng_0037）、special:frail（dive_0022、trem_0034）。

**单职业独占**：special:poison 只有 anm_0039；special:delete_random 只有 trem_0022；gaze_gain 只有 trem_0055、trem_0066；special:gaze_reduce 只有 trem_0027、trem_0029；special:rule_bypass 只有 share_0001。

结论：**真正的「职业身份语言」只有共振与凝视两条，而它们各自只被 1.5 个职业说过**——共振由震语者说满、下潜者说一半、维护者只压不花（gain 3 张、drain 3 张、cost 0 张）、疯先知完全沉默；凝视基本是震语者一个人的方言（15 张 gaze_cost 里 10 张是 trem）。

## 3. 被边缘化的机制（总使用 ≤3 次）

| 机制 | 总数 | 卡 | 本来想干什么 |
|---|---|---|---|
| special:exhaust | 3 | dive_0003、trem_0070、trem_0071 | 一次性爆发/弃用换临时收益，「打出去就没了」的取舍轴 |
| special:thorns | 3 | dive_0019、dive_0065、cng_0025 | 反伤流派，配合维护者高格挡本应成立 |
| special:weak | 2 | dive_0030、cng_0037 | 减伤 debuff，全池只有 2 张攻击附带 |
| special:frail | 2 | dive_0022、trem_0034 | 加伤 debuff，同样只有 2 张 |
| gaze_gain | 2 | trem_0055、trem_0066 | 凝视的自我膨胀——但全池没有任何「凝视高有好处的卡」承接它 |
| special:gaze_reduce | 2 | trem_0027、trem_0029 | 凝视的刹车，说明设计里承认凝视是负债 |
| special:delete_random | 1 | trem_0022 | 随机删牌（删的是牌池里的牌），唯一的牌库编辑机制 |
| special:poison | 1 | anm_0039 | 中毒 DoT，做了机制没做流派 |
| special:rule_bypass | 1 | share_0001 | 绕过某条层规则的钥匙，全局只有这一把 |

边缘化机制的共同点：**它们都是「单点」而不是「轴」**。poison 只有 1 张就构不成 DoT 流派；weak/frail 加起来 4 张，撑不起一个 debuff 体系；thorns 3 张分属两个职业，谁也组不成反伤队。这些机制每一个都是设计者动过念头的证据，但全部停在「各发一张」的程度。

## 4. 复杂度：每张卡叠几个机制

分布：1 种机制 124 张（46.4%）、2 种 88 张（33.0%）、3 种 48 张（18.0%）、4 种 7 张（2.6%）；全池平均 1.77。

4 机制的 7 张顶配：dive_0030（伤害+全体+gaze_cost3+weak2，rare lock 卡「抗共振司·镇爆弹」）、trem_0014（共振+4、gaze_cost3、regenerate5 的「听地神脉搏」）、trem_0023（伤害12+resonance_cost5+burn4 的「震语：沸息」）、trem_0034、trem_0058（gaze_cost8 换 strength2+dexterity2 的「静底·深阅」）、trem_0070、trem_0082。其中 6 张是震语者——**震语者承担了全游戏几乎全部的机制复合实验**。

3 机制的有 anm_0011（伤害+burn）、anm_0020 与 anm_0027（格挡+resonance_lock 双子）、anm_0039（伤害+poison）、anm_0041（regenerate2+strength1 的 power 卡「保运行优先级」）等。疯先知最复杂的一档就停在 2 机制（如 cng_0037「影语」伤害9+weak2）。

顺带发现的两个异常（后面 T321 会展开）：trem_0014「听地神脉搏」的升级按引擎规则是**追加**一条 regenerate2（[engine/core.js:981]，special 为 concat 而非替换），即升级后再生总量 5+2；dive_0081、dive_0082、dive_0083、trem_0081、trem_0082、trem_0083 这 6 张卡根本没有 upgrade 字段，无法升级。

## 5. 骨架结论

1. **四职业里有两个半共用同一副骨架**：疯先知（1.34）与维护者（1.58）是「基础四动作 + 少量状态」的减配版，下潜者（1.80）加了半条共振线，只有震语者（2.11）长出了自己的东西。
2. **资源层名存实亡**：全池 267 张卡里，读到或写过共振的卡 54 张（含 resonance_lock 6 张，与凝视卡有 4 张交集）、读到或写过凝视的卡 19 张，而这两条资源恰好是引擎里唯一有阈值反应的资源（共振跨档触发 MODE_REACTION，见 [engine/core.js:29]）。资源的核心性与其卡池占比严重不匹配——疯先知对全游戏最重要的资源系统参与度是 0。
3. **状态层只有 7 种且合计 64 卡次**（regenerate 19 + strength 16 + dexterity 13 + burn 9 + thorns 3 + weak 2 + frail 2），真正成轴的只有 regenerate/strength/dexterity/burn 四条，weak/frail/thorns/poison 都是单点。
4. **代价层（cost_type）倒是四职业都有个性**：下潜者 vitality 10 张、震语者 memory 10 张、维护者 heal 侧重、疯先知零代价（49/50 张 none）——前三个职业在「付出什么」上区分度尚可，唯独疯先知连代价系统也没接入。

一句话：**这套卡池的多样性主要靠「数值与文案」撑着，机制语言在四个职业里只有一套是完整的，其余是它的裁剪版。**

## 决定记录

- 「机制」的操作定义取 effect 顶层键 + special.code（去 target/hits），与 mechanisms.md 口径核对一致；mechanisms.md 漏了 share_0001 的 rule_bypass，本文按 23 种计，但正文沿用其 22 行表的数据以保持可对照。
- mechanisms.md 表头写作「共鸣」，任务书与引擎注释（core.js）写作「共振」，本文统一用「共振」指 resonance_*，引用原表时保留其写法。
- trem_0014 升级为追加条目、6 张卡无 upgrade 字段两处异常未改动任何数据（本任务禁改 json），只记录，留待 T321 定性。
- 卡数按 267（含 shared）统计；任务书说「266 张」，差 1 即 share_0001，未深究导出口径。
