// T25：苍民 DLC 前端接入（第四职业 + 双世界 UI）
'use strict';
const fs = require('fs');
const path = require('path');
const ROOT = path.join(__dirname, '..');
let s = fs.readFileSync(path.join(ROOT, 'web/index.html'), 'utf8');
let n = 0;
function rep(anchor, replacement, tag) {
  if (!s.includes(anchor)) { console.error('FAIL 锚点未找到: ' + tag); process.exit(1); }
  s = s.replace(anchor, replacement);
  n++;
}

// 1. RAW 同步（cangmin 四包）
{
  const m = s.match(/const RAW = (\{.*?\});\n/);
  if (!m) { console.error('RAW 未找到'); process.exit(1); }
  const raw = JSON.parse(m[1]);
  raw.cangmin = JSON.parse(fs.readFileSync(path.join(ROOT, 'cards/cangmin.json'), 'utf8'));
  raw.cngEnemies = JSON.parse(fs.readFileSync(path.join(ROOT, 'enemies/cangmin.json'), 'utf8'));
  raw.cngRelics = JSON.parse(fs.readFileSync(path.join(ROOT, 'relics/cangmin.json'), 'utf8'));
  raw.cngEvents = JSON.parse(fs.readFileSync(path.join(ROOT, 'events/cangmin.json'), 'utf8'));
  s = s.replace(m[0], 'const RAW = ' + JSON.stringify(raw) + ';\n');
}

// 2. CLASS_POOL
rep(`const CLASS_POOL = { diver: RAW.diver.map(adaptCard), tremor: RAW.tremor.map(adaptCard), anmin: RAW.anmin.map(adaptCard) };`,
`const CLASS_POOL = { diver: RAW.diver.map(adaptCard), tremor: RAW.tremor.map(adaptCard), anmin: RAW.anmin.map(adaptCard), cangmin: RAW.cangmin.map(adaptCard) };`, 'class pool');

// 3. 第四职业卡
rep(`      <button class="class-card" data-class="anmin">`,
`      <button class="class-card" data-class="cangmin">
        <h2>疯先知</h2>
        <p>苍民。一千三百年来第一批重新梦见伊格的人。城里人叫你疯先知，你没有纠正。</p>
        <p class="stat">醒 30 / 梦 60　清醒度 3　双牌堆：清醒与梦</p>
      </button>
      <button class="class-card" data-class="anmin">`, 'fourth class');

// 4. HUD：清醒度 + 梦境生命
rep(`      <span id="hud-parts-wrap" class="hidden"><span class="k">零件 </span><span class="v" id="hud-parts" style="cursor:pointer" title="点击打开回收面板">0</span></span>`,
`      <span id="hud-parts-wrap" class="hidden"><span class="k">零件 </span><span class="v" id="hud-parts" style="cursor:pointer" title="点击打开回收面板">0</span></span>
      <span id="hud-clarity-wrap" class="hidden"><span class="k">清醒度 </span><span class="v" id="hud-clarity">0</span></span>
      <span id="hud-dream-wrap" class="hidden"><span class="k">梦境 </span><span class="v" id="hud-dream">60</span></span>`, 'hud clarity');

// 5. CSS：双世界
rep(`  .enemy { transition: opacity .45s ease; }`,
`  /* 苍民双世界：醒（冷灰蓝）/ 梦（暗红脉动） */
  #screen-combat.world-dream { transition: background .4s ease; background: #190708; }
  #screen-combat.world-wake { transition: background .4s ease; background: #101318; }
  #screen-combat.world-dream::before {
    content: ''; position: absolute; inset: 0; pointer-events: none;
    box-shadow: inset 0 0 70px rgba(150, 25, 30, .35);
    animation: dreampulse 2s ease-in-out infinite;
  }
  @keyframes dreampulse { 50% { box-shadow: inset 0 0 40px rgba(150, 25, 30, .18); } }
  .card.wrongworld { opacity: .3; }
  .v.clarity-low { animation: atkpulse 1.2s ease-in-out infinite; color: var(--red-hi); }
  .enemy { transition: opacity .45s ease; }`, 'dual world css');

// 6. render：清醒度/梦境 HUD、世界类、协议横幅之后
rep(`  const pb = $('#protocol-banner');`,
`  const cw = $('#hud-clarity-wrap');
  if (run.classId === 'cangmin') {
    cw.classList.remove('hidden');
    const ce = $('#hud-clarity');
    ce.textContent = run.clarity + '/' + (run.clarityMax || 5);
    ce.classList.toggle('clarity-low', run.clarity < 3);
  } else cw.classList.add('hidden');
  const dw = $('#hud-dream-wrap');
  if (run.classId === 'cangmin' && C && C.world === 'dream') {
    dw.classList.remove('hidden');
    $('#hud-dream').textContent = C.dreamHp + '/' + C.dreamMaxHp;
  } else dw.classList.add('hidden');
  const pb = $('#protocol-banner');`, 'render clarity');
// 世界类与切世按钮文案在 render 末尾处理：找 render 的结束位置不现实，改挂在世界类到 #screen-combat 上
rep(`  showScreen('#screen-combat');
  render();
}

function applyRelicTurnStart() {`,
`  showScreen('#screen-combat');
  document.getElementById('screen-combat').classList.toggle('world-dream', C.world === 'dream');
  document.getElementById('screen-combat').classList.toggle('world-wake', C.world !== 'dream');
  render();
}

function applyRelicTurnStart() {`, 'world class on combat start');

// 7. render() 里同步世界类与切世按钮（combat 中每次 render）
rep(`  $('#pile-draw').textContent = '抽牌堆 ' + C.drawPile.length;`,
`  const bw = document.getElementById('btn-world');
  if (run.classId === 'cangmin') {
    const sc = document.getElementById('screen-combat');
    sc.classList.toggle('world-dream', C.world === 'dream');
    sc.classList.toggle('world-wake', C.world !== 'dream');
    if (bw) {
      bw.classList.remove('hidden');
      const inDream = C.world === 'dream';
      bw.textContent = inDream ? '醒来' : '入梦';
      bw.disabled = (inDream && C.dreamLocked) || (!inDream && run.clarity <= 0);
      bw.title = inDream ? '结束这次入梦' : '消耗 1 点清醒度入梦';
    }
  } else if (bw) {
    bw.classList.add('hidden');
    document.getElementById('screen-combat').classList.remove('world-dream');
    document.getElementById('screen-combat').classList.add('world-wake');
  }
  $('#pile-draw').textContent = '抽牌堆 ' + C.drawPile.length;`, 'render world sync');

// 8. 切世按钮（HTML）
rep(`        <button id="btn-end">结束回合</button>`,
`        <button id="btn-world" class="hidden">入梦</button>
        <button id="btn-end">结束回合</button>`, 'world button html');
rep(`$('#btn-end').addEventListener('click', () => {`,
`$('#btn-world').addEventListener('click', () => {
  if (!C || C.over || run.classId !== 'cangmin') return;
  const target = C.world === 'dream' ? 'wake' : 'dream';
  const r = RedAbyss.switchWorld(C, target);
  toast(r.ok ? (target === 'dream' ? '你睡着了。' : '你醒了。') : r.msg);
  render();
});
document.addEventListener('keydown', (ev) => {
  if (ev.key === 'w' || ev.key === 'W') { const b = document.getElementById('btn-world'); if (b && !b.disabled && !b.classList.contains('hidden')) b.click(); }
});
$('#btn-end').addEventListener('click', () => {`, 'world button bind');

// 9. 手牌世界不匹配：wrongworld 视觉
rep(`    const d = el('div', 'card' +
      (card.cost_type !== 'none' ? ' costly' : '') +
      (card.upgraded ? ' upgraded' : '') +
      (reason ? ' dimmed' : '') +
      (pending === i ? ' selected' : ''));`,
`    const worldMismatch = run.classId === 'cangmin' && !!card.dream !== (C.world === 'dream');
    const d = el('div', 'card' +
      (card.cost_type !== 'none' ? ' costly' : '') +
      (card.upgraded ? ' upgraded' : '') +
      (worldMismatch ? ' wrongworld' : '') +
      (reason ? ' dimmed' : '') +
      (pending === i ? ' selected' : ''));`, 'wrongworld visual');
// 点击提示文案
rep(`      if (reason) { toast(reason); return; }`,
`      if (worldMismatch) { toast(card.dream ? '这来自梦里，醒着的手握不住。' : '醒着的东西进不了这个深度。'); return; }
      if (reason) { toast(reason); return; }`, 'wrongworld toast');

// 10. 苍民事件/遗物池
rep(`    let pool = run.isEcho ? RAW.anminEvents.filter(x => x.layer === run.depth) : RAW.events.filter(x => x.layer === run.depth);`,
`    let pool = run.isEcho ? RAW.anminEvents.filter(x => x.layer === run.depth)
      : run.classId === 'cangmin' ? RAW.cngEvents.filter(x => x.layer === run.depth)
      : RAW.events.filter(x => x.layer === run.depth);`, 'cng event pool');
rep(`  const srcAll = run.isEcho ? RAW.relics.concat(RAW.anminRelics) : RAW.relics;`,
`  const srcAll = run.isEcho ? RAW.relics.concat(RAW.anminRelics) : run.classId === 'cangmin' ? RAW.relics.concat(RAW.cngRelics) : RAW.relics;`, 'cng relic pool');

// 11. 引擎建局后 run.clarity 等已存在；苍民开局默认醒侧

fs.writeFileSync(path.join(ROOT, 'web/index.html'), s, 'utf8');
console.log('T25 前端接入完成，共 ' + n + ' 处');
