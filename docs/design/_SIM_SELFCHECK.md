# I03 · 模拟脚本自检（可复现性 / 硬编码 / 除零）

> 方法：① `run_all.py` 连跑两次，原始输出落盘 `data/sim/run1.txt` / `run2.txt` 供复核；② grep 静态扫描硬编码路径与除零模式；③ 逐脚本核对种子使用。所有结论标「估算」口径同前。

## 一、双跑一致性（逐脚本）

剥离计时行（`0.0s/0.1s` 来自 run_all 的耗时打印，与模拟无关）后，**两次输出逐行一致**：

| 脚本 | 双跑一致 | 种子 | 说明 |
|---|---|---|---|
| sim_reward | ✅ 一致 | seed=42 | MC 1000×20 |
| sim_combat | ✅ 一致 | seed=42 | MC 400×8 |
| sim_economy | ✅ 一致 | seed=42 | MC 1000 局 |
| sim_build_speed | ✅ 一致 | seed=42 | MC 5×1000 |
| sim_sensitivity | ✅ 一致 | seed=42 | MC 8 档×2000 |
| sim_event_value | ✅ 一致 | 无随机 | 确定模型 |
| sim_relic_value | ✅ 一致 | 无随机 | 确定模型 |
| sim_combo_damage | ✅ 一致 | 无随机 | 确定 |
| sim_vein_level | ✅ 一致 | seed=42 | MC 5×1000 局 |
| sim_decision_load | ✅ 一致 | seed=42 | MC 4×2000 |
| sim_starter_survival | ✅ 一致 | seed=42 | 微模拟 200×4×3 |
| sim_full_run | ✅ 一致 | seed=42 | MC 200 局 |
| run_all 差异原文 | 仅 1 行 | — | `44c44: 0.0s → 0.1s`（计时） |

**结论：固定种子成立，全部结果可复现。** 原始输出已落盘（见上）供人工复核。

## 二、硬编码路径扫描

- `grep "C:\\\|D:\\\"` tools/sim/*.py → **0 处**：无绝对路径，全部经 `simlib.GAME`（`Path(__file__).parents[2]`）相对定位。
- 迁移安全：整个 `game/` 目录换盘/换机可直接跑。

## 三、除零风险点（逐个核对，全部有守卫）

| 位置 | 表达式 | 守卫 |
|---|---|---|
| simlib.enemy_metrics | `len(atks)/len(its)` | `if its else 0` ✅ |
| sim_reward / sweep | `hits/shown_n` | shown_n≥60 恒成立（20 场×3）✅ |
| sim_relic_value / triage | `worth/price` | price 恒 140/285 ✅ |
| sim_full_run | `ELITE_ROWS[L]/max(1,…)` | max 守卫 ✅ |
| sim_decision_load | `spent` 累加 | 无除法 ✅ |
| sim_economy | `q(v,p)` | 索引 int 截断 ✅ |

**结论：未发现可触发除零的路径。**

## 四、种子使用核对

- 有 MC 的 10 个脚本全部 `random.Random(42)` 显式实例化（grep `Random(` 计 10 处）；3 个确定模型（event_value/relic_value/combo_damage）无随机。
- 一个口径提醒：`run_all.py` 顺序执行导致各脚本**共享同一 seed 起点**——若未来给某脚本改 seed，注意报告里的 seed 声明要同步。

## 五、两条遗留提醒（不是 bug）

1. `sim_reward_sweep.py` 的 monkey-patch 只改 `PARAMS` 数值、不还原函数行为——若未来 simlib 把参数闭包进函数内，patch 会失效（已在 sweep 注释里声明）。
2. 全部脚本的「估算」性质不变：模型口径见 `tools/sim/README.md` 边界声明与 `_SIM_REPORT.md` 共同局限。

## 复算

```bash
python tools/sim/run_all.py > data/sim/run1.txt 2>&1
python tools/sim/run_all.py > data/sim/run2.txt 2>&1
diff <(grep -v "s$" data/sim/run1.txt) <(grep -v "s$" data/sim/run2.txt)   # 剥计时行后应零差异
```
