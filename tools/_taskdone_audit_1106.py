# -*- coding: utf-8 -*-
"""TASK_DONE.md 产出存在性审计（2026-11-06 · 兜底任务 2）。

只读：TASK_DONE.md。只写：docs/design/_TASKDONE_AUDIT_1106.md。
跑法：python -I tools/_taskdone_audit_1106.py
"""
import io, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'TASK_DONE.md')
OUT = os.path.join(ROOT, 'docs', 'design', '_TASKDONE_AUDIT_1106.md')

def main():
    txt = io.open(SRC, encoding='utf-8').read()
    entries = re.split(r'\n## ', txt)[1:]
    report = []
    total = 0
    with_out = 0
    broken = []   # (title, missing paths)
    nofile = []   # (title) output 里没有任何可核路径
    for e in entries:
        title = e.split('\n')[0].strip()
        total += 1
        # output 块：从 "- output:" 到下一个 "- check"
        m = re.search(r'- output:(.*?)(?=\n- check:|\n- status)', e, re.S)
        if not m:
            continue
        block = m.group(1)
        paths = re.findall(r'(?:docs|tools|tasks|web|cards|engine|glossary\.json|TASK_DONE\.md)[\w\-/\\\.]*', block)
        paths = [p.strip('，。；、）') for p in paths if p.strip('，。；、）')]
        if not paths:
            nofile.append(title)
            continue
        with_out += 1
        missing = []
        for p in paths:
            norm = p.replace('\\', '/')
            if norm.endswith('.md') or '.' in os.path.basename(norm):
                if not os.path.exists(os.path.join(ROOT, norm)):
                    missing.append(p)
        if missing:
            broken.append((title, missing))

    report.append('# TASK_DONE 产出存在性审计（自动生成，勿手改）')
    report.append('')
    report.append('> 由 `tools/_taskdone_audit_1106.py` 生成。基准目录：仓库根（game/）。')
    report.append('> 口径：只核 `output:` 块里带扩展名的路径是否存在于磁盘；不含扩展名的描述行跳过；「.bak」历史备份视同存在（存在性而非时效性）。')
    report.append('')
    report.append('## 总览')
    report.append('')
    report.append('| 项 | 数 |')
    report.append('|---|---|')
    report.append('| 条目总数 | %d |' % total)
    report.append('| 带可核路径的条目 | %d |' % with_out)
    report.append('| 无路径条目（纯分析/结论类） | %d |' % len(nofile))
    report.append('| **产出缺失条目** | **%d** |' % len(broken))
    report.append('')
    if broken:
        report.append('## 缺失明细')
        report.append('')
        report.append('| 条目 | 缺失路径 |')
        report.append('|---|---|')
        for title, missing in broken:
            report.append('| %s | %s |' % (title.replace('|', '\\|'), '、'.join(missing)))
    else:
        report.append('## 缺失明细')
        report.append('')
        report.append('无。所有带路径的条目，其产出文件都在磁盘上。')
    io.open(OUT, 'w', encoding='utf-8').write('\n'.join(report) + '\n')
    print('条目 %d / 带路径 %d / 缺失 %d' % (total, with_out, len(broken)))
    for title, missing in broken[:20]:
        print('  MISSING:', title[:50], '->', missing[:3])

if __name__ == '__main__':
    main()
