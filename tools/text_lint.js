/* T64 文本体检：对 cards/ enemies/ relics/ events/ 全量扫描，输出 tools/text_lint.json + 终端摘要。
   五类检查：说明书腔 / 翻译腔 / 长度异常 / 重复意象（报告）/ 命名冲突（同名+近似名）。
   用法：node tools/text_lint.js [--json-only] */
'use strict';
const fs = require('fs');
const path = require('path');
const ROOT = path.join(__dirname, '..');

/* 规则表（正则均可机器复核） */
const MECH = [ // 说明书腔：把 UI 该显示的数字写进正文
  /你(获得|得到|失去)/, /(获得|得到)\s*\d+/, /造成\s*\d+\s*点/, /增加\s*\d+\s*点/,
  /恢复\s*\d+\s*点/, /减少\s*\d+\s*点/, /每回合(增加|获得|回复)/, /点(伤害|格挡|生命)/
];
const TRANSL = [ // 翻译腔
  /的的/, /了了/, /地地/, /被[^。，；]{1,8}所[^。，；]{1,6}[，。]/, /作为一个/
];
const IMAGES = ['眼', '门', '刀', '杯', '星', '蛇', '玫瑰', '骷髅', '手', '骨', '灰', '灯', '账', '壳', '水', '火', '历', '印', '苔', '雪'];

/* 扫描对象：集合 → 条目 → 文本字段（flavor 类；effect_text/effect 是 UI 字段不扫） */
const files = {
  cards_diver: { file: 'cards/diver.json', name: 'name', texts: ['flavor', 'cost_text'] },
  cards_tremor: { file: 'cards/tremor.json', name: 'name', texts: ['flavor', 'cost_text'] },
  cards_anmin: { file: 'cards/anmin.json', name: 'name', texts: ['flavor', 'cost_text'] },
  cards_cangmin: { file: 'cards/cangmin.json', name: 'name', texts: ['flavor', 'cost_text'] },
  enemies: { file: 'enemies/all.json', name: 'name', texts: ['flavor'] },
  relics: { file: 'relics/all.json', name: 'name', texts: ['flavor'] },
  events: { file: 'events/all.json', name: 'title', texts: ['body', 'result_text'] }
};
// events 的 result_text 在 options 里，单独展开
function loadEntries() {
  const entries = [];
  Object.keys(files).forEach(key => {
    const f = files[key];
    const arr = JSON.parse(fs.readFileSync(path.join(ROOT, f.file), 'utf8'));
    arr.forEach(item => {
      const texts = [];
      f.texts.forEach(t => { if (item[t]) texts.push({ field: t, text: item[t] }); });
      if (key === 'events') (item.options || []).forEach((o, i) => {
        if (o.result_text) texts.push({ field: 'options[' + i + '].result_text', text: o.result_text });
      });
      entries.push({ set: key, file: f.file, id: item.id, name: item[f.name], tier: item.tier || item.rarity || '', texts });
    });
  });
  return entries;
}

function lev(a, b) {
  const m = a.length, n = b.length;
  if (!m || !n) return Math.max(m, n);
  const d = Array.from({ length: m + 1 }, (_, i) => [i].concat(Array(n).fill(0)));
  for (let j = 0; j <= n; j++) d[0][j] = j;
  for (let i = 1; i <= m; i++) for (let j = 1; j <= n; j++) {
    d[i][j] = Math.min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
  }
  return d[m][n];
}

function lint() {
  const entries = loadEntries();
  const problems = [];
  entries.forEach(e => e.texts.forEach(t => {
    MECH.forEach(re => { if (re.test(t.text)) problems.push({ set: e.set, id: e.id, name: e.name, field: t.field, kind: 'mech', rule: re.source, text: t.text.slice(0, 60) }); });
    TRANSL.forEach(re => { if (re.test(t.text)) problems.push({ set: e.set, id: e.id, name: e.name, field: t.field, kind: 'transl', rule: re.source, text: t.text.slice(0, 60) }); });
    if (t.field === 'flavor') {   // 长度规则只对 flavor 生效（cost_text 是 UI 简句， exempt）
      const L = t.text.length;
      if (L > 48) problems.push({ set: e.set, id: e.id, name: e.name, field: t.field, kind: 'len_long', len: L, text: t.text.slice(0, 60) });
      else if (L < 6) problems.push({ set: e.set, id: e.id, name: e.name, field: t.field, kind: 'len_short', len: L, text: t.text });
    }
  }));

  // 重复意象（报告型）：名词 → 出现条目数；超集合 30% 列出
  const imagery = {};
  IMAGES.forEach(img => {
    const hits = entries.filter(e => e.texts.some(t => t.text.indexOf(img) >= 0)).length;
    imagery[img] = { count: hits, ratio: +(hits / entries.length).toFixed(3) };
  });
  const hotImagery = Object.keys(imagery).filter(k => imagery[k].ratio > 0.3);

  // 命名冲突：同名 / 家族命名（同词干+括注/后缀，设计使然，单列报告）/ 真近似名
  // 近似阈值按长度分级：≤3 字名 lev 1 才算（否则任意两张 2 字名都命中），≥4 字名 lev 2
  const dupNames = [], nearNames = [], familyNames = [];
  const bySet = {};
  entries.forEach(e => { (bySet[e.set] = bySet[e.set] || []).push(e); });
  Object.keys(bySet).forEach(set => {
    const arr = bySet[set];
    const seen = {};
    arr.forEach(e => { (seen[e.name] = seen[e.name] || []).push(e.id); });
    Object.keys(seen).forEach(n => { if (seen[n].length > 1) dupNames.push({ set, name: n, ids: seen[n] }); });
    const stem = n => n.replace(/[（(].*$/, '').replace(/[·：:].*$/, '');
    const commonPrefix = (a, b) => { let i = 0; while (i < a.length && i < b.length && a[i] === b[i]) i++; return i; };
    for (let i = 0; i < arr.length; i++) for (let j = i + 1; j < arr.length; j++) {
      const a = arr[i].name, b = arr[j].name;
      if (a === b) continue;
      const th = Math.max(a.length, b.length) >= 4 ? 2 : 1;
      if (lev(a, b) <= th) {
        const isFamily = stem(a) === stem(b) || (commonPrefix(a, b) >= 2 && Math.min(a.length, b.length) >= 3);
        if (isFamily) familyNames.push({ set, a: arr[i].id + ':' + a, b: arr[j].id + ':' + b });
        else nearNames.push({ set, a: arr[i].id + ':' + a, b: arr[j].id + ':' + b });
      }
    }
  });

  const out = {
    meta: { task: 'T64', entries: entries.length, rules: { mech: MECH.map(r => r.source), transl: TRANSL.map(r => r.source) } },
    counts: {
      total: problems.length,
      byKind: problems.reduce((a, p) => { a[p.kind] = (a[p.kind] || 0) + 1; return a; }, {}),
      bySet: problems.reduce((a, p) => { a[p.set] = (a[p.set] || 0) + 1; return a; }, {})
    },
    problems,
    imagery: { threshold: '集合内 >30% 条目含该名词则列出', counts: imagery, hot: hotImagery },
    names: { dupNames, familyNames: familyNames.slice(0, 120), nearNames: nearNames.slice(0, 80) }
  };
  fs.writeFileSync(path.join(ROOT, 'tools', 'text_lint.json'), JSON.stringify(out, null, 1));
  return out;
}

const res = lint();
if (process.argv.indexOf('--json-only') < 0) {
  console.log('=== T64 文本体检 ===');
  console.log('扫描条目: ' + res.meta.entries);
  console.log('问题总数: ' + res.counts.total + '  ' + JSON.stringify(res.counts.byKind) + '  ' + JSON.stringify(res.counts.bySet));
  console.log('说明书腔样例:');
  res.problems.filter(p => p.kind === 'mech').slice(0, 8).forEach(p => console.log('  [' + p.set + '/' + p.id + '/' + p.field + '] ' + p.rule + ' ← ' + p.text));
  console.log('翻译腔样例:');
  res.problems.filter(p => p.kind === 'transl').slice(0, 8).forEach(p => console.log('  [' + p.set + '/' + p.id + '] ← ' + p.text));
  console.log('长度异常: 长 ' + res.counts.byKind.len_long + ' / 短 ' + res.counts.byKind.len_short);
  console.log('热点意象(>30%): ' + JSON.stringify(res.imagery.hot));
  console.log('同名冲突: ' + res.names.dupNames.length + ' 组; 家族命名(设计使然): ' + res.names.familyNames.length + ' 对; 真近似名: ' + res.names.nearNames.length + ' 对');
}
