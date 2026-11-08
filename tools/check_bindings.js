/* T58 绑定表校验器：id 存在、数量达标、无重复、每生态深带有自己的 boss、生态枚举与 spec 一致。
   输出覆盖率表（生态 × 带 × 类型 填充率）。任何不达标 → exit 1。
   用法：node tools/check_bindings.js */
'use strict';
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
let fails = 0;
const fail = m => { console.log('  FAIL  ' + m); fails++; };
const ok = m => console.log('  ok    ' + m);

const spec = JSON.parse(fs.readFileSync(path.join(ROOT, 'tools', 'mapgen_spec.json'), 'utf8'));
const table = JSON.parse(fs.readFileSync(path.join(ROOT, 'data', 'mapgen_bindings.json'), 'utf8'));
const enemies = require(path.join(ROOT, 'enemies', 'all.json'));
const events = require(path.join(ROOT, 'events', 'all.json'));

const enemyIds = new Set(enemies.map(x => x.id));
const eventIds = new Set(events.map(x => x.id));
const BANDS = ['1', '2', '3', '4', '5', '6', '7', '8'];
const TYPES = ['enemy', 'elite', 'boss', 'event'];

console.log('=== T58 绑定表校验 ===\n');

// 1. 生态枚举一致
const specEcos = spec.ecos.map(e => e.id).sort().join(',');
const tableEcos = Object.keys(table.eco).sort().join(',');
if (specEcos === tableEcos) ok('生态枚举与 mapgen_spec.json 一致（8 种）');
else fail('生态枚举不一致：spec=' + specEcos + ' table=' + tableEcos);

// 2. 每（生态×带）校验
const MIN = { enemy: 3, elite: 1, boss: 1, event: 1 };
const coverage = {};   // eco -> band -> {type: n}
let cellCount = 0, filled = 0;
const ecoBossSets = {};
for (const ecoId of Object.keys(table.eco)) {
  const e = table.eco[ecoId];
  coverage[ecoId] = {};
  const bands = Object.keys(e.bands);
  if (bands.length !== 8 || BANDS.some(b => bands.indexOf(b) < 0)) fail(ecoId + ' 带键不完整（应 1..8）');
  BANDS.forEach(b => {
    const cell = e.bands[b];
    if (!cell) { fail(ecoId + '@b' + b + ' 缺格'); return; }
    cellCount++;
    coverage[ecoId][b] = {};
    TYPES.forEach(t => {
      const pool = cell[t] || [];
      coverage[ecoId][b][t] = pool.length;
      if (pool.length >= MIN[t]) filled++;
      else fail(ecoId + '@b' + b + ' ' + t + ' 数量 ' + pool.length + ' < ' + MIN[t]);
      // id 存在
      pool.forEach(id => {
        const exists = t === 'event' ? eventIds.has(id) : enemyIds.has(id);
        if (!exists) fail(ecoId + '@b' + b + ' ' + t + ' 引用不存在的 id：' + id);
      });
      // 无重复
      if (new Set(pool).size !== pool.length) fail(ecoId + '@b' + b + ' ' + t + ' 池内有重复 id');
    });
    if (cell.shop !== 1 && cell.shop !== 2 && cell.shop !== 3) fail(ecoId + '@b' + b + ' shop 档位非法：' + cell.shop);
    // boss 独占性收集
    ecoBossSets[ecoId] = ecoBossSets[ecoId] || new Set();
    (cell.boss || []).forEach(x => ecoBossSets[ecoId].add(x));
  });
}

// 3. 每生态深带（6–8）有自己的 boss（不许共用）
for (const ecoId of Object.keys(table.eco)) {
  const deep = ['6', '7', '8'].filter(b => (table.eco[ecoId].bands[b].boss || []).length > 0);
  if (deep.length === 3) ok(ecoId + ' 深带 6–8 均有自己的 boss 候选（' + [...ecoBossSets[ecoId]].join(', ') + '）');
  else fail(ecoId + ' 深带 boss 缺失（只有 b' + deep.join(',b') + '）');
}
// 4. boss 池跨生态不共用（两生态的 boss 池交集应为空）
const ecoList = Object.keys(ecoBossSets);
for (let i = 0; i < ecoList.length; i++) for (let j = i + 1; j < ecoList.length; j++) {
  const a = ecoBossSets[ecoList[i]], b2 = ecoBossSets[ecoList[j]];
  const shared = [...a].filter(x => b2.has(x));
  if (shared.length) fail('boss 共用：' + ecoList[i] + ' 与 ' + ecoList[j] + ' 共享 ' + shared.join(','));
}
if (fails === 0) ok('boss 池跨生态零共用');

// 5. 覆盖率表
console.log('\n── 覆盖率（每格池大小；要求 敌≥3 精≥1 boss≥1 事件≥1）──');
console.log('生态\\带         ' + BANDS.map(b => 'b' + b + '        ').join(''));
for (const ecoId of Object.keys(coverage)) {
  let line = ecoId.padEnd(14) + ' ';
  BANDS.forEach(b => {
    const c = coverage[ecoId][b] || {};
    line += ('e' + (c.enemy || 0) + '/l' + (c.elite || 0) + '/B' + (c.boss || 0) + '/v' + (c.event || 0) + '  ').padEnd(10);
  });
  console.log(line);
}
const totalCells = cellCount * TYPES.length;
console.log('\n填充率：' + filled + '/' + totalCells + ' 格类型达标（敌≥3 精≥1 boss≥1 事件≥1）');

if (fails > 0) { console.log('\n' + fails + ' 项不达标'); process.exit(1); }
console.log('\n全部达标。');
