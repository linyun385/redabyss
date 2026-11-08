// 整体平衡摸底（只读）：按卡桶统计规模 / 稀有度 / 权重 / 费用分布
// 用途：整体平衡重构开工前的现状快照。DECK 桶定义见 INDEX 常量。
const fs = require('fs');
const path = require('path');

const HTML = path.join(__dirname, '..', 'web', 'index.html');
const lines = fs.readFileSync(HTML, 'utf8').split(/\r?\n/);
let idx = -1;
for (let i = 0; i < lines.length; i++) if (lines[i].trim().startsWith('const RAW = ')) { idx = i; break; }
if (idx < 0) { console.error('RAW not found'); process.exit(1); }
const RAW = JSON.parse(lines[idx].trim().replace(/^const RAW = /, '').replace(/;\s*$/, ''));

const DECK_BUCKETS = ['shared', 'diver', 'tremor', 'anmin', 'cangmin'];
const ENEMY_BUCKETS = ['enemies', 'anminEnemies', 'cngEnemies'];
const W = { common: 6, uncommon: 3, rare: 1 };   // index.html:7481
const pct = (a, b) => b ? (a / b * 100).toFixed(1) + '%' : '-';

console.log('上线权重表（index.html:7481）:', JSON.stringify(W));
console.log('special 不进奖励池（index.html:7480）\n');

let grand = 0, grandPool = 0;
for (const b of DECK_BUCKETS) {
  const arr = RAW[b] || [];
  if (!arr.length) { console.log('=== ' + b + ': 空 ===\n'); continue; }
  const rar = {};
  for (const c of arr) rar[c.rarity || '(无)'] = (rar[c.rarity || '(无)'] || 0) + 1;
  const pool = arr.filter(c => c.rarity !== 'special');
  const totalW = pool.reduce((a, c) => a + (W[c.rarity] || 1), 0);
  grand += arr.length; grandPool += pool.length;

  // 各稀有度占权重比
  const wByRar = {};
  for (const c of pool) wByRar[c.rarity || '(无)'] = (wByRar[c.rarity || '(无)'] || 0) + (W[c.rarity] || 1);

  // 费用分布
  const energies = arr.map(c => c.energy).filter(e => typeof e === 'number');
  const zeros = energies.filter(e => e === 0).length;
  const partC = arr.filter(c => c.part_cost);

  console.log('=== ' + b + ' ===');
  console.log('  卡数', arr.length, '| 进奖励池', pool.length, '| 总权重', totalW);
  console.log('  稀有度:', JSON.stringify(rar));
  const wLine = Object.keys(wByRar).map(k => k + ' ' + wByRar[k] + '(' + pct(wByRar[k], totalW) + ')').join('  ');
  console.log('  权重占比:', wLine);
  console.log('  能量: 0费', zeros, '/ ' + energies.length, '| 区间', Math.min(...energies), '~', Math.max(...energies));
  if (partC.length) console.log('  part_cost: ' + partC.length + ' 张, 值 ' + partC.map(c => c.part_cost).join('/'));
  const veins = {};
  for (const c of arr) for (const v of (c.veins || [])) veins[v] = (veins[v] || 0) + 1;
  if (Object.keys(veins).length) console.log('  脉:', JSON.stringify(veins));
  const types = {};
  for (const c of arr) types[c.type || '(无)'] = (types[c.type || '(无)'] || 0) + 1;
  console.log('  类型:', JSON.stringify(types));
  console.log('');
}

console.log('卡总数', grand, '| 其中进奖励池', grandPool, '\n');

// 敌人
console.log('=== 敌人 ===');
for (const b of ENEMY_BUCKETS) {
  const arr = RAW[b] || [];
  if (!arr.length) { console.log('  ' + b + ': 空'); continue; }
  const withHp = arr.filter(e => typeof e.hp === 'number');
  const withPhases = arr.filter(e => Array.isArray(e.phases));
  console.log('  ' + b + ':', arr.length, '个 | 顶层有hp', withHp.length, '| 有phases', withPhases.length);
  if (withHp.length) {
    const v = withHp.map(e => e.hp).sort((a, b2) => a - b2);
    console.log('      hp', v[0], '~', v[v.length - 1], '中位', v[Math.floor(v.length / 2)]);
  }
  if (withPhases.length) {
    const e0 = withPhases[0];
    const ph = e0.phases.map(p => typeof p.hp === 'number' ? p.hp : JSON.stringify(Object.keys(p)));
    console.log('      phases 样本(' + e0.id + '):', JSON.stringify(ph).slice(0, 200));
  }
}
