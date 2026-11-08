// HY4 · Y5 四职业卡池结构分布
// 用法：node tools/hy4_class_shape.js            （打印 Markdown 报告）
//       node tools/hy4_class_shape.js --json     （机器可读 JSON）
// 口径：只数 RAW 的四个职业数组键 diver/tremor/anmin/cangmin；shared(11 张) 是共用牌，不计入。
//       veins 为数组，按「标签出现次数」统计，故各脉之和 >= 卡数。
//       平均费用 = 所有卡 energy 的算术平均，保留 2 位。
'use strict';
const fs = require('fs');
const path = require('path');
const C = require('./hy4_common');

const { raw } = C.readRaw();
const LABEL = { diver: '下潜者', tremor: '震语者', anmin: '黯民', cangmin: '苍民' };
const TYPES = ['attack', 'skill', 'power'];
const VEINS = ['light', 'mineral', 'tremor', 'heat', 'water'];
const RARITY = ['common', 'uncommon', 'rare', 'special'];
const NEW_IDS = ['anm_0051', 'anm_0052', 'anm_0053', 'anm_0054', 'anm_0055', 'anm_0056', 'anm_0057'];

function profile(cards) {
  const p = {
    total: cards.length,
    type: Object.fromEntries(TYPES.map(t => [t, 0])),
    veins: Object.fromEntries(VEINS.map(v => [v, 0])),
    rarity: Object.fromEntries(RARITY.map(r => [r, 0])),
    energy_sum: 0,
    avg_energy: 0,
    part_cost: 0,
    cost_type_non_none: 0,
    no_bonus: 0,
    vein_tags: 0
  };
  for (const c of cards) {
    if (p.type[c.type] !== undefined) p.type[c.type]++;
    for (const v of (c.veins || [])) { p.vein_tags++; if (p.veins[v] !== undefined) p.veins[v]++; }
    if (p.rarity[c.rarity] !== undefined) p.rarity[c.rarity]++;
    p.energy_sum += (typeof c.energy === 'number' ? c.energy : 0);
    if (c.part_cost !== undefined) p.part_cost++;
    if (c.cost_type && c.cost_type !== 'none') p.cost_type_non_none++;
    if (c.no_bonus || (c.effect && c.effect.no_bonus)) p.no_bonus++;
  }
  p.avg_energy = p.total ? +(p.energy_sum / p.total).toFixed(2) : 0;
  return p;
}

const cols = C.CLASS_KEYS;                 // 表格顺序按任务书：黯民 / 下潜者 / 震语者 / 苍民
const order = ['anmin', 'diver', 'tremor', 'cangmin'];
const P = Object.fromEntries(cols.map(k => [k, profile(raw[k])]));

// 加入核心卡之前：从现有 anmin 中剔除这 7 个新 id（与备份互证）
const before = P.anmin.total - NEW_IDS.length;
const Pbefore = profile(raw.anmin.filter(c => !NEW_IDS.includes(c.id)));
// 备份文件（第一轮 6 张落地后、子代理之前）
let backup = null;
const bp = path.join(C.CARDS, 'anmin.json.bak-20261106-0125-anmin-core');
if (fs.existsSync(bp)) backup = { total: JSON.parse(fs.readFileSync(bp, 'utf8')).length };

const pct = (n, d) => (d ? (100 * n / d).toFixed(1) + '%' : '—');
const rows = [];
const add = (name, fn) => rows.push([name, ...order.map(k => String(fn(P[k], k)))]);
add('总张数', p => p.total);
TYPES.forEach(t => add('type · ' + t, p => p.type[t]));
VEINS.forEach(v => add('脉 · ' + v, p => p.veins[v]));
RARITY.forEach(r => add('稀有度 · ' + r, p => p.rarity[r]));
add('平均费用', p => p.avg_energy);
add('有 part_cost', p => p.part_cost);
add('cost_type != none', p => p.cost_type_non_none);
add('no_bonus', p => p.no_bonus);

const out = {
  source: 'web/index.html 的 const RAW（已由 Y1 确认与 cards/*.json 完全一致）',
  pool_keys: order,
  shared_excluded: raw.shared.length,
  profiles: P,
  before_new_cards: { profile: Pbefore, removed_ids: NEW_IDS, original_total: before },
  backup,
  rows,
  ratios: {
    before: {
      skill: pct(Pbefore.type.skill, Pbefore.total),
      attack: pct(Pbefore.type.attack, Pbefore.total),
      power: pct(Pbefore.type.power, Pbefore.total),
      avg_energy: Pbefore.avg_energy,
      zero_energy: pct(raw.anmin.filter(c => !NEW_IDS.includes(c.id) && c.energy === 0).length, Pbefore.total)
    },
    after: {
      skill: pct(P.anmin.type.skill, P.anmin.total),
      attack: pct(P.anmin.type.attack, P.anmin.total),
      power: pct(P.anmin.type.power, P.anmin.total),
      avg_energy: P.anmin.avg_energy,
      zero_energy: pct(raw.anmin.filter(c => c.energy === 0).length, P.anmin.total)
    }
  },
  peer_avg: {
    skill: pct(order.filter(k => k !== 'anmin').reduce((s, k) => s + P[k].type.skill, 0), order.filter(k => k !== 'anmin').reduce((s, k) => s + P[k].total, 0)),
    attack: pct(order.filter(k => k !== 'anmin').reduce((s, k) => s + P[k].type.attack, 0), order.filter(k => k !== 'anmin').reduce((s, k) => s + P[k].total, 0)),
    power: pct(order.filter(k => k !== 'anmin').reduce((s, k) => s + P[k].type.power, 0), order.filter(k => k !== 'anmin').reduce((s, k) => s + P[k].total, 0))
  }
};

if (process.argv.includes('--json')) {
  console.log(JSON.stringify(out, null, 2));
} else {
  console.log('# Y5 · 四职业卡池结构分布');
  console.log('');
  console.log(`数据源：${out.source}；shared 共用牌 ${out.shared_excluded} 张不计入职业对比。`);
  console.log('');
  console.log('| 维度 | 黯民 | 下潜者 | 震语者 | 苍民 |');
  console.log('|---|---|---|---|---|');
  for (const r of out.rows) console.log('| ' + r.join(' | ') + ' |');
  console.log('');
  console.log('## 加入核心卡前后（黯民）');
  console.log('');
  console.log(`剔除 7 个新 id（${NEW_IDS.join(', ')}）后为 ${Pbefore.total} 张；备份文件 anmin.json.bak-20261106-0125-anmin-core 为 ${backup ? backup.total : '无'} 张（= 第一轮 6 张落地后）。`);
  console.log('');
  console.log('| 指标 | 加入前 47 | 加入后 54 | 另外三职业合计 |');
  console.log('|---|---|---|---|');
  console.log(`| skill 占比 | ${out.ratios.before.skill} | ${out.ratios.after.skill} | ${out.peer_avg.skill} |`);
  console.log(`| attack 占比 | ${out.ratios.before.attack} | ${out.ratios.after.attack} | ${out.peer_avg.attack} |`);
  console.log(`| power 占比 | ${out.ratios.before.power} | ${out.ratios.after.power} | ${out.peer_avg.power} |`);
  console.log(`| 平均费用 | ${out.ratios.before.avg_energy} | ${out.ratios.after.avg_energy} | — |`);
  console.log(`| 0 费占比 | ${out.ratios.before.zero_energy} | ${out.ratios.after.zero_energy} | — |`);
}
