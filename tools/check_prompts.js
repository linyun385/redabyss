// 提示词机械校验（规则见 docs/ART_PROMPT_WORKBOOK.md §四）
'use strict';
const fs = require('fs');
const path = require('path');
const ROOT = path.join(__dirname, '..');
const ABSTRACT = /symbol|emblem|abstract|essence|embodiment|minimal/i;
const SKETCH = /pencil sketch|graphite|charcoal|pencil shading/i;
const LAYOUT = /diagram|callout|inset|multiple views|study sheet/i;
const TEXTLIKE = /\btext\b|\bletters\b|\blabels?\b|\bsignature\b|\bcaption\b|\bhandwriting\b/i;
const CONCRETE = new RegExp(['leg|limb|claw|fang|tooth|teeth|gill|scale|shell|carapace|plate|spine|rib|bone|joint','eye|mouth|jaw|head|belly|skin|hide|tendril|thread|silk|spore|stalk|cap|root|vein','valve|pipe|hose|cable|wire|chain|nail|bolt|rivet|tag|gauge|dial|needle|lens|glass','grip|barrel|handle|blade|rope|knot|noose|clipboard|stamp|ledger|page|book|lantern|lamp','stitch|seam|patch|crack|chip|dent|rust|soot|ash|salt|crystal|crust|mud|water|stone','rubble|mark|scratch|tally|cloth|suit|faceplate|corridor|gear|fork|hook|tube|coil|stub',
  'metal|plate|dust|edge|groove|iris|draft|condensation|wax|markings'].join('|'), 'i');
const ALIEN = new RegExp(['salt-crystal|salt vein|salt-vein|rusted iron|iron scale|copper fin|glass bead|coral','translucent wax|wax-like|steel rod|brass valve|brass tag|copper pipe|bone and copper','bone-white|papery|bone dust|laminated|mineral crust|glassy','stitched|sewn|grafted|bolted|serial number|maintenance tag|iron brace|tar and thread','copper wire|chains threaded|ring of \\w+ eyes|six small eyes|ringed around',
  'glass gauge|heart-like|nails driven|tapped into|wired into','second smaller skeleton|second skeleton|two mouths|too many \\w+ fingers|second heart','second layer of'].join('|'), 'i');
const EVENT_DETAIL = new RegExp(['salt|rust|ash|soot|bone|crystal|seam|stitch|wire|brass|copper|glass|serial|tag','scratched|carved|cut into|nailed|bolted|laminated|moss|spore|tally|gauge|faceplate',
  'wax|still water|layer of water|condensation|metal plate|seam|dust|crack'].join('|'), 'i');
const INVERT = /upside down|inverted|hanging|belly-up|organs? (?:on|towards?) the underside|feeding organs clustered on the underside|mouth opening downward|trailing downward/i;
const UNDERLIGHT = /lit from below|red glow rising|red glow from below|red haze rising|underlight/i;
let fails = 0, warns = 0;
const fail = m => { console.log('  FAIL  ' + m); fails++; };
function judge(tag, p, kind, soft) {
  const errs = [];
  if (ABSTRACT.test(p)) errs.push('抽象词');
  if (SKETCH.test(p)) errs.push('素描词');
  if (LAYOUT.test(p)) errs.push('排版/图鉴词');
  if (TEXTLIKE.test(p) && !/no text/i.test(p)) errs.push('画面内文字词');
  if (kind === 'event') { if (!EVENT_DETAIL.test(p)) errs.push('事件缺世界细节'); }
  else if (!ALIEN.test(p)) errs.push('缺异化标记(A/C/B)');
  if (!UNDERLIGHT.test(p)) errs.push('缺"红光自下而上"');
  if ((kind === 'foe' || kind === 'card') && !INVERT.test(p)) errs.push('缺"倒吊/器官朝下"');
  const nouns = (p.match(new RegExp(CONCRETE.source, 'gi')) || []).length;
  if (nouns < 3) errs.push('具体名词不足(' + nouns + ')');
  if (!errs.length) return true;
  if (soft) { console.log('  warn  ' + tag + ' → ' + errs.join(' / ')); warns++; }
  else fail(tag + ' → ' + errs.join(' / ') + '  [' + p.slice(0, 56) + '…]');
  return false;
}
function main() {
  console.log('=== 提示词校验 ===\n');
  const famPath = path.join(ROOT, 'data', 'art_families.json');
  if (fs.existsSync(famPath)) {
    const fam = JSON.parse(fs.readFileSync(famPath, 'utf8'));
    let n = 0, good = 0;
    for (const kind of ['foe', 'card', 'event']) {
      for (const [fid, meta] of Object.entries(fam[kind] || {})) {
        n++;
        if ((meta.members || []).length > 3) fail(fid + ' → 族内成员 >3');
        if (judge(fid, meta.prompt || '', kind, true)) good++;
      }
    }
    console.log('\n[art_families.json] ' + good + '/' + n + ' 达标（其余是旧版，等重写）\n');
  }
  const wb = fs.readFileSync(path.join(ROOT, 'docs', 'ART_PROMPT_WORKBOOK.md'), 'utf8');
  let ok = 0, total = 0, kind = 'foe';
  for (const l of wb.split('\n')) {
    if (/^###\s*敌人/.test(l)) { kind = 'foe'; continue; }
    if (/^###\s*卡牌/.test(l)) { kind = 'card'; continue; }
    if (/^###\s*事件/.test(l)) { kind = 'event'; continue; }
    if (/^##\s/.test(l)) { kind = 'none'; continue; }
    if (!/^>\s+(a|an|the)\s/i.test(l)) continue;
    if (kind === 'none') continue;
    total++;
    const p = l.replace(/^>\s*/, '').trim();
    if (judge('样板', p, kind, false)) ok++;
  }
  const lines = new Array(total);
  console.log('[手册样板] ' + ok + '/' + lines.length + ' 通过');
  console.log('\n========================================');
  console.log(fails === 0 ? ('全部通过（旧版族 ' + warns + ' 条待重写）') : (fails + ' 条不合格'));
  process.exit(fails === 0 ? 0 : 1);
}
main();
