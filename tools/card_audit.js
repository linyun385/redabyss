// T47 卡池结构诊断。只读数据，不改任何东西。
// 用法：node tools/card_audit.js
// 输出：tools/card_audit.json + 控制台摘要
//
// 「应有量」公式（独立性零假设）：
//   E(cell) = 行合计 × 列合计 / 总数
//   即假设「脉分布」与「费用分布」无关时该格的期望卡数。
//   残差 = O - E；|残差| ≥ max(3, 2*sqrt(E)) 记为热区/空洞。
//
// 超模折算系数（假设，非官方数据——来源见 docs/CARD_AUDIT.md）：
//   伤害 1.0/点，格挡 1.0/点，回复 1.0/点，抽牌 2.5/张，
//   凝视 2.0/点，共振 0.5/点，力量/敏捷 4.0/点（持续），再生 1.5/点，
//   灼烧/中毒 1.2/点×回数，虚弱/脆弱 1.0/回合。
//   能量折算：score / max(1, energy) 为「每费价值」。0 费牌以 1 费为分母（防除零，会低估 0 费价值——见报告边界）。
'use strict';
const fs = require('fs');
const path = require('path');
const ROOT = path.join(__dirname, '..');

const CLASSES = ['diver', 'tremor', 'anmin', 'cangmin'];
const VEINS = ['light', 'water', 'heat', 'tremor', 'mineral'];
const TYPES = ['attack', 'skill', 'power'];
const RARITIES = ['common', 'uncommon', 'rare', 'special'];

// ── 读入并断言 ──
const data = {};
let total = 0;
const expect = { diver: 80, tremor: 80, anmin: 50, cangmin: 50 };
for (const cls of CLASSES) {
  const p = path.join(ROOT, 'cards', cls + '.json');
  const d = JSON.parse(fs.readFileSync(p, 'utf8'));
  data[cls] = Array.isArray(d) ? d : d.cards;
  total += data[cls].length;
}
for (const cls of CLASSES) {
  if (data[cls].length !== expect[cls]) {
    console.error('断言失败: ' + cls + ' 卡数 ' + data[cls].length + ' != ' + expect[cls] + '（卡池被改动，先跑 pack_check 确认）');
    process.exit(1);
  }
}
console.log('读入 ' + total + ' 张卡（断言通过：' + CLASSES.map(c => c + '=' + data[c].length).join(' / ') + '）');

// ── 工具 ──
function veinKey(c) { const v = (c.veins || []).filter(x => VEINS.includes(x)); return v.length ? v[0] : 'none'; }
function costKey(c) { const e = c.energy || 0; return e >= 3 ? '3+' : String(e); }
function fingerprint(c) {
  const e = c.effect || {};
  const parts = [];
  for (const k of Object.keys(e).sort()) {
    const v = JSON.stringify(e[k]);
    parts.push(k + '=' + v);
  }
  return parts.join(';') || '(无效果)';
}
function score(c) {
  // 折算系数见文件头注释
  const e = c.effect || {};
  let s = 0;
  s += (e.damage || 0) * (e.hits || 1) * 1.0;
  s += (e.block || 0) * 1.0;
  s += (e.heal || 0) * 1.0;
  s += (e.draw || 0) * 2.5;
  s += (e.gaze_gain || 0) * 2.0;
  s += (e.gaze_reduce || 0) * 1.0;
  s += (e.resonance_gain || 0) * 0.5;
  s += (e.resonance_drain || 0) * 0.5;
  for (const sp of (e.special || [])) {
    const code = sp.code || sp;
    const v = typeof sp === 'object' ? (sp.v || sp.value || 0) : 0;
    const t = sp.turns || 0;
    if (code === 'strength' || code === 'dexterity') s += v * 4.0;
    else if (code === 'regenerate') s += v * 1.5;
    else if (code === 'burn' || code === 'poison') s += (v || 3) * 1.2 * (t || 3);
    else if (code === 'weak' || code === 'frail') s += (sp.turns || 2) * 1.0;
    else if (code === 'thorns') s += v * 1.5;
    else if (code === 'delete_random') s += 6.0;
  }
  if (e.exhaust) s *= 0.8;           // 消耗折价 20%
  if (e.retain) s += 1.5;
  return s;
}

// ── 矩阵：职业 × 脉 × 费用 × 类型 ──
const matrix = {};
for (const cls of CLASSES) {
  const cards = data[cls];
  const m = { total: cards.length, byVein: {}, byCost: {}, byType: {}, byRarity: {}, cells: {} };
  for (const v of VEINS.concat(['none'])) m.byVein[v] = 0;
  for (const c of ['0', '1', '2', '3+']) m.byCost[c] = 0;
  for (const t of TYPES) m.byType[t] = 0;
  for (const r of RARITIES) m.byRarity[r] = 0;
  for (const card of cards) {
    m.byVein[veinKey(card)]++;
    m.byCost[costKey(card)]++;
    if (m.byType[card.type] !== undefined) m.byType[card.type]++;
    if (m.byRarity[card.rarity] !== undefined) m.byRarity[card.rarity]++;
    const key = veinKey(card) + '|' + costKey(card) + '|' + card.type;
    m.cells[key] = (m.cells[key] || 0) + 1;
  }
  matrix[cls] = m;
}

// ── 热区/空洞（独立性残差，按职业内 脉×费用 边际表）──
const spots = [];
for (const cls of CLASSES) {
  const m = matrix[cls];
  const cells = m.cells;
  const rowTot = {}, colTot = {};
  let grand = 0;
  for (const key of Object.keys(cells)) {
    const [v, c] = key.split('|');
    rowTot[v] = (rowTot[v] || 0) + cells[key];
    colTot[c] = (colTot[c] || 0) + cells[key];
    grand += cells[key];
  }
  for (const key of Object.keys(cells)) {
    const [v, c, t] = key.split('|');
    const E = rowTot[v] * colTot[c] / grand;
    const O = cells[key];
    const resid = O - E;
    if (Math.abs(resid) >= Math.max(3, 2 * Math.sqrt(E))) {
      spots.push({ cls, vein: v, cost: c, type: t, observed: O, expected: +E.toFixed(1), residual: +resid.toFixed(1), kind: resid > 0 ? '热区' : '空洞' });
    }
  }
}

// ── 重复度 ──
const byFp = {};
const nameCount = {};
for (const cls of CLASSES) {
  for (const c of data[cls]) {
    const fp = fingerprint(c);
    (byFp[fp] = byFp[fp] || []).push({ cls, id: c.id, name: c.name, cost: c.energy, rarity: c.rarity });
    nameCount[c.name] = (nameCount[c.name] || 0) + 1;
  }
}
const dupEffects = Object.entries(byFp).filter(([fp, list]) => list.length > 1)
  .map(([fp, list]) => ({ count: list.length, cards: list, fp: fp.slice(0, 120) }))
  .sort((a, b) => b.count - a.count);
const dupNames = Object.entries(nameCount).filter(([n, c]) => c > 1).map(([n, c]) => ({ name: n, count: c }));

// ── 超模/废卡嫌疑（同职业同类型内，score/energy 与中位数比）──
function median(a) { const s = a.slice().sort((x, y) => x - y); const m = Math.floor(s.length / 2); return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2; }
const suspects = [];
for (const cls of CLASSES) {
  for (const t of TYPES) {
    const pool = data[cls].filter(c => c.type === t).map(c => ({ card: c, density: score(c) / Math.max(1, c.energy || 0) }));
    if (pool.length < 4) continue;
    const med = median(pool.map(p => p.density));
    for (const p of pool) {
      if (p.density > med * 1.8 && p.density > 8) suspects.push({ cls, type: t, name: p.card.name, id: p.card.id, cost: p.card.energy, density: +p.density.toFixed(1), med: +med.toFixed(1), kind: '超模嫌疑' });
      if (p.density < med * 0.35) suspects.push({ cls, type: t, name: p.card.name, id: p.card.id, cost: p.card.energy, density: +p.density.toFixed(1), med: +med.toFixed(1), kind: '废卡嫌疑' });
    }
  }
}
suspects.sort((a, b) => b.density / b.med - a.density / a.med);

// ── 落盘 + 摘要 ──
const out = { total, matrix, spots, dupEffects, dupNames, suspects, coefficients: { damage: 1.0, block: 1.0, heal: 1.0, draw: 2.5, gaze: 2.0, resonance: 0.5, strength: 4.0, dexterity: 4.0, regenerate: 1.5, burn: 1.2, poison: 1.2, weak: 1.0, frail: 1.0, thorns: 1.5, exhaustDiscount: 0.8, note: '系数为设计假设：1 费≈1 点即时价值；抽牌按 StS 经验一张牌≈2.5 价值；持续 buff 按整场战斗约 2 次收益折算。' } };
fs.writeFileSync(path.join(ROOT, 'tools', 'card_audit.json'), JSON.stringify(out, null, 1), 'utf8');

console.log('\n── 脉分布（各职业）──');
for (const cls of CLASSES) {
  const m = matrix[cls];
  console.log(cls.padEnd(8) + VEINS.map(v => v + '=' + (m.byVein[v] || 0)).join('  ') + '  none=' + (m.byVein.none || 0));
}
console.log('\n── 费用分布 ──');
for (const cls of CLASSES) {
  const m = matrix[cls];
  console.log(cls.padEnd(8) + ['0', '1', '2', '3+'].map(c => c + '=' + (m.byCost[c] || 0)).join('  '));
}
console.log('\n── 类型分布 ──');
for (const cls of CLASSES) {
  const m = matrix[cls];
  console.log(cls.padEnd(8) + TYPES.map(t => t + '=' + (m.byType[t] || 0)).join('  ') + '  rare=' + m.byRarity.rare);
}
console.log('\n── 热区/空洞（独立性残差 |O-E| ≥ max(3, 2√E)）── ' + spots.length + ' 格');
for (const s of spots.slice(0, 24)) console.log('  [' + s.kind + '] ' + s.cls + ' ' + s.vein + '/' + s.cost + '/' + s.type + ' 实' + s.observed + ' 期望' + s.expected + ' 残差' + s.residual);
console.log('\n── 完全同效果卡组 ── ' + dupEffects.length + ' 组');
for (const d of dupEffects.slice(0, 10)) console.log('  ×' + d.count + ' ' + d.cards.map(c => c.name + '(' + c.cls + ')').join(' | '));
console.log('\n── 同名卡 ── ' + dupNames.length + ' 组: ' + dupNames.map(d => d.name + '×' + d.count).join('、'));
console.log('\n── 超模/废卡嫌疑（按每费价值 vs 同类中位数）── ' + suspects.length + ' 张');
for (const s of suspects.slice(0, 20)) console.log('  [' + s.kind + '] ' + s.cls + ' ' + s.name + ' ' + s.cost + '费 密度' + s.density + '（中位 ' + s.med + '）' + ' ' + s.id);
console.log('\n已写入 tools/card_audit.json');
