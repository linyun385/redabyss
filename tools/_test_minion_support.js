// 验证 09_minion_support.json 这 5 张「给子代理上 buff」的种子卡能不能被引擎吃。
// 用法：node tools/_test_minion_support.js
'use strict';
const fs = require('fs'), path = require('path'), vm = require('vm');
const ROOT = path.join(__dirname, '..');
const html = fs.readFileSync(path.join(ROOT, 'web', 'index.html'), 'utf8');
const blocks = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]);
const engine = blocks.find(b => b.includes('root.RedAbyss = API'));

const sandbox = { console };
sandbox.window = sandbox;
sandbox.applyLayerTheme = function () {};
sandbox.document = { getElementById: () => null, querySelector: () => null, body: null };
vm.createContext(sandbox);
vm.runInContext(engine, sandbox);
const R = sandbox.RedAbyss;

const cards = JSON.parse(fs.readFileSync(path.join(ROOT, 'docs/design/anmin_minions/09_minion_support.json'), 'utf8'));
console.log('读到 %d 张种子卡\n', cards.length);

let pass = 0, fail = 0;
function ok(name, cond, extra) {
  if (cond) { pass++; console.log('  ok   ' + name); }
  else { fail++; console.log('  FAIL ' + name + (extra !== undefined ? '  → ' + JSON.stringify(extra) : '')); }
}

function mkC() {
  const run = R.newRun('anmin', { seed: 11 });
  run.parts = 20;
  const C = R.startCombat(run, [{ name: '靶子', hp: '80', intent_pattern: [{ type: 'attack', value: 1 }] }]);
  C.energy = 20;
  C.hand = []; C.drawPile = []; C.discardPile = [];
  return C;
}
function summon(C) {
  C.parts = 5;
  C.hand = [{ id: 'sum', name: '子代理', type: 'skill', energy: 0, part_cost: 5,
    effect: { target: 'self', special: [{ code: 'summon_minion', hp: 10, atk: 3 }] }, cost_type: 'none' }];
  R.playCard(C, 0, 0);
  C.parts = 20;   // 召唤花掉 5 个，补足，后面的卡要付零件
  return C.enemies.find(e => e.isMinion);
}

for (const card of cards) {
  console.log('[' + card.id + '] ' + card.name + '  target=' + card.effect.target);
  const C = mkC();
  const m = summon(C);
  m.hp = 4;                       // 打残，方便看回血
  card.energy = card.energy || 0;
  C.hand = [card];
  const before = { atk: m.atk, hp: m.hp, regen: m.regen, thorns: m.thorns,
                   pStr: C.buffs.strength || 0, pRegen: C.buffs.regen || 0, pThorns: C.buffs.thorns || 0 };
  const r = R.playCard(C, 0, m.idx);
  ok('打出成功', r.ok === true, r);

  const e = card.effect || {};
  if (e.heal) ok('子代理回血 ' + before.hp + ' → ' + m.hp, m.hp === Math.min(m.maxHp, before.hp + e.heal), m.hp);
  (e.special || []).forEach(sp => {
    const V = sp.value;
    if (sp.code === 'strength') {
      if (e.target === 'all_ally') {
        ok('玩家力量 +' + V, (C.buffs.strength || 0) === before.pStr + V, C.buffs.strength);
        ok('子代理攻击 +' + V, m.atk === before.atk + V, m.atk);
      } else {
        ok('子代理攻击 ' + before.atk + ' → ' + m.atk, m.atk === before.atk + V, m.atk);
        ok('玩家力量没动', (C.buffs.strength || 0) === before.pStr, C.buffs.strength);
      }
    }
    if (sp.code === 'regenerate') ok('子代理再生 +' + V, m.regen === before.regen + V, m.regen);
    if (sp.code === 'thorns') ok('子代理荆棘 +' + V, m.thorns === before.thorns + V, m.thorns);
  });
  console.log('');
}

console.log('===== 结果：%d 通过 / %d 失败 =====', pass, fail);
process.exit(fail ? 1 : 0);
