// T76 选项对比度检查器。
//   从 web/index.html 的 CSS 文本读取三主题（off/A/B/C）的选项变量与页面背景变量，
//   计算 WCAG 相对亮度/对比度并打表；断言：
//     ① 选项框 vs 页面背景 ≥1.6:1（off/B/C 额外对「最亮层底 D1 #39434e」复核——运行时层色会改写 --bg）
//     ② 选项主文字/副说明/营火标题 vs 选项框 ≥4.5:1
//     ③ hover 背景亮度变化 ≥8%（相对）
//     ④ 色条同源：OPT_BAR / 营火 nth-child 色条 ∈ 地图生态色板 ECO_C
//     ⑤ disabled 不透明度 = 0.45
// 用法：node tools/check_contrast.js   （通过 exit 0）
'use strict';
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const html = fs.readFileSync(path.join(ROOT, 'web', 'index.html'), 'utf8');
const css = (html.match(/<style>([\s\S]*?)<\/style>/) || [null, ''])[1];

let fails = 0;
const ok = m => console.log('  ok    ' + m);
const fail = m => { console.log('  FAIL  ' + m); fails++; };

/* ── 颜色工具 ── */
function hex2rgb(h) {
  const m = /^#?([0-9a-f]{6})$/i.exec((h || '').trim());
  if (!m) return null;
  const n = parseInt(m[1], 16);
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
}
function lum(rgb) {   // WCAG 相对亮度
  const [r, g, b] = rgb.map(v => {
    const c = v / 255;
    return c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
  });
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}
function contrast(a, b) {   // WCAG 对比度（≥1 的比值）
  const l1 = lum(a), l2 = lum(b);
  return (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
}
function colorMix(rgbA, rgbB, wA) {   // CSS color-mix(in srgb, A wA%, B (1-wA)%)
  return rgbA.map((v, i) => Math.round(v * wA + rgbB[i] * (1 - wA)));
}

/* ── 解析主题变量块（按 CSS 出现顺序合并覆盖；先剥注释——注释会夹在分号之间） ── */
function parseVarBlocks() {
  const blocks = [];
  const cssClean = css.replace(/\/\*[\s\S]*?\*\//g, '');
  const re = /(^|\n)\s*(?::root|html\[data-theme="([A-C]+)"\](?:\s*,\s*html\[data-theme="([A-C]+)"\])*)\s*\{([^}]*)\}/g;
  let m;
  while ((m = re.exec(cssClean))) {
    const themes = m[2] ? [m[2], m[3]].filter(Boolean) : ['off'];
    const vars = {};
    m[4].split(';').forEach(kv => {
      const mm = /^\s*(--[\w-]+)\s*:\s*([^;]+)$/.exec(kv);
      if (mm) vars[mm[1]] = mm[2].trim();
    });
    blocks.push({ themes, vars });
  }
  return blocks;
}
function themeVars(name, blocks) {
  const out = {};
  blocks.forEach(b => { if (b.themes.includes(name)) Object.assign(out, b.vars); });
  return out;
}
function resolveColor(v, vars) {   // 支持 var(--x) 引用一层
  const ref = /^var\(--([\w-]+)\)$/.exec(v || '');
  if (ref) return vars[ref[1]] !== undefined ? resolveColor(vars[ref[1]], vars) : null;
  return hex2rgb(v);
}

const blocks = parseVarBlocks();
const THEMES = ['off', 'A', 'B', 'C'];
const D1_LAYER = hex2rgb('#39434e');   // 运行时最亮层底（applyLayerTheme D1），最坏情况页底
const LAYER_DARKEST = hex2rgb('#0d1013');

console.log('=== T76 选项对比度检查（三主题） ===\n');

/* ── ① ② ③ 逐主题打表 ── */
const results = {};
for (const th of THEMES) {
  const v = themeVars(th, blocks);
  const need = ['--opt-bg', '--opt-bg-hover', '--opt-fg', '--opt-sub', '--opt-border'];
  const missing = need.filter(k => !v[k]);
  if (missing.length) { fail('主题 ' + th + ' 缺变量: ' + missing.join(',')); continue; }
  const optBg = hex2rgb(v['--opt-bg']), optHover = hex2rgb(v['--opt-bg-hover']);
  const optFg = hex2rgb(v['--opt-fg']), optSub = hex2rgb(v['--opt-sub']);
  const red = hex2rgb('#8b2a20');   // 营火标题色（--red）
  if (!optBg || !optHover || !optFg || !optSub) { fail('主题 ' + th + ' 颜色解析失败'); continue; }

  // 页面底候选：静态 --bg（off/B/C）或 color-mix（A）×层色两档，取「对比最差」者
  const pageCands = [];
  const bgStatic = resolveColor(v['--bg'], v);
  if (bgStatic) pageCands.push({ tag: '--bg', rgb: bgStatic });
  pageCands.push({ tag: 'D1层底', rgb: D1_LAYER });
  if (v['--paper'] && th === 'A') {
    pageCands.push({ tag: '纸混D1', rgb: colorMix(hex2rgb(v['--paper']), D1_LAYER, 0.78) });
    pageCands.push({ tag: '纸混最暗层', rgb: colorMix(hex2rgb(v['--paper']), LAYER_DARKEST, 0.78) });
  }
  let worst = null;
  pageCands.forEach(pc => {
    const c = contrast(optBg, pc.rgb);
    if (!worst || c < worst.c) worst = { tag: pc.tag, c };
  });
  const bgPass = worst.c >= 1.6;
  if (!bgPass) fails++;
  const cFg = contrast(optFg, optBg);
  const cSub = contrast(optSub, optBg);
  const cCampTitle = contrast(red, optBg);
  const fgPass = cFg >= 4.5, subPass = cSub >= 4.5, titlePass = cCampTitle >= 4.5;
  if (!fgPass) fails++; if (!subPass) fails++; if (!titlePass) fails++;
  const lBase = lum(optBg), lHover = lum(optHover);
  const hoverDelta = Math.abs(lHover - lBase) / lBase;
  const hoverPass = hoverDelta >= 0.08;
  if (!hoverPass) fails++;

  results[th] = { worst: worst.tag, bgRatio: worst.c, cFg, cSub, cCampTitle, hoverDelta };
  console.log('『' + th + '』');
  console.log('  ① 选项框/页面底  ' + worst.c.toFixed(2) + ':1（最坏页底=' + worst.tag + '）  ≥1.6  ' + (bgPass ? '✓' : '✗'));
  console.log('  ② 主文字/选项框   ' + cFg.toFixed(2) + ':1  ≥4.5  ' + (fgPass ? '✓' : '✗') +
    '    副说明/选项框  ' + cSub.toFixed(2) + ':1  ' + (subPass ? '✓' : '✗') +
    '    营火标题/选项框 ' + cCampTitle.toFixed(2) + ':1  ' + (titlePass ? '✓' : '✗'));
  console.log('  ③ hover 亮度变化  ' + (hoverDelta * 100).toFixed(1) + '%  ≥8%  ' + (hoverPass ? '✓' : '✗'));
  console.log('');
}

/* ── ④ 色条同源：OPT_BAR / 营火色条 ∈ 地图生态色板 ECO_C ── */
const ecoM = /const ECO_C = \{([\s\S]*?)\};/.exec(html);
if (!ecoM) { fail('找不到地图生态色板 ECO_C'); }
else {
  const ecoSet = new Set();
  ecoM[1].split(',').forEach(kv => {
    const mm = /'(#[0-9a-fA-F]{6})'/.exec(kv);
    if (mm) ecoSet.add(mm[1].toLowerCase());
  });
  const barM = /const OPT_BAR = \{([^}]*)\};/.exec(html);
  if (!barM) { fail('找不到 OPT_BAR 色条表'); }
  else {
    const bars = {};
    barM[1].split(',').forEach(kv => {
      const mm = /\s*('?)([\w]+)\1?:\s*'(#[0-9a-fA-F]{6})'/.exec(kv);
      if (mm) bars[mm[2]] = mm[3].toLowerCase();
    });
    const off = Object.keys(bars).filter(k => !ecoSet.has(bars[k]));
    if (off.length) fail('OPT_BAR 色不在地图生态色板内: ' + off.join(','));
    else ok('事件选项色条（按脉取向）∈ 地图生态色板 ECO_C：' +
      Object.keys(bars).map(k => k + '=' + bars[k]).join(' '));
  }
  const campBars = [...css.matchAll(/\.campopt:nth-of-type\(3n(?:\+([12]))?\)\s*\{\s*border-left-color:\s*(#[0-9a-fA-F]{6})/g)]
    .map(m => m[2].toLowerCase());
  if (campBars.length < 3) fail('营火选项 nth-child 色条不足 3 条');
  else {
    const off2 = campBars.filter(c => !ecoSet.has(c));
    if (off2.length) fail('营火色条不在生态色板内: ' + off2.join(','));
    else ok('营火选项色条（按位轮换）∈ 地图生态色板 ECO_C：' + campBars.join(' '));
  }
}

/* ── ⑤ disabled 不透明度 0.45 ── */
const disOpt = /\.optbtn:disabled\s*\{\s*opacity:\s*\.45/.test(css);
const disCamp = /\.campopt\.disabled\s*\{\s*opacity:\s*\.45/.test(css);
if (disOpt && disCamp) ok('disabled 不透明度 0.45（事件 + 营火）');
else { fail('disabled 不透明度不是 0.45（optbtn=' + disOpt + ' campopt=' + disCamp + '）'); }

/* ── 背景未被改动（C 条款：--bg 与 --paper 基础值保持原样） ── */
const offVars = themeVars('off', blocks);
if ((offVars['--bg'] || '').toLowerCase() === '#0a0506') ok('off 页面底 --bg 未被改动（#0a0506）');
else fail('off 页面底 --bg 被改动了（只许改选项样式）');

console.log('');
if (fails) { console.log('T76 对比度检查：' + fails + ' 项失败'); process.exit(1); }
console.log('T76 对比度检查全过：三主题 ①≥1.6:1 ②≥4.5:1 ③hover≥8% ④色条同源 ⑤disabled 0.45');
