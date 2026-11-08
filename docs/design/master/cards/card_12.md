## card_12：discard 分支

**改哪个文件**：engine/core.js applyCardEffect [engine/core.js:445] 附近 + web/index.html 内联副本

**具体怎么改**：在 applyCardEffect 的抽牌段（[engine/core.js:476] 附近）之后加：if (e.discard) { 让玩家选择弃 e.discard 张手牌 }。实际实现需要前端配合（手牌选择 UI），引擎侧只标记 e.discard 值。

**改完跑什么**：打通·空的手（u_0001），选择弃 1 张再抽 2 张

**失败了怎么退**：删掉 discard 相关代码

**这一步做完，游戏会变成**：手牌过滤第一次成为可能——起手烂牌有了主动出口
