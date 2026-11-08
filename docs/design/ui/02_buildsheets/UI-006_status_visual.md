# UI-006 敌人 debuff 状态无可视化

## 现状
`web/index.html:7837` 附近
```js
(e.status.weak ? '　虚弱' : '') +
(e.status.frail ? '　脆弱' : '') + ...
```
只有文本拼接，无图标或颜色。且 frail 是死状态（引擎不读），玩家更困惑。

## 问题
敌人的 weak/burn/poison/frail 状态在 intent 行内只有纯文本，玩家要逐字读。违反「状态颜色语义全局统一」（UI.md §2 表）。

## 改法
在敌人 DOM 构建段追加状态图标行：
```js
// render() 敌人构建段，在 intent 之后：
if (e.status && Object.keys(e.status).length) {
    const sl = el('div', 'estatus');
    if (e.status.weak) sl.appendChild(el('span', 'st st-weak', '虚'));
    if (e.status.frail) sl.appendChild(el('span', 'st st-frail', '脆'));
    if (e.status.burn) sl.appendChild(el('span', 'st st-burn', '燃' + e.status.burn.v));
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

## 影响面
战斗屏敌人区。追加一个 DOM 子元素。frail 如果引擎修复后，此处自动生效。

## 验收
- L5 热议会的执汤者 debuff burn 后，敌人卡下方出现「燃N」标签
- 视觉部分需设计机在浏览器确认

## 风险
低——只追加 DOM。frail 标签在引擎修复前仍会显示（死状态本身是 BUG-1 的事）。
