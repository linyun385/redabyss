# 第二轮改动交接（2026-10-29 白天）

> 这些改动是**人工直接改的 `web/index.html`**，GLM 接手前必须先读这份。
> 所有改动都有明确理由，**不要"优化"回去**。

---

## 一、布局：flexbox 溢出修复（最重要）

### 问题
用户实玩发现：战斗日志累积后页面被撑高，**「结束回合」按钮被挤出屏幕，点不到**。

### 根因
1. `#screen-combat` **完全没有 CSS 规则** —— 它没有 flex 约束，高度由内容撑开
2. `#log-wrap` 只有 `flex: 1` 和 `min-height: 70px`，缺 `min-height: 0`
3. flex 子项默认 `min-height: auto`，内容会顶开父容器，`overflow-y: auto` 失效

### 修法（不要改回去）
```css
#screen-combat {
  flex: 1 1 0; min-height: 0;
  display: flex; flex-direction: column;
  width: 100%; max-width: var(--lane); margin: 0 auto;
}
#log-wrap { flex: 1 1 0; min-height: 60px; overflow-y: auto; }
#hand-area { flex: 0 0 auto; }
#enemy-area { flex: 0 0 auto; overflow-x: auto; }
```

---

## 二、统一内容梁 `--lane: 1240px`

用户原话：「开头是布局在中间，但路程中又怎么一小块类似手机内的布局，战斗又都是左边，问题在于布局的不统一」。

三个界面现在共用一条 1240px 的梁：

```css
:root { --lane: 1240px; }
#screen-select { max-width: var(--lane); margin: auto; }
#screen-combat { max-width: var(--lane); margin: 0 auto; }
#flow-panel   { max-width: var(--lane); margin: auto; text-align: center; }
#screen-flow  { display: flex; flex-direction: column; }
```

内容重心也统一到中线：地图节点、事件选项、卡牌奖励、敌人卡、手牌、日志全部居中。

长文本（`.flavor` / `.statline` / `.ending`）保留左对齐。

---

## 三、HUD 常驻（结构改动）

### 之前
`<header id="hud">` 在 `#screen-combat` 内部，只有战斗时显示。

### 现在
移到了 `#app` 下，成为所有界面共用的顶栏：

```html
<div id="app">
  <header id="hud" class="hidden"> ... </header>   ← 这里
  <section id="screen-select">
  <section id="screen-combat">   ← 内部已无 header
  <section id="screen-flow">
</div>
```

HUD 拆成两行：
```html
<div class="hud-stats"> 生命/格挡/能量/共鸣/凝视/金币/层 </div>
<div class="hud-relics" id="hud-relics"> 遗物 </div>
```

### 显隐规则
| 位置 | 代码 |
|---|---|
| 进局显示 | `showMap()` 里 `$('#hud').classList.remove('hidden')` |
| 回选职业隐藏 | 重开逻辑里 `$('#hud').classList.add('hidden')` |
| 非战斗时收起战斗项 | `showMap()` 里给 `#hud-block-wrap` / `#hud-energy-wrap` / `#hud-res-wrap` 加 `hidden` |
| 战斗时恢复 | `renderHud()` 里对这三个 `remove('hidden')` |

**格挡/能量/共鸣是战斗内概念**，非战斗界面不显示它们。生命/凝视/金币/零件/清醒度常驻。

---

## 四、keep_block 遗物：格挡不再无限累积

### 问题
用户拿到一件 `keep_block` 遗物后，格挡一路累积到 44，变成"第二条命"。他原话：「我最初以为格挡是一回合内的血，后来发现似乎不是，但格挡数加上去后好像又是这样了」。

### 修法
```js
// 原来
if (!keepBlock) C.block = 0;
// 现在
if (keepBlock) C.block = Math.floor(C.block / 2); else C.block = 0;
```

### 遗留
4 条遗物文案还写着"格挡不再在回合结束清零"，**要改成"保留一半"**：
- `relics/all.json` · 圣火残留（长明）
- `relics/all.json` · 渊民的合葬结
- `relics/anmin.json` · 封存册残页
- `relics/cangmin.json` · 猎巫密册（残）

---

## 五、层深度主题色

用户要：「最开始白色，随着不断的深入逐渐变暗，再逐渐变亮红色」。
第一版做得太保守（看不出差别），第二版拉开跨度：

```js
const LAYER_THEME = {
  1: { bg: '#39434e', fg: '#f0ece6' },   // 地表：天光
  2: { bg: '#2a323a', fg: '#e6e0d8' },
  3: { bg: '#1c2228', fg: '#dcd4cc' },
  4: { bg: '#0d1013', fg: '#cfc7c0' },   // 空洞海：最黑
  5: { bg: '#1a0b0e', fg: '#d8c8c0' },
  6: { bg: '#2b0a10', fg: '#e2c4bb' },
  7: { bg: '#420a12', fg: '#eec0b6' },
  8: { bg: '#64101a', fg: '#ffc9bd' }    // 核心：红光
};
function applyLayerTheme(d) { ... 设 --bg / --text ... }
```

调用点：`showMap()` 和 `startCombat()` 开头。

---

## 六、点击目标放大

用户要「点击的东西要足够显眼、大」。

| 元素 | 之前 | 现在 |
|---|---|---|
| 地图节点 `.mnode` | 104×60 / 字号 18 | **140×80 / 字号 22** |
| 事件选项 `.optbtn` | 640 宽 / padding 10 | **760 宽 / padding 16 / 字号 15** |
| 奖励卡牌 `#flow-cards .card` | 150×150 | **210×210** |

---

## 七、已知未完成

| 项 | 状态 |
|---|---|
| 地图底部两行文字没居中 | `.rulerow` 和地图底部提示仍是左对齐 |
| `?` 机制说明面板 | 没做（格挡/共鸣/凝视的说明） |
| 卡牌改长方形 + 图案区 | 没做（T36 的核心） |
| HUD 图标化（♥ ⬢ ✦ ∿ ◉） | 没做（T36） |

---

## 八、改这些地方的注意事项

1. **不要为了"看起来更简洁"把 `min-height: 0` 删掉** —— 那是防溢出的关键
2. **HUD 的 id 不能改名** —— JS 用 `$('#hud-hp')` 这类选择器
3. **`--lane` 变量是三个界面共用的**，改它等于改所有界面宽度
4. 改完必须跑 `node tools/check_web.js`，并**真开浏览器**打 10 回合确认按钮还在
