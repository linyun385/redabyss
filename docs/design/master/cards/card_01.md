## card_01：备份四份 cards/*.json

**改哪个文件**：cards/diver.json, cards/tremor.json, cards/anmin.json, cards/cangmin.json

**具体怎么改**：复制四份文件为 *.bak-20261104（同目录）

**改完跑什么**：ls cards/*.bak-20261104 → 四个文件存在

**失败了怎么退**：删除 .bak 文件（如果不需要回滚）

**这一步做完，游戏会变成**：有回滚保险，后续所有步骤可安全执行
