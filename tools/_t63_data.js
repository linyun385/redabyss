/* T63 生态遗物 + 专属卡牌落地（一次性，幂等）。
   配额（docs/CONTENT_PLAN.md §3.1 缺口）：遗物 +1（eco_arid）、素卡 +6（surface 3 → diver / nexus 3 → tremor）。
   遗物使用引擎已实现的 mod.vein_cost 通道（engine/core.js:396，现有 76 件从未用过——非新动作）。
   卡牌只用现有 effect 词汇（damage/hits/block/draw/resonance_gain/gaze_cost/special:retain，cost_type:vitality）。
   用法：node tools/_t63_data.js */
'use strict';
const fs = require('fs');
const path = require('path');
const ROOT = path.join(__dirname, '..');

/* ── 遗物：eco_arid（arid 现有 8 件 < 配额 9）──────────── */
const RFILE = path.join(ROOT, 'relics', 'all.json');
const relics = JSON.parse(fs.readFileSync(RFILE, 'utf8'));
if (!relics.find(r => r.id === 'relic_77')) {
  relics.push({
    id: 'relic_77',
    name: '泉权的账戳',
    rarity: 'rare',
    veins: ['water'],
    eco: 'eco_arid',
    effect_text: '开战时格挡 +3。水脉牌的费用 -1——干旱带的规程也认这个印。',
    effect_code: [{ trigger: 'combat_start', action: 'block', value: 3 }],
    mod: { vein_cost: 'water', vein_cost_delta: -1 },
    flavor: '泉权的印，往水牌上一戳。路是它的，水也记它的账。'
  });
  console.log('遗物 +1: relic_77 泉权的账戳');
} else console.log('跳过（已存在）: relic_77');
fs.writeFileSync(RFILE, JSON.stringify(relics, null, 1));

/* ── 卡牌：surface 素卡 ×3（diver）+ nexus 素卡 ×3（tremor）── */
const NEW_CARDS = {
  'cards/diver.json': [
    { id: 'dive_0081', name: '气闸的规程', class: 'diver', type: 'skill', rarity: 'common', veins: [], energy: 0,
      effect: { block: 4, target: 'self', special: [{ code: 'retain' }] }, cost_type: 'none', cost_text: '',
      flavor: '先合，再开，再合。规程留在手里，什么时候开，什么时候算数。' },
    { id: 'dive_0082', name: '按规程应答', class: 'diver', type: 'attack', rarity: 'common', veins: [], energy: 1,
      effect: { damage: 9, hits: 1, target: 'single', gaze_cost: 1 }, cost_type: 'none', cost_text: '',
      flavor: '编号报得越标准，回音里的东西越清楚。红光也在听。' },
    { id: 'dive_0083', name: '坠轨的清单', class: 'diver', type: 'skill', rarity: 'uncommon', veins: [], energy: 1,
      effect: { draw: 2, target: 'self' }, cost_type: 'vitality', cost_text: '清单上没有的东西，都有分量。',
      flavor: '没登记的那一件压在最底下。你拿了它，就替它签了收。' }
  ],
  'cards/tremor.json': [
    { id: 'trem_0081', name: '值班交接', class: 'tremor', type: 'skill', rarity: 'common', veins: [], energy: 1,
      effect: { block: 5, target: 'self', resonance_gain: 1 }, cost_type: 'none', cost_text: '',
      flavor: '班表递过来的时候很轻。接住的那只手，就算到岗了。' },
    { id: 'trem_0082', name: '不许关闭', class: 'tremor', type: 'skill', rarity: 'common', veins: [], energy: 0,
      effect: { block: 2, target: 'self', resonance_gain: 1, special: [{ code: 'retain' }] }, cost_type: 'none', cost_text: '',
      flavor: '钉子是新的。牌子留在手里，不许灭，也不许扔。' },
    { id: 'trem_0083', name: '谐振的余音', class: 'tremor', type: 'attack', rarity: 'uncommon', veins: [], energy: 2,
      effect: { damage: 5, hits: 2, target: 'single' }, cost_type: 'none', cost_text: '',
      flavor: '声音停了以后还响着的那部分。第二段，打的是你没防备的地方。' }
  ]
};
Object.keys(NEW_CARDS).forEach(rel => {
  const FILE = path.join(ROOT, rel);
  const cards = JSON.parse(fs.readFileSync(FILE, 'utf8'));
  const ids = new Set(cards.map(c => c.id));
  NEW_CARDS[rel].forEach(c => {
    if (ids.has(c.id)) { console.log('跳过（已存在）: ' + c.id); return; }
    cards.push(c); ids.add(c.id);
    console.log('卡牌 +1: ' + c.id + ' ' + c.name + '（' + rel + '）');
  });
  fs.writeFileSync(FILE, JSON.stringify(cards, null, 1));
});
