## card_03：贴 10 张零引擎改动通用牌

**改哪个文件**：cards/shared.json（追加 10 个卡对象）

**具体怎么改**：按 T341 §二 的 10 个 json 草案逐个追加到 shared.json 的数组末尾。id：u_0003/u_0006/u_0007/u_0008/u_0009/u_0010/u_0011/u_0012/u_0013/u_0016。class 全部 "shared"。

**改完跑什么**：node tools/_t46_wire.js → 无报错。然后 python -c "import json; json.load(open('cards/shared.json',encoding='utf-8'))" → 可解析

**失败了怎么退**：删除追加的 10 个对象，重跑 _t46_wire.js

**这一步做完，游戏会变成**：10 张通用牌四职业可用——商店/事件/奖励三渠道都能刷出
