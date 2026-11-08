# UI-005 零件值 cursor:pointer 无视觉指示

## 现状
`web/index.html:843`
```html
<span class="v" id="hud-parts" style="cursor:pointer" title="点击打开回收面板">0</span>
```
inline style `cursor:pointer` 无配套视觉变化。T451 已标记。

## 问题
维护者的零件计数器可点击打开回收面板，但外观与不可点击的普通数值一样。玩家不知道能点。T451 已判 P0（HUD 首次 >0 时加提示），这里补视觉指示。

## 改法
CSS 追加：
```css
#hud-parts {
    cursor: pointer;
    text-decoration: underline dotted;
    text-underline-offset: 3px;
}
#hud-parts:hover { color: var(--red-hi); }
```
删掉 inline `style="cursor:pointer"`（改由 CSS 管理）。

## 影响面
HUD。只影响维护者的零件数值显示。

## 验收
- 1280×720：维护者 HUD 零件数值带虚线下划线
- 悬停变色

## 风险
无。
