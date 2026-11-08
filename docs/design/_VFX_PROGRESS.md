# 战斗动效 · 进度（2026-11-06）

## 已完成

| 批 | 内容 | 状态 |
|---|---|---|
| 0 | 引擎补「锁死状态」 | **取消** —— 已存在（`card._locked`） |
| 1 | 特效层骨架 + 坐标快照 + 强度档 | ✅ 完成 |
| 4（部分） | 伤害 → 血痕 接入 | ✅ 完成 |

## 落地的东西

### 新增文件

| 文件 | 大小 | 说明 |
|---|---|---|
| `web/fx.css` | ~9KB | 14 个 keyframes：血痕/飘字/震动/碎片/击杀/8 状态 |
| `web/fx.js` | ~10KB | `window.FX`，9 个 API，MVVM 无关、静默失败 |

### index.html 改动（净 +436 字节）

| 位置 | 改动 |
|---|---|
| `</style>` 之后 | `<link rel="stylesheet" href="fx.css">` |
| `<body>` 之后 | `<div id="fx-layer" aria-hidden="true"></div>` |
| 最后 `</script>` 之后 | `<script src="fx.js"></script>` |
| `applyCardEffect` 开头 | 记下本次出牌主脉 → `C._fxVeins` |
| `render()` 敌人循环 | 掉血检测 → `FX.damage(box, dmg, C._fxVeins)`（try/catch 包住）|

**没有改的**：`dealToEnemy`、伤害计算、任何游戏逻辑。特效完全旁挂。

### 备份

`web/index.html.bak-20261106-1220-prefx`（改动前）

## 已验证

| 检查 | 结果 |
|---|---|
| `node --check web/fx.js` | 通过 |
| `fx.css` 大括号平衡 | 93 / 93 |
| `check_web.js` | 0 警告，7 个内联 script 全部可解析 |
| 三处引入都只有一次 | ✅ |
| `FX.damage` 全项目只一处调用 | ✅ |
| `prev.hps` 两处赋值仍在（startCombatFlow + render）| ✅ |

## 没验证的

**动效在真实页面里的观感。** 静态检查全绿，但「血痕好不好看、会不会烦」只能眼看。

手动验收步骤：打开游戏 → 进战斗 → 打一张攻击牌 → 目标身上应出现一道斜向划痕 + 红数字 + 短促震动。
控制台可看 `FX._debug()` 确认 `{live, max:6, layer:true, intensity:'mid'}`。

## 待做

| 项 | 谁 |
|---|---|
| 批 2/3：GLM 的完整版 CSS/JS（今晚 23:00 派）| GLM |
| 批 4 剩余：格挡碎裂、治疗、击杀、状态特连接入 | 我 |
| 批 5：锁死红叉（`FX.lockCard` 已写好，只差在 `renderCardStatic` 里调用）| 我 |
| 批 6：7 张核心卡专属特效 | 我 |
| 批 7：性能与体感调参 | 我 |

## 一个待验证的疑点（不阻塞动效）

`card._locked` 全程只出现 3 次，**没有看到重置逻辑**。`startCombat` 里 `drawPile` 是新建的空数组，
但卡片对象是深拷贝还是引用 `run.deck` 没查到底。

- 若是**深拷贝** → 没问题
- 若是**引用** → 锁死会跨战斗残留，是真 bug（玩家会看到上一场锁死的牌这一场还是锁的）

验证法：打一张锁死卡 → 结束该战斗 → 进下一场 → 看那张牌是否仍被锁。
