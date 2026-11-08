# MAPGEN_DESIGN.md — 地图生成框架设计（T54 产出）

> 需求唯一来源：`docs/MAPGEN_BRIEF.md`（原文未改写，本文件只是展开）。
> 参数唯一来源：`tools/mapgen_spec.json`（本文件与后续任务都从它读参数，不各写一份）。
> 本文是**设计文档**：不含任何游戏代码实现；`web/index.html`、`engine/`、`cards/` 零改动。
> 依据标注约定：【需求】=出自 MAPGEN_BRIEF；【既有】=本项目既有设定/代码；【假设】=我的设计假设（可调参）。

---

## 0. 与既有设定的映射（先看这张，再读正文）

### 0.1 生态枚举（8 种）↔ 既有八层

生态枚举与八层**一一对应**：每层的档案生态（docs/LAYERS.md）就是该生态的母本。D1/D8 在设定里「无（生物）生态」，地图上仍是一种生态——**非生物生态**（设定原文：D1「没有生态。真空、强辐射」；D8「无生态。只有嗜热菌在谐振器的余光里」），不推翻设定。

| eco id | 名称 | 母本层 | 主脉亲和 | 层规则（既有） | 生态内容（LAYERS.md 摘要） |
|---|---|---|---|---|---|
| `eco_surface` | 死寂壳层 | D1 地表死寂区 | —（光脉失效） | `no_light` | 真空、强辐射、休眠孢子 |
| `eco_cold` | 沉积冷洞 | D2 外层冷洞 | tremor | `dim` | 碎屑雪、休眠两栖类、慢时间 |
| `eco_arid` | 泉眼干旱区 | D3 干旱空洞区 | water（枯竭） | `dry` | 泉眼、缓步动物、水按滴记 |
| `eco_sea` | 红蕨空洞海 | D4 稳定空洞海 | light | `bright` | 倒挂红蕨林、气囊藻毯、滤食鱼群 |
| `eco_vent` | 热泉裂带 | D5 热泉裂带 | heat | `heat_tick` | 硫菌丘、管虫、喷发周期 |
| `eco_rad` | 辐射荒漠 | D6 辐射矿石区 | mineral | `rad_tick` | 辐射合成菌、重金属鳞甲壳 |
| `eco_core` | 核心高热区 | D7 核心高热区 | heat | `burn_hand` | 嗜热菌毯、超临界流体 |
| `eco_nexus` | 核心回路 | D8 红渊核心 | — | `time_loop` | 谐振器走廊、八万年作息 |

脉亲和的依据是游戏内 LAYER_NOTE（D1 光脉点不亮、D2 震脉清晰、D3 水脉枯竭、D4 光脉更亮）与层规则字段【既有】。亲和只用于内容绑定的默认排序权重，不新增引擎机制。

### 0.2 节点类型映射

| 需求原文 | 本设计 type | 与既有类型的关系 |
|---|---|---|
| 战斗 | `combat` | 同既有 |
| 精英 | `elite` | 同既有 |
| 随机 | `random` | **新类型**。既有「营火 campfire」并入它：点开时按 `random.mix` 权重随机落成 营火/事件/商店 之一（权重见参数表）【假设】。既有 6 类型里的 campfire 不再单独占节点格 |
| 商店 | `shop` | 同既有 |
| 事件 | `event` | 同既有（「现在点进去触发的那块」） |
| （运行时替换） | `boss` | 生成阶段**不产生** boss 类型节点；仅运行时跨带判定命中后替换（见 §8）【需求·已确认2】 |
| 最终 BOSS | `finalBoss` | 唯一，生成阶段确定（见 §2 步骤4）【需求·五】 |

### 0.3 与现行地图结构的关系

- 现行：每层一张小图（`layers/layers.json` 的 rows，4 行 × 1–2 节点），层间由「打完 boss 进下一层」衔接【既有】。
- 新设计：**整局一张大图**，`band = 层`（D1 最上 … D8 最下），现行 rows 结构被生成器输出取代；层的 rule/no_light 等机制**照旧按 band 生效**（引擎 LAYERS 表不动）【需求·已确认1】。
- 备份：旧地图已备份为 `web/index.html.bak-mapgen-v0-20261030-1834`，新地图成为默认【需求·已确认3】。

### 0.4 与「已确认」条款的关系（防日后误读）

- 需求原文二「从上一个深度线滑到下一个深度线的事件块**必然是 BOSS**」→ 已被已确认条款 2 修正为：**首次跨带必 BOSS，之后按递减概率判定**。本文按已确认条款执行。
- T54 任务书流程步骤 4「带间连接节点强制为 boss」→ 按已确认前提（「BOSS 不在生成阶段决定」）落地为：**生成阶段只打 crossBand 标记，运行时替换**（§8）。生成结果里除 finalBoss 外没有任何 boss 类型节点。
- 备份后直接替换，不做开关【需求·已确认3】。

---

## 1. 数据模型（JSON 伪结构）

```jsonc
Region = {
  "w": 14, "h": 48,                 // 网格宽高（格）。h 必须是 8 的倍数【假设】
  "bandRows": 6,                    // = h / 8，每带行数（派生值）
  "cells": [ { "x":0, "y":0 } … ],  // w*h 个单元格（按行铺平也可，实现自选）
  "ecoOf": [ "eco_cold" … ],        // ecoOf(cell) → eco id，长度 w*h
  "weight": [ 0.72 … ],             // weight[cell] = 生成时该 cell 被其 eco 占据的权重
                                    //   （= weightTable[ecoOf(cell)][band(cell)]，仅作存档/调试用）
  "nodes": [ Node … ],
  "edges": [ Edge … ],
  "startId": "n0",                  // 唯一起点（band 1）
  "finalBossId": "n63",             // 唯一 finalBoss（band 8 最底行）
  "seed": 12345                     // 本图使用的最终种子（含重试偏移）
}

Node = {
  "id": "n17",
  "type": "combat|elite|random|shop|event|finalBoss",
                                    // 生成阶段不出 'boss'；boss 只在运行时替换出现（§8）
  "x": 7, "y": 23,                  // 格坐标。y=0 最上，y=h-1 最下
  "band": 4,                        // = bandOf(y)（公式见 §2 步骤4，生成后冗余存储便于断言）
  "eco": "eco_sea",                 // = ecoOf(cell(x,y))，冗余存储
  "binding": {                      // 内容绑定指针（步骤5 填充）
    "enemyPool": ["enemy_d4_01"],   // 敌人池（enemies/all.json 的 id）
    "elitePool": [ "…" ],
    "bossPool":  [ "…" ],           // 仅运行时替换为 boss 时消费
    "eventPool": [ "event_d4_2" ],
    "shopTier": 2
  },
  "crossBandIn": true               // 是否有跨带入边（运行时 BOSS 判定的对象标记）
}

Edge = {
  "from": "n17", "to": "n31",
  "dx": 2, "dy": 3,                 // 位移（格）。dy ≥ 1，方向恒向下【需求·二】
  "len": 3,                         // = max(|dx|, dy)，1..k
  "angle": 33.7,                    // = atan2(|dx|, dy)（度，向下为 0，保留 1 位小数）
  "crossBand": false                // band(from) ≠ band(to) 时为 true（运行时 BOSS 标记）
}

Band = {                             // 深度线：带 b 与带 b+1 的分界（b = 1..7）
  "index": 4,
  "topY": 18, "bottomY": 23,         // 该带占据的行区间（闭区间）
  "lineY": 23.5                      // 深度线位置（带底与下带顶之间，仅作图示用）
}
```

`band = f(y)` 公式（写死）：

```
bandRows = h / 8
depthFromBottom(y) = h - 1 - y          // 距底格的距离【需求·二「距底格的距离=深度」】
band(y) = 8 - min(7, floor(depthFromBottom(y) / bandRows))
```

验证（h=48, bandRows=6）：y=47→带8；y=42→带8；y=41→带7；y=6→带2；y=0→带1。✓

---

## 2. 生成流程（五步）

总入口 `generate(seed, params) → Region`（完整伪代码见 §7）。失败一律抛 `GenError(reason)`，由重试循环接住；**重试上限内全部失败则报错并列出各原因计数，绝不静默返回半成品**【需求·任务书】。

### 步骤 1：生态生长（多源生长）

- **输入**：seed、`eco.count`、`weightTable`（由 `weight.canonical/adjacent/rest` 构造）、`eco.kappa`、`eco.minPatchArea`、`eco.maxComponents`。
- **做法**：
  1. 构造 `weightTable[eco][band]`（T72 v1.5 重定）：每带内，母本生态权重 `home = 0.45`（范围 0.40–0.50），**每个**相邻带生态 `adjacentEach = 0.20`（范围 0.15–0.25，n=1 时顶格 0.25），其余生态均分剩余。每带内和为 1。
     再按**层规则调制**（`spec.ruleModulation` × `ruleByBand`，数据镜像 layers.json 的 rule 字段——不许硬编码）：如 no_light 带发光生态（light 亲和）×0.5、dry 带水亲和 ×0.6、bright 带光亲和 ×1.25；调制后每带归一。
     参数依据：T72 用户拍板（主场 0.40–0.50、邻带 0.15–0.25、每带生态数 2–4、单带最大占比 ≤60%）——原 0.72 主场权重造成「一层一个环境」，已废弃。
  2. 每种生态按其在全图的权重质量抽样一个「老家带」，在带内随机取一个**源点**。
  3. 多源生长（优先队列泛洪）：从 8 个源点同时扩散，进入相邻格的代价
     `c = 已走代价 + (1 − weightTable[eco][band(目标格)]) × (3 × κ) + noise × (1 − κ)`，
     其中 noise = rng.uniform(0,1)。κ→1：跨权重区扩张极贵 → 生态紧成一片；κ→0：噪声主导 → 碎斑。【假设公式，κ 语义来自需求「聚合程度决定权重」】
  4. 后处理：面积 < `minPatchArea` 的连通块并入**共享边界最长的邻居生态**；每个生态的连通分量数 > `maxComponents` 时，把其最小分量并入邻居。若合并后仍违例 → `GenError('eco.minPatchArea' / 'eco.maxComponents')`。
- **输出**：`ecoOf[]`（每格生态）、`weight[]`。
- **失败条件**：合并后仍有 < minPatchArea 的块，或某生态分量数仍 > maxComponents，或某生态完全没有格（源点被完全吞并）。

### 步骤 2：事件格布点（配额 + 蓝噪声分散）

- **输入**：`ecoOf[]`、各带配额表（`quota`，见参数表）、`node.minSameTypeDist`（D）。
- **做法**：对每带 b，按配额逐类型撒点。 rejection sampling：在带行区间内均匀取格，要求
  ① 该格无任何节点（节点不共格）；
  ② 与**同带同类型**的已有节点曼哈顿距离 ≥ D（「两个同类事件尽量不相邻」【需求·二】）；
  ③ 不占用起点格 / finalBoss 格（这两格先于普通撒点预留）。
  每格最多尝试 50 次仍放不下 → `GenError('place.<type>.<band>')`。
- **预留格**：起点 = band 1、y=0 行、x 取带内中间三格之一（type 计入 D1 combat 配额）【既有：现行游戏开局即战斗】；finalBoss = band 8、y=h−1 行、x 中间格。
- **行覆盖规则**【假设，为步骤 3 的跨带连通服务】：每带最上面两行与最下面两行**至少各有 1 个节点**。
- **输出**：`nodes[]`（含起终两格）。
- **失败条件**：任一带任一类型配额在 50 次尝试内放不下。

### 步骤 3：连线（向下的 DAG）

- **输入**：`nodes[]`、`edge` 参数组（maxLen k、角度集合、出度 1..3、maxInDeg）。
- **位移表**（角度集合固定 {0, ±35, ±60, ±85}【需求·任务书例值】；网格量化后的实际位移候选）：

  | 名义角 | 位移候选 (dx, dy) | 实际角（atan2\|dx\|,dy） |
  |---|---|---|
  | 0° | (0,1) (0,2) (0,3) | 0° |
  | ±35° | (±1,2) (±2,3) | 26.6° / 33.7° |
  | ±60° | (±2,1) (±3,2) | 63.4° / 56.3° |
  | ±85° | (±4,1) (±5,1) | 76.0° / 78.7° |

  说明：dy ≥ 1 恒成立（总体向下【需求·二】）；±85 档在 w=14 的网格上量化到 76–79°，网格再宽也不会超过 79°——「左右直着都行」由 ±60/±85 两档的大横移承担【假设·量化说明】。边长 len = max(|dx|,dy) ∈ 1..k。
- **做法**（三阶段 + 补丁）：
  - A（保入边，自上而下）：对除起点外每个节点 v，在「位移表可达且路径无遮挡」的上方节点里取最近者连一条 u→v。入度上限 `node.maxInDeg`。
  - B（保出边，自下而上）：对除 finalBoss 外每个节点 u，若无出边，同理向下连 1 条。出度上限 3【需求·二「出边 1–3 条」】。
  - C（补充分叉，自上而下）：对每个出度 < 3 的节点，以概率补第 2/3 条出边（目标仍是位移表可达、路径无遮挡、y 更大的节点），增加路线多样性【需求·「方向随机」】。
  - D（保跨带）：对每个带边界 b（1..7），若没有一条 from 在带 b、to 在带 b+1 的边，则取带 b 最靠底的节点与带 b+1 最靠顶的节点补一条；补不上 → `GenError('connect.crossband.<b>')`。
- **路径无遮挡判定**：把 (dx,dy) 用 Bresenham 栅格化，边经过的**中间格**不得含任何节点格、不得与其他边的中间格重叠（禁止交叉【需求·任务书】）；两条边共享**端点**（汇聚）是允许且必需的（死路的来源，见 §5）。
- **输出**：`edges[]`（每条含 dx/dy/len/angle/crossBand）。
- **失败条件**：A/B/D 任一阶段补不上边；或栅格化冲突无法绕开。

### 步骤 4：深度线与 BOSS 标记

- **输入/输出**：`nodes[]` + §1 公式 → 每个节点填 `band`；边填 `crossBand = (band(from) ≠ band(to))`；被跨带边指到的节点填 `crossBandIn = true`。纯函数，无失败分支。
- **finalBoss**：布点阶段已预留的 band 8 最底行中间格节点，type 置 `finalBoss`。生成阶段**不做**其他 boss 决定【需求·已确认2】。
- **不变量检查**：见 §3（此处失败的 reason 进入重试）。

### 步骤 5：内容绑定（结构与默认值；实际表在 T58）

- **输入**：`ecoOf[]`、每节点 (eco, band)。
- **结构**：`binding[eco][band] → { enemyPool, elitePool, bossPool, eventPool, shopTier }`（字段见 §1 Node.binding）。
- **默认值（T58 交付前的回退链）**：按 eco+band 精确匹配 → 无则回退「该带的母本生态」→ 再回退「该生态的母本带」→ 仍空则 `GenError('binding.empty')`。池内容 = 既有数据按 layer 过滤（enemies/all.json、events/all.json 的 layer 字段；bossPool 取 tier==='boss' 含变体）【既有】。
- **shopTier 默认**：band 1–3 → 1，band 4–6 → 2，band 7–8 → 3【假设】。
- **失败条件**：回退链走完仍为空池。
- 备注：`eco.count=8 × band=8 = 64` 个组合的池覆盖与缺口盘点是 **T60 的输入**；本步只保证结构与回退链可断言。

---

## 3. 不变量（invariants，全部可断言；T55/T59 直接实现为断言）

| # | 不变量 | 断言写法 |
|---|---|---|
| I1 | 节点不共格；起终点各恰 1 个 | `new Set(nodes.map(n=>n.x+','+n.y)).size === nodes.length`；start/finalBoss 各 1 |
| I2 | 100% 可达 | 从 startId DFS（只沿边方向），所有节点都被访问到（等价于：除起点外每节点入度 ≥1 且连通）【需求·任务书】 |
| I3 | 出边下限 | 除 finalBoss 外每节点出度 ≥ 1（结构死路不存在；运行时死路来自汇聚，见 §5） |
| I4 | 无环 | 三色 DFS 或拓扑排序成功（构造上 y 严格增，此条是防御性断言） |
| I5 | y 严格单调向下 | 每条边 `to.y > from.y`【需求·二「总体向下」】 |
| I6 | finalBoss 唯一、可达、在最底 | type==='finalBoss' 恰 1 个；band===8 且 y===h−1 行；I2 覆盖可达【需求·五】 |
| I7 | 每带节点数 ≥ 配额 | `count(nodes in band b) >= quota[b] 总和`【需求·二】 |
| I8 | 同带同类型分散 | 同带同类型两节点曼哈顿距离 ≥ D（默认 2）【需求·二「尽量分散」+任务书 D 默认 2 格】 |
| I9 | 每条带边界可跨越 | 对 b=1..7，至少一条 crossBand 边 from.band===b ∧ to.band===b+1（保证能一路走到最底【需求·二】） |
| I10 | 无交叉边、不穿节点 | 任意两条边的中间格集合不相交；中间格不含任何节点格 |
| I11 | 出度上限 | 每节点出度 ≤ 3【需求·二】；入度 ≤ `node.maxInDeg` |
| I12 | 生态约束 | 每种 eco 至少 1 格；全局连通分量数 ≤ maxComponents；块面积 ≥ minPatchArea（=12，T72 降档） |
| I13 | 带级生态数 | 每带实现的生态数 ∈ [2, 4]（零例外） |
| I14 | 带级最大占比 | 单带最大生态占比 ≤ 0.60（零例外） |
| I15 | 相邻带交集 | 相邻两带共享生态 ≥1（D3 干旱咬进 D4 边缘） |
| I16 | 带内连通块 | 每带内同生态连通块 ≤3（验收口径 95 分位；validate 按 100% 强制） |

**重试**：任一不变量失败 → `GenError(reason)` → 换种子（seed + attempt）重来，上限 `retry.max = 20`【需求·任务书】；超限抛错并列出各 reason 计数，不许静默返回。

---

## 4. 可见性规则

- **定义**【需求·三】：`visible = visited ∪ neighbors(visited, depth=1)`，neighbors 沿**边**（无视方向）取 1 跳——「周边」= 与已触发节点有边相连的节点。
- **总图**：渲染 visible 子图（节点 + 其间的边）。
- **小图**（常驻）：玩家节点 + 其边邻居 + 玩家所在 eco 区块的轮廓。生态轮廓半径 `minimap.ecoRadius`（默认 3 格，曼哈顿）内以 ecoOf 上色【假设】。
- **数据层裁剪（防偷看）**【需求·三】：前端拿到的**永远是被裁剪后的副本**——
  `pruneForFrontend(region, visitedSet) → { nodes: [可见节点（含 binding）], edges: [两端皆可见的边] }`。
  未可见节点**不进入**传给渲染层的对象，也就不进 DOM——不是 CSS 藏起来。
  实现注记：单文件游戏没有服务端，做法是**闭包持有完整 Region**（生成函数返回一个带 `getVisible(visited)` 方法的状态对象，raw 数据不挂到 `window`/DOM 可达的属性上）。边界：JS 内存对开着 devtools 的玩家是可读的，本规则防的是「从 DOM 里偷看」，不含内存级对抗【假设·边界】。
- 迷雾**不因救援重置**（§5）、不因跨带重置；visited 集合是 run 级状态。

---

## 5. 死路救援规则

- **dead-end 判定**【需求·任务书】：玩家所在节点 u 满足 `u.type ≠ 'finalBoss'` 且 u 的全部出边终点都已 visited → 死路。（结构上出度 ≥1 由 I3 保证，所以死路只来自**路径汇聚**：岔路合流后无未访问出路。）
- **救援目标**【需求·四】：从「未访问节点」里挑**最近的可达入口**：
  候选 = 未访问节点 v 且存在已访问节点 x 有边 x→v（前沿节点）。
  排序键：(同带优先：band(v)===band(u) ? 0 : 1) → 曼哈顿距离 dist(u,v) → rng 决胜。
  玩家**立即转到**该节点（v 置 visited）【需求·四「立即转到此前还没走过的另一条路径」】。
- **代价（二选一、随机 50/50）**【需求·四】：
  - `penalty`：hp −`ceil(maxHp × rescue.hpPenaltyPct / 100)`（默认 10%）【假设数值】；
  - `ambush`：以当前带 enemyPool 触发一场随机战斗（走引擎既有 `startCombat`，战斗结算不改【红线】）。
- **免费声明**【需求·四】：救援**不消耗回合数、不重置迷雾**。
- **接口**（T57 消费）：
  `findRescueTarget(region, visited, playerNodeId) → nodeId | null`
  `rollRescueCost(rng, run) → { kind: 'penalty', hp: n } | { kind: 'ambush', pool: [...] }`
  若不存在候选（理论不可能：finalBoss 未到则必有未访问节点有入边——由 I2/I9 保证）→ 返回 null 并报错记录，不静默。

---

## 6. 参数表

完整机读版在 `tools/mapgen_spec.json`（唯一来源）。依据列：**需**=需求原文/任务书，**既**=既有设定，**假**=我的假设。

| 参数 | 默认 | 范围 | 影响 | 依据 |
|---|---|---|---|---|
| `grid.w` | 14 | 10–20 | 横向空间；太窄则 ±85° 档没得选 | 假 |
| `grid.h` | 48 | 40–64（8 的倍数） | 纵向密度；带行数 = h/8 | 假 |
| `eco.count` | 8 | 6–8 | 生态枚举数；8=层数一一对应 | 既 |
| `weight.canonical` | 0.72 | 0.5–0.9 | 带内母本生态占比；越高带越「纯」 | 假 |
| `weight.adjacent` | 0.20 | 0.05–0.35 | 相邻带生态渗入量 | 假 |
| `eco.kappa` | 0.7 | 0–1 | 聚合度：1=紧成一片，0=碎斑 | 需（语义）/假（公式） |
| `eco.minPatchArea` | 18 | 8–40 | 最小生态块面积（格） | 假 |
| `eco.maxComponents` | 2 | 1–3 | 每生态允许的连通分量数 | 需（连成一片）/假（数值） |
| `node.minSameTypeDist` (D) | 2 | 1–4 | 同带同类型最小曼哈顿距离 | 需（D 默认 2 来自任务书） |
| `node.maxInDeg` | 3 | 2–4 | 汇聚上限；影响死路频率 | 假 |
| `edge.outDeg` | 1–3 | — | 每节点出边数 | 需 |
| `edge.maxLen` (k) | 4 | 2–6 | 边长上限（格） | 需（1..k）/假（k 值） |
| `edge.angles` | {0,±35,±60,±85} | — | 方向档位 | 需（例值） |
| `retry.max` | 20 | 5–50 | 生成重试上限 | 需 |
| `boss.p0` | 0.5 | 0.3–1 | 第 2 次跨带的 BOSS 判定概率（第 1 次恒 1） | 假 |
| `boss.decay` | 0.6 | 0.3–1 | 每多一次跨带的概率乘子 | 假 |
| `boss.floor` | 0.1 | 0–0.2 | 概率下限 | 假 |
| `visibility.depth` | 1 | 1–2 | 「周边」的边跳数 | 需 |
| `minimap.ecoRadius` | 3 | 2–5 | 小图生态轮廓半径 | 假 |
| `rescue.hpPenaltyPct` | 10 | 5–20 | penalty 分支的扣血比例 | 假 |
| `rescue.ambushOdds` | 0.5 | 0.3–0.7 | ambush 分支概率（50/50） | 需（二选一随机）/假（数值） |
| `random.mix` | campfire .45 / event .40 / shop .15 | — | random 节点触发时的落点分布 | 假 |
| `quota[b][type]` | 见下 | — | 各带各类型配额 | 需（按深度区设计）/假（数值） |

配额默认值（「合计」即 I7 的下限；D1 起点计入 combat）：

| band | combat | elite | random | shop | event | finalBoss | 合计 |
|---|---|---|---|---|---|---|---|
| D1 | 3 | 0 | 1 | 0 | 1 | 0 | 5 |
| D2 | 3 | 1 | 1 | 1 | 1 | 0 | 7 |
| D3 | 3 | 1 | 1 | 1 | 2 | 0 | 8 |
| D4 | 4 | 1 | 2 | 1 | 1 | 0 | 9 |
| D5 | 4 | 2 | 2 | 1 | 1 | 0 | 10 |
| D6 | 4 | 2 | 1 | 1 | 2 | 0 | 10 |
| D7 | 4 | 2 | 2 | 1 | 1 | 0 | 10 |
| D8 | 3 | 1 | 1 | 0 | 1 | 1 | 7 |

全图合计 ≈ 66 节点。D1 无精英/商店对齐现行层配比【既有：现行 D1 只有战斗/事件】；D2–D7 每带 1 商店顺带回应 T49「D4/D5/D7/D8 无店可逛」的断点（最终是否全带设店由 T58/T60 定夺）；D8 商店 0（终点前不设消费）【假设】。

**默认值可玩性验收口径**：以默认参数连跑 20 个不同 seed，全部通过 I1–I12【需求·任务书】（T55 实测落盘）。

---

## 7. 伪代码：`generate(seed, params) → Region`

```text
function generate(seed, P):
  failures = {}                                   # reason -> count
  for attempt in 1 .. P.retry.max:
    rng      = makeRng(seed * 1000003 + attempt)  # 确定性：全程禁用 Math.random
    seedUsed = seed * 1000003 + attempt
    try:
      # ── 步骤1 生态生长 ─────────────────────────────
      W        = buildWeightTable(P)               # [eco][band]，每带内和=1
      ecoOf    = growEcos(rng, W, P)               # 多源泛洪 + 小块合并（§2 步骤1）
      assertEco(ecoOf, P)                          # I12，违例 → GenError

      # ── 步骤2 事件格布点 ───────────────────────────
      cells    = reserveStartAndFinalBoss(P)       # band1 顶行 / band8 底行中间
      nodes    = placeNodes(rng, ecoOf, P, cells)  # 配额 + 蓝噪声 D=2（§2 步骤2）
      assertPlacement(nodes, P)                    # I1, I7, I8

      # ── 步骤3 连线 ────────────────────────────────
      edges    = connect(rng, nodes, P)            # A保入边 B保出边 C补分叉 D保跨带
      assertGraph(nodes, edges, P)                 # I2..I5, I9, I10, I11

      # ── 步骤4 深度线与标记 ─────────────────────────
      for n in nodes: n.band = bandOf(n.y, P)      # §1 公式，写死
      for e in edges: e.crossBand = (band(e.from) != band(e.to))
                      if e.crossBand: e.to.crossBandIn = true
      nodes[finalBossIdx].type = 'finalBoss'
      assertBands(nodes, edges, P)                 # I6, I9 复核

      # ── 步骤5 内容绑定 ────────────────────────────
      for n in nodes:
        n.binding = resolveBinding(n.eco, n.band, P)   # 回退链（§2 步骤5）
      assertBinding(nodes)                         # 池非空

      return { region: pack(ecoOf, nodes, edges, seedUsed), attempts: attempt }
    catch GenError as err:
      failures[err.reason] += 1

  raise Error('generate: ' + P.retry.max + ' 次尝试全部失败 → ' + tally(failures))
  # 绝不静默返回半成品【需求·任务书】
```

```text
function growEcos(rng, W, P):
  label = [null] * (P.grid.w * P.grid.h)
  PQ    = MinHeap()
  for e in ECOS:                                  # 8 源点：按生态质量抽老家带
    band  = sampleBand(rng, rowMass(W, e))
    PQ.push(0, randomCellInBand(rng, band), e)
  while PQ not empty:
    cost, cell, e = PQ.pop()
    if label[cell] != null: continue
    label[cell] = e
    for nCell in neighbors4(cell):
      if label[nCell] == null:
        w = W[e][bandOf(nCell)]
        push(cost + (1-w)*(3*P.eco.kappa) + rng.uniform(0,1)*(1-P.eco.kappa), nCell, e)
  for comp in components(label):                  # 小块并入最长共享边界邻居
    if size(comp) < P.eco.minPatchArea: merge(comp, bestNeighbor(comp, label))
  for e in ECOS:                                  # 分量数收敛
    while countComponents(label, e) > P.eco.maxComponents:
      merge(smallestComponent(label, e), bestNeighbor(...))
  if anyViolation: raise GenError('eco.invariant')   # 不放宽、不静默
  return label
```

```text
function connect(rng, nodes, P):
  occ     = cellOccupancy()                       # 节点格 + 已用边中间格
  cands(u) = [ (dx,dy) in DISPLACEMENT_TABLE     # §2 步骤3 位移表
               | v = nodeAt(u.x+dx, u.y+dy), v != null
               , pathClear(u, v, occ) ]           # Bresenham 中间格无节点、无已用边
  # A 保入边（自上而下）
  for v in nodesByYAscending, v != start:
    if inDeg(v) == 0:
      u = argmin over { u' | v in cands(u') } of (dist(u',v), rng tie)
      if u == null: raise GenError('connect.indeg')
      addEdge(u, v)
  # B 保出边（自下而上，finalBoss 除外）
  for u in nodesByYDescending, u.type != 'finalBoss':
    if outDeg(u) == 0:
      v = nearest(cands(u)); if v == null: raise GenError('connect.outdeg')
      addEdge(u, v)
  # C 补分叉（多样性）
  for u in nodesByYAscending:
    while outDeg(u) < 3 and rng.bool(0.35) and cands(u) not empty:
      addEdge(u, pickWeighted(cands(u), preferCrossBand=false))
  # D 保跨带
  for b in 1..7:
    if no edge with from.band==b and to.band==b+1:
      u = bottom-most node in band b; v = top-most node in band b+1
      if (v - u) not in cands(u): raise GenError('connect.crossband.' + b)
      addEdge(u, v)
  return edges
```

```text
# ── 运行时（T57 实现，非生成器内部）────────────────────────
function crossBandBossChance(k, P):               # k = 本局第几次跨带（1 起）
  if k == 1: return 1                             # 首次必 BOSS【需求·已确认2】
  return max(P.boss.floor, P.boss.p0 * P.boss.decay ^ (k - 2))

function maybeReplaceWithBoss(run, node, k, rng):
  if not node.crossBandIn: return node            # 只有跨带边终点参与判定
  if rng.uniform(0,1) < crossBandBossChance(k, P):
    override = { type: 'boss', binding: node.binding.bossPool }   # 只改类型与内容
    run.mapOverride[node.id] = override           # 不改写生成的 Region【需求·已确认2】
  return effectiveNode(run, node)
```

---

## 8. 运行时跨带 BOSS 接口（T57 消费；本任务不实现）

- **触发点**：玩家沿一条 `crossBand === true` 的边移动到终点节点时判定。`k` = 本局**已完成**的跨带次数 + 1（run 级计数器）。
- **概率**：`p(1) = 1`；`p(k) = max(boss.floor, boss.p0 × boss.decay^(k−2))`（k ≥ 2）。默认参数下 p(1..5) = 1 / 0.5 / 0.3 / 0.18 / 0.108。
- **命中动作**：把**该跨带边的终点节点**在 run 级 override 里替换为 `type='boss'`，内容从该节点 binding 的 `bossPool` 抽取（bossPool 走 §2 步骤5 回退链）。节点 id / 坐标 / 边全部不变——「运行时替换类型与内容，不改生成结果」【需求·已确认2】。
- **未命中**：节点保持生成时的类型（combat/elite/event/shop/random），正常触发。
- **存储**：`run.mapOverride = { [nodeId]: { type:'boss', bossId } }`；渲染与触发一律先查 override 再读 Region。
- **边界**：finalBoss 永不参与此判定；同一条边只判一次（判定后该边记已结算）。

---

## 9. 后续任务消费表（本文与 spec.json 的下游）

| 任务 | 消费 |
|---|---|
| T55 生成器原型 | 按 §7 伪代码实现 `tools/mapgen.js`（纯算法）；断言 = §3 全表；200 seed 全绿 |
| T56 小图/总图 | §4 可见性 + `pruneForFrontend`；可见性在数据层裁剪 |
| T57 死路/推进/BOSS | §5 救援接口 + §8 跨带 BOSS 接口 + `random.mix` 落点 |
| T58 绑定表 | §2 步骤5 的结构 → `data/mapgen_bindings.json` 实表 |
| T60 配额盘点 | §6 配额表 × 64 组合（eco×band×type）做内容缺口口径 |
| T59 回归 | §3 全部不变量 + 20 seed 可玩性口径 + 500 局模拟 |

---

## 10. 边界声明汇总（哪些是假设）

1. **网格与节点密度**（w=14/h=48/配额数值/minPatchArea=18/maxComponents=2/D=2/k=4/maxInDeg=3）全部是【假设】；需求只锁了「连成一片」「每深度区设计数量」「尽量分散（D 默认 2）」「出边 1–3」「长度 1..k」「重试 20」。
2. **κ 的代价公式**（(1−w)·3κ + noise·(1−κ)）是为实现「聚合度」语义设计的【假设】，T55 实测后可在 spec.json 调。
3. **角度量化**：需求例值 ±35/±60/±85 在网格上实现为 26.6–78.7° 的固定位移表【假设·量化】；「左右直着都行」由大横移档承担。
4. **random 节点**是新增类型，既有 campfire 并入其落点分布（.45/.40/.15）【假设】；分布本身可在 spec.json 改，不影响生成器结构。
5. **跨带 BOSS 三个参数**（p0=0.5/decay=0.6/floor=0.1）【假设】；规则本身（首跨必 BOSS、递减、运行时替换）是【需求·已确认2】。
6. **救援扣血 10%**【假设】；「惩罚或战斗二选一、随机」「不耗回合、不重置迷雾」是【需求·四】。
7. **shopTier 分档**（1–3/4–6/7–8 带）【假设】，T58 可改。
8. **可见性防偷看**只到「不进 DOM」层面，不含内存级对抗【假设·边界】。
9. 需求原文二「跨带必然是 BOSS」已被用户已确认条款修正为「首次必 BOSS + 递减概率」，本文按已确认执行（§0.4）——不是改需求，是执行用户的最新拍板。
