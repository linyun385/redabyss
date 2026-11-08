## card_10：energy_debt 字段

**改哪个文件**：engine/core.js beginTurn [engine/core.js:258] 附近 + web/index.html 内联副本

**具体怎么改**：在 beginTurn 的能量计算行改为：C.energy = Math.max(0, run.energyMax + (run.energyBonus || 0) - (C.energyPenalty || 0) - (C.energyDebt || 0));。同时在 applySpecial 加 case 'energy_debt': C.energyDebt = (C.energyDebt || 0) + (sp.value || 1); break;（预支的氧打出时立即 +2 能，下一回合 beginTurn 时扣债务）

**改完跑什么**：打通·预支的氧（u_0005），当回合能量 +2、下一回合能量 -1

**失败了怎么退**：删掉 energyDebt 相关代码

**这一步做完，游戏会变成**：能量第一次可以被卡牌操作——共振阈值冲刺和爆发终结有了时序工具
