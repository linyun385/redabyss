/* 红渊 · 窗口适配（2026-11-06）
 *
 * 决定：不做响应式。整个游戏按 1600×900 设计，按窗口等比缩放，四周留黑边。
 *
 * 为什么：多断点平衡的成本远大于收益，而且断点之间的排版永远有夹缝。
 * 固定画布 + 等比缩放（letterbox）是游戏的标准做法 —— 任何窗口比例下
 * 画面都不变形，元素位置也不飘，代价只是极端比例时有黑边。
 *
 * 缩放系数写进 --ui-scale，由 web/ui.css 的 #app 消费：
 *   transform: translate(-50%,-50%) scale(var(--ui-scale,1))
 */
(function () {
  'use strict';

  var DESIGN_W = 1600;
  var DESIGN_H = 900;
  var lastScale = 0;

  function fit() {
    var vw = window.innerWidth;
    var vh = window.innerHeight;
    // 按短边缩，保证内容完整可见；不放大超过 1（放大会模糊文字）
    var s = Math.min(vw / DESIGN_W, vh / DESIGN_H, 1);
    /* ★ 死区：滚动条出现/消失会让 innerWidth 差 15px，缩放只变 0.009 左右 ——
       为这点变化重排一次，视觉上就是「点一下按钮画面抖一下、放大一点点」。
       实测玩家点到「结束回合」时日志变多、滚动条冒出来，正好触发这个抖动。
       <0.01 的变化直接忽略，画面就不会跟着滚动条抽搐。 */
    if (Math.abs(s - lastScale) < 0.01) return lastScale;
    lastScale = s;
    document.documentElement.style.setProperty('--ui-scale', s.toFixed(4));
    return s;
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', fit);
  } else {
    fit();
  }
  window.addEventListener('resize', fit);
  window.addEventListener('orientationchange', fit);

  var last = { w: 0, h: 0 };
  window.addEventListener('resize', function () {
    var w = window.innerWidth, h = window.innerHeight;
    if (w === last.w && h === last.h) return;
    last.w = w; last.h = h;
  });

  window.UIFit = {
    DESIGN_W: DESIGN_W,
    DESIGN_H: DESIGN_H,
    fit: fit,
    current: function () {
      return parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--ui-scale')) || 1;
    }
  };
})();
