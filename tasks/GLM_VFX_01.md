# GLM 任务：战斗动效库（第 1 包）

> 一句话：**只新建两个文件**，写纯 CSS 动画 + 纯特效函数，不碰任何已有文件。

## 一、先读这三份（不读就动手 = 白做）

| 文件 | 取什么 |
|---|---|
| `docs/design/_VFX_PLAN_1106.md` | 整体设计、四层模型、为什么这么分层 |
| `docs/ART_PROMPT_SPEC.md` | 世界观的两条硬规则（倒吊 / 红光自下而上），动效配色要服它 |
| `docs/GLOSSARY.md` | 五脉的正确中文写法 |

## 二、产出物（只有这两个）

| 文件 | 内容 |
|---|---|
| `vfx/fx.css` | 全部 `@keyframes` + 特效元素样式 |
| `vfx/fx.js` | 全部特效函数，挂到 `window.FX` 上 |

### 硬边界（越界即退回）

1. **不许改任何已有文件**，一个字节都不行。不许碰 `web/index.html`、`web/assets/`、`cards/`、`engine/`。
2. **不许引入外部库**（jQuery / GSAP / anime.js 一律不许）。
3. **不许用 `setTimeout` 驱动动画本身** —— 动画必须走 CSS `animation`，`setTimeout` 只允许用来清理元素。
4. `vfx/` 是新建目录，不是 `web/vfx/`。我会负责搬进去。

## 三、函数契约（必须一模一样，我会照这个接）

全部函数：**不抛异常、不返回值、不阻塞**。任何参数缺失都要静默跳过。

```js
window.FX = {
  init(opts),                          // opts: { layer:HTMLElement, intensity:'low'|'mid'|'high' }
  damage(rect, amount, veins),         // rect:{x,y,w,h} 中心点+宽高；amount:number；veins:数组，可能空
  block(rect, amount),                 // 格挡被打掉
  heal(rect, amount),                  // 回血
  status(rect, code),                  // code: 'burn'|'poison'|'weak'|'frail'|'strength'|'dexterity'|'regenerate'|'thorns'
  kill(rect),                          // 目标死亡
  setIntensity(level),                 // 'low'|'mid'|'high'
  lockCard(cardEl),                    // 给真实卡牌元素盖红叉（不是 overlay）
  unlockCard(cardEl),
  version                              // 字符串，如 '1.0.0'
};
```

`rect` 里的 `x,y` 是**屏幕坐标中心点**（`getBoundingClientRect` 换算来的），特效元素用 `position:fixed` 直接定位到那里。

## 四、要做的动画清单

### L0 通用（六个）

| 名称 | 触发 | 要求 |
|---|---|---|
| `fx-scar` 血痕 | `damage` | SVG 两层路径叠：粗暗红（6px、模糊）+ 细亮红（2px）。`stroke-dasharray` 从 0 拉到全长（划出来的过程），停 100ms，整体淡出。**路径必须是折线、两端收细**，不能是直线 |
| `fx-hit` 命中震动 | `damage` | 目标位置附近一个短促位移脉冲（±3px），80ms |
| `fx-dmg` 伤害数字 | `damage` | 红色数字从目标上方浮起 24px、淡出，250ms。可复用现有 `.float` 风格 |
| `fx-block` 格挡碎裂 | `block` | 灰白碎片向四周散开，200ms |
| `fx-heal` 治疗 | `heal` | 绿色数字 + 柔和上浮，250ms |
| `fx-kill` 击杀 | `kill` | 闪白 40ms → 下沉 12px + 淡出，280ms |

**全部 ≤ 350ms。** 超过的不收。

### L1 五脉色与形（`damage` 的 `veins[0]` 决定血痕配色）

| 脉 | 主色 | 血痕形态 |
|---|---|---|
| `light` | `#ff5a3c` 朱红偏橙 | 细长直划，边缘发亮 |
| `mineral` | `#8a8f96` 铁灰 | 断口粗、带碎屑 |
| `tremor` | `#7fa8c8` 冷蓝灰 | 波纹状，两层涟漪 |
| `heat` | `#ff8a1e` 亮橙 | 边缘烧灼，带几点火星 |
| `water` | `#3f7f7a` 暗青 | 流淌状，边缘液化 |

`veins` 为空时用默认朱红 `#c0202a`。

### L1 八状态（`status(rect, code)`）

| code | 表现 |
|---|---|
| `burn` | 火苗从目标底部往上蹿，橙红，240ms |
| `poison` | 绿色液滴悬挂后下坠，300ms |
| `weak` | 灰色裂纹从中心向外爬，260ms |
| `frail` | 壳体碎块剥落，240ms |
| `strength` | 金色环形脉冲向外扩散，280ms |
| `dexterity` | 青色圆环绕目标转半圈，280ms |
| `regenerate` | 血红色搏动上升，300ms |
| `thorns` | 尖刺从目标表面弹出，200ms |

### L3 锁死红叉（操作真实卡牌元素）

`lockCard(cardEl)` 给传入的元素加 class `locked`，`unlockCard` 移除。

```css
.card.locked{filter:saturate(.35) brightness(.75)}
.card.locked .lock-x{...}       /* 用 ::before/::after 画两笔红叉 */
```

红叉要求：**两笔粗线，带一点不均匀（不要像印刷的 ✕）**，颜色 `#c0202a`→`#e04048`，带暗红外发光。

## 五、强度三档

| 档 | 行为 |
|---|---|
| `low` | 只保留飘字 + 血痕静态闪现。其余全关 |
| `mid`（默认） | 全开，但**所有时长按上表的 100%** |
| `high` | 全开 + 额外一层细节（血痕加第二层、震动幅度 ×1.5） |

`setIntensity` 要能随时切，切完立即生效。

## 六、性能与克制（这几条最容易被忽略）

1. 同屏特效元素**上限 6 个**，超了直接丢弃新的（不排队）
2. 每个特效元素播完必须 `remove()`，**不许留残留节点**
3. 优先用 `transform` 和 `opacity`，**不许动画 `width/height/top/left`**（会触发布局）
4. 尊重 `prefers-reduced-motion: reduce` → 自动等价 `low`
5. `FX.init` 没被调用时，所有函数静默空转，不报错

## 七、验收（我会按这个查）

| # | 检查 | 怎么验 |
|---|---|---|
| 1 | 只多了两个文件 | `git status` 或文件时间对比 |
| 2 | 没有外部库 | 搜 `import` / `require` / `<script src` |
| 3 | 八个函数都在 `window.FX` 上 | `Object.keys(FX)` |
| 4 | 逐个手动触发不留残留 | 触发后数 `#fx-layer` 子节点数归零 |
| 5 | 每个特效 ≤350ms | 看 CSS 里 `animation` 的时长 |
| 6 | `low` 档只剩飘字 | 切档后肉眼确认 |
| 7 | 参数缺失不报错 | `FX.damage(null, 5, [])` 不抛异常 |

## 八、交付方式

两个文件写完，回我一份简短说明：

- 每个动画的**实际时长**
- 同屏上限怎么实现的
- **哪几个你觉得效果不够、想让我看**（不要自己反复改到满意，那会拖很久）

## 九、不要做的事

| 别做 | 为什么 |
|---|---|
| 不要写「接入代码」（调用点、事件绑定） | 那是我的活，你写的会和我冲突 |
| 不要改 `web/index.html` | 同上 |
| 不要自己造额外的特效 | 清单外的等我看过再说 |
| 不要给 219 张卡各写一个特效 | 四层模型就是防这个 |
