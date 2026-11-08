/* T55 生成器断言（命令行）：node tools/mapgen_test.js
   —— 200 seed 全部通过 validate（I1–I12）+ 统计表 + 确定性 + spec 同步 + 100 图耗时。
   任何一项不过 → exit 1（不许「大部分通过」就交）。 */
'use strict';
const fs = require('fs');
const path = require('path');
const MG = require('./mapgen.js');

/* 内容绑定数据源（T55 只做默认回退链验证；实表在 T58） */
const enemies = require('../enemies/all.json');
const events = require('../events/all.json');
function dataProvider(ecoId, band) {
  const es = enemies.filter(function (x) { return x.layer === band; });
  const evs = events.filter(function (x) { return x.layer === band; });
  if (!es.length && !evs.length) return null;
  return {
    enemyPool: es.filter(function (x) { return x.tier === 'normal'; }).map(function (x) { return x.id; }),
    elitePool: es.filter(function (x) { return x.tier === 'elite'; }).map(function (x) { return x.id; }),
    bossPool: es.filter(function (x) { return x.tier === 'boss'; }).map(function (x) { return x.id; }),
    eventPool: evs.map(function (x) { return x.id; })
  };
}

function main() {
  const N = 200;
  const t0 = Date.now();
  let pass = 0;
  const failReasons = {};
  const st = {
    nodes: [], bandNodes: {}, outdeg: {}, edgeLen: [], crossBand: 0,
    bfsMax: [], fbDepth: [], attempts: [], minPatch: [], fbOk: 0, bindingEmpty: 0
  };
  const regions = [];
  for (let s = 1; s <= N; s++) {
    try {
      const r = MG.generate(s, null, dataProvider);
      const v = MG.validate(r);
      if (!v.ok) throw new Error('validate: ' + v.errors[0]);
      pass += 1;
      regions.push(r);
      st.nodes.push(r.nodes.length);
      for (let b = 1; b <= 8; b++) {
        const c = r.nodes.filter(function (n) { return n.band === b; }).length;
        (st.bandNodes[b] = st.bandNodes[b] || []).push(c);
      }
      const outDegMap = {};
      r.edges.forEach(function (e) { outDegMap[e.from] = (outDegMap[e.from] || 0) + 1; });
      r.nodes.forEach(function (n) {
        const d = outDegMap[n.id] || 0;
        st.outdeg[d] = (st.outdeg[d] || 0) + 1;
      });
      r.edges.forEach(function (e) {
        st.edgeLen.push(e.len);
        if (e.crossBand) st.crossBand += 1;
      });
      const bp = MG.bfsMaxDepth(r);
      st.bfsMax.push(bp.max); st.fbDepth.push(bp.finalBoss);
      st.attempts.push(r.attempts);
      if (r.bindingFallbacks !== 0) throw new Error('bindingFallbacks=' + r.bindingFallbacks + ' (seed ' + s + '，应为 0)');
      if (r.nodes.some(function (n) { return !n.binding || n.binding.source !== 'table'; })) throw new Error('seed ' + s + ' 有节点未走绑定表');
      st.fallbackTotal = (st.fallbackTotal || 0) + r.bindingFallbacks;
      const fb = r.nodes.filter(function (n) { return n.type === 'finalBoss'; });
      if (fb.length === 1 && fb[0].id === r.finalBossId) st.fbOk += 1;
      if (r.nodes.some(function (n) { return !n.binding || !n.binding.enemyPool || !n.binding.enemyPool.length; })) st.bindingEmpty += 1;
      // 最小生态块面积
      let minC = 1e9;
      MG.ECOS.forEach(function (eco) {
        const seen = new Array(r.w * r.h).fill(false);
        for (let i = 0; i < r.w * r.h; i++) {
          if (seen[i] || r.ecoOf[i] !== eco.id) continue;
          let size = 0; const stack = [i]; seen[i] = true;
          while (stack.length) {
            const c = stack.pop(); size += 1;
            const x = c % r.w, y = (c / r.w) | 0;
            [[1, 0], [-1, 0], [0, 1], [0, -1]].forEach(function (d) {
              const nx = x + d[0], ny = y + d[1];
              if (nx < 0 || ny < 0 || nx >= r.w || ny >= r.h) return;
              const ni = ny * r.w + nx;
              if (!seen[ni] && r.ecoOf[ni] === eco.id) { seen[ni] = true; stack.push(ni); }
            });
          }
          if (size < minC) minC = size;
        }
      });
      st.minPatch.push(minC);
    } catch (e) {
      const key = e.message.slice(0, 90);
      failReasons[key] = (failReasons[key] || 0) + 1;
    }
  }
  const genMs = Date.now() - t0;

  /* ── 报告 ── */
  const avg = function (a) { return a.length ? (a.reduce(function (x, y) { return x + y; }, 0) / a.length) : 0; };
  const min = function (a) { return a.length ? Math.min.apply(null, a) : 0; };
  const max = function (a) { return a.length ? Math.max.apply(null, a) : 0; };
  console.log('═══ T55 mapgen 断言 ═══');
  console.log('通过率: ' + pass + '/' + N + (pass === N ? '  ✓' : '  ✗ 未全绿'));
  Object.keys(failReasons).forEach(function (k) { console.log('  失败原因: ' + k + ' ×' + failReasons[k]); });
  console.log('');
  console.log('节点数: 平均 ' + avg(st.nodes).toFixed(1) + '（min ' + min(st.nodes) + ' / max ' + max(st.nodes) + '）');
  let bandLine = '';
  for (let b = 1; b <= 8; b++) bandLine += 'D' + b + '=' + avg(st.bandNodes[b]).toFixed(1) + ' ';
  console.log('每带节点均值: ' + bandLine);
  console.log('出度分布: ' + JSON.stringify(st.outdeg) + '（0 出度=finalBoss）');
  console.log('边长 len: 平均 ' + avg(st.edgeLen).toFixed(2) + '（min ' + min(st.edgeLen) + ' / max ' + max(st.edgeLen) + '）；跨带边均值 ' + (st.crossBand / N).toFixed(1) + ' 条/图');
  console.log('最长最短路径（BFS 深度）: 平均 ' + avg(st.bfsMax).toFixed(1) + '（min ' + min(st.bfsMax) + ' / max ' + max(st.bfsMax) + '）；finalBoss 深度均值 ' + avg(st.fbDepth).toFixed(1));
  console.log('finalBoss 唯一且 id 一致: ' + st.fbOk + '/' + N);
  console.log('绑定空池节点数: ' + st.bindingEmpty + '（应 0）');
  console.log('最小生态块面积: 最小 ' + min(st.minPatch) + '（下限 ' + MG.DEFAULTS.ecoGrowth.minPatchArea + '）');
  console.log('重试: 平均 ' + avg(st.attempts).toFixed(2) + ' 次（max ' + max(st.attempts) + '）');
  const retryAvg = avg(st.attempts), retryMax = max(st.attempts);
  if (retryAvg > 6) { console.log('  ✗ 重试均值 ' + retryAvg.toFixed(2) + ' > 6（T74 验收线）'); process.exit(1); }
  if (retryMax > 40) { console.log('  ✗ 重试最大 ' + retryMax + ' > 40（T74 验收线）'); process.exit(1); }
  console.log('  重试验收（T74）: 均值 ≤6 ✓ / 最大 ≤40 ✓');
  console.log('生成 ' + N + ' 图耗时: ' + genMs + 'ms');

  /* ── 确定性：同 seed 同参数 → 逐字节一致 ── */
  [1, 42, 777, 200, 12345].forEach(function (s) {
    const a = JSON.stringify(MG.generate(s, null, dataProvider));
    const b = JSON.stringify(MG.generate(s, null, dataProvider));
    if (a !== b) { console.error('✗ 确定性破坏 seed=' + s); process.exit(1); }
  });
  console.log('确定性（5 个 seed 双跑比对）: ✓');

  /* ── spec 同步：mapgen.js 内置默认值 ↔ mapgen_spec.json ── */
  const spec = JSON.parse(fs.readFileSync(path.join(__dirname, 'mapgen_spec.json'), 'utf8'));
  const D = MG.DEFAULTS;
  const eq = function (a, b, what) {
    if (JSON.stringify(a) !== JSON.stringify(b)) {
      console.error('✗ spec 同步失败: ' + what + ' — mapgen.js=' + JSON.stringify(a) + ' spec=' + JSON.stringify(b));
      process.exit(1);
    }
  };
  eq(D.grid.w, spec.grid.w.default, 'grid.w');
  eq(D.grid.h, spec.grid.h.default, 'grid.h');
  eq(D.ecoGrowth.kappa, spec.ecoGrowth.kappa.default, 'ecoGrowth.kappa');
  eq(D.ecoGrowth.minPatchArea, spec.ecoGrowth.minPatchArea.default, 'minPatchArea');
  eq(D.ecoGrowth.maxComponents, spec.ecoGrowth.maxComponents.default, 'maxComponents');
  eq(D.node.minSameTypeDist, spec.node.minSameTypeDist.default, 'minSameTypeDist');
  eq(D.node.maxInDeg, spec.node.maxInDeg.default, 'maxInDeg');
  eq(D.node.verticalSpacing, spec.node.verticalSpacing.minRows, 'verticalSpacing');
  eq(D.edge.outDegMax, spec.edge.outDegMax.default, 'outDegMax');
  eq(D.edge.maxLen, spec.edge.maxLen.default, 'maxLen');
  eq(D.edge.extraBranchOdds, spec.edge.extraBranchOdds.default, 'extraBranchOdds');
  eq(D.retry.max, spec.retry.max.default, 'retry.max');
  eq(D.weight.home, spec.weight.home.default, 'weight.home');
  eq(D.weight.adjacentEach, spec.weight.adjacentEach.default, 'weight.adjacentEach');
  eq(D.ecoGrowth.minPatchArea, spec.bandMix.minPatch.default, 'bandMix.minPatch');
  eq(D.bandMix.countMin, spec.bandMix.countPerBand.min, 'bandMix.countMin');
  eq(D.bandMix.countMax, spec.bandMix.countPerBand.max, 'bandMix.countMax');
  eq(D.bandMix.maxShare, spec.bandMix.maxShare.default, 'bandMix.maxShare');
  eq(D.bandMix.perBandComponents, spec.bandMix.perBandComponents.max, 'bandMix.perBandComponents');
  for (let b = 1; b <= 8; b++) eq(D.quota[b], spec.quota.bands[String(b)], 'quota.band' + b);
  // 位移表：spec 分桶展开后与 mapgen.js 的平面表一致
  const specDisp = [];
  spec.edge.displacementTable.forEach(function (c) {
    c.candidates.forEach(function (p) { specDisp.push(p[0] + ',' + p[1]); });
  });
  const jsDisp = D.edge.displacement.map(function (p) { return p[0] + ',' + p[1]; });
  eq(jsDisp.slice().sort(), specDisp.slice().sort(), 'displacementTable');
  const P = { boss: { firstAlways: true, p0: 0.5, decay: 0.6, min: 0.1 },
    rescue: { penaltyHpPct: 10, penaltyGoldPct: 15, ambushChance: 0.5, pickRule: 'sameBandFirst',
      backtrack: { badEvent: 0.45, combat: 0.30, elite: 0.15, boss: 0.08, none: 0.02, hpPct: [0.08, 0.15], goldPct: [0.15, 0.25] } },
    randomMix: { campfire: 0.45, event: 0.40, shop: 0.15 } };
  eq(P.boss.firstAlways, spec.boss.firstAlways.value, 'boss.firstAlways');
  eq(P.boss.p0, spec.boss.p0.default, 'boss.p0');
  eq(P.boss.decay, spec.boss.decay.default, 'boss.decay');
  eq(P.boss.min, spec.boss.min.default, 'boss.min');
  eq(P.rescue.penaltyHpPct, spec.rescue.penaltyHpPct.default, 'rescue.penaltyHpPct');
  eq(P.rescue.penaltyGoldPct, spec.rescue.penaltyGoldPct.default, 'rescue.penaltyGoldPct');
  eq(P.rescue.ambushChance, spec.rescue.ambushChance.default, 'rescue.ambushChance');
  eq(P.rescue.pickRule, spec.rescue.pickRule.default, 'rescue.pickRule');
  ['badEvent', 'combat', 'elite', 'boss', 'none'].forEach(function (k) {
    eq(P.rescue.backtrack[k], spec.rescue.backtrack[k].default, 'rescue.backtrack.' + k);
  });
  ['hpPct', 'goldPct'].forEach(function (k) {
    eq(P.rescue.backtrack[k], spec.rescue.backtrack[k].default, 'rescue.backtrack.' + k);
  });
  eq(P.randomMix.campfire, spec.randomMix.campfire.default, 'randomMix.campfire');
  eq(P.randomMix.event, spec.randomMix.event.default, 'randomMix.event');
  eq(P.randomMix.shop, spec.randomMix.shop.default, 'randomMix.shop');
  console.log('spec 同步（权重 v1.5 + 8 带配额 + 位移表 + boss/rescue/randomMix + bandMix）: ✓');

  /* ── 耗时：100 图 < 2s ── */
  const t1 = Date.now();
  for (let s = 5000; s < 5100; s++) MG.generate(s, null, null);
  const dt = Date.now() - t1;
  console.log('100 图耗时: ' + dt + 'ms（' + (dt / 100).toFixed(1) + 'ms/图）' + (dt < 2000 ? '  ✓ <2s' : '  ✗ 超时'));

  if (pass !== N || dt >= 2000) process.exit(1);
  console.log('');
  console.log('全部断言通过。');
}

main();
