# UI-003 带目标牌无键盘路径

## 现状
`web/index.html:7977` `startCardPointer` 只绑 pointer 事件（mousedown/mousemove/mouseup），不绑键盘。
`web/index.html:8111` `#cd-play` 打出后如果 `needsTarget(card)` 则进入 `pending = i` 态——敌人加 `.targetable`，但键盘无法选中敌人。
T28 审计 #17 已标记此缺口，至今未修。

## 问题
键盘-only 玩家在打出带目标的牌（如 `dive_0011` 辐射弹）后无法完成操作——必须用鼠标点击敌人。违反「键盘完成一整个回合」（UI.md T28 #17）。

## 改法
`web/index.html` 的键盘事件处理器（keydown，约 `:8200` 附近，搜 `keydown`）追加：

```js
// 在现有 keydown 处理器内追加：
// pending 态下数字键 1-5 转发给敌人索引
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

同步更新 `openCardDetail` 的 needsTarget 说明（`:8090`）：
```js
/* old */
if (needsTarget(card)) lines.push('<div class="osub">打出后要选一个目标：把它拖到敌人身上，或按「打出」再点敌人。</div>');
/* new */
if (needsTarget(card)) lines.push('<div class="osub">打出后要选一个目标：拖到敌人身上、按「打出」再点敌人、或按数字键 1-5。</div>');
```

## 影响面
战斗屏键盘处理器。只在 `pending !== null` 时拦截数字键——不影响正常出牌（pending 为 null 时数字键走原路径）。

## 验收
- `node tools/check_web.js` → 全绿
- 打一张 needsTarget 的牌 → 按「打出」→ 按 1 → 打在第一个敌人
- 视觉部分需设计机在浏览器确认

## 风险
低——只在 pending 态拦截数字键。与现有 1-9 出牌不冲突（pending 态下 1-9 不会走到出牌逻辑）。
