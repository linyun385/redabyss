# tools/sim · 红渊蒙特卡洛模拟工具集（H 批）

> ★ **边界声明（先读）**：这些脚本**不是真引擎**——是按 `docs/design/` 文档假设搭的近似模型。
> 所有报告结论必须读作「估算」；每份 `docs/design/sim_*.md` 开头都有「假设」「局限」两段。
> 不模拟的东西清单见下文「模型边界」。

## 快速开始

```bash
# 全部重跑（H01-H11 + H14，结果写入 docs/design/sim_*.md）
python tools/sim/run_all.py

# 只跑指定编号
python tools/sim/run_all.py 01 05 14

# 单跑一个
python tools/sim/sim_reward.py
```

所有脚本：**参数在文件顶部**（N/SEED/阈值等，改完重跑即可）；随机一律固定种子（默认 42）；无写死结果。

## 脚本一览

| 脚本 | 产出 | 一次时长 | 随机性 |
|---|---|---|---|
| sim_reward.py | sim_reward.md | ~2s | MC 1000×20 |
| sim_combat.py | sim_combat.md | ~1s | MC 400×8 层 |
| sim_economy.py | sim_economy.md | ~1s | MC 1000 局 |
| sim_build_speed.py | sim_build_speed.md | ~8s | MC 5 脉×1000 |
| sim_sensitivity.py | sim_sensitivity.md | ~3s | MC 8 档×2000 |
| sim_event_value.py | sim_event_value.md | <1s | 确定（无随机） |
| sim_relic_value.py | sim_relic_value.md | <1s | 确定 |
| sim_combo_damage.py | sim_combo_damage.md | <1s | 确定 |
| sim_vein_level.py | sim_vein_level.md | ~1s | MC 5 脉×1000 局 |
| sim_decision_load.py | sim_decision_load.md | ~2s | MC 4 角色×2000 |
| sim_starter_survival.py | sim_starter_survival.md | ~3s | 回合制微模拟 200×4×3 |
| sim_full_run.py | sim_full_run.md | ~3s | MC 200 局全流程 |

## simlib.py —— 公共库

所有脚本 `from simlib import ...`：

| 函数 | 干什么 | 口径来源 |
|---|---|---|
| `load_cards()/load_raw()` | 只读 cards/*.json 与 data/audit/raw_all.json | — |
| `class_pool(cls)` | 角色池+通用池（CLASS_POOL 同款） | web:414314 |
| `reward_weights()/show_three()` | 奖励三选一：稀有度 6/3/1 × 脉权重(1+min(持有,6)×0.25) × 擅长1.3 + 硬保证 | T400 §2.3 |
| `pick_card()` | 拿牌策略（贪心目标脉/随机） | 本批假设 |
| `layer_enemy_pool()/enemy_metrics()` | 敌池与指标（血中值/平均单发/攻击频率） | T440 |
| `simulate_fight()` | 近似战斗：回合=ceil(血/DPS)、承伤=攻击×频率×回合 | D11/T453 口径 |
| `gold_for_fight()/parts_for()` | 金 20-40/场、boss 50-80、零件 1-2/4/10 | web 实测常数 |

**改参数**：全局口径改 `simlib.PARAMS`（能量/DPS/权重/血量表）；单实验参数改各脚本文件顶部的常量（N/SEED/目标数）。**改了数值重跑一次 run_all.py 即可刷新全部报告。**

## 模型边界（所有脚本共享的不模拟清单）

- **不做格挡决策**（H14 用 H11 校准的 0.25 减伤系数近似；H11 本身有贪心格挡微模拟）
- **不做卡牌真结算**：无升级/遗物联动/协议/双世界/共振层反应对战斗的影响
- **不做流牌**：抽牌堆只是统计口径，不模拟手牌构造策略（H11 除外）
- **不做 UI 层**：层主题/事件呈现/多敌同场站位
- 敌人精英/boss 承伤用粗乘数（×1.4/×1.6，H14）

## 已知模型事故（留档防复发）

1. H14 首版：hp 未扣血就拿「累计承伤≥血」判死 → 100% 假死。
2. H14 二版：裸吃口径无格挡 → 100% 死亡失去分辨力 → 引入 H11 校准的减伤 0.25。
3. H10 首版：可行子集指标饱和（31/32）→ 换「有意义子集（花≥3 能量）」。
4. 多次 `%` 格式化字符串与中文 `%` 冲突 → 已全部改写。
教训：**先看指标分布再下结论；口径变了必须改报告的假设段。**

## 与静态分析的关系

静态批（T/D/F）给出口径与事实；本批把口径变成可跑模型。两者结论一致时=互证（如 H02 与 T453、H09 与 T526）；不一致时=以模拟为准并在报告里写明（如 H03 金币 803 vs 静态 550 的支出策略差）。

## K05 补充 · config.py（参数集中化）

所有口径常数已集中到 `tools/sim/config.py`（分节：引擎口径/战斗近似/经济/抽卡权重/层结构/遗物模型/种子/样本数）。`simlib.PARAMS` 从 config 取值；各脚本顶部的实验参数（样本数等）也改为 `from config import …`。**改数值只改 config.py，然后 `python tools/sim/run_all.py` 一次刷新全部报告。** 口径出处注释保留在 config.py 各节。
