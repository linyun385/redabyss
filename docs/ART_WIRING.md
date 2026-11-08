# 定稿图接线记录（2026-11-03）

> 定稿 → 导入 → 接线，三步。任何一步都能单独回滚。

## 一、定稿

`data/picks.json` 461 条全部已选已复核。

| 项 | 值 |
|---|---|
| 条目 | 461 |
| 替换（非 v0） | 258 |
| 保持原图 | 203 |
| 版本分布 | v0=203 · v1=131 · v2=117 · v3=9 · v7=1 |

清单：`docs/FINAL_MANIFEST.md`（人看）、`data/final_manifest.json`（机器用，含 sha256）

## 二、导入

```powershell
python tools/finalize_art.py           # 演练，只生成清单
python tools/finalize_art.py --apply   # 备份 + 复制
```

备份：`art/_backup/art_<时间戳>`（整目录 607 个文件）
回滚：`python tools/finalize_art.py --rollback art_20261103_164305`

## 三、接线（改了 web/index.html）

接线前的事实：`window.ART` 只有 **79 条**（face 48 / foe 24 / class 4 / end 3），
**461 个素材一个都没收录**。游戏当时只用少量通用图：

| 用途 | 原逻辑 | 位置 |
|---|---|---|
| 卡面 | `face_` + 生态 + 哈希取 1/6 | `cardArtId()` |
| 敌人 | `foe_` + 生态 + 哈希取 1/3 | 战斗渲染 |
| 选人立绘 | `class_` + 职业 | 选人界面 |
| 结局 | `end_ending_` + 结局 | 结局页 |

### 三处改动

1. **`window.ART` 从 79 条补到 540 条** —— 加了 461 条 `id → assets/art/<id>.webp`
2. **`cardArtId()` 开头加一行**：`if (card && card.id && ART[card.id]) return card.id;`
   —— 专属图优先，查不到自动走原逻辑
3. **敌人渲染的 `fid` 改一处**：
   `(e.def.id && ART[e.def.id]) ? e.def.id : ('foe_' + ecoHome + '_' + (1 + h % 3))`
   —— 同样先查专属图，回落生态图

**关键设计：两处都是「优先查、查不到回落」，不是「替换」。** 任何一张图缺失都不会白屏。

### 验证（实测）

起 `python -m http.server 8090`（在 `web/` 里），浏览器实测：

- 选人界面四张职业立绘正常
- 战斗界面：沉屑鱼、冷洞食腐鳗各自显示独立的敌人图
- 手牌：死亡合同、一击、缩起、锚桩，每张都有专属图案
- 无控制台错误

### 回滚接线

```powershell
Copy-Item web\index.html.bak_wire web\index.html -Force
```

（接线前的 index.html 备份在 `web/index.html.bak_wire`）

## 四、遗留

| 项 | 状态 |
|---|---|
| 事件图（`event_d1_1` 等 82 张） | **未验证**。事件是否走 `appendArt` 没确认，可能仍是生态图 |
| 敌人图比例 | 原生态图是 `cover` 裁切，专属图也是 1:1，应该没问题，但没逐一比对 |
| 局内缓存 | 图换了要硬刷新（Ctrl+F5），否则浏览器可能用旧图 |

## 五、效果不好怎么换单张

1. 在挑选台 `http://127.0.0.1:8770` 搜那张，重新选一个版本
2. `python tools/finalize_art.py --apply`（重跑会重新备份、只覆盖非 v0 的）
3. 浏览器硬刷新

因为导入是从 `picks.json` 读的，**可以重复执行**，不会累积错误。
