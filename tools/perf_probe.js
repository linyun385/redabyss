/* T52 性能探针：在浏览器控制台执行，或由自动化注入（本任务用 node_repl evaluate 注入）。
   window.__perfStart() 开始 rAF 帧采样；window.__perfStop() 停止并返回
   { avgFrame, maxFrame, samples, domNodes, dcl }。
   帧采样剔除 >250ms 的切页大坑（标签切换/断点停顿），只保留真实渲染帧。 */
(function () {
  'use strict';
  let frames = [], last = 0, on = false;
  function tick(now) { if (!on) return; frames.push(now - last); last = now; requestAnimationFrame(tick); }
  window.__perfStart = function () { frames = []; last = performance.now(); on = true; requestAnimationFrame(tick); };
  window.__perfStop = function () {
    on = false;
    const f = frames.filter(x => x < 250);
    const nav = performance.getEntriesByType('navigation')[0];
    return {
      avgFrame: +(f.reduce((a, c) => a + c, 0) / Math.max(1, f.length)).toFixed(2),
      maxFrame: +Math.max(...f, 0).toFixed(2),
      samples: f.length,
      domNodes: document.getElementsByTagName('*').length,
      dcl: Math.round(nav.domContentLoadedEventEnd - nav.startTime)
    };
  };
})();
