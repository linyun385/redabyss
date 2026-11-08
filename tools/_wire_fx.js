// 把动效层接进 web/index.html（三处插入，按位置而非精确换行匹配，幂等）
const fs = require('fs');
const path = require('path');

const GAME = 'C:\\Users\\Administrator\\Desktop\\杂七杂八\\红渊\\game';
const HTML = path.join(GAME, 'web', 'index.html');

let src = fs.readFileSync(HTML, 'utf8');
const before = src.length;
const NL = src.includes('\r\n') ? '\r\n' : '\n';
console.log('换行符:', NL === '\r\n' ? 'CRLF' : 'LF');
let done = 0;

function insertAfter(anchor, text, label) {
  const i = src.indexOf(anchor);
  if (i < 0) { console.error('★ 找不到锚点: ' + anchor); return false; }
  const at = i + anchor.length;
  src = src.slice(0, at) + NL + text + src.slice(at);
  console.log('  + ' + label);
  done++;
  return true;
}

// 1) fx.css（紧随 </style>）
if (!src.includes('href="fx.css"')) {
  if (!insertAfter('</style>', '<link rel="stylesheet" href="fx.css">', '<link fx.css>')) process.exit(1);
}

// 2) 特效层容器（紧随 <body>）
if (!src.includes('id="fx-layer"')) {
  if (!insertAfter('<body>', '<div id="fx-layer" aria-hidden="true"></div>', '<div fx-layer>')) process.exit(1);
}

// 3) fx.js（在最后一个 </script> 之后）
if (!src.includes('src="fx.js"')) {
  const i = src.lastIndexOf('</script>');
  if (i < 0) { console.error('★ 找不到 </script>'); process.exit(1); }
  const at = i + '</script>'.length;
  src = src.slice(0, at) + NL + '<script src="fx.js"></script>' + src.slice(at);
  console.log('  + <script fx.js>');
  done++;
}

if (!done) { console.log('三处都已存在，无需改动'); process.exit(0); }

fs.writeFileSync(HTML, src, 'utf8');

const back = fs.readFileSync(HTML, 'utf8');
const checks = {
  'fx.css 引入一次': (back.match(/href="fx\.css"/g) || []).length === 1,
  'fx-layer 容器恰好一个': (back.match(/id="fx-layer"/g) || []).length === 1,
  'fx.js 引入一次': (back.match(/src="fx\.js"/g) || []).length === 1,
  'fx.js 在最后一个 script 之后': back.indexOf('src="fx.js"') > back.lastIndexOf('window.ART'),
  'style 块仍是 1 个': (back.match(/<style>/g) || []).length === 1
};
let ok = true;
for (const [k, v] of Object.entries(checks)) {
  console.log(`  ${v ? 'ok  ' : '★FAIL'} ${k}`);
  if (!v) ok = false;
}
console.log(`\n字节 ${before} → ${back.length}（+${back.length - before}）`);
console.log(ok ? '全部通过' : '有失败项，请检查');
process.exit(ok ? 0 : 1);
