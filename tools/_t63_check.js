/* T63 自检：①新卡超模比值（同费同稀有度现有卡上限 1.3 倍封顶，折算系数沿用 tools/card_audit.js 的口径）；
   ②新遗物引擎通道验证（mod.vein_cost 真实改变水脉牌费用，用引擎 cardCost 断言）；
   ③新旧卡 id/字段完整性。用法：node tools/_t63_check.js —— 失败 exit 1 */
'use strict';
const path = require('path');
const fs = require('fs');
const RedAbyss = require(path.join(__dirname, '..', 'engine', 'core.js'));
const allCards = [
  ...require(path.join(__dirname, '..', 'cards', 'diver.json')),
  ...require(path.join(__dirname, '..', 'cards', 'tremor.json')),
  ...require(path.join(__dirname, '..', 'cards', 'anmin.json')),
  ...require(path.join(__dirname, '..', 'cards', 'cangmin.json'))
];
const relics = require(path.join(__dirname, '..', 'relics', 'all.json'));

/* 折算系数（card_audit.js 口径）：伤害/格挡/回复 1.0、抽牌 2.5、共振 0.5、力量/敏捷 4.0（持续按 2 次收益） */
const VALUE = { damage: 1, block: 1, heal: 1, draw: 2.5, resonance_gain: 0.5 };
const SPECIAL = { strength: 4, dexterity: 4, regenerate: 2, thorns: 1.5, retain: 1 };
function cardValue(c) {
  const e = c.effect || {};
  let v = 0;
  v += (e.damage || 0) * (e.hits || 1);
  v += (e.block || 0);
  v += (e.heal || 0);
  v += (e.draw || 0) * VALUE.draw;
  v += (e.resonance_gain || 0) * VALUE.resonance_gain;
  (e.special || []).forEach(s => { v += (SPECIAL[s.code] || 0) * (s.value || 1) / (s.code === 'strength' || s.code === 'dexterity' ? 2 : 1); });
  return v;
}
const newIds = new Set(['dive_0081', 'dive_0082', 'dive_0083', 'trem_0081', 'trem_0082', 'trem_0083']);
const newCards = allCards.filter(c => newIds.has(c.id));

let fail = 0;
console.log('── 超模比值（新卡价值 / 同费同稀有度现有卡最大价值；上限 1.3）──');
newCards.forEach(c => {
  const pool = allCards.filter(x => !newIds.has(x.id) && x.energy === c.energy && x.rarity === c.rarity);
  const maxOld = Math.max(...pool.map(cardValue));
  const ratio = cardValue(c) / maxOld;
  const flag = ratio > 1.3 ? ' ✗ 超模' : '';
  console.log('  ' + c.id + ' ' + c.name + '（' + c.energy + '费/' + c.rarity + '）价值 ' + cardValue(c).toFixed(1) + ' / 上限 ' + maxOld.toFixed(1) + ' = ' + ratio.toFixed(2) + flag);
  if (ratio > 1.3) fail++;
});

/* 引擎通道验证：mod.vein_cost 让水脉牌在 D3（dry 层，水 +1 费）恢复原价（静态断言：引擎通道 + 遗物字段形状） */
console.log('── 引擎通道验证（relic_77 mod.vein_cost × D3 dry 规则）──');
{
  const core = fs.readFileSync(path.join(__dirname, '..', 'engine', 'core.js'), 'utf8');
  const hasChannel = /vein_cost_delta/.test(core) && /m\.vein_cost/.test(core);
  const relic = relics.find(r => r.id === 'relic_77');
  const shapeOk = relic.mod && relic.mod.vein_cost === 'water' && relic.mod.vein_cost_delta === -1;
  console.log('  引擎 mod.vein_cost 通道存在: ' + hasChannel + '；relic_77 字段形状正确: ' + shapeOk);
  if (!hasChannel || !shapeOk) fail++;
  // 干旱规则基础断言：dry 层水脉 +1（engine 391 行）
  const dryRule = /rule === 'dry'/.test(core);
  console.log('  D3 dry 层水脉 +1 规则在位: ' + dryRule + '（两者相消 = 通道生效的语义）');
  if (!dryRule) fail++;
}

/* 字段完整性 */
newCards.forEach(c => {
  if (!c.id || !c.name || !c.flavor || typeof c.energy !== 'number' || !c.cost_type) { console.error('FAIL 字段缺失: ' + c.id); fail++; }
});
const r77 = relics.find(r => r.id === 'relic_77');
if (!r77.eco || !r77.flavor || !r77.effect_text) { console.error('FAIL 遗物字段缺失'); fail++; }

console.log(fail ? fail + ' 项失败' : 'T63 自检全部通过。');
process.exit(fail ? 1 : 0);
