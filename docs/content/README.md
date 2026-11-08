# 内容总表（脚本生成）

> 由 `tools/export_content_md.py` 从 `cards/`、`enemies/`、`events/`、`relics/` 导出。
> **数据变了要重跑脚本，不要手改这些文件。**

| 文件 | 内容 |
|---|---|
| [cards_anmin.md](cards_anmin.md) | 维护者 · 50 张 |
| [cards_cangmin.md](cards_cangmin.md) | 疯先知 · 50 张 |
| [cards_diver.md](cards_diver.md) | 下潜者 · 83 张 |
| [cards_tremor.md](cards_tremor.md) | 震语者 · 83 张 |
| [enemies.md](enemies.md) | 敌人 · 113 个 |
| [events.md](events.md) | 事件 · 82 个 |
| [relics.md](relics.md) | 遗物 · 77 个 |
| [mechanisms.md](mechanisms.md) | 机制对照 · 22 种 |

## 怎么用

1. 查某张卡 → 打开对应职业的表，`Ctrl+F` 搜 id 或名字
2. 想知道「某个机制被几个职业用」→ 看 mechanisms.md
3. 想改 → **改 json，不要改 md**，改完重跑本脚本

## 名词

术语以 `docs/GLOSSARY.md` 为准。本表里的换算：

| 原值 | 显示为 |
|---|---|
| `attack` | 攻击 |
| `skill` | 技能 |
| `power` | 能力 |
| `common` | 普通 |
| `uncommon` | 罕见 |
| `rare` | 稀有 |
| `special` | 特殊 |
| `boss` | 首领 |
| `light` | 光脉 |
| `water` | 水脉 |
| `heat` | 热脉 |
| `tremor` | 震脉 |
| `mineral` | 矿脉 |
| `none` | 无 |
| `vitality` | 体力 |
| `lock` | 每层一次 |
| `memory` | 记忆 |
| `mark` | 标记 |
| `block` | 格挡 |
| `damage` | 伤害 |
| `draw` | 抽牌 |
| `heal` | 治疗 |
| `resonance_gain` | 共鸣+ |
| `resonance_cost` | 共鸣→ |
| `resonance_drain` | 共鸣流失 |
| `gaze_cost` | 凝视→ |
| `gaze_gain` | 凝视+ |
| `special:regenerate` | 再生 |
| `special:strength` | 力量 |
| `special:dexterity` | 敏捷 |
| `special:burn` | 灼烧 |
| `special:retain` | 保留 |
| `special:resonance_lock` | 共鸣锁定 |
| `special:exhaust` | 消耗 |
| `special:thorns` | 荆棘 |
| `special:weak` | 虚弱 |
| `special:frail` | 脆弱 |
| `special:poison` | 中毒 |
| `special:delete_random` | 随机删牌 |
| `special:gaze_reduce` | 凝视- |
| `self` | 自身 |
| `single` | 单体 |
| `all` | 全体 |
| `random` | 随机 |
| `normal` | 普通 |
| `elite` | 精英 |
| `defend` | 防御 |
| `buff` | 强化 |
| `debuff` | 削弱 |
| `hits` | 段 |
| `amount` | 量 |
| `times` | 次 |
