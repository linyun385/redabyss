# 战斗动效系统 · 设计与任务拆分（2026-11-06）

## 一、先看现状（实测，不是估计）

| 项 | 实测 |
|---|---|
| `web/index.html` | 9,560 行，556KB，单文件 |
| 已有 `@keyframes` | **19 个**（gazeblink / blockpulse / pilepulse / turnflash / intentblink / ehit / floatup / shakeit / eggflash / mblink / glowbreath / atkpulse / dreampulse / shake / cardfly / dyingpulse / resflash …）|
| 已有飘字 | `floatText(container, txt, heal, staggerKey)`，450ms 自动移除，带并发错位（最多 3 层，每层 -20px）|
| 已有动作队列 | `enqueueAnim(fn)` + `pumpAnim()`，注释写「T37 动作队列：动画依次播，输入不等动画」。**但只用了 2 处**，基本闲置 |
| 已有性能护栏 | `perfWatch()`：连续 3 帧 > 50ms 就降级（关光晕/上浮，只留颜色）|
| 已有音效钩子 | `playSfx('combat.hurt')` / `'combat.block'` 等，已在 `render()` 里按 hp/block 变化触发 |
| `dealToEnemy(C, enemy, amount)` | **纯逻辑，不碰 DOM**，只有数据对象 |
| 数据对象上的 DOM 引用 | `$el` / `_el` / `domEl` / `elRef` 全部为 **0** |
| `render()` | **增量更新**（改 textContent、toggle class），不是整体重绘 |
| 敌方/手牌元素 | `el('div','enemy')`、`el('div','card')` 创建；选择器 `#enemy-area .enemy`、`#hand .card`；`innerHTML =` 共 16 处 |

### 由此得出一条硬约束

**敌人和卡牌的 DOM 元素会被重建，且数据对象上没有反向引用。**

所以：
- 不能把动画类挂在 `.enemy` 元素上等它自己播完（元素可能中途被换掉）
- 不能靠 `enemy.xxx` 找元素

**唯一稳的做法：独立特效层 + 触发瞬间的坐标快照。**

---

## 二、四层设计

不是「每张卡写一个特效」。那样 219 张卡会失控。分成四层，90% 的卡靠前两层自动获得反馈。

### L0 · 通用反馈层（覆盖全部卡，零配置）

| 特效 | 触发时机 | 表现 |
|---|---|---|
| 伤害飘字 | 任何扣血 | 红色数字从目标上浮、淡出（升级现有 `floatText`） |
| **血痕划过** | 每次攻击命中 | 一道不规则红色划痕从目标边缘斜向划过，0.25s 内拉伸出现→变暗→消散 |
| 命中震动 | 命中 | 目标元素轻微位移抖动 |
| 格挡碎裂 | 有护甲时被打 | 护甲数字上方浮出灰白碎片 |
| 治疗上浮 | 回血 | 绿色数字 + 柔和上浮 |
| 秒杀/击杀 | 目标死亡 | 目标短暂闪白 → 下沉淡出 |
| 玩家受伤 | 玩家掉血 | 屏幕边缘红闪（已有 `dying` 类，可复用） |

★ 这一层**不需要任何卡配置**。只要走了 `dealToEnemy` / `healPlayer`，就在渲染层拿到效果。

### L1 · 类型与状态层（按数据自动选，零配置）

**五脉（`card.veins[0]`）**：各一套主色 + 形状

| 脉 | 色 | 划痕/特效形态 |
|---|---|---|
| light 光脉 | 朱红偏橙 | 细长直划，边缘发亮 |
| mineral 矿物 | 铁灰 | 断口粗、带碎屑 |
| tremor 震语 | 清冷蓝灰 | 波纹状，多层涟漪 |
| heat 热脉 | 亮橙 | 划痕边缘烧灼、带火星 |
| water 水脉 | 暗青 | 流淌状，边缘液化 |

**状态（`special.code`）**：

| code | 特效 |
|---|---|
| burn | 目标身上浮出火苗，短暂 |
| poison | 绿色液滴悬挂、下坠 |
| weak | 灰色裂纹从目标向外爬 |
| frail | 壳体碎块剥落 |
| strength | 金色脉冲向外扩散 |
| dexterity | 青色环形旋绕 |
| regenerate | 血红色搏动上升 |
| thorns | 尖刺从目标表面弹出 |

★ 这一层由 `special.code` → 特效名自动映射。**新卡只要用已有 code，自动有特效。**

### L2 · 卡牌专属层（只给关键卡手写）

白名单制。没进白名单的卡**自动回落到 L0 + L1**，不会没反馈。

第一批只做 **7 张核心卡**：

| 卡 | 特效 |
|---|---|
| 0051 机械增生 | 卡面金属板裂开、新结构从卡内长出 |
| 0052 子代理 | 一个空壳从卡牌位置坠下、落到战场上立住 |
| 0053 悬浮体 | 卡牌悬浮离手、漂浮到场上 |
| 0054 武器试验 | 一把武器从卡牌飞出、刺入目标，目标身上永久留下一道疤 |
| 0055 有机质发电 | 目标被管线连接、管线亮起，能量回流到玩家 |
| 0056 重铸 | 卡牌散成零件再拼回 |
| 0057 更新换代 | 手牌整体下滑、新的从下方推上来 |

### L3 · 持久状态层（常驻标记，不是一次性动画）

| 状态 | 表现 |
|---|---|
| **锁死（`cost_type: lock`）** | 卡面盖一个粗红叉（两笔，略带抖动），整体降饱和，不可点击；悬停显示「本场战斗已锁死」 |
| 凝视代价（`mark`） | 卡面右下角一个眼睛徽记 + 数字 |
| 子代理在场 | 场上/卡面显示徽记，标明当前数量 |
| 已升级（`upgraded`） | 卡面金色细边（已有 `upgraded` 类，可强化） |

★ 锁死这条用户特别点名了，我把它放进 L3 第一批。

---

## 三、技术实现

### 3.1 独立特效层（唯一正确的位置）

在 `web/index.html` 的 `<body>` 里加一个固定层：

```html
<div id="fx-layer" aria-hidden="true"></div>
```

```css
#fx-layer{position:fixed;inset:0;pointer-events:none;z-index:60;overflow:hidden}
```

它**不随 `render()` 重建**，所以动画播完就播完。

### 3.2 坐标快照（解决元素被重建的问题）

触发时立刻取位置，之后跟原元素无关：

```js
function fxRect(target){
  if (typeof target === 'string') target = document.querySelector(target);
  if (!target) return null;
  const r = target.getBoundingClientRect();
  return {x: r.left + r.width/2, y: r.top + r.height/2, w: r.width, h: r.height};
}
```

### 3.3 特效契约（GLM 照这个写，我负责接）

`web/fx.js` 只导出这些函数，**不接管任何游戏逻辑**：

```js
// 全部返回 undefined，不抛异常，不阻塞
FX.init(opts)                       // opts:{layer, intensity:'low'|'mid'|'high'}
FX.damage(rect, amount, veins)      // 血痕 + 飘字
FX.block(rect, amount)              // 格挡碎裂
FX.heal(rect, amount)               // 治疗
FX.status(rect, code)               // burn/poison/weak/... 单状态特效
FX.kill(rect)                       // 击杀
FX.lockCard(cardEl)                 // 给卡面盖红叉（L3，操作真实元素，非 overlay）
FX.unlockCard(cardEl)
FX.setIntensity(level)              // low/mid/high，low = 只有飘字
```

### 3.4 血痕怎么画（具体做法）

用 SVG 而不是 div。一条 `<path>`，不规则折线 + 两端收细：

```js
function scarPath(w,h){
  // 从左上到右下的一条带毛边的折线
  return `M${-w*0.1},${h*0.15} L${w*0.3},${h*0.45} L${w*0.55},${h*0.4} L${w*1.1},${h*0.85}`;
}
```

动画：`stroke-dasharray` 从 0 到全长（划出来的感觉）→ 停 120ms → 整体 `opacity` 淡出。
两个 `<path>` 叠加：粗的一层暗红（宽 6px，模糊），细的一层亮红（宽 2px），才有「血」的层次。

### 3.5 卡牌震动

```css
@keyframes fx-cardshake{
  0%,100%{transform:translate(0,0) rotate(0)}
  20%{transform:translate(-3px,2px) rotate(-1.2deg)}
  45%{transform:translate(4px,-2px) rotate(1deg)}
  70%{transform:translate(-2px,1px) rotate(-.6deg)}
}
```

★ **不能在 `.card` 上加 animation 类**（会被重建冲掉）。做法：用 overlay 里复制一份卡面快照（用 `getBoundingClientRect` + 直接把元素 `cloneNode(true)` 进去，播完删），或者在 `render()` 之后重新加类。

我选**克隆快照**：干净、不影响真实元素、也不会被重建打断。

### 3.6 锁死红叉（L3，必须操作真实元素）

这个不能用 overlay，因为它是常驻的、要跟着卡牌走。做法：

在 `renderCardStatic(card)` 里加一层判断：

```js
if (card.cost_type === 'lock' && card.__lockedThisBattle) {
  d.classList.add('locked');
  d.appendChild(el('div','lock-x'));   // 两笔 + 后面一个 ✕
}
```

```css
.card.locked{filter:saturate(.35) brightness(.75)}
.card.locked .lock-x{
  position:absolute;inset:0;pointer-events:none;
}
.card.locked .lock-x::before,
.card.locked .lock-x::after{
  content:'';position:absolute;left:-6%;top:50%;width:112%;height:5px;
  background:linear-gradient(90deg,transparent,#c0202a 12%,#e04048 50%,#c0202a 88%,transparent);
  box-shadow:0 0 6px #7a0d14;
}
.card.locked .lock-x::before{transform:rotate(32deg)}
.card.locked .lock-x::after{transform:rotate(-32deg)}
```

★ 需要引擎里加一个「本场已锁死」标记。查过：`cost_type: lock` 现在只是扣费方式，**没有在卡上留状态**。这是必须先补的逻辑，否则红叉没依据。

### 3.7 性能与克制

- 接进已有 `perfWatch()`：降级时 `FX.setIntensity('low')`
- 尊重 `prefers-reduced-motion: reduce` → 自动 low
- 单帧同屏特效上限（建议 6 个），超了直接丢弃新的
- **特效总时长不超过 350ms**。超过就会拖慢出牌节奏

---

## 四、分工（这是关键，决定能不能落地）

### 为什么必须拆文件

GLM 不许动 `web/`（已有规矩）。但动效全是样式 + 特效函数，正好可以独立。

| 谁 | 产出 | 边界 |
|---|---|---|
| **GLM** | `vfx/fx.css`、`vfx/fx.js`（新目录，项目根下） | **只许创建这两个新文件**，一个字都不许改已有文件；按第三节的函数签名写 |
| **我** | 把 `vfx/` 搬进 `web/`，在 `index.html` 加引入 + overlay + 调用点 + 引擎里的锁死标记 | 全部要改 `index.html` 的活 |
| **HY4** | 全池 219 张卡的「特效需求清单」（纯统计表） | 不改任何代码 |

### HY4 的具体任务（机械活，不给判断）

```
输出一张 CSV：card_id, name, has_damage, damage_count, veins, special_codes, needs_L2
needs_L2 一律填 no —— 那是我的判断，你只填前几列
```
它的价值在于：让我一眼看出哪些卡走 L0/L1 就能覆盖、哪些是空白（比如纯防御卡没有任何 L1 特效）。

---

## 五、排批次

| 批 | 内容 | 谁 | 验收标准 |
|---|---|---|---|
| **0** | 引擎补「本场已锁死」标记；`cost_type:lock` 打出后写入 | 我 | 打一张锁死卡，`card.__locked` 为 true，重进战斗清零 |
| **1** | overlay 层 + `FX` 命名空间骨架 + 坐标快照 + 强度开关 + perfWatch 接入 | 我 | 页面上出现空 `#fx-layer`；`FX.damage` 能画一个方块；低档位无动画 |
| **2** | L0 六个特效（CSS + JS） | GLM | 逐个手动触发，300ms 内结束，无残留元素 |
| **3** | L1 五脉 + 八状态（CSS + JS） | GLM | 按 veins/code 自动选对，颜色符合下表 |
| **4** | 把 L0/L1 接到 `render()` 与出牌流程 | 我 | 打任意攻击牌 → 目标有血痕 + 飘字 + 震动 |
| **5** | L3 锁死红叉 + 凝视徽记 | GLM 写 CSS，我接 | 打出锁死卡 → 卡面盖红叉、降饱和、不可再点 |
| **6** | L2 七张核心卡专属特效 | 我 | 逐张手动验证 |
| **7** | 性能与体感调参 | 我 | 满屏特效时帧率不掉；连打 5 张不卡 |

### 任务量（按我的惯例先估再乘 2）

| 批 | 我的初估 | 乘 2 后 |
|---|---|---|
| 0 | 0.5 人日 | 1 |
| 1 | 1 | 2 |
| 2 | 1 | 2 |
| 3 | 1.5 | 3 |
| 4 | 1 | 2 |
| 5 | 0.5 | 1 |
| 6 | 1.5 | 3 |
| 7 | 1 | 2 |
| **合计** | | **约 16 人日** |

真正的时间大头不是写，是**调**——每个特效都要看、嫌烦、改小，来回几轮。

---

## 六、我要提醒的三件事

### 1. 动效做多了会烦

这是卡牌游戏，一回合出 3–5 张牌。如果每张都播 0.5 秒特效，一回合就多花 2 秒，几十回合下来人会烦。

**我的建议：L0 全部压到 250ms 以内，且默认强度设「中」，不是「高」。** 由你决定默认档。

### 2. 锁死红叉现在没有数据依据

`cost_type: lock` 目前只影响扣费，**没有在卡牌对象上留下「本场已锁」的状态**。所以第 0 批必须先补这个逻辑，否则红叉不知道什么时候画。这是唯一一处**必须先改引擎**的地方。

### 3. 别给 219 张卡都写专属特效

那是无底洞，而且做出来玩家也分不清。按四层走，L2 只给 7 张核心卡 + 你后续指定的少数几张。
