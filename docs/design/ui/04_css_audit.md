# K04 兜底 · CSS 机器级审计

> 任务书（自拟）：对 `web/index.html` 样式块（:6–:829，共 824 行）做机器级统计。不判断好坏——结果告诉设计机「该不该重构」。
> 方法：Python 脚本逐行解析 CSS 规则，统计五类指标。可复算：`python tools/sim/css_audit.py`。

## 结果

| 指标 | 值 | 说明 |
|---|---|---|
| CSS 字符数 | 45,670 字符（:6–:829，824 行） | 含注释和空行 |
| 规则块数 | **393 个选择器块** | 按 `{` 计（css_audit.py 实测） |
| 魔法数字 px | **506 个**（68 种唯一值） | 非变量、非 calc 的 px 值 |
| CSS 变量引用 | **255 处** `var(--…)` / 49 个变量定义 | |
| !important | **3 处** | `.hidden`、`.campopt.disabled`、`prefers-reduced-motion` |
| 内联 style（HTML 属性） | **2 处** | cursor:pointer ×1 + 动态 backgroundImage ×1（JS 设置的不计） |
| background+border-color 对 | **19 对** | 同一属性组出现在 2+ 个选择器中（主要是 B/C 主题覆盖） |
| 未引用类名 | 待定 | 需要交叉引用 JS 中的 classList 操作 |

## 魔法数字 Top 10（出现频率最高的 px 值）

| px 值 | 出现次数 | 主要用途 |
|---|---|---|
| 1px | 63 | border-width |
| 4px | 50 | border-radius / padding / gap |
| 6px | 37 | padding / margin / gap |
| 12px | 34 | font-size（日志/描述） |
| 8px | 32 | padding / gap / border-radius |
| 10px | 30 | font-size（标签/角标） |
| 3px | 27 | border-radius / gap |
| 14px | 25 | font-size（body/HUD/按钮） |
| 2px | 19 | border-radius / offset |
| 5px | 16 | padding / margin |

## 重复规则 Top 5（主题覆盖导致的重复）

| 属性组 | 出现次数 | 原因 |
|---|---|---|
| `background + border-color`（卡牌/敌人/面板） | ~15 对 | A/B/C 三主题各覆盖一遍 |
| `color`（text/dim/ink-dim） | ~12 对 | 主题变量级联 |
| `border-bottom-color` | ~6 对 | 图案区/面板分隔线 |
| `font-size` | ~8 对 | 主题/组件级覆盖 |
| `border-radius` | ~5 对 | 统一 4px 但硬编码 |

## 主题架构评估

当前三主题（off/B/C）的覆盖模式是**选择器级覆盖**——每个主题对同一选择器写一套覆盖规则。这意味着：
- 新增一个 UI 元素需要在每个主题下各写一遍覆盖（当前 14+ 行 for B、14+ 行 for C）
- 改基础样式需要在所有主题下同步

**替代方案**：把所有颜色/间距/字号抽成 CSS 变量（如 `--card-bg`/`--card-border`），主题只改变量值不改选择器。可将主题覆盖代码从 ~100 行压缩到 ~30 行（只改变量定义）。但需要一次性重构 ~180 个魔法数字为变量引用。

## 建议

| 优先级 | 建议 | 理由 |
|---|---|---|
| 1 | `--lane` 加 `min(1240px, 100vw)` | D4 发现的 1024px 溢出——一行修 |
| 2 | 把 `.card` 的 5 个 px 值改为 CSS 变量 | 卡牌是复用最多的组件（手牌/详情/三选一/营火），改一处全生效 |
| 3 | 把 `.enemy` 的 3 个 px 值改为 CSS 变量 | 同上 |
| 4 | `.hidden` 的 `!important` 保留（安全网） | 其余 2 处可去 |
| 5 | 主题覆盖压缩为变量定义 | 长期——需要一次性重构，不急 |

## 复算

`python tools/sim/css_audit.py`（脚本对 `web/index.html` 样式块做正则统计，参数无——纯只读）。
