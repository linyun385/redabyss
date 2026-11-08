# 通用牌 × 职业专属牌 查重对照

> 由 `tools/dup_check.py` 机械生成。**只列事实，不替你决定删哪张**。
> 通用牌 11 张；职业牌 208 张（维护者 47、疯先知 47、下潜者 57、震语者 57）。

两种撞法：
- **完全撞**：effect 一模一样
- **近似撞**：主效果同、数值差 ≤2、目标相同（6 伤害 vs 7 伤害）

---

## `share_0001` 强行供能（通用）

效果：`{"special": [{"code": "rule_bypass"}], "target": "self"}`

**没有任何职业牌与它相撞** —— 这张填补的是空白。

---

## `u_0003` 虹吸管（通用）

效果：`{"damage": 5, "hits": 1, "target": "single", "heal": 2}`

**没有任何职业牌与它相撞** —— 这张填补的是空白。

---

## `u_0006` 风险合同（通用）

效果：`{"damage": 9, "hits": 1, "target": "single"}`

### 完全撞（3 张）

- `anm_0002` 扳手规程（维护者）
- `cng_0021` 巨神的欠账（疯先知）
- `cng_0048` 猎巫巡逻·换防（疯先知）

### 近似撞（7 张）

- `anm_0047` 通风守卫·代班（维护者）— `{"damage": 8, "hits": 1, "target": "single"}`
- `cng_0027` 红矮星风（疯先知）— `{"damage": 8, "hits": 1, "target": "single"}`
- `anm_0025` 协议：终端确认（维护者）— `{"damage": 10, "hits": 1, "target": "single"}`
- `dive_0002` 聚能枪（下潜者）— `{"damage": 10, "hits": 1, "target": "single"}`
- `trem_0009` 震语：断脉（震语者）— `{"damage": 10, "hits": 1, "target": "single"}`
- `anm_0030` 运料车残骸（维护者）— `{"damage": 7, "hits": 1, "target": "single"}`
- `cng_0026` 光父的钟摆（疯先知）— `{"damage": 7, "hits": 1, "target": "single"}`

---

## `u_0008` 灰烬测振仪（通用）

效果：`{"damage": 6, "hits": 1, "target": "single", "resonance_gain": 2, "special": [{"code": "burn", "value": 2, "turns": 2}]}`

**没有任何职业牌与它相撞** —— 这张填补的是空白。

---

## `u_0009` 倒转圣痕（通用）

效果：`{"target": "self", "special": [{"code": "gaze_reduce", "value": 2}, {"code": "resonance_gain", "value": 3}]}`

**没有任何职业牌与它相撞** —— 这张填补的是空白。

---

## `u_0010` 谐振垫层（通用）

效果：`{"block": 7, "target": "self", "resonance_drain": 2}`

### 近似撞（2 张）

- `anm_0017` 回收协议·总则（维护者）— `{"block": 8, "resonance_drain": 8, "target": "self"}`
- `dive_0070` 回收员的账本（下潜者）— `{"block": 5, "resonance_drain": 5, "target": "self"}`

---

## `u_0011` 活水引泉（通用）

效果：`{"heal": 4, "target": "self", "special": [{"code": "dexterity", "value": 1}]}`

**没有任何职业牌与它相撞** —— 这张填补的是空白。

---

## `u_0012` 双芯灯管（通用）

效果：`{"damage": 7, "hits": 1, "target": "single", "special": [{"code": "burn", "value": 1, "turns": 2}]}`

### 近似撞（5 张）

- `anm_0011` 焊接臂·民用型（维护者）— `{"damage": 6, "hits": 1, "target": "single", "special": [{"code": "burn", "value": 3, "turns": 2}]}`
- `anm_0039` 菌婪者组织样本（维护者）— `{"damage": 6, "hits": 1, "target": "single", "special": [{"code": "poison", "v": 4}]}`
- `dive_0033` 圣火武器（下潜者）— `{"damage": 6, "hits": 1, "target": "single", "special": [{"code": "burn", "value": 3, "turns": 2}]}`
- `cng_0037` 影语（疯先知）— `{"damage": 9, "hits": 1, "target": "single", "special": [{"code": "weak", "turns": 2}]}`
- `trem_0080` 震语：长夜（震语者）— `{"damage": 9, "hits": 1, "target": "single", "special": [{"code": "burn", "value": 4, "turns": 3}]}`

---

## `u_0013` 散落的铅字（通用）

效果：`{"damage": 4, "hits": 1, "target": "all", "special": [{"code": "weak", "turns": 2}]}`

**没有任何职业牌与它相撞** —— 这张填补的是空白。

---

## `u_0016` 越权的批文（通用）

效果：`{"target": "self"}`

**没有任何职业牌与它相撞** —— 这张填补的是空白。

---

## `u_0007` 传声钢缆（通用）

效果：`{"block": 5, "draw": 1, "target": "self"}`

### 完全撞（1 张）

- `trem_0028` 涌喉·光池倒影（震语者）

### 近似撞（7 张）

- `anm_0021` 协议：优先级翻转（维护者）— `{"draw": 1, "block": 4, "target": "self"}`
- `cng_0008` 历法之争（疯先知）— `{"draw": 2, "block": 4, "target": "self"}`
- `anm_0019` 例检手套（维护者）— `{"block": 6, "draw": 1, "target": "self"}`
- `cng_0049` 岩洞集会（疯先知）— `{"block": 6, "draw": 1, "target": "self"}`
- `cng_0014` 伊格的方向（疯先知）— `{"block": 3, "draw": 1, "target": "self"}`
- `dive_0006` 渊光重工·工作灯（下潜者）— `{"block": 3, "draw": 1, "target": "self"}`
- `trem_0026` 光导石（震语者）— `{"block": 3, "draw": 1, "target": "self"}`

---

## 汇总

- 通用牌里**完全撞**掉的职业牌：4 次
- 通用牌里**近似撞**上的职业牌：21 次
- **没撞任何职业牌**的通用牌：7 张 —— share_0001 强行供能、u_0003 虹吸管、u_0008 灰烬测振仪、u_0009 倒转圣痕、u_0011 活水引泉、u_0013 散落的铅字、u_0016 越权的批文

> 注意：一个职业牌可能同时被两张通用牌撞上，统计是「次数」不是「张数」。
