// 生成 HY4 的卡图索引任务包（精确文件清单，不靠手写）
const fs = require('fs');
const path = require('path');

const GAME = 'C:\\Users\\Administrator\\Desktop\\杂七杂八\\红渊\\game';
const artDir = path.join(GAME, 'web', 'assets', 'art');

const j = JSON.parse(fs.readFileSync(path.join(GAME, 'cards', 'anmin.json'), 'utf8'));
const cards = Array.isArray(j) ? j : (j.cards || []);
const byId = new Map(cards.map(c => [c.id, c]));

const src = fs.readFileSync(path.join(GAME, 'web', 'index.html'), 'utf8');
const m = src.match(/window\.ART = (\{[\s\S]*?\});/);
const ART = m ? JSON.parse(m[1]) : {};

const files = new Set(
  fs.readdirSync(artDir).filter(f => f.endsWith('.webp') && !f.includes('.old.')).map(f => f.replace(/\.webp$/, ''))
);

const rows = [];
for (const c of cards) {
  if (files.has(c.id) && ART[c.id]) rows.push(c);
}
rows.sort((a, b) => (a.id < b.id ? -1 : 1));

const lines = [];
lines.push('# HY4 任务：维护者卡图索引');
lines.push('');
lines.push('**目的**：把 47 张维护者卡图逐张翻译成一句文字描述，做成索引表。');
lines.push('之后定稿新卡时，照这张表挑图，不用重新看图。');
lines.push('');
lines.push('## 边界（先读这段）');
lines.push('');
lines.push('| 允许 | 禁止 |');
lines.push('|---|---|');
lines.push('| 读这些 webp，写一句描述 | 改任何文件（图片、json、html 都不许动）|');
lines.push('| 指出某张图看不清 | 判断「这张图该配哪张卡」——那是我的活 |');
lines.push('| 写「未识别」 | 编造图里没有的东西 |');
lines.push('');
lines.push('## 输出格式');
lines.push('');
lines.push('存成一份 CSV，UTF-8 无 BOM，两列，不要表头以外的多余列：');
lines.push('');
lines.push('```');
lines.push('id,描述');
lines.push('anm_0001,"洞穴中一把红色工具，握把缠白色布条，插在地上"');
lines.push('```');
lines.push('');
lines.push('描述规矩：');
lines.push('');
lines.push('1. **只写图里看得见的**：主体是什么、材质、姿态/朝向、背景、光从哪来');
lines.push('2. 一句，不超过 40 字，不写形容词堆砌，不写寓意');
lines.push('3. 不出现「似乎」「可能」「象征着」这类猜测词');
lines.push('4. 看不清就说「画面模糊/抽象，仅见红色团块」——**别硬猜**');
lines.push('');
lines.push('## 要处理的 47 张');
lines.push('');
lines.push('目录：`' + artDir + '`');
lines.push('');
lines.push('| # | id | 卡名 | 稀有度 | 主脉 |');
lines.push('|---|---|---|---|---|');
rows.forEach((c, i) => {
  const rar = c.rarity || '';
  const vein = (c.veins && c.veins[0]) || '';
  lines.push(`| ${i + 1} | ${c.id} | ${c.name} | ${rar} | ${vein} |`);
});
lines.push('');
lines.push(`合计 **${rows.length}** 张。`);
lines.push('');
lines.push('## 验收方式');
lines.push('');
lines.push('我随机抽 3 张，自己看图对描述。任一条对不上（编造、张冠李戴），整批退回重做。');
lines.push('');
lines.push('★ 卡名**只用于让你知道这批图属于哪个职业**，**不要**拿卡名去反推画面内容——');
lines.push('　旧卡的图和旧卡的机制本来就可能对不上，照着卡名描述等于没看。');
lines.push('');

const out = path.join(GAME, 'tasks', 'HY4_art_index.md');
fs.writeFileSync(out, lines.join('\n'), 'utf8');
console.log('写出:', out, '| 卡数:', rows.length);
