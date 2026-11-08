# 全量回归记录（T261，2026-11-03 夜班）

依次实跑，每条输出落盘本目录（*.txt 为原始输出）。

| # | 检查器 | 命令 | exit | 结果摘要 | 日志 |
|---|---|---|---|---|---|
| 1 | web 静态检查 | node tools/check_web.js | 0 | 全部通过（0 个警告） | check_web.txt |
| 2 | 引擎测试 | node tools/test_engine.js | 0 | 全部通过 | test_engine.txt |
| 3 | 数据包检查 | node tools/pack_check.js all | 0 | 全部通过（5 个警告，均为信息性） | pack_check_all.txt |
| 4 | 绑定表 | node tools/check_bindings.js | 0 | 全部达标 | check_bindings.txt |
| 5 | 地图生成测试 | node tools/mapgen_test.js | 0 | 全部断言通过；100 图 1337ms（<2s） | mapgen_test.txt |
| 6 | 色板 | node tools/check_palette.js | 0 | T71 全过 | check_palette.txt |
| 7 | 对比度 | node tools/check_contrast.js | 0 | T76 全过 | check_contrast.txt |
| 8 | 回返判定 | node tools/check_backtrack.js | 0 | T75 全过（500 次分布 ±5pp） | check_backtrack.txt |
| 9 | 生态混合 | node tools/check_ecomix.js --runs 100 | 0 | T72 验收全过 | check_ecomix.txt |
| 10 | 卡牌强度审计 | node tools/card_power.js --strict | 0 | R1–R4 四职业全部达标 | card_power_strict.txt |
| 11 | 地图节奏模拟 | node tools/mapgen_sim.js --runs 300 --assert | 0 | 步数≥36 ✓ / D2–D7≥4.2 ✓ / 通关 100% ✓ | mapgen_sim_assert.txt |
| 12 | 四职业模拟 | node tools/sim.js --class X --runs 300 ×4 | 0 | diver 3% / tremor 1% / anmin 2% / cangmin 3%（与 T252 的 500 局基线一致，非回归） | sim_*.txt |
| 13 | 提示词 lint | python -I tools/prompt_lint.py | 0 | 扫 461、命中 133（rewrite 前口径） | prompt_lint.txt |
| 14 | 图数字质检 | python -I tools/art_qa.py | 0 | 461 张，near_black=0 | art_qa.txt |
| 15 | rewrite 校验 | python -I tools/_check_rw.py | 0 | RW 30 文件全过 | check_rw.txt |
| 16 | lore 校验 | python -I tools/_check_lore.py | 0 | 461 条全过 | check_lore.txt |
| 17 | 文案校验 | python -I tools/_check_copy.py | 0 | card 266+foe 113+evt 82 全过 | check_copy.txt |

## 结论
- 17 项全绿（exit 0），无失败项，「未解决」一节不适用。
- 注：部分 node 脚本的中文输出在 Windows 管道下显示为 GBK 转码乱码，exit 码与判定行均正常，属终端代码页现象、非产品问题。
