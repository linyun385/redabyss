/* T55 地图生成器原型 —— 纯算法，无 DOM 依赖，node 与浏览器皆可跑。
   设计来源：docs/MAPGEN_DESIGN.md（T54 产出）；参数默认值与 tools/mapgen_spec.json 保持同步
   （tools/mapgen_test.js 内置同步断言）。
   本文件不接游戏：不改 web/、engine/、layers/、cards/ 等任何数据文件。
   确定性：全程使用内置 mulberry32 PRNG，禁用 Math.random——同 seed + 同参数 → 完全相同的 Region。 */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.MapGen = factory();
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  /* ── 绑定表载入（T58）：node 读 data/mapgen_bindings.json，浏览器读注入的 window.MAPGEN_BINDINGS ──
     T74 性能：加进程内缓存——原实现每次 generate 都重读并 JSON.parse 52KB（重试多时占近半耗时） */
  var __fs = (typeof require === 'function') ? require('fs') : null;
  var __path = (typeof require === 'function') ? require('path') : null;
  var __bindingsCache = null;
  function loadBindings() {
    if (__bindingsCache) return __bindingsCache;
    if (typeof window !== 'undefined' && window.MAPGEN_BINDINGS) { __bindingsCache = window.MAPGEN_BINDINGS; return __bindingsCache; }
    if (__fs && __path) {
      try {
        __bindingsCache = JSON.parse(__fs.readFileSync(__path.join(__dirname, '..', 'data', 'mapgen_bindings.json'), 'utf8'));
        return __bindingsCache;
      } catch (e) { return null; }
    }
    return null;
  }

  /* ── PRNG（mulberry32）────────────────────────────── */
  function makeRng(seed) {
    var a = seed >>> 0;
    return function () {
      a |= 0; a = (a + 0x6D2B79F5) | 0;
      var t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  /* ── 生态枚举（T54 §0.1，与八层一一对应）──────────── */
  var ECOS = [
    { id: 'eco_surface', homeBand: 1 },
    { id: 'eco_cold',    homeBand: 2 },
    { id: 'eco_arid',    homeBand: 3 },
    { id: 'eco_sea',     homeBand: 4 },
    { id: 'eco_vent',    homeBand: 5 },
    { id: 'eco_rad',     homeBand: 6 },
    { id: 'eco_core',    homeBand: 7 },
    { id: 'eco_nexus',   homeBand: 8 }
  ];

  /* ── 默认参数（唯一来源 tools/mapgen_spec.json；改动须两处同步）── */
  var DEFAULTS = {
    grid: { w: 20, h: 96 },   // T74: 14→20（加宽减阻塞）+ 64→96（节奏，每带 12 行）
    weight: { home: 0.45, adjacentEach: 0.20 },   // T72：主场 0.40–0.50、邻带生态 0.15–0.25
    ruleModulation: [                             // T72：层规则调制（数据镜像 layers.json 的 rule 字段）
      { rule: 'no_light',  affinity: 'light',   factor: 0.5 },
      { rule: 'dim',       affinity: 'light',   factor: 0.75 },
      { rule: 'dry',       affinity: 'water',   factor: 0.6 },
      { rule: 'bright',    affinity: 'light',   factor: 1.25 },
      { rule: 'heat_tick', affinity: 'heat',    factor: 1.1 },
      { rule: 'rad_tick',  affinity: 'mineral', factor: 1.05 },
      { rule: 'burn_hand', affinity: 'heat',    factor: 1.1 }
    ],
    ruleByBand: { 1: 'no_light', 2: 'dim', 3: 'dry', 4: 'bright', 5: 'heat_tick', 6: 'rad_tick', 7: 'burn_hand', 8: 'time_loop' },
    bandMix: { countMin: 2, countMax: 4, maxShare: 0.60, adjacentIntersect: 1, perBandComponents: 3 },
    ecoGrowth: { kappa: 0.7, minPatchArea: 8, maxComponents: 2 },   // T74: 12→8（配合加宽，少回改）
    node: { minSameTypeDist: 2, maxInDeg: 3, fbInDegCap: 10, verticalSpacing: 1 },   // T74: fb 帽 6→10（band8 底部漏斗容量，T73 同款杠杆）；纵向间距 ≥2→≥1（死锁主因，允许项）
    edge: {
      outDegMin: 1, outDegMax: 3, maxLen: 4, extraBranchOdds: 0.15,   // T73: 降低分叉→步数拉长
      // 位移表 v1.2：dy 1..4 × |dx| 0..4 全覆盖（len=max(|dx|,dy)≤4 与 maxLen 闸门一致），
      // 名义角 {0,±35,±60,±85} 按最近实际角归桶（见 tools/mapgen_spec.json displacementTable）。
      // T55 实测：窄表×稀疏行分布会让过半节点零上游候选（connect.indeg 高发），故扩为全覆盖。
      displacement: (function () {
        var d = [];
        for (var dy = 1; dy <= 4; dy++)
          for (var adx = 0; adx <= 4; adx++) {
            if (adx === 0) { d.push([0, dy]); continue; }
            d.push([adx, dy], [-adx, dy]);
          }
        return d;
      })()
    },
    quota: { // T74 v3（下限语义）：T73 表 ×1.5（带高 8→12 行等比摊开），总节点 ≈246
      1: { combat: 11, elite: 0, random: 5, shop: 2, event: 5 },
      2: { combat: 12, elite: 3, random: 5, shop: 2, event: 5 },
      3: { combat: 12, elite: 3, random: 5, shop: 2, event: 5 },
      4: { combat: 13, elite: 3, random: 6, shop: 2, event: 8 },
      5: { combat: 13, elite: 5, random: 6, shop: 2, event: 7 },
      6: { combat: 13, elite: 5, random: 6, shop: 2, event: 7 },
      7: { combat: 15, elite: 4, random: 6, shop: 2, event: 8 },
      8: { combat: 13, elite: 4, random: 5, shop: 2, event: 5, finalBoss: 1 }   // T74: 30（×1.5 约量）；漏斗只收最底 1 行槽位（见 growDAG 收束注释）
    },
    quotaScale: 1.0,               // 调试页「节点数」滑块用的整体缩放
    retry: { max: 300 },
    visibility: { depth: 1 },
    binding: { shopTierByBand: { lo: 3, mid: 6 } } // band≤3→1，≤6→2，否则 3
  };

  var GenError = function (reason, detail) {
    var e = new Error('GenError: ' + reason + (detail ? ' (' + detail + ')' : ''));
    e.reason = reason; e.isGenError = true;
    return e;
  };

  /* ── 基础几何 ─────────────────────────────────────── */
  function bandRowsOf(p) { return p.grid.h / 8; }
  function bandOfY(y, h, br) { return 8 - Math.min(7, Math.floor((h - 1 - y) / br)); }
  function bandRange(b, br) { return { top: (b - 1) * br, bottom: b * br - 1 }; } // 闭区间

  // Bresenham：两端点含在内；interior = 去掉首尾
  function lineCells(x0, y0, x1, y1) {
    var cells = [], dx = Math.abs(x1 - x0), sx = x0 < x1 ? 1 : -1,
        dy = -Math.abs(y1 - y0), sy = y0 < y1 ? 1 : -1, err = dx + dy, x = x0, y = y0, guard = 0;
    while (guard++ < 4096) {
      cells.push([x, y]);
      if (x === x1 && y === y1) break;
      var e2 = 2 * err;
      if (e2 >= dy) { err += dy; x += sx; }
      if (e2 <= dx) { err += dx; y += sy; }
    }
    return cells;
  }

  /* ── 确定性最小堆（cost 平序按插入序）───────────────── */
  function Heap() { this.a = []; this.seq = 0; }
  Heap.prototype.push = function (cost, item) {
    var a = this.a, i = a.length;
    a.push({ c: cost, s: this.seq++, it: item });
    while (i > 0) {
      var p = (i - 1) >> 1;
      if (a[p].c <= a[i].c && a[p].s <= a[i].s) break; // s 兜底同 cost 稳定
      if (a[p].c < a[i].c || (a[p].c === a[i].c && a[p].s < a[i].s)) break;
      var t = a[p]; a[p] = a[i]; a[i] = t; i = p;
    }
  };
  Heap.prototype.pop = function () {
    var a = this.a, top = a[0], last = a.pop();
    if (a.length) {
      a[0] = last; var i = 0;
      for (;;) {
        var l = 2 * i + 1, r = l + 1, m = i;
        if (l < a.length && (a[l].c < a[m].c || (a[l].c === a[m].c && a[l].s < a[m].s))) m = l;
        if (r < a.length && (a[r].c < a[m].c || (a[r].c === a[m].c && a[r].s < a[m].s))) m = r;
        if (m === i) break;
        var t = a[m]; a[m] = a[i]; a[i] = t; i = m;
      }
    }
    return top ? top.it : null;
  };
  Object.defineProperty(Heap.prototype, 'size', { get: function () { return this.a.length; } });

  /* ── 步骤1：生态生长（多源泛洪 + 小块合并）──────────── */
  var DIRS4 = [[1, 0], [-1, 0], [0, 1], [0, -1]];

  var DIRS4 = [[1, 0], [-1, 0], [0, 1], [0, -1]];

  function buildWeightTable(p) {
    // T72：home 0.45 / 邻带各 0.20（n=1 顶格 0.25，余量入 rest）/ rest 均分；
    // 再按层规则调制（p.ruleModulation × p.ruleByBand），调制后每带归一。
    var W = {};
    ECOS.forEach(function (e) { W[e.id] = {}; });
    var homeW = p.weight.home, adjW = p.weight.adjacentEach;
    for (var b = 1; b <= 8; b++) {
      var home = ECOS.filter(function (e) { return e.homeBand === b; })[0];
      var adj = ECOS.filter(function (e) { return Math.abs(e.homeBand - b) === 1; });
      var rest = ECOS.filter(function (e) { return Math.abs(e.homeBand - b) >= 2; });
      W[home.id][b] = homeW;
      var adjEach = Math.min(0.25, Math.max(0.15, adjW * 2 / adj.length));
      var adjSum = 0;
      adj.forEach(function (e) { W[e.id][b] = adjEach; adjSum += adjEach; });
      var restW = Math.max(0, 1 - homeW - adjSum) / Math.max(1, rest.length);
      rest.forEach(function (e) { W[e.id][b] = restW; });
    }
    (p.ruleModulation || []).forEach(function (m) {
      if (!m.affinity) return;
      for (var b2 = 1; b2 <= 8; b2++) {
        if ((p.ruleByBand || {})[b2] !== m.rule) continue;
        ECOS.forEach(function (e) {
          if (e.veinAffinity === m.affinity && W[e.id][b2] !== undefined) W[e.id][b2] *= m.factor;
        });
      }
    });
    for (var b3 = 1; b3 <= 8; b3++) {
      var sum = 0;
      ECOS.forEach(function (e) { sum += W[e.id][b3]; });
      ECOS.forEach(function (e) { if (sum > 0) W[e.id][b3] /= sum; });
    }
    return W;
  }

  function componentsOf(ecoOf, w, h, ecoId) {
    var seen = new Array(w * h).fill(false), comps = [];
    for (var i = 0; i < w * h; i++) {
      if (seen[i] || ecoOf[i] !== ecoId) continue;
      var comp = [], stack = [i]; seen[i] = true;
      while (stack.length) {
        var c = stack.pop(); comp.push(c);
        var x = c % w, y = (c / w) | 0;
        [[1, 0], [-1, 0], [0, 1], [0, -1]].forEach(function (d) {
          var nx = x + d[0], ny = y + d[1];
          if (nx < 0 || ny < 0 || nx >= w || ny >= h) return;
          var ni = ny * w + nx;
          if (!seen[ni] && ecoOf[ni] === ecoId) { seen[ni] = true; stack.push(ni); }
        });
      }
      comps.push(comp);
    }
    return comps;
  }

  function growEcos(rng, p, W) {

    var w = p.grid.w, h = p.grid.h, br = bandRowsOf(p), n = w * h;
    var ecoOf = new Array(n).fill(null);
    // T74 性能：邻接表预计算（泛洪从「每格闭包 + 边界判断」改为整数表查表；n=1920 × 多轮组件扫描是热点）
    var NB = new Int32Array(n * 4);
    for (var nc = 0; nc < n; nc++) {
      var nx0 = nc % w, ny0 = (nc / w) | 0, j0 = nc * 4;
      NB[j0] = nx0 > 0 ? nc - 1 : -1;
      NB[j0 + 1] = nx0 < w - 1 ? nc + 1 : -1;
      NB[j0 + 2] = ny0 > 0 ? nc - w : -1;
      NB[j0 + 3] = ny0 < h - 1 ? nc + w : -1;
    }
    var pq = new Heap();
    ECOS.forEach(function (e) {
      var rg = bandRange(e.homeBand, br);
      var x = Math.floor(rng() * w), y = rg.top + Math.floor(rng() * br);
      pq.push(0, [y * w + x, e.id]);
    });
    var stepK = 0.6 * p.ecoGrowth.kappa, noiseK = 1.6 * (1 - p.ecoGrowth.kappa);
    while (pq.size) {
      var it = pq.pop(), cell = it[0], eco = it[1];
      if (ecoOf[cell] !== null) continue;
      ecoOf[cell] = eco;
      for (var q4 = cell * 4; q4 < cell * 4 + 4; q4++) {
        var niQ = NB[q4];
        if (niQ < 0 || ecoOf[niQ] !== null) continue;
        var cost = (1 - W[eco][bandOfY((niQ / w) | 0, h, br)]) * stepK + rng() * noiseK;
        pq.push(cost, [niQ, eco]);
      }
    }
    var bandOfCell = function (c) { return bandOfY((c / w) | 0, h, br); };
    function compsOf(pred) {
      var seen = new Array(n).fill(false), out = [];
      for (var i = 0; i < n; i++) {
        if (seen[i] || !pred(i, ecoOf[i])) continue;
        var comp = [], st = [i]; seen[i] = true;
        while (st.length) {
          var c = st.pop(); comp.push(c);
          for (var j = c * 4; j < c * 4 + 4; j++) {
            var ni = NB[j];
            if (ni >= 0 && !seen[ni] && pred(ni, ecoOf[ni])) { seen[ni] = true; st.push(ni); }
          }
        }
        out.push(comp);
      }
      return out;
    }
    function borderOf(comp, exclude) {
      var inComp = {}; comp.forEach(function (c) { inComp[c] = true; });
      var border = {};
      comp.forEach(function (c) {
        for (var j = c * 4; j < c * 4 + 4; j++) {
          var ni = NB[j];
          if (ni < 0) continue;
          var o = ecoOf[ni];
          if (o && o !== exclude && !inComp[ni]) border[o] = (border[o] || 0) + 1;
        }
      });
      return border;
    }
    function relabelTo(comp, forceTarget) {
      var target = forceTarget;
      if (!target) {
        var border = borderOf(comp, null);
        var keys = Object.keys(border);
        if (!keys.length) return false;
        keys.sort(function (a, b) { return border[b] - border[a] || (a < b ? -1 : 1); });
        target = keys[0];
      }
      comp.forEach(function (c) { ecoOf[c] = target; });
      return true;
    }
    function dominantEco(band, except) {
      var cnt = {};
      for (var i = 0; i < n; i++) if (bandOfCell(i) === band) { var o = ecoOf[i]; if (o !== except) cnt[o] = (cnt[o] || 0) + 1; }
      var best = null, bn = -1;
      Object.keys(cnt).forEach(function (e) { if (cnt[e] > bn) { bn = cnt[e]; best = e; } });
      return best;
    }
    function reviveLast(comp, eco) {   // 灭门复活：最后一块不并入，从邻居圈地补足 minPatch
      var need = p.ecoGrowth.minPatchArea - comp.length;
      var border = borderOf(comp, null);
      var keys = Object.keys(border).sort(function (a, b) { return border[b] - border[a]; });
      for (var ki = 0; ki < keys.length; ki++) {
        var donor = keys[ki], claimed = [], guard = 0;
        var frontier = comp.slice();
        while (claimed.length < need && guard++ < 500) {
          var grew = false;
          for (var fi = 0; fi < frontier.length; fi++) {
            var c = frontier[fi], x = c % w, y = (c / w) | 0;
            for (var di = 0; di < 4; di++) {
              var d = DIRS4[di], nx = x + d[0], ny = y + d[1];
              if (nx < 0 || ny < 0 || nx >= w || ny >= h) continue;
              var ni = ny * w + nx;
              if (ecoOf[ni] === donor && claimed.indexOf(ni) < 0 && comp.indexOf(ni) < 0) {
                claimed.push(ni); frontier.push(ni); grew = true;
                if (claimed.length >= need) break;
              }
            }
            if (claimed.length >= need) break;
          }
          if (!grew) break;
        }
        if (claimed.length >= need) {
          claimed.forEach(function (c) { ecoOf[c] = eco; });
          return true;
        }
      }
      return false;
    }
    function scanGroups() {          // 全局（按生态）+ 带内（生态×带，带内真连通）组件分组
      // T74 修正：带内组件必须是「带内连通分量」（泛洪限制在带内）——旧实现把全局组件按起始格分带，
      // 跨带舌状渗入的「一指」在 merge 阶段不可见，最后 bandmix.comps 断言才炸（12 行带高发）。
      var seen = new Int32Array(n), out = { global: {}, band: {} };
      for (var i = 0; i < n; i++) {
        if (seen[i]) continue;
        var o = ecoOf[i], comp = [], st = [i];
        seen[i] = 1;
        while (st.length) {
          var c = st.pop(); comp.push(c);
          for (var j = c * 4; j < c * 4 + 4; j++) {
            var ni = NB[j];
            if (ni >= 0 && !seen[ni] && ecoOf[ni] === o) { seen[ni] = 1; st.push(ni); }
          }
        }
        (out.global[o] = out.global[o] || []).push(comp);
      }
      for (var b = 1; b <= 8; b++) {
        var top = (b - 1) * br, bot = b * br - 1;
        var seenB = new Int32Array(n);
        for (var y = top; y <= bot; y++) {
          for (var x = 0; x < w; x++) {
            var c0 = y * w + x;
            if (seenB[c0]) continue;
            var o2 = ecoOf[c0], comp2 = [], st2 = [c0];
            seenB[c0] = 1;
            while (st2.length) {
              var c2 = st2.pop(); comp2.push(c2);
              for (var j2 = c2 * 4; j2 < c2 * 4 + 4; j2++) {
                var ni2 = NB[j2];
                if (ni2 < 0 || seenB[ni2]) continue;
                var ny2 = (ni2 / w) | 0;
                if (ny2 < top || ny2 > bot) continue;   // 限制在带内
                if (ecoOf[ni2] === o2) { seenB[ni2] = 1; st2.push(ni2); }
              }
            }
            var key = o2 + '@' + b;
            (out.band[key] = out.band[key] || []).push(comp2);
          }
        }
      }
      return out;
    }
    function mergeSmallAndCap() {   // 全局碎片(<minPatch) + 每带连通块上限 + 全局分量上限
      // T74: 每轮扫描批量处理全部违规项（原「每轮只修最差一个」在 ×2.1 网格上轮数爆炸）
      var changed = false, guard = 0;
      for (;;) {
        if (++guard > 100) throw GenError('eco.merge.loop');
        var groups = scanGroups();
        var acted = false;
        Object.keys(groups.global).forEach(function (eco) {
          var comps = groups.global[eco];
          comps.forEach(function (comp) {
            if (comp.length < p.ecoGrowth.minPatchArea) {
              if (comps.length === 1) { if (reviveLast(comp, eco)) acted = true; }
              else { if (relabelTo(comp, null)) acted = true; }
            }
          });
          if (comps.length > p.ecoGrowth.maxComponents) {
            comps.sort(function (a, c) { return a.length - c.length; });
            for (var i = 0; i < comps.length - p.ecoGrowth.maxComponents; i++)
              if (relabelTo(comps[i], null)) acted = true;
          }
        });
        Object.keys(groups.band).forEach(function (key) {
          var comps = groups.band[key];
          if (comps.length > p.bandMix.perBandComponents) {
            comps.sort(function (a, c) { return a.length - c.length; });
            for (var i = 0; i < comps.length - p.bandMix.perBandComponents; i++)
              if (relabelTo(comps[i], null)) acted = true;
          }
        });
        if (!acted) return changed;
        changed = true;
      }
    }
    function fixTonguesAndCount() { // 相邻带交集 ≥1 + 带内单生态补块（2×6=12 格补丁）——T74: bandCells 查表
      var changed = false;
      for (var b = 1; b <= 8; b++) {
        var cellsB = bandCells[b], cnt = {}, tot = cellsB.length;
        cellsB.forEach(function (c) { var o = ecoOf[c]; cnt[o] = (cnt[o] || 0) + 1; });
        var ecos = Object.keys(cnt);
        if (ecos.length >= p.bandMix.countMin) {
          if (b <= 7) {
            var setB = {};
            bandCells[b + 1].forEach(function (c) { setB[ecoOf[c]] = true; });
            var shared = ecos.some(function (e) { return setB[e]; });
            if (shared) continue;
          } else continue;
        }
        var cand = [];
        if (b > 1) { var e0 = dominantEco(b - 1, ecos[0]); if (e0 && ecos.indexOf(e0) < 0) cand.push({ eco: e0, edgeRow: bandRange(b, br).top }); }
        if (b < 8) { var e1 = dominantEco(b + 1, ecos[0]); if (e1 && ecos.indexOf(e1) < 0) cand.push({ eco: e1, edgeRow: bandRange(b, br).bottom - 1 }); }
        var placed = false;
        for (var ci = 0; ci < cand.length && !placed; ci++) {
          var E = cand[ci].eco, r0 = cand[ci].edgeRow;
          for (var att = 0; att < 24 && !placed; att++) {
            var x0 = Math.floor(rng() * (w - 6));
            var ok = true;
            for (var yy = r0; yy < r0 + 2 && ok; yy++)
              for (var xx = x0; xx < x0 + 6 && ok; xx++)
                if (ecoOf[yy * w + xx] === E) ok = false;
            if (!ok) continue;
            for (var yy2 = r0; yy2 < r0 + 2; yy2++)
              for (var xx2 = x0; xx2 < x0 + 6; xx2++) ecoOf[yy2 * w + xx2] = E;
            placed = true; changed = true;
          }
        }
        if (!placed) throw GenError('bandmix.patch', 'b' + b);
      }
      return changed;
    }
    function shareTrim() {          // 单带最大生态占比 >60% → 切 12 格给次生态
      // T74: 网格 ×2.1 后，一轮一刀收敛不动了——改为带内循环切到达标（每刀仍 12 格连续块）
      var changed = false;
      for (var b = 1; b <= 8; b++) {
        var cellsB = bandCells[b], guardB = 0;
        for (;;) {
          if (++guardB > 8) break;   // 单带最多 8 刀（12/240≈5%/刀，>60% 最多 3-4 刀即达标）
          var cnt = {}, cells = {}, tot = cellsB.length;
          cellsB.forEach(function (c) { var o = ecoOf[c]; cnt[o] = (cnt[o] || 0) + 1; (cells[o] = cells[o] || []).push(c); });
          var ecos = Object.keys(cnt);
          if (ecos.length < 2) break;
          ecos.sort(function (a, c) { return cnt[c] - cnt[a]; });
          var top = ecos[0];
          if (cnt[top] / tot <= p.bandMix.maxShare) break;
          var second = ecos[1];
          var topCells = cells[top];
          var seed = null;
          topCells.forEach(function (c) {
            var x = c % w, y = (c / w) | 0;
            if (seed) return;
            for (var di = 0; di < 4; di++) {
              var d = DIRS4[di], nx = x + d[0], ny = y + d[1];
              if (nx < 0 || ny < 0 || nx >= w || ny >= h) continue;
              if (ecoOf[ny * w + nx] === second) { seed = c; return; }
            }
          });
          if (seed === null) seed = topCells[Math.floor(rng() * topCells.length)];
          var cut = [seed], frontier = [seed], guard = 0;
          while (cut.length < 12 && guard++ < 300) {
            var grew = false;
            for (var fi = 0; fi < frontier.length && cut.length < 12; fi++) {
              var c = frontier[fi], x = c % w, y = (c / w) | 0;
              for (var di2 = 0; di2 < 4 && cut.length < 12; di2++) {
                var d2 = DIRS4[di2], nx = x + d2[0], ny = y + d2[1];
                if (nx < 0 || ny < 0 || nx >= w || ny >= h) continue;
                var ni = ny * w + nx;
                if (ecoOf[ni] === top && cut.indexOf(ni) < 0) { cut.push(ni); frontier.push(ni); grew = true; }
              }
            }
            if (!grew) break;
          }
          cut.forEach(function (c) { ecoOf[c] = second; }); changed = true;
        }
      }
      return changed;
    }
    // T74: 带内格表一次分桶（tongues/share/终检从 O(带数×n) 扫描降为 O(n)+带内表）
    var bandCells = [];
    for (var b10 = 1; b10 <= 8; b10++) bandCells[b10] = [];
    for (var i10 = 0; i10 < n; i10++) bandCells[bandOfCell(i10)].push(i10);
    var pass = 0;
    for (;;) {
      if (++pass > 30) throw GenError('eco.postprocess.loop');   // T74: 10→30（网格 ×2.1，等比放宽）
      var c1 = mergeSmallAndCap();
      var c2 = fixTonguesAndCount();
      var c3 = shareTrim();
      if (!c1 && !c2 && !c3) break;
    }
    // 终检（T74: 一次扫描建 生态×带 格表 + floodCells 桶内泛洪，替代 ~90 次全网格扫描）
    function floodCells(cells) {   // cells 内同生态（可再限同带）的连通分量
      var seen = {}, comps = [];
      cells.forEach(function (c) { seen[c] = false; });
      cells.forEach(function (c) {
        if (seen[c]) return;
        var comp = [], st = [c]; seen[c] = true;
        while (st.length) {
          var u = st.pop(); comp.push(u);
          for (var j = u * 4; j < u * 4 + 4; j++) {
            var v = NB[j];
            if (v >= 0 && seen[v] === false) { seen[v] = true; st.push(v); }
          }
        }
        comps.push(comp);
      });
      return comps;
    }
    var ecoCellsL = {}, bandEcoL = {};
    for (var i4 = 0; i4 < n; i4++) {
      var e4 = ecoOf[i4], b4 = bandOfCell(i4);
      (ecoCellsL[e4] = ecoCellsL[e4] || []).push(i4);
      (bandEcoL[b4 + '|' + e4] = bandEcoL[b4 + '|' + e4] || []).push(i4);
    }
    ECOS.forEach(function (e) { if (!ecoCellsL[e.id]) throw GenError('eco.missing', e.id); });
    ECOS.forEach(function (e) {
      var comps = floodCells(ecoCellsL[e.id]);
      if (comps.length > p.ecoGrowth.maxComponents) throw GenError('eco.maxComponents', e.id);
      comps.forEach(function (comp) {
        if (comp.length < p.ecoGrowth.minPatchArea) throw GenError('eco.minPatch', e.id + '=' + comp.length);
      });
    });
    for (var b = 1; b <= 8; b++) {
      var cnt = {}, ecos = [];
      Object.keys(bandEcoL).forEach(function (k) {
        var pr = k.split('|');
        if (+pr[0] === b) { ecos.push(pr[1]); cnt[pr[1]] = bandEcoL[k].length; }
      });
      var tot = bandCells[b].length;
      if (ecos.length < p.bandMix.countMin || ecos.length > p.bandMix.countMax)
        throw GenError('bandmix.count', 'b' + b + '=' + ecos.length);
      var maxShare = Math.max.apply(null, ecos.map(function (e) { return cnt[e] / tot; }));
      if (maxShare > p.bandMix.maxShare) throw GenError('bandmix.share', 'b' + b + '=' + maxShare.toFixed(2));
      ecos.forEach(function (e) {
        var comps = floodCells(bandEcoL[b + '|' + e]);
        if (comps.length > p.bandMix.perBandComponents)
          throw GenError('bandmix.comps', e + '@b' + b + '=' + comps.length);
      });
    }
    for (var bb = 1; bb <= 7; bb++) {
      var sa = {}, sb = {};
      Object.keys(bandEcoL).forEach(function (k) {
        var pr = k.split('|');
        if (+pr[0] === bb) sa[pr[1]] = true; else if (+pr[0] === bb + 1) sb[pr[1]] = true;
      });
      if (!Object.keys(sa).some(function (e) { return sb[e]; }))
        throw GenError('bandmix.intersect', 'b' + bb);
    }
    return ecoOf;
  }

  /* ── 步骤2：事件格布点（配额 + 蓝噪声分散）──────────── */
  function effectiveQuota(p) {
    var q = {}, s = p.quotaScale;
    for (var b = 1; b <= 8; b++) {
      q[b] = {};
      var src = DEFAULTS.quota[b];
      Object.keys(src).forEach(function (t) {
        var v = src[t];
        if (t !== 'finalBoss') v = Math.max(t === 'combat' ? 1 : 0, Math.round(v * s));
        q[b][t] = v;
      });
      if (b === 8) q[b].finalBoss = 1;
    }
    return q;
  }

  function dispSet(p) {
    var s = {};
    p.edge.displacement.forEach(function (c) { s[c[0] + ',' + c[1]] = true; });
    return s;
  }
  function dispOkD(disp, maxLen, dx, dy) {
    return dy >= 1 && disp[dx + ',' + dy] && Math.max(Math.abs(dx), dy) <= maxLen;
  }

  function shuffleInPlace(arr, rng) {
    for (var i = arr.length - 1; i > 0; i--) {
      var j = Math.floor(rng() * (i + 1));
      var t = arr[i]; arr[i] = arr[j]; arr[j] = t;
    }
  }

  /* ── 步骤2+3（生长式合并）：事件格布点 + 连线 ─────────
     T55 实测取舍：先撒点后连线是两个约束求解器互相打架（布点不知连线可达性，
     连线受度上限与路径占用夹击，重试常耗尽）。改为「行槽位 + 前置队列生长」：
     配额先摊到每行（行均衡，保每行有节点→下游候选密度），frontier 自下而上生长，
     节点落格的同时连上父边——「除起点外每节点有入边」由构造保证。
     叶子（零出边）在后置阶段处理：先试直连，失败则搬迁重建（父边拆了重连，
     内部格按边独占可安全拆除）。产出与数据模型不变（实现策略变体，T55 记录）。 */
  function growDAG(rng, ecoOf, p) {
    var w = p.grid.w, h = p.grid.h, br = bandRowsOf(p);
    var q = effectiveQuota(p), D = p.node.minSameTypeDist;
    var disp = dispSet(p), k = p.edge.maxLen;
    var nodes = [], edges = [];
    var byCell = new Array(w * h).fill(null), interiorUsed = new Uint8Array(w * h);   // T74: y*w+x 整数索引（字符串键拼接是百万级热点）
    var edgeCells = [];   // 与 edges 平行：每条边的中间格列表（拆除时反标）
    // 行槽位：slots[b][rowLocal] = 待落类型数组（band1 排除行 0=起点行；band8 排除行 br−1=fb 行；
    // band8 倒数第二行不加量——该行下游只有 fb，要给 fb 入度留余量）
    var slots = {}, totalRemaining = 0;
    var quotaOrder = ['combat', 'elite', 'random', 'shop', 'event', 'finalBoss'];
    for (var b = 1; b <= 8; b++) {
      var items = [];
      quotaOrder.forEach(function (type) {
        var need = (q[b][type] || 0);
        if (type === 'combat' && b === 1) need -= 1;      // 起点已计入
        if (type === 'finalBoss' && b === 8) need -= 1;   // fb 已预留
        for (var i = 0; i < need; i++) items.push(type);
      });
      shuffleInPlace(items, rng);
      var rowBase = (b === 1) ? 1 : 0;
      var rowSpan = (b === 1 || b === 8) ? br - 1 : br;
      var rowList = [];
      for (var r = 0; r < rowSpan; r++) rowList.push(rowBase + r);
      slots[b] = {};
      rowList.forEach(function (r) { slots[b][r] = []; });
      // T74: band8 槽位分布加权——上部 5 行 ×2、下部 6 行 ×1，
      // 上部有 20 列回旋余地，下部越靠近 fb 走廊越窄（±4），重配只会制造死叶（旧 r6Guarantee 已移除）
      var seq = [];
      if (b === 8) {
        var lateFrom = 5;   // rowSpan=11：局部行 0-4（y 84-88）×2，5-10（y 89-94）×1
        rowList.forEach(function (r) {
          seq.push(r);
          if (r < lateFrom) seq.push(r);
        });
      } else {
        seq = rowList.slice();
      }
      for (var i2 = 0; i2 < items.length; i2++) {
        var rr = seq[i2 % seq.length];
        if (b === 8 && rr === rowSpan - 1) rr = seq[(i2 + 1) % seq.length]; // 末行不加量
        slots[b][rr].push(items[i2]);
        totalRemaining += 1;
      }
    }
    function pathClear(x0, y0, x1, y1) {
      // T74: Bresenham 内联无分配版（原 lineCells 每候选分配数组，10k+ 次/图成 GC 热点）；首尾格不计，同原口径
      var dx = Math.abs(x1 - x0), sx = x0 < x1 ? 1 : -1,
          dy = -Math.abs(y1 - y0), sy = y0 < y1 ? 1 : -1, err = dx + dy, x = x0, y = y0, guard = 0;
      for (;;) {
        var e2 = 2 * err;
        if (e2 >= dy) { err += dy; x += sx; }
        if (e2 <= dx) { err += dx; y += sy; }
        if (x === x1 && y === y1) return true;
        if (++guard > 4096) return false;
        var key = y * w + x;
        if (byCell[key] || interiorUsed[key]) return false;
      }
    }
    function markInterior(x0, y0, x1, y1) {
      var ic = lineCells(x0, y0, x1, y1).slice(1, -1);
      ic.forEach(function (c) { interiorUsed[c[1] * w + c[0]] = 1; });
      return ic;
    }
    function addNode(type, x, y) {
      var nd = {
        id: 'n' + nodes.length, type: type, x: x, y: y,
        band: bandOfY(y, h, br), eco: ecoOf[y * w + x],
        crossBandIn: false, binding: null, _out: [], _in: []
      };
      nodes.push(nd); byCell[y * w + x] = nd;
      bucketAdd(nd);
      return nd;
    }
    function addEdge(u, v, dx, dy) {
      if (u._out.indexOf(v) >= 0) return null;   // 防平行重复边（fb 直连 dx=0,dy=1 中间格为空时会漏）
      var e = {
        from: u.id, to: v.id, dx: dx, dy: dy,
        len: Math.max(Math.abs(dx), dy),
        angle: Math.round(Math.atan2(Math.abs(dx), dy) * 180 / Math.PI * 10) / 10,
        crossBand: false
      };
      edgeCells.push(markInterior(u.x, u.y, v.x, v.y));
      edges.push(e);
      u._out.push(v); v._in.push(u);
      return e;
    }
    function removeEdge(e) {
      var idx = edges.indexOf(e);
      if (idx < 0) return;
      edges.splice(idx, 1);
      var ic = edgeCells.splice(idx, 1)[0];
      ic.forEach(function (c) { interiorUsed[c[1] * w + c[0]] = 0; });
      var u = byIdOf(nodes, e.from), v = byIdOf(nodes, e.to);
      u._out.splice(u._out.indexOf(v), 1);
      v._in.splice(v._in.indexOf(u), 1);
    }
    // T74 索引：同带同列节点查 byCell，同带同类型查 typeCells 桶——把 O(N) 扫描降为 O(1)/O(桶)
    var typeCells = {};   // 'band|type' -> [{x,y,n}]
    function bucketAdd(nd) {
      var key = nd.band + '|' + nd.type;
      (typeCells[key] = typeCells[key] || []).push({ x: nd.x, y: nd.y, n: nd });
    }
    function bucketMove(nd, nx, ny) {
      var arr = typeCells[nd.band + '|' + nd.type] || [];
      for (var i = 0; i < arr.length; i++) if (arr[i].n === nd) { arr[i].x = nx; arr[i].y = ny; return; }
    }
    // T73 纵向间距：同带同列的两节点 y 间隔 ≥ spacing（T74 放宽为 1；查 byCell 而非全节点）
    function verticalOk(band, x, y, exclude) {
      var s = p.node.verticalSpacing;
      for (var d = 1; d < s; d++) {
        var up = byCell[(y - d) * w + x];
        if (up && up !== exclude && up.band === band) return false;
        var dn = byCell[(y + d) * w + x];
        if (dn && dn !== exclude && dn.band === band) return false;
      }
      return true;
    }
    function sameTypeOk(band, type, x, y, exclude) {
      var arr = typeCells[band + '|' + type];
      if (!arr) return true;
      for (var i = 0; i < arr.length; i++) {
        var o = arr[i];
        if (o.n === exclude) continue;
        if (Math.abs(o.x - x) + Math.abs(o.y - y) < D) return false;
      }
      return true;
    }
    // 落点是否有「下游潜力」：下方 k 行内既有节点可连 / fb 可连（有余量）/ 还有空槽位可落
    // T74: 只扫下方 k 行 × ±k 列（byCell）；fb 检查加注入度帽（防 band8 尾部成批叶子）
    function hasDownPotential(tx, ty) {
      // T74: 槽位检查提前短路（常见命中省 36 次查格）；fb 查注入度帽
      for (var dy2 = 1; dy2 <= k; dy2++) {
        var yy = ty + dy2;
        if (yy >= h) break;
        var tb2 = bandOfY(yy, h, br), rl2 = yy - (tb2 - 1) * br;
        if (slots[tb2][rl2] && slots[tb2][rl2].length) return true;
      }
      if (fb._in.length < p.node.fbInDegCap && dispOkD(disp, k, fb.x - tx, fb.y - ty)) return true;
      for (var dy3 = 1; dy3 <= k; dy3++) {
        var yy3 = ty + dy3;
        if (yy3 >= h) break;
        for (var dx3 = -k; dx3 <= k; dx3++) {
          var xx3 = tx + dx3;
          if (xx3 < 0 || xx3 >= w) continue;
          var o = byCell[yy3 * w + xx3];
          if (o && o._in && o._in.length < p.node.maxInDeg && dispOkD(disp, k, xx3 - tx, yy3 - ty)) return true;
        }
      }
      return false;
    }
    // 预留起点与 finalBoss（T74: 起点随网格宽取中，不再钉死 14 列的 6–8）
    var startX = Math.floor(w / 2) - 1 + Math.floor(rng() * 3);
    var start = addNode('combat', startX, 0);
    var fb = addNode('finalBoss', Math.floor(w / 2), h - 1);
    var fbIdx = (h - 1) * w + Math.floor(w / 2);

    // T74: 位移表按 dy 预分桶（浅降优先语义不变：逐桶洗牌代替全表 shuffle+稳定排序）
    var dispByDy = [];
    for (var dyB = 0; dyB <= k; dyB++) dispByDy[dyB] = [];
    p.edge.displacement.forEach(function (c) { dispByDy[c[1]].push(c); });
    var frontier = [start];
    // 生长主循环：每轮 frontier 自下而上各生 1 个子节点（深者优先，把槽位往下带）
    var guard = 0;
    while (totalRemaining > 0 && guard++ < 4000) {
      frontier.sort(function (a, c) { return c.y - a.y || (a.id < c.id ? -1 : 1); });
      var progressed = false;
      var spawnLater = [];
      for (var fi = 0; fi < frontier.length; fi++) {
        var u = frontier[fi];
        if (u._blocked || u._out.length >= p.edge.outDegMax) continue;
        var cands = [];
        for (var dyB2 = 1; dyB2 <= k; dyB2++) {
          var bucket = dispByDy[dyB2].slice();
          shuffleInPlace(bucket, rng);
          cands.push.apply(cands, bucket);   // T73 浅降优先：dy 小的先试；同 dy 内已随机
        }
        var done = false;
        // 两轮扫描：先只落在「有下游潜力」的格（防造出注定死叶），再全量兜底（防死锁）
        for (var pass2 = 0; pass2 < 2 && !done; pass2++) {
        for (var ci = 0; ci < cands.length && !done; ci++) {
          if (totalRemaining <= 0) break;
          var dx = cands[ci][0], dy = cands[ci][1];
          var tx = u.x + dx, ty = u.y + dy;
          if (tx < 0 || ty < 0 || tx >= w || ty >= h) continue;
          if (Math.max(Math.abs(dx), dy) > k) continue;
          // 落在 finalBoss 格上 → 直接连入 fb（不占槽位）
          if (ty * w + tx === fbIdx) {
            if (fb._in.length < p.node.fbInDegCap && pathClear(u.x, u.y, tx, ty)) {
              addEdge(u, fb, dx, dy); done = true; progressed = true;
            }
            continue;
          }
          if (byCell[ty * w + tx]) continue;
          if (interiorUsed[ty * w + tx]) continue;   // 不得落在既有边的中间格上（I10）
          var tb = bandOfY(ty, h, br), rl = ty - (tb - 1) * br;
          if (!slots[tb][rl] || !slots[tb][rl].length) continue;  // 该行槽位已满
          // T74: band8 全带收 ±6（两跳内必可汇入 fb），仅最底槽位行（h-2）收 ±4——该行只有 fb 可连
          if (tb === 8 && ty >= h - 2 && Math.abs(tx - fb.x) > k) continue;
          else if (tb === 8 && Math.abs(tx - fb.x) > 6) continue;
          if (!pathClear(u.x, u.y, tx, ty)) continue;             // 边不穿节点/不交叉
          if (pass2 === 0 && !hasDownPotential(tx, ty)) continue; // 不造注定死叶
          if (!verticalOk(tb, tx, ty)) continue;          // T73 纵向间距 ≥2 行
          var pool = slots[tb][rl].filter(function (t) { return sameTypeOk(tb, t, tx, ty); });
          if (!pool.length) continue;
          var type = pool[Math.floor(rng() * pool.length)];
          var slotArr = slots[tb][rl];
          slotArr.splice(slotArr.indexOf(type), 1);   // 只删一个（同类型可能占两槽）
          totalRemaining -= 1;
          var v = addNode(type, tx, ty);
          addEdge(u, v, dx, dy);
          spawnLater.push(v);
          done = true; progressed = true;
        }
        }
        if (!done) u._blocked = true;   // 单调性：格只会更满，这轮全堵 = 永堵
      }
      spawnLater.forEach(function (v) { frontier.push(v); });
      if (!progressed) break;
    }
    // T73 槽位抢救：frontier 卡死后，剩余槽位在**带内迁移**到任何有合法父节点的格子
    //（类型/带不变，行可迁移——槽位语义是「这个带要有这种节点」，不是「必须在第 r 行」）
    var rescueGuard = 0;
    while (totalRemaining > 0 && rescueGuard++ < 200) {
      var progressed = false, slotList = [];
      for (var sb in slots) for (var sr in slots[sb]) if (slots[sb][sr].length)
        slotList.push({ b: +sb, r: +sr, types: slots[sb][sr] });
      for (var si = 0; si < slotList.length && !progressed; si++) {
        var sl = slotList[si], bandTop = (sl.b - 1) * br;
        var rowOrder = [];
        for (var off = 0; off < br; off++) {
          if (sl.r + off < br) rowOrder.push(sl.r + off);
          if (off > 0 && sl.r - off >= 0) rowOrder.push(sl.r - off);
        }
        for (var ri = 0; ri < rowOrder.length && !progressed; ri++) {
          var ty = bandTop + rowOrder[ri];
          for (var tx = 0; tx < w && !progressed; tx++) {
            if (byCell[ty * w + tx]) continue;
            if (interiorUsed[ty * w + tx]) continue;
            if (sl.b === 8 && ty >= h - 2 && Math.abs(tx - fb.x) > k) continue;   // 末槽位行 ±4
            else if (sl.b === 8 && Math.abs(tx - fb.x) > 6) continue;             // 其余 ±6
            if (!hasDownPotential(tx, ty)) continue;               // 抢救落子也要有下游潜力
            if (!verticalOk(sl.b, tx, ty)) continue;
            var type = sl.types[0];
            if (!sameTypeOk(sl.b, type, tx, ty)) continue;
            var parents = [];
            for (var dyP = 1; dyP <= k; dyP++) {
              var yyP = ty - dyP;
              if (yyP < 0) break;
              for (var dxP = -k; dxP <= k; dxP++) {
                var xxP = tx + dxP;
                if (xxP < 0 || xxP >= w) continue;
                var u2 = byCell[yyP * w + xxP];
                if (!u2 || u2 === fb || u2._out.length >= p.edge.outDegMax) continue;
                if (!dispOkD(disp, k, tx - u2.x, ty - u2.y)) continue;
                var cellsP = lineCells(u2.x, u2.y, tx, ty), okP = true;
                for (var ciP = 1; ciP < cellsP.length - 1 && okP; ciP++) {
                  var ckP = cellsP[ciP][1] * w + cellsP[ciP][0];
                  if (byCell[ckP] || interiorUsed[ckP]) okP = false;
                }
                if (okP) parents.push(u2);
              }
            }
            if (!parents.length) continue;
            var u = parents[Math.floor(rng() * parents.length)];
            var type2 = sl.types.shift(); totalRemaining -= 1;
            var v = addNode(type2, tx, ty);
            addEdge(u, v, tx - u.x, ty - u.y);
            frontier.push(v);
            progressed = true;
          }
        }
      }
      if (!progressed) break;
    }
    if (totalRemaining > 0) {
      if (typeof globalThis.__dlHook === 'function') globalThis.__dlHook({ frontier: frontier.map(function (u) { return u.id + '@' + u.x + ',' + u.y + '/b' + u.band + '/out' + u._out.length; }), nodes: nodes.length, slotsLeft: (function () { var c = 0; for (var b in slots) for (var r in slots[b]) c += slots[b][r].length; return c; })(), slotsSnap: (function () { var o = {}; for (var b in slots) for (var r in slots[b]) if (slots[b][r].length) o['b' + b + 'r' + r] = slots[b][r].join('/'); return o; })() });
      throw GenError('grow.deadlock', '剩余槽位 ' + totalRemaining);
    }

    // 叶子补边：非 finalBoss 且零出边的节点（含生长结束时最后一波没轮到出手的），
    // 自下而上处理。先试直连；直连失败则搬迁重建——搬到「所有父边可达 × 某下游可达」
    // 的同带空格，拆旧父边、重连。内部格按边独占（I10），拆除反标是安全的。
    var leaves = nodes.filter(function (u) { return u !== fb && u._out.length === 0; });
    leaves.sort(function (a, c) { return c.y - a.y || (a.id < c.id ? -1 : 1); });
    leaves.forEach(function (u) {
      // ① 直连：向下连已存在的节点（含 fb）——T74: 只扫下方 k 行 × ±k 列
      var cands = [];
      for (var dyL = 1; dyL <= k; dyL++) {
        var yyL = u.y + dyL;
        if (yyL >= h) break;
        for (var dxL = -k; dxL <= k; dxL++) {
          var xxL = u.x + dxL;
          if (xxL < 0 || xxL >= w) continue;
          var vL = byCell[yyL * w + xxL];
          if (!vL) continue;
          var capL = (vL === fb) ? p.node.fbInDegCap : p.node.maxInDeg;
          if (vL._in.length >= capL) continue;
          if (!dispOkD(disp, k, vL.x - u.x, vL.y - u.y)) continue;
          if (!pathClear(u.x, u.y, vL.x, vL.y)) continue;
          cands.push({ v: vL, d: Math.abs(dxL) + Math.abs(dyL) });
        }
      }
      if (cands.length) {
        cands.sort(function (a, c) { return a.d - c.d; });
        addEdge(u, cands[0].v, cands[0].v.x - u.x, cands[0].v.y - u.y);
        return;
      }
      // ② 搬迁：新位须满足 所有父边 disp 可达且路径无遮挡 × 某下游 disp 可达且路径无遮挡 × 同带空格
      var parents = u._in.slice();
      var downs = [];
      for (var dyD = 1; dyD <= k; dyD++) {
        var yyD = u.y + dyD;
        if (yyD >= h) break;
        for (var dxD = -k; dxD <= k; dxD++) {
          var xxD = u.x + dxD;
          if (xxD < 0 || xxD >= w) continue;
          var vD = byCell[yyD * w + xxD];
          if (!vD || vD === u) continue;
          var capD = (vD === fb) ? p.node.fbInDegCap : p.node.maxInDeg;
          if (vD._in.length >= capD) continue;
          if (dispOkD(disp, k, vD.x - u.x, vD.y - u.y)) downs.push(vD);
        }
      }
      downs.sort(function (a, c) {
        return (Math.abs(a.x - u.x) + Math.abs(a.y - u.y)) - (Math.abs(c.x - u.x) + Math.abs(c.y - u.y));
      });
      var moved = false;
      for (var di = 0; di < downs.length && !moved; di++) {
        var wv = downs[di];
        // 候选新位 = 某父节点 + 位移（枚举父节点可达格），且新位到 wv 仍有表内位移
        var cells = [];
        parents.forEach(function (s) {
          p.edge.displacement.forEach(function (c) {
            cells.push([s.x + c[0], s.y + c[1]]);
          });
        });
        for (var cii = 0; cii < cells.length && !moved; cii++) {
          var nx = cells[cii][0], ny = cells[cii][1];
          if (nx < 0 || ny < 0 || nx >= w || ny >= h) continue;
          if (nx === u.x && ny === u.y) continue;                 // 搬回原地无意义（直连已失败）
          if (bandOfY(ny, h, br) !== u.band) continue;            // 同带（保每带配额）
          if (byCell[ny * w + nx]) continue;
          if (interiorUsed[ny * w + nx]) continue;   // 不得搬进既有边的中间格（I10）
          var wdx = wv.x - nx, wdy = wv.y - ny;
          if (!dispOkD(disp, k, wdx, wdy)) continue;
          // 父边全部可重连（一律走完整检查，无豁免分支）
          var parentsOk = true;
          parents.forEach(function (s) {
            if (!dispOkD(disp, k, nx - s.x, ny - s.y)) parentsOk = false;
          });
          if (!parentsOk) continue;
          if (!sameTypeOk(u.band, u.type, nx, ny, u)) continue;
          parents.forEach(function (s) { if (!pathClear(s.x, s.y, nx, ny)) parentsOk = false; });
          if (!parentsOk) continue;
          if (!pathClear(nx, ny, wv.x, wv.y)) continue;
          // 执行搬迁
          byCell[u.y * w + u.x] = null;
          parents.forEach(function (s) {
            removeEdge(edges.filter(function (e) { return e.from === s.id && e.to === u.id; })[0]);
          });
          u.x = nx; u.y = ny;
          u.eco = ecoOf[ny * w + nx];
          u.band = bandOfY(ny, h, br);
          byCell[ny * w + nx] = u;
          bucketMove(u, nx, ny);   // T74: 同类型桶同步（搬迁不换带，桶键不变）
          parents.forEach(function (s) { addEdge(s, u, u.x - s.x, u.y - s.y); });
          addEdge(u, wv, wv.x - u.x, wv.y - u.y);
          moved = true;
        }
      }
      if (!moved) throw GenError('grow.leaf', u.id + '@' + u.x + ',' + u.y);
    });

    // 保跨带：每个带边界至少一条 b→b+1 的边（T74: 只扫边界上下各 k 行，等价于原 disp 闸）
    for (var bb = 1; bb <= 7; bb++) {
      var has = edges.some(function (e) {
        return byIdOf(nodes, e.from).band === bb && byIdOf(nodes, e.to).band === bb + 1;
      });
      if (has) continue;
      var yUmin = Math.max(0, bb * br - k), yUmax = bb * br - 1;
      var yVmin = bb * br, yVmax = Math.min(h - 1, bb * br + k - 1);
      var pairs = [];
      for (var yu = yUmin; yu <= yUmax; yu++) {
        for (var xu = 0; xu < w; xu++) {
          var u = byCell[yu * w + xu];
          if (!u || u === fb || u._out.length >= p.edge.outDegMax) continue;
          for (var yv = yVmin; yv <= yVmax; yv++) {
            for (var xv = 0; xv < w; xv++) {
              var v = byCell[yv * w + xv];
              if (!v || v._in.length >= p.node.maxInDeg) continue;
              var dx = v.x - u.x, dy = v.y - u.y;
              if (!dispOkD(disp, k, dx, dy)) continue;
              if (!pathClear(u.x, u.y, v.x, v.y)) continue;
              pairs.push({ u: u, v: v, d: Math.abs(dx) });
            }
          }
        }
      }
      if (!pairs.length) throw GenError('grow.crossband', 'b' + bb);
      pairs.forEach(function (pr) { pr.r = rng(); });
      pairs.sort(function (a, c) { return a.d - c.d || a.r - c.r; });
      addEdge(pairs[0].u, pairs[0].v, pairs[0].v.x - pairs[0].u.x, pairs[0].v.y - pairs[0].u.y);
    }

    // finalBoss 入边兜底（T74: 只扫 fb 上方 k 行）
    if (!fb._in.length) {
      var ups = [];
      for (var dyF = 1; dyF <= k; dyF++) {
        var yyF = fb.y - dyF;
        if (yyF < 0) break;
        for (var dxF = -k; dxF <= k; dxF++) {
          var xxF = fb.x + dxF;
          if (xxF < 0 || xxF >= w) continue;
          var uF = byCell[yyF * w + xxF];
          if (!uF || uF._out.length >= p.edge.outDegMax) continue;
          if (!dispOkD(disp, k, fb.x - uF.x, fb.y - uF.y)) continue;
          if (!pathClear(uF.x, uF.y, fb.x, fb.y)) continue;
          ups.push(uF);
        }
      }
      if (!ups.length) throw GenError('grow.fbin');
      var u0 = ups[Math.floor(rng() * ups.length)];
      addEdge(u0, fb, fb.x - u0.x, fb.y - u0.y);
    }

    // 补分叉（多样性；同带目标优先；放最后——非硬性约束不与硬性抢走廊）
    // T74: 候选只扫下方 k 行 × ±k 列（disp 闸本就只允许向下 ≤k）
    nodes.forEach(function (u) {
      if (u === fb) return;
      var guardC = 0;
      while (u._out.length < p.edge.outDegMax && rng() < p.edge.extraBranchOdds && guardC++ < 8) {
        var cands = [];
        for (var dyE = 1; dyE <= k; dyE++) {
          var yyE = u.y + dyE;
          if (yyE >= h) break;
          for (var dxE = -k; dxE <= k; dxE++) {
            var xxE = u.x + dxE;
            if (xxE < 0 || xxE >= w) continue;
            var vE = byCell[yyE * w + xxE];
            if (!vE || vE === u || u._out.indexOf(vE) >= 0) continue;
            var capE = (vE === fb) ? p.node.fbInDegCap : p.node.maxInDeg;
            if (vE._in.length >= capE) continue;
            if (!dispOkD(disp, k, vE.x - u.x, vE.y - u.y)) continue;
            if (!pathClear(u.x, u.y, vE.x, vE.y)) continue;
            cands.push(vE);
          }
        }
        if (!cands.length) break;
        var sameBand = cands.filter(function (v) { return v.band === u.band; });
        var pool = sameBand.length ? sameBand : cands;
        var v = pool[Math.floor(rng() * pool.length)];
        addEdge(u, v, v.x - u.x, v.y - u.y);
      }
    });

    nodes.forEach(function (n) { delete n._out; delete n._in; delete n._blocked; });
    return { nodes: nodes, edges: edges, start: start, finalBoss: fb };
  }
  function byIdOf(nodes, id) {
    for (var i = 0; i < nodes.length; i++) if (nodes[i].id === id) return nodes[i];
    return null;
  }
  /* ── 步骤4：深度带标记；步骤5：内容绑定 ─────────────── */
  function markBands(nodes, edges, p, finalBoss) {
    var h = p.grid.h, br = bandRowsOf(p);
    nodes.forEach(function (n) {
      n.band = bandOfY(n.y, h, br);
      n.crossBandIn = false;
    });
    edges.forEach(function (e) {
      var fu = nodes[+e.from.slice(1)], tv = nodes[+e.to.slice(1)];
      e.crossBand = fu.band !== tv.band;
      if (e.crossBand) tv.crossBandIn = true;
    });
    finalBoss.type = 'finalBoss';
  }

  // dataProvider(ecoId, band) → { enemyPool, elitePool, bossPool, eventPool } | null
  // 缺省（浏览器调试页无数据时）：只落结构，pools 置 null、binding.pending=true，不做空池断言
  // T58：绑定表优先（64 格全覆盖）；缺格回落「同带母本生态」再走 provider 链，每次回落计数（验收应为 0）
  function resolveBinding(nodes, p, provider, stat) {
    var homeOf = {}; ECOS.forEach(function (e) { homeOf[e.id] = e.homeBand; });
    var ecoHomeAt = function (band) {
      var hit = ECOS.filter(function (e) { return e.homeBand === band; });
      return hit.length ? hit[0].id : null;
    };
    var tiers = p.binding.shopTierByBand;
    var T = loadBindings();
    nodes.forEach(function (n) {
      var pools = null, source = null;
      // 1 绑定表精确格
      if (T && T.eco[n.eco] && T.eco[n.eco].bands[String(n.band)]) {
        var cell = T.eco[n.eco].bands[String(n.band)];
        if ((cell.enemy || []).length && (cell.event || []).length) {
          pools = {
            enemyPool: cell.enemy.slice(), elitePool: cell.elite.slice(),
            bossPool: cell.boss.slice(), eventPool: cell.event.slice(),
            mods: cell._meta && cell._meta.mods ? { hpMul: cell._meta.mods.hpMul, atkMul: cell._meta.mods.atkMul } : null
          };
          source = 'table';
        }
      }
      // 2 回落：同带母本生态格（记兜底）
      if (!pools && T && n.band >= 1) {
        var homeId = ecoHomeAt(n.band);
        if (homeId && T.eco[homeId] && T.eco[homeId].bands[String(n.band)]) {
          var cell2 = T.eco[homeId].bands[String(n.band)];
          pools = {
            enemyPool: cell2.enemy.slice(), elitePool: cell2.elite.slice(),
            bossPool: cell2.boss.slice(), eventPool: cell2.event.slice(),
            mods: cell2._meta && cell2._meta.mods ? { hpMul: cell2._meta.mods.hpMul, atkMul: cell2._meta.mods.atkMul } : null
          };
          source = 'fallback';
          if (stat) stat.bindingFallbacks += 1;
        }
      }
      // 3 provider 链（旧回退）
      if (!pools && provider) {
        var chain = [
          [n.eco, n.band],
          [ecoHomeAt(n.band), n.band],
          [n.eco, homeOf[n.eco]]
        ].filter(function (c) { return c[0] !== null; });
        for (var i = 0; i < chain.length; i++) {
          pools = provider(chain[i][0], chain[i][1]);
          if (pools && (pools.enemyPool.length || pools.eventPool.length)) { source = 'chain'; break; }
          pools = null;
        }
        if (pools && stat) stat.bindingFallbacks += 1;
        if (!pools) throw GenError('binding.empty', n.eco + '@b' + n.band);
      }
      var tier = n.band <= tiers.lo ? 1 : (n.band <= tiers.mid ? 2 : 3);
      n.binding = pools
        ? { enemyPool: pools.enemyPool, elitePool: pools.elitePool, bossPool: pools.bossPool,
            eventPool: pools.eventPool, shopTier: tier, mods: pools.mods || null, source: source }
        : { enemyPool: null, elitePool: null, bossPool: null, eventPool: null,
            shopTier: tier, pending: true };
    });
  }

  /* ── 不变量校验（T54 §3 全表 I1–I12）────────────────── */
  function validate(region) {
    var errors = [];
    var p = region.params, w = p.grid.w, h = p.grid.h, br = region.bandRows;
    var byId = {}, cellMap = {};
    region.nodes.forEach(function (n) {
      byId[n.id] = n; cellMap[n.x + ',' + n.y] = n;
      n._out = []; n._in = [];
    });
    region.edges.forEach(function (e) {
      var u = byId[e.from], v = byId[e.to];
      if (!u || !v) { errors.push('E: 边引用不存在的节点 ' + e.from + '->' + e.to); return; }
      u._out.push(v); v._in.push(u);
    });
    function err(id, msg) { errors.push(id + ': ' + msg); }

    // I1 节点不共格；start/finalBoss 各恰 1
    if (Object.keys(cellMap).length !== region.nodes.length) err('I1', '节点共格');
    var starts = region.nodes.filter(function (n) { return n.id === region.startId; });
    var fbs = region.nodes.filter(function (n) { return n.type === 'finalBoss'; });
    if (starts.length !== 1) err('I1', '起点不唯一');
    if (fbs.length !== 1) err('I6', 'finalBoss 数量=' + fbs.length);

    // I2 100% 可达（DFS）
    if (starts.length === 1) {
      var seen = {}; var stack = [region.startId]; seen[region.startId] = true;
      while (stack.length) {
        var cur = byId[stack.pop()];
        cur._out.forEach(function (v) { if (!seen[v.id]) { seen[v.id] = true; stack.push(v.id); } });
      }
      var miss = region.nodes.filter(function (n) { return !seen[n.id]; });
      if (miss.length) err('I2', '不可达节点 ' + miss.length + ' 个（如 ' + miss[0].id + '）');
    }

    // I3 出边下限
    region.nodes.forEach(function (n) {
      if (n.type !== 'finalBoss' && n._out.length < 1) err('I3', n.id + ' 无出边');
    });

    // I4 无环（Kahn 拓扑）
    var deg = {}; region.nodes.forEach(function (n) { deg[n.id] = n._in.length; });
    var queue = region.nodes.filter(function (n) { return deg[n.id] === 0; }).map(function (n) { return n.id; });
    var done = 0;
    while (queue.length) {
      var id = queue.pop(); done++;
      byId[id]._out.forEach(function (v) { if (--deg[v.id] === 0) queue.push(v.id); });
    }
    if (done !== region.nodes.length) err('I4', '存在环');

    // I5 y 严格单调向下
    region.edges.forEach(function (e) {
      var u = byId[e.from], v = byId[e.to];
      if (v.y <= u.y) err('I5', e.from + '->' + e.to + ' 未向下');
      if (e.dy !== v.y - u.y || e.dx !== v.x - u.x) err('E', e.from + '->' + e.to + ' 位移字段不符');
      if (e.len !== Math.max(Math.abs(e.dx), e.dy)) err('E', e.from + '->' + e.to + ' len 字段不符');
      if (e.dy < 1) err('I5', e.from + '->' + e.to + ' dy<1');
      var expect = Math.round(Math.atan2(Math.abs(e.dx), e.dy) * 180 / Math.PI * 10) / 10;
      if (Math.abs(e.angle - expect) > 0.05) err('E', e.from + '->' + e.to + ' angle 字段不符');
    });

    // I6 finalBoss 唯一、band8 最底行
    fbs.forEach(function (n) {
      if (n.band !== 8 || n.y !== h - 1) err('I6', 'finalBoss 位置错误 y=' + n.y);
    });

    // I7 每带节点数 ≥ 配额
    var q = effectiveQuota(p);
    for (var b = 1; b <= 8; b++) {
      var cnt = region.nodes.filter(function (n) { return n.band === b; }).length;
      var need = 0; Object.keys(q[b]).forEach(function (t) { need += q[b][t]; });
      if (cnt < need) err('I7', 'band' + b + ' 节点 ' + cnt + '<配额' + need);
    }

    // I8 同带同类型最小曼哈顿距离（T74: 按 band|type 分桶，不再全节点两两）
    var D = p.node.minSameTypeDist;
    var typeBuckets = {};
    region.nodes.forEach(function (n) {
      var kb = n.band + '|' + n.type;
      (typeBuckets[kb] = typeBuckets[kb] || []).push(n);
    });
    Object.keys(typeBuckets).forEach(function (kb) {
      var arr = typeBuckets[kb];
      for (var i = 0; i < arr.length; i++) for (var j = i + 1; j < arr.length; j++) {
        var a = arr[i], c = arr[j];
        if (Math.abs(a.x - c.x) + Math.abs(a.y - c.y) < D)
          err('I8', a.id + '~' + c.id + '（' + a.type + '@b' + a.band + '）距离 < ' + D);
      }
    });

    // I9 每个带边界可跨越；crossBand 必为相邻带
    region.edges.forEach(function (e) {
      var u = byId[e.from], v = byId[e.to];
      if (e.crossBand !== (u.band !== v.band)) err('E', e.from + '->' + e.to + ' crossBand 标记不符');
      if (e.crossBand && v.band !== u.band + 1) err('I9', '跨带边跳带 ' + u.band + '->' + v.band);
    });
    for (var bb = 1; bb <= 7; bb++) {
      var has = region.edges.some(function (e) {
        return byId[e.from].band === bb && byId[e.to].band === bb + 1;
      });
      if (!has) err('I9', 'band' + bb + '→' + (bb + 1) + ' 无跨带边');
    }

    // I10 无交叉边、不穿节点
    var interiorUsed = {}, edgeInteriors = [];
    region.edges.forEach(function (e) {
      var u = byId[e.from], v = byId[e.to];
      var cells = lineCells(u.x, u.y, v.x, v.y).slice(1, -1);
      cells.forEach(function (c) {
        var k = c[0] + ',' + c[1];
        if (cellMap[k]) err('I10', e.from + '->' + e.to + ' 穿过节点 ' + cellMap[k].id);
        if (interiorUsed[k]) err('I10', '边交叉 @' + k);
        interiorUsed[k] = true;
      });
      edgeInteriors.push(cells);
    });

    // I11 度上限
    region.nodes.forEach(function (n) {
      if (n._out.length > p.edge.outDegMax) err('I11', n.id + ' 出度 ' + n._out.length);
      var inCap = (n.type === 'finalBoss') ? p.node.fbInDegCap : p.node.maxInDeg;
      if (n._in.length > inCap) err('I11', n.id + ' 入度 ' + n._in.length);
    });

    // I12 生态约束
    var counts = {};
    region.ecoOf.forEach(function (e) { counts[e] = (counts[e] || 0) + 1; });
    ECOS.forEach(function (e) {
      if (!counts[e.id]) { err('I12', '生态缺失 ' + e.id); return; }
      var comps = componentsOf(region.ecoOf, w, h, e.id);
      if (comps.length > p.ecoGrowth.maxComponents)
        err('I12', e.id + ' 分量数 ' + comps.length);
      comps.forEach(function (comp) {
        if (comp.length < p.ecoGrowth.minPatchArea) err('I12', e.id + ' 块面积 ' + comp.length);
      });
    });

    // I17 纵向间距（T73；T74 放宽至 ≥1）：同带同列两节点 |dy| ≥ spacing（T74: 按带|列分桶查）
    var colBuckets = {};
    region.nodes.forEach(function (n) {
      var kc = n.band + '|' + n.x;
      (colBuckets[kc] = colBuckets[kc] || []).push(n);
    });
    Object.keys(colBuckets).forEach(function (kc) {
      var arr = colBuckets[kc];
      for (var i = 0; i < arr.length; i++) for (var j = i + 1; j < arr.length; j++) {
        var na = arr[i], nc = arr[j];
        if (Math.abs(na.y - nc.y) < p.node.verticalSpacing)
          err('I17', na.id + '~' + nc.id + ' 同列纵向间距 ' + Math.abs(na.y - nc.y) + ' < ' + p.node.verticalSpacing);
      }
    });

    // 模型一致性：band / eco 冗余字段
    region.nodes.forEach(function (n) {
      if (n.band !== bandOfY(n.y, h, br)) err('E', n.id + ' band 字段不符');
      if (n.eco !== region.ecoOf[n.y * w + n.x]) err('E', n.id + ' eco 字段不符');
    });
    region.edges.forEach(function (e) {
      var v = byId[e.to];
      if (e.crossBand && !v.crossBandIn) err('E', e.to + ' crossBandIn 标记缺失');
      if (!e.crossBand && v.crossBandIn && !region.edges.some(function (e2) {
        return e2.to === e.to && e2.crossBand; })) err('E', e.to + ' crossBandIn 标记多余');
    });

    region.nodes.forEach(function (n) { delete n._out; delete n._in; });
    return { ok: errors.length === 0, errors: errors };
  }

  /* ── 可见性（T54 §4；T56 消费）────────────────────── */
  // visible = visited ∪ 边邻居 depth 跳（默认 1）；未可见节点不进返回值——数据层裁剪
  function pruneForFrontend(region, visitedIds, depth) {
    var d = depth || 1;
    var byId = {};
    region.nodes.forEach(function (n) { byId[n.id] = n; });
    var vis = {};
    Object.keys(visitedIds).forEach(function (id) { vis[id] = true; });
    var frontier = Object.keys(visitedIds).map(function (id) { return byId[id]; });
    for (var step = 0; step < d; step++) {
      var next = [];
      frontier.forEach(function (n) {
        region.edges.forEach(function (e) {
          var other = null;
          if (e.from === n.id) other = byId[e.to];
          else if (e.to === n.id) other = byId[e.from];
          if (other && !vis[other.id]) { vis[other.id] = true; next.push(other); }
        });
      });
      frontier = next;
    }
    var nodes = region.nodes.filter(function (n) { return vis[n.id]; })
      .map(function (n) { return Object.assign({}, n); });
    var edges = region.edges.filter(function (e) { return vis[e.from] && vis[e.to]; })
      .map(function (e) { return Object.assign({}, e); });
    return { nodes: nodes, edges: edges };
  }

  /* ── 统计辅助（测试与调试页用）─────────────────────── */
  function bfsMaxDepth(region) {
    var byId = {};
    region.nodes.forEach(function (n) { byId[n.id] = n; n._d = -1; });
    var start = byId[region.startId]; start._d = 0;
    var queue = [start], max = 0;
    while (queue.length) {
      var u = queue.shift();
      region.edges.forEach(function (e) {
        if (e.from !== u.id) return;
        var v = byId[e.to];
        if (v._d < 0) { v._d = u._d + 1; max = Math.max(max, v._d); queue.push(v); }
      });
    }
    var fbDepth = byId[region.finalBossId]._d;
    region.nodes.forEach(function (n) { delete n._d; });
    return { max: max, finalBoss: fbDepth };
  }

  /* ── 主入口：generate(seed, params[, dataProvider]) → Region ── */
  function generate(seed, params, dataProvider) {
    var p = resolveParams(params);
    var failures = {};
    var stat = { bindingFallbacks: 0 };
    for (var attempt = 1; attempt <= p.retry.max; attempt++) {
      var seedUsed = (seed >>> 0) * 1000003 + attempt;
      var rng = makeRng(seedUsed);
      try {
        var w = p.grid.w, h = p.grid.h, br = bandRowsOf(p);
        var W = buildWeightTable(p);
        var ecoOf = growEcos(rng, p, W);                     // 步骤1
        var grown = growDAG(rng, ecoOf, p);                  // 步骤2+3（生长式合并）
        markBands(grown.nodes, grown.edges, p, grown.finalBoss); // 步骤4
        resolveBinding(grown.nodes, p, dataProvider, stat);  // 步骤5（T58 绑定表优先）
        var weight = ecoOf.map(function (e, i) { return W[e][bandOfY((i / w) | 0, h, br)]; });
        var region = {
          w: w, h: h, bandRows: br,
          params: p, seedUsed: seedUsed, attempts: attempt, bindingFallbacks: stat.bindingFallbacks,
          ecoOf: ecoOf, weight: weight,
          nodes: grown.nodes, edges: grown.edges,
          startId: grown.start.id, finalBossId: grown.finalBoss.id
        };
        var v = validate(region);
        if (!v.ok) throw GenError('validate', v.errors[0]);
        return region;
      } catch (err) {
        if (err && err.isGenError) {
          failures[err.reason] = (failures[err.reason] || 0) + 1;
        } else { throw err; }
      }
    }
    var tally = Object.keys(failures).map(function (k) { return k + '×' + failures[k]; }).join(', ');
    throw new Error('generate: ' + p.retry.max + ' 次尝试全部失败 → ' + tally);
  }

  function resolveParams(overrides) {
    var p = JSON.parse(JSON.stringify(DEFAULTS));
    if (overrides) Object.keys(overrides).forEach(function (k) {
      if (k === 'quotaScale') { p.quotaScale = overrides[k]; return; }
      if (typeof overrides[k] === 'object' && !Array.isArray(overrides[k])) {
        Object.keys(overrides[k]).forEach(function (k2) { p[k][k2] = overrides[k][k2]; });
      } else p[k] = overrides[k];
    });
    return p;
  }

  return {
    generate: generate,
    validate: validate,
    pruneForFrontend: pruneForFrontend,
    bfsMaxDepth: bfsMaxDepth,
    effectiveQuota: effectiveQuota,
    makeRng: makeRng,
    bandOfY: bandOfY,
    DEFAULTS: DEFAULTS,
    ECOS: ECOS,
    lineCells: lineCells,
    _debug: { growEcos: growEcos, growDAG: growDAG, buildWeightTable: buildWeightTable, markBands: markBands, resolveParams: resolveParams }
  };
});
