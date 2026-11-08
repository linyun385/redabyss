## card_11：keep_block_half 特效

**改哪个文件**：engine/core.js endTurn [engine/core.js:682] 附近 + web/index.html 内联副本

**具体怎么改**：在 endTurn 的格挡清零段（keepBlock 遗物检查之后）加一个卡牌标记检查：如果 C.hand 或 C.effects 中有 keep_block_half 标记，则 C.block = Math.floor(C.block / 2) 而非 C.block = 0。具体实现路径取决于 keep_block_half 是写在卡牌 effect 还是 C.buffs——建议写在 C.buffs（与 regen 同级）

**改完跑什么**：打通·守夜人的钟（u_0002），回合结束格挡不清零而是减半

**失败了怎么退**：删掉新增的检查分支

**这一步做完，游戏会变成**：格挡从「每回合重建」变成「可累积」——格挡墙流的核心升级
