# UI-004 营火升级预览走 title 属性

## 现状
`web/index.html:6763`
```js
d.title = '升级预览：' + preview.name + '\n' + cardDesc(preview) +
    (preview.upgrade.flavor_add ? '\n———\n' + preview.upgrade.flavor_add : '');
```
title 属性在移动端不可达、键盘不可达——升级效果预览对非鼠标用户完全不可见。

## 问题
营火升级是本游戏唯一的「改卡」操作。玩家在决定升级哪张牌时需要看到升级后的效果差量。title 属性只有鼠标悬停才能触发，违反「键盘完成一整个回合」+「移动端可达」（T451 引导缺口）。

## 改法
在营火升级的卡牌 DOM 里追加一个可见的预览区（`showCampfire` 函数内，`:6755` 附近）：
```js
/* old */
d.title = '升级预览：' + preview.name + '\n' + cardDesc(preview) +
    (preview.upgrade.flavor_add ? '\n———\n' + preview.upgrade.flavor_add : '');

/* new */
d.title = '';  // 清除 title（不再依赖悬停）
// 在卡面下方追加可见的预览文本
const prev = el('div', 'osub',
    '→ ' + preview.name + '：' + cardDesc(preview) +
    (preview.upgrade.flavor_add ? '　' + preview.upgrade.flavor_add : ''));
d.appendChild(prev);
```
CSS 追加（`.campopt` 或 `#flow-cards .card` 附近）：
```css
#flow-cards .card .osub {
    font-size: 11px; color: var(--dim); padding: 4px 8px; margin-top: auto;
    border-top: 1px dashed #4a2a2c;
}
```

## 影响面
营火界面（`showCampfire`）。追加一个 DOM 子元素，不改升级逻辑（`RedAbyss.upgradeCard` 调用不变）。

## 验收
- `node tools/check_web.js` → 全绿
- 营火界面：升级卡下方直接显示「→ 升级后名字：效果差量」——不需要悬停
- 1280×720 / 1920×1080 两档均可见（卡高 267px + osub ~30px = ~300px，在 flow 区不溢出）

## 风险
低——只追加 DOM 子元素。卡高 267px + osub 可能撑到 ~300px，#flow-cards 有 flex-wrap 不怕。不影响 RAW/引擎。
