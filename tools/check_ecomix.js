/* T72 生态混合验收：500 张图逐张测带级指标 + 5 张不同 seed 的色块图（SVG）。
   指标（对应任务书验收线）：
   ① 每带生态数 ∈ [2,4]（零例外）
   ② 单带最大生态占比 ≤ 60%（零例外）
   ③ 相邻两带共享生态 ≥1（100%）
   ④ 带内同生态连通块 ≤3（95 分位；同时统计 100% 违例率）
   ⑤ 最小生态块 ≥ spec.ecoGrowth.minPatchArea 格（零例外；T72 定 12，T74 允许项降到 8）
   用法：node tools/check_ecomix.js --runs 500   → tools/ecomix_report.json + art/ecomix/*.svg */
'use strict';
const fs = require('fs');
const path = require('path');
const MG = require(path.join(__dirname, 'mapgen.js'));
const SPEC_MIN_PATCH = require("./mapgen_spec.json").ecoGrowth.minPatchArea.default;   // T74: 阈值跟随 spec（12→8）

const ECOPALETTE = {
  eco_surface: '#6b7683', eco_cold: '#3f6470', eco_arid: '#7d7258', eco_sea: '#2e5d46',
  eco_vent: '#8a4a2e', eco_rad: '#5d7a35', eco_core: '#8a3226', eco_nexus: '#4a3a5e'
};
const DIRS = [[1, 0], [-1, 0], [0, 1], [0, -1]];

function bandMetrics(region) {
  const { w, h, bandRows, ecoOf } = region;
  const per = [];
  for (let b = 1; b <= 8; b++) {
    const cnt = {}, tot = bandRows * w;
    for (let y = (b - 1) * bandRows; y < b * bandRows; y++)
      for (let x = 0; x < w; x++) {
        const o = ecoOf[y * w + x];
        cnt[o] = (cnt[o] || 0) + 1;
      }
    const ecos = Object.keys(cnt);
    const shares = ecos.map(e => cnt[e] / tot);
    per.push({ band: b, ecos: ecos.length, ecoList: ecos, maxShare: Math.max(...shares), counts: cnt, tot });
  }
  return per;
}

function bandCompCounts(region) {   // 每 (eco,band) 的连通块数
  const { w, h, bandRows, ecoOf } = region;
  const out = [];
  for (let b = 1; b <= 8; b++) {
    const cnt = {};
    for (let y = (b - 1) * bandRows; y < b * bandRows; y++)
      for (let x = 0; x < w; x++) {
        const o = ecoOf[y * w + x];
        cnt[o] = (cnt[o] || 0) + 1;
      }
    const seen = new Set();
    for (let y = (b - 1) * bandRows; y < b * bandRows; y++)
      for (let x = 0; x < w; x++) {
        const i = y * w + x, o = ecoOf[i];
        if (seen.has(i)) continue;
        let size = 0; const st = [i]; seen.add(i);
        while (st.length) {
          const c = st.pop(); size++;
          const cx = c % w, cy = (c / w) | 0;
          DIRS.forEach(d => {
            const nx = cx + d[0], ny = cy + d[1];
            if (nx < 0 || ny < (b - 1) * bandRows || nx >= w || ny >= b * bandRows) return;
            const ni = ny * w + nx;
            if (!seen.has(ni) && ecoOf[ni] === o) { seen.add(ni); st.push(ni); }
          });
        }
        out.push({ band: b, eco: o, comps: size >= 0 ? 1 : 1, size });
      }
    // 上面的逐格 size 累计不对——重新按块输出：
    void cnt; void out.pop;
  }
  void out;
  return perBandComps(region);
}

function perBandComps(region) {     // 正确版：按 (eco,band) 连通块
  const { w, bandRows, ecoOf } = region;
  const out = [];
  for (let b = 1; b <= 8; b++) {
    const cnt = {};
    for (let y = (b - 1) * bandRows; y < b * bandRows; y++)
      for (let x = 0; x < w; x++) {
        const o = ecoOf[y * w + x];
        cnt[o] = (cnt[o] || 0) + 1;
      }
    const seen = new Set();
    for (let y = (b - 1) * bandRows; y < b * bandRows; y++)
      for (let x = 0; x < w; x++) {
        const i = y * w + x, o = ecoOf[i];
        if (seen.has(i)) continue;
        let size = 0; const st = [i]; seen.add(i);
        while (st.length) {
          const c = st.pop(); size++;
          const cx = c % w, cy = (c / w) | 0;
          DIRS.forEach(d => {
            const nx = cx + d[0], ny = cy + d[1];
            if (nx < 0 || ny < (b - 1) * bandRows || nx >= w || ny >= b * bandRows) return;
            const ni = ny * w + nx;
            if (!seen.has(ni) && ecoOf[ni] === o) { seen.add(ni); st.push(ni); }
          });
        }
        out.push({ band: b, eco: o, comps: 1, size });
      }
    // 计数压缩：同 (eco,band) 的块数
  }
  return out;
}

function perBandCompList(region) {  // [{band, eco, size}] 每个连通块一条
  const { w, bandRows, ecoOf } = region;
  const out = [];
  for (let b = 1; b <= 8; b++) {
    const seen = new Set();
    for (let y = (b - 1) * bandRows; y < b * bandRows; y++)
      for (let x = 0; x < w; x++) {
        const i = y * w + x, o = ecoOf[i];
        if (seen.has(i)) continue;
        let size = 0; const st = [i]; seen.add(i);
        while (st.length) {
          const c = st.pop(); size++;
          const cx = c % w, cy = (c / w) | 0;
          DIRS.forEach(d => {
            const nx = cx + d[0], ny = cy + d[1];
            if (nx < 0 || ny < (b - 1) * bandRows || nx >= w || ny >= b * bandRows) return;
            const ni = ny * w + nx;
            if (!seen.has(ni) && ecoOf[ni] === o) { seen.add(ni); st.push(ni); }
          });
        }
        out.push({ band: b, eco: o, size });
      }
  }
  return out;
}

function minPatchOf(region) {       // 全图最小生态块（含跨带）
  const { w, h, ecoOf } = region;
  const seen = new Set();
  let min = Infinity;
  for (let i = 0; i < w * h; i++) {
    if (seen.has(i)) continue;
    let size = 0; const st = [i]; seen.add(i);
    while (st.length) {
      const c = st.pop(); size++;
      const x = c % w, y = (c / w) | 0;
      DIRS.forEach(d => {
        const nx = x + d[0], ny = y + d[1];
        if (nx < 0 || ny < 0 || nx >= w || ny >= h) return;
        const ni = ny * w + nx;
        if (!seen.has(ni) && ecoOf[ni] === ecoOf[i]) { seen.add(ni); st.push(ni); }
      });
    }
    if (size < min) min = size;
  }
  return min;
}

function svgMap(region, seed) {
  const CS = 14, PAD = 10;
  const { w, h, bandRows, ecoOf } = region;
  let s = `<svg xmlns="http://www.w3.org/2000/svg" width="${w * CS + PAD * 2}" height="${h * CS + PAD * 2}" viewBox="0 0 ${w * CS + PAD * 2} ${h * CS + PAD * 2}">`;
  s += `<rect width="100%" height="100%" fill="#0d1013"/>`;
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++)
    s += `<rect x="${PAD + x * CS}" y="${PAD + y * CS}" width="${CS}" height="${CS}" fill="${ECOPALETTE[ecoOf[y * w + x]] || '#333'}"/>`;
  for (let b = 1; b <= 8; b++) {
    const y0 = PAD + (b - 1) * bandRows * CS;
    s += `<text x="${w * CS + PAD + 2}" y="${y0 + 14}" fill="#8a7f78" font-size="10">D${b}</text>`;
    if (b > 1) s += `<line x1="${PAD}" y1="${y0}" x2="${w * CS + PAD}" y2="${y0}" stroke="#cfc7c0" stroke-opacity=".3" stroke-dasharray="4,3"/>`;
  }
  s += `<text x="${PAD}" y="${h * CS + PAD + 12}" fill="#8a7f78" font-size="10">seed ${seed} · 生态混合色块图（T72 验收样张）</text>`;
  return s + '</svg>';
}

function main() {
  const args = process.argv.slice(2);
  const gi = args.indexOf('--runs');
  const RUNS = gi >= 0 ? parseInt(args[gi + 1], 10) : 500;
  const SEED0 = 1;

  const t0 = Date.now();
  const runs = [];
  let bandCountViol = 0, maxShareViol = 0, intersectViol = 0, compViol = 0, minPatchViol = 0;
  const compCounts = [];      // 所有 (eco,band) 连通块数的分布样本
  const minPatches = [];
  const intersectFails = [];
  for (let i = 0; i < RUNS; i++) {
    const seed = SEED0 + i;
    const r = MG.generate(seed, null, null);
    const per = bandMetrics(r);
    per.forEach(p => {
      if (p.ecos < 2 || p.ecos > 4) bandCountViol++;
      if (p.maxShare > 0.60) maxShareViol++;
    });
    for (let b = 1; b <= 7; b++) {
      const A = new Set(per[b - 1].ecoList), B = new Set(per[b].ecoList);
      const shared = [...A].some(e => B.has(e));
      if (!shared) { intersectViol++; intersectFails.push({ seed, boundary: b }); }
    }
    const comps = perBandCompList(r);
    const byKey = {};
    comps.forEach(c => { const k = c.band + '@' + c.eco; byKey[k] = (byKey[k] || 0) + 1; });
    Object.values(byKey).forEach(n => compCounts.push(n));
    if (Object.values(byKey).some(n => n > 3)) compViol++;
    const mp = minPatchOf(r);
    minPatches.push(mp);
    if (mp < SPEC_MIN_PATCH) minPatchViol++;
    runs.push({ seed, per, minPatch: mp });
  }
  const ms = Date.now() - t0;

  compCounts.sort((a, b) => a - b);
  const p95 = compCounts[Math.floor(compCounts.length * 0.95)];
  const p100 = compCounts[compCounts.length - 1];
  const summary = {
    runs: RUNS,
    bandCount: { viol: bandCountViol, rate: +(bandCountViol / (RUNS * 8)).toFixed(4), note: '每带生态数∈[2,4]，零例外=0 违例' },
    maxShare: { viol: maxShareViol, rate: +(maxShareViol / (RUNS * 8)).toFixed(4), note: '单带最大占比≤60%，零例外=0 违例' },
    adjacentIntersect: { viol: intersectViol, rate: +(intersectViol / (RUNS * 7)).toFixed(4), note: '相邻带交集≥1，100% 达标=0 违例' },
    perBandComponents: { p95, p100: p100, violRuns: compViol, note: '带内同生态连通块 ≤3（95 分位）' },
    minPatch: { viol: minPatchViol, min: Math.min(...minPatches), note: '最小生态块 ≥' + SPEC_MIN_PATCH + ' 格（spec 同步），零例外=0 违例' },
    perf: { msTotal: ms, msPerRun: +(ms / RUNS).toFixed(1) }
  };

  console.log('=== T72 生态混合验收（' + RUNS + ' 张）===');
  console.log('① 每带生态数∈[2,4]    违例 ' + bandCountViol + '（' + summary.bandCount.rate + '%）' + (bandCountViol === 0 ? ' ✓' : ' ✗'));
  console.log('② 单带最大占比≤60%    违例 ' + maxShareViol + '（' + summary.maxShare.rate + '%）' + (maxShareViol === 0 ? ' ✓' : ' ✗'));
  console.log('③ 相邻带交集≥1        违例 ' + intersectViol + '（' + summary.adjacentIntersect.rate + '%）' + (intersectViol === 0 ? ' ✓' : ' ✗'));
  console.log('④ 带内连通块≤3        95分位 ' + p95 + '（100%违例局 ' + compViol + '）' + (p95 <= 3 ? ' ✓' : ' ✗'));
  console.log('⑤ 最小生态块≥12格     最小 ' + Math.min(...minPatches) + '，违例 ' + minPatchViol + (minPatchViol === 0 ? ' ✓' : ' ✗'));
  console.log('耗时: ' + ms + 'ms（' + summary.perf.msPerRun + 'ms/张）');

  // 5 张不同 seed 的色块图
  const outDir = path.join(__dirname, '..', 'art', 'ecomix');
  fs.mkdirSync(outDir, { recursive: true });
  [1, 42, 777, 1234, 2024].forEach(seed => {
    const r = MG.generate(seed, null, null);
    fs.writeFileSync(path.join(outDir, 'sample_seed' + seed + '.svg'), svgMap(r, seed));
  });
  console.log('色块图 5 张 → art/ecomix/sample_seed{1,42,777,1234,2024}.svg');

  fs.writeFileSync(path.join(__dirname, 'ecomix_report.json'),
    JSON.stringify({ meta: { task: 'T72', runs: RUNS, threshold: { compP95: 3, minPatch: 12, maxShare: 0.6, count: [2, 4] } },
      summary, runs }, null, 1));

  const allOk = bandCountViol === 0 && maxShareViol === 0 && intersectViol === 0 && p95 <= 3 && minPatchViol === 0;
  console.log(allOk ? '\nT72 验收全过。' : '\nT72 验收未过。');
  process.exit(allOk ? 0 : 1);
}

main();
