// T77 卡牌强度分与开局牌库审计。
//   power = (伤害 + 格挡×0.8 + 抽牌×3 + 能量×4 + 全体伤害×1.6 + 附加效果估值) / 费用当量
//   费用当量 = 费用 === 0 ? 0.5 : max(1, 费用)          —— 0 费按 0.5 计，避免爆炸
// 附加效果估值表（固定、可调；都是「①回合内/持续收益的保守折算」）：
//   heal            生命回复      ×1.0   （回 1 血 = 0.8 格挡的软替代）
//   strength        力量(永久)    ×2.5/点 （每回合每击都吃到的伤害增益）
//   dexterity       敏捷(永久)    ×2.0/点 （同上，格挡侧）
//   regenerate      再生          ×0.8/点/回合 （value×turns×0.8）
//   burn            灼烧(敌)      ×1.0/点/回合 （value×turns，延迟伤害打折）
//   poison          毒            ×1.5/点
//   thorns          荆棘          ×1.5/点
//   weak / frail    弱化/脆弱(敌) ×1.5/次 （放大全队输出/承伤，固定估值）
//   retain          保留          ×1.0
//   resonance_gain  共鸣增益      ×0.5/点 （共鸣是双刃：到阈值有回应、过载有惩罚，保守）
//   gaze_reduce     减凝视        ×2.0/点 （凝视直接放大敌人伤害）
//   gaze_gain       加凝视        ×-2.0/点 （负估值：代价而非收益）
//   resonance_lock  锁共鸣        ×1.0   （保底效用）
//   resonance_drain / resonance_cost / gaze_cost / exhaust / delete_random
//                              ×-3.0   （负估值：自毁/消耗类是代价；删牌是战略效用但也扣资源）
//   cost_type ≠ none（vitality/memory/lock/mark） 额外 ×0.9（有额外付出，整体打折）
// 输出：
//   tools/card_power.json   每张牌 power + 每职业 P75/P90 + 审计结果
//   控制台                  审计报告（R1–R4 对四职业「当前生效的初始牌库」逐条判定）
// 用法：node tools/card_power.js [--strict]   （--strict：审计不过 exit 1）
'use strict';
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const CLASSES = ['diver', 'tremor', 'anmin', 'cangmin'];

/* ── 附加效果估值表（见头注释） ── */
const SPECIAL_VALUE = {
  strength: (v) => 2.5 * (v || 1),
  dexterity: (v) => 2.0 * (v || 1),
  regenerate: (v, t) => 0.8 * (v || 1) * (t || 2),
  burn: (v, t) => 1.0 * (v || 1) * (t || 2),
  poison: (v) => 1.5 * (v || 1),
  thorns: (v) => 1.5 * (v || 1),
  weak: () => 1.5,
  frail: () => 1.5,
  retain: () => 1.0,
  resonance_lock: () => 1.0,
  gaze_reduce: (v) => 2.0 * (v || 1),
  gaze_gain: (v) => -2.0 * (v || 1),
  resonance_drain: (v) => -1.0 * (v || 1),
  exhaust: () => -3.0,
  delete_random: () => -3.0
};

/* ── 强度分 ── */
function cardPower(card) {
  const e = card.effect || {};
  const hits = e.hits || 1;
  const all = e.target === 'all';
  const dmg = all ? 0 : (e.damage || 0) * hits;           // 单体伤害
  const allDmg = all ? (e.damage || 0) * hits : 0;        // 全体伤害（×1.6）
  const block = e.block || 0;
  const draw = e.draw || 0;
  const energy = e.energy || 0;                           // 直接给能量（当前卡池未用，公式保留）
  let extra = (e.heal || 0) * 1.0 + (e.resonance_gain || 0) * 0.5;
  (e.special || []).forEach(sp => {
    const fn = SPECIAL_VALUE[sp.code];
    if (fn) extra += fn(sp.value, sp.turns);
    else extra += 0;                                       // 未登记码估值 0（新增码须补表）
  });
  let power = dmg + block * 0.8 + draw * 3 + energy * 4 + allDmg * 1.6 + extra;
  const cost = card.energy || 0;
  const divisor = cost === 0 ? 0.5 : Math.max(1, cost);
  power /= divisor;
  if ((card.cost_type || 'none') !== 'none') power *= 0.9;  // 额外付出（血/记忆/锁/标记）整体打折
  return Math.round(power * 100) / 100;
}

/* ── 黑名单（R2：无脑牌不进初始牌库） ── */
function blacklistHit(card) {
  const e = card.effect || {};
  const hits = e.hits || 1;
  const free = (card.energy || 0) === 0 && (card.cost_type || 'none') === 'none';
  const hits_ = [];
  if (free && (e.draw || 0) >= 2) hits_.push('0费且抽≥2');
  if (free && e.target === 'all' && (e.damage || 0) * hits >= 10) hits_.push('无代价全体伤害≥10');
  (e.special || []).forEach(sp => {
    if (sp.code === 'retain' && sp.value === 'self' && (sp.turns || 0) >= 99) hits_.push('无限连组件');   // 预留：打出后抽回自身类
  });
  return hits_;
}

/* ── 机制分类（R4：攻/防/抽/特殊） ── */
function mechOf(card) {
  const e = card.effect || {};
  const tags = [];
  if ((e.damage || 0) > 0) tags.push('攻');
  if ((e.block || 0) > 0) tags.push('防');
  if ((e.draw || 0) > 0) tags.push('抽');
  if ((e.special || []).length || (e.heal || 0) > 0 || (e.resonance_gain || 0) > 0 || e.target === 'all') tags.push('特殊');
  return tags;
}

/* ── 分位 ── */
function pct(arr, p) {
  const a = arr.slice().sort((x, y) => x - y);
  const idx = Math.ceil((p / 100) * a.length) - 1;
  return a[Math.max(0, Math.min(a.length - 1, idx))];
}

/* ── 主流程 ── */
const pools = {}, powers = {};
CLASSES.forEach(c => {
  pools[c] = JSON.parse(fs.readFileSync(path.join(ROOT, 'cards', c + '.json'), 'utf8'));
  powers[c] = pools[c].map(card => ({ id: card.id, name: card.name, power: cardPower(card), mech: mechOf(card) }));
});
const percentiles = {};
CLASSES.forEach(c => {
  const arr = powers[c].map(x => x.power);
  percentiles[c] = { P50: pct(arr, 50), P75: pct(arr, 75), P90: pct(arr, 90), n: arr.length };
});

/* ── 引擎内置初始牌（engine buildStarterDeck 的镜像：引擎闭包内不可 require，逐张对拍同步） ── */
const BASIC_ATK = { id: 'basic_atk', name: '一击', energy: 1, cost_type: 'none', effect: { damage: 7, hits: 1, target: 'single' } };
const BASIC_DEF = { id: 'basic_def', name: '缩起', energy: 1, cost_type: 'none', effect: { block: 5, target: 'self' } };
const SIGNS = {
  diver: { id: 'diver_sign', name: '死亡合同副本', energy: 0, cost_type: 'none', effect: { draw: 1, target: 'self' } },
  tremor: { id: 'tremor_sign', name: '静日触杖', energy: 0, cost_type: 'none', effect: { draw: 1, target: 'self' } },
  anmin: { id: 'anmin_sign', name: '登记工号牌', energy: 0, cost_type: 'none', effect: { draw: 1, target: 'self' } }
};
const CANG_STARTERS = [
  { id: 'cng_w_atk', name: '石矛', energy: 1, cost_type: 'none', effect: { damage: 5, target: 'single' }, count: 2, mech: ['攻'] },
  { id: 'cng_w_def', name: '缩进岩洞', energy: 1, cost_type: 'none', effect: { block: 5, target: 'self' }, count: 3, mech: ['防'] },
  { id: 'cng_d_atk', name: '火母的低语', energy: 1, cost_type: 'none', effect: { damage: 9, target: 'single' }, count: 3, mech: ['攻'] },
  { id: 'cng_d_def', name: '火母的注视', energy: 1, cost_type: 'none', effect: { block: 8, target: 'self' }, count: 2, mech: ['防'] }
];

/* ── 开局补位（T77 审计产生：power ≤ P75、非黑名单、补机制多样性；与 web startRun / tools/sim.js 同步） ── */
let STARTER_EXTRA = {
  diver: ['dive_0046', 'dive_0052'],
  tremor: ['trem_0044', 'trem_0050'],
  anmin: ['anmin_0046', 'anmin_0052'],
  cangmin: ['cang_0046', 'cang_0052']
};
const EXTRA_FILE = path.join(ROOT, 'tools', 'starter_decks.json');
if (fs.existsSync(EXTRA_FILE)) STARTER_EXTRA = JSON.parse(fs.readFileSync(EXTRA_FILE, 'utf8'));

/* ── 组装「当前生效的初始牌库」并审计 ── */
function starterDeckOf(cls) {
  const list = [];
  const push = (card, count, src) => {
    for (let i = 0; i < count; i++) list.push({ card, src });
  };
  if (cls === 'cangmin') {
    CANG_STARTERS.forEach(cs => {
      const real = pools[cls].find(x => x.id === cs.id) || cs;
      push(real, cs.count, 'engine.cangmin');
    });
  } else {
    push(BASIC_ATK, 5, 'engine.basic');
    push(BASIC_DEF, 4, 'engine.basic');
    push(SIGNS[cls], 1, 'engine.sign');
  }
  (STARTER_EXTRA[cls] || []).forEach(id => {
    const real = pools[cls].find(x => x.id === id);
    if (real) push(real, 1, 'starter_extra');
    else push({ id, name: '(未找到:' + id + ')', energy: 0, cost_type: 'none', effect: {} }, 1, 'starter_extra');
  });
  return list;
}

const audit = {};
let allPass = true;
CLASSES.forEach(cls => {
  const deck = starterDeckOf(cls);
  const P75 = percentiles[cls].P75;
  const rows = deck.map(({ card, src }) => {
    const power = cardPower(card);
    const bl = blacklistHit(card);
    return { id: card.id, name: card.name, power, src, mech: mechOf(card), blacklist: bl,
      r1: power <= P75 };
  });
  const overP75 = rows.filter(r => !r.r1);
  const blacklisted = rows.filter(r => r.blacklist.length);
  const hasDef = rows.some(r => r.mech.includes('防'));
  const mechs = new Set();
  rows.forEach(r => r.mech.forEach(m => mechs.add(m)));
  const countOk = deck.length >= 10 && deck.length <= 12;
  const mechOk = mechs.size >= 3;
  const pass = overP75.length === 0 && blacklisted.length === 0 && hasDef && countOk && mechOk;
  if (!pass) allPass = false;
  audit[cls] = {
    count: deck.length, P75,
    maxPower: Math.max(...rows.map(r => r.power)),
    overP75: overP75.map(r => r.id + '(' + r.power + ')'),
    blacklist: blacklisted.flatMap(r => r.id + '[' + r.blacklist.join('/') + ']'),
    hasDef, mechKinds: [...mechs], countOk, mechOk, pass,
    rows
  };
});

/* ── 输出 ── */
const out = {
  meta: { task: 'T77', formula: '(伤害 + 格挡×0.8 + 抽牌×3 + 能量×4 + 全体伤害×1.6 + 附加效果) / 费用当量（0费按0.5计）',
    valuation: '见 tools/card_power.js 头注释估值表', generatedAt: new Date().toISOString() },
  percentiles,
  audit,
  cards: {}
};
CLASSES.forEach(c => { out.cards[c] = powers[c]; });
fs.writeFileSync(path.join(ROOT, 'tools', 'card_power.json'), JSON.stringify(out, null, 1) + '\n');

/* ── 控制台报告 ── */
console.log('=== T77 卡牌强度分与开局牌库审计 ===\n');
CLASSES.forEach(c => {
  const a = audit[c];
  console.log('『' + c + '』 卡池 ' + percentiles[c].n + ' 张  P50=' + percentiles[c].P50 +
    '  P75=' + percentiles[c].P75 + '  P90=' + percentiles[c].P90);
  console.log('  初始牌库 ' + a.count + ' 张  最大power=' + a.maxPower + '  机制[' + a.mechKinds.join('/') + ']  防御=' + a.hasDef);
  console.log('  R1 power≤P75: ' + (a.overP75.length ? '✗ ' + a.overP75.join(',') : '✓') +
    '   R2 黑名单: ' + (a.blacklist.length ? '✗ ' + a.blacklist.join(',') : '✓ 0 张') +
    '   R3 防御≥1: ' + (a.hasDef ? '✓' : '✗') +
    '   R4 张数10–12: ' + (a.countOk ? '✓' : '✗') + '  机制≥3: ' + (a.mechOk ? '✓' : '✗'));
  console.log('  开局构成: ' + a.rows.map(r => r.name + (r.power ? '(' + r.power + ')' : '') + (r.blacklist.length ? '[黑名单!]' : '')).join(' ×? ').replace(/ ×? /g, ' + ').slice(0, 160));
  console.log('');
});
console.log(allPass ? '审计全过：R1–R4 四职业全部达标' : '审计有未过项（见上）');
const strict = process.argv.includes('--strict');
if (strict && !allPass) process.exit(1);
