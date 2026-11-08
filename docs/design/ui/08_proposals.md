# B · 设计提案（10 条，从 28 条问题里挑出）

> 来源=01_issues.md（28 条）。选了 4 条 P0 全部 + 6 条影响面最大的 P1。
> 每条固定六段：现状/改成什么/为什么/影响面/风险/验收。全部标估算。
> **只写设计，不执行——落地由设计机在浏览器里做。**

---

## UI-001 · HUD overflow 裁切（P0）

**现状**：`#hud`（index.html:88）设 `overflow: hidden`，`.hud-stats`（:90）有 `flex-wrap: wrap`。10 项 HUD 在视口 <1000px 时换行到第二行，第二行被 `overflow: hidden` 裁切——生命/能量不可见。

**改成什么**：`:88` 删 `overflow: hidden`。如需防撑爆，改加 `max-height: 80px; overflow-y: auto`。

**为什么**：HUD 的 flex 容器 `#app` 是 `flex-direction: column`，`#hud` 是 `flex: 0 0 auto`——HUD 高度增长会挤压 `#screen-combat` 的 `flex: 1 1 0`。但战斗区有 `min-height: 0` 防爆。所以去掉 overflow:hidden 后 HUD 最多占两行（~60px），战斗区仍有 ~500px 可用（720p 下）。

**影响面**：所有界面（HUD 常驻）。去掉 overflow:hidden 后，HUD 内容如果真的超高（两行以上），会压缩战斗区高度。

**风险**：可能让 HUD 在极端窄屏下占太多高度。缓解：加 `max-height: 80px; overflow-y: auto` 作为安全网。

**验收**：1280×720 下 10 项不换行，HUD 不变；800×600 下 HUD 换行但全部可见；`node tools/check_web.js` 全绿。

---

## UI-002 · 穿透/镜像/drain 意图无视觉区分（P0）

**现状**：`render()` 敌人意图构建（:7810 附近）只按 `it.type` 加 class——attack 加 `.i-atk`（红色）、defend 加 `.i-def`（蓝色）。所有攻击类（含 pierce/mirror/drain_discard）都是同一个红色。CSS（:139-140）只有这两个 class。

**改成什么**：
1. CSS `:140` 后追加三条：
```css
.enemy .intent .i-atk.pierce { color: #c46994; text-decoration: underline wavy; }
.enemy .intent .i-atk.mirror { color: #84b2e4; font-style: italic; }
.enemy .intent .i-atk.drain { color: #c9a35a; }
```
2. `render()` 敌人意图构建处（:7810 附近），把 attack 的 class 从硬编码 `'i-atk'` 改为动态拼接：
```js
let cls = 'i-atk';
if (it.pierce) cls += ' pierce';
if (it.mirror) cls += ' mirror';
if (it.drain_discard) cls += ' drain';
```

**为什么**：H11 微模拟显示穿透在 L5-L8 造成大量不可格挡伤害——但玩家在 UI 上看到的与普通攻击一模一样。色选 #c46994（紫粉=穿透）/#84b2e4（蓝=复刻）/ #c9a35a（金=drain）——三色在 check_palette.js 的 ECO_C 色板里已有先例，对比度 ≥3（次要级）。

**影响面**：战斗屏敌人区。新增 3 个 CSS class；render() 里改 3 行 JS。不影响引擎（意图数据不变）。

**风险**：色盲玩家可能分不清 pierce（紫粉）与普通攻击（红）——但波浪下划线是形状差异，不只靠颜色。

**验收**：L5 震喉 P3（穿透）→ 意图显紫色+波浪线；L5 震喉 P1（镜像）→ 蓝色斜体；`check_web.js` 全绿。

---

## UI-003 · 带目标牌键盘不可达（P0）

**现状**：`startCardPointer`（:7977）只绑 pointer 事件。`#cd-play` 打出 needsTarget 卡后 `pending = i`，敌人加 `.targetable`，但键盘无法选中敌人。T28 #17 已标记，至今未修。

**改成什么**：在现有 `keydown` 事件处理器（:8200 附近）内追加一段：
```js
if (pending !== null && ev.key >= '1' && ev.key <= '5') {
    const idx = parseInt(ev.key) - 1;
    if (C && C.enemies[idx] && !C.enemies[idx].dead) {
        doPlay(pending, idx);
        pending = null;
        ev.preventDefault();
        return;
    }
}
```
同步改 `openCardDetail` 里 needsTarget 的说明文本（:8090）：
```js
// old
'把它拖到敌人身上，或按「打出」再点敌人。'
// new
'拖到敌人身上、按「打出」再点敌人、或按数字键 1-5。'
```

**为什么**：数字键在 pending=null 时走的是出牌路径（1-9），pending≠null 时走目标选择——两条路径互不冲突（pending 不为 null 时数字键不会走到出牌逻辑）。敌人最多 5 只（L8），1-5 够用。

**影响面**：战斗屏键盘处理器。只在 pending≠null 时拦截数字键。不影响非 pending 态。

**风险**：如果未来加了需要选择友方的卡（目标>5），1-5 不够。当前引擎无此类卡。

**验收**：打一张 needsTarget 的牌 → 按「打出」→ 按 1 → 打在第一个敌人；`check_web.js` 全绿。

---

## UI-004 · 营火升级预览走 title（P0）

**现状**：`showCampfire`（:6755 附近）里升级选项的预览存在 `d.title` 属性（:6763）：
```js
d.title = '升级预览：' + preview.name + '\n' + cardDesc(preview) + ...
```
title 只有鼠标悬停才能触发——移动端不可达、键盘不可达。

**改成什么**：把预览从 `d.title` 改为 DOM 可见文本。在卡面下方追加一个 `div.osub`：
```js
// old
d.title = '升级预览：...';
// new
d.title = '';  // 清除
const prev = el('div', 'osub',
    '→ ' + preview.name + '：' + cardDesc(preview) +
    (preview.upgrade.flavor_add ? ' ' + preview.upgrade.flavor_add : ''));
d.appendChild(prev);
```

**为什么**：营火是唯一改卡操作。玩家需要看到升级后的效果差量才能做选择。title 的 hover-only 限制在 T451 已标 P0（UI-004）。改 DOM 可见文本后所有输入方式可达。

**影响面**：营火界面。追加一个 DOM 子元素。卡高 267px + osub ~30px = ~300px，`#flow-cards` 有 `flex-wrap` 不怕。

**风险**：osub 的 30px 可能让三张卡在窄屏换行——但 #flow-cards 有 flex-wrap，换行是正确行为。

**验收**：营火界面：升级卡下方直接显示「→ 升级后名字：效果差量」——不需要悬停；`check_web.js` 全绿。

---

## UI-005 · 零件计数器无视觉指示（P1）

**现状**：`#hud-parts`（:843）有 inline `style="cursor:pointer"` 和 `title="点击打开回收面板"`，但外观与不可点击的普通数值一样。

**改成什么**：CSS 追加：
```css
#hud-parts { text-decoration: underline dotted; text-underline-offset: 3px; }
#hud-parts:hover { color: var(--red-hi); }
```
删 inline `style="cursor:pointer"`。

**为什么**：维护者的核心成长路径（零件→改造）全靠点这个数字打开面板。T451 已判 P0（引导缺口 #1）。虚线下划线是「可点击文本」的通用 affordance。

**影响面**：HUD。只影响维护者的零件数值显示。

**风险**：无。

**验收**：维护者 HUD 零件数值带虚线下划线；悬停变色。

---

## UI-006 · 敌人 debuff 状态无可视化（P1）

**现状**：敌人身上的 weak/frail/burn/poison 只有文本拼接在 intent 行内（:7837 附近）。无图标、无颜色标记。

**改成什么**：在敌人 DOM 构建段追加状态图标行。在 intent 行之后：
```js
if (e.status && Object.keys(e.status).length) {
    const sl = el('div', 'estatus');
    if (e.status.weak) sl.appendChild(el('span', 'st st-weak', '虚'));
    if (e.status.frail) sl.appendChild(el('span', 'st st-frail', '脆'));
    if (e.status.burn) sl.appendChild(el('span', 'st st-burn', '燃' + (e.status.burn.v || '')));
    if (e.status.poison) sl.appendChild(el('span', 'st st-poison', '毒'));
    enemyDiv.appendChild(sl);
}
```
CSS 追加：
```css
.estatus { margin-top: 4px; display: flex; gap: 4px; }
.st { font-size: 10px; padding: 1px 4px; border-radius: 2px; border: 1px solid; }
.st-weak { color: #a89a90; border-color: #a89a90; }
.st-frail { color: #6b5334; border-color: #6b5334; }
.st-burn { color: var(--red-hi); border-color: var(--red); }
.st-poison { color: #68b291; border-color: #68b291; }
```

**为什么**：weak 影响敌人攻击 ×0.75（core.js:745）、burn 每回合掉血（覆盖语义）——这些状态影响战斗结果但 UI 上只有纯文本。图标化让玩家一眼看到状态。

**影响面**：战斗屏敌人区。追加一个 DOM 子元素。frail 在引擎修复前仍显示（死状态本身是 BUG-1）。

**风险**：低——只追加 DOM。frail 标签在引擎修复前仍会显示（死状态本身是 BUG-1 的事）。

**验收**：L5 热议会的执汤者 debuff burn 后，敌人卡下方出现「燃」标签。

---

## UI-007 · 卡详情升级预览缺失（P1）

**现状**：`openCardDetail`（:8084）里非升级卡只写 `osub` 一行「这张牌可以在营火升级」（:8095）。营火的 `upgradeCard()`（:6755）有完整预览但战斗中的卡详情没有。

**改成什么**：`openCardDetail` 里在 upgrade 提示行后追加差量：
```js
if (card.upgrade && !card.upgraded) {
    const preview = RedAbyss.upgradeCard(card);
    lines.push('<div class="osub">升级后 → ' + preview.name + '：' + cardDesc(preview) + '</div>');
}
```

**为什么**：玩家在看卡详情时最想知道「升级了值不值」。营火已有 `upgradeCard()` 函数返回完整升级卡——调用它生成差量文本只需 3 行。

**影响面**：卡详情面板（#card-detail）。追加一行文本。

**风险**：`RedAbyss.upgradeCard` 是引擎函数——但只读不改数据。确认它在战斗中可安全调用（不修改原卡）——从注释看它返回新对象不改原卡 ✅。

**验收**：选一张非升级卡 → #cd-lines 里出现「升级后 → …」一行。

---

## UI-009 · 日志无自动滚动到底（P1）

**现状**：`renderLog()`（:8540）重建 #log 内容，但没有 `scrollTop = scrollHeight`。新条目在底部但可视区可能停在顶部。

**改成什么**：`renderLog()` 函数末尾追加：
```js
const wrap = document.getElementById('log-wrap');
if (wrap) wrap.scrollTop = wrap.scrollHeight;
```

**为什么**：日志是玩家理解战斗流程的主要信息源。新条目在底部，如果滚动区停在顶部，玩家看不到最新的行动结果。

**影响面**：战斗屏日志区。

**风险**：如果玩家正在向上翻阅旧日志，自动滚动会打断——但当前 `renderLog()` 是全量重建（不是增量追加），翻阅状态本来就不保留。

**验收**：打 3+ 张牌后日志自动滚到最新行。

---

## UI-010 · 效果未实现红字走普通样式（P1）

**现状**：引擎 `applySpecial` default 分支（core.js:515 附近）调用 `log(C, msg)` 不带 type 参数——日志渲染为普通 --dim 颜色。与普通信息行无视觉区别。

**改成什么**：core.js 的 default 分支改为 `log(C, msg, 'warn')`——然后在 web/index.html 的日志渲染处给 `.warn` 加红色样式：
```css
#log div.warn { color: var(--red-hi); font-weight: bold; }
```
注意：这需要改 **engine/core.js** 一行（log 调用加 type 参数）**和** web/index.html 的 log 渲染一行（.warn 样式）——两者都在「不许改」列表内。

**为什么**：u_0009 打出时弹的「这个效果这一版还没做」红字在游戏里显示为普通灰字——玩家不知道这是异常。

**影响面**：战斗屏日志区 + engine/core.js 一行。

**风险**：改 engine/core.js 需要同步 web 内联副本（BUG-3 的教训）。如果只改 web 不改 core，下次 core 同步时会被覆盖。

**验收**：打 u_0009 → 日志区出现红字加粗「resonance_gain 尚未实现」。

**结论**：这条**需要引擎改动**（core.js 的 log type 参数 + web 内联副本同步），不在纯 UI 施工范畴。标记为**需引擎**。

---

## UI-011 · 事件禁用选项原因走 title（P1）

**现状**：`showEvent`（:7370）里 requires 不满足时 `b.disabled = true; b.title = '该脉的牌不够（需要 N 张，你有 M 张）'`。title 是 hover-only。

**改成什么**：disabled 时在 .osub 里显示原因：
```js
if (have < req) {
    b.disabled = true;
    const dis = el('div', 'osub', '该脉的牌不够（需要 ' + req + ' 张，你有 ' + have + ' 张）');
    b.appendChild(dis);
    b.title = '';  // 清除 title
}
```

**为什么**：与 UI-004 同理——title 属性在移动端/键盘不可达。disabled 选项更需要告诉玩家「为什么不能选」。

**影响面**：事件界面。

**风险**：disabled + 追加子元素可能改变按钮高度——但 .opts 有 flex-direction: column，不影响其他选项。

**验收**：选一个 requires.vein_min 不满足的事件 → 禁用选项下方显示「该脉的牌不够」文本（不悬停也可见）。

---

## UI-014 · 字号缩放不改变卡牌像素尺寸（P1）

**现状**：`.fontbtns` 的文+/文- 通过 `body.style.fontSize = s + '%'` 缩放。但 `.card` 的 `.cname`/`.ctext`/`.cflavor` 用 `px` 固定（13px/11px/10px），不随 body fontSize 缩放。效果=点文+ 后正文变大但卡牌文字不变。

**改成什么**：卡牌内部字号从 px 改为 em（以 .card 的 font-size 为基准）：
```css
/* old */
.card { font-size: 12px; }
.card .cname { font-size: 13px; }
.card .ctext { font-size: 11px; }
.card .cflavor { font-size: 10px; }
/* new */
.card { font-size: 1.1em; }      /* 12/14=0.857... 简化为接近值 */
.card .cname { font-size: 1.08em; }   /* 13/12 */
.card .ctext { font-size: 0.92em; }   /* 11/12 */
.card .cflavor { font-size: 0.83em; } /* 10/12 */
```
同时 `.enemy .hpnum`、`.hud-stats .k`/`.v` 也改 em。

**为什么**：T28 要求字号缩放覆盖所有文本。当前实现只缩放 body，卡牌/敌人用 px 硬编码不跟随——缩放按钮名不副实。

**影响面**：所有用 px 字号的元素（~25 处 CSS）。改后卡牌/敌人的文字随全局缩放——卡牌尺寸（宽高）不变（那也是 px），只有文字大小变。

**风险**：em 基准链可能导致嵌套元素字号倍增。缓解：只在 `.card`/`.enemy`/`.hud-stats` 三个顶层容器设 em 基准，内部用相对比例。

**验收**：点文+ 三次 → 正文变大 + 卡牌内文字同步变大；点文- 三次 → 全部变小。`check_web.js` 全绿。
