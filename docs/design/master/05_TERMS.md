# 05_TERMS · 术语与命名裁决

> 这一章解决：GLOSSARY.md 的 7 条冲突怎么改。来源：D12 / glossary_check / CONFLICTS / name_consistency.py。

## 结论

7 条冲突全部有执行方案，全部不碰代码。最高优先：「共鸣→共振」（glossary 自身不一致，203 处别名出现）。最低优先：「震语者全称」（简称不影响理解）。

## 7 条裁决

| # | 冲突 | 裁决 | 改哪 | 验证 |
|---|---|---|---|---|
| 1 | 共鸣→共振 | 统一「共振」 | GLOSSARY.md 第 11 行 | grep 共鸣 = 0 |
| 2 | DLC_CANGMIN 文件名 | 保留文件名+加头注 | DLC_CANGMIN.md 头部 | 肉眼 |
| 3 | 266 vs 267 | 统一 267（含 shared） | content/README.md | 脚本 |
| 4 | layer vs band | 双轨保留 | 不改 | — |
| 5 | 苍民=种族/疯先知=职业 | glossary 加对照 | GLOSSARY.md | grep |
| 6 | 震语者全称 | glossary 补对照 | GLOSSARY.md | grep |
| 7 | 通用牌/shared | glossary 补条目 | GLOSSARY.md | grep |

## name_consistency.py 的扫描结果

| 正名 | 别名 | 出现次数 | 说明 |
|---|---|---|---|
| 凝视 | gaze | 289 | 代码键，不改 |
| 苍民 | 疯先知 | 240 | 种族/职业对照，不冲突 |
| 共振 | resonance | 216 | 代码键，不改 |
| 共振 | 共鸣 | **203** | **最高优先修正** |
| 震语者 | tremor | 162 | 代码键 |
| 维护者 | 黯民 | 149 | 别名需 glossary 对照 |
| 下潜者 | diver | 149 | 代码键 |
| 维护者 | anmin | 117 | 代码键 |
| 层 | band | 100 | 双轨保留 |

## 本章待确认

| # | 事项 | 倾向 |
|---|---|---|
| 1 | 共鸣→共振的 glossary 修改是否执行 | 是——零风险，改完所有新文档统一 |
| 2 | name_consistency.py 是否纳入常规检查 | 是——与 rule_coverage.py 形成文档质量双检查 |
