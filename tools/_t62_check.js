/* T62 可达性自检（可重跑）：每条新事件在对应 (eco, band) 的绑定表里被引用 + 效果字段全在引擎支持清单内。
   用法：node tools/_t62_check.js —— 任何失败 exit 1 */
'use strict';
const path = require('path');
const fs = require('fs');
const b = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'data', 'mapgen_bindings.json'), 'utf8'));
const ev = require(path.join(__dirname, '..', 'events', 'all.json'));
const web = fs.readFileSync(path.join(__dirname, '..', 'web', 'index.html'), 'utf8');

const SUPPORTED = ['heal', 'damage', 'gaze', 'gold', 'maxhp', 'card_reward', 'relic'];
const newEv = ev.filter(x => x.eco);
let bad = 0;

// ① 绑定表引用
newEv.forEach(x => {
  const cell = b.eco[x.eco];
  if (!cell) { console.error('FAIL 生态缺失 ' + x.eco); bad++; return; }
  (x.bands || [x.layer]).forEach(band => {
    const c = cell.bands[String(band)];
    if (!c || c.event.indexOf(x.id) < 0) { console.error('FAIL 未被引用 ' + x.id + '@' + x.eco + '/b' + band); bad++; }
  });
});

// ② 效果字段合法性
newEv.forEach(x => x.options.forEach((o, i) => {
  Object.keys(o.result || {}).forEach(k => {
    if (SUPPORTED.indexOf(k) < 0) { console.error('FAIL 效果字段不支持: ' + x.id + ' 选项' + (i + 1) + ' r.' + k); bad++; }
  });
}));

// ③ 内联 RAW 同步（web/index.html 的 RAW.events 含全部新 id）
newEv.forEach(x => {
  if (web.indexOf('"' + x.id + '"') < 0) { console.error('FAIL 内联 RAW 缺 ' + x.id); bad++; }
});

// ④ 说明书腔自检：result_text / body 不出现「你获得/你失去/你得到 + 数字」
const badStyle = [];
newEv.forEach(x => {
  const texts = [x.body].concat(x.options.map(o => o.result_text || ''));
  texts.forEach(t => {
    if (/你(获得|失去|得到)[^。]*\d/.test(t)) badStyle.push(x.id);
  });
});
if (badStyle.length) { console.error('FAIL 疑似说明书腔: ' + badStyle.join(',')); bad++; }

console.log(bad ? bad + ' 处失败' : 'T62 自检全过：' + newEv.length + ' 条新事件（绑定可达 / 效果合法 / RAW 同步 / 无说明书腔）');
process.exit(bad ? 1 : 0);
