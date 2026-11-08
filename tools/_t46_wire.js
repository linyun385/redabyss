// T46 一次性 wire：把 events/all.json 与 relics/all.json 同步进 web 内联 RAW
'use strict';
const fs = require('fs');
const path = require('path');
const ROOT = path.join(__dirname, '..');
const web = path.join(ROOT, 'web', 'index.html');
let s = fs.readFileSync(web, 'utf8');

const m = s.match(/const RAW = (\{.*?\});\n/);
if (!m) { console.error('RAW 未找到'); process.exit(1); }
const raw = JSON.parse(m[1]);
raw.events = JSON.parse(fs.readFileSync(path.join(ROOT, 'events/all.json'), 'utf8'));
if (raw.events.events) raw.events = raw.events.events;
raw.relics = JSON.parse(fs.readFileSync(path.join(ROOT, 'relics/all.json'), 'utf8'));
if (raw.relics.relics) raw.relics = raw.relics.relics;
raw.enemies = JSON.parse(fs.readFileSync(path.join(ROOT, 'enemies/all.json'), 'utf8'));
if (raw.enemies.enemies) raw.enemies = raw.enemies.enemies;
s = s.replace(m[0], 'const RAW = ' + JSON.stringify(raw) + ';\n');
fs.writeFileSync(web, s, 'utf8');
['diver', 'tremor', 'anmin', 'cangmin'].forEach(cls => {
  raw[cls] = JSON.parse(fs.readFileSync(path.join(ROOT, 'cards/' + cls + '.json'), 'utf8'));
});
console.log('RAW 同步完成: events=' + raw.events.length + ' relics=' + raw.relics.length + ' enemies=' + raw.enemies.length + ' cards=' + ['diver','tremor','anmin','cangmin'].map(c => raw[c].length).join('/'));
