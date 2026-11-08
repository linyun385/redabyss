## card_09：chain_keep 豁免

**改哪个文件**：engine/core.js [engine/core.js:263] 附近 + web/index.html 内联副本

**具体怎么改**：在 beginTurn 的 veinChain = {} 清零行加条件：if (!C.chainKeep) C.veinChain = {};。同时在 applySpecial 加 case 'chain_keep': C.chainKeep = true; break;

**改完跑什么**：打通·共鸣腔（u_0014），下一回合开始时连携计数不清零（上一回合的最后连携值延续）

**失败了怎么退**：删掉豁免判断和 case

**这一步做完，游戏会变成**：连携从「每回合重置」变成「可跨回合累积」——连携循环流成立
