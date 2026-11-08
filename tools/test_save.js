// 存档往返测试（不依赖浏览器）
// 1. 从 index.html 抠出真实的 makeRng，验证 getState/setState 能精确复现随机序列
// 2. 在 vm 沙箱里加载 web/save.js，用假 localStorage 测 snapshot → JSON → applyTo 往返
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = path.join(__dirname, '..');
let pass = 0, fail = 0;
function ok(name, cond, extra) {
  if (cond) { pass++; console.log('  OK   ' + name); }
  else { fail++; console.log('  FAIL ' + name + (extra ? ' → ' + extra : '')); }
}

/* ── 1. makeRng ─────────────────────────────────── */
const html = fs.readFileSync(path.join(ROOT, 'web', 'index.html'), 'utf8');
// index.html 里有两个 makeRng（不同 script 块）。按 fn.getState 标记定位**改造过的那个**，
// 再用括号配平切出完整函数体（正则匹配 \n  + 缩进不可靠）。
const marker = html.indexOf('fn.getState');
if (marker < 0) { console.error('index.html 里找不到 fn.getState，改造没生效'); process.exit(1); }
const fnStart = html.lastIndexOf('function makeRng(seed) {', marker);
if (fnStart < 0) { console.error('找不到 makeRng 函数头'); process.exit(1); }
let depth = 0, endIdx = -1;
for (let i = html.indexOf('{', fnStart); i < html.length; i++) {
  if (html[i] === '{') depth++;
  else if (html[i] === '}') { depth--; if (depth === 0) { endIdx = i; break; } }
}
if (endIdx < 0) { console.error('makeRng 括号未闭合'); process.exit(1); }
const src = html.slice(fnStart, endIdx + 1);
const makeRng = new Function(src + '; return makeRng;')();

console.log('=== makeRng 状态存取 ===');
ok('有 getState', typeof makeRng(1).getState === 'function');
ok('有 setState', typeof makeRng(1).setState === 'function');

const r = makeRng(987654321);
const before = [r(), r(), r(), r()];
const st = r.getState();
const after = [r(), r(), r(), r()];

const r2 = makeRng(1);            // 故意用不同种子
r2.setState(st);
const replay = [r2(), r2(), r2(), r2()];
ok('状态恢复后序列完全一致', JSON.stringify(after) === JSON.stringify(replay),
  'after=' + after.join(',') + ' replay=' + replay.join(','));
ok('恢复前的序列不受影响', before.every(x => x >= 0 && x < 1));

// 空跑若干次后再存取，确认状态一直在推进（不是恒等）
const r3 = makeRng(42);
for (let i = 0; i < 100; i++) r3();
const s100 = r3.getState();
const n100 = r3();
const r4 = makeRng(0); r4.setState(s100);
ok('跑 100 次后状态依然可恢复', r4() === n100);

/* ── 2. save.js ─────────────────────────────────── */
console.log('\n=== Save 往返 ===');
const store = {};
const sandbox = {
  window: null,
  localStorage: {
    getItem: k => (k in store ? store[k] : null),
    setItem: (k, v) => { store[k] = String(v); },
    removeItem: k => { delete store[k]; }
  },
  JSON, Date, Object, Array, console, Math, Number, String, Boolean, Error
};
sandbox.window = sandbox;
vm.createContext(sandbox);
vm.runInContext(fs.readFileSync(path.join(ROOT, 'web', 'save.js'), 'utf8'), sandbox);
const Save = sandbox.Save;
ok('Save 挂载成功', !!Save);
ok('版本号存在', typeof Save.VERSION === 'number');

// 造一个贴近真实的 run
const rr = makeRng(20261106);
const deck = [];
for (let i = 0; i < 14; i++) {
  deck.push({
    id: 'anm_00' + (10 + i), name: '卡' + i, rarity: i % 3 ? 'common' : 'rare',
    type: i % 2 ? 'skill' : 'attack', veins: ['light'],
    energy: 1, cost_type: 'none', uid: 'u' + i,
    effect: { damage: 5 + i, block: 0, hits: 1, target: 'single' },
    flavor: '一段中文风味文本，用来测试编码与体积。',
    upgrade: { name_suffix: '·固', effect: { damage: 7 + i } }
  });
}
const run = {
  classId: 'anmin', hp: 61, maxHp: 76, energyMax: 3, gaze: 4, depth: 3, node: 2,
  gold: 40, parts: 12, strength: 1, dead: false, won: false,
  clarity: undefined, clarityMax: undefined, dreamMaxHp: undefined,
  deck: deck, relics: [{ id: 'rel_01', name: '遗物' }],
  log: Array.from({ length: 120 }, (_, i) => ({ text: '第' + i + '条日志', kind: 'info' })),
  stats: { battles: 5, kills: 9, events: 2 },
  row: 3, col: 1,
  rng: rr,
  _tempRef: { nested: { ok: true } }
};
// 塞一个不可序列化的东西，确认会被跳过而不是炸掉
run._fn = function () { return 1; };

const snap = Save.snapshot(run);
ok('snapshot 非空', !!snap);
ok('跳过函数字段', Array.isArray(snap._skipped) && snap._skipped.includes('_fn'));
ok('保留 rngState', typeof snap.rngState === 'number');
ok('log 截到 40 条', snap.logTail.length === 40);
ok('丢掉 undefined 字段', !('clarity' in snap.fields));

const json = JSON.stringify(snap);
ok('体积在合理范围', json.length < 20000, json.length + ' 字节');

// 恢复：造一个干净 run（模拟 newRun 的结构），把存档灌进去
const fresh = makeRng(1);
const run2 = {
  classId: null, hp: 0, maxHp: 0, energyMax: 0, gaze: 0, depth: 0, node: 0,
  gold: 0, parts: 0, strength: 0, dead: false, won: false,
  deck: [], relics: [], log: [], stats: {}, row: -1, col: 0, rng: fresh
};
const back = Save.applyTo(run2, JSON.parse(json));
ok('applyTo 返回对象', !!back);
ok('classId 还原', run2.classId === 'anmin');
ok('hp 还原', run2.hp === 61 && run2.maxHp === 76);
ok('depth/row/col 还原', run2.depth === 3 && run2.row === 3 && run2.col === 1);
ok('parts 还原', run2.parts === 12);
ok('deck 长度还原', run2.deck.length === 14);
ok('deck 卡内容还原', run2.deck[3].effect.damage === 8 && run2.deck[3].uid === 'u3');
ok('中文未损坏', run2.deck[0].flavor.includes('中文风味'));
ok('relics 还原', run2.relics.length === 1 && run2.relics[0].id === 'rel_01');
ok('stats 还原', run2.stats.battles === 5);
ok('log 截断后还原', run2.log.length === 40 && run2.log[39].text === '第119条日志');

// 最关键：恢复后随机序列是否接上
const origNext = [run.rng(), run.rng(), run.rng()];
const restNext = [run2.rng(), run2.rng(), run2.rng()];
ok('恢复后随机序列接得上', JSON.stringify(origNext) === JSON.stringify(restNext),
  'orig=' + origNext.map(x => x.toFixed(6)).join(',') + ' rest=' + restNext.map(x => x.toFixed(6)).join(','));

/* ── 3. 存取与失效 ─────────────────────────────── */
console.log('\n=== 存取 / 失效 ===');
ok('save 成功', Save.save(run) === true);
ok('has 为真', Save.has() === true);
const info = Save.info();
ok('info 摘要完整', info && info.className === '黯民' && info.deckSize === 14 && info.depth === 3,
  JSON.stringify(info));
ok('clear 成功', Save.clear() === true && Save.has() === false);

store[Save.KEY] = '{坏的 json';
ok('坏档返回 null（不抛）', Save.load() === null);
ok('坏档被自动清掉', !(Save.KEY in store));

store[Save.KEY] = JSON.stringify({ v: 999, fields: { classId: 'anmin', deck: [{}] } });
ok('版本不符返回 null', Save.load() === null);
ok('版本不符被清掉', !(Save.KEY in store));

store[Save.KEY] = JSON.stringify({ v: Save.VERSION, fields: { classId: 'anmin', deck: [] } });
ok('空牌组返回 null', Save.load() === null);

/* ── 4. 配额满 ─────────────────────────────────── */
console.log('\n=== 极端情况 ===');
const quota = {
  getItem: () => null,
  setItem: () => { const e = new Error('QuotaExceededError'); e.name = 'QuotaExceededError'; throw e; },
  removeItem: () => {}
};
const box2 = { window: null, localStorage: quota, JSON, Date, Object, Array, console, Math, Number, String, Boolean, Error };
box2.window = box2;
vm.createContext(box2);
vm.runInContext(fs.readFileSync(path.join(ROOT, 'web', 'save.js'), 'utf8'), box2);
ok('配额满时返回 false 而不是抛异常', box2.Save.save(run) === false);

console.log('\n' + (fail ? '✗ ' + fail + ' 项失败，' + pass + ' 项通过' : '✓ 全部通过（' + pass + ' 项）'));
process.exit(fail ? 1 : 0);
