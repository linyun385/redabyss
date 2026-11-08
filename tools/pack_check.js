// 数据包验收检查器。GLM 每完成一个任务后必须跑它。
// 用法：node tools/pack_check.js [cards|enemies|relics|events|all]
'use strict';
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const VEINS = ['light', 'water', 'heat', 'tremor', 'mineral'];
const BANNED_FLAVOR = ['造成', '获得', '点伤害', '点格挡', '恭喜', '解锁', '成功获得', '系统', '玩家'];
const BOSS_NAMES = ['光蛭母', '震喉', '穹顶之影', '墟蛹'];

let fails = 0, warns = 0;
function ok(msg) { console.log('  ok    ' + msg); }
function fail(msg) { console.log('  FAIL  ' + msg); fails++; }
function warn(msg) { console.log('  warn  ' + msg); warns++; }
function head(t) { console.log('\n=== ' + t + ' ==='); }

function readJson(rel) {
  const p = path.join(ROOT, rel);
  if (!fs.existsSync(p)) return null;
  try {
    return JSON.parse(fs.readFileSync(p, 'utf8'));
  } catch (e) {
    fail(rel + ' JSON 解析失败: ' + e.message);
    return null;
  }
}

function arrOf(v) {
  if (Array.isArray(v)) return v;
  if (v && Array.isArray(v.cards)) return v.cards;
  if (v && Array.isArray(v.enemies)) return v.enemies;
  if (v && Array.isArray(v.relics)) return v.relics;
  if (v && Array.isArray(v.events)) return v.events;
  return null;
}

// ---------- 卡牌 ----------
function checkCards() {
  head('card packs');
  [['cards/diver.json', 'diver', 40], ['cards/tremor.json', 'tremor', 40]].forEach(([rel, cls, want]) => {
    const data = readJson(rel);
    if (!data) { fail(rel + ' 不存在'); return; }
    const cards = arrOf(data);
    if (!cards) { fail(rel + ' 不是数组'); return; }

    if (cards.length < want) fail(rel + ' 至少 ' + want + ' 张，实际 ' + cards.length);
    else if (cards.length > want) warn(rel + ' 共 ' + cards.length + ' 张（基础 ' + want + '，扩充已生效）');
    else ok(rel + ' 共 ' + cards.length + ' 张');

    const ids = new Set(), names = new Set();
    let badFlavor = 0, noFlavor = 0, wrongClass = 0;
    const rarity = { common: 0, uncommon: 0, rare: 0, special: 0 };

    cards.forEach((c, i) => {
      const tag = rel + '[' + i + '] ' + (c.name || '(无名)');
      if (!c.id) fail(tag + ' 缺 id');
      else if (ids.has(c.id)) fail(tag + ' id 重复');
      else ids.add(c.id);

      if (!c.name) fail(tag + ' 缺 name');
      else if (names.has(c.name)) warn(tag + ' 卡名重复');
      else names.add(c.name);

      if (c.class !== cls) wrongClass++;
      if (!c.type) fail(tag + ' 缺 type');
      if (!VEINS.concat(['']).includes((c.veins || [])[0] || '')) { /* 允许空 */ }
      if ((c.veins || []).length > 2) fail(tag + ' 脉标签超过 2 个');
      (c.veins || []).forEach(v => { if (!VEINS.includes(v)) fail(tag + ' 非法脉: ' + v); });
      if (typeof c.energy !== 'number') fail(tag + ' 缺 energy');
      if (!c.effect || typeof c.effect !== 'object') fail(tag + ' 缺 effect');
      if (!c.cost_type) fail(tag + ' 缺 cost_type');
      if (rarity[c.rarity] === undefined) warn(tag + ' 未知 rarity: ' + c.rarity);
      else rarity[c.rarity]++;

      if (!c.flavor) { noFlavor++; }
      else {
        const hit = BANNED_FLAVOR.filter(w => c.flavor.includes(w));
        if (hit.length) { badFlavor++; if (badFlavor <= 5) fail(tag + ' flavor 含禁用词 ' + hit.join(',')); }
      }
    });

    if (wrongClass) fail(rel + ' 有 ' + wrongClass + ' 张 class 不等于 ' + cls);
    if (noFlavor) fail(rel + ' 有 ' + noFlavor + ' 张缺 flavor');
    if (badFlavor) fail(rel + ' 有 ' + badFlavor + ' 张 flavor 含禁用词');
    else ok(rel + ' flavor 全部合规');
    console.log('        rarity: ' + JSON.stringify(rarity));
  });
}

// ---------- 敌人 ----------
function checkEnemies() {
  head('enemy pack');
  const data = readJson('enemies/all.json');
  if (!data) { fail('enemies/all.json 不存在'); return; }
  const list = arrOf(data);
  if (!list) { fail('enemies/all.json 不是数组'); return; }

  if (list.length < 36) fail('敌人至少 36 个，实际 ' + list.length);
  else if (list.length > 36) warn('敌人共 ' + list.length + ' 个（基础 36，扩充已生效）');
  else ok('敌人 36 个');

  const ids = new Set();
  const byLayer = {};
  let badLayer = 0, badHp = 0, noFlavor = 0;

  list.forEach((e, i) => {
    const tag = 'enemy[' + i + '] ' + (e.name || '(无名)');
    if (!e.id) fail(tag + ' 缺 id'); else if (ids.has(e.id)) fail(tag + ' id 重复'); else ids.add(e.id);
    if (!['normal', 'elite', 'boss'].includes(e.tier)) fail(tag + ' tier 非法: ' + e.tier);
    if (typeof e.layer !== 'number' || e.layer < 1 || e.layer > 8) { fail(tag + ' layer 非法: ' + e.layer); badLayer++; }
    else byLayer[e.layer] = (byLayer[e.layer] || 0) + 1;

    // hp 支持 数字 或 "18-24"
    if (typeof e.hp === 'number') { if (e.hp <= 0) badHp++; }
    else if (typeof e.hp === 'string' && /^\d+\s*-\s*\d+$/.test(e.hp.trim())) { /* ok */ }
    else { fail(tag + ' hp 格式非法: ' + JSON.stringify(e.hp)); badHp++; }

    if (!Array.isArray(e.intent_pattern) || e.intent_pattern.length === 0) fail(tag + ' 缺 intent_pattern');
    (e.intent_pattern || []).forEach(it => {
      if (!['attack', 'defend', 'buff', 'debuff'].includes(it.type)) fail(tag + ' 意图类型非法: ' + it.type);
    });
    if (!e.flavor) noFlavor++;
  });

  console.log('        分层: ' + JSON.stringify(byLayer));
  if (noFlavor) fail('有 ' + noFlavor + ' 个敌人缺 flavor'); else ok('敌人 flavor 齐全');

  const bosses = list.filter(e => e.tier === 'boss').map(e => e.name);
  // T48：Boss 允许变体——canonical 4 个必须在位（层 4/5/7/8），变体 Boss 数量不限但层必须在 1..8
  if (bosses.length < 4) fail('Boss 至少 4 个（canonical），实际 ' + bosses.length);
  else {
    const missing = BOSS_NAMES.filter(n => !bosses.includes(n));
    if (missing.length) fail('Boss 名称缺: ' + missing.join(',')); else ok('四个 canonical Boss 名称正确');
    if (bosses.length > 4) ok('另有 ' + (bosses.length - 4) + ' 个 Boss 变体（T48）');
  }
  const bossLayers = list.filter(e => e.tier === 'boss').map(e => e.layer).sort((a, b) => a - b);
  const badVariantLayer = bossLayers.filter(l => ![4, 5, 7, 8].includes(l) && ![1, 2, 3, 6].includes(l));
  if (badVariantLayer.length) fail('Boss 层非法: ' + badVariantLayer.join('/'));
  else if (JSON.stringify([4, 5, 7, 8].filter(l => bossLayers.includes(l))) !== JSON.stringify([4, 5, 7, 8])) fail('canonical Boss 层（4/5/7/8）不齐: ' + bossLayers.join('/'));
  else ok('Boss 层校验通过（canonical 4/5/7/8 + 变体层 1/2/3/6 允许）');
}

// ---------- 遗物 ----------
function checkRelics() {
  head('relic pack');
  const data = readJson('relics/all.json');
  if (!data) { fail('relics/all.json 不存在'); return; }
  const list = arrOf(data);
  if (!list) { fail('relics/all.json 不是数组'); return; }
  if (list.length < 20) fail('遗物至少 20 个，实际 ' + list.length);
  else if (list.length > 20) warn('遗物共 ' + list.length + ' 个（基础 20，扩充已生效）');
  else ok('遗物 20 个');
  const ids = new Set();
  list.forEach((r, i) => {
    const tag = 'relic[' + i + '] ' + (r.name || '(无名)');
    if (!r.id) fail(tag + ' 缺 id'); else if (ids.has(r.id)) fail(tag + ' id 重复'); else ids.add(r.id);
    if (!r.effect_text) fail(tag + ' 缺 effect_text');
    if (!Array.isArray(r.effect_code) || !r.effect_code.length) fail(tag + ' 缺 effect_code');
    (r.effect_code || []).forEach(ec => {
      if (!['combat_start', 'turn_start', 'on_play', 'on_kill', 'run_start'].includes(ec.trigger))
        fail(tag + ' trigger 非法: ' + ec.trigger);
    });
  });
}

// ---------- 事件 ----------
function checkEvents() {
  head('event pack');
  const data = readJson('events/all.json');
  if (!data) { fail('events/all.json 不存在'); return; }
  const list = arrOf(data);
  if (!list) { fail('events/all.json 不是数组'); return; }
  if (list.length < 12) fail('事件至少 12 个，实际 ' + list.length);
  else if (list.length > 12) warn('事件共 ' + list.length + ' 个（基础 12，扩充已生效）');
  else ok('事件 12 个');
  const ids = new Set();
  list.forEach((ev, i) => {
    const tag = 'event[' + i + '] ' + (ev.title || '(无题)');
    if (!ev.id) fail(tag + ' 缺 id'); else if (ids.has(ev.id)) fail(tag + ' id 重复'); else ids.add(ev.id);
    if (!ev.body) fail(tag + ' 缺 body');
    if (!Array.isArray(ev.options) || ev.options.length !== 3) fail(tag + ' 选项应为 3 个，实际 ' + (ev.options || []).length);
    else {
      const veins = new Set();
      (ev.options || []).forEach(o => {
        if (!o.text) fail(tag + ' 有选项缺 text');
        if (!o.result_text) fail(tag + ' 有选项缺 result_text');
        (o.veins || []).forEach(v => { if (!VEINS.includes(v)) fail(tag + ' 选项脉非法: ' + v); else veins.add(v); });
      });
      if (veins.size < 2) fail(tag + ' 三个选项未覆盖 2 个以上脉（实际 ' + veins.size + '）');
    }
  });
}

// ---------- 黯民 DLC 包（T18）----------
function checkDlcAnmin() {
  head('anmin DLC pack');
  // 卡牌：50 张，class=anmin，稀有度 20/16/10/4
  {
    const data = readJson('cards/anmin.json');
    if (!data) { fail('cards/anmin.json 不存在'); return; }
    const cards = arrOf(data);
    if (!cards) { fail('cards/anmin.json 不是数组'); return; }
    if (cards.length < 50) fail('anmin 卡至少 50 张，实际 ' + cards.length);
    else ok('anmin 卡 50 张');
    const ids = new Set(), names = new Set();
    const rarity = { common: 0, uncommon: 0, rare: 0, special: 0 };
    let noFlavor = 0, badFlavor = 0, wrongClass = 0;
    cards.forEach((c, i) => {
      const tag = 'anmin card[' + i + '] ' + (c.name || '(无名)');
      if (!c.id) fail(tag + ' 缺 id');
      else if (ids.has(c.id)) fail(tag + ' id 重复');
      else ids.add(c.id);
      if (!c.name) fail(tag + ' 缺 name');
      else if (names.has(c.name)) warn(tag + ' 卡名重复');
      else names.add(c.name);
      if (c.class !== 'anmin') wrongClass++;
      if (!c.type) fail(tag + ' 缺 type');
      if (typeof c.energy !== 'number') fail(tag + ' 缺 energy');
      if (!c.effect || typeof c.effect !== 'object') fail(tag + ' 缺 effect');
      if (!c.cost_type) fail(tag + ' 缺 cost_type');
      (c.veins || []).forEach(v => { if (!VEINS.includes(v)) fail(tag + ' 非法脉: ' + v); });
      if (rarity[c.rarity] === undefined) warn(tag + ' 未知 rarity: ' + c.rarity);
      else rarity[c.rarity]++;
      if (!c.flavor) noFlavor++;
      else if (BANNED_FLAVOR.filter(w => c.flavor.includes(w)).length) badFlavor++;
      if (!c.upgrade) fail(tag + ' 缺 upgrade（黯民卡也要能进营火）');
    });
    if (wrongClass) fail('anmin 卡有 ' + wrongClass + ' 张 class 不等于 anmin');
    if (noFlavor) fail('anmin 卡有 ' + noFlavor + ' 张缺 flavor');
    if (badFlavor) fail('anmin 卡 flavor 含禁用词');
    console.log('        rarity: ' + JSON.stringify(rarity));
    const want = { common: 20, uncommon: 16, rare: 10, special: 4 };
    Object.keys(want).forEach(k => {
      if (rarity[k] !== undefined && rarity[k] !== want[k]) warn('anmin 卡 ' + k + ' 应为 ' + want[k] + '，实际 ' + rarity[k]);
    });
  }
  // 敌人：16 个（12 普通 + 3 精英 + 1 Boss），层 1–3（回响层）
  {
    const data = readJson('enemies/anmin.json');
    if (!data) { fail('enemies/anmin.json 不存在'); return; }
    const list = arrOf(data);
    if (!list) { fail('enemies/anmin.json 不是数组'); return; }
    if (list.length !== 16) fail('anmin 敌人应 16 个，实际 ' + list.length);
    else ok('anmin 敌人 16 个');
    const ids = new Set();
    const tiers = { normal: 0, elite: 0, boss: 0 };
    const layers = {};
    let noFlavor = 0;
    list.forEach((e, i) => {
      const tag = 'anmin enemy[' + i + '] ' + (e.name || '(无名)');
      if (!e.id) fail(tag + ' 缺 id');
      else if (ids.has(e.id)) fail(tag + ' id 重复');
      else ids.add(e.id);
      if (!['normal', 'elite', 'boss'].includes(e.tier)) fail(tag + ' tier 非法: ' + e.tier);
      else tiers[e.tier]++;
      if (typeof e.layer !== 'number' || e.layer < 1 || e.layer > 3) fail(tag + ' 层非法（回响层应为 1–3）: ' + e.layer);
      else layers[e.layer] = (layers[e.layer] || 0) + 1;
      if (typeof e.hp === 'number') { if (e.hp <= 0) fail(tag + ' hp 非法'); }
      else if (typeof e.hp === 'string' && /^\d+\s*-\s*\d+$/.test(e.hp.trim())) { /* ok */ }
      else fail(tag + ' hp 格式非法: ' + JSON.stringify(e.hp));
      if (!Array.isArray(e.intent_pattern) || !e.intent_pattern.length) fail(tag + ' 缺 intent_pattern');
      (e.intent_pattern || []).forEach(it => {
        if (!['attack', 'defend', 'buff', 'debuff'].includes(it.type)) fail(tag + ' 意图类型非法: ' + it.type);
      });
      if (!e.flavor) noFlavor++;
    });
    if (noFlavor) fail('anmin 敌人有 ' + noFlavor + ' 个缺 flavor'); else ok('anmin 敌 flavor 齐全');
    console.log('        tier: ' + JSON.stringify(tiers) + '  分层: ' + JSON.stringify(layers));
    if (tiers.normal !== 12) fail('anmin 普通敌人应 12 个，实际 ' + tiers.normal);
    if (tiers.elite !== 3) fail('anmin 精英应 3 个，实际 ' + tiers.elite);
    if (tiers.boss !== 1) fail('anmin Boss 应 1 个，实际 ' + tiers.boss);
  }
  // 遗物：15 个
  {
    const data = readJson('relics/anmin.json');
    if (!data) { fail('relics/anmin.json 不存在'); return; }
    const list = arrOf(data);
    if (!list) { fail('relics/anmin.json 不是数组'); return; }
    if (list.length !== 15) fail('anmin 遗物应 15 个，实际 ' + list.length);
    else ok('anmin 遗物 15 个');
    const ids = new Set();
    list.forEach((r, i) => {
      const tag = 'anmin relic[' + i + '] ' + (r.name || '(无名)');
      if (!r.id) fail(tag + ' 缺 id');
      else if (ids.has(r.id)) fail(tag + ' id 重复');
      else ids.add(r.id);
      if (!r.effect_text) fail(tag + ' 缺 effect_text');
      if (!Array.isArray(r.effect_code) || !r.effect_code.length) fail(tag + ' 缺 effect_code');
      (r.effect_code || []).forEach(ec => {
        if (!['combat_start', 'turn_start', 'on_kill', 'run_start', 'on_play'].includes(ec.trigger))
          fail(tag + ' trigger 非法: ' + ec.trigger);
      });
    });
  }
  // 事件：10 个
  {
    const data = readJson('events/anmin.json');
    if (!data) { fail('events/anmin.json 不存在'); return; }
    const list = arrOf(data);
    if (!list) { fail('events/anmin.json 不是数组'); return; }
    if (list.length !== 10) fail('anmin 事件应 10 个，实际 ' + list.length);
    else ok('anmin 事件 10 个');
    const ids = new Set();
    list.forEach((ev, i) => {
      const tag = 'anmin event[' + i + '] ' + (ev.title || '(无题)');
      if (!ev.id) fail(tag + ' 缺 id');
      else if (ids.has(ev.id)) fail(tag + ' id 重复');
      else ids.add(ev.id);
      if (!ev.body) fail(tag + ' 缺 body');
      if (!Array.isArray(ev.options) || ev.options.length !== 3) fail(tag + ' 选项应为 3 个');
      else {
        const veins = new Set();
        ev.options.forEach(o => {
          if (!o.text) fail(tag + ' 有选项缺 text');
          if (!o.result_text) fail(tag + ' 有选项缺 result_text');
          (o.veins || []).forEach(v => { if (VEINS.includes(v)) veins.add(v); });
        });
        if (veins.size < 2) fail(tag + ' 三个选项未覆盖 2 个以上脉');
      }
    });
  }
}


// ---------- 苍民 DLC 包（T23）----------
function checkDlcCangmin() {
  head('cangmin DLC pack');
  {
    const data = readJson('cards/cangmin.json');
    if (!data) { fail('cards/cangmin.json 不存在'); return; }
    const cards = arrOf(data);
    if (!cards) { fail('cards/cangmin.json 不是数组'); return; }
    if (cards.length < 50) fail('cangmin 卡至少 50 张，实际 ' + cards.length);
    else ok('cangmin 卡 50 张');
    const ids = new Set(), names = new Set();
    const rarity = { common: 0, uncommon: 0, rare: 0, special: 0 };
    let noFlavor = 0, badFlavor = 0, wrongClass = 0, noDream = 0, dreamCount = 0;
    cards.forEach((c, i) => {
      const tag = 'cng card[' + i + '] ' + (c.name || '(无名)');
      if (!c.id) fail(tag + ' 缺 id');
      else if (ids.has(c.id)) fail(tag + ' id 重复');
      else ids.add(c.id);
      if (!c.name) fail(tag + ' 缺 name');
      else if (names.has(c.name)) warn(tag + ' 卡名重复');
      else names.add(c.name);
      if (c.class !== 'cangmin') wrongClass++;
      if (typeof c.dream !== 'boolean') fail(tag + ' 缺 dream 布尔标记');
      else { if (c.dream) dreamCount++; }
      if (!c.type) fail(tag + ' 缺 type');
      if (typeof c.energy !== 'number') fail(tag + ' 缺 energy');
      if (!c.effect || typeof c.effect !== 'object') fail(tag + ' 缺 effect');
      if (!c.cost_type) fail(tag + ' 缺 cost_type');
      (c.veins || []).forEach(v => { if (!VEINS.includes(v)) fail(tag + ' 非法脉: ' + v); });
      if (rarity[c.rarity] === undefined) warn(tag + ' 未知 rarity: ' + c.rarity);
      else rarity[c.rarity]++;
      if (!c.flavor) noFlavor++;
      else if (BANNED_FLAVOR.filter(w => c.flavor.includes(w)).length) badFlavor++;
      if (!c.upgrade) fail(tag + ' 缺 upgrade');
    });
    if (wrongClass) fail('cangmin 卡有 ' + wrongClass + ' 张 class 不等于 cangmin');
    if (noFlavor) fail('cangmin 卡有 ' + noFlavor + ' 张缺 flavor');
    if (badFlavor) fail('cangmin 卡 flavor 含禁用词');
    if (dreamCount !== 25) fail('cangmin 梦牌应 25 张，实际 ' + dreamCount + '（清醒应 ' + (cards.length - dreamCount) + '）');
    else ok('清醒牌 / 梦牌 = 25 / 25');
    console.log('        rarity: ' + JSON.stringify(rarity));
  }
  {
    const data = readJson('enemies/cangmin.json');
    if (!data) { fail('enemies/cangmin.json 不存在'); return; }
    const list = arrOf(data);
    if (!list) { fail('enemies/cangmin.json 不是数组'); return; }
    if (list.length !== 16) fail('cangmin 敌人应 16 个，实际 ' + list.length);
    else ok('cangmin 敌人 16 个');
    const ids = new Set();
    const tiers = { normal: 0, elite: 0, boss: 0 };
    const layers = {};
    let noFlavor = 0;
    list.forEach((e, i) => {
      const tag = 'cng enemy[' + i + '] ' + (e.name || '(无名)');
      if (!e.id) fail(tag + ' 缺 id');
      else if (ids.has(e.id)) fail(tag + ' id 重复');
      else ids.add(e.id);
      if (!['normal', 'elite', 'boss'].includes(e.tier)) fail(tag + ' tier 非法: ' + e.tier);
      else tiers[e.tier]++;
      if (typeof e.layer !== 'number' || e.layer < 1 || e.layer > 3) fail(tag + ' 层非法（应为 1–3）: ' + e.layer);
      else layers[e.layer] = (layers[e.layer] || 0) + 1;
      if (typeof e.hp === 'number') { if (e.hp <= 0) fail(tag + ' hp 非法'); }
      else if (typeof e.hp === 'string' && /^\d+\s*-\s*\d+$/.test(e.hp.trim())) { /* ok */ }
      else fail(tag + ' hp 格式非法: ' + JSON.stringify(e.hp));
      if (!Array.isArray(e.intent_pattern) || !e.intent_pattern.length) fail(tag + ' 缺 intent_pattern');
      if (!e.flavor) noFlavor++;
    });
    if (noFlavor) fail('cangmin 敌人有 ' + noFlavor + ' 个缺 flavor'); else ok('cangmin 敌 flavor 齐全');
    console.log('        tier: ' + JSON.stringify(tiers) + '  分层: ' + JSON.stringify(layers));
  }
  {
    const data = readJson('relics/cangmin.json');
    if (!data) { fail('relics/cangmin.json 不存在'); return; }
    const list = arrOf(data);
    if (!list) { fail('relics/cangmin.json 不是数组'); return; }
    if (list.length !== 15) fail('cangmin 遗物应 15 个，实际 ' + list.length);
    else ok('cangmin 遗物 15 个');
    const ids = new Set();
    list.forEach((r, i) => {
      const tag = 'cng relic[' + i + '] ' + (r.name || '(无名)');
      if (!r.id) fail(tag + ' 缺 id');
      else if (ids.has(r.id)) fail(tag + ' id 重复');
      else ids.add(r.id);
      if (!r.effect_text) fail(tag + ' 缺 effect_text');
      if (!Array.isArray(r.effect_code) || !r.effect_code.length) fail(tag + ' 缺 effect_code');
    });
  }
  {
    const data = readJson('events/cangmin.json');
    if (!data) { fail('events/cangmin.json 不存在'); return; }
    const list = arrOf(data);
    if (!list) { fail('events/cangmin.json 不是数组'); return; }
    if (list.length !== 10) fail('cangmin 事件应 10 个，实际 ' + list.length);
    else ok('cangmin 事件 10 个');
    const ids = new Set();
    list.forEach((ev, i) => {
      const tag = 'cng event[' + i + '] ' + (ev.title || '(无题)');
      if (!ev.id) fail(tag + ' 缺 id');
      else if (ids.has(ev.id)) fail(tag + ' id 重复');
      else ids.add(ev.id);
      if (!ev.body) fail(tag + ' 缺 body');
      if (!Array.isArray(ev.options) || ev.options.length !== 3) fail(tag + ' 选项应为 3 个');
      else {
        const veins = new Set();
        ev.options.forEach(o => {
          if (!o.text) fail(tag + ' 有选项缺 text');
          if (!o.result_text) fail(tag + ' 有选项缺 result_text');
          (o.veins || []).forEach(v => { if (VEINS.includes(v)) veins.add(v); });
        });
        if (veins.size < 2) fail(tag + ' 三个选项未覆盖 2 个以上脉');
      }
    });
  }
}

// ---------- 主 ----------
const which = (process.argv[2] || 'all').toLowerCase();
if (which === 'cards' || which === 'all') checkCards();
if (which === 'enemies' || which === 'all') checkEnemies();
if (which === 'relics' || which === 'all') checkRelics();
if (which === 'events' || which === 'all') checkEvents();
if (which === 'anmin' || which === 'all') checkDlcAnmin();
if (which === 'cangmin' || which === 'all') checkDlcCangmin();

console.log('\n' + '='.repeat(40));
console.log(fails === 0 ? '全部通过（' + warns + ' 个警告）' : fails + ' 项失败，' + warns + ' 个警告');
process.exit(fails === 0 ? 0 : 1);
