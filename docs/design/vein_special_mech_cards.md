# T411 · 特殊机制卡清单（lock / gaze / resonance）

> 数据源：`cards/*.json`（219 张）。机制入口覆盖 cost_type / effect 键 / special code 三个层面（定义见文末）。
> 一张卡可用多个机制，在每个机制下各出现一行。复算：`python data/audit/gen_t411.py`。

## lock（本层一次）（9 张卡）

| id | 名字 | 角色 | 数值 |
|---|---|---|---|
| dive_0015 | 星髓矿业·爆破执照 | 下潜者 | cost_type=lock |
| dive_0030 | 抗共振司·镇爆弹 | 下潜者 | cost_type=lock |
| dive_0063 | 抗共振司·静音瓦 | 下潜者 | cost_type=lock |
| dive_0075 | 深红资源集团·地契 | 下潜者 | cost_type=lock |
| dive_0080 | 渊光重工·断路闸 | 下潜者 | cost_type=lock |
| trem_0011 | 震台石碑 | 震语者 | cost_type=lock |
| trem_0014 | 听地神脉搏 | 震语者 | cost_type=lock |
| trem_0046 | 震语：舍字 | 震语者 | cost_type=lock |
| anm_0024 | 协议：库存封存 | 维护者 | cost_type=lock |

## mark 代价（打出凝视+1）（7 张卡）

| id | 名字 | 角色 | 数值 |
|---|---|---|---|
| dive_0018 | 墟盐 | 下潜者 | 凝视 +1 |
| trem_0028 | 涌喉·光池倒影 | 震语者 | 凝视 +1 |
| trem_0030 | 震语：照骨 | 震语者 | 凝视 +1 |
| trem_0037 | 相石·初刻 | 震语者 | 凝视 +1 |
| trem_0067 | 五脉符（缺位） | 震语者 | 凝视 +1 |
| anm_0050 | 主控密钥（烧毁） | 维护者 | 凝视 +1 |
| cng_0050 | 疯先知的笔记 | 疯先知 | 凝视 +1 |

## gaze_cost（凝视门槛）（15 张卡）

| id | 名字 | 角色 | 数值 |
|---|---|---|---|
| dive_0011 | 辐射弹 | 下潜者 | gaze_cost=3 |
| dive_0024 | 深红资源集团·钻探平台 | 下潜者 | gaze_cost=4 |
| dive_0030 | 抗共振司·镇爆弹 | 下潜者 | gaze_cost=3 |
| dive_0082 | 按规程应答 | 下潜者 | gaze_cost=1 |
| trem_0010 | 震语：三震 | 震语者 | gaze_cost=2 |
| trem_0013 | 震语：崩齿 | 震语者 | gaze_cost=4 |
| trem_0014 | 听地神脉搏 | 震语者 | gaze_cost=3 |
| trem_0030 | 震语：照骨 | 震语者 | gaze_cost=4 |
| trem_0056 | 震语：回望 | 震语者 | gaze_cost=5 |
| trem_0057 | 相石·对视 | 震语者 | gaze_cost=3 |
| trem_0058 | 静底·深阅 | 震语者 | gaze_cost=8 |
| trem_0059 | 震台石碑（注视） | 震语者 | gaze_cost=2 |
| trem_0060 | 五脉符（逆位） | 震语者 | gaze_cost=6 |
| trem_0078 | 观红（对影） | 震语者 | gaze_cost=3 |
| anm_0018 | 威胁等级·评估员 | 维护者 | gaze_cost=3 |

## gaze_gain（加凝视）（2 张卡）

| id | 名字 | 角色 | 数值 |
|---|---|---|---|
| trem_0055 | 震语：直视 | 震语者 | gaze_gain=1 |
| trem_0066 | 震语：回声定位 | 震语者 | gaze_gain=1 |

## gaze_reduce（降凝视）（3 张卡）

| id | 名字 | 角色 | 数值 |
|---|---|---|---|
| trem_0027 | 震语：明目 | 震语者 | gaze_reduce=1 |
| trem_0029 | 观红（深相） | 震语者 | gaze_reduce=2 |
| u_0009 | 倒转圣痕 | 通用 | gaze_reduce=2 |

## resonance_gain（攒共振）（26 张卡）

| id | 名字 | 角色 | 数值 |
|---|---|---|---|
| dive_0011 | 辐射弹 | 下潜者 | resonance_gain=4 |
| dive_0014 | 震髓探测器 | 下潜者 | resonance_gain=2 |
| dive_0025 | 震频器 | 下潜者 | resonance_gain=2 |
| dive_0028 | 震频器（校准） | 下潜者 | resonance_gain=4 |
| dive_0042 | 震髓探测器（阵列） | 下潜者 | resonance_gain=5 |
| dive_0044 | 抗共振司·导波索 | 下潜者 | resonance_gain=4 |
| dive_0047 | 深红资源集团·谐振井 | 下潜者 | resonance_gain=6 |
| dive_0067 | 震髓残响 | 下潜者 | resonance_gain=3 |
| dive_0071 | 渊光重工·灯序表 | 下潜者 | resonance_gain=1 |
| trem_0002 | 听震 | 震语者 | resonance_gain=3 |
| trem_0004 | 震语：回响 | 震语者 | resonance_gain=2 |
| trem_0006 | 震台石碑（拓片） | 震语者 | resonance_gain=1 |
| trem_0014 | 听地神脉搏 | 震语者 | resonance_gain=4 |
| trem_0037 | 相石·初刻 | 震语者 | resonance_gain=3 |
| trem_0038 | 相石·满录 | 震语者 | resonance_gain=2 |
| trem_0047 | 震台石碑（残诵） | 震语者 | resonance_gain=4 |
| trem_0057 | 相石·对视 | 震语者 | resonance_gain=5 |
| trem_0061 | 震语：数息 | 震语者 | resonance_gain=2 |
| trem_0069 | 震台石碑（新碑） | 震语者 | resonance_gain=3 |
| trem_0070 | 震语：低语 | 震语者 | resonance_gain=1 |
| trem_0071 | 震语：试井 | 震语者 | resonance_gain=2 |
| trem_0082 | 不许关闭 | 震语者 | resonance_gain=1 |
| anm_0006 | 库存盘点 | 维护者 | resonance_gain=2 |
| anm_0013 | 料径校准 | 维护者 | resonance_gain=4 |
| anm_0048 | 运输井规程 | 维护者 | resonance_gain=3 |
| u_0008 | 灰烬测振仪 | 通用 | resonance_gain=2 |

## resonance_cost（花共振）（7 张卡）

| id | 名字 | 角色 | 数值 |
|---|---|---|---|
| dive_0026 | 震髓装药 | 下潜者 | resonance_cost=5 |
| dive_0029 | 红渊研究院·震谱仪 | 下潜者 | resonance_cost=8 |
| dive_0046 | 星髓矿业·深部震源 | 下潜者 | resonance_cost=15 |
| trem_0013 | 震语：崩齿 | 震语者 | resonance_cost=6 |
| trem_0023 | 震语：沸息 | 震语者 | resonance_cost=5 |
| trem_0034 | 震语：断流 | 震语者 | resonance_cost=6 |
| trem_0075 | 历法刻盘（倒页） | 震语者 | resonance_cost=6 |

## resonance_drain（泄共振）（5 张卡）

| id | 名字 | 角色 | 数值 |
|---|---|---|---|
| dive_0070 | 回收员的账本 | 下潜者 | resonance_drain=5 |
| anm_0008 | 报废清单 | 维护者 | resonance_drain=5 |
| anm_0017 | 回收协议·总则 | 维护者 | resonance_drain=8 |
| anm_0049 | 撤销程序残片 | 维护者 | resonance_drain=6 |
| u_0010 | 谐振垫层 | 通用 | resonance_drain=2 |

## resonance_lock（共振锁定）（5 张卡）

| id | 名字 | 角色 | 数值 |
|---|---|---|---|
| dive_0016 | 共振抑制仪 | 下潜者 | 锁定 |
| dive_0023 | 抗共振司·静默规程 | 下潜者 | 锁定 |
| trem_0019 | 禁声日 | 震语者 | 锁定 |
| anm_0020 | 协议：静默段 | 维护者 | 锁定 |
| anm_0027 | 协议：静默段·延长 | 维护者 | 锁定 |

## 定义（复算口径）

- lock：`cost_type=="lock"`（引擎：本层只能用一次）
- mark：`cost_type=="mark"`（打出时凝视 +1）
- gaze_cost / gaze_gain：同名 effect 键；gaze_reduce：special code
- resonance_gain / resonance_cost / resonance_drain：同名 effect 键；resonance_lock：special code
- 合计 79 行（含一卡多机制重复计入）；涉及去重卡数 71。
