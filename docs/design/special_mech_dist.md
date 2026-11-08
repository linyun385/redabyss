# T503 · lock / 凝视 / 共振 三种特殊机制的使用分布

> 数据源：`cards/*.json`（219 张）。定义见文末。复算：`python data/audit/gen_t503.py`。

- **lock（本层一次）**：9 张卡用到（去重 id 数 9）；按角色：下潜者 5、维护者 1、震语者 3
  - 数值证据：`dive_0015` 星髓矿业·爆破执照(cost_type=lock), `dive_0030` 抗共振司·镇爆弹(cost_type=lock), `dive_0063` 抗共振司·静音瓦(cost_type=lock), `dive_0075` 深红资源集团·地契(cost_type=lock), `dive_0080` 渊光重工·断路闸(cost_type=lock), `trem_0011` 震台石碑(cost_type=lock), `trem_0014` 听地神脉搏(cost_type=lock), `trem_0046` 震语：舍字(cost_type=lock), `anm_0024` 协议：库存封存(cost_type=lock)
  - 平均数值：—（仅统计带数字的用法，n=0）
  - 定位：给大数值动作定价——「这层只给你一次机会」。
- **凝视（mark 代价 + 效果键）**：27 张卡用到（去重 id 数 26）；按角色：下潜者 5、疯先知 1、维护者 2、通用 1、震语者 18
  - 数值证据：`dive_0011` 辐射弹(gaze_cost=3), `dive_0018` 墟盐(cost_type=mark(打出凝视+1)), `dive_0024` 深红资源集团·钻探平台(gaze_cost=4), `dive_0030` 抗共振司·镇爆弹(gaze_cost=3), `dive_0082` 按规程应答(gaze_cost=1), `trem_0010` 震语：三震(gaze_cost=2), `trem_0013` 震语：崩齿(gaze_cost=4), `trem_0014` 听地神脉搏(gaze_cost=3), `trem_0027` 震语：明目(gaze_reduce=1), `trem_0028` 涌喉·光池倒影(cost_type=mark(打出凝视+1)), `trem_0029` 观红（深相）(gaze_reduce=2), `trem_0030` 震语：照骨(cost_type=mark(打出凝视+1)), `trem_0030` 震语：照骨(gaze_cost=4), `trem_0037` 相石·初刻(cost_type=mark(打出凝视+1)) … 等 13 条
  - 平均数值：3.05（仅统计带数字的用法，n=20）
  - 定位：凝视既是代价（cost_type=mark）又是门槛（gaze_cost）又能被管理（gaze_reduce）。
- **共振（gain / cost / drain / lock）**：43 张卡用到（去重 id 数 43）；按角色：下潜者 15、维护者 8、通用 2、震语者 18
  - 数值证据：`dive_0011` 辐射弹(resonance_gain=4), `dive_0014` 震髓探测器(resonance_gain=2), `dive_0016` 共振抑制仪(resonance_lock), `dive_0023` 抗共振司·静默规程(resonance_lock), `dive_0025` 震频器(resonance_gain=2), `dive_0026` 震髓装药(resonance_cost=5), `dive_0028` 震频器（校准）(resonance_gain=4), `dive_0029` 红渊研究院·震谱仪(resonance_cost=8), `dive_0042` 震髓探测器（阵列）(resonance_gain=5), `dive_0044` 抗共振司·导波索(resonance_gain=4), `dive_0046` 星髓矿业·深部震源(resonance_cost=15), `dive_0047` 深红资源集团·谐振井(resonance_gain=6), `dive_0067` 震髓残响(resonance_gain=3), `dive_0070` 回收员的账本(resonance_drain=5) … 等 29 条
  - 平均数值：4.00（仅统计带数字的用法，n=38）
  - 定位：资源循环——攒（gain）、花（cost）、泄（drain）、锁（resonance_lock）。
## 附：special 全部 code 分布（找只被 1 张卡用的机制）

| code | 用卡数 | 卡 | 只此一张？ |
|---|---|---|---|
| delete_random | 1 | `trem_0022` 回归墟骨 | **是 ← 死机制候选** |
| poison | 1 | `anm_0039` 菌婪者组织样本 | **是 ← 死机制候选** |
| rule_bypass | 1 | `share_0001` 强行供能 | **是 ← 死机制候选** |
| resonance_gain | 1 | `u_0009` 倒转圣痕 | **是 ← 死机制候选** |
| frail | 2 | `dive_0022` 硬矿钻（重型）、`trem_0034` 震语：断流 |  |
| exhaust | 3 | `dive_0003` 曜元、`trem_0070` 震语：低语、`trem_0071` 震语：试井 |  |
| thorns | 3 | `dive_0019` 抗共振司·锚桩、`dive_0065` 渊光重工·接地缆、`cng_0025` 沉默权柄 |  |
| weak | 3 | `dive_0030` 抗共振司·镇爆弹、`cng_0037` 影语、`u_0013` 散落的铅字 |  |
| gaze_reduce | 3 | `trem_0027` 震语：明目、`trem_0029` 观红（深相）、`u_0009` 倒转圣痕 |  |
| resonance_lock | 5 | `dive_0016` 共振抑制仪、`dive_0023` 抗共振司·静默规程、`trem_0019` 禁声日、`anm_0020` 协议：静默段、`anm_0027` 协议：静默段·延长 |  |
| retain | 5 | `dive_0081` 气闸的规程、`trem_0018` 静日、`trem_0039` 埋骨布、`trem_0082` 不许关闭、`anm_0043` 静默段徵章 |  |
| dexterity | 10 | `dive_0007` 渊光重工·导光索、`dive_0017` 星髓矿业·深地车、`dive_0052` 光苔矿（盆栽）、`trem_0020` 静日触杖、`trem_0058` 静底·深阅、`trem_0067` 五脉符（缺位）、`anm_0016` 主控授权·安全线、`anm_0050` 主控密钥（烧毁）、`cng_0050` 疯先知的笔记、`u_0011` 活水引泉 |  |
| burn | 10 | `dive_0033` 圣火武器、`dive_0034` 反走私局·焚烧记录、`trem_0017` 震语：焚名、`trem_0023` 震语：沸息、`trem_0024` 震语：熔名、`trem_0080` 震语：长夜、`anm_0011` 焊接臂·民用型、`cng_0034` 火母的怀抱、`u_0008` 灰烬测振仪、`u_0012` 双芯灯管 |  |
| strength | 13 | `dive_0017` 星髓矿业·深地车、`dive_0020` 黑曜采掘·加班条例、`dive_0035` 深红资源集团·地热井口、`dive_0056` 死亡合同（增补条款）、`dive_0075` 深红资源集团·地契、`trem_0044` 相石·封忆、`trem_0058` 静底·深阅、`trem_0067` 五脉符（缺位）、`anm_0015` 主控授权·工程线、`anm_0035` 超频保养、`anm_0041` 保运行优先级、`anm_0050` 主控密钥（烧毁）、`cng_0019` 王权梦 |  |
| regenerate | 16 | `dive_0005` 氧气再生器、`dive_0018` 墟盐、`dive_0032` 曜元（缓释）、`dive_0037` 红渊研究院·水样档案、`dive_0038` 氧气再生器（满压）、`dive_0076` 曜元（夜班型）、`trem_0014` 听地神脉搏、`trem_0015` 触温、`trem_0016` 喷息·热池边、`trem_0031` 尝水、`trem_0033` 涌喉·水契、`trem_0035` 尝水（深井）、`anm_0040` 协议：例外条款、`anm_0041` 保运行优先级、`cng_0028` 五十日、`cng_0042` 火母的回应 |  |

## 结论

- 只被 1 张卡用到的 special code：`delete_random`、`poison`、`rule_bypass`、`resonance_gain` —— 共 4 个。它们大概率是「为一张卡单独写的机制」，引擎里可能各只有一处分支（只报告，不改）。
- 三族里最重的是共振（43 次用法 / 43 张卡），凝视次之（27 次 / 26 张），lock 最轻（9 次 / 9 张）。与 T400 §2.2 的机制归属一致：共振/凝视是跨角色经济，lock 是低频大招的定价器。

定义：lock 族 = `cost_type=="lock"`；凝视族 = `cost_type=="mark"` ∪ `gaze_cost` ∪ `gaze_gain` ∪ special`gaze_reduce`；共振族 = `resonance_gain` ∪ `resonance_cost` ∪ `resonance_drain` ∪ special`resonance_lock`。一张卡可同入多族（按用法计次）。
