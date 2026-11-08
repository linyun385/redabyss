# -*- coding: utf-8 -*-
"""收紧/放宽 check_prompts.js：异化标记用关键词集，事件不强制异化但要有世界细节；素描词只拦"pencil sketch"这类短语。"""
from pathlib import Path

G = Path(__file__).resolve().parents[1]
P = G / 'tools' / 'check_prompts.js'
s = P.read_text(encoding='utf-8')

s = s.replace(
    "const SKETCH = /pencil|graphite|charcoal/i;",
    "const SKETCH = /pencil sketch|graphite drawing|charcoal drawing|pencil shading/i;")

old_alien = s[s.index('const ALIEN = new RegExp(['):s.index("].join('|'), 'i');") + len("].join('|'), 'i');")]
new_alien = """const ALIEN = new RegExp([
  // A 材料替代
  'salt-crystal|salt vein|rusted iron|iron scale|copper fin|glass bead|coral|translucent wax',
  'steel rod|brass valve|brass tag|copper pipe|bone and copper|bone-white|papery|bone dust',
  'laminated|mineral crust|wax-like|glassy',
  // C 工艺寄生
  'stitched|sewn|grafted|bolted|bolted on|serial number|maintenance tag|iron brace|tar and thread',
  'copper wire|chains threaded|hoses? grafted|patches? of another',
  // B 器官错位
  'ringed around|ring of \\\\w+ eyes|six small eyes|second smaller skeleton|two mouths',
  'too many \\\\w+ fingers|second heart|second layer of'
].join('|'), 'i');
// 事件不强制异化标记，但必须有"这个世界的细节"（工艺/材料/痕迹）
const EVENT_DETAIL = new RegExp([
  'salt|rust|ash|soot|bone|crystal|seam|stitch|wire|brass|copper|glass|serial|tag',
  'scratched|carved|cut into|nailed|bolted|stitched|laminated|moss|spore|tally|gauge'
].join('|'), 'i');"""
s = s.replace(old_alien, new_alien)
s = s.replace("const TEXTLIKE = /\\btext\\b|\\bletters\\b|\\blabels?\\b|\\bsignature\\b|\\bcaption/i;",
              "const TEXTLIKE = /\\btexture\\b(?!)|\\btext\\b|\\bletters\\b|\\blabels?\\b|\\bsignature\\b|\\bcaption/i;")

s = s.replace("  if (!ALIEN.test(p)) errs.push('缺异化标记（A/C/B）');",
              "  if (kind === 'event') {\n"
              "    if (!EVENT_DETAIL.test(p)) errs.push('事件缺世界细节（工艺/材料/痕迹）');\n"
              "  } else if (!ALIEN.test(p)) errs.push('缺异化标记（A/C/B）');")

# art_families.json 里的旧族先只报 warn（等重写），手册样板才硬性失败
s = s.replace("        if (checkPrompt(fid, p, kind)) famOk++;",
              "        if (checkPrompt(fid, p, kind, true)) famOk++;")
s = s.replace("function checkPrompt(tag, p, kind) {", "function checkPrompt(tag, p, kind, soft) {")
s = s.replace("  if (errs.length) fail(tag + ' → ' + errs.join(' / ') + '  [' + p.slice(0, 60) + '…]');",
              "  if (errs.length) {\n"
              "    if (soft) { console.log('  warn  ' + tag + ' → ' + errs.join(' / ')); }\n"
              "    else fail(tag + ' → ' + errs.join(' / ') + '  [' + p.slice(0, 60) + '…]');\n"
              "  }")

P.write_text(s, encoding='utf-8')
print('check_prompts.js 已调整：异化标记关键词集 / 事件豁免但需世界细节 / 旧族只 warn')
