// 数值模拟器：简单 AI 自动跑完整局，统计通关率/死亡层/各层通过率/剩余血量。
// 用法：node tools/sim.js --class diver --runs 200
// 只 import engine/core.js 与数据文件，不修改引擎。
'use strict';
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

/* ───────── 参数 ───────── */
const args = {};
process.argv.slice(2).forEach((a, i, arr) => { if (a.startsWith('--')) args[a.slice(2)] = arr[i + 1]; });
const CLASS_ID = args.class || 'diver';
const RUNS = parseInt(args.runs || '200', 10);
const SEED0 = parseInt(args.seed || '12345', 10);
const SMART = args.smart === '1';

/* ───────── 工具 ───────── */
function weightedCards(rng, n) {
  const pool = RAW[CLASS_ID].filter(c => c.rarity !== 'special');
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

/* ───────── 战斗 AI：能出就出，优先攻击，打第一个活着的敌人 ───────── */
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
    // 出牌阶段（0 费抽牌可能无限循环，限每回合最多出 12 张）
    let plays = 0;
    let progress = plays < 12;
    while (progress && !C.over) {
      progress = false;
      // smart：残血且敌方意图含攻击时，先打格挡（最多 2 张）
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
        const t = C.enemies.findIndex(e => !e.dead);   // 打第一个活着的敌人
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

/* ───────── 单局 ───────── */
function playRun(seed) {
  const rng = RA.makeRng(seed);
  const run = RA.newRun(CLASS_ID, { rng });
  run._seed = seed;
  run._playedIds = new Set();
  // T77 开局牌库审计：与前端 startRun 同步——固定补位 2 张（总 12 张），不再随机抽 6 张池牌。
  // 三处同步：tools/starter_decks.json / web startRun / 此处。
  const STARTER_EXTRA = {
    diver: ['dive_0053', 'dive_0019'],
    tremor: ['trem_0044', 'trem_0050'],
    anmin: ['anm_0006', 'anm_0042'],
    cangmin: ['cng_0016', 'cng_0032']
  };
  (STARTER_EXTRA[CLASS_ID] || []).forEach((id, i) => {
    const c = RAW[CLASS_ID].find(x => x.id === id);
    if (c) run.deck.push(Object.assign({}, c, { uid: 'p' + i }));
  });
  run.stats = { battles: 0 };
  const hpAfterLayer = [];

  for (let depth = 1; depth <= 8; depth++) {
    run.depth = depth;
    run.row = -1;
    run.col = 0;
    const layer = RAW.layers.layers[depth - 1];
    const rows = layer.rows;

    for (let ri = 0; ri < rows.length; ri++) {
      run.row = ri;
      // 岔路选择：残血时优先事件/营火/商店，否则均匀随机
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
        // DLC 职业主局仍走基础敌人池（DLC 敌人包属于回响短局）
        const candidates = RAW.enemies.filter(x => x.layer === depth && x.tier === tier);
        if (!candidates.length) return { dead: true, layer: depth, reason: 'no-enemy', playedIds: run._playedIds };
        const picks = [];
        const n = tier === 'normal' ? (rng() < 0.35 ? 1 : 2) : 1;
        const bag = candidates.slice();
        while (picks.length < n && bag.length) picks.push(bag.splice(Math.floor(rng() * bag.length), 1)[0]);
        run._pendingEnemies = picks;
        run.stats.battles++;
        const r = aiCombat(run);
        if (r.result !== 'win') return { dead: true, layer: depth, hpAfterLayer, playedIds: run._playedIds };
        // 战斗奖励（与前端一致）
        if (type === 'boss') {
          pickRelics(rng, 1, new Set(run.relics.map(x => x.id))).forEach(x => run.relics.push(x));
          if (depth < 8) run.gold += randInt(rng, 50, 80);
        } else if (type === 'elite') {
          if (run.deck.length < 32 || rng() < 0.5) {
            run.deck.push(Object.assign({}, weightedCards(rng, 1)[0], { uid: 'e' + run.deck.length }));
          }
          pickRelics(rng, 1, new Set(run.relics.map(x => x.id))).forEach(x => run.relics.push(x));
        } else {
          if (run.deck.length < 32 || rng() < 0.5) {
            run.deck.push(Object.assign({}, weightedCards(rng, 1)[0], { uid: 'c' + run.deck.length }));
          }
        }
      } else if (type === 'event') {
        // D1/D8 没有专属事件，回退到最近的层
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
        if (r.gold) run.gold += r.gold;
        if (r.maxhp) run.maxHp = Math.max(1, run.maxHp + r.maxhp);
        if (r.card_reward) {
          const c = weightedCards(rng, 3)[0];
          run.deck.push(Object.assign({}, c, { uid: 'v' + run.deck.length }));
        }
        if (r.relic) {
          const rel = pickRelics(rng, 1, new Set(run.relics.map(x => x.id)))[0];
          if (rel) run.relics.push(rel);
        }
        if (run.hp <= 0) return { dead: true, layer: depth, hpAfterLayer, playedIds: run._playedIds };
      } else if (type === 'campfire') {
        if (run.classId === 'cangmin') run.clarity = Math.min(run.clarityMax || 5, run.clarity + 1); // 守夜养神
        // AI：血量低于 65% 就休息，否则升级一张随机卡
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
        // AI：缺血先买合剂（60 金，回 25%），否则买得起最便宜的卡就买一张
        if (run.hp < run.maxHp * 0.6 && run.gold >= 60) {
          run.gold -= 60;
          run.hp = Math.min(run.maxHp, run.hp + Math.floor(run.maxHp * 0.35));
        } else {
          const stock = weightedCards(rng, 3).map(c => ({
            c,
            price: c.rarity === 'rare' ? 175 : c.rarity === 'uncommon' ? 92 : 50
          })).sort((a, b) => a.price - b.price);
          const buy = stock.find(s => run.gold >= s.price && (run.deck.length < 32 || rng() < 0.5));
          if (buy) {
            run.gold -= buy.price;
            run.deck.push(Object.assign({}, buy.c, { uid: 's' + run.deck.length }));
          }
        }
      }
    }
    hpAfterLayer.push(run.hp);
    if (run.hp <= 0) return { dead: true, layer: depth, hpAfterLayer, playedIds: run._playedIds };
  }
  return { dead: false, layer: 8, hpAfterLayer, playedIds: run._playedIds };
}

/* ───────── 汇总 ───────── */
const arrival = new Array(9).fill(0);   // 到达第 i 层的局数
const cleared = new Array(9).fill(0);   // 通过第 i 层（到达 i+1）的局数
const hpSum = new Array(9).fill(0);     // 通过第 i 层后的总血量
const deathLayer = {};
let wins = 0, deaths = 0, deathLayerSum = 0;
const cardStat = {};                    // 每卡：被 AI 打出过的局数 / 其中获胜局数

const runTimes = [];
for (let i = 0; i < RUNS; i++) {
  const t0 = Date.now();
  const r = playRun(SEED0 + i * 7919);
  const ms = Date.now() - t0;
  if (ms > 2000) console.error('!! 慢局 seed=' + (SEED0 + i * 7919) + ' 用时 ' + ms + 'ms');
  runTimes.push({ seed: SEED0 + i * 7919, ms: ms });
  (r.playedIds || []).forEach(id => {
    const s = cardStat[id] || (cardStat[id] = { n: 0, w: 0 });
    s.n++;
    if (!r.dead) s.w++;
  });
  for (let d = 1; d <= 8; d++) {
    if (d <= r.layer) arrival[d]++;
    if (d < r.layer || (!r.dead && d === 8)) cleared[d]++;
  }
  r.hpAfterLayer.forEach((hp, idx) => { hpSum[idx + 1] += hp; });
  if (r.dead) {
    deaths++;
    deathLayer[r.layer] = (deathLayer[r.layer] || 0) + 1;
    deathLayerSum += r.layer;
  } else wins++;
}

console.log('=== 模拟：' + CLASS_ID + ' × ' + RUNS + ' 局（seed0=' + SEED0 + (SMART ? '，会格挡 AI' : '') + '）===');
console.log('通关率: ' + (wins / RUNS * 100).toFixed(1) + '%');
console.log('平均死亡层: ' + (deaths ? (deathLayerSum / deaths).toFixed(2) : '—'));
console.log('');
console.log('层级   到达   通过   通过率   存活率   平均过层血量');
for (let d = 1; d <= 8; d++) {
  const passRate = arrival[d] ? (cleared[d] / arrival[d] * 100).toFixed(0) + '%' : '—';
  const survRate = (cleared[d] / RUNS * 100).toFixed(1) + '%';
  const hpAvg = cleared[d] ? Math.round(hpSum[d] / cleared[d]) : '—';
  console.log(
    'D' + d + '    ' + String(arrival[d]).padEnd(6) + String(cleared[d]).padEnd(6) +
    String(passRate).padEnd(8) + String(survRate).padEnd(8) + hpAvg
  );
}
console.log('');
console.log('死亡层分布: ' + JSON.stringify(deathLayer));
// 每卡使用率：AI 打出过该卡的局占比；Δ胜率 = 打出该卡的局胜率 - 总胜率（样本少的卡噪声大）
console.log('');
console.log('每卡使用率（按使用率升序）:');
const overallWr = wins / RUNS * 100;
const cardRows = Object.keys(cardStat).map(id => {
  const def = RAW[CLASS_ID].find(c => c.id === id) || {};
  const s = cardStat[id];
  return { id, name: def.name || id, rarity: def.rarity || '?', n: s.n,
           usage: s.n / RUNS * 100, wr: s.w / s.n * 100, delta: s.w / s.n * 100 - overallWr };
}).sort((a, b) => a.usage - b.usage);
cardRows.forEach(r => {
  console.log('  ' + r.name + '  用' + r.n + '局  使用率' + r.usage.toFixed(1) + '%  胜率' + r.wr.toFixed(0) + '%  Δ' + (r.delta >= 0 ? '+' : '') + r.delta.toFixed(0) + 'pp  ' + r.id);
});
const never = RAW[CLASS_ID].filter(c => c.rarity !== 'special' && !cardStat[c.id]);
if (never.length) {
  console.log('  ——整场从未被打出：' + never.map(c => c.name + '(' + c.id + ')').join('、'));
}
if (process.env.SIM_PROFILE) {
  const slow = runTimes.slice().sort((a, b) => b.ms - a.ms).slice(0, 5);
  console.log('最慢 5 局: ' + JSON.stringify(slow) + '（用 SIM_PROFILE=1 开启）');
}
