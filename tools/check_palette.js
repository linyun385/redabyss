// T71 生态色板检查器。验三件事：
//   1. web/index.html ==T56-MAP-MODULE== 里的 ECO_C 表与 tools/eco_palette.json 完全一致（两份副本防漂移）
//   2. 8 个生态色 L*（CIELAB, D65/2°）全部 ≥ 55
//   3. 相邻深度带（1→2→…→8）主生态色 ΔL* ≥ 6；8 色两两色相间隔 ≥ 25°
// 用法：node tools/check_palette.js   （通过 exit 0，失败 exit 1，输出 L*/a*/b* 表）
'use strict';
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const HTML = path.join(ROOT, 'web', 'index.html');
const JSON_FILE = path.join(ROOT, 'tools', 'eco_palette.json');

let fails = 0;
const ok = m => console.log('  ok    ' + m);
const fail = m => { console.log('  FAIL  ' + m); fails++; };

// ── sRGB → CIELAB（D65 白点、2° 视角）────────────────────
function hex2rgb(h) {
  const m = /^#?([0-9a-f]{6})$/i.exec(h.trim());
  if (!m) return null;
  const n = parseInt(m[1], 16);
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255].map(v => v / 255);
}
function rgb2lab([r, g, b]) {
  const lin = c => (c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4));
  const R = lin(r), G = lin(g), B = lin(b);
  const X = (0.4124564 * R + 0.3575761 * G + 0.1804375 * B) / 0.95047;
  const Y = 0.2126729 * R + 0.7151522 * G + 0.0721750 * B;
  const Z = (0.0193339 * R + 0.1191920 * G + 0.9503041 * B) / 1.08883;
  const f = t => (t > 0.008856 ? Math.cbrt(t) : 7.787 * t + 16 / 116);
  const fx = f(X), fy = f(Y), fz = f(Z);
  return [116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)];
}
const hueOf = lab => (Math.atan2(lab[2], lab[1]) * 180 / Math.PI + 360) % 360;
const chromaOf = lab => Math.hypot(lab[1], lab[2]);

// ── 数据源 ────────────────────────────────────────────────
const spec = JSON.parse(fs.readFileSync(JSON_FILE, 'utf8'));
const order = spec.order;                 // 带序 1..8 的主生态
const want = spec.colors;
const homeBand = spec.homeBand;

const html = fs.readFileSync(HTML, 'utf8');
// 从 ==T56-MAP-MODULE== 段提取 ECO_C 字面量（两份副本对拍，防手改漂移）
const modStart = html.indexOf('==T56-MAP-MODULE==');
const block = modStart >= 0 ? html.slice(modStart) : '';
const m = /const ECO_C = \{([\s\S]*?)\};/.exec(block);
if (!m) { fail('index.html 里找不到 ECO_C 表（应在 ==T56-MAP-MODULE== 段）'); process.exit(1); }
const got = {};
m[1].split(',').forEach(kv => {
  const mm = /\s*(eco_\w+)\s*:\s*['"]#([0-9a-fA-F]{6})['"]/.exec(kv);
  if (mm) got[mm[1]] = '#' + mm[2].toLowerCase();
});

console.log('=== T71 生态色板检查 ===\n');

// 1. 两份副本一致
const keys = Object.keys(want).sort().join(',');
if (Object.keys(got).sort().join(',') !== keys) {
  fail('ECO_C 键集合与 eco_palette.json 不一致：json=[' + keys + '] html=[' + Object.keys(got).sort().join(',') + ']');
} else {
  const drift = order.filter(id => got[id] !== want[id]);
  if (drift.length) fail('色值漂移：' + drift.map(id => id + ' json=' + want[id] + ' html=' + got[id]).join('；'));
  else ok('index.html ECO_C 与 tools/eco_palette.json 完全一致（8/8）');
}

// 2. L* 表 + 阈值
console.log('\n  生态          色值      L*      a*      b*   C*     h°    带校');
const rows = order.map(id => {
  const lab = rgb2lab(hex2rgb(want[id]));
  return { id, hex: want[id], lab, h: hueOf(lab), C: chromaOf(lab), band: homeBand[id] };
});
rows.forEach(r => {
  console.log('  ' + r.id.padEnd(12) + r.hex + '  ' +
    r.lab.map(v => v.toFixed(1).padStart(6)).join('  ') + '  ' +
    r.C.toFixed(1).padStart(4) + '  ' + r.h.toFixed(1).padStart(5) + '  D' + r.band);
});
const lmin = Math.min(...rows.map(r => r.lab[0]));
if (lmin >= 55) ok('全部 L* ≥ 55（最低 ' + lmin.toFixed(1) + '）');
else fail('有 L* < 55（最低 ' + lmin.toFixed(1) + '）');

// 3a. 相邻带 ΔL* ≥ 6（按带序相邻）
console.log('');
let dlBad = 0;
for (let i = 0; i + 1 < order.length; i++) {
  const a = rows[i].lab[0], b = rows[i + 1].lab[0];
  const d = Math.abs(a - b);
  const tag = 'D' + rows[i].band + '→D' + rows[i + 1].band + '  ' + rows[i].id + ' / ' + rows[i + 1].id;
  if (d >= 6) ok('ΔL* ' + tag + ' = ' + d.toFixed(1));
  else { fail('ΔL* ' + tag + ' = ' + d.toFixed(1) + ' (< 6)'); dlBad++; }
}

// 3b. 两两色相间隔 ≥ 25°（环上最邻间隔）
const hs = rows.slice().sort((x, y) => x.h - y.h);
let hmin = 999, hminPair = '';
for (let i = 0; i < hs.length; i++) {
  const j = (i + 1) % hs.length;
  const d = i + 1 < hs.length ? hs[j].h - hs[i].h : 360 - hs[hs.length - 1].h + hs[0].h;
  if (d < hmin) { hmin = d; hminPair = hs[i].id + ' / ' + hs[j].id; }
}
if (hmin >= 25) ok('两两色相最小间隔 ' + hmin.toFixed(1) + '° ≥ 25°（最近：' + hminPair + '）');
else fail('色相间隔不足：' + hminPair + ' 仅 ' + hmin.toFixed(1) + '° (< 25°)');

console.log('');
if (fails) { console.log('T71 色板检查：' + fails + ' 项失败'); process.exit(1); }
console.log('T71 色板检查全过：8 色 L*≥55、相邻带 ΔL*≥6、色相间隔≥25°，双份副本一致');
