// HY4 · Y1 数据一致性核对：cards/anmin.json  <->  web/index.html 的 RAW.anmin
// 用法：node tools/hy4_raw_vs_json.js            （打印报告）
//       node tools/hy4_raw_vs_json.js --json     （只输出机器可读 JSON）
// 只读脚本：不修改任何文件。
'use strict';
const C = require('./hy4_common');

const { raw } = C.readRaw();
const jf = C.readCardJson('anmin');
const J = jf.data;                 // cards/anmin.json 解析后的数组
const R = Array.isArray(raw.anmin) ? raw.anmin : null;

const result = {
  json_path: 'cards/anmin.json',
  web_path: 'web/index.html',
  json_count: J.length,
  raw_count: R === null ? null : R.length,
  equal_count: R !== null && J.length === R.length,
  ids_only_in_json: [], ids_only_in_raw: [], duplicate_ids_json: [], duplicate_ids_raw: [],
  content_diff: [],
  byte_level: {},
  other_pools: [],
  verdict: ''
};

// --- 1. id 集合 ---
const jIds = J.map(c => c.id), rIds = R ? R.map(c => c.id) : [];
const jSet = new Set(jIds), rSet = new Set(rIds);
result.ids_only_in_json = [...jSet].filter(x => !rSet.has(x));
result.ids_only_in_raw = [...rSet].filter(x => !jSet.has(x));
result.duplicate_ids_json = jIds.filter((x, i) => jIds.indexOf(x) !== i);
result.duplicate_ids_raw = rIds.filter((x, i) => rIds.indexOf(x) !== i);

// --- 2. 逐卡内容（稳定序列化，忽略键顺序） ---
const jById = new Map(J.map(c => [c.id, c]));
const rById = new Map(R ? R.map(c => [c.id, c]) : []);
for (const id of [...jSet].filter(x => rSet.has(x)).sort()) {
  const a = C.stable(jById.get(id)), b = C.stable(rById.get(id));
  if (a !== b) result.content_diff.push({ id, json: a.slice(0, 400), raw: b.slice(0, 400) });
}

// --- 3. 逐字节：RAW 数组文本 vs anmin.json 的紧凑化文本 ---
// RAW 是 _sync_cards.js 用 JSON.stringify(raw) 整段写入的，因此 RAW.anmin 的字节
// 应严格等于 JSON.stringify(J)；再校验 anmin.json 去掉字符串外空白后是否同一串。
const compactJsonFile = C.stripJsonWhitespace(jf.text);
const compactParsed = JSON.stringify(J);
const rawAnminText = R ? JSON.stringify(R) : '';
result.byte_level = {
  method: 'JSON.stringify(RAW.anmin) 与 JSON.stringify(anmin.json 解析结果) 与 stripWhitespace(anmin.json 原文) 三方逐字符比较',
  lengths: {
    'JSON.stringify(RAW.anmin)': rawAnminText.length,
    'JSON.stringify(json)': compactParsed.length,
    'stripWhitespace(json 原文)': compactJsonFile.length
  },
  raw_vs_json_parsed_identical: rawAnminText === compactParsed,
  json_file_vs_parsed_identical: compactJsonFile === compactParsed,
  first_diff_offset: (() => {
    const n = Math.min(rawAnminText.length, compactJsonFile.length);
    for (let i = 0; i < n; i++) if (rawAnminText[i] !== compactJsonFile[i]) return i;
    return rawAnminText.length === compactJsonFile.length ? -1 : n;
  })(),
  identical_all_three: rawAnminText === compactParsed && compactJsonFile === compactParsed
};

// --- 4. 顺带：其余 4 个卡池键的同步状态（不计入 Y1 结论，仅作旁证） ---
for (const k of C.POOL_KEYS.filter(x => x !== 'anmin')) {
  let n = null, same = null;
  try {
    const d = C.readCardJson(k).data;
    n = d.length;
    same = Array.isArray(raw[k]) && C.stable(raw[k]) === C.stable(d);
  } catch (e) { /* 文件不存在 */ }
  result.other_pools.push({ key: k, json_count: n, raw_count: Array.isArray(raw[k]) ? raw[k].length : null, identical: same });
}

const clean = result.equal_count &&
  result.ids_only_in_json.length === 0 && result.ids_only_in_raw.length === 0 &&
  result.duplicate_ids_json.length === 0 && result.duplicate_ids_raw.length === 0 &&
  result.content_diff.length === 0 && result.byte_level.identical_all_three;
result.verdict = clean ? '完全一致' : '存在差异（见上）';

if (process.argv.includes('--json')) {
  console.log(JSON.stringify(result, null, 2));
} else {
  const b = result.byte_level;
  console.log('# Y1 · anmin.json ↔ RAW.anmin 一致性');
  console.log('');
  console.log('| 项 | 值 |');
  console.log('|---|---|');
  console.log(`| cards/anmin.json 条数 N | ${result.json_count} |`);
  console.log(`| RAW.anmin 条数 M | ${result.raw_count} |`);
  console.log(`| N === M | ${result.equal_count ? '是' : '否'} |`);
  console.log(`| 仅在 json 的 id | ${result.ids_only_in_json.length ? result.ids_only_in_json.join(', ') : '（无）'} |`);
  console.log(`| 仅在 RAW 的 id | ${result.ids_only_in_raw.length ? result.ids_only_in_raw.join(', ') : '（无）'} |`);
  console.log(`| json 重复 id | ${result.duplicate_ids_json.length ? result.duplicate_ids_json.join(', ') : '（无）'} |`);
  console.log(`| RAW 重复 id | ${result.duplicate_ids_raw.length ? result.duplicate_ids_raw.join(', ') : '（无）'} |`);
  console.log(`| 逐卡内容不同的 id | ${result.content_diff.length ? result.content_diff.map(x => x.id).join(', ') : '（无）'} |`);
  console.log('');
  console.log('## 逐字节');
  console.log('');
  console.log(`- 方法：${b.method}`);
  console.log(`- 长度：RAW 段 ${b.lengths['JSON.stringify(RAW.anmin)']} / json 解析 ${b.lengths['JSON.stringify(json)']} / json 原文去空白 ${b.lengths['stripWhitespace(json 原文)']}`);
  console.log(`- RAW 与 json 解析结果逐字符相同：${b.raw_vs_json_parsed_identical}`);
  console.log(`- json 原文与解析结果逐字符相同：${b.json_file_vs_parsed_identical}`);
  console.log(`- 首个差异偏移：${b.first_diff_offset}（-1 = 完全相同）`);
  console.log(`- 三方全同：${b.identical_all_three}`);
  console.log('');
  console.log('## 其余卡池键（旁证，非 Y1 要求）');
  console.log('');
  console.log('| 键 | json | RAW | 内容一致 |');
  console.log('|---|---|---|---|');
  for (const p of result.other_pools) console.log(`| ${p.key} | ${p.json_count} | ${p.raw_count} | ${p.identical} |`);
  console.log('');
  console.log(`## 结论：${result.verdict}`);
  console.log('');
  console.log('脚本：tools/hy4_raw_vs_json.js（共用解析 tools/hy4_common.js）');
}
process.exitCode = clean ? 0 : 1;
