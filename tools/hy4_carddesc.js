// HY4 · Y4 cardDesc 映射完整性（纯静态读源码，不跑浏览器）
// 用法：node tools/hy4_carddesc.js           （打印 Markdown 报告）
//       node tools/hy4_carddesc.js --json    （机器可读 JSON）
// 从 web/index.html 的 function cardDesc 中抽出 `const m = { code: '中文', ... }`，
// 与 8 个新 code 白名单、以及全池实际用到的 code 三方比对。
'use strict';
const C = require('./hy4_common');

const WHITELIST = [
  'mech_grow', 'perm_strength', 'energy_gain', 'energy_on_enemy_attack',
  'enemy_defend_draw', 'discard_hand', 'parts_from_discard', 'random_effect'
];

const { raw, webText } = C.readRaw();
const lines = webText.split('\n');
const descLine = lines.findIndex(l => /function cardDesc\s*\(/.test(l)) + 1;   // 1-based

function extractMap() {
  const from = webText.indexOf('function cardDesc');
  const body = webText.slice(from, webText.indexOf('\n}', from) + 2);
  const m = body.match(/const m = \{([\s\S]*?)\};/);
  if (!m) throw new Error('cardDesc 里找不到 const m = {...}');
  const map = {};
  for (const mm of m[1].matchAll(/([A-Za-z_][A-Za-z0-9_]*)\s*:\s*'([^']*)'/g)) map[mm[1]] = mm[2];
  return { map, body };
}
const { map, body: descBody } = extractMap();

// cardDesc 对 exhaust 有独立兜底（不是走 m 表），单列出来避免误判
const specialDisplay = {
  exhaust: /e\.exhaust\s*\|\||code === 'exhaust'/.test(descBody)
    ? "独立分支 parts.push('消耗')（cardDesc 8467 行）" : ''
};

// 全池实际使用的 code
const used = new Map();
for (const { card } of C.flatPool(raw)) {
  for (const sp of C.specialsOf(card)) {
    if (!sp.code) continue;
    if (!used.has(sp.code)) used.set(sp.code, new Set());
    used.get(sp.code).add(card.id);
  }
}

const mapKeys = Object.keys(map);
const out = {
  cardDesc_line: descLine,
  map_size: mapKeys.length,
  map,
  whitelist_check: WHITELIST.map(code => ({ code, has: Object.prototype.hasOwnProperty.call(map, code), cn: map[code] || null, used_cards: [...(used.get(code) || [])] })),
  missing_in_whitelist: WHITELIST.filter(c => !Object.prototype.hasOwnProperty.call(map, c)),
  used_but_no_map: [...used.keys()].filter(c => !Object.prototype.hasOwnProperty.call(map, c)).sort(),
  outside_whitelist: mapKeys.filter(c => !WHITELIST.includes(c)).sort().map(c => ({ code: c, cn: map[c], used_cards: [...(used.get(c) || [])] })),
  true_dead: mapKeys.filter(c => !used.has(c)).sort().map(c => ({ code: c, cn: map[c] })),
  special_display: specialDisplay
};

if (process.argv.includes('--json')) {
  console.log(JSON.stringify(out, null, 2));
} else {
  console.log('# Y4 · cardDesc 映射完整性');
  console.log('');
  console.log(`源码位置：web/index.html 第 ${out.cardDesc_line} 行起（function cardDesc）；映射表 \`const m\` 共 **${out.map_size}** 项`);
  console.log('');
  console.log('## 表 A · 白名单 8 个逐条核验（缺映射的）');
  console.log('');
  console.log('| code | 映射中文 | 卡池使用 | 判定 |');
  console.log('|---|---|---|---|');
  for (const w of out.whitelist_check) {
    console.log(`| \`${w.code}\` | ${w.cn || '**缺**'} | ${w.used_cards.length ? w.used_cards.join(', ') : '0 张'} | ${w.has ? '✅ 有中文' : '⚠️ 什么都不显示'} |`);
  }
  console.log('');
  console.log(`白名单内缺映射：**${out.missing_in_whitelist.length} 个**${out.missing_in_whitelist.length ? '（' + out.missing_in_whitelist.join(', ') + '）' : ''}`);
  console.log('');
  console.log('## 表 A2 · 全池实际用到、但卡面无 m 映射的 code');
  console.log('');
  console.log('| code | 卡 id | 卡面表现 |');
  console.log('|---|---|---|');
  for (const c of out.used_but_no_map) {
    const s = specialDisplay[c] || '⚠️ 什么都不显示';
    console.log(`| \`${c}\` | ${[...used.get(c)].join(', ')} | ${s} |`);
  }
  console.log('');
  console.log('## 表 B · 映射表里有、白名单里没有的 code（任务书称「死映射」）');
  console.log('');
  console.log('| code | 映射中文 | 卡池使用张数 | 是否真死代码 |');
  console.log('|---|---|---|---|');
  for (const r of out.outside_whitelist) {
    console.log(`| \`${r.code}\` | ${r.cn} | ${r.used_cards.length} | ${r.used_cards.length ? '否（老 code，在用）' : '**是**'} |`);
  }
  console.log('');
  console.log('## 真·死映射（映射表有、全池 0 张卡使用）');
  console.log('');
  console.log(out.true_dead.length ? out.true_dead.map(r => '` ' + r.code + ' `' + ' → ' + r.cn).join('\n') : '（无）');
}
