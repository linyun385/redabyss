# HY4 · Y1 数据一致性：cards/anmin.json ↔ RAW.anmin

> 2026-11-06 02:37。机械核对，结论先行。脚本：`tools/hy4_raw_vs_json.js`（共用 `tools/hy4_common.js`）。
> 运行：`node tools/hy4_raw_vs_json.js`（退出码 0 = 一致）；`--json` 出机器可读结果。

## 结论

**完全一致。差异清单为空。**

## 条数

| 项 | 值 |
|---|---|
| `cards/anmin.json` 条数 N | **54** |
| `web/index.html` 的 `const RAW.anmin` 条数 M | **54** |
| N === M | 是 |
| id 集合完全相同 | 是 |
| json 侧重复 id | 0 |
| RAW 侧重复 id | 0 |
| 逐卡内容不同的 id | 0 |
| 逐字节相同 | 是（三方全同，首个差异偏移 = -1） |

> 任务书背景写「6 张核心卡」，验证文档 `_VERIFY_anmin_core_cards.md` 记的是**两轮共 7 张**（多了 `anm_0052` 子代理）。本项按实际数据 54 张计，不按 6 张推算。

## 差异清单

| 类别 | 内容 |
|---|---|
| 仅在 json 的 id | （无） |
| 仅在 RAW 的 id | （无） |
| 内容不同的 id | （无） |
| 字节级差异 | （无） |

**空清单即结论**：没有「如果有」的分支。

## 方法（可复算）

1. 解析 RAW：不用正则。字符串定位 `const RAW = `（第 6620 行），从 `{` 开始按大括号深度扫描，扫描过程跳过字符串字面量内的括号（与 `tools/_sync_cards.js` 同一写法），取出整段 JSON 后 `JSON.parse`。
2. id 集合：`Set` 双向差集 + 重复检测。
3. 逐卡内容：`stable()` 按字典序重排所有键后序列化，消除「键顺序不同」造成的假差异；只在 id 交集内比。
4. 逐字节：`JSON.stringify(RAW.anmin)` / `JSON.stringify(json 解析结果)` / `stripJsonWhitespace(anmin.json 原文)` 三方逐字符比较。`stripJsonWhitespace` 只删字符串字面量**之外**的空白，不碰字符串内部空格，所以是真正的字节级而非「格式化后相等」。

## 逐字节结果

| 文本 | 长度（字符） |
|---|---|
| `JSON.stringify(RAW.anmin)` | 18194 |
| `JSON.stringify(json)` | 18194 |
| `stripWhitespace(json 原文)` | 18194 |

三者长度相同、逐字符相同、首个差异偏移 -1。`anmin.json` 是格式化文本，RAW 是它的紧凑形式，没有第三份数据。

## 旁证：其余 4 个卡池键

| 键 | json | RAW | 内容一致 |
|---|---|---|---|
| diver | 57 | 57 | true |
| tremor | 57 | 57 | true |
| cangmin | 47 | 47 | true |
| shared | 11 | 11 | true |

四个键也全部一致，说明 `_sync_cards.js` 的写回是整池同步，不是只补了黯民。

## 边界声明

- 【实测】以上数字全部来自脚本实跑输出，可 `node tools/hy4_raw_vs_json.js` 复算。
- 【未验证】`web/index.html` 里除 `const RAW` 之外的其它卡牌副本（若存在）不在本项范围；本项只比任务书点名的两份。
- 项目未初始化 git（`game/` 与 `红渊/` 下均无 `.git`），无法用 `git diff` 佐证写回历史，按任务书要求「没有就别折腾」。
