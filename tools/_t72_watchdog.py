# -*- coding: utf-8 -*-
"""T72 调试哨兵：在 growEcos 的每个变异点后挂 assertAlive（生态灭门立刻变可捕错误）。
永久保留——灭门 → GenError → 换 seed 重试，不静默。"""
import io

p = 'tools/mapgen.js'
s = io.open(p, encoding='utf-8').read()

if 'assertAlive' in s:
    print('watchdog 已存在')
else:
    o0 = '    function mergeSmallAndCap() {'
    n0 = """    function assertAlive(tag) {
      var c = {};
      for (var i = 0; i < n; i++) c[ecoOf[i]] = (c[ecoOf[i]] || 0) + 1;
      ECOS.forEach(function (e) { if (!c[e.id]) throw GenError('extinct@' + tag + ':' + e.id); });
    }
    function mergeSmallAndCap() {"""
    assert o0 in s, 'o0'
    s = s.replace(o0, n0)

    o1 = """        if (worstIsLast) {
          if (!reviveLast(worst.comp, worstEco)) throw GenError('eco.merge.noNeighbor', worstEco);
          changed = true;
        } else {
          if (!relabelTo(worst.comp, null)) throw GenError('eco.merge.noNeighbor');
          changed = true;
        }"""
    n1 = """        if (worstIsLast) {
          if (!reviveLast(worst.comp, worstEco)) throw GenError('eco.merge.noNeighbor', worstEco);
          assertAlive('revive'); changed = true;
        } else {
          if (!relabelTo(worst.comp, null)) throw GenError('eco.merge.noNeighbor');
          assertAlive('relabel'); changed = true;
        }"""
    assert o1 in s, 'o1'
    s = s.replace(o1, n1)

    o2 = """            for (var yy2 = r0; yy2 < r0 + 2; yy2++)
              for (var xx2 = x0; xx2 < x0 + 6; xx2++) ecoOf[yy2 * w + xx2] = E;
            placed = true; changed = true;
          }"""
    n2 = """            for (var yy2 = r0; yy2 < r0 + 2; yy2++)
              for (var xx2 = x0; xx2 < x0 + 6; xx2++) ecoOf[yy2 * w + xx2] = E;
            placed = true; changed = true;
            assertAlive('tongue');
          }"""
    assert o2 in s, 'o2'
    s = s.replace(o2, n2)

    o3 = "        cut.forEach(function (c) { ecoOf[c] = second; });\n        changed = true;"
    n3 = "        cut.forEach(function (c) { ecoOf[c] = second; });\n        assertAlive('trim'); changed = true;"
    assert o3 in s, 'o3'
    s = s.replace(o3, n3)


    io.open(p, 'w', encoding='utf-8').write(s)
    print('watchdog installed:', s.count('assertAlive('), 'calls')
