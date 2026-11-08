// T52 对比度体检：读 web/index.html 的颜色变量与层深度色表，按 WCAG 算对比度。
// 用法：node tools/a11y_check.js [--fix-verify]
// 输出：tools/a11y_report.json + 控制台摘要。正文 ≥4.5 / 次要 ≥3。
'use strict';
const fs = require('fs');
const path = require('path');
const ROOT = path.join(__dirname, '..');
const html = fs.readFileSync(path.join(ROOT, 'web', 'index.html'), 'utf8');

function hx(h) { h = h.trim().replace('#', ''); return [0, 2, 4].map(i => parseInt(h.slice(i, i + 2), 16)); }
function lum(c) {
  const f = v => { v /= 255; return v <= 0.04045 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
  const [r, g, b] = c.map(f);
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}
function contrast(a, b) { const la = lum(a), lb = lum(b); const hi = Math.max(la, lb), lo = Math.min(la, lb); return +((hi + 0.05) / (lo + 0.05)).toFixed(2); }

// 从 index.html 抓变量
const rootVars = {};
const rootBlock = html.match(/:root \{([\s\S]*?)\}/)[1];
rootBlock.replace(/--([a-z0-9-]+):\s*(#[0-9a-fA-F]{6})/g, (_, k, v) => { rootVars['--' + k] = hx(v); return _; });
const layerBlock = html.match(/const LAYER_THEME = \{([\s\S]*?)\};/)[1];
const LAYERS = {};
layerBlock.replace(/(\d+):\s*\{\s*bg:\s*'(#[0-9a-fA-F]{6})',\s*fg:\s*'(#[0-9a-fA-F]{6})'/g, (_, d, bg, fg) => { LAYERS[+d] = { bg: hx(bg), fg: hx(fg) }; return _; });

if (Object.keys(LAYERS).length !== 8) { console.error('断言失败：LAYER_THEME 应有 8 层，抓到 ' + Object.keys(LAYERS).length); process.exit(1); }
if (!rootVars['--dim'] || !rootVars['--text'] || !rootVars['--red-hi']) { console.error('断言失败：:root 缺 --text/--dim/--red-hi'); process.exit(1); }

// 次要文字修正量（T52）：--dim 若被本任务修改，这里读取修改后的值
// （--dim 直接定义在 :root，脚本读到的就是当前生效值）
const report = { generatedAt: new Date().toISOString(), checks: [], fails: 0 };
function check(name, fg, bg, level) {
  const ratio = contrast(fg, bg);
  const limit = level === 'body' ? 4.5 : 3;
  const pass = ratio >= limit;
  if (!pass) report.fails++;
  report.checks.push({ name, fg: '#' + fg.map(x => x.toString(16).padStart(2, '0')).join(''), bg: '#' + bg.map(x => x.toString(16).padStart(2, '0')).join(''), ratio, level, limit, pass });
  return { ratio, pass };
}

console.log('=== 正文（--text / 层背景，8 层）===');
let worstBody = 99;
for (const d of Object.keys(LAYERS)) {
  const r = check('D' + d + ' 正文', LAYERS[d].fg, LAYERS[d].bg, 'body');
  worstBody = Math.min(worstBody, r.ratio);
}
console.log('  最差对比度: ' + worstBody + (worstBody >= 4.5 ? '  ✓' : '  ✗'));

console.log('=== 次要（--dim / 层背景，8 层）===');
let worstDim = 99;
for (const d of Object.keys(LAYERS)) {
  const r = check('D' + d + ' 次要(--dim)', rootVars['--dim'], LAYERS[d].bg, 'secondary');
  worstDim = Math.min(worstDim, r.ratio);
}
console.log('  最差对比度: ' + worstDim + (worstDim >= 3 ? '  ✓' : '  ✗'));

console.log('=== 强调（--red-hi / 层背景，8 层，次要级）===');
let worstRed = 99;
for (const d of Object.keys(LAYERS)) {
  const r = check('D' + d + ' 强调(--red-hi)', rootVars['--red-hi'], LAYERS[d].bg, 'secondary');
  worstRed = Math.min(worstRed, r.ratio);
}
console.log('  最差对比度: ' + worstRed + (worstRed >= 3 ? '  ✓' : '  ✗'));

console.log('=== 主题纸面（C/B 卡面：--ink vs --paper）===');
const ink = hx('#2b2118'), paper = hx('#d9cfbe');
const rPaper = check('纸面正文(--ink vs --paper)', ink, paper, 'body');
console.log('  对比度: ' + rPaper.ratio + (rPaper.pass ? '  ✓' : '  ✗'));
const rPaperDim = check('纸面次要(--ink-dim #6b5334 vs --paper)', hx('#6b5334'), paper, 'secondary');
console.log('  对比度: ' + rPaperDim.ratio + (rPaperDim.pass ? '  ✓' : '  ✗'));

report.summary = { worstBody, worstDim, worstRed, paperBody: rPaper.ratio, paperSecondary: rPaperDim.ratio };
fs.writeFileSync(path.join(ROOT, 'tools', 'a11y_report.json'), JSON.stringify(report, null, 1), 'utf8');
const allPass = worstBody >= 4.5 && worstDim >= 3 && worstRed >= 3 && rPaper.pass && rPaperDim.pass;
console.log('\n' + (allPass ? '全部达标' : '有不达标项（见 a11y_report.json 的 checks[].pass=false）'));
process.exit(allPass ? 0 : 2);
