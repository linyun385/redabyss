// 修复 _wire_save.js 插入的启动块：原来多行字符串拼接丢了一个引号，导致 `+</span>` 语法错误。
// 这里把整块替换成单行 innerHTML 的干净版本。幂等。
const fs = require('fs');
const path = require('path');

const HTML = path.join(__dirname, '..', 'web', 'index.html');
let text = fs.readFileSync(HTML, 'utf8');
const EOL = text.indexOf('\r\n') >= 0 ? '\r\n' : '\n';

const START = '<script>' + EOL + '/* 存档 v1';
const si = text.indexOf(START);
if (si < 0) {
  console.log('找不到启动块，可能已修复或未插入');
  process.exit(0);
}
const ei = text.indexOf('</script>', si);
if (ei < 0) { console.error('启动块没有结束标签'); process.exit(1); }

const oldLen = ei + '</script>'.length - si;

const boot = [
  '<script>',
  '/* 存档 v1：启动时若有存档，在职业选择上方挂一条「继续下潜」 */',
  '(function () {',
  '  if (!window.Save) return;',
  '  var info = null;',
  '  try { if (!Save.has()) return; info = Save.info(); } catch (e) { return; }',
  '  if (!info) return;',
  '  function mount() {',
  '    var face = document.querySelector(".classface");',
  '    if (!face) return false;',
  '    if (document.getElementById("resume-bar")) return true;',
  '    var bar = document.createElement("div");',
  '    bar.id = "resume-bar";',
  '    bar.style.cssText = "margin:0 0 18px;padding:14px 18px;border:1px solid #7a2d24;border-radius:6px;background:linear-gradient(90deg,rgba(120,28,20,.28),rgba(40,14,12,.18));display:flex;align-items:center;gap:16px;flex-wrap:wrap";',
  '    var label = document.createElement("span");',
  '    label.style.cssText = "flex:1;min-width:200px;color:#e9d4c8";',
  '    label.innerHTML = "上次下潜：<b>" + info.className + "</b> · 第 " + info.depth + " 层 · 生命 " + info.hp + "/" + info.maxHp + " · " + info.deckSize + " 张牌 · " + info.ageText;',
  '    var btnGo = document.createElement("button");',
  '    btnGo.id = "btn-resume-run";',
  '    btnGo.textContent = "继续";',
  '    btnGo.style.cssText = "padding:8px 20px;cursor:pointer";',
  '    var btnDrop = document.createElement("button");',
  '    btnDrop.id = "btn-drop-run";',
  '    btnDrop.textContent = "放弃";',
  '    btnDrop.style.cssText = "padding:8px 14px;cursor:pointer;opacity:.7";',
  '    bar.appendChild(label);',
  '    bar.appendChild(btnGo);',
  '    bar.appendChild(btnDrop);',
  '    face.parentNode.insertBefore(bar, face.parentNode.firstChild);',
  '    btnGo.addEventListener("click", function () {',
  '      try { playSfx("ui.click"); } catch (e) {}',
  '      try {',
  '        var d = Save.load();',
  '        if (!d) return;',
  '        run = RedAbyss.newRun(d.fields.classId, { seed: 1 });',
  '        Save.applyTo(run, d);',
  '        showMap();',
  '      } catch (e) { console.warn("存档恢复失败", e); }',
  '    });',
  '    btnDrop.addEventListener("click", function () {',
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

text = text.slice(0, si) + boot + text.slice(ei + '</script>'.length);
fs.writeFileSync(HTML, text, 'utf8');

// 自检：新块能否被 new Function 解析
const m = [...text.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(x => x[1]);
console.log('内联 script 块数:', m.length, '| 旧块长度:', oldLen, '→ 新块长度:', boot.length);
let bad = 0;
m.forEach((code, i) => {
  try { new Function(code); }
  catch (e) { bad++; console.error('  script[' + i + '] 语法错误: ' + e.message); }
});
if (bad) { console.error('有 ' + bad + ' 块语法错误'); process.exit(1); }
console.log('全部 ' + m.length + ' 块语法可解析');
