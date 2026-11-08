// 把 FX 接到战斗流程（两处，幂等）
const fs = require('fs');
const path = require('path');

const GAME = 'C:\\Users\\Administrator\\Desktop\\杂七杂八\\红渊\\game';
const HTML = path.join(GAME, 'web', 'index.html');

let src = fs.readFileSync(HTML, 'utf8');
const NL = src.includes('\r\n') ? '\r\n' : '\n';
let done = 0;

function replaceOnce(find, repl, label) {
  const i = src.indexOf(find);
  if (i < 0) { console.error('★ 找不到锚点：' + label); return false; }
  if (src.indexOf(find, i + 1) >= 0) { console.error('★ 锚点不唯一：' + label); return false; }
  src = src.slice(0, i) + repl + src.slice(i + find.length);
  console.log('  ✓ ' + label);
  done++;
  return true;
}

// ── 1) applyCardEffect：记住这张卡的主脉，供血痕上色 ──
if (!src.includes('C._fxVeins')) {
  const find = 'function applyCardEffect(C, card, targetIdx, chainBonus) {' + NL + '    const e = card.effect || {};';
  const repl = 'function applyCardEffect(C, card, targetIdx, chainBonus) {' + NL +
    '    // 动效：记下本次出牌的主脉，render 里给血痕上色用（不影响任何逻辑）' + NL +
    '    if (window.FX) C._fxVeins = (card.veins || []).slice();' + NL +
    '    const e = card.effect || {};';
  if (!replaceOnce(find, repl, 'applyCardEffect 记录主脉')) process.exit(1);
} else {
  console.log('  - applyCardEffect 已接过，跳过');
}

// ── 2) render()：敌人掉血 → 血痕 + 飘字 ──
if (!src.includes('prevHp !== undefined')) {
  const find = '    prev.hps[e.idx] = e.hp;' + NL + '    ea.appendChild(box);';
  const repl = '    // 动效：掉血检测（必须在覆盖 prev 之前读旧值）' + NL +
    '    const prevHp = prev.hps[e.idx];' + NL +
    '    prev.hps[e.idx] = e.hp;' + NL +
    '    ea.appendChild(box);' + NL +
    '    if (prevHp !== undefined && e.hp < prevHp && window.FX) {' + NL +
    '      try { FX.damage(box, prevHp - e.hp, C._fxVeins); } catch (err) {}' + NL +
    '    }';
  if (!replaceOnce(find, repl, 'render 掉血触发血痕')) process.exit(1);
} else {
  console.log('  - render 已接过，跳过');
}

if (!done) { console.log('两处都已存在，无需改动'); process.exit(0); }

fs.writeFileSync(HTML, src, 'utf8');

// 校验
const back = fs.readFileSync(HTML, 'utf8');
const checks = {
  'applyCardEffect 有 _fxVeins': back.includes('C._fxVeins = (card.veins'),
  'render 有掉血检测': back.includes('prevHp !== undefined && e.hp < prevHp'),
  'FX.damage 恰好一处调用': (back.match(/FX\.damage\(/g) || []).length === 1,
  'try/catch 包住（不让特效拖垮逻辑）': back.includes('try { FX.damage('),
  '原 prev.hps 赋值仍在': (back.match(/prev\.hps\[e\.idx\] = e\.hp;/g) || []).length === 2
};
let ok = true;
for (const [k, v] of Object.entries(checks)) {
  console.log(`  ${v ? 'ok  ' : '★FAIL'} ${k}`);
  if (!v) ok = false;
}
console.log(`\n字节 → ${back.length}`);
console.log(ok ? '全部通过' : '有失败项');
process.exit(ok ? 0 : 1);
