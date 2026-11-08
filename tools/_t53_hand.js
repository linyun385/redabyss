// T53 交互改版补丁：扇形手牌 + 点击详情 + 拖动出牌。一次性 wire 脚本（对 web/index.html）。
'use strict';
const fs = require('fs');
const path = require('path');
const p = path.join(__dirname, '..', 'web', 'index.html');
let s = fs.readFileSync(p, 'utf8');
let n = 0;
function rep(oldStr, newStr, tag) {
  const c = s.split(oldStr).length - 1;
  if (c !== 1) { console.error('锚点失败 [' + tag + '] 出现 ' + c + ' 次'); process.exit(1); }
  s = s.replace(oldStr, newStr);
  n++;
  console.log('ok', tag);
}

/* ── 1. CSS：#hand 从 flex 改为扇形容器 ── */
rep(`  #hand { display: flex; gap: 8px; min-height: 128px; flex-wrap: wrap; justify-content: center; align-items: flex-start; }`,
`  #hand { position: relative; height: 238px; min-height: 238px; }`,
'hand container');

/* ── 2. CSS：手牌扇形变换 + 拖拽态（插在 .card .cflavor 规则之后） ── */
rep(`  .card .cflavor {
    margin-top: auto; padding: 3px 8px 6px; color: #5a4446; font-size: 10px;
    display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
  }`,
`  .card .cflavor {
    margin-top: auto; padding: 3px 8px 6px; color: #5a4446; font-size: 10px;
    display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
  }
  /* ── 手牌扇形叠放（T53：点击=详情，拖出=打出） ── */
  #hand .card {
    position: absolute; left: 50%; bottom: 4px; margin-left: -75px;
    --fan: translateX(calc(-50% + var(--tx, 0px))) translateY(var(--ty, 0px)) rotate(var(--rot, 0deg));
    transform: var(--fan);
    transform-origin: 50% 100%;
  }
  #hand .card:hover:not(.dimmed):not(.wrongworld):not(.dragging) {
    transform: translateX(calc(-50% + var(--tx, 0px))) translateY(calc(var(--ty, 0px) - 46px)) rotate(0deg) scale(1.06);
    z-index: 99;
  }
  #hand .card.selected {
    transform: translateX(calc(-50% + var(--tx, 0px))) translateY(calc(var(--ty, 0px) - 46px)) rotate(0deg);
    z-index: 98;
  }
  #hand .card.dragging { transition: none !important; z-index: 100; cursor: grabbing; }`,
'fan css');

/* ── 3. CSS：T37 的整体上浮规则改为只作用于非手牌（奖励卡） ── */
rep(`  .card:not(.dimmed):not(.wrongworld):hover { transform: translateY(-4px); }`,
`  #flow-cards .card:not(.dimmed):not(.wrongworld):hover { transform: translateY(-4px); }`,
'flow hover scope');

/* ── 4. CSS：减动效 / perf-low 保留扇形、只取消浮起 ── */
rep(`    .card:not(.dimmed):hover, .mnode.pickable:hover, .relicrow .relic:hover { transform: none; }
  }`,
`    #flow-cards .card:not(.dimmed):hover, .mnode.pickable:hover, .relicrow .relic:hover { transform: none; }
    #hand .card:hover:not(.dimmed):not(.dragging) { transform: var(--fan); }
  }`,
'reduced motion');
rep(`  body.perf-low .card:not(.dimmed):hover, body.perf-low .mnode.pickable:hover, body.perf-low .relicrow .relic:hover { transform: none; }`,
`  body.perf-low #flow-cards .card:not(.dimmed):hover, body.perf-low .mnode.pickable:hover, body.perf-low .relicrow .relic:hover { transform: none; }
  body.perf-low #hand .card:hover:not(.dragging) { transform: var(--fan); }`,
'perf low');

/* ── 5. CSS：详情弹层（接在扇形 CSS 的 dragging 规则之后） ── */
rep(`  #hand .card.dragging { transition: none !important; z-index: 100; cursor: grabbing; }`,
`  #hand .card.dragging { transition: none !important; z-index: 100; cursor: grabbing; }
  /* ── T53 卡牌详情弹层 ── */
  #card-detail { position: fixed; inset: 0; background: rgba(0, 0, 0, .6); display: flex; align-items: center; justify-content: center; z-index: 55; }
  #cd-box { display: flex; gap: 18px; background: #120a0b; border: 1px solid var(--red); border-radius: 6px; padding: 20px; max-width: 92vw; }
  #cd-card .card { width: 190px; height: 267px; cursor: default; position: relative; }
  #cd-card .card .cname { font-size: 15px; }
  #cd-side { width: 320px; display: flex; flex-direction: column; }
  #cd-side h3 { color: var(--red-hi); font-weight: normal; letter-spacing: 2px; margin: 0 0 10px; font-size: 17px; }
  #cd-lines { flex: 1 1 auto; font-size: 13px; color: var(--text); line-height: 1.7; }
  #cd-lines .warn { color: var(--red-hi); }
  #cd-lines .osub { color: var(--dim); font-size: 12px; margin-top: 6px; }
  #cd-side .btnrow { display: flex; gap: 10px; margin-top: 12px; }
  #cd-side button { background: #1a0d0e; color: var(--red-hi); border: 1px solid var(--red); border-radius: 4px; font-family: inherit; padding: 6px 18px; cursor: pointer; }
  #cd-side button:disabled { opacity: .35; cursor: not-allowed; }
  #cd-side button:hover:not(:disabled) { border-color: var(--red-hi); }
  html[data-theme="B"] #cd-box, html[data-theme="C"] #cd-box { background: var(--paper); }
  html[data-theme="B"] #cd-lines, html[data-theme="C"] #cd-lines { color: var(--ink); }
  html[data-theme="B"] #cd-side button, html[data-theme="C"] #cd-side button { background: #cfc3ae; }`,
'detail css');

/* ── 6. HTML：详情弹层结构（插在 #toast 之前） ── */
rep(`<div id="toast"></div>`,
`<div id="card-detail" class="hidden">
  <div id="cd-box">
    <div id="cd-card"></div>
    <div id="cd-side">
      <h3 id="cd-name"></h3>
      <div id="cd-lines"></div>
      <div class="btnrow"><button id="cd-play">打出</button><button id="cd-cancel">收回</button></div>
    </div>
  </div>
</div>
<div id="toast"></div>`,
'detail html');

/* ── 7. JS：手牌交互从 click 改为 pointer 拖拽/详情 ── */
rep(`    d.addEventListener('click', () => {
      if (!C || C.over) return;
      if (pending === i) { pending = null; render(); return; }
      if (worldMismatch) { shakeCard(d); toast(card.dream ? '这来自梦里，醒着的手握不住。' : '醒着的东西进不了这个深度。'); return; }
      if (reason) {
        shakeCard(d);
        // T40：第一次能量不足，用提示句代替冷冰冰的原因
        if (/能量不足/.test(reason)) {
          playSfx('state.energy_empty');
          if (run.stats.battles < 3 && onceHint('energy', '能量见底了。结束回合，它会满上。')) return;
        }
        toast(reason);
        return;
      }
      if (needsTarget(card)) { pending = i; render(); toast('选择一个目标'); }
      else doPlay(i, undefined);
    });`,
`    d.addEventListener('pointerdown', (ev) => startCardPointer(ev, d, card, i, worldMismatch));`,
'hand pointer');

/* ── 8. JS：renderHand 尾部调用 layoutFan ── */
rep(`    hand.appendChild(d);
  });

  const bw = document.getElementById('btn-world');`,
`    hand.appendChild(d);
  });
  layoutFan();

  const bw = document.getElementById('btn-world');`,
'layout fan call');

/* ── 9. JS：拖拽引擎 + 详情面板（插在 shakeCard 定义之后） ── */
rep(`/* 卡牌不可用：轻微抖动（浮字原因走 toast） */
function shakeCard(d) {
  d.classList.remove('shakeit'); void d.offsetWidth; d.classList.add('shakeit');
  setTimeout(() => d.classList.remove('shakeit'), 320);
}`,
`/* 卡牌不可用：轻微抖动（浮字原因走 toast） */
function shakeCard(d) {
  d.classList.remove('shakeit'); void d.offsetWidth; d.classList.add('shakeit');
  setTimeout(() => d.classList.remove('shakeit'), 320);
}

/* ───────── T53 手牌交互：扇形布局 / 点击详情 / 拖动打出 ───────── */
function layoutFan() {
  const cards = [...document.querySelectorAll('#hand .card')];
  const n = cards.length;
  if (!n) return;
  const mid = (n - 1) / 2;
  const hand = document.getElementById('hand');
  const span = Math.min(66, Math.max(38, (hand.clientWidth - 170) / Math.max(n - 1, 1)));
  const depth = mid > 0 ? Math.min(26, 210 * 0.12) : 0;
  const k = mid > 0 ? depth / (mid * mid) : 0;
  cards.forEach((el, i) => {
    const off = i - mid;
    el.style.setProperty('--tx', (off * span).toFixed(1) + 'px');
    el.style.setProperty('--ty', (off * off * k).toFixed(1) + 'px');
    el.style.setProperty('--rot', (off * (n > 1 ? 2.2 : 0)).toFixed(2) + 'deg');
    el.style.zIndex = i + 1;
  });
}
function startCardPointer(ev, d, card, i, worldMismatch) {
  if (ev.button !== 0 || !C || C.over) return;
  const startX = ev.clientX, startY = ev.clientY;
  let dragging = false;
  const worldBad = worldMismatch || (run.classId === 'cangmin' && !!card.dream !== (C.world === 'dream'));
  const onMove = (e2) => {
    const dx = e2.clientX - startX, dy = e2.clientY - startY;
    if (!dragging && Math.hypot(dx, dy) > 8) {
      dragging = true;
      try { d.setPointerCapture(ev.pointerId); } catch (err) {}
      d.classList.add('dragging');
      if (needsTarget(card)) [...document.querySelectorAll('#enemy-area .enemy:not(.dead)')].forEach(b => b.classList.add('targetable'));
    }
    if (dragging) {
      d.style.transform = 'translate(' + dx + 'px,' + (dy - 18) + 'px) rotate(' + Math.max(-8, Math.min(8, dx * 0.06)) + 'deg) scale(1.05)';
      d.style.zIndex = 100;
    }
  };
  const onUp = (e2) => {
    d.removeEventListener('pointermove', onMove);
    d.removeEventListener('pointerup', onUp);
    d.removeEventListener('pointercancel', onCancel);
    d.classList.remove('dragging');
    [...document.querySelectorAll('#enemy-area .enemy.targetable')].forEach(b => b.classList.remove('targetable'));
    d.style.transform = ''; d.style.zIndex = '';
    layoutFan();
    if (!dragging) { openCardDetail(i); return; }
    // T40 首次能量不足提示（拖出失败也走一次）
    const reason = (() => {
      if (worldBad) return card.dream ? '这来自梦里，醒着的手握不住。' : '醒着的东西进不了这个深度。';
      return playBlockReason(card);
    })();
    if (reason) {
      shakeCard(d);
      if (/能量不足/.test(reason) && run.stats.battles < 3 && onceHint('energy', '能量见底了。结束回合，它会满上。')) return;
      toast(reason);
      return;
    }
    const hit = document.elementFromPoint(e2.clientX, e2.clientY);
    const ebox = hit && hit.closest ? hit.closest('#enemy-area .enemy') : null;
    const onEnemy = ebox && !ebox.classList.contains('dead');
    if (needsTarget(card)) {
      if (onEnemy) { doPlay(i, +ebox.id.split('-')[1]); return; }
      pending = null;
      toast('把它拖到目标身上才算数。');
      render();
      return;
    }
    if (e2.clientY < startY - 24 || onEnemy) { doPlay(i, undefined); return; }
    // 收回：落回手牌区，什么都不发生
  };
  const onCancel = () => {
    d.removeEventListener('pointermove', onMove);
    d.removeEventListener('pointerup', onUp);
    d.classList.remove('dragging');
    [...document.querySelectorAll('#enemy-area .enemy.targetable')].forEach(b => b.classList.remove('targetable'));
    d.style.transform = ''; d.style.zIndex = '';
    layoutFan();
  };
  d.addEventListener('pointermove', onMove);
  d.addEventListener('pointerup', onUp);
  d.addEventListener('pointercancel', onCancel);
}
function openCardDetail(i) {
  if (!C || C.over || !C.hand[i]) return;
  const card = C.hand[i];
  const worldBad = run.classId === 'cangmin' && !!card.dream !== (C.world === 'dream');
  const box = document.getElementById('card-detail');
  const cc = document.getElementById('cd-card');
  cc.textContent = '';
  cc.appendChild(renderCardStatic(card));
  const reason = worldBad ? (card.dream ? '这来自梦里，醒着的手握不住。' : '醒着的东西进不了这个深度。') : playBlockReason(card);
  const lines = [];
  if (worldBad) lines.push('<div class="warn">' + reason + '</div>');
  if (card.cost_type !== 'none' && card.cost_text) lines.push('<div>代价：' + card.cost_text + '</div>');
  if (needsTarget(card)) lines.push('<div class="osub">打出后要选一个目标：把它拖到敌人身上，或按「打出」再点敌人。</div>');
  if (reason && !worldBad) lines.push('<div class="warn">现在打不出：' + reason + '</div>');
  if (card.upgrade && !card.upgraded) lines.push('<div class="osub">这张牌可以在营火升级。</div>');
  document.getElementById('cd-name').textContent = card.name;
  document.getElementById('cd-lines').innerHTML = lines.join('');
  document.getElementById('cd-play').disabled = !!(reason || worldBad);
  document.getElementById('cd-play').onclick = () => {
    box.classList.add('hidden');
    if (needsTarget(card)) { pending = i; render(); toast('选择一个目标'); }
    else doPlay(i, undefined);
  };
  box.classList.remove('hidden');
}`,
'shake card anchor');

/* ── 10. Esc 同时收起详情面板 ── */
rep(`document.addEventListener('keydown', (ev) => {
  if (ev.key === 'Escape') document.getElementById('help-overlay').classList.add('hidden');
});`,
`document.addEventListener('keydown', (ev) => {
  if (ev.key === 'Escape') {
    document.getElementById('help-overlay').classList.add('hidden');
    document.getElementById('card-detail').classList.add('hidden');
    if (pending !== null) { pending = null; if (window.G && window.G.phase === 'combat') render(); }
  }
});`,
'esc');

fs.writeFileSync(p, s, 'utf8');
console.log('全部 ' + n + ' 处补丁完成');
