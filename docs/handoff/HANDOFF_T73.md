# HANDOFF_T73.md — 会话交接文档（2026-10-31，T72+T73 完成后）

> **给新会话的 opener**：读这份文档 + `game/TASK_DONE.md` 最后 10 条 + `game/docs/MAPGEN_DESIGN.md`，然后你就可以接手了。
> **绝对不要重做的事**：本文档「已完成」列表里的每一项都有 TASK_DONE 记录和检查器通过证据。

## 一、项目当前状态（一句话）

红渊卡牌 roguelike（单文件 `web/index.html` 584KB）已完成 T54–T70 + T72 + T73 全队列。地图系统已从旧的 4 行 48 格升级为 161 节点 14×64 大图（8 深度带 × 2–4 种生态混合），素材 79 张外置到 `web/assets/art/`，三检查器 + mapgen_test + check_bindings + check_ecomix 全绿。

## 二、已完成任务清单（不要重做！）

| 任务 | 状态 | 产出位置 |
|---|---|---|
| T54 设计文档 | ✅ | docs/MAPGEN_DESIGN.md（含 I1–I17 不变量） |
| T55 生成器 | ✅ | tools/mapgen.js（↑已内联进 index.html）+ mapgen_test.js（200 seed）+ mapgen_debug.html |
| T56 小图/总图 | ✅ | web/index.html T56-MAP-MODULE 段（默认新地图；?map=old 回退） |
| T57 玩法接入 | ✅ | 推进/死路救援/跨带 BOSS/结局，全在 T56-MAP-MODULE 段 |
| T60 配额盘点 | ✅ | tools/content_gap.js + content_gap.json + docs/CONTENT_PLAN.md |
| T58 绑定表 | ✅ | data/mapgen_bindings.json + tools/check_bindings.js（256/256 满格） |
| T59 回归 | ✅ | tools/mapgen_sim.js + docs/MAPGEN_REPORT.md |
| T61 敌人 | ✅ | enemies/all.json +33（eco 标签）+ docs/ECO_ENEMIES.md |
| T62 事件 | ✅ | events/all.json +10（eco+bands 标签）+ docs/ECO_EVENTS.md |
| T63 遗物卡牌 | ✅ | relics/all.json +1 / cards +6 + docs/ECO_RELIC_CARD.md |
| T64 文风 | ✅ | tools/text_lint.js + docs/GLOSSARY.md |
| T65 内容收口 | ✅ | docs/CONTENT_REGRESSION.md |
| T66 素材管线 | ✅ | tools/art_manifest.json(79 条) + gen_art_batch.py + art_similarity.py + art/ 79 张 |
| T67 素材接入 | ✅ | check_web.js 规则修订（允许 data:+站内相对路径）+ ART 表（现为路径版）+ ART_DELIVERY.md |
| T69 素材补齐 | ✅ | art/ 79/79、闸门 0/79 命中、外置到 web/assets/art/ |
| T70 终局回归 | ✅ | docs/FINAL_REGRESSION.md + 截图 6 张 |
| T72 生态混合 | ✅ | spec v1.5 + mapgen.js 权重/调制/后处理 + tools/check_ecomix.js |
| T73 节奏重做 | ✅ | spec v1.6 + mapgen.js 配额 161/64 行/纵向间距/浅降优先/槽位抢救 + 8 张分布图 |

## 三、双份文件同步（最容易踩的坑！）

**`tools/mapgen.js` 和 `web/index.html` 内的 `/* ==MAPGEN-LIB== */` 块是两份副本。**

**任何对 tools/mapgen.js 的修改，必须重跑 `node tools/_t56_wire.js` 同步进 index.html！**

这个脚本还同步 MAPGEN-BINDINGS（T58 的绑定表 data URI 版）。漏跑的后果：游戏跑旧生成器，用户会发现（T72 就踩过）。

同理：**改 tools/mapgen_spec.json 后必须重跑 `node tools/mapgen_test.js`**（同步断言在里面）。

**改 tools/art_manifest.json 或 art/ 后必须跑 `python tools/art_sync.py` + `node tools/_t56_wire.js`**（同步素材到 web/assets/art/ + 刷新 ART 路径表）。

## 四、检查器全套（每次改动后全跑）

```bash
node tools/pack_check.js all       # 5 个警告（扩充通道，正常）
node tools/test_engine.js          # 全部通过
node tools/check_web.js            # 0 个警告
node tools/check_bindings.js       # 256/256 满格
node tools/mapgen_test.js          # 200/200 ✓
node tools/check_ecomix.js --runs 100  # T72 验收全过（快速跑 100 张够用）
```

全套通过 = 绿灯。任何一个红 → 查 TASK_DONE 对应条目的边界声明。

## 五、架构要点（谁改了什么，2026-10-31 用户亲手改的）

| 改动者 | 内容 |
|---|---|
| **用户** | 素材外置（web/assets/art/，79 张）、ART 表从 base64 改相对路径、check_web 规则改（允许 data:+站内路径，禁 http 外链）、build_pack.py 打包工具 |
| **GLM (T54-T73)** | mapgen.js / mapgen_spec.json / mapgen_test.js / check_ecomix.js / mapgen_sim.js / 各文档 / web/index.html T56-MAP-MODULE 段 |

**不要再把图 base64 内联进 HTML。** 素材在 `web/assets/art/`，ART 表存相对路径。

## 六、关键文件与路径

| 文件 | 说明 |
|---|---|
| `web/index.html` | 游戏本体（584KB）。内含 7 个 `<script>` 块：MAPGEN-BINDINGS / ART-TABLE / MAPGEN-LIB / 引擎 / RAW / 数据适配 / T56-MAP-MODULE |
| `tools/mapgen.js` | 生成器源码（修改后重跑 _t56_wire.js） |
| `tools/mapgen_spec.json` | 参数唯一来源 v1.6 |
| `tools/art_manifest.json` | 素材清单 79 条 |
| `data/mapgen_bindings.json` | T58 绑定表（生态×带→内容池） |
| `web/assets/art/` | 79 张 webp（用户外置的架构） |
| `enemies/all.json` | 113 只（含 T61 新增 33 只带 eco 标签） |
| `events/all.json` | 82 条（含 T62 新增 10 条带 eco+bands 标签） |
| `relics/all.json` | 77 件（含 T63 新增 relic_77） |
| `cards/*.json` | 266 张（含 T63 新增 6 张素卡） |

## 七、遗留问题清单（只记录不修，FINAL_REGRESSION §8 同步）

1. 生图速度 ~5-9 分钟/张（VAE fp32 upcast 疑因）
2. 敌图 3 张/生态按 id 哈希共享（非每怪专属）
3. B 语言偶发细边框
4. A 语言罗马数字不稳定
5. UI 视觉（用户自评「太丑」，等参考图）
6. T47 卡池结构问题 12 项
7. mapgen 自然死路率 0（救援功能触发少）
8. 步数 32.3 < 40 目标（DAG 深度限制，需加大网格或改走图算法）

## 八、打包

- `python tools/build_pack.py` → dist/redabyss-*.zip（2.3MB）
- `python tools/build_pack.py --inline` → 单文件版（3.1MB，备用）

## 九、给新会话的开场白

```
你是红渊项目的接手者。项目根目录 C:\Users\Administrator\Desktop\杂七杂八\红渊\game。

先读 docs/HANDOFF_T73.md（交接文档）和 TASK_DONE.md 最后 10 条，了解当前状态。
然后读 tasks/ 目录看有没有新任务。

关键约束：
- 不改 engine/core.js 的战斗结算
- 不修 ComfyUI
- 不许为过关放宽检查器
- 改 tools/mapgen.js 后必须重跑 node tools/_t56_wire.js
- 改 tools/mapgen_spec.json 后必须重跑 node tools/mapgen_test.js
- 素材外置（web/assets/art/），不要 base64 内联

检查器全套（每次改动后全跑）：
node tools/pack_check.js all
node tools/test_engine.js
node tools/check_web.js
node tools/check_bindings.js
node tools/mapgen_test.js
node tools/check_ecomix.js --runs 100
```
