## card_02：删 58 张卡

**改哪个文件**：cards/diver.json（26处）、cards/tremor.json（26处）、cards/anmin.json（3处）、cards/cangmin.json（3处）

**具体怎么改**：按 T340_DELETE_OPS.md 的逐条清单，整条删除每个卡对象（从 `"id": "dive_0009"` 到闭合花括号）。同文件内一次改完。

**改完跑什么**：python -c "import json; [json.load(open(f,encoding='utf-8')) for f in ['cards/diver.json','cards/tremor.json','cards/anmin.json','cards/cangmin.json']]" → 四个 json 可解析。数量核对：diver 57 / tremor 57 / anmin 47 / cangmin 47

**失败了怎么退**：用 .bak-20261104 覆盖回去

**这一步做完，游戏会变成**：卡池 267→209，冗余卡消除，T332 矩阵 10 条流派评级全部保持（R2_D3 已验证）
