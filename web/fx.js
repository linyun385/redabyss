/* 红渊 · 战斗动效层（MVP v0.1）
 *
 * 设计约束（见 docs/design/_VFX_PLAN_1106.md）：
 *   1. 独立层定位，用坐标快照 —— 因为敌人/卡牌 DOM 会被 render() 重建
 *   2. 只做视觉，不碰游戏逻辑，不返回任何值，不抛异常
 *   3. 动画走 CSS，JS 只负责建节点和清理
 *   4. 同屏上限 6 个，超了直接丢弃（不排队，避免出牌变慢）
 */
(function () {
  'use strict';

  var MAX_LIVE = 6;
  var VERSION = '0.1.0';

  var layer = null;
  var intensity = 'mid';
  var live = 0;
  var hasInit = false;

  /* ── 内部工具 ── */

  function now() { return (window.performance && performance.now) ? performance.now() : Date.now(); }

  function make(tag, cls) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    return n;
  }

  function reduced() {
    try {
      return window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    } catch (e) { return false; }
  }

  /** 把一个节点放进特效层，ms 后自动移除；超过上限返回 null */
  function spawn(node, ms) {
    if (!layer || !node) return null;
    if (reduced()) return null;
    if (live >= MAX_LIVE) return null;
    layer.appendChild(node);
    live++;
    var done = false;
    var kill = function () {
      if (done) return;
      done = true;
      if (node.parentNode) node.parentNode.removeChild(node);
      live = Math.max(0, live - 1);
    };
    // 主清理：定时器（仅用于移除，不驱动动画）
    window.setTimeout(kill, ms + 60);
    // 兜底：动画结束也清一次
    node.addEventListener('animationend', function (ev) {
      if (ev.target === node) window.setTimeout(kill, 40);
    });
    return node;
  }

  /** 从 rect 对象或元素拿屏幕坐标中心点 */
  function center(rect) {
    if (!rect) return null;
    if (typeof rect.getBoundingClientRect === 'function') {
      var r = rect.getBoundingClientRect();
      if (!r || (!r.width && !r.height)) return null;
      return { x: r.left + r.width / 2, y: r.top + r.height / 2, w: r.width, h: r.height };
    }
    if (typeof rect.x === 'number' && typeof rect.y === 'number') {
      return { x: rect.x, y: rect.y, w: rect.w || 64, h: rect.h || 64 };
    }
    return null;
  }

  /* ── 血痕 ── */

  var SCAR_PATH = 'M -10,20 L 26,46 L 43,40 L 60,60 L 76,53 L 110,84';

  function spawnScar(c, veins) {
    var w = Math.max(40, c.w * 1.05);
    var h = Math.max(40, c.h * 1.05);
    var box = make('div', 'fx fx-scar');
    box.style.left = (c.x - w / 2) + 'px';
    box.style.top = (c.y - h / 2) + 'px';
    box.style.width = w + 'px';
    box.style.height = h + 'px';

    var ink = (veins && veins.length && veins[0]) ? veins[0] : '';
    var colorMap = {
      light: '#ff5a3c',
      mineral: '#b7bcc2',
      tremor: '#7fa8c8',
      heat: '#ff8a1e',
      water: '#4f9a92'
    };
    if (colorMap[ink]) box.style.setProperty('--fx-scar', colorMap[ink]);

    var svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('viewBox', '0 0 100 100');
    svg.setAttribute('preserveAspectRatio', 'none');
    svg.setAttribute('width', '100%');
    svg.setAttribute('height', '100%');

    ['ink-under', 'ink-over'].forEach(function (cls) {
      var p = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      p.setAttribute('d', SCAR_PATH);
      p.setAttribute('class', 'ink ' + cls);
      p.setAttribute('pathLength', '1');
      svg.appendChild(p);
    });
    box.appendChild(svg);

    var node = spawn(box, 340);
    if (node) {
      // 划完之后进入淡出
      window.setTimeout(function () { node.classList.add('leaving'); }, 170);
    }
    return node;
  }

  /* ── 伤害数字 ── */

  function spawnNum(c, txt, kind) {
    var n = make('div', 'fx fx-num ' + (kind || 'dmg'));
    n.textContent = txt;
    n.style.left = c.x + 'px';
    n.style.top = (c.y - Math.max(12, c.h * 0.18)) + 'px';
    return spawn(n, 270);
  }

  /* ── 命中震动 ── */

  function spawnHit(c) {
    var n = make('div', 'fx fx-hit');
    var w = Math.max(28, c.w * 0.92);
    var h = Math.max(28, c.h * 0.92);
    n.style.left = c.x + 'px';
    n.style.top = c.y + 'px';
    n.style.width = w + 'px';
    n.style.height = h + 'px';
    return spawn(n, 140);
  }

  /* ── 碎片 / 击杀 / 状态 ── */

  function spawnShards(c, count) {
    var made = 0;
    for (var i = 0; i < count; i++) {
      var s = make('div', 'fx fx-shard');
      var ang = (Math.PI * 2 * i) / count + Math.random() * 0.5;
      var dist = 16 + Math.random() * 18;
      s.style.left = (c.x + Math.cos(ang) * c.w * 0.22) + 'px';
      s.style.top = (c.y + Math.sin(ang) * c.h * 0.22) + 'px';
      s.style.setProperty('--dx', (Math.cos(ang) * dist).toFixed(1) + 'px');
      s.style.setProperty('--dy', (Math.sin(ang) * dist).toFixed(1) + 'px');
      if (spawn(s, 220)) made++;
      else break;
    }
    return made;
  }

  /* ── 公开 API ── */

  var STATUS_OK = {
    burn: 1, poison: 1, weak: 1, frail: 1,
    strength: 1, dexterity: 1, regenerate: 1, thorns: 1
  };

  var FX = {

    version: VERSION,

    init: function (opts) {
      opts = opts || {};
      layer = opts.layer || document.getElementById('fx-layer');
      if (!layer) return false;
      hasInit = true;
      FX.setIntensity(opts.intensity || 'mid');
      return true;
    },

    setIntensity: function (level) {
      if (level !== 'low' && level !== 'mid' && level !== 'high') level = 'mid';
      intensity = level;
      try {
        var b = document.body;
        if (b) {
          b.classList.remove('fx-low', 'fx-mid', 'fx-high');
          b.classList.add('fx-' + level);
        }
      } catch (e) { /* 静默 */ }
    },

    getIntensity: function () { return intensity; },

    damage: function (rect, amount, veins) {
      try {
        if (!hasInit || intensity === 'low' && false) return;
        var c = center(rect);
        if (!c) return;
        spawnScar(c, veins);
        if (intensity !== 'low') spawnHit(c);
        var n = Number(amount);
        if (isFinite(n) && n > 0) spawnNum(c, '-' + n, 'dmg');
      } catch (e) { /* 静默 */ }
    },

    block: function (rect, amount) {
      try {
        if (!hasInit) return;
        var c = center(rect);
        if (!c) return;
        spawnShards(c, 5);
        var n = Number(amount);
        if (isFinite(n) && n > 0) spawnNum(c, '◈' + n, 'blk');
      } catch (e) { /* 静默 */ }
    },

    heal: function (rect, amount) {
      try {
        if (!hasInit) return;
        var c = center(rect);
        if (!c) return;
        var n = Number(amount);
        if (isFinite(n) && n > 0) spawnNum(c, '+' + n, 'heal');
      } catch (e) { /* 静默 */ }
    },

    status: function (rect, code) {
      try {
        if (!hasInit || intensity === 'low') return;
        if (!STATUS_OK[code]) return;
        var c = center(rect);
        if (!c) return;
        var n = make('div', 'fx fx-st ' + code);
        n.style.left = c.x + 'px';
        n.style.top = c.y + 'px';
        spawn(n, 340);
      } catch (e) { /* 静默 */ }
    },

    kill: function (rect) {
      try {
        if (!hasInit) return;
        var c = center(rect);
        if (!c) return;
        var n = make('div', 'fx fx-kill');
        n.style.left = c.x + 'px';
        n.style.top = c.y + 'px';
        n.style.width = Math.max(40, c.w * 1.1) + 'px';
        n.style.height = Math.max(40, c.h * 1.1) + 'px';
        spawn(n, 300);
      } catch (e) { /* 静默 */ }
    },

    lockCard: function (cardEl) {
      try {
        if (!cardEl || !cardEl.classList) return;
        cardEl.classList.add('locked');
        if (!cardEl.querySelector('.lock-x')) {
          var x = make('div', 'lock-x');
          cardEl.appendChild(x);
        }
      } catch (e) { /* 静默 */ }
    },

    unlockCard: function (cardEl) {
      try {
        if (!cardEl || !cardEl.classList) return;
        cardEl.classList.remove('locked');
        var x = cardEl.querySelector('.lock-x');
        if (x && x.parentNode) x.parentNode.removeChild(x);
      } catch (e) { /* 静默 */ }
    },

    /* 调试用：当前存活特效数、层是否就绪 */
    _debug: function () { return { live: live, max: MAX_LIVE, layer: !!layer, intensity: intensity }; }
  };

  window.FX = FX;

  // 自动初始化：DOM 就绪后立刻接上层
  function boot() {
    if (hasInit) return;
    FX.init({ layer: document.getElementById('fx-layer') });
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
