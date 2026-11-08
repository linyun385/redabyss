# -*- coding: utf-8 -*-
"""docs/design 全量索引生成（2026-11-06 · 兜底任务 3）。
只读 docs/design/**/*.md；只写 docs/design/_INDEX_1106.md。
跑法：python -I tools/_design_index_1106.py
摘要为机械抽取（首个标题 + 首个正文行截 70 字），非逐篇精读。
"""
import io, os, re

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'docs', 'design')
OUT = os.path.join(ROOT, '_INDEX_1106.md')
NL = chr(10)

AUTH = [
    ('世界观名词（生物/族群）', 'glossary.json（仓库根）', '自述「所有命名从这里取」'),
    ('五脉判据', 'docs/design/vein_flavor_card.md', '提炼自 T400_master §2.1'),
    ('引擎行为基准（能量/手牌/结局分档等）', 'docs/design/all_numbers.md + engine_diff.md', '含 web 与 core.js 双副本差异'),
    ('规则机制总览', 'docs/design/T323_RULES.md', '注意：引 core.js 行号，core.js 是过期副本（见 _CONFLICTS_1106 第 5 条）'),
    ('维护者核心卡实测', 'docs/design/_VERIFY_anmin_core_cards.md', '45 项实测 + 自作主张三处待确认'),
    ('附属卡设计（2026-11-06 夜班）', 'docs/design/anmin_minions/00_README.md', '8 文件入口'),
    ('敌人全量 roster 与战斗台词', 'docs/design/enemies/_roster_full.tmp.md + battle_lines.md', '113 只'),
    ('数值曲线', 'docs/design/curves/curve_report.md + parts_economy.md', '脚本 tools/_curve_audit_1106.py、tools/_parts_economy_1106.py'),
    ('音效钩子', 'docs/SFX_LIST.md（docs 根，不在 design/ 下）', '19 钩子 + 8 氛围'),
    ('术语一致性', 'docs/design/glossary_audit.md', '15 条 + 排除项'),
    ('矛盾追踪（本夜班版）', 'docs/design/_CONFLICTS_1106.md', '旧账见 _CONFLICTS.md / old_doc_conflicts.md'),
    ('引导文案', 'docs/design/tutorial/first_3_battles.md', ''),
    ('结局文本', 'docs/design/endings/ten_endings.md', ''),
    ('商店/回收文案', 'docs/design/shops/shop_and_recycle.md', ''),
    ('卡面文案审查', 'docs/design/copy/flavor_audit.md + name_audit.md', '40 条 flavor + 11 条名字'),
]

def main():
    rows = []
    for root, dirs, files in os.walk(ROOT):
        dirs.sort()
        for f in sorted(files):
            if not f.endswith('.md'):
                continue
            p = os.path.relpath(os.path.join(root, f), ROOT).replace(chr(92), '/')
            full = os.path.join(root, f)
            if p.endswith('_INDEX_1106.md'):
                continue
            try:
                t = io.open(full, encoding='utf-8').read()
            except Exception:
                t = ''
            lines = [l for l in t.split(NL) if l.strip()]
            title, desc = '', ''
            for l in lines[:6]:
                if l.startswith('#') and not title:
                    title = l.lstrip('#').strip()[:60]
                elif not l.startswith('#') and not l.startswith('>') and not desc:
                    desc = re.sub(r'[|*>`\[\]]', '', l).strip()[:70]
            if not title:
                title = f
            rows.append((p, title, desc))

    out = io.open(OUT, 'w', encoding='utf-8')
    out.write('# docs/design 全量索引（机械摘要 + 权威地图）' + NL + NL)
    out.write('> 2026-11-06 夜班 · 兜底任务 3。**摘要为脚本机械抽取**（每个 md 的首个标题 + 首个正文行截 70 字），不是逐篇精读——机械摘要失真的，以文件本体为准。' + NL)
    out.write('> 由 `tools/_design_index_1106.py` 生成，可重跑刷新。共 %d 个 md。' % len(rows) + NL + NL)
    out.write('## 权威文件地图（手工维护，先看这里）' + NL + NL)
    out.write('| 要查什么 | 去哪 | 备注 |' + NL)
    out.write('|---|---|---|' + NL)
    for a, b, c in AUTH:
        out.write('| %s | %s | %s |' % (a, b, c) + NL)
    out.write(NL + '## 全量文件（机械摘要）' + NL)
    cur = ''
    for p, title, desc in rows:
        d = os.path.dirname(p)
        if d != cur:
            cur = d
            out.write(NL + '### %s' % (d if d != 'docs/design' else 'docs/design（根）') + NL + NL)
        out.write('- `%s` — %s%s' % (os.path.basename(p), title, ('：' + desc) if desc else '') + NL)
    out.close()
    print('indexed %d files -> %s' % (len(rows), OUT))

if __name__ == '__main__':
    main()
