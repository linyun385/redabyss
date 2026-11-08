/* T61 自检：①新敌意图签名两两去重（+对照现有签名）；②任选 3 只新敌用真实引擎开战验证能出手。
   用法：node tools/_t61_check.js —— 任何失败 exit 1 */
'use strict';
const path = require('path');
const fs = require('fs');
const enemies = require(path.join(__dirname, '..', 'enemies', 'all.json'));
const RedAbyss = require(path.join(__dirname, '..', 'engine', 'core.js'));

const sig = p => p.map(i => i.type +
  (i.times ? 'x' + i.times : '') + (i.pierce ? 'P' : '') + (i.mirror ? 'M' : '') +
  (i.drain_discard ? 'D' : '') + (i.status ? '#' + i.status : '')).join('>');

const newOnes = enemies.filter(x => x.eco);
const oldOnes = enemies.filter(x => !x.eco);

// ① 新敌签名两两去重
const seen = {}; let dupPairs = 0;
newOnes.forEach(x => {
  const s = sig(x.intent_pattern);
  if (seen[s]) { console.error('FAIL 新敌签名重复: ' + seen[s] + ' vs ' + x.id + ' → ' + s); dupPairs++; }
  seen[s] = x.id;
});
// 对照现有（旧内容允许重复，但新敌不许撞旧签名）
let oldClash = 0;
const oldSigs = {};
oldOnes.forEach(x => { oldSigs[sig(x.intent_pattern)] = x.id; });
newOnes.forEach(x => {
  const s = sig(x.intent_pattern);
  if (oldSigs[s]) { console.error('FAIL 新敌撞旧签名: ' + x.id + ' = ' + oldSigs[s] + ' → ' + s); oldClash++; }
});

// ② 生态间普通怪签名去重（硬约束：任意两个生态的普通怪意图组合不能完全相同）
const ecoNormalSigs = {};
newOnes.filter(x => x.tier === 'normal').forEach(x => {
  const s = sig(x.intent_pattern);
  (ecoNormalSigs[s] = ecoNormalSigs[s] || []).push(x.eco);
});
let ecoDup = 0;
Object.entries(ecoNormalSigs).forEach(([s, ecos]) => {
  if (new Set(ecos).size > 1) { console.error('FAIL 跨生态普通怪同签名: ' + s + ' → ' + ecos.join(',')); ecoDup++; }
});

// ③ 引擎实出：抽 3 只新敌（普通/精英/boss 各一）真实开战并打几回合
const picks = [
  enemies.find(x => x.id === 'enemy_d1_06'),
  enemies.find(x => x.id === 'enemy_d3_e3'),
  enemies.find(x => x.id === 'enemy_d6_b2')
];
const engineLog = [];
const results = picks.map(def => {
  const run = RedAbyss.newRun('diver', { seed: 424242 });
  const C = RedAbyss.startCombat(run, [def]);
  let guard = 0;
  while (!C.over && guard++ < 30) {
    RedAbyss.endTurn(C);            // 敌方回合驱动（engine.nextIntent / enemyAct）
  }
  return { id: def.id, name: def.name, turns: Math.min(guard, 30),
    over: C.over, hp: run.hp, acted: run.hp < run.maxHp || C.enemies.some(e => e.buffAtk || e.block > 0) };
});

const passed = dupPairs === 0 && oldClash === 0 && ecoDup === 0 && results.every(r => r.acted);
console.log('新敌数量: ' + newOnes.length + '；唯一签名: ' + Object.keys(seen).length);
console.log('新敌两两重复: ' + dupPairs + '；撞旧签名: ' + oldClash + '；跨生态普通怪同签名: ' + ecoDup);
results.forEach(r => console.log('引擎实出: ' + r.id + ' ' + r.name + ' → ' + r.turns + ' 回合，over=' + r.over + '，hp ' + r.hp + (r.acted ? '（已出手）✓' : '（未出手？）✗')));
console.log(passed ? '\nT61 自检全部通过。' : '\nT61 自检失败。');
process.exit(passed ? 0 : 1);
