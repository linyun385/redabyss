/* T58 绑定表构建脚本（一次性，保留供重建）：从真实数据生成 data/mapgen_bindings.json。
   规则（口径 B，见 docs/CONTENT_PLAN.md）：
   - 格（生态,带）池 = 该生态母本批（全部普通/精英/boss/事件）；
   - 普通敌人 < 3 时从相邻带母本生态借 1–2 只补足（_meta.borrowed 记录）；
   - shop tier 按 band（1–3→1 / 4–6→2 / 7–8→3）；
   - mods：数值修饰（hpMul/atkMul，深于母本带加强、浅于母本带减弱），假设值供 T61/T65 调。
   用法：node tools/_t58_build.js */
'use strict';
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const spec = JSON.parse(fs.readFileSync(path.join(ROOT, 'tools', 'mapgen_spec.json'), 'utf8'));
const enemies = require(path.join(ROOT, 'enemies', 'all.json'));
const events = require(path.join(ROOT, 'events', 'all.json'));

const ECOS = spec.ecos;
const BANDS = [1, 2, 3, 4, 5, 6, 7, 8];
const shopTier = b => (b <= 3 ? 1 : b <= 6 ? 2 : 3);
const mod = (band, home) => {
  const d = band - home;
  const hpMul = Math.round(Math.max(0.7, Math.min(1.6, 1 + Math.max(0, d) * 0.12 - Math.max(0, -d) * 0.10)) * 100) / 100;
  const atkMul = Math.round(Math.max(0.7, Math.min(1.6, 1 + Math.max(0, d) * 0.08 - Math.max(0, -d) * 0.06)) * 100) / 100;
  return { hpMul, atkMul };
};

const ecoById = {}; ECOS.forEach(e => { ecoById[e.id] = e; });
const homeEcoAt = {}; ECOS.forEach(e => { homeEcoAt[e.homeBand] = e.id; });

const eco = {};
const legendEnemy = {}, legendEvent = {};
const borrowLog = [];

ECOS.forEach(e => {
  const ownE = enemies.filter(x => x.layer === e.homeBand);
  const ownN = ownE.filter(x => x.tier === 'normal').map(x => x.id);
  const ownL = ownE.filter(x => x.tier === 'elite').map(x => x.id);
  const ownB = ownE.filter(x => x.tier === 'boss').map(x => x.id);
  const ownV = events.filter(x => x.layer === e.homeBand).map(x => x.id);
  ownE.forEach(x => { legendEnemy[x.id] = x.name; });
  ownV.forEach(x => { const def = events.find(v => v.id === x); legendEvent[x] = def ? def.title : x; });

  const bands = {};
  BANDS.forEach(b => {
    let enemy = ownN.slice();
    const borrowed = [];
    // 普通敌人不足 3：从相邻带母本生态借（优先邻近母本带）
    if (enemy.length < 3) {
      const neighbors = BANDS.filter(x => Math.abs(x - e.homeBand) === 1)
        .sort((a, c) => Math.abs(a - e.homeBand) - Math.abs(c - e.homeBand));
      for (const nb of neighbors) {
        if (enemy.length >= 3) break;
        const pool = enemies.filter(x => x.layer === nb && x.tier === 'normal' && enemy.indexOf(x.id) < 0);
        for (const p of pool) {
          if (enemy.length >= 3) break;
          enemy.push(p.id); borrowed.push(p.id);
          borrowLog.push(e.id + '@b' + b + ' 借 ' + p.id + '（' + p.name + '，母本带 D' + nb + '）');
        }
      }
    }
    bands[String(b)] = {
      enemy, elite: ownL.slice(), boss: ownB.slice(), event: ownV.slice(),
      shop: shopTier(b),
      _meta: { borrowed, mods: mod(b, e.homeBand) }
    };
  });
  eco[e.id] = { name: e.name, homeBand: e.homeBand, bands };
});

const out = {
  _about: 'T58 生态×深度内容绑定表。规则与字段见 docs/CONTENT_PLAN.md §3.2 与 tools/mapgen_spec.json。生成：node tools/_t58_build.js（勿手改 id）。',
  _legend: { enemies: legendEnemy, events: legendEvent },
  borrowLog,
  eco
};
const OUT = path.join(ROOT, 'data', 'mapgen_bindings.json');
fs.mkdirSync(path.dirname(OUT), { recursive: true });
fs.writeFileSync(OUT, JSON.stringify(out, null, 1));
console.log('绑定表已生成：' + OUT);
console.log('借调记录：' + borrowLog.length + ' 条');
borrowLog.forEach(l => console.log('  ' + l));
