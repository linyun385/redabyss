#!/usr/bin/env node
/* _save_stress.js — 存档压力测试（T262）。
 * 游戏的持久化面 = web/index.html 里 4 处 localStorage 读写：
 *   ① redabyss_cleared（开局读，L~6428/6435，try/catch 包裹）
 *   ② redabyss_death_<key>（死因提示记账，L~7051，try/catch）
 *   ③ redabyss_endings（通关标记 JSON 数组，markCleared，L~7457，try/catch 含 JSON.parse）
 *   ④ redabyss_hint_<key>（一次性提示记账，onceHint，L~7562，try/catch）
 * 本脚本做两件事：
 *   A. 源码守护断言——4 处读写必须仍在 try/catch 内（防止将来有人裸写）
 *   B. 行为压测——用 localStorage mock 按源码同款逻辑连存/读 200 次、
 *      塞损坏 JSON、空存档读、配额满模拟，验证没有任何异常逃逸
 * 产出 data/save_stress.json；exit 0 = 全过。
 */
const fs = require('fs');
const path = require('path');
const ROOT = path.join(__dirname, '..');
const src = fs.readFileSync(path.join(ROOT, 'web', 'index.html'), 'utf8');
const out = { meta: { tool: 'tools/_save_stress.js', cycles: 200 }, guards: [], stress: [], fail: [] };

// ---------- A. 源码守护断言 ----------
const GUARDS = [
  { name: 'cleared 读取', re: /try\s*\{\s*cleared\s*=\s*localStorage\.getItem\('redabyss_cleared'\)\s*===\s*'1';\s*\}\s*catch\s*\(e\)\s*\{\}/ },
  { name: 'cleared 二周目', re: /try\s*\{\s*if\s*\(localStorage\.getItem\('redabyss_cleared'\)\s*===\s*'1'\)\s*\{/ },
  { name: 'death 提示记账', re: /try\s*\{\s*const k = 'redabyss_death_' \+ key;/ },
  { name: 'markCleared endings', re: /try\s*\{\s*localStorage\.setItem\('redabyss_cleared',\s*'1'\);/ },
  { name: 'onceHint 记账', re: /try\s*\{\s*const k = 'redabyss_hint_' \+ key;/ },
];
for (const g of GUARDS) {
  const ok = g.re.test(src);
  out.guards.push({ name: g.name, guarded: ok });
  if (!ok) out.fail.push('守护断言失败：' + g.name + '（源码形态变了，更新本脚本的正则）');
}

// ---------- B. 行为压测 ----------
function makeLS(opts) {
  const store = new Map();
  let calls = 0;
  return {
    calls: () => calls,
    getItem: (k) => { calls++; if (opts.boomGet) throw new Error('quota'); return store.has(k) ? store.get(k) : null; },
    setItem: (k, v) => { calls++; if (opts.boomSet) throw new Error('quota'); store.set(k, String(v)); },
  };
}
// 与源码同款的四个逻辑（照 web/index.html 抄，try/catch 一致）
function readCleared(LS) { let cleared = false; try { cleared = LS.getItem('redabyss_cleared') === '1'; } catch (e) {} return cleared; }
function deathHint(LS, key, msg) { try { const k = 'redabyss_death_' + key; if (LS.getItem(k)) return null; LS.setItem(k, '1'); } catch (e) { return null; } return msg; }
function markCleared(LS, endingId) { try { LS.setItem('redabyss_cleared', '1'); const seen = JSON.parse(LS.getItem('redabyss_endings') || '[]'); if (seen.indexOf(endingId) < 0) { seen.push(endingId); LS.setItem('redabyss_endings', JSON.stringify(seen)); } } catch (e) {} }
function onceHint(LS, key, msg) { let show = true; try { const k = 'redabyss_hint_' + key; if (LS.getItem(k)) show = false; else LS.setItem(k, '1'); } catch (e) { } if (show) { /* toast */ } return show; }

const ENDINGS = ['dive_end', 'tremor_end', 'anmin_end', 'cangmin_end', 'secret_end'];

function scenario(name, fn) {
  try { const r = fn(); out.stress.push({ name, ok: true, detail: r }); }
  catch (e) { out.stress.push({ name, ok: false, detail: String(e) }); out.fail.push(name + ': ' + e); }
}

scenario('连存/读 200 次（4 条路径轮转）', () => {
  const LS = makeLS({});
  if (readCleared(LS) !== false) throw '初始 cleared 应 false';
  for (let i = 0; i < 200; i++) {
    if (onceHint(LS, 'h' + (i % 8), '提示') && i >= 8) throw 'onceHint 第 ' + i + ' 轮不该再弹';
    if (deathHint(LS, 'k' + (i % 5), '话') !== null && i >= 5) throw 'deathHint 第 ' + i + ' 轮不该再提示';
    markCleared(LS, ENDINGS[i % ENDINGS.length]);
  }
  if (readCleared(LS) !== true) throw 'markCleared 后 cleared 应转 true（二周目语义）';
  if (JSON.parse(LS.getItem('redabyss_endings')).length !== ENDINGS.length) throw 'endings 去重失败';
  return '200 轮完成；cleared false→true 转换正确；endings 去重正确；hint/death 各自只记一次';
});

scenario('空存档读', () => {
  const LS = makeLS({});
  if (readCleared(LS) !== false) throw '空档 cleared 应 false';
  if (deathHint(LS, 'x', '话') !== '话') throw '空档 deathHint 应提示';
  if (!onceHint(LS, 'y', '话')) throw '空档 onceHint 应提示';
  markCleared(LS, 'e1'); // 空档上直接 mark：getItem null → || '[]'
  return '全部按空档语义工作';
});

scenario('损坏 JSON（endings 被塞脏数据）', () => {
  const LS = makeLS({});
  LS.setItem('redabyss_endings', '{not json');
  markCleared(LS, 'e1'); // parse 抛错 → 被 try/catch 吞掉，不逃逸
  LS.setItem('redabyss_endings', 'null');
  markCleared(LS, 'e2');
  LS.setItem('redabyss_endings', '12345');
  markCleared(LS, 'e3');
  return '损坏 JSON 不崩（markCleared 静默跳过本轮记账）';
});

scenario('空串/超长值', () => {
  const LS = makeLS({});
  LS.setItem('redabyss_cleared', '');
  if (readCleared(LS) !== false) throw '空串应判 false';
  LS.setItem('redabyss_endings', JSON.stringify(new Array(5000).fill('e')));
  markCleared(LS, 'e1');
  return '超长数组读入+去重不崩';
});

scenario('配额满（getItem/setItem 抛错）', () => {
  const LS = makeLS({ boomGet: true, boomSet: true });
  if (readCleared(LS) !== false) throw '异常时 cleared 应取 false 兜底';
  if (deathHint(LS, 'k', '话') !== null) throw '异常时 deathHint 应返回 null';
  if (!onceHint(LS, 'k', '话')) throw '异常时 onceHint 应本次提示';
  markCleared(LS, 'e1');
  return '全部异常被 try/catch 吞掉，不逃逸';
});

out.pass = out.fail.length === 0;
fs.writeFileSync(path.join(ROOT, 'data', 'save_stress.json'), JSON.stringify(out, null, 1), 'utf8');
console.log('save_stress: 守护断言 %d/%d，压测 %d/%d → data/save_stress.json',
  out.guards.filter(g => g.guarded).length, out.guards.length,
  out.stress.filter(s => s.ok).length, out.stress.length);
process.exit(out.pass ? 0 : 1);
