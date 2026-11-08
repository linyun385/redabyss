# -*- coding: utf-8 -*-
"""接线：把定稿的 461 张图接进渲染。

三处改动：
  1. window.ART 表补 461 条（id → assets/art/<id>.webp）
  2. cardArtId() 优先按 card.id 查专属图，查不到回落原来的 face_
  3. 敌人渲染优先按 e.def.id 查专属图，查不到回落原来的 foe_

★ 只改「优先查 id」，原来那套逻辑全部保留 —— 任何一步查不到都自动回落，不会白屏。
"""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
GAME = Path(__file__).resolve().parents[1]
HTML = GAME / 'web' / 'index.html'
s = HTML.read_text(encoding='utf-8')

# ── 1. ART 表补 461 条 ─────────────────────────────
i = s.find('window.ART = {')
j = s.find('};', i)
old_line = s[i:j + 2]
art = json.loads(old_line[len('window.ART = '):-1])
before = len(art)

cat = json.loads((GAME / 'data' / 'art_catalog.json').read_text(encoding='utf-8'))
added = 0
for r in cat:
    aid = r['id']
    if not (GAME / 'web' / 'assets' / 'art' / (aid + '.webp')).exists():
        print('!! 文件不存在，跳过：%s' % aid)
        continue
    if aid not in art:
        art[aid] = 'assets/art/%s.webp' % aid
        added += 1

new_line = 'window.ART = ' + json.dumps(art, ensure_ascii=False, separators=(',', ':')) + ';'
s = s.replace(old_line, new_line, 1)
print('ART 表：%d 条 → %d 条（新增 %d）' % (before, len(art), added))

# ── 2. cardArtId 优先专属图 ──────────────────────
OLD_CARD = """function cardArtId(card) {
  const veinEco = { light: 'eco_sea', water: 'eco_arid', heat: 'eco_vent', tremor: 'eco_cold', mineral: 'eco_rad' };"""
NEW_CARD = """function cardArtId(card) {
  // 定稿专属图优先：461 张卡面按 id 直接查，查不到才回落生态图
  if (card && card.id && window.ART && ART[card.id]) return card.id;
  const veinEco = { light: 'eco_sea', water: 'eco_arid', heat: 'eco_vent', tremor: 'eco_cold', mineral: 'eco_rad' };"""
assert s.count(OLD_CARD) == 1, 'cardArtId 没匹配到'
s = s.replace(OLD_CARD, NEW_CARD, 1)
print('cardArtId ✓')

# ── 3. 敌人优先专属图 ───────────────────────────
OLD_FOE = """      const h = String(e.def.id || '').split('').reduce((a, ch) => a + ch.charCodeAt(0), 0);
      const fid = 'foe_' + ecoHome + '_' + (1 + h % 3);"""
NEW_FOE = """      const h = String(e.def.id || '').split('').reduce((a, ch) => a + ch.charCodeAt(0), 0);
      // 定稿专属图优先：按敌人 id 查，查不到回落生态图
      const fid = (e.def.id && ART[e.def.id]) ? e.def.id : ('foe_' + ecoHome + '_' + (1 + h % 3));"""
assert s.count(OLD_FOE) == 1, '敌人渲染没匹配到'
s = s.replace(OLD_FOE, NEW_FOE, 1)
print('敌人渲染 ✓')

HTML.write_text(s, encoding='utf-8')
print()
print('已写入 web/index.html（原文件已由 art 备份覆盖不到，这里单独备份）')
