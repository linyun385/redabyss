// T75 回返遭遇判定检查器。
//   1. 从 web/index.html 抽取 ==T75-BACKTRACK-ROLL== 段的纯函数（测的就是发货代码，防两处漂移）
//   2. 用 tools/mapgen_spec.json 的 rescue.backtrack 参数跑 500 次判定
//   3. 输出分布表并断言：badEvent 45% / combat 30% / elite 15% / boss 8% / none 2%（各 ±5pp）
// 用法：node tools/check_backtrack.js   （通过 exit 0）
'use strict';
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const HTML = path.join(ROOT, 'web', 'index.html');
const SPEC = JSON.parse(fs.readFileSync(path.join(ROOT, 'tools', 'mapgen_spec.json'), 'utf8'));

let fails = 0;
const ok = m => console.log('  ok    ' + m);
const fail = m => { console.log('  FAIL  ' + m); fails++; };

console.log('=== T75 回返遭遇判定检查 ===\n');

// ── 1. 抽取页面内的 backtrackRoll（发货代码本体）
const html = fs.readFileSync(HTML, 'utf8');
const M = '/* ==T75-BACKTRACK-ROLL==';
const ME = '/* ==/T75-BACKTRACK-ROLL== */';
const si = html.indexOf(M), ei = html.indexOf(ME);
if (si < 0 || ei < 0) { fail('web/index.html 里找不到 ==T75-BACKTRACK-ROLL== 段'); process.exit(1); }
let snippet = html.slice(si + M.length, ei).trim();
const closeCmt = snippet.indexOf('*/');            // 标记行尾的注释闭合要剥掉
if (closeCmt >= 0) snippet = snippet.slice(closeCmt + 2).trim();
let backtrackRoll;
try {
  backtrackRoll = new Function(snippet + '\nreturn backtrackRoll;')();
} catch (e) { fail('backtrackRoll 片段无法求值：' + e.message); process.exit(1); }
ok('已从 ==T75-BACKTRACK-ROLL== 段抽取 backtrackRoll（发货代码）');

// ── 2. 参数（spec 单一来源）
const PB = {};
['badEvent', 'combat', 'elite', 'boss', 'none'].forEach(k => { PB[k] = SPEC.rescue.backtrack[k].default; });
ok('参数（spec rescue.backtrack）：' + JSON.stringify(PB));
const sum = PB.badEvent + PB.combat + PB.elite + PB.boss + PB.none;
if (Math.abs(sum - 1) > 1e-9) fail('五项概率之和 = ' + sum + ' ≠ 1');
else ok('五项概率之和 = 1');

// ── 3. 与页面运行时参数对拍（web 模块 P.rescue.backtrack 也得跟 spec 一致）
const webP = /rescue: \{[^}]*backtrack: \{([^}]*)\}/.exec(html);
if (!webP) fail('web 模块里找不到 P.rescue.backtrack');
else {
  const webObj = new Function('return {' + webP[1] + '};')();
  const drift = Object.keys(PB).filter(k => JSON.stringify(webObj[k]) !== JSON.stringify(PB[k]));
  if (drift.length) fail('web 模块 P.rescue.backtrack 与 spec 漂移：' + drift.join(','));
  else ok('web 模块 P.rescue.backtrack 与 spec 一致（5 项）');
}

// ── 4. 500 次判定（mulberry32，与生成器同款确定性 RNG）
function makeRng(seed) {
  let a = seed >>> 0;
  return function () {
    a |= 0; a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
const RUNS = 500;
const rng = makeRng(20771);
const tally = { badEvent: 0, combat: 0, elite: 0, boss: 0, none: 0 };
for (let i = 0; i < RUNS; i++) tally[backtrackRoll(rng, PB)] += 1;

console.log('\n  回返遭遇分布（' + RUNS + ' 次）：');
console.log('  判定      次数   实测%   目标%   偏差   判定');
const targets = { badEvent: 45, combat: 30, elite: 15, boss: 8, none: 2 };
Object.keys(targets).forEach(k => {
  const pct = tally[k] / RUNS * 100;
  const d = pct - targets[k];
  const pass = Math.abs(d) <= 5;
  if (!pass) fails++;
  console.log('  ' + k.padEnd(10) + String(tally[k]).padStart(4) + '   ' +
    pct.toFixed(1).padStart(5) + '  ' + String(targets[k]).padStart(5) + '  ' +
    (d >= 0 ? '+' : '') + d.toFixed(1).padStart(5) + 'pp  ' + (pass ? '✓' : '✗ >±5pp'));
});

// ── 5. 确定性：同 seed 双跑一致
const rng2a = makeRng(42), rng2b = makeRng(42);
let detOk = true;
for (let i = 0; i < 200; i++) if (backtrackRoll(rng2a, PB) !== backtrackRoll(rng2b, PB)) detOk = false;
if (detOk) ok('确定性（同 seed 双跑 200 次）: ✓');
else fail('确定性破坏');

console.log('');
if (fails) { console.log('T75 回返判定检查：' + fails + ' 项失败'); process.exit(1); }
console.log('T75 回返判定检查全过：发货代码 500 次分布 ≈ 45/30/15/8/2（±5pp）');
