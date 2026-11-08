# UI-002 穿透/镜像/drain 意图无视觉区分

## 现状
`web/index.html:139-140`
```css
.enemy .intent .i-atk { color: var(--red-hi); }
.enemy .intent .i-def { color: #6f8b9a; }
```
`web/index.html:7810-7820`（render() 敌人意图构建段）
```js
// 意图 span 只根据 type 加 class，无 pierce/mirror/drain 区分
if (it.type === 'attack') {
    s = el('span', 'i-atk', ...);  // 所有攻击（含穿透/镜像/drain）都是同一个红色
}
```

## 问题
穿透（pierce）、镜像（mirror）、弃牌攻击（drain_discard）在 UI 上与普通攻击完全一样（红字），玩家必须读完整文本才能区分。H11 微模拟已证明穿透在 L5/L7/L8 造成大量不可格挡伤害——玩家第一次遇到会以为是 bug。

## 改法
`web/index.html` CSS 块追加（`:140` 之后）：
```css
.enemy .intent .i-atk.pierce { color: #c46994; text-decoration: underline wavy; }
.enemy .intent .i-atk.mirror { color: #84b2e4; font-style: italic; }
.enemy .intent .i-atk.drain { color: #c9a35a; }
```
`render()` 敌人意图构建段（约 `:7810`）改：
```js
/* old */
if (it.type === 'attack') {
    s = el('span', 'i-atk', ...);
}
/* new */
if (it.type === 'attack') {
    let cls = 'i-atk';
    if (it.pierce) cls += ' pierce';
    if (it.mirror) cls += ' mirror';
    if (it.drain_discard) cls += ' drain';
    s = el('span', cls, ...);
}
```

## 影响面
战斗屏敌人区。新增 3 个 CSS class，不改现有 class。不影响引擎（意图数据不变）。

## 验收
- `node tools/check_web.js` → 全绿
- L5 震喉 P3：穿透意图应显紫色+波浪下划线
- L5 震喉 P1：镜像意图应显蓝色斜体
- 视觉部分需设计机在浏览器确认

## 风险
低——只加 CSS class 判断，不改意图数据结构。render() 里加三个 if 不影响其他渲染。
