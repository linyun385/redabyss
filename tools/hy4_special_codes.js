// HY4 · Y3 新 special code 使用率审计
// 用法：node tools/hy4_special_codes.js           （打印 Markdown 报告）
//       node tools/hy4_special_codes.js --json    （机器可读 JSON）
// 口径：卡池 = RAW 里 diver / tremor / anmin / cangmin / shared 五个数组键。
//       enemies / relics / events / layers / *Enemies / *Relics / *Events 不是卡牌，不计入。
//       扫每张卡 effect.special[].code 与 upgrade.effect.special[].code。
// 只读脚本：不修改任何文件。
'use strict';
const C = require('./hy4_common');

const WHITELIST = [
  'mech_grow', 'perm_strength', 'energy_gain', 'energy_on_enemy_attack',
  'enemy_defend_draw', 'discard_hand', 'parts_from_discard', 'random_effect'
];

const { raw, webText } = C.readRaw();
const pool = C.flatPool(raw);

// --- 统计：按 code 归集「主效果 / 升级效果 / 合并去重」 ---
const stat = {};
function bump(code, id, where, name) {
  if (!code) return;
  const s = stat[code] || (stat[code] = { effect: new Map(), upgrade: new Map(), all: new Map() });
  const m = where === 'effect' ? s.effect : s.upgrade;
  m.set(id, name);
  s.all.set(id, name);
}
for (const { card } of pool) {
  for (const sp of C.specialsOf(card)) bump(sp.code, card.id, sp.where, card.name);
}
const codes = Object.keys(stat).sort();

// --- 引擎侧：applySpecial 的 case 列表（用于判断「写了但引擎没实现」） ---
const engineCases = (() => {
  const from = webText.indexOf('function applySpecial');
  const to = webText.indexOf('\n  function ', from + 10);
  const body = webText.slice(from, to > from ? to : from + 14000);
  const set = new Set();
  for (const m of body.matchAll(/case\s+'([^']+)'\s*:/g)) set.add(m[1]);
  return set;
})();

// --- 卡面侧：cardDesc 的映射表 key（Y4 复用同一份抽取逻辑） ---
const descKeys = (() => {
  const from = webText.indexOf('function cardDesc');
  const to = webText.indexOf('\n}', from);
  const body = webText.slice(from, to > from ? to : from + 4000);
  const m = body.match(/const m = \{([\s\S]*?)\};/);
  if (!m) return new Set();
  const set = new Set();
  for (const mm of m[1].matchAll(/([A-Za-z_][A-Za-z0-9_]*)\s*:\s*'/g)) set.add(mm[1]);
  return set;
})();

const rows = codes.map(code => ({
  code,
  in_whitelist: WHITELIST.includes(code),
  effect_cards: [...stat[code].effect.keys()],
  upgrade_cards: [...stat[code].upgrade.keys()],
  all_cards: [...stat[code].all.keys()],
  engine_implemented: engineCases.has(code),
  has_carddesc: descKeys.has(code)
}));

const out = {
  whitelist: WHITELIST,
  pool_keys: C.POOL_KEYS,
  pool_sizes: Object.fromEntries(C.POOL_KEYS.map(k => [k, Array.isArray(raw[k]) ? raw[k].length : null])),
  pool_total: pool.length,
  distinct_codes: codes.length,
  whitelist_usage: WHITELIST.map(code => {
    const r = rows.find(x => x.code === code);
    return { code, effect_cards: r ? r.effect_cards : [], upgrade_cards: r ? r.upgrade_cards : [], all_cards: r ? r.all_cards : [] };
  }),
  zero_usage: WHITELIST.filter(code => !rows.find(x => x.code === code)),
  outside_whitelist: rows.filter(r => !r.in_whitelist),
  all_rows: rows,
  engine_case_count: engineCases.size,
  carddesc_key_count: descKeys.size
};

if (process.argv.includes('--json')) {
  console.log(JSON.stringify(out, null, 2));
} else {
  console.log('# Y3 · special code 使用率审计');
  console.log('');
  console.log(`卡池口径：${C.POOL_KEYS.join(' / ')}`);
  console.log(`各键张数：${out.pool_sizes && C.POOL_KEYS.map(k => k + '=' + out.pool_sizes[k]).join(', ')}；合计 **${out.pool_total} 张**`);
  console.log(`扫出 distinct code：**${out.distinct_codes} 个**；引擎 applySpecial 的 case：**${out.engine_case_count} 个**；cardDesc 映射 key：**${out.carddesc_key_count} 个**`);
  console.log('');
  console.log('## 白名单 8 个');
  console.log('');
  console.log('| code | 主效果卡数 | 升级效果卡数 | 合并卡数 | 卡 id |');
  console.log('|---|---|---|---|---|');
  for (const w of out.whitelist_usage) {
    console.log(`| \`${w.code}\` | ${w.effect_cards.length} | ${w.upgrade_cards.length} | ${w.all_cards.length} | ${w.all_cards.join(', ') || '（无）'} |`);
  }
  console.log('');
  console.log(`白名单中一次都没用上的：${out.zero_usage.length ? '⚠️ ' + out.zero_usage.join(', ') : '（无）'}`);
  console.log('');
  console.log('## 全池 code 总表（白名单外的标 ⚠️）');
  console.log('');
  console.log('| code | 白名单 | 卡数(合并) | 卡 id | 引擎 case | cardDesc |');
  console.log('|---|---|---|---|---|---|');
  for (const r of out.all_rows) {
    const flag = r.in_whitelist ? '✅' : '⚠️';
    console.log(`| \`${r.code}\` | ${flag} | ${r.all_cards.length} | ${r.all_cards.join(', ')} | ${r.engine_implemented ? '有' : '**无**'} | ${r.has_carddesc ? '有' : '**无**'} |`);
  }
}
