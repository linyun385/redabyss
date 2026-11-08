# C · P0 施工单（4 条，可粘 diff）

> 来源=08_proposals.md 的 UI-001/002/003/004。全部只改 `web/index.html`。
> 每段代码可直接搜索定位后替换。未验证项已标明。

---

## UI-001 · HUD overflow 裁切

### 改动点

**文件**：`web/index.html`
**行号**：:88
**现在原文**：
```css
    flex: 0 0 auto; overflow: hidden;
```

### 替换成

```css
    flex: 0 0 auto;
```

### 为什么这样改

`overflow: hidden` 裁掉了 `.hud-stats` 的 `flex-wrap: wrap` 换行结果。在 <1000px 视口下 10 项 HUD 换行到第二行，第二行不可见。去掉后 flex 容器自动扩展。`#screen-combat` 的 `min-height: 0` 保证战斗区自适应不会撑爆。

### 影响面

`#hud` 常驻于所有界面。删除 overflow: hidden 后 HUD 高度从固定变为自适应——最多两行（~60px），战斗区高度压缩 ~20px。

### 回滚方式

在 `flex: 0 0 auto;` 后面加回 `overflow: hidden;`。

### 验收

800×600 视口下 HUD 两行全部可见（生命/能量不被裁切）；1280×720 下 HUD 不变（10 项单行）；`node tools/check_web.js` 全绿。

---

## UI-002 · 穿透/镜像/drain 意图无视觉区分

### 改动点 1（CSS）

**文件**：`web/index.html`
**行号**：:140 之后
**现在原文**（:139-141）：
```css
  .enemy .intent .i-atk { color: var(--red-hi); }
  .enemy .intent .i-def { color: #6f8b9a; }
  .enemy .hpbar { margin-top: 8px; ...
```

### 替换成

```css
  .enemy .intent .i-atk { color: var(--red-hi); }
  .enemy .intent .i-atk.pierce { color: #c46994; text-decoration: underline wavy; }
  .enemy .intent .i-atk.mirror { color: #84b2e4; font-style: italic; }
  .enemy .intent .i-atk.drain { color: #c9a35a; }
  .enemy .intent .i-def { color: #6f8b9a; }
  .enemy .hpbar { margin-top: 8px; ...
```

### 改动点 2（JS——render() 敌人意图构建）

**行号**：约 :7810（搜 `i-atk`）
**现在原文**：
```js
    if (it.type === 'attack') {
      itl.appendChild(el('span', 'i-atk', ...));
```

### 替换成

```js
    if (it.type === 'attack') {
      let cls = 'i-atk';
      if (it.pierce) cls += ' pierce';
      if (it.mirror) cls += ' mirror';
      if (it.drain_discard) cls += ' drain';
      itl.appendChild(el('span', cls, ...));
```

**注意**：上面的 `...` 是原有的意图文本构建代码，保持不变。只改 span 的 class 参数。

### 为什么这样改

穿透在 L5/L7/L8 造成大量不可格挡伤害（H11/H02 实证）——但 UI 上与普通攻击完全一样。三个颜色的选取依据 check_palette.js ECO_C 色板已有值（#c46994/ #84b2e4/ #c9a35a），对比度 ≥3（次要级）。波浪下划线和斜体提供非颜色辅助。

### 影响面

战斗屏敌人区的意图行。不影响引擎（意图数据不变）。不影响其他区域的 .i-atk 使用（只有敌人 intent 用这个 class）。

### 回滚方式

删除 3 行新增 CSS + 把 render() 里的 `let cls = 'i-atk'; ...` 改回 `el('span', 'i-atk', ...)`。

### 验收

L5 震喉 P3 穿透意图 → 紫色+波浪下划线；L5 P1 镜像意图 → 蓝色斜体；L5 震喉·空腔独奏 drain 意图 → 金色；`check_web.js` 全绿。

---

## UI-003 · 带目标牌键盘不可达

### 改动点 1（keydown 事件处理器——追加数字键选目标）

**文件**：`web/index.html`
**行号**：约 :8200 附近（搜 `keydown`——这是全局 keydown 处理器）
**现在原文**（keydown 处理器的开头附近）：
```js
document.addEventListener('keydown', (ev) => {
  if (ev.key === 'Escape') { hideOverlay(); return; }
```

### 替换成

```js
document.addEventListener('keydown', (ev) => {
  if (ev.key === 'Escape') { hideOverlay(); return; }
  // UI-003: pending 态下数字键选目标
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

### 改动点 2（needsTarget 说明文本更新）

**文件**：`web/index.html`
**行号**：:8090
**现在原文**：
```js
  if (needsTarget(card)) lines.push('<div class="osub">打出后要选一个目标：把它拖到敌人身上，或按「打出」再点敌人。</div>');
```

### 替换成

```js
  if (needsTarget(card)) lines.push('<div class="osub">打出后要选一个目标：拖到敌人身上、按「打出」再点敌人、或按数字键 1-5。</div>');
```

### 为什么这样改

数字键在 pending=null 时走 1-9 出牌路径（已有功能）；pending≠null 时走目标选择——两条路径互不冲突因为 pending 不为 null 时数字键不会走到出牌逻辑。敌人最多 5 只（L8），1-5 够。

### 影响面

战斗屏全局 keydown 处理器。只在 pending≠null 时拦截数字键。不影响非 pending 态的 1-9 出牌。

### 回滚方式

删除追加的 7 行 if 块 + 把 needsTarget 文本改回原文。

### 验收

打一张 needsTarget 的牌（如 dive_0011 辐射弹）→ 按「打出」→ 按 `1` → 第一个敌人掉血；`check_web.js` 全绿。

### 未验证

- pending 态下按 6-9 是否仍走原出牌逻辑（理论上是——拦截范围只有 1-5）
- 苍民双世界下 pending+数字键是否正常（需要实际测试）

---

## UI-004 · 营火升级预览走 title 属性

### 改动点 1（title → DOM 可见文本）

**文件**：`web/index.html`
**行号**：:6763-6764
**现在原文**：
```js
    d.title = '升级预览：' + preview.name + '\n' + cardDesc(preview) +
      (preview.upgrade.flavor_add ? '\n———\n' + preview.upgrade.flavor_add : '');
```

### 替换成

```js
    const prev = el('div', 'osub',
      '→ ' + preview.name + '：' + cardDesc(preview) +
      (preview.upgrade.flavor_add ? ' ' + preview.upgrade.flavor_add : ''));
    d.appendChild(prev);
```

### 为什么这样改

title 属性只有鼠标悬停才显示——移动端/键盘不可达。改为 DOM 子元素后所有输入方式可达。`el()` 是项目已有的 DOM 构建辅助函数。`.osub` class 已存在（font-size: 12px, color: --dim），视觉一致。

### 影响面

营火界面（showCampfire）。追加一个 DOM 子元素到卡面下方。不改升级逻辑。

### 回滚方式

删除追加的 3 行 `const prev = ...` + `d.appendChild(prev);`，恢复原来的 `d.title = ...` 两行。

### 验收

营火界面：升级卡下方直接显示「→ 升级后名字：效果差量」文本——不需要悬停；`check_web.js` 全绿。

### 未验证

- .osub 的 30px 高度是否让三张升级卡在 720p 下换行（#flow-cards 有 flex-wrap，换行是正确行为但布局会变）
- 卡面 267px + osub 30px = ~300px，三张并排 = 900px < 1024 ✅ 但接近边缘
