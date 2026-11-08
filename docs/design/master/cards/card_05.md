## card_05：加 2 条新手引导

**改哪个文件**：web/index.html（两处）

**具体怎么改**：① 在 doPlay 的 r.chain > 0 分支（[index.html:6987] 附近）加：onceHint('chain', '同一脉连着打，第二张起有加成')
② 在 playBlockReason 的凝视分支（[index.html:7589] 附近）加：onceHint('gaze_cost', '凝视不扣，它只看够不够')

**改完跑什么**：新游戏进战斗，第一次连携和第一次凝视不足时各弹出一条提示（且只弹一次）

**失败了怎么退**：删掉两行 onceHint 调用

**这一步做完，游戏会变成**：新手在第一次撞上连携/凝视规则时获得引导
