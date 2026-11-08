# RULE_COVERAGE · 规则 VIII/IX/X 覆盖率（T270）

## 结论（5 行）

1. 规则 VIII（去物种）覆盖率 **99.6%**：461 条主体段仅 2 条残留（dive_0022 苔藓、event 一条 蕨），且都在 rewrite 清单内——**已实质完成**。
2. 规则 IX（去电器）覆盖率 **83.5%**：76 条残留、92 次词项命中，「灯」占 53——其中 38 条在 rewrite 清单内被改过仍残留，38 条从未重写（anm/cng 为主）。
3. 规则 X/§六（机械禁词：装置/编号/字/标签…）覆盖率 **80.9%**：88 条残留 117 次，anm 一族占 35 条——**维护者/疯先知两池从未进入 rewrite 流程**。
4. 分池合规率断层明显：trem 85.5% / dive 78.3% / enemy 89.4% / event 74.4% 对 anm 28.0% / cng 32.0%——残留不是随机分布，是**rewrite 只跑了 dive/trem/event** 的执行缺口。
5. 裁决建议：anm/cng 的「灯/按钮/编号」命中属世界观本体（维护者叙事即电器与规程），是否豁免需人工拍板；若不豁免，剩余工作 = 未覆盖 105 条（appliance 38 + mech 67）的主体段重写。

## 可复算

```powershell
python tools/prompt_lint.py                                          # 主体段口径 -> data/lint.json
python tools/prompt_lint.py --full --out data/lint_full_prompts.json # 整条口径（见口径注记）
python tools/rule_coverage.py                                        # 汇总表 -> data/rule_coverage.json
```

`rule_coverage.py` 无时间戳无随机，同输入两次运行逐字节一致（2026-11-04 已验证 diff 为空）。词表来源与键名沿用 `tools/prompt_lint.py`（species=SPEC§VIII / appliance=规则IX / mech=SPEC§六禁词 / en_bad=§四英文禁词，见 docs/ART_PIPELINE.md「prompt_lint 词表」节）。

## 按规则

| 规则 | 词项命中 | 命中条数 | 覆盖率（0 命中占比） | rewrite 清单覆盖 | 未覆盖样本 |
|---|---|---|---|---|---|
| VIII 去物种 | 2 | 2 | 99.6% | 2/2 | 0 |
| IX 去电器 | 92 | 76 | 83.5% | 38/76 | 38（anm/cng 为主） |
| X/§六 机械禁词 | 117 | 88 | 80.9% | 21/88 | 67（anm 35 条居首） |
| §四英文禁词 | 0 | 0 | 100.0% | 0/0 | 0 |

IX 残留词分布：灯 53、显示 15、屏 9、按钮 6、表盘 3、喇叭 2、电线 2。X/§六 残留词分布：字 38、编号 34、标签 13、装置 10、刻度 5、仪表 4、开关 3、仪器 3。

## 按池

| 池 | 总量 | 命中条数 | 覆盖率 | species | appliance | mech |
|---|---|---|---|---|---|---|
| anm（维护者） | 50 | 36 | 28.0% | 0 | 10 | 35 |
| cng（疯先知） | 50 | 34 | 32.0% | 0 | 19 | 23 |
| dive（下潜者） | 83 | 18 | 78.3% | 1 | 17 | 5 |
| trem（震语者） | 83 | 12 | 85.5% | 0 | 10 | 4 |
| enemy | 113 | 12 | 89.4% | 0 | 9 | 9 |
| event | 82 | 21 | 74.4% | 1 | 11 | 12 |

（每池两列词项数为「命中该规则的卡条数」；与按规则表的「条数」口径一致，与「词项命中次数」不同。）

## 口径注记（三条，防止误读）

1. **覆盖率按主体段**（「洞底是一整片深红的光」前半，prompt_lint 的缺省口径）——这是 rewrite 的作业范围。整条口径下 mech 会 100% 命中，因为固定尾部工艺段含「字」（对应英文负面词 no text），那是风格段本身，不算违规（[tools/prompt_lint.py:25] 的 MARKER 切分逻辑）。
2. **规则名映射**：任务书说的 X（事件「牌/文字/纸类/设备」重写，[docs/ART_PROMPT_SPEC.md:200] 的执行记录）在词表体系里落在 `mech` 键；`appliance` 是第一轮翻车源新增的 IX 词表；两者是不同词表，本表分开统计。
3. **rewrite 清单**（147 条，data/rewrite/_targets.json）当时只覆盖 dive/trem/event 的目标段；anm/cng/foe 从未进入——这是第 4 条结论「执行缺口」的出处，不是 lint 或重写的失败。

## 与既有基线的关系

docs/ART_PIPELINE.md「夜班基线数字」记 lint 主体段命中 133（rewrite 前口径）；本次用当前 `data/zh_prompts_full.json` 重跑 lint 仍为 133 条/24 词项——即**现有残留与重写前的记录完全同集**：rewrite 确实消除了它目标内的词（dive/trem/event 的 appliance 残留均为改写文本中新出现或遗留的非目标词），而 anm/cng/foe 段从未被处理。换句话说：当前 133 条残留 = 105 条从未重写（anm 36 + cng 34 + enemy 12 + 与清单相交部分）+ 28 条重写后仍带非目标词的存量，处理顺序应先做前者。
