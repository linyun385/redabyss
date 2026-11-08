// 把存档模块接进 web/index.html：5 处改动，幂等，改完自检
// 1. makeRng 加 getState/setState（唯一必改的引擎代码）
// 2. 末尾引入 save.js + 一段启动检测脚本
// 3. showMap() 存盘
// 4. showGameOver() / showVictory() 清档
// 5. restart() 清档
const fs = require('fs');
const path = require('path');

const HTML = path.join(__dirname, '..', 'web', 'index.html');
const raw = fs.readFileSync(HTML, 'utf8');
const EOL = raw.indexOf('\r\n') >= 0 ? '\r\n' : '\n';
let lines = raw.split(/\r?\n/);

const log = [];
function findLine(pred, from, label) {
  for (let i = from || 0; i < lines.length; i++) if (pred(lines[i], i)) return i;
  throw new Error('找不到: ' + label);
}

/* ── 1. makeRng ─────────────────────────────────────── */
const MARK = 'let s = (seed === undefined ? Date.now() : seed) >>> 0;';
const rngIdx = findLine(l => l.includes(MARK), 0, 'makeRng 的种子行');
if (!raw.includes('fn.getState')) {
  // 旧版结构（5405 那个）：function 行 / let s 行 / return function / s=.. / return .. / }; / }
  const fnStart = rngIdx - 1;
  const fnEnd = rngIdx + 5;              // '  }' 闭合行
  const oldBlock = lines.slice(fnStart, fnEnd + 1);
  const expectEnd = oldBlock[oldBlock.length - 1];
  if (oldBlock[0].trim() !== 'function makeRng(seed) {' || expectEnd.trim() !== '}') {
    throw new Error('makeRng 结构与预期不符，中止：\n' + oldBlock.join('\n'));
  }
  const indent = oldBlock[0].match(/^\s*/)[0];
  const newBlock = [
    indent + 'function makeRng(seed) {',
    indent + '  let s = (seed === undefined ? Date.now() : seed) >>> 0;',
    indent + '  const fn = function () {',
    indent + '    s = (s * 1664525 + 1013904223) >>> 0;',
    indent + '    return s / 4294967296;',
    indent + '  };',
    indent + '  // 2026-11-06 存档用：把闭包里的 LCG 状态暴露出来，不改任何调用方',
    indent + '  fn.getState = function () { return s >>> 0; };',
    indent + '  fn.setState = function (v) { s = v >>> 0; return s; };',
    indent + '  return fn;',
    indent + '}'
  ];
  lines.splice(fnStart, oldBlock.length, ...newBlock);
  log.push('makeRng: 已加 getState/setState');
} else {
  log.push('makeRng: 已改造，跳过');
}

/* ── 2. showMap / showGameOver / showVictory / restart 挂点 ── */
function insertAfterSignature(sig, code, label) {
  const i = findLine(l => l.trim() === sig, 0, label);
  // 幂等判断必须看「签名正下方那一行」，不能看全文 —— 三处清档代码完全相同，全文匹配会误判
  const probe = code.slice(0, 40);
  if (lines[i + 1] && lines[i + 1].includes(probe)) {
    log.push(label + ': 已有挂点，跳过');
    return;
  }
  const indent = lines[i].match(/^\s*/)[0] + '  ';
  lines.splice(i + 1, 0, indent + code);
  log.push(label + ': 已挂');
}

insertAfterSignature('function showMap() {',
  'try { if (window.Save && run && !run.dead && !run.won) Save.save(run); } catch (e) {}',
  'showMap 存盘');
insertAfterSignature('function showGameOver() {',
  'try { if (window.Save) Save.clear(); } catch (e) {}',
  'showGameOver 清档');
insertAfterSignature('function showVictory() {',
  'try { if (window.Save) Save.clear(); } catch (e) {}',
  'showVictory 清档');
insertAfterSignature('function restart() {',
  'try { if (window.Save) Save.clear(); } catch (e) {}',
  'restart 清档');

/* ── 3. 末尾引入 save.js + 启动检查 ── */
let text = lines.join(EOL);
if (text.includes('src="save.js"')) {
  log.push('save.js 引入: 已存在，跳过');
} else {
  const idx = text.lastIndexOf('</script>');
  if (idx < 0) throw new Error('找不到最后一个 </script>');
  const boot = [
    '<script src="save.js"></script>',
    '<script>',
    '/* 存档 v1：启动时若有存档，在职业选择上方挂一条「继续下潜」 */',
    '(function () {',
    '  if (!window.Save) return;',
    '  var data = null;',
    '  try { data = Save.load(); } catch (e) { return; }',
    '  if (!data) return;',
    '  var info = null;',
    '  try { info = Save.info(); } catch (e) {}',
    '  if (!info) return;',
    '  function mount() {',
    '    var face = document.querySelector(".classface");',
    '    if (!face) return false;',
    '    if (document.getElementById("resume-bar")) return true;',
    '    var bar = document.createElement("div");',
    '    bar.id = "resume-bar";',
    '    bar.style.cssText = "margin:0 0 18px;padding:14px 18px;border:1px solid #7a2d24;border-radius:6px;" +',
    '      "background:linear-gradient(90deg,rgba(120,28,20,.28),rgba(40,14,12,.18));display:flex;" +',
    '      "align-items:center;gap:16px;flex-wrap:wrap";',
    '    bar.innerHTML = "<span style=\\"flex:1;min-width:200px;color:#e9d4c8\\">" +',
    '      "上次下潜：<b>" + info.className + "</b> · 第 " + info.depth + " 层 · 生命 " +',
    '      info.hp + "/" + info.maxHp + " · " + info.deckSize + " 张牌 · " + info.ageText +</span>" +',
    '      "<button id=\\"btn-resume-run\\" style=\\"padding:8px 20px;cursor:pointer\\">继续</button>" +',
    '      "<button id=\\"btn-drop-run\\" style=\\"padding:8px 14px;cursor:pointer;opacity:.7\\">放弃</button>";',
    '    face.parentNode.insertBefore(bar, face.parentNode.firstChild);',
    '    document.getElementById("btn-resume-run").addEventListener("click", function () {',
    '      try { playSfx("ui.click"); } catch (e) {}',
    '      try {',
    '        var d = Save.load();',
    '        if (!d) return;',
    '        run = RedAbyss.newRun(d.fields.classId, { seed: 1 });',
    '        Save.applyTo(run, d);',
    '        showMap();',
    '      } catch (e) { console.warn("存档恢复失败", e); }',
    '    });',
    '    document.getElementById("btn-drop-run").addEventListener("click", function () {',
    '      try { playSfx("ui.click"); } catch (e) {}',
    '      try { Save.clear(); } catch (e) {}',
    '      bar.remove();',
    '    });',
    '    return true;',
    '  }',
    '  if (!mount()) {',
    '    document.addEventListener("DOMContentLoaded", function () { mount(); });',
    '    window.addEventListener("load", function () { mount(); });',
    '  }',
    '})();',
    '</script>'
  ].join(EOL);
  text = text.slice(0, idx + '</script>'.length) + EOL + boot + text.slice(idx + '</script>'.length);
  log.push('save.js + 启动检查: 已插入');
}

fs.writeFileSync(HTML, text, 'utf8');

/* ── 4. 自检 ── */
const out = fs.readFileSync(HTML, 'utf8');
const checks = [
  ['makeRng getState', out.includes('fn.getState = function () { return s >>> 0; };')],
  ['makeRng setState', out.includes('fn.setState = function (v) { s = v >>> 0; return s; };')],
  ['save.js 引入', out.includes('<script src="save.js"></script>')],
  ['showMap 存盘', out.includes('Save.save(run)')],
  ['showGameOver 清档', (out.match(/Save\.clear\(\)/g) || []).length >= 3],
  ['启动检查块', out.includes('btn-resume-run')],
  ['原有 showMap 仍在', out.includes('function showMap() {')],
  ['原有 makeRng 只剩两处定义', (out.match(/function makeRng\(seed\) \{/g) || []).length === 2]
];

console.log('改动:', log.join(' | '));
console.log('文件大小:', raw.length, '→', out.length, '(+' + (out.length - raw.length) + ')');
let bad = 0;
for (const [name, ok] of checks) {
  console.log((ok ? '  OK  ' : '  FAIL') + ' ' + name);
  if (!ok) bad++;
}
if (bad) { console.error('有 ' + bad + ' 项未通过'); process.exit(1); }
console.log('全部通过');
