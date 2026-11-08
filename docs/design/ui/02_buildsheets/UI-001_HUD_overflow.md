# UI-001 HUD overflow 裁切

## 现状
`web/index.html:88`
```css
#hud {
    ...
    overflow: hidden;
}
```
`web/index.html:90`
```css
.hud-stats { display: flex; gap: 18px; justify-content: center; flex-wrap: wrap; }
```

## 问题
`#hud` 设 `overflow: hidden`，`.hud-stats` 有 `flex-wrap: wrap`。10 项 HUD 在 <1000px 视口下换行，第二行被 `overflow: hidden` 裁切——生命/能量不可见。违反「一级信息一眼可见」（UI.md §1 表）。

## 改法
`web/index.html:88` 只删一个属性：
```css
/* old */
    flex: 0 0 auto; overflow: hidden;
/* new */
    flex: 0 0 auto;
```
如果担心换行后 HUD 高度撑爆，改加 `max-height` + `overflow-y: auto`：
```css
    flex: 0 0 auto; max-height: 80px; overflow-y: auto;
```

## 影响面
所有界面（HUD 常驻）。去掉 overflow: hidden 后，如果内容真的超高，HUD 会撑高——但 flex-wrap 的换行在有 wrap 时高度可控（两行 ≈ 60px）。不影响战斗区/地图（#screen-combat 有 `flex: 1 1 0; min-height: 0` 自适应）。

## 验收
- `node tools/check_web.js` → 全绿
- 1280×720：HUD 不变（10 项不换行）
- 800×600：HUD 换行但全部可见
- 视觉部分需设计机在浏览器确认

## 风险
无——只删一个 CSS 属性，不改 DOM/JS。
