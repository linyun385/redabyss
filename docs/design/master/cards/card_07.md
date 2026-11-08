## card_07：双脉连携改写

**改哪个文件**：engine/core.js [engine/core.js:429] + web/index.html 内联副本 [index.html:5789]

**具体怎么改**：把 `const primary = vs[0];` 改为遍历 vs 数组、每个脉各计一次连携。具体：把 veinChainBonus 的计数从单键改为多键。

**改完跑什么**：打一张双脉牌（如通·传声钢缆 light+tremor），toast 应显示连携加成（如果这是同回合第二张脉牌）

**失败了怎么退**：恢复为 `const primary = vs[0]`

**这一步做完，游戏会变成**：双脉卡的连携在两个脉各计一次——桥梁层从降级变为完全体
