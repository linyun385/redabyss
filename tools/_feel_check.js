/* tools/_feel_check.js — T27「战斗顺滑（可测量）」补做实测（临时脚本，只读）
 * 用法: node tools/_feel_check.js
 * 只做两件事，不写任何文件、不改任何游戏代码：
 *   A. 引擎层响应实测：加载 engine/core.js，模拟「出牌→结束回合→敌人动作」纯逻辑，
 *      多局多样本取 中位/p95/max，对照 T27 门槛（出牌<100ms、结束回合→敌人动作<200ms）。
 *   B. UI 动画时序代码审计：正则抽取 web/index.html 内联 CSS 的 animation/transition 声明，
 *      换算成毫秒（含迭代次数），供 docs/FEEL.md 数值表落档。
 * 注：node 无 DOM，浏览器端到端（点击→渲染完成）无法在此实测，见 FEEL.md 说明。
 */
'use strict';
const fs = require('fs');
const path = require('path');
const E = require(path.join(__dirname, '..', 'engine', 'core.js'));

const fmtMs = (ns) => (Number(ns) / 1e6).toFixed(3) + 'ms';
function quantile(sorted, p) { return sorted[Math.min(sorted.length - 1, Math.floor(p * sorted.length))]; }
function stats(arr) {
  const s = [...arr].sort((a, b) => a - b);
  const median = s.length % 2 ? s[(s.length - 1) / 2] : (s[s.length / 2 - 1] + s[s.length / 2]) / 2;
  return { median, p95: quantile(s, 0.95), max: s[s.length - 1], n: s.length };
}
const now = () => process.hrtime.bigint();

/* ── A. 引擎层实测 ─────────────────────────────────────────── */
// 与 enemies/ 现役数据同构的实验体（intent_pattern + hp），双敌制造多目标伤害路径
const FOES = [
  { id: 'feel_a', name: '实测体·甲', hp: 40, intent_pattern: [{ type: 'attack', value: 6 }] },
  { id: 'feel_b', name: '实测体·乙', hp: 28, intent_pattern: [{ type: 'defend', value: 5 }, { type: 'attack', value: 7 }] }
];
function freshCombat(seed, cls) {
  const run = E.newRun(cls, { seed });
  run.depth = 3; // 干旱空洞区：常规层规则（dry），不带 tick 干扰
  return E.startCombat(run, FOES);
}
function pickPlayable(C) {
  for (let i = 0; i < C.hand.length; i++) {
    const c = C.hand[i];
    if ((c.energy || 0) <= C.energy) return i;
  }
  return -1;
}

const t_play = [], t_endTurn = [], t_chain3 = [], t_reject = [], t_start = [], t_world = [];
const BATTLES = 400;
let turnsTotal = 0, playsTotal = 0;

for (let b = 0; b < BATTLES; b++) {
  const seed = 20261103 + b;
  let t0 = now();
  const C = freshCombat(seed, 'diver');
  t_start.push(Number(now() - t0));

  let guard = 0;
  while (!C.over && guard++ < 60) {
    // 连打 3 张（能量 3，前几回合可打满）：模拟「连续快速出牌」的引擎开销
    let played = 0, t1 = now();
    while (played < 3) {
      const i = pickPlayable(C);
      if (i < 0) break;
      const card = C.hand[i];
      const needsT = card.effect && card.effect.target === 'single' && (card.effect.damage || (card.effect.special || []).length);
      const tgt = needsT ? C.enemies.findIndex(e => !e.dead) : undefined;
      t0 = now();
      const r = E.playCard(C, i, tgt);
      t_play.push(Number(now() - t0));
      playsTotal++;
      if (!r.ok) break;
      played++;
    }
    if (played === 3) t_chain3.push(Number(now() - t1));
    if (C.over) break;
    // 能量不足拒绝路径（卡牌不可用的引擎侧响应）
    if (C.hand.length && pickPlayable(C) < 0) {
      t0 = now();
      E.playCard(C, 0, 0);
      t_reject.push(Number(now() - t0));
    }
    // 结束回合：敌人行动 + 状态结算 + 意图/阶段推进 + 下一回合开始（引擎一次同步调用）
    t0 = now();
    E.endTurn(C);
    t_endTurn.push(Number(now() - t0));
    turnsTotal++;
  }
}

// 苍民切世（世界切换的引擎侧开销；UI 过渡是 CSS 400ms，见 B）
for (let i = 0; i < 200; i++) {
  const C = freshCombat(20261103 + i, 'cangmin');
  const t0 = now();
  const r = E.switchWorld(C, 'dream');
  t_world.push(Number(now() - t0));
  if (!r.ok) { t_world.pop(); } // 只统计成功切世
}

const p = (x) => fmtMs(x);
console.log('=== T27 引擎层响应实测（node ' + process.version + ', ' + process.platform + ', ' + BATTLES + ' 局） ===');
console.log('startCombat（建局）            : 中位 ' + p(stats(t_start).median) + '  p95 ' + p(stats(t_start).p95) + '  max ' + p(stats(t_start).max));
console.log('playCard 单次（出牌结算）      : 中位 ' + p(stats(t_play).median) + '  p95 ' + p(stats(t_play).p95) + '  max ' + p(stats(t_play).max) + '  样本 ' + stats(t_play).n);
console.log('playCard×3 连打（不打架链路）  : 中位 ' + p(stats(t_chain3).median) + '  p95 ' + p(stats(t_chain3).p95) + '  max ' + p(stats(t_chain3).max) + '  样本 ' + stats(t_chain3).n);
console.log('playCard 拒绝（卡不可用响应）  : 中位 ' + p(stats(t_reject).median) + '  p95 ' + p(stats(t_reject).p95) + '  max ' + p(stats(t_reject).max) + '  样本 ' + stats(t_reject).n);
console.log('endTurn（敌人行动+推进全链）   : 中位 ' + p(stats(t_endTurn).median) + '  p95 ' + p(stats(t_endTurn).p95) + '  max ' + p(stats(t_endTurn).max) + '  样本 ' + stats(t_endTurn).n);
console.log('switchWorld（切世纯逻辑）      : 中位 ' + p(stats(t_world).median) + '  p95 ' + p(stats(t_world).p95) + '  max ' + p(stats(t_world).max) + '  样本 ' + stats(t_world).n);
console.log('合计: 回合 ' + turnsTotal + ', 出牌 ' + playsTotal);
console.log('');
const ms = (ns) => ns / 1e6; // 门槛对比统一换算成毫秒
console.log('门槛对照: 出牌<100ms → max=' + p(stats(t_play).max) + (ms(stats(t_play).max) < 100 ? ' 达标' : ' 超标') +
  '；结束回合→敌人动作<200ms → endTurn 全链 max=' + p(stats(t_endTurn).max) + (ms(stats(t_endTurn).max) < 200 ? ' 达标' : ' 超标'));

/* ── B. UI 动画时序审计（读 web/index.html 内联 CSS） ───────── */
const html = fs.readFileSync(path.join(__dirname, '..', 'web', 'index.html'), 'utf8');
const lines = html.split('\n');
const TIME = /(\d*\.?\d+)(ms|s)\b/g;
function toMs(num, unit) { return parseFloat(num) * (unit === 'ms' ? 1 : 1000); }
function parseAnim(line) {
  // 例: animation: resflash .5s steps(2) 2;  /  cardfly .22s ease-in forwards
  const noSteps = line.replace(/steps?\([^)]*\)/g, 'EASING');
  const times = [...noSteps.matchAll(TIME)];
  if (!times.length) return null;
  const dur = toMs(times[0][1], times[0][2]);
  const tail = noSteps.slice(noSteps.indexOf(times[0][0]) + times[0][0].length);
  const nums = [...tail.matchAll(/\b(\d+(?:\.\d+)?)\b/g)].map(m => parseFloat(m[1]));
  const iters = /\binfinite\b/.test(tail) ? Infinity : (nums.length ? nums[0] : 1);
  return { dur, iters };
}
function parseTrans(line) {
  // transition: transform .15s ease, border-color .15s ...  → 逐段取首个时间
  return line.split(',').map(seg => {
    const m = [...seg.matchAll(TIME)][0]; // matchAll 返回 match 对象，下标 1/2 是数值/单位
    return m ? toMs(m[1], m[2]) : null;
  }).filter(x => x !== null && !isNaN(x));
}
const found = [];
lines.forEach((ln, i) => {
  let m = ln.match(/animation:\s*([^;]+);/);
  if (m) {
    const a = parseAnim(m[1]);
    if (a) found.push({ line: i + 1, kind: 'animation', raw: m[1].trim(), one: a.dur, total: a.dur * a.iters, inf: a.iters === Infinity });
    return;
  }
  m = ln.match(/transition:\s*([^;]+);/);
  if (m) {
    const ds = parseTrans(m[1]);
    if (ds.length) found.push({ line: i + 1, kind: 'transition', raw: m[1].trim(), one: Math.max(...ds), total: Math.max(...ds), inf: false });
  }
});
console.log('');
console.log('=== UI 动画时序审计（web/index.html 内联 CSS，共 ' + found.length + ' 条声明） ===');
found.forEach(f => {
  const tag = f.inf ? '（无限循环·常驻氛围，不计入动作时长）' : (f.total > 500 ? '  ← 单次总时长超 500ms' : '');
  console.log('L' + String(f.line).padStart(5) + '  ' + f.kind.padEnd(10) +
    ' 单次 ' + String(Math.round(f.one)).padStart(5) + 'ms' +
    (f.inf ? '' : '  总 ' + String(Math.round(f.total)).padStart(5) + 'ms') +
    '  ' + f.raw.slice(0, 72) + tag);
});
const oneshotOver = found.filter(f => !f.inf && f.total > 500);
console.log('');
console.log('>500ms 的一次性动作/反馈声明: ' + (oneshotOver.length ? oneshotOver.map(f => 'L' + f.line + ' ' + Math.round(f.total) + 'ms').join(' | ') : '无'));
console.log('（注：常驻循环 atkpulse/mblink/glowbreath/dreampulse/dyingpulse 等为状态指示，不属于 T27 的「动作」口径，单列）');
