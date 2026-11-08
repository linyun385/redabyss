// 把新生成的卡面 id 插进 web/index.html 的 window.ART 表。
// 原则：只加不删；每条都必须有真实 webp 文件；加完必须校验条目数 = 原数 + 新增数。
const fs = require('fs');
const path = require('path');

const GAME = 'C:\\Users\\Administrator\\Desktop\\杂七杂八\\红渊\\game';
const HTML = path.join(GAME, 'web', 'index.html');
const ART_DIR = path.join(GAME, 'web', 'assets', 'art');

const NEW_IDS = ['anm_0051', 'anm_0052', 'anm_0053', 'anm_0054', 'anm_0055', 'anm_0056', 'anm_0057'];
const dry = !process.argv.includes('--apply');

const src = fs.readFileSync(HTML, 'utf8');
const m = src.match(/window\.ART = (\{[\s\S]*?\});/);
if (!m) { console.error('找不到 window.ART 表，中止'); process.exit(1); }

const ART = JSON.parse(m[1]);
const before = Object.keys(ART).length;

const add = [];
for (const id of NEW_IDS) {
  const f = path.join(ART_DIR, id + '.webp');
  if (!fs.existsSync(f)) { console.error(`★ 缺文件 ${id}.webp，中止（不做半截事）`); process.exit(1); }
  if (ART[id]) { console.log(`  已有，跳过 ${id}`); continue; }
  ART[id] = `assets/art/${id}.webp`;
  add.push(id);
}

const after = Object.keys(ART).length;
console.log(`原 ${before} 条，新增 ${add.length} 条，新共 ${after} 条`);
add.forEach(id => console.log(`  + ${id} -> assets/art/${id}.webp`));

if (after !== before + add.length) { console.error('★ 条目数校验失败，中止'); process.exit(1); }
if (dry) { console.log('\n[dry run] 加 --apply 才写'); process.exit(0); }

// 序列化：保持原有的紧凑单行风格
const json = JSON.stringify(ART);
const out = src.replace(m[0], `window.ART = ${json};`);
fs.writeFileSync(HTML, out, 'utf8');

// 回读校验
const re = fs.readFileSync(HTML, 'utf8').match(/window\.ART = (\{[\s\S]*?\});/);
const reART = JSON.parse(re[1]);
console.log(`写回校验：ART 条目 ${Object.keys(reART).length}，anm_0051=${!!reART['anm_0051']}，anm_0001=${!!reART['anm_0001']}`);
console.log(`文件字节 ${Buffer.byteLength(out, 'utf8')}`);
