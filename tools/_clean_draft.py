# -*- coding: utf-8 -*-
"""清理草稿里误写进去的界面字段（_desc / _updesc 之类）
原因：文件里存的 _desc 是「保存那一刻」的翻译，会随导出写进 cards/*.json 污染数据。
只删 _ 开头的键，别的都不动。先备份。"""
import json, shutil, time, io
from pathlib import Path

GAME = Path(__file__).resolve().parents[1]
P = GAME / 'cards' / '_draft.json'
d = json.loads(P.read_text(encoding='utf-8'))

bak = P.with_name('_draft.json.bak-' + time.strftime('%Y%m%d-%H%M%S'))
shutil.copy2(P, bak)

removed = []
for op in d.get('ops', []):
    card = op.get('card')
    if not isinstance(card, dict):
        continue
    for k in [k for k in card if k.startswith('_')]:
        removed.append('%s.%s' % (op.get('id'), k))
        del card[k]

P.write_text(json.dumps(d, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
out = io.StringIO()
out.write('备份: %s\n' % bak.name)
out.write('删掉的字段: %s\n' % (', '.join(removed) if removed else '（无，本来就干净）'))
out.write('草稿剩余 %d 条操作\n' % len(d.get('ops', [])))
print(out.getvalue())
