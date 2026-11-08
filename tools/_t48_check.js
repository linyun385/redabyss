// T48 自检：3 个新敌人加载并出手（引擎断言式）
'use strict';
const path = require('path');
const RA = require(path.join(__dirname, '..', 'engine', 'core.js'));
const arr = require(path.join(__dirname, '..', 'enemies', 'all.json'));
const list = Array.isArray(arr) ? arr : arr.enemies;
const picks = ['盐壳拾荒者', '光蛭母·逆流', '墟蛹·未完成'];
let bad = 0;
for (const name of picks) {
  const def = list.find(e => e.name === name);
  if (!def) { console.error('FAIL 找不到 ' + name); bad++; continue; }
  const run = RA.newRun('diver', { seed: 4242 });
  run.depth = def.layer;
  const C = RA.startCombat(run, [def]);
  let acted = 0;
  let guard = 0;
  while (!C.over && guard++ < 30) {
    // 玩家随便出一张能出的
    for (let i = 0; i < C.hand.length; i++) { const r = RA.playCard(C, i, C.enemies.findIndex(e => !e.dead)); if (r.ok) break; }
    if (C.over) break;
    const logLen = C.log.length;
    RA.endTurn(C);
    if (C.log.length > logLen) acted++;
    if (C.enemies.every(e => e.dead)) break;
  }
  const actedByEnemy = C.log.some(l => l.includes(def.name) && (/击中你/.test(l) || /合拢/.test(l) || /变得更快/.test(l) || /抽走/.test(l) || /亮了一下/.test(l)));
  if (acted && actedByEnemy) console.log('  ok  ' + name + ' 加载并出手（回合 ' + acted + '，敌方日志命中）');
  else { console.error('FAIL ' + name + ' 未正常出手'); bad++; }
}
process.exit(bad ? 1 : 0);
