/* T59 地图生成回归模拟：生成 → 贪心走图（优先未访问出边；死路走救援规则）→ finalBoss。
   复用 tools/mapgen.js 的生成器与 T57 web 模块的同一套运行时规则（跨带 BOSS 判定 / 救援落点），
   不另写近似逻辑。只测量，不改游戏代码。
   用法：node tools/mapgen_sim.js --runs 500 [--seed0 1] */
'use strict';
const fs = require('fs');
const path = require('path');

const MG = require(path.join(__dirname, 'mapgen.js'));
const enemies = require(path.join(ROOT_PATH(), 'enemies', 'all.json'));
const events = require(path.join(ROOT_PATH(), 'events', 'all.json'));
function ROOT_PATH() { return path.join(__dirname, '..'); }

/* 参数与 tools/mapgen_spec.json v1.3 同步（与 web 模块、mapgen_test 三方一致） */
const P = {
  boss: { firstAlways: true, p0: 0.5, decay: 0.6, min: 0.1 },
  rescue: { penaltyHpPct: 10, penaltyGoldPct: 15, ambushChance: 0.5, pickRule: 'sameBandFirst' }
};

function dataProvider(ecoId, band) {
  const es = enemies.filter(x => x.layer === band);
  const evs = events.filter(x => x.layer === band);
  if (!es.length && !evs.length) return null;
  return {
    enemyPool: es.filter(x => x.tier === 'normal').map(x => x.id),
    elitePool: es.filter(x => x.tier === 'elite').map(x => x.id),
    bossPool: es.filter(x => x.tier === 'boss').map(x => x.id),
    eventPool: evs.map(x => x.id)
  };
}

function simulate(seed) {
  const t0 = process.hrtime.bigint();
  const region = MG.generate(seed, null, dataProvider);
  const genNs = process.hrtime.bigint() - t0;
  const rng = MG.makeRng((seed >>> 0) * 7919 + 13);   // 走图用独立种子流（与生成器解耦但可复现）

  const byId = {};
  region.nodes.forEach(n => { byId[n.id] = n; });
  const effTypeOf = n => (override[n.id] && n.type !== 'finalBoss') ? 'boss' : n.type;
  const visited = {}; const override = {}; const walked = {};
  let currentId = region.startId, crossCount = 0;
  visited[currentId] = true;
  let steps = 0, rescues = 0, bossFights = 0, ambushes = 0, penalties = 0;
  const bandVisits = {}; const typeVisited = {}; const typeWalkedOnly = {};
  const visitedByWalk = {};   // 首次救援发生前的自然推进
  let firstRescueHappened = false;
  bandVisits[byId[currentId].band] = 1;

  const outTargets = id => region.edges.filter(e => e.from === id).map(e => e.to);
  const isDeadEnd = () => effTypeOf(byId[currentId]) !== 'finalBoss' &&
    !outTargets(currentId).some(t => !visited[t]);
  function rescueTargets() {
    const cur = byId[currentId];
    const dist = n => Math.abs(n.x - cur.x) + Math.abs(n.y - cur.y);
    return region.nodes.filter(n => !visited[n.id] &&
      region.edges.some(e => e.to === n.id && visited[e.from]))
      .sort((a, b) => {
        if (P.rescue.pickRule === 'sameBandFirst') {
          const sa = a.band === cur.band ? 0 : 1, sb = b.band === cur.band ? 0 : 1;
          if (sa !== sb) return sa - sb;
        }
        return dist(a) - dist(b) || (a.id < b.id ? -1 : 1);
      });
  }
  function enterNode(nid) {
    const n = byId[nid];
    const edge = region.edges.find(e => e.from === currentId && e.to === nid);
    if (edge && edge.crossBand) {
      crossCount += 1;
      const p = (crossCount === 1 && P.boss.firstAlways)
        ? 1 : Math.max(P.boss.min, P.boss.p0 * Math.pow(P.boss.decay, crossCount - 2));
      if (rng() < p && n.type !== 'finalBoss') override[nid] = true;
    }
    steps += 1;
    if (edge) walked[edge.from + '>' + edge.to] = true;
    visited[nid] = true;
    visitedByWalk[nid] = !firstRescueHappened;
    currentId = nid;
    bandVisits[n.band] = (bandVisits[n.band] || 0) + 1;
    const t = effTypeOf(n);
    typeVisited[t] = (typeVisited[t] || 0) + 1;
    if (visitedByWalk[nid]) typeWalkedOnly[t] = (typeWalkedOnly[t] || 0) + 1;
    if (t === 'boss' || t === 'finalBoss') bossFights += 1;
  }
  function doRescue() {
    const cands = rescueTargets();
    if (!cands.length) return false;                 // 理论不可达（I2/I9 保证），出现即记录
    const t = cands[0];
    rescues += 1; firstRescueHappened = true;
    if (rng() < P.rescue.ambushChance) ambushes += 1; else penalties += 1;
    visited[t.id] = true; currentId = t.id;
    bandVisits[t.band] = (bandVisits[t.band] || 0) + 1;
    const tt = effTypeOf(t);
    typeVisited[tt] = (typeVisited[tt] || 0) + 1;
    return true;
  }

  let guard = 0, stuck = false;
  while (byId[currentId].type !== 'finalBoss' && guard++ < 5000) {
    if (byId[currentId].type === 'finalBoss') break;
    const outs = outTargets(currentId);
    const unvisited = outs.filter(t => !visited[t]);
    if (unvisited.length) {
      // 贪心：未访问出边里随机取一个（简单走法；不做深度寻路）
      enterNode(unvisited[Math.floor(rng() * unvisited.length)]);
    } else if (isDeadEnd()) {
      if (!doRescue()) { stuck = true; break; }
    } else break; // 不可达状态（防御）
  }
  const cleared = byId[currentId].type === 'finalBoss' && !stuck;
  return {
    seed, attempts: region.attempts, cleared, stuck, steps, rescues, bossFights,
    ambushes, penalties, crossCount,
    bandVisits, typeVisited, typeWalkedOnly,
    visitedTotal: Object.keys(visited).length,
    nodeTotal: region.nodes.length,
    genMs: Number(genNs / 1000000n * 1000n) / 1e6
  };
}

function main() {
  const args = process.argv.slice(2);
  const getArg = (k, d) => { const i = args.indexOf(k); return i >= 0 ? parseInt(args[i + 1], 10) : d; };
  const RUNS = Math.max(1, getArg('--runs', 500));
  const SEED0 = getArg('--seed0', 1);

  const t0 = Date.now();
  const runs = [];
  let failures = [];
  for (let i = 0; i < RUNS; i++) {
    const r = simulate(SEED0 + i);
    runs.push(r);
    if (!r.cleared) failures.push(r);
  }
  const simMs = Date.now() - t0;

  // 生成性能：100 张图
  const t1 = Date.now();
  for (let s = 900000; s < 900100; s++) MG.generate(s, null, null);
  const gen100Ms = Date.now() - t1;

  const avg = a => a.length ? a.reduce((x, y) => x + y, 0) / a.length : 0;
  const dist = a => { const d = {}; a.forEach(x => d[x] = (d[x] || 0) + 1); return d; };
  const clearRate = runs.filter(r => r.cleared).length / RUNS;
  const summary = {
    runs: RUNS, seed0: SEED0,
    clearRate,
    failSeeds: failures.map(f => ({ seed: f.seed, reason: f.stuck ? 'rescue 无落点（困死）' : '防御性中断（guard 上限）' })),
    rescuesPerRun: { avg: avg(runs.map(r => r.rescues)), dist: dist(runs.map(r => r.rescues)), runsWithZero: runs.filter(r => r.rescues === 0).length },
    stepsPerRun: { avg: avg(runs.map(r => r.steps)), min: Math.min(...runs.map(r => r.steps)), max: Math.max(...runs.map(r => r.steps)) },
    bossFightsPerRun: { avg: avg(runs.map(r => r.bossFights)), dist: dist(runs.map(r => r.bossFights)) },
    crossBandPerRun: { avg: avg(runs.map(r => r.crossCount)) },
    bandDwellAvg: {},       // band -> 平均到访格数
    typeVisitedAvg: {},     // type -> 平均到访（含救援）
    typeWalkedOnlyAvg: {},  // type -> 平均自然走到（首救前）——配额被「正常玩法」遇到的程度
    typeTotalOnMap: {},     // type -> 图上该类节点平均总数
    rescueBranch: { ambushAvg: avg(runs.map(r => r.ambushes)), penaltyAvg: avg(runs.map(r => r.penalties)) },
    perf: { gen100Ms, simMs, simMsPerRun: simMs / RUNS }
  };
  for (let b = 1; b <= 8; b++) summary.bandDwellAvg['D' + b] = avg(runs.map(r => r.bandVisits[b] || 0));
  ['combat', 'elite', 'random', 'shop', 'event', 'boss', 'finalBoss'].forEach(t => {
    summary.typeVisitedAvg[t] = avg(runs.map(r => r.typeVisited[t] || 0));
    summary.typeWalkedOnlyAvg[t] = avg(runs.map(r => r.typeWalkedOnly[t] || 0));
  });
  // 图上类型总数（用对照图按生成口径统计；各局节点数相同）
  const refRegion = MG.generate(SEED0, null, dataProvider);
  const refCount = {};
  refRegion.nodes.forEach(n => { refCount[n.type] = (refCount[n.type] || 0) + 1; });
  summary.typeTotalOnMap = refCount;

  const out = { meta: { task: 'T59', rules: '与 T57 web 模块同一套运行时规则（跨带 BOSS 判定/救援落点/贪心未访问优先）', params: P }, summary, runs };
  fs.writeFileSync(path.join(__dirname, 'mapgen_sim.json'), JSON.stringify(out, null, 1));

  /* ── 摘要输出 ── */
  console.log('=== T59 地图回归模拟 ===');
  console.log('可通关率: ' + (clearRate * 100).toFixed(1) + '%（' + runs.filter(r => r.cleared).length + '/' + RUNS + '）');
  if (failures.length) { console.log('未通关 seed 与原因:'); failures.slice(0, 20).forEach(f => console.log('  seed ' + f.seed + ': ' + (f.stuck ? 'rescue 无落点' : 'guard 中断'))); }
  console.log('救援次数/局: 平均 ' + summary.rescuesPerRun.avg.toFixed(2) + '，分布 ' + JSON.stringify(summary.rescuesPerRun.dist) + '，零救援局 ' + summary.rescuesPerRun.runsWithZero);
  console.log('步数/局: 平均 ' + summary.stepsPerRun.avg.toFixed(1) + '（' + summary.stepsPerRun.min + '–' + summary.stepsPerRun.max + '）');
  console.log('BOSS 战/局: 平均 ' + summary.bossFightsPerRun.avg.toFixed(2) + '，分布 ' + JSON.stringify(summary.bossFightsPerRun.dist) + '（跨带次数/局均值 ' + summary.crossBandPerRun.avg.toFixed(2) + '）');
  console.log('每带到访格数: ' + JSON.stringify(summary.bandDwellAvg));
  console.log('类型到访/局（含救援 | 仅自然走到 | 图上总数）:');
  ['combat', 'elite', 'random', 'shop', 'event', 'finalBoss'].forEach(t => {
    console.log('  ' + t.padEnd(10) + summary.typeVisitedAvg[t].toFixed(2) + ' | ' + summary.typeWalkedOnlyAvg[t].toFixed(2) + ' | ' + (summary.typeTotalOnMap[t] || 0));
  });
  console.log('救援分支: 伏击均值 ' + summary.rescueBranch.ambushAvg.toFixed(2) + ' / 惩罚均值 ' + summary.rescueBranch.penaltyAvg.toFixed(2));
  console.log('性能: 生成 100 图 ' + gen100Ms + 'ms；' + RUNS + ' 局模拟 ' + simMs + 'ms（' + summary.perf.simMsPerRun.toFixed(1) + 'ms/局）');

  /* ── T74 验收模式：--assert 时按验收线判 exit（步数≥36 / D2–D7 每带≥4.2 / 通关 100%）── */
  if (args.indexOf('--assert') >= 0) {
    const bad = [];
    if (summary.stepsPerRun.avg < 36) bad.push('步数均值 ' + summary.stepsPerRun.avg.toFixed(1) + ' < 36');
    for (let b = 2; b <= 7; b++) {
      const v = summary.bandDwellAvg['D' + b];
      if (v < 4.2) bad.push('D' + b + ' 到访 ' + v.toFixed(2) + ' < 4.2');
    }
    if (clearRate < 1) bad.push('通关率 ' + (clearRate * 100).toFixed(1) + '% < 100%');
    if (bad.length) { console.log('✗ T74 节奏验收未过: ' + bad.join('；')); process.exit(1); }
    console.log('T74 节奏验收（--assert）: 步数 ≥36 ✓ / D2–D7 每带 ≥4.2 ✓ / 通关 100% ✓');
  }
}

main();
