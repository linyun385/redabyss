// 把 cards/*.json 同步进 web/index.html 的 const RAW（修正 _t46_wire.js 的写读顺序 bug）
// 用法：node tools/_sync_cards.js           干跑
//       node tools/_sync_cards.js --apply   真写
'use strict';
const fs = require('fs');
const path = require('path');
const ROOT = path.join(__dirname, '..');
const WEB = path.join(ROOT, 'web', 'index.html');
const APPLY = process.argv.includes('--apply');

const s = fs.readFileSync(WEB, 'utf8');

// 不用正则——RAW 是一整行 5MB+ 的 JSON，先用字符串定位
const MARK = 'const RAW = ';
const start = s.indexOf(MARK);
if (start < 0) { console.error('找不到 const RAW = '); process.exit(1); }
const bodyStart = start + MARK.length;
// JSON 字符串里也可能有 ;\n，所以不能用 indexOf 找结尾——按大括号深度扫描
let depth = 0, inStr = false, esc = false, i = bodyStart;
for (; i < s.length; i++) {
  const ch = s[i];
  if (inStr) {
    if (esc) esc = false;
    else if (ch === '\\') esc = true;
    else if (ch === '"') inStr = false;
    continue;
  }
  if (ch === '"') inStr = true;
  else if (ch === '{') depth++;
  else if (ch === '}') { depth--; if (depth === 0) { i++; break; } }
}
if (depth !== 0) { console.error('RAW 括号未闭合，depth=%d', depth); process.exit(1); }
const bodyEnd = i;                      // 指向 JSON 结束的 } 之后
const rawText = s.slice(bodyStart, bodyEnd);

let raw;
try {
  raw = JSON.parse(rawText);
} catch (e) {
  console.error('RAW 解析失败:', e.message.slice(0, 200));
  console.error('片段:', rawText.slice(0, 120), '…', rawText.slice(-120));
  process.exit(1);
}

console.log('RAW 键：', Object.keys(raw).join(', '));

const classes = ['diver', 'tremor', 'anmin', 'cangmin', 'shared'];
for (const cls of classes) {
  const p = path.join(ROOT, 'cards', cls + '.json');
  if (!fs.existsSync(p)) { console.log('  %s 无 json，保留原样', cls); continue; }
  const cur = JSON.parse(fs.readFileSync(p, 'utf8'));
  const before = Array.isArray(raw[cls]) ? raw[cls].length : '(无此键)';
  console.log('  %-8s RAW %s → json %d', cls, before, cur.length);
  raw[cls] = cur;
}

const out = MARK + JSON.stringify(raw) + ';\n';
const next = s.slice(0, start) + out + s.slice(bodyEnd + 2);

if (!APPLY) {
  console.log('\n[干跑] RAW 段 %d → %d 字节（%+d）', rawText.length, out.length - MARK.length - 2, (out.length - MARK.length - 2) - rawText.length);
  console.log('[干跑] 文件总长 %d → %d', s.length, next.length);
  console.log('加 --apply 真写。');
  process.exit(0);
}

fs.writeFileSync(WEB, next, 'utf8');
console.log('\n已写回 web/index.html（%d 字节）', next.length);
