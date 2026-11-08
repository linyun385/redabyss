## card_08：clear_debuffs 分支

**改哪个文件**：engine/core.js [engine/core.js:655] 附近 + web/index.html 内联副本 [index.html:6017] 附近

**具体怎么改**：在 endTurn 的敌人状态结算之后、玩家 debuff tick 的位置加一个 case：当 special code 为 clear_debuffs 时清空 C.debuffs = {}。实际实现：在 applyCardEffect 里加 if (e.clear_debuffs) C.debuffs = {};

**改完跑什么**：打通·减压舱（u_0017），身上的 weak/poison/burn 全部清除

**失败了怎么退**：删掉新增的一行

**这一步做完，游戏会变成**：玩家第一次有了主动解 debuff 的手段
