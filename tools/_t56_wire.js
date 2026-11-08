/* T56 接线脚本：把 tools/mapgen.js 同步注入 web/index.html 的 mapgen-lib 脚本块。
   幂等：已存在则整段替换（改了 tools/mapgen.js 后重跑本脚本即可再同步）。
   用法：node tools/_t56_wire.js  —— 锚点缺失则不写盘、exit 1。
   注：用普通 <script>（无属性）+ 标记注释定位，让 check_web 的逐脚本语法检查覆盖到它。 */
'use strict';
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const HTML = path.join(ROOT, 'web', 'index.html');
const LIB = path.join(ROOT, 'tools', 'mapgen.js');

const html = fs.readFileSync(HTML, 'utf8');
const lib = fs.readFileSync(LIB, 'utf8');

const M_OPEN = '/* ==MAPGEN-LIB== T55 tools/mapgen.js 内联副本 —— 由 tools/_t56_wire.js 注入同步（勿手改；改 tools/mapgen.js 后重跑 _t56_wire.js） == */';
const M_CLOSE = '/* ==/MAPGEN-LIB== */';
const block = '<script>\n' + M_OPEN + '\n' + lib.trim() + '\n' + M_CLOSE + '\n</script>';

// 锚点：引擎主脚本头
const anchorRe = /<script>\r?\n\/\* 《红渊：下潜》战斗引擎核心/;   // CRLF/LF 兼容
const am = html.match(anchorRe);
if (!am) { console.error('锚点缺失：引擎 <script> 头'); process.exit(1); }
const ai = am.index;

const oi = html.indexOf(M_OPEN);
const BIND_OPEN = '/* ==MAPGEN-BINDINGS== T58 data/mapgen_bindings.json 内联（由 tools/_t56_wire.js 注入同步；重跑 _t58_build.js 后再跑本脚本） == */';
const BIND_CLOSE = '/* ==/MAPGEN-BINDINGS== */';
const bindJson = fs.readFileSync(path.join(ROOT, 'data', 'mapgen_bindings.json'), 'utf8').trim();
const bindBlock = '<script>\n' + BIND_OPEN + '\nwindow.MAPGEN_BINDINGS = ' + bindJson + ';\n' + BIND_CLOSE + '\n</script>';

let out;
if (oi >= 0) {
  const ci = html.indexOf(M_CLOSE, oi);
  if (ci < 0) { console.error('已存在的 MAPGEN-LIB 块没有闭合'); process.exit(1); }
  // 向前吃到本块 <script> 开标签、向后吃到 </script>
  const so = html.lastIndexOf('<script>', oi);
  const se = html.indexOf('</script>', ci) + '</script>'.length;
  out = html.slice(0, so) + block + html.slice(se);
  console.log('mapgen-lib 已替换同步（' + (lib.length / 1024).toFixed(1) + ' KB）');
} else {
  out = html.slice(0, ai) + block + '\n' + html.slice(ai);
  console.log('mapgen-lib 已注入（' + (lib.length / 1024).toFixed(1) + ' KB）');
}
// 绑定表注入/同步（放在 mapgen-lib 块之后）
const bi = out.indexOf(BIND_OPEN);
if (bi >= 0) {
  const so2 = out.lastIndexOf('<script>', bi);
  const ci2 = out.indexOf(BIND_CLOSE, bi);
  const se2 = out.indexOf('</script>', ci2) + '</script>'.length;
  out = out.slice(0, so2) + bindBlock + out.slice(se2);
  console.log('MAPGEN-BINDINGS 已替换同步（' + (bindJson.length / 1024).toFixed(1) + ' KB）');
} else {
  const insertAfter = out.indexOf('</script>', out.indexOf(M_CLOSE));
  out = out.slice(0, insertAfter + 9) + '\n' + bindBlock + out.slice(insertAfter + 9);
  console.log('MAPGEN-BINDINGS 已注入（' + (bindJson.length / 1024).toFixed(1) + ' KB）');
}
fs.writeFileSync(HTML, out);
console.log('ok');
