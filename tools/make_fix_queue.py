# -*- coding: utf-8 -*-
"""从质检台账生成修复队列 —— 用 125 而不是它自述的 78。

为什么要脚本：2026-11-02 夜班里 GLM 人工汇总「不合格约 78」，实际 125（低估 38%），
而它自己的 qa_report.py 算的也是 125。结论：**汇总数字必须由脚本出**。

产出：
  data/queue_redraw.json   需要重画的（有白画框/电器/文字这类改提示词救不回来的）
  data/queue_rewrite.json  只需改提示词的（构图对，只是提示词拉错了东西）
  data/queue_summary.md    一页汇总，给人看的

用法：python tools/make_fix_queue.py
"""
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
GAME = Path(__file__).resolve().parents[1]
CAT = {r['id']: r for r in json.loads((GAME / 'data' / 'art_catalog.json').read_text(encoding='utf-8'))}
PROMPTS = {r['id']: r['prompt'] for r in json.loads((GAME / 'data' / 'zh_prompts_full.json').read_text(encoding='utf-8'))}
SPLIT = '洞底是一整片深红的光'
IX = ('锈穿', '焊缝', '砸扁', '铆钉头')
XF = ('反复划过', '刮得发亮', '凹痕')
ID_RE = re.compile(r'^\|\s*((?:enemy|anm|cng|dive|trem|event)_[A-Za-z0-9_]+)\s*\|')


def main():
    rows = defaultdict(dict)
    for p in sorted((GAME / 'data' / 'qa').glob('QA_*.md')):
        for ln in p.read_text(encoding='utf-8', errors='replace').splitlines():
            m = ID_RE.match(ln)
            if not m:
                continue
            cells = [c.strip() for c in ln.strip().strip('|').split('|')]
            rid = m.group(1)
            last = cells[-1] if cells else ''
            if last in ('', '—', '-', '–') or last.startswith('合格'):
                v = 'ok'
            elif '重画' in last:
                v = 'redraw'
            elif '提示词' in last:
                v = 'rewrite'
            else:
                v = 'other'
            rows[rid] = {'verdict': v, 'note': last[:160],
                         'subject': cells[-2][:80] if len(cells) >= 2 else '',
                         'file': p.name}

    redraw = [k for k, v in rows.items() if v['verdict'] == 'redraw']
    rewrite = [k for k, v in rows.items() if v['verdict'] == 'rewrite']
    other = [k for k, v in rows.items() if v['verdict'] == 'other']

    out1 = GAME / 'data' / 'queue_redraw.json'
    out1.write_text(json.dumps(
        [{'id': i, 'name': CAT.get(i, {}).get('name', ''), 'kind': i.split('_')[0],
          'note': rows[i]['note'], 'qa': rows[i]['file']} for i in sorted(redraw)],
        ensure_ascii=False, indent=1), encoding='utf-8')

    out2 = GAME / 'data' / 'queue_rewrite.json'
    out2.write_text(json.dumps(
        [{'id': i, 'name': CAT.get(i, {}).get('name', ''), 'kind': i.split('_')[0],
          'note': rows[i]['note'], 'qa': rows[i]['file'],
          'prompt_body': PROMPTS[i].split(SPLIT)[0]} for i in sorted(rewrite)],
        ensure_ascii=False, indent=1), encoding='utf-8')

    # 漏改的 9 条
    have = set()
    for p in (GAME / 'data' / 'rewrite').glob('RW_*.json'):
        try:
            for x in json.loads(p.read_text(encoding='utf-8')):
                if isinstance(x, dict) and x.get('id'):
                    have.add(x['id'])
        except Exception:
            pass
    missing = []
    for i in CAT:
        k = i.split('_')[0]
        s = PROMPTS[i].split(SPLIT)[0]
        if k in ('dive', 'trem') and not any(w in s for w in IX) and i not in have:
            missing.append(i)
        elif k == 'event' and not any(w in s for w in XF) and i not in have:
            missing.append(i)
    (GAME / 'data' / 'rewrite_missing.json').write_text(
        json.dumps([{'id': i, 'name': CAT[i]['name'], 'body': PROMPTS[i].split(SPLIT)[0],
                     'tail': PROMPTS[i].split(SPLIT)[1] if SPLIT in PROMPTS[i] else ''}
                    for i in missing], ensure_ascii=False, indent=1), encoding='utf-8')

    md = ['# 修复队列汇总（脚本生成）\n',
          '| 项 | 数 |\n|---|---|',
          '| 已质检 | %d |' % len(rows),
          '| 合格 | %d |' % sum(1 for v in rows.values() if v['verdict'] == 'ok'),
          '| 需重画 | %d |' % len(redraw),
          '| 只改提示词 | %d |' % len(rewrite),
          '| 判定异常 | %d |' % len(other),
          '| **不合格合计** | **%d** |' % (len(redraw) + len(rewrite)),
          '| 提示词漏改 | %d |' % len(missing), '',
          '按卡组分布（不合格）：', '',
          '| 组 | 重画 | 改提示词 |\n|---|---|---|']
    by = defaultdict(Counter)
    for i in redraw:
        by[i.split('_')[0]]['redraw'] += 1
    for i in rewrite:
        by[i.split('_')[0]]['rewrite'] += 1
    for k, c in sorted(by.items()):
        md.append('| %s | %d | %d |' % (k, c['redraw'], c['rewrite']))
    (GAME / 'data' / 'queue_summary.md').write_text('\n'.join(md) + '\n', encoding='utf-8')

    print('重画 %d 张 → data/queue_redraw.json' % len(redraw))
    print('只改提示词 %d 张 → data/queue_rewrite.json' % len(rewrite))
    print('判定异常 %d 张%s' % (len(other), ('：' + ', '.join(other[:5])) if other else ''))
    print('提示词漏改 %d 条 → data/rewrite_missing.json' % len(missing))
    print('漏改的: %s' % ' '.join(missing))
    return 0


if __name__ == '__main__':
    sys.exit(main())
