# -*- coding: utf-8 -*-
"""T72 补丁 v2：把 _t72_patch.py 的 C 段（newG）替换为带三道保护的版本：
灭门复活（最后一块不并入、从邻居圈地补足）/ 份额修剪（>60% 切 12 格给次生态）/
单生态补块（带内只有 1 种生态时从邻带引 12 格）。执行一次即可。"""
import io, sys

p = 'tools/_t72_patch.py'
s = io.open(p, encoding='utf-8').read()

if '灭门复活' in s:
    print('C 段已是 v2，跳过')
    sys.exit(0)

start = s.index("newG = \"\"\"")
end = s.index('"""', start + 12) + 3

newG = 'newG = """  function growEcos(rng, p, W) {\n' + '''
    var w = p.grid.w, h = p.grid.h, br = bandRowsOf(p), n = w * h;
    var ecoOf = new Array(n).fill(null);
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
      var cx = cell % w, cy = (cell / w) | 0;
      DIRS4.forEach(function (d) {
        var nx = cx + d[0], ny = cy + d[1];
        if (nx < 0 || ny < 0 || nx >= w || ny >= h) return;
        var ni = ny * w + nx;
        if (ecoOf[ni] !== null) return;
        var cost = (1 - W[eco][bandOfY(ny, h, br)]) * stepK + rng() * noiseK;
        pq.push(cost, [ni, eco]);
      });
    }
    var bandOfCell = function (c) { return bandOfY((c / w) | 0, h, br); };
    function compsOf(pred) {
      var seen = new Array(n).fill(false), out = [];
      for (var i = 0; i < n; i++) {
        if (seen[i] || !pred(i, ecoOf[i])) continue;
        var comp = [], st = [i]; seen[i] = true;
        while (st.length) {
          var c = st.pop(); comp.push(c);
          var x = c % w, y = (c / w) | 0;
          DIRS4.forEach(function (d) {
            var nx = x + d[0], ny = y + d[1];
            if (nx < 0 || ny < 0 || nx >= w || ny >= h) return;
            var ni = ny * w + nx;
            if (!seen[ni] && pred(ni, ecoOf[ni])) { seen[ni] = true; st.push(ni); }
          });
        }
        out.push(comp);
      }
      return out;
    }
    function borderOf(comp, exclude) {
      var border = {};
      comp.forEach(function (c) {
        var x = c % w, y = (c / w) | 0;
        DIRS4.forEach(function (d) {
          var nx = x + d[0], ny = y + d[1];
          if (nx < 0 || ny < 0 || nx >= w || ny >= h) return;
          var ni = ny * w + nx, o = ecoOf[ni];
          if (o && o !== exclude && comp.indexOf(ni) < 0) border[o] = (border[o] || 0) + 1;
        });
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
    function mergeSmallAndCap() {   // 全局碎片(<minPatch) + 每带连通块上限 + 全局分量上限
      var changed = false, guard = 0;
      for (;;) {
        if (++guard > 800) throw GenError('eco.merge.loop');
        var worst = null, worstIsLast = false, worstEco = null;
        ECOS.forEach(function (e) {
          var comps = compsOf(function (i, o) { return o === e.id; });
          comps.forEach(function (comp) {
            if (comp.length < p.ecoGrowth.minPatchArea && (!worst || comp.length < worst.size)) {
              worst = { comp: comp, size: comp.length };
              worstIsLast = comps.length === 1; worstEco = e.id;
            }
          });
          if (comps.length > p.ecoGrowth.maxComponents) {
            comps.sort(function (a, c) { return a.length - c.length; });
            var comp = comps[0];
            if (!worst || comp.length < worst.size) {
              worst = { comp: comp, size: comp.length };
              worstIsLast = false; worstEco = e.id;
            }
          }
        });
        for (var e2 = 0; e2 < ECOS.length; e2++) {
          (function (e) {
            for (var b2 = 1; b2 <= 8; b2++) {
              var comps = compsOf(function (i, o) { return o === e && bandOfCell(i) === b2; });
              if (comps.length > p.bandMix.perBandComponents) {
                comps.sort(function (a, c) { return a.length - c.length; });
                comps.slice(0, comps.length - p.bandMix.perBandComponents).forEach(function (comp) {
                  if (!worst || comp.length < worst.size) { worst = { comp: comp, size: comp.length }; worstIsLast = false; worstEco = e; }
                });
              }
            }
          })(ECOS[e2].id);
        }
        if (!worst) return changed;
        if (worstIsLast) {
          if (!reviveLast(worst.comp, worstEco)) throw GenError('eco.merge.noNeighbor', worstEco);
          changed = true;
        } else {
          if (!relabelTo(worst.comp, null)) throw GenError('eco.merge.noNeighbor');
          changed = true;
        }
      }
    }
    function fixTonguesAndCount() { // 相邻带交集 ≥1 + 带内单生态补块（2×6=12 格补丁）
      var changed = false;
      for (var b = 1; b <= 8; b++) {
        var cnt = {}, tot = 0;
        for (var i = 0; i < n; i++) if (bandOfCell(i) === b) { cnt[ecoOf[i]] = (cnt[ecoOf[i]] || 0) + 1; tot++; }
        var ecos = Object.keys(cnt);
        if (ecos.length >= p.bandMix.countMin) {
          if (b <= 7) {
            var setB = {};
            for (var i2 = 0; i2 < n; i2++) if (bandOfCell(i2) === b + 1) setB[ecoOf[i2]] = true;
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
      var changed = false;
      for (var b = 1; b <= 8; b++) {
        var cnt = {}, tot = 0, cells = {};
        for (var i = 0; i < n; i++) if (bandOfCell(i) === b) {
          var o = ecoOf[i]; cnt[o] = (cnt[o] || 0) + 1; tot++;
          (cells[o] = cells[o] || []).push(i);
        }
        var ecos = Object.keys(cnt);
        if (ecos.length < 2) continue;
        ecos.sort(function (a, c) { return cnt[c] - cnt[a]; });
        var top = ecos[0];
        if (cnt[top] / tot <= p.bandMix.maxShare) continue;
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
        cut.forEach(function (c) { ecoOf[c] = second; });
        changed = true;
      }
      return changed;
    }
    var pass = 0;
    for (;;) {
      if (++pass > 10) throw GenError('eco.postprocess.loop');
      var c1 = mergeSmallAndCap();
      var c2 = fixTonguesAndCount();
      var c3 = shareTrim();
      if (!c1 && !c2 && !c3) break;
    }
    var counts = {};
    ecoOf.forEach(function (e) { counts[e] = (counts[e] || 0) + 1; });
    ECOS.forEach(function (e) { if (!counts[e.id]) throw GenError('eco.missing', e.id); });
    ECOS.forEach(function (e) {
      var comps = compsOf(function (i, o) { return o === e.id; });
      if (comps.length > p.ecoGrowth.maxComponents) throw GenError('eco.maxComponents', e.id);
      comps.forEach(function (comp) {
        if (comp.length < p.ecoGrowth.minPatchArea) throw GenError('eco.minPatch', e.id + '=' + comp.length);
      });
    });
    for (var b = 1; b <= 8; b++) {
      var cnt = {}, tot = 0;
      for (var i2 = 0; i2 < n; i2++) if (bandOfCell(i2) === b) { cnt[ecoOf[i2]] = (cnt[ecoOf[i2]] || 0) + 1; tot++; }
      var ecos = Object.keys(cnt);
      if (ecos.length < p.bandMix.countMin || ecos.length > p.bandMix.countMax)
        throw GenError('bandmix.count', 'b' + b + '=' + ecos.length);
      var maxShare = Math.max.apply(null, ecos.map(function (e) { return cnt[e] / tot; }));
      if (maxShare > p.bandMix.maxShare) throw GenError('bandmix.share', 'b' + b + '=' + maxShare.toFixed(2));
      ECOS.forEach(function (e) {
        if (!cnt[e.id]) return;
        var comps = compsOf(function (i, o) { return o === e.id && bandOfCell(i) === b; });
        if (comps.length > p.bandMix.perBandComponents)
          throw GenError('bandmix.comps', e.id + '@b' + b + '=' + comps.length);
      });
    }
    for (var bb = 1; bb <= 7; bb++) {
      var sa = {}, sb = {};
      for (var i3 = 0; i3 < n; i3++) {
        var bd3 = bandOfCell(i3);
        if (bd3 === bb) sa[ecoOf[i3]] = true; else if (bd3 === bb + 1) sb[ecoOf[i3]] = true;
      }
      if (!Object.keys(sa).some(function (e) { return sb[e]; }))
        throw GenError('bandmix.intersect', 'b' + bb);
    }
    return ecoOf;
  }
"""'''
s = s[:start] + newG + s[end:]
io.open(p, 'w', encoding='utf-8').write(s)
print('C 段替换为 v2')
