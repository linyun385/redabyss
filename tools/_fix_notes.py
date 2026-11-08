# -*- coding: utf-8 -*-
"""修掉任务文件里被 PowerShell 反引号转义弄坏的那段「已确认前提」。

事故原因：把 python -c "…" 写在 PowerShell 双引号里，反引号在 PowerShell 里是转义符，
`b / `t 这类组合被 PowerShell 吃掉（b 被删、t 变成制表符）。
所以这段文字里**一律不用反引号**，改用「」。
"""
from pathlib import Path

GAME = Path(__file__).resolve().parents[1]

NOTES = {
    'tasks/T54.md': [
        '## 已确认前提（2026-10-30 18:35）',
        '- **整局一张大图**：深度带 band = 层（D1 最上 … D8 最下），不是每层一张图。',
        '- **BOSS 不在生成阶段决定**：生成器只标出「跨带边」（from 在某带、to 在下带）并打 crossBand 标记，运行时再由 T57 判定是否替换成 BOSS。',
        '- 设计文档必须给出「运行时替换事件格」的接口定义与参数（p0、衰减系数、下限）。',
        '',
    ],
    'tasks/T55.md': [
        '## 已确认前提（2026-10-30 18:35）',
        '- 生成器只产 band 与 crossBand 标记，**不产 boss 节点**（boss 由运行时替换产生）。',
        '- 不变量按整张大图的 8 个深度带校验。',
        '',
    ],
    'tasks/T56.md': [
        '## 已确认前提（2026-10-30 18:35）',
        '- 地图是**整局一张大图**（8 个深度带）：总图要支持缩放/拖动，小图只显示当前带附近。',
        '- 新地图**成为默认**；旧 4 行地图已备份为 web/index.html.bak-mapgen-v0-20261030-1834，不再保留切换开关。',
        '',
    ],
    'tasks/T57.md': [
        '## 已确认前提（2026-10-30 18:35）',
        '- **BOSS 是运行时判定的**：第一次跨带必出 BOSS；之后按 p0 逐带衰减（有下限、不为 0）；命中时把该跨带的事件格**运行时替换**为 BOSS（类型与内容一起换，生成结果不变）。',
        '- 参数写进 tools/mapgen_spec.json：boss.firstAlways、boss.p0、boss.decay、boss.min。',
        '',
    ],
    'tasks/T58.md': [
        '## 已确认前提（2026-10-30 18:35）',
        '- 每个（生态 × 深度带）都要有 **BOSS 池**，供运行时替换使用（生成阶段不用它）。',
        '',
    ],
    'tasks/T59.md': [
        '## 已确认前提（2026-10-30 18:35）',
        '- 模拟必须按**运行时 BOSS 判定**走（首次跨带必 BOSS + 递减概率），并统计「实际打了几次 BOSS」。',
        '',
    ],
}


def main():
    for rel, note in NOTES.items():
        p = GAME / rel
        s = p.read_text(encoding='utf-8')
        start = s.find('## 已确认前提')
        if start >= 0:
            end = s.find('\n## ', start + 1)
            s = (s[:start] + s[end + 1:]) if end > 0 else s[:start]
        # 插到第一个二级标题之前（若已删掉开头那段，第一个 ## 就是正文首节）
        idx = s.find('\n## ')
        block = '\n'.join(note) + '\n\n'
        if idx >= 0:
            s = s[:idx + 1] + block + s[idx + 1:]
        else:
            s = s.rstrip() + '\n\n' + block
        p.write_text(s, encoding='utf-8')
        print('fixed', rel, len(s), 'chars')


if __name__ == '__main__':
    main()
