// 侦察动效改造所需的 DOM 结构信息
const fs = require('fs');
const src = fs.readFileSync('web/index.html', 'utf8');

console.log('=== dataset 赋值键 ===');
const ds = [...src.matchAll(/dataset\.([A-Za-z]+)\s*=/g)].map(m => m[1]);
console.log([...new Set(ds)].join(', ') || '（无）');

console.log('\n=== querySelector 选择器（前 30） ===');
const qs = [...src.matchAll(/querySelector(?:All)?\(\s*'([^']+)'/g)].map(m => m[1]);
console.log([...new Set(qs)].slice(0, 30).join(' | ') || '（无）');

console.log('\n=== el( 创建的带 enemy/card/board 的类名 ===');
const els = [...src.matchAll(/\bel\('div',\s*'([^']*)'/g)].map(m => m[1]);
const picked = [...new Set(els)].filter(c => /enemy|card|hand|board|feld|foe|unit/i.test(c));
console.log(picked.join(' | ') || '（无匹配）');

console.log('\n=== 数据对象是否挂 DOM 引用 ===');
for (const kw of ['.$el', 'elRef', '._el', '.domEl', '.node']) {
  console.log(`  ${kw}: ${src.split(kw).length - 1}`);
}

console.log('\n=== 渲染函数签名 ===');
for (const m of src.matchAll(/function (render[A-Za-z]*)\(([^)]*)\)/g)) {
  console.log(`  ${m[1]}(${m[2]})`);
}

console.log('\n=== 敌方单位渲染相关片段位置 ===');
for (const kw of ["'enemy'", 'class="enemy', 'enemy-list', 'foes', 'foeWrap']) {
  const i = src.indexOf(kw);
  console.log(`  ${kw}: ${i >= 0 ? '@' + i : '未找到'}`);
}

console.log('\n=== 出牌流程：applyCardEffect 前后 ===');
const i = src.indexOf('function applyCardEffect');
console.log(src.slice(i, i + 900));
