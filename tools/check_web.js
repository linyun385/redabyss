// 前端产物检查器。T5/T6/T7 都要跑。
// 用法：node tools/check_web.js
'use strict';
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const FILE = path.join(ROOT, 'web', 'index.html');

let fails = 0, warns = 0;
const ok = m => console.log('  ok    ' + m);
const fail = m => { console.log('  FAIL  ' + m); fails++; };
const warn = m => { console.log('  warn  ' + m); warns++; };

console.log('=== web/index.html 检查 ===\n');

if (!fs.existsSync(FILE)) { fail('web/index.html 不存在'); process.exit(1); }

const html = fs.readFileSync(FILE, 'utf8');
const kb = (Buffer.byteLength(html, 'utf8') / 1024).toFixed(1);
console.log('  大小: ' + kb + ' KB\n');

// 1. 体量 —— 2026-10-31 改：素材外置后，体积上限不再是硬指标
//    （原来 3MB 是为了限制 base64 内联；现在素材在 web/assets/，HTML 只留代码与数据）
if (html.length < 30000) fail('文件只有 ' + kb + 'KB，可能没内联数据（应 >30KB）');
else if (html.length > 1500000) warn('HTML 超过 1.5MB，偏重（素材应外置到 web/assets/）');
else ok('体量合理：' + kb + ' KB');

// 2. 自包含：禁止**外网**请求
//    2026-11-05 改：素材外置之后（web/assets/ 的图片走 <img src>），
//    站内相对路径的 fetch/XHR（如 sfx/*.wav 走 Web Audio）和 <img src> 是同一类，
//    不算外部依赖。只有指向 http(s):// 或 // 的外链才拦。
const netPatterns = [
  [/(?:fetch|XMLHttpRequest)\s*\([^)]*["'`]\s*(?:https?:)?\/\//i, '外部网络请求（fetch/XHR 指向外链）'],
  [/\bimport\s*\(/, '动态 import()'],
  [/(?:src|href)\s*=\s*["']https?:/i, '外部 script/link 引用'],
  [/@import\s+url/i, 'CSS @import'],
  [/url\s*\(\s*["']?https?:/i, 'CSS 远程资源'],
  // T67：素材走 data: 内联后，外链素材（任何协议的图片引用，含 JS 字符串）仍然要拦
  [/https?:\/\/[^"'\s)]+\.(png|jpe?g|webp|gif|svg)/i, '外链素材引用（http 图片）']
];
let netHits = 0;
netPatterns.forEach(([re, name]) => {
  if (re.test(html)) { fail('发现外部依赖：' + name + '（必须自包含）'); netHits++; }
});
if (!netHits) ok('无外网依赖（站内相对路径的 fetch/<img src> 不算）');

// 2b. 站内素材存在性：fetch 出来的 wav 必须真在 web/ 下
const sfxFetches = [...html.matchAll(/fetch\('sfx\/'\s*\+\s*\w+\s*\+\s*'\.wav'/g)];
if (sfxFetches.length) {
  const fs = require('fs');
  const missing = [];
  const names = ['card.play.attack','card.play.skill','card.play.power','card.play.cost',
    'combat.start','enemy.hit','combat.hurt','combat.block','combat.kill',
    'state.resonance','state.gaze','state.energy_empty',
    'ui.click','ui.page',
    'special.boss_phase','special.world_switch','special.egg','special.victory','special.death',
    'ambience.depth1','ambience.depth2','ambience.depth3','ambience.depth4',
    'ambience.depth5','ambience.depth6','ambience.depth7','ambience.depth8'];
  names.forEach(n => { if (!fs.existsSync(require('path').join(__dirname, '..', 'web', 'sfx', n + '.wav'))) missing.push(n); });
  if (missing.length) fail('音效文件缺失：' + missing.join(', '));
  else ok('音效文件齐全（' + names.length + ' 个 wav）');
}

// 3. 引擎已内联
if (!/RedAbyss/.test(html)) fail('找不到 RedAbyss 引擎导出');
else ok('引擎已内联（RedAbyss 存在）');

['newRun', 'startCombat', 'playCard', 'endTurn'].forEach(fn => {
  if (!new RegExp(fn).test(html)) fail('引擎 API 未使用：' + fn);
});
if (/newRun[\s\S]*startCombat[\s\S]*playCard[\s\S]*endTurn/.test(html)) ok('四个核心 API 均已接线');

// 4. 数据已内联
const dataMarks = ['相石', '震髓'];  // glossary 里的名词
if (/diver/.test(html)) ok('职业数据存在'); else fail('缺少 diver 职业数据');
const layerNames = ['地表死寂区', '外层冷洞', '稳定空洞海', '红渊核心'].filter(n => html.includes(n));
if (layerNames.length >= 2) ok('层数据已内联（命中 ' + layerNames.length + ' 个层名）');
else fail('层数据未内联（只命中 ' + layerNames.length + ' 个层名）');

// 5. UI 要素
const uiWords = ['结束回合', '能量', '共振', '凝视', '生命'];
const missingUi = uiWords.filter(w => !html.includes(w));
if (missingUi.length) fail('HUD 缺少字样：' + missingUi.join('、'));
else ok('HUD 要素齐全（结束回合/能量/共振/凝视/生命）');

if (/intent/.test(html)) ok('敌人意图已渲染'); else fail('找不到 intent，敌人意图未显示');
if (/\.log|日志|战斗记录/.test(html)) ok('战斗日志已渲染'); else warn('可能没有渲染战斗日志');

// 6. 结构
if (!/<\/html>/i.test(html)) fail('HTML 结构不完整（缺 </html>）'); else ok('HTML 结构完整');
if (!/charset\s*=\s*["']?utf-8/i.test(html)) fail('缺少 UTF-8 声明，中文会乱码'); else ok('UTF-8 声明存在');

// 7. 素材引用 —— 2026-10-31 改：素材改为**外置相对路径**（web/assets/…）。
//    规则：
//      · 仍然**禁止任何 http(s) 外链**（上面第 2 段已经在拦，含 JS 字符串里的图片 URL）
//      · 允许 `url(data:…)` 与 `url(assets/…)` 这类**站内相对路径**
//      · 允许 <img src="assets/…">、<audio src="assets/…">
//      · 相对路径必须**真的存在**（下面做存在性校验，避免改名后静默 404）
const isLocalRel = u => /^(\.\/)?(assets|art|audio|sound|img|media)\//i.test(u.trim());
if (/<img\s/i.test(html)) {
  const imgSrcs = [...html.matchAll(/<img\b[^>]*\bsrc\s*=\s*["']([^"']+)["']/gi)].map(m => m[1]);
  const bad = imgSrcs.filter(u => !isLocalRel(u) && !/^data:/i.test(u));
  if (bad.length) fail('发现 <img> 引用了非站内相对路径：' + bad.slice(0, 3).join(' | '));
  else ok('<img> 全部为站内相对路径（' + imgSrcs.length + ' 处）');
} else {
  const bgUrls = [...html.matchAll(/background-image\s*:\s*url\(\s*['"]?([^'")]+)/gi)].map(m => m[1].trim());
  const badBg = bgUrls.filter(u => !/^data:/i.test(u) && !isLocalRel(u));
  if (badBg.length) fail('background-image 引用了站外地址（只允许 data: 或站内相对路径）: ' +
    badBg.slice(0, 3).join(' | '));
  else if (bgUrls.length) ok('background-image 引用合法（' + bgUrls.length + ' 处：data/站内相对路径）');
  else ok('无图片资源依赖');
}

// 7b. 站内相对路径存在性校验（把"改名了就静默 404"这条堵掉）
(() => {
  const refs = new Set();
  for (const m of html.matchAll(/(?:src|href)\s*=\s*["']([^"']+)["']/gi)) refs.add(m[1]);
  for (const m of html.matchAll(/url\(\s*['"]?([^'")]+)/gi)) refs.add(m[1]);
  for (const m of html.matchAll(/["']((?:\.\/)?(?:assets|art|audio|sound|img|media)\/[^"']+)["']/g)) refs.add(m[1]);
  const missing = [];
  for (const r of refs) {
    if (/^(https?:|data:|#|mailto:)/i.test(r)) continue;
    const clean = r.split(/[?#]/)[0];
    if (!isLocalRel(clean)) continue;
    const abs = path.join(ROOT, 'web', clean);
    if (!fs.existsSync(abs)) missing.push(clean);
  }
  if (missing.length) fail('站内资源不存在（' + missing.length + ' 个）：' + missing.slice(0, 5).join(' | '));
  else ok('站内素材存在性校验通过（' + [...refs].filter(r => isLocalRel(r.split(/[?#]/)[0])).length + ' 个引用）');
})();

// 8. 占位符检测 —— T67：排除 ART 表的 base64 数据体（base64 随机字符含 'xxx' 三连
//    属概率事件，~500KB 内必然出现 1-2 次；占位检测的目标是人工写的文字，数据体排除
//    是精度修正，不是放宽——外链/图片规则不受影响）
const htmlNoArt = html.replace(/\/\* ==ART-TABLE==[\s\S]*?==\/ART-TABLE== \*\//g, '');
const placeholders = ['TODO', 'FIXME', '待补充', '示例卡', 'xxx', '占位'];
const found = placeholders.filter(p => htmlNoArt.includes(p));
if (found.length) warn('发现疑似占位内容：' + found.join('、'));

// 9. JS 语法可解析（内联脚本挂掉 = 整页失效，关键词检查查不出来）
const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]);
if (!scripts.length) fail('找不到内联 <script>');
scripts.forEach((code, i) => {
  try { new Function(code); ok('script[' + i + '] 语法可解析（' + (code.length / 1024).toFixed(0) + ' KB）'); }
  catch (e) { fail('script[' + i + '] 语法错误：' + e.message); }
});

console.log('\n' + '='.repeat(40));
console.log(fails === 0 ? '全部通过（' + warns + ' 个警告）' : fails + ' 项失败，' + warns + ' 个警告');
process.exit(fails === 0 ? 0 : 1);
