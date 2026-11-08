# J01 · 模拟器 bug 家族全面排查

> 方法：逐行审 `tools/sim/simlib.py`（117 行）与 14 个脚本，按四类模式找：① 算而不用 ② 键错位 ③ 丢弃中间结果 ④ 权重算出未读。
> 每处给：文件+行号 / 类别 / 影响哪个结论 / 状态（已修/未修/误诊）。
> **本篇最重要的产出是第 3 节：对 06 批「键错位」误诊的更正。**

## 一、真 bug 家族（2 个，均已修）

| # | bug | 位置（修复前） | 类别 | 影响的结论 | 状态 |
|---|---|---|---|---|---|
| B1 | **show_three 权重未接入采样**：`reward_weights` 算出 `ws` 后，采样用 `rng.randrange(len(pool))` 均匀抽取——权重从未被读 | simlib.py（06 批修复前 line 81） | ④ 权重算出未读（=①算而不用的子类） | H01 主脉率（41.1%→45.9%）、I01 全部扫描档位、H04/H14 的抽样分布 | **已修**（06 批，改为 `rng.choices(pool_idx, weights=w)` 无放回加权） |
| B2 | **pick_card 丢弃分数**：scored 排序后 `return shown[0]`——永远拿第一张展示牌，目标脉策略从未执行 | simlib.py（06 批修复前 line 107） | ③ 丢弃中间结果 | H04 成型速度（水 60 场→全脉 5 场）、H14 拿牌序列、H01 的 owned 增长路径 | **已修**（06 批，`return shown[scored[0][2]]`） |

## 二、误诊更正（记录错误的诊断，防止它被继续引用）

| # | 当时的诊断 | 实际情况 | 为什么误诊 | 状态 |
|---|---|---|---|---|
| P1 | **「owned 字典中文键 vs 卡 veins 英文键」**（06 批更正条 1） | `CN_VEIN = {'light': '光', ...}` **键本来就是英文**——`{v: 0 for v in CN_VEIN}` 迭代出来一直是英文键，与卡 veins 键位一致 | 修复扫描时只看了值的语言（'光'），没验证键的语言；后续「修复后数字相同」本应触发怀疑，却按「巧合」放行 | **误诊已撤**（J01 本节；TASK_DONE 06 批更正条与本篇互为勘误） |
| P2 | 连带：H14「本文件漏网键错位」（I01 时段补修） | 同上——键从来没错；修的是注释不是行为 | 同 P1 | **已澄清**（sim_full_run.py 注释已改写为中性说明） |

**教训（写进 sim/README 事故栏）**：改「键」类 bug 前先跑一行断言 `list(d.keys())[:2]`——两个键位体系的错位用眼睛盯值是盯不出来的。

## 三、J01 新发现（同类模式的其他实例，全部当场清理）

| # | 位置 | 类别 | 内容 | 影响 | 状态 |
|---|---|---|---|---|---|
| N1 | simlib.py `combat_rounds()` | ① 算而不用（死代码） | 定义了「hp/DPS」函数，无任何调用点（各脚本都自己算） | 无（死代码） | **已删** |
| N2 | simlib.py `PARAMS['N_FIGHTS_PER_LAYER']` | ① 算而不用（死参数） | 每层场数参数无人读——sim_economy/sim_full_run 各自定义本地副本 | 无（但两份副本存在口径漂移风险） | **已删参数**（本地副本保留并注明来源） |
| N3 | sim_full_run.py `elite_frac` | ① 算而不用（死变量） | 计算后从未使用 | 无 | **已删** |
| N4 | sim_build_speed.py `show_three(rng, pool, {vein: owned}, …)` | ④ 变体：owned 状态未喂给权重喂了——但 | 修复前权重本身死（B1）；修复后 owned 正确进入权重 | 无（修复后 5 场由硬保证决定，权重不改变中位） | **确认无恙**（重跑 5 场不变） |
| N5 | sim_starter_survival.py 0 费抽牌卡 | ① 算而不用（策略近似） | 死亡合同副本等 0 费抽牌从手牌移除但**不模拟抽牌效果**——手牌恒 5 | H11 的回合数略保守（少抽的牌没算） | **保留为已声明近似**（局限段注明） |
| N6 | sim_starter_survival.py 出牌排序 | 策略选择（非 bug） | 攻击回合「弱伤先出」排序——能量打满时总伤相同，能量不够时次优 | H11 轻微低估输出 | **保留**（局限段已声明贪心策略） |
| N7 | sim_full_run.py boss 条件式 | 可读性 | `('boss' if L == 4 and False else 'elite')` 死表达式 | 无 | **已简化** |

## 四、逐脚本排查结论（14+2 个文件全过一遍）

| 文件 | 排查结果 |
|---|---|
| simlib.py | B1 已修；N1/N2 已清；其余（load/class_pool/reward_weights/enemy_metrics/simulate_fight/gold_for_fight/parts_for）逻辑与用途一致 |
| sim_reward.py / sim_reward_sweep.py | 键英文 ✅、权重生效（B1 修复后实测 41.1%→45.9%/49.8% 变化证明通路打开）、PARAMS 还原 ✅ |
| sim_combat.py | 只用 simulate_fight/layer_enemy_pool——不受 B1/B2 影响 ✅ |
| sim_economy.py | 不碰抽卡——不受影响 ✅；ELITES_PER_LAYER 本地副本与 T507 一致 |
| sim_build_speed.py | N4 确认无恙 |
| sim_sensitivity.py | 内联复刻敌人指标（与 simlib 重复——口径漂移风险，建议未来改 import；本轮不动） |
| sim_event_value.py / sim_relic_value.py / relic_triage.py / sim_combo_damage.py | 确定模型，无采样——不受 B1/B2 影响 ✅ |
| sim_vein_level.py | 自有走层逻辑，不碰 show_three ✅ |
| sim_decision_load.py | 自有权重抽样（rng.choices 用了 weights ✅） |
| sim_starter_survival.py | N5/N6 保留为已声明近似 |
| sim_full_run.py | N3/N7 已清；键澄清（P1/P2）；修复后重跑数字与澄清前一致（125/75——因为「键修复」本来就是无操作） |

## 五、受污染结论的最终清单（与 J02 重算互证）

- **曾被污染**：H01 主脉率（B1+B2）、H04 成型速度（B2）、H14 拿牌序列（B1+B2——但结论结构稳定）、I01 扫描全部档位（B1）。
- **从未被污染**：H02/H03/H05/H06/H07/H08/H09/H10/H11（不使用 show_three/pick_card，或为确定模型）——这份「干净名单」是 J03 置信度分级的直接输入。

## 复算

排查为人工逐行（本篇）；清理后的行为验证：`python tools/sim/run_all.py`（全绿）+ `python tools/sim/sim_build_speed.py`（5 场不变）。
