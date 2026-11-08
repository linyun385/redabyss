/* T60 内容缺口盘点：生态 × 深度带 × 内容类型，现有量 vs 配额目标，口径 A/B 对比。
   只盘点不写内容，不改任何数据。用法：node tools/content_gap.js
   输出：tools/content_gap.json + 终端矩阵。所有数字由本脚本产出。 */
'use strict';
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const spec = JSON.parse(fs.readFileSync(path.join(ROOT, 'tools', 'mapgen_spec.json'), 'utf8'));
const enemies = require(path.join(ROOT, 'enemies', 'all.json'));
const events = require(path.join(ROOT, 'events', 'all.json'));
const relics = require(path.join(ROOT, 'relics', 'all.json'));
const cards = [
  ...require(path.join(ROOT, 'cards', 'diver.json')),
  ...require(path.join(ROOT, 'cards', 'tremor.json')),
  ...require(path.join(ROOT, 'cards', 'anmin.json')),
  ...require(path.join(ROOT, 'cards', 'cangmin.json'))
];

const ECOS = spec.ecos;                       // 8 生态，homeBand 1..8，veinAffinity 见 spec
const BANDS = [1, 2, 3, 4, 5, 6, 7, 8];

/* 配额目标（口径 B，用户 2026-10-30 18:50 拍板「复用 + 带修饰」，数值取任务书区间中值）
   敌人 14 = 普通 8 / 精英 4 / boss 2；事件 8；遗物 9；卡 12 */
const QUOTA_B = { enemyNormal: 8, enemyElite: 4, enemyBoss: 2, event: 8, relic: 9, card: 12 };
/* 口径 A（仅作对比数字）：每（生态×带）独有，最小可玩密度 2 普通 / 1 精英 / 1 boss / 1 事件 / 1 遗物 / 2 卡 */
const QUOTA_A = { enemyNormal: 2, enemyElite: 1, enemyBoss: 1, event: 1, relic: 1, card: 2 };
/* 文本量估算（字/条）：任务书 80–150 字区间内按类型取值 */
const CHARS = { enemy: 100, event: 150, relic: 80, card: 80 };

/* 归属规则（脚本口径，与 docs/MAPGEN_DESIGN.md §0.1 一致）：
   - 敌人/事件：数据自带 layer 字段 → layer = 生态母本带
   - 遗物/卡牌：无 layer，按 veins 含生态主脉亲和归属；一个条目多脉时向每个亲和生态重复计数（共享计数）
   - 无脉亲和生态（eco_surface / eco_nexus）：按「素品」口径归 无脉 条目（veins 为空） */
function affinityOf(eco) { return eco.veinAffinity; }
function isPlain(item) { return !item.veins || !item.veins.length; }
function matchesEco(item, eco) {
  const v = affinityOf(eco);
  if (v === null || v === undefined) return isPlain(item);
  return (item.veins || []).indexOf(v) >= 0;
}

/* ── 现有量：按生态（母本带 / 脉亲和）────────────────── */
const currentPerEco = {};
ECOS.forEach(eco => {
  const home = eco.homeBand;
  const es = enemies.filter(x => x.layer === home);
  const evs = events.filter(x => x.layer === home);
  const rls = relics.filter(x => matchesEco(x, eco));
  const cds = cards.filter(x => matchesEco(x, eco));
  currentPerEco[eco.id] = {
    homeBand: home,
    veinAffinity: eco.veinAffinity,
    enemy: {
      normal: es.filter(x => x.tier === 'normal').length,
      elite: es.filter(x => x.tier === 'elite').length,
      boss: es.filter(x => x.tier === 'boss').length,
      total: es.length
    },
    event: evs.length,
    relic: rls.length,
    card: cds.length
  };
});

/* ── 现有量矩阵：生态 × 带（内容只落在母本带格，其余格为 0 —— 这就是要补的缺口）── */
const matrix = [];
ECOS.forEach(eco => BANDS.forEach(band => {
  const isHome = band === eco.homeBand;
  const es = isHome ? enemies.filter(x => x.layer === band) : [];
  const evs = isHome ? events.filter(x => x.layer === band) : [];
  matrix.push({
    eco: eco.id, band,
    isHome,
    enemy: { normal: es.filter(x => x.tier === 'normal').length, elite: es.filter(x => x.tier === 'elite').length, boss: es.filter(x => x.tier === 'boss').length, total: es.length },
    event: evs.length,
    relic: isHome ? relics.filter(x => matchesEco(x, eco)).length : 0,
    card: isHome ? cards.filter(x => matchesEco(x, eco)).length : 0,
    note: isHome ? '母本带：现有内容按口径 B 全额复用' : '口径 B 下不独有内容：由带修饰（数值/词缀/精英化）覆盖'
  });
}));

/* ── 口径 B 缺口：每生态 配额 − 现有 ────────────────── */
const gapsB = {};
let newB = { enemyNormal: 0, enemyElite: 0, enemyBoss: 0, event: 0, relic: 0, card: 0, chars: 0 };
ECOS.forEach(eco => {
  const c = currentPerEco[eco.id];
  const g = {
    enemyNormal: Math.max(0, QUOTA_B.enemyNormal - c.enemy.normal),
    enemyElite: Math.max(0, QUOTA_B.enemyElite - c.enemy.elite),
    enemyBoss: Math.max(0, QUOTA_B.enemyBoss - c.enemy.boss),
    event: Math.max(0, QUOTA_B.event - c.event),
    relic: Math.max(0, QUOTA_B.relic - c.relic),
    card: Math.max(0, QUOTA_B.card - c.card)
  };
  g.enemyTotal = g.enemyNormal + g.enemyElite + g.enemyBoss;
  g.chars = g.enemyTotal * CHARS.enemy + g.event * CHARS.event + g.relic * CHARS.relic + g.card * CHARS.card;
  gapsB[eco.id] = g;
  newB.enemyNormal += g.enemyNormal; newB.enemyElite += g.enemyElite; newB.enemyBoss += g.enemyBoss;
  newB.event += g.event; newB.relic += g.relic; newB.card += g.card;
  newB.chars += g.chars;
});
newB.enemyTotal = newB.enemyNormal + newB.enemyElite + newB.enemyBoss;

/* ── 口径 A 总量：64 格 × 每格配额；现有内容只抵母本带格 ── */
const totalA = {
  enemyNormal: QUOTA_A.enemyNormal * 64, enemyElite: QUOTA_A.enemyElite * 64,
  enemyBoss: QUOTA_A.enemyBoss * 64, event: QUOTA_A.event * 64,
  relic: QUOTA_A.relic * 64, card: QUOTA_A.card * 64
};
totalA.enemyTotal = totalA.enemyNormal + totalA.enemyElite + totalA.enemyBoss;
// A 可复用：现有内容只覆盖（生态×母本带）这 8 个格，且每格最多抵掉该格配额
const reuseA = { enemyNormal: 0, enemyElite: 0, enemyBoss: 0, event: 0, relic: 0, card: 0 };
ECOS.forEach(eco => {
  const c = currentPerEco[eco.id];
  reuseA.enemyNormal += Math.min(c.enemy.normal, QUOTA_A.enemyNormal);
  reuseA.enemyElite += Math.min(c.enemy.elite, QUOTA_A.enemyElite);
  reuseA.enemyBoss += Math.min(c.enemy.boss, QUOTA_A.enemyBoss);
  reuseA.event += Math.min(c.event, QUOTA_A.event);
  reuseA.relic += Math.min(c.relic, QUOTA_A.relic);
  reuseA.card += Math.min(c.card, QUOTA_A.card);
});
const newA = {};
['enemyNormal', 'enemyElite', 'enemyBoss', 'event', 'relic', 'card'].forEach(k => {
  newA[k] = totalA[k] - reuseA[k];
});
newA.enemyTotal = newA.enemyNormal + newA.enemyElite + newA.enemyBoss;
newA.chars = newA.enemyTotal * CHARS.enemy + newA.event * CHARS.event + newA.relic * CHARS.relic + newA.card * CHARS.card;

/* ── 对比与每生态生产单 ── */
const result = {
  meta: {
    task: 'T60',
    generatedBy: 'tools/content_gap.js',
    sources: {
      enemies: 'enemies/all.json（80：normal 43 / elite 25 / boss 12，layer 字段归属）',
      events: 'events/all.json（72，layer 字段归属）',
      relics: 'relics/all.json（76，无 layer，按 veins 主脉亲和归属，无脉归素品）',
      cards: 'cards/{diver,tremor,anmin,cangmin}.json（260，按 veins 主脉亲和归属，多脉共享计数）',
      ecoDefs: 'tools/mapgen_spec.json v1.3（8 生态，homeBand 与 veinAffinity）'
    },
    quotaB: QUOTA_B,
    quotaA: QUOTA_A,
    charsPerItem: CHARS,
    notes: [
      '现有内容在口径 B 下全额复用为本生态唯一批次；深度带差异由绑定表的数值/词缀/精英化字段承载（T58），不计新条目。',
      '口径 A 数字按「每（生态×带）最小可玩密度」计（2 普通/1 精英/1 boss/1 事件/1 遗物/2 卡 × 64 格）；现有内容只抵母本带格。',
      '共享计数：一张多脉卡/遗物向每个含其主脉的生态重复计入「可用」，缺口 = max(0, 配额 − 可用)。',
      '无主脉生态（eco_surface/eco_nexus）按素品口径（veins 为空的条目）计数。'
    ]
  },
  currentPerEco,
  matrix,
  planB: { gaps: gapsB, newTotals: newB },
  planA: { total: totalA, reuse: reuseA, newTotals: newA },
  comparison: {
    enemy: { A: totalA.enemyTotal, B: QUOTA_B.enemyTotalPerEco = undefined, Bnew: newB.enemyTotal, reuseB: 80 },
    note: '对比明细见 planA/planB 字段；B 的「总量」= 现有 80 敌（复用）+ 新增'
  }
};
// comparison 修正（避免误植字段）
result.comparison = {
  enemy: { totalA: totalA.enemyTotal, existing: 80, newB: newB.enemyTotal, newA: newA.enemyTotal },
  event: { totalA: totalA.event, existing: events.length, newB: newB.event, newA: newA.event },
  relic: { totalA: totalA.relic, existing: relics.length, newB: newB.relic, newA: newA.relic },
  card: { totalA: totalA.card, existing: cards.length, newB: newB.card, newA: newA.card }
};

/* ── 终端矩阵 ── */
const pad = (s, n) => (String(s) + ' '.repeat(n)).slice(0, n);
console.log('=== T60 内容缺口盘点（数字全部由脚本产出）===');
console.log('\n── 每生态现有量（母本带归属 / 脉亲和归属）──');
console.log('生态            带  敌(普/精/boss)  事件  遗物  卡');
ECOS.forEach(eco => {
  const c = currentPerEco[eco.id];
  console.log(pad(eco.id, 14) + pad(c.homeBand, 4) +
    pad(c.enemy.normal + '/' + c.enemy.elite + '/' + c.enemy.boss, 16) +
    pad(c.event, 6) + pad(c.relic, 6) + c.card);
});
console.log('\n── 口径 B 缺口（每生态要新写多少）──');
console.log('生态            敌(普/精/boss)  事件  遗物  卡   预计字数');
ECOS.forEach(eco => {
  const g = gapsB[eco.id];
  const pad = (s, n) => (String(s) + ' '.repeat(n)).slice(0, n);
  console.log(pad(eco.id, 14) +
    pad(g.enemyNormal + '/' + g.enemyElite + '/' + g.enemyBoss, 16) +
    pad(g.event, 6) + pad(g.relic, 6) + pad(g.card, 5) + g.chars);
});
console.log(pad('合计', 14) +
  pad(newB.enemyNormal + '/' + newB.enemyElite + '/' + newB.enemyBoss, 16) +
  pad(newB.event, 6) + pad(newB.relic, 6) + pad(newB.card, 5) + newB.chars);
console.log('\n── 口径对比（新增条目 / 预计字数）──');
console.log('类型    口径A总量  A可复用  A新增   B新增');
console.log('敌人    ' + pad(totalA.enemyTotal, 9) + pad(reuseA.enemyNormal + reuseA.enemyElite + reuseA.enemyBoss, 9) + pad(newA.enemyTotal, 8) + newB.enemyTotal);
console.log('事件    ' + pad(totalA.event, 9) + pad(reuseA.event, 9) + pad(newA.event, 8) + newB.event);
console.log('遗物    ' + pad(totalA.relic, 9) + pad(reuseA.relic, 9) + pad(newA.relic, 8) + newB.relic);
console.log('卡牌    ' + pad(totalA.card, 9) + pad(reuseA.card, 9) + pad(newA.card, 8) + newB.card);
console.log('字数    ' + pad('—', 9) + pad('—', 9) + pad(newA.chars, 8) + newB.chars);

fs.writeFileSync(path.join(ROOT, 'tools', 'content_gap.json'), JSON.stringify(result, null, 2));
console.log('\n已写出 tools/content_gap.json');
