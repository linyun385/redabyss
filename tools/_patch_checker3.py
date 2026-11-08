import re
from pathlib import Path
# 1) 校验器：按手册小节判断 kind，而不是靠关键词猜
p = Path('tools/check_prompts.js'); s = p.read_text(encoding='utf-8')
old = """  const lines = wb.split('\\n').filter(l => /^>\\s+(a|an|the)\\s/i.test(l));
  let ok = 0;
  for (const l of lines) {
    const p = l.replace(/^>\\s*/, '').trim();
    const kind = /corridor|rubble|lamp|body|pool|cloth|fern|pipe|stone|door|tunnel|wall/.test(p) ? 'event' : 'foe';
    if (judge('样板', p, kind, false)) ok++;
  }"""
new = """  let ok = 0, total = 0, kind = 'foe';
  for (const l of wb.split('\\n')) {
    if (/^###\\s*敌人/.test(l)) { kind = 'foe'; continue; }
    if (/^###\\s*卡牌/.test(l)) { kind = 'card'; continue; }
    if (/^###\\s*事件/.test(l)) { kind = 'event'; continue; }
    if (/^##\\s/.test(l)) { kind = 'none'; continue; }
    if (!/^>\\s+(a|an|the)\\s/i.test(l)) continue;
    if (kind === 'none') continue;
    total++;
    const p = l.replace(/^>\\s*/, '').trim();
    if (judge('样板', p, kind, false)) ok++;
  }
  const lines = new Array(total);"""
assert old in s
s = s.replace(old, new)
p.write_text(s, encoding='utf-8')

# 2) 管道那条补名词
w = Path('docs/ART_PROMPT_WORKBOOK.md'); t = w.read_text(encoding='utf-8')
t = t.replace('> a thick pipe hanging down from the ceiling, its open end pointed upward, a puff of hot air leaking out at regular intervals, condensation running along the outside',
 '> a thick pipe hanging from the ceiling through a banded metal joint, its open end pointed upward, a puff of hot air leaking out at regular intervals, condensation running down its outside')
w.write_text(t, encoding='utf-8')
print('ok')
