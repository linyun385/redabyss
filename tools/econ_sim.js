// T49 经济与进度曲线模拟。
// 战斗/对局逻辑逐字复用 tools/sim.js 的 aiCombat 与 playRun（见文末「同步断言」——
// 若两文件的对局函数文本不一致会报错退出，防止两套 AI 漂移）。
// 在对局循环里加了经济埋点：每层的 金币/遗物数/卡组规模/商店访问与消费。
//
// 用法：
//   node tools/econ_sim.js                      # 4 职业 × 500 局（seed0=12345）
//   node tools/econ_sim.js --runs 300 --class diver --out tools/econ_curve.json
//   node tools/econ_sim.js --seed 777
'use strict';
const fs = require('fs');
const path = require('path');
const ROOT = path.join(__dirname, '..');
const RA = require(path.join(ROOT, 'engine', 'core.js'));

const RAW = {
  diver: require(path.join(ROOT, 'cards', 'diver.json')),
  tremor: require(path.join(ROOT, 'cards', 'tremor.json')),
  anmin: require(path.join(ROOT, 'cards', 'anmin.json')),
  cangmin: require(path.join(ROOT, 'cards', 'cangmin.json')),
  enemies: require(path.join(ROOT, 'enemies', 'all.json')),
  relics: require(path.join(ROOT, 'relics', 'all.json')),
  events: require(path.join(ROOT, 'events', 'all.json')),
  layers: require(path.join(ROOT, 'layers', 'layers.json'))
};
if (!Array.isArray(RAW.diver)) RAW.diver = RAW.diver.cards;
if (!Array.isArray(RAW.tremor)) RAW.tremor = RAW.tremor.cards;
if (!Array.isArray(RAW.anmin)) RAW.anmin = RAW.anmin.cards;
if (!Array.isArray(RAW.cangmin)) RAW.cangmin = RAW.cangmin.cards;
if (!Array.isArray(RAW.enemies)) RAW.enemies = RAW.enemies.enemies;
if (!Array.isArray(RAW.relics)) RAW.relics = RAW.relics.relics;
if (!Array.isArray(RAW.events)) RAW.events = RAW.events.events;

const args = {};
process.argv.slice(2).forEach((a, i, arr) => { if (a.startsWith('--')) args[a.slice(2)] = arr[i + 1]; });
const RUNS = parseInt(args.runs || '500', 10);
const SEED0 = parseInt(args.seed || '12345', 10);
const ONLY = args.class || null;
const OUT = args.out || path.join(ROOT, 'tools', 'econ_curve.json');
const SMART = args.smart === '1';

/* ───────── 工具（与 sim.js 一致） ───────── */
function weightedCards(rng, n) {
  const pool = RAW[CLASS_ID] ? RAW[CLASS_ID].filter(c => c.rarity !== 'special') : [];
  const weight = { common: 6, uncommon: 3, rare: 1 };
  const out = [];
  const bag = pool.slice();
  while (out.length < n && bag.length) {
    let total = 0;
    bag.forEach(c => { total += weight[c.rarity] || 1; });
    let roll = rng() * total;
    let pick = bag[0];
    for (const c of bag) { roll -= weight[c.rarity] || 1; if (roll <= 0) { pick = c; break; } }
    out.push(pick);
    bag.splice(bag.indexOf(pick), 1);
  }
  return out;
}
function pickRelics(rng, n, owned) {
  const bag = RAW.relics.filter(r => !owned.has(r.id));
  const out = [];
  while (out.length < n && bag.length) out.push(bag.splice(Math.floor(rng() * bag.length), 1)[0]);
  return out;
}
function randInt(rng, a, b) { return a + Math.floor(rng() * (b - a + 1)); }

/* ───────── 战斗 AI（与 sim.js 逐字一致，勿在此改动——改动请同步 sim.js） ───────── */
function aiCombat(run) {
  let C = RA.startCombat(run, run._pendingEnemies);
  // 苍民：开局自动入梦（清醒度允许时）
  if (run.classId === 'cangmin' && C.world === 'wake' && run.clarity > 0 && !C.dreamLocked) {
    RA.switchWorld(C, 'dream');
  }
  run._pendingEnemies = null;
  const t0 = Date.now();
  let guard = 0;
  while (!C.over && guard++ < 80) {
    if (Date.now() - t0 > 3000) {
      throw new Error('战斗卡死 seed=' + run._seed + ' depth=' + run.depth +
        ' 敌人=' + C.enemies.map(e => e.name + ':' + e.hp).join(',') +
        ' 回合=' + C.turn + ' 手牌=' + C.hand.map(c => c.name).join('/'));
    }
    let plays = 0;
    let progress = plays < 12;
    while (progress && !C.over) {
      progress = false;
      let blocksFirst = 0;
      if (SMART && run.hp <= run.maxHp * 0.5) {
        const incoming = C.enemies.filter(e => !e.dead)
          .reduce((sum, e) => sum + (e.intent && e.intent.type === 'attack' ? (e.intent.value || 0) * (e.intent.times || 1) : 0), 0);
        if (incoming >= 6) blocksFirst = 2;
      }
      const order = C.hand
        .map((c, i) => i)
        .sort((a, b) => {
          const ca = C.hand[a], cb = C.hand[b];
          const isBlockA = (ca.effect.block || 0) > 0 && ca.type !== 'attack';
          const isBlockB = (cb.effect.block || 0) > 0 && cb.type !== 'attack';
          if (blocksFirst > 0 && isBlockA !== isBlockB) return isBlockA ? -1 : 1;
          const ta = ca.type === 'attack' ? 0 : 1, tb = cb.type === 'attack' ? 0 : 1;
          if (ta !== tb) return ta - tb;
          return (cb.effect.damage || 0) - (ca.effect.damage || 0);
        });
      for (const i of order) {
        const t = C.enemies.findIndex(e => !e.dead);
        if (t < 0) break;
        const played = C.hand[i];
        const r = RA.playCard(C, i, t);
        if (r.ok) {
          if (played.id) run._playedIds.add(played.id);
          if (blocksFirst > 0 && (played.effect.block || 0) > 0 && played.type !== 'attack') blocksFirst--;
          progress = ++plays < 12; break;
        }
      }
    }
    if (C.over) break;
    RA.endTurn(C);
  }
  const result = C.result;
  const hpLeft = run.hp;
  RA.finishCombat(C);
  return { result, hpLeft };
}

/* ───────── 单局（对局骨架与 sim.js 一致；商店/奖励段加经济埋点） ───────── */
let CLASS_ID = 'diver';
function playRun(seed, econ) {
  const rng = RA.makeRng(seed);
  const run = RA.newRun(CLASS_ID, { rng });
  run._seed = seed;
  run._playedIds = new Set();
  const pool = RAW[CLASS_ID].filter(c => c.rarity !== 'special').slice();
  for (let i = 0; i < 6 && pool.length; i++) {
    const j = Math.floor(rng() * pool.length);
    run.deck.push(Object.assign({}, pool.splice(j, 1)[0], { uid: 'p' + i }));
  }
  run.stats = { battles: 0 };
  const hpAfterLayer = [];

  for (let depth = 1; depth <= 8; depth++) {
    run.depth = depth;
    run.row = -1;
    run.col = 0;
    econ.layer(depth, 'goldStart', run.gold);
    const layer = RAW.layers.layers[depth - 1];
    const rows = layer.rows;

    for (let ri = 0; ri < rows.length; ri++) {
      run.row = ri;
      const row = rows[ri];
      let cols = row.map((_, i) => i);
      if (run.hp < run.maxHp * 0.65) {
        const safe = cols.filter(c => ['event', 'campfire', 'shop'].includes(row[c].type));
        if (safe.length) cols = safe;
      }
      const ci = cols[Math.floor(rng() * cols.length)];
      run.col = ci;
      const type = row[ci].type;

      if (type === 'combat' || type === 'elite' || type === 'boss') {
        const tier = type === 'elite' ? 'elite' : type === 'boss' ? 'boss' : 'normal';
        const candidates = RAW.enemies.filter(x => x.layer === depth && x.tier === tier);
        if (!candidates.length) return { dead: true, layer: depth, hpAfterLayer };
        const picks = [];
        const n = tier === 'normal' ? (rng() < 0.35 ? 1 : 2) : 1;
        const bag = candidates.slice();
        while (picks.length < n && bag.length) picks.push(bag.splice(Math.floor(rng() * bag.length), 1)[0]);
        run._pendingEnemies = picks;
        run.stats.battles++;
        const r = aiCombat(run);
        if (r.result !== 'win') return { dead: true, layer: depth, hpAfterLayer };
        if (type === 'boss') {
          pickRelics(rng, 1, new Set(run.relics.map(x => x.id))).forEach(x => { run.relics.push(x); econ.layer(depth, 'relicGain', 1); });
          if (depth < 8) run.gold += randInt(rng, 50, 80);
        } else if (type === 'elite') {
          if (run.deck.length < 32 || rng() < 0.5) {
            run.deck.push(Object.assign({}, weightedCards(rng, 1)[0], { uid: 'e' + run.deck.length }));
          }
          pickRelics(rng, 1, new Set(run.relics.map(x => x.id))).forEach(x => { run.relics.push(x); econ.layer(depth, 'relicGain', 1); });
        } else {
          if (run.deck.length < 32 || rng() < 0.5) {
            run.deck.push(Object.assign({}, weightedCards(rng, 1)[0], { uid: 'c' + run.deck.length }));
          }
        }
      } else if (type === 'event') {
        let evs = RAW.events.filter(x => x.layer === depth);
        if (!evs.length) {
          for (let off = 1; off <= 8 && !evs.length; off++) {
            evs = RAW.events.filter(x => x.layer === depth - off || x.layer === depth + off);
          }
        }
        const ev = evs[Math.floor(rng() * evs.length)];
        const opt = ev.options[Math.floor(rng() * ev.options.length)];
        const r = opt.result || {};
        if (r.heal) run.hp = Math.min(run.maxHp, run.hp + r.heal);
        if (r.damage) run.hp -= r.damage;
        if (r.gaze) run.gaze = Math.max(0, run.gaze + r.gaze);
        if (r.gold) { run.gold += r.gold; econ.layer(depth, 'goldGain', r.gold); }
        if (r.maxhp) run.maxHp = Math.max(1, run.maxHp + r.maxhp);
        if (r.card_reward) {
          const c = weightedCards(rng, 3)[0];
          run.deck.push(Object.assign({}, c, { uid: 'v' + run.deck.length }));
        }
        if (r.relic) {
          const rel = pickRelics(rng, 1, new Set(run.relics.map(x => x.id)))[0];
          if (rel) { run.relics.push(rel); econ.layer(depth, 'relicGain', 1); }
        }
        if (run.hp <= 0) return { dead: true, layer: depth, hpAfterLayer };
      } else if (type === 'campfire') {
        if (run.classId === 'cangmin') run.clarity = Math.min(run.clarityMax || 5, run.clarity + 1);
        if (run.hp < run.maxHp * 0.65) {
          run.hp = Math.min(run.maxHp, run.hp + Math.floor(run.maxHp * 0.5));
        } else {
          const ups = run.deck.filter(c => c.upgrade && !c.upgraded);
          if (ups.length) {
            const i = run.deck.indexOf(ups[Math.floor(rng() * ups.length)]);
            run.deck[i] = RA.upgradeCard(run.deck[i]);
          }
        }
      } else if (type === 'shop') {
        econ.layer(depth, 'shopVisit', 1);
        // 商店库存与价格（与前端 showShop 的定价一致：卡 50/92/175，遗物 120-160/250-320，合剂 60，删牌 75）
        if (run.hp < run.maxHp * 0.6 && run.gold >= 60) {
          run.gold -= 60;
          run.hp = Math.min(run.maxHp, run.hp + Math.floor(run.maxHp * 0.35));
          econ.layer(depth, 'shopBuy', 1);
        } else {
          const stock = weightedCards(rng, 3).map(c => ({
            c,
            price: c.rarity === 'rare' ? 175 : c.rarity === 'uncommon' ? 92 : 50
          })).sort((a, b) => a.price - b.price);
          const buy = stock.find(s => run.gold >= s.price && (run.deck.length < 32 || rng() < 0.5));
          if (buy) {
            run.gold -= buy.price;
            econ.layer(depth, 'shopBuy', 1);
            econ.layer(depth, 'goldSpend', buy.price);
            run.deck.push(Object.assign({}, buy.c, { uid: 's' + run.deck.length }));
          } else {
            const cheapest = stock.slice().sort((a, b) => a.price - b.price)[0];
            if (run.gold < cheapest.price) econ.layer(depth, 'shopCannotAfford', 1);
            else econ.layer(depth, 'shopFullDeck', 1);
          }
        }
      }
    }
    hpAfterLayer.push(run.hp);
    econ.layer(depth, 'goldEnd', run.gold);
    econ.layer(depth, 'relicsEnd', run.relics.length);
    econ.layer(depth, 'deckEnd', run.deck.length);
    if (run.hp <= 0) return { dead: true, layer: depth, hpAfterLayer };
  }
  return { dead: false, layer: 8, hpAfterLayer };
}

/* ───────── 同步断言：对局函数必须与 sim.js 逐字一致 ───────── */
(function syncAssert() {
  const simSrc = fs.readFileSync(path.join(ROOT, 'tools', 'sim.js'), 'utf8');
  const mySrc = fs.readFileSync(__filename, 'utf8');
  function grab(src, startMark, endMark) {
    const a = src.indexOf(startMark);
    const b = src.indexOf(endMark, a);
    if (a < 0 || b < 0) return null;
    return src.slice(a, b).replace(/\s+/g, ' ').trim();
  }
  // 对比战斗 AI 函数体（不含 _playedIds 埋点行——埋点行在对比前剔除）
  const strip = t => t
    .replace(/if \(played\.id\) run\._playedIds\.add\(played\.id\);/g, '')
    .replace(/\/\/[^\n]*/g, '')          // 注释不参与比对（代码漂移才报错）
    .replace(/\/\*[\s\S]*?\*\//g, '')
    .replace(/\s+/g, ' ').trim();
  const a = strip(grab(simSrc, 'function aiCombat', '/* ───────── 单局'));
  const b = strip(grab(mySrc, 'function aiCombat', '/* ───────── 单局'));
  if (!a || !b || a !== b) {
    console.error('断言失败：econ_sim.js 的 aiCombat 与 sim.js 不一致——请以 sim.js 为准同步，勿让两套 AI 漂移。');
    process.exit(1);
  }
  console.log('同步断言通过：aiCombat 与 sim.js 逐字一致（埋点行除外）');
})();

/* ───────── 主循环 ──��──────── */
const CLASSES = ONLY ? [ONLY] : ['diver', 'tremor', 'anmin', 'cangmin'];
const curve = {};
const t0 = Date.now();
for (const cls of CLASSES) {
  CLASS_ID = cls;
  const rec = { runs: RUNS, seed0: SEED0, layers: {} };
  const buckets = {};
  for (let d = 1; d <= 8; d++) buckets[d] = { goldStart: [], goldEnd: [], goldGain: [], goldSpend: [], relicsEnd: [], deckEnd: [], shopVisit: 0, shopBuy: 0, shopCannotAfford: 0, shopFullDeck: 0, relicGain: [], arrived: 0, diedHere: 0 };
  let wins = 0;
  for (let i = 0; i < RUNS; i++) {
    const econ = {
      layer(d, k, v) { const b = buckets[d]; if (!b) return; if (k === 'shopVisit' || k === 'shopBuy' || k === 'shopCannotAfford' || k === 'shopFullDeck') b[k] += v; else b[k].push(v); }
    };
    const r = playRun(SEED0 + i * 7919, econ);
    if (!r.dead) wins++;
    for (let d = 1; d <= 8; d++) {
      const aliveHere = !r.dead || d < r.layer;
      if (aliveHere) buckets[d].arrived++;
      if (r.dead && r.layer === d) buckets[d].diedHere++;
    }
  }
  // 汇总
  function med(a) { if (!a.length) return null; const s = a.slice().sort((x, y) => x - y); const m = Math.floor(s.length / 2); return s.length % 2 ? s[m] : Math.round((s[m - 1] + s[m]) / 2 * 10) / 10; }
  function pct(a, q) { if (!a.length) return null; const s = a.slice().sort((x, y) => x - y); const idx = Math.min(s.length - 1, Math.floor(s.length * q)); return s[idx]; }
  for (let d = 1; d <= 8; d++) {
    const b = buckets[d];
    rec.layers[d] = {
      arrived: b.arrived, diedHere: b.diedHere,
      goldStartMed: med(b.goldStart), goldStartP25: pct(b.goldStart, 0.25), goldStartP75: pct(b.goldStart, 0.75),
      goldEndMed: med(b.goldEnd), goldEndP25: pct(b.goldEnd, 0.25), goldEndP75: pct(b.goldEnd, 0.75),
      goldGainAvg: b.goldGain.length ? +(b.goldGain.reduce((a, c) => a + c, 0) / b.goldGain.length).toFixed(1) : 0,
      goldSpendAvg: b.goldSpend.length ? +(b.goldSpend.reduce((a, c) => a + c, 0) / Math.max(1, b.shopVisit)).toFixed(1) : 0,
      relicsEndMed: med(b.relicsEnd), deckEndMed: med(b.deckEnd),
      shopVisit: b.shopVisit, shopBuy: b.shopBuy,
      shopCannotAfford: b.shopCannotAfford, shopFullDeck: b.shopFullDeck,
      relicGainTotal: b.relicGain.reduce((a, c) => a + c, 0),
      deathLayer: b.diedHere
    };
  }
  rec.winRate = +(wins / RUNS * 100).toFixed(1) + '%';
  curve[cls] = rec;
}
fs.writeFileSync(OUT, JSON.stringify(curve, null, 1), 'utf8');
console.log('完成 ' + (CLASSES.length * RUNS) + ' 局，耗时 ' + ((Date.now() - t0) / 1000).toFixed(1) + 's → ' + OUT);
for (const cls of CLASSES) console.log('  ' + cls + ' 通关率 ' + curve[cls].winRate);
