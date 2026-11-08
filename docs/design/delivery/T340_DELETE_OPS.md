# T340 · 删卡施工单（58 条逐条可执行）

> 数据源：docs/design/stream/T335_PRUNE.csv（58 行）。影响面为本夜全仓 grep 实测：范围 cards/*.json、tools/*.js、tools/*.json、engine/*.js、web/index.html、data/*.json、layers|relics|events|enemies/*.json、glossary.json、DESIGN.md。
> 铁律：本单只写不改；执行人改完 cards/*.json 后**必须**跑 node tools/_t46_wire.js 重建 web/index.html 的 RAW 行（[tools/_t46_wire.js:18]）。

## 〇、执行顺序表

| 步 | 动作 | 之后跑什么 | 通过标准 |
|---|---|---|---|
| 0 | 备份四份 cards/*.json（复制为 *.bak-20261104） | — | 四个 .bak 存在 |
| 1 | 按 §一~§四 逐文件整条删除（同文件一次改完） | python 解析四个 json | 四个 json 可解析 |
| 2 | 数量核对 | 打印各文件 len | diver 57 / tremor 57 / anmin 47 / cangmin 47 |
| 3 | 重建 web 内联数据 | node tools/_t46_wire.js | 无报错；58 个 id 在 web/index.html 命中 0 |
| 4 | 模拟器回归（sim.js 运行时 require cards，自动同步） | node tools/sim.js --class diver --runs 200 等 4 条 | exit 0；通关率与 docs/BALANCE_T29.md 同量级（2-5%） |
| 5 | 验收脚本 | python tools/check_design_refs.py --dir docs/design 与 --dir docs/design/stream | 5/5 与 6/6 |
| 6 | web 体检 | node tools/check_web.js | 0 警告 |

## 一、cards/diver.json（26 条，整条删除）

| 卡 id | 名称 | 删除方式 | cards 外影响面（grep 实测） | 连带操作 |
|---|---|---|---|---|
| dive_0009 | 聚能枪（双管） | 整条删除 | web/index.html（RAW 行，步 3 重建即清）；美术登记簿孤儿化无害（见 §四.5） | RAW 重建；无 |
| dive_0010 | 聚变鱼雷 | 整条删除 | web/index.html（RAW 行，步 3 重建即清）；美术登记簿孤儿化无害（见 §四.5） | RAW 重建；无 |
| dive_0021 | 星髓矿业·定向爆破 | 整条删除 | web/index.html（RAW 行，步 3 重建即清）；美术登记簿孤儿化无害（见 §四.5） | RAW 重建；无 |
| dive_0027 | 星髓矿业·钻杆 | 整条删除 | web/index.html（RAW 行，步 3 重建即清）；美术登记簿孤儿化无害（见 §四.5） | RAW 重建；无 |
| dive_0031 | 聚能枪（过热） | 整条删除 | web/index.html（RAW 行，步 3 重建即清）；美术登记簿孤儿化无害（见 §四.5） | RAW 重建；无 |
| dive_0036 | 红渊贸易局·净水配给 | 整条删除 | web/index.html（RAW 行，步 3 重建即清）；美术登记簿孤儿化无害（见 §四.5） | RAW 重建；无 |
| dive_0040 | 重力训练舱 | 整条删除 | web/index.html（RAW 行，步 3 重建即清）；美术登记簿孤儿化无害（见 §四.5） | RAW 重建；无 |
| dive_0041 | 震频器（并联） | 整条删除 | web/index.html（RAW 行，步 3 重建即清）；美术登记簿孤儿化无害（见 §四.5） | RAW 重建；无 |
| dive_0043 | 曜元（共振型） | 整条删除 | web/index.html（RAW 行，步 3 重建即清）；美术登记簿孤儿化无害（见 §四.5） | RAW 重建；无 |
| dive_0045 | 红渊研究院·共振采样 | 整条删除 | web/index.html（RAW 行，步 3 重建即清）；美术登记簿孤儿化无害（见 §四.5） | RAW 重建；无 |
| dive_0048 | 矿票（回收藏） | 整条删除 | web/index.html（RAW 行，步 3 重建即清）；美术登记簿孤儿化无害（见 §四.5） | RAW 重建；无 |
| dive_0049 | 硬矿钻（手持） | 整条删除 | web/index.html（RAW 行，步 3 重建即清）；美术登记簿孤儿化无害（见 §四.5） | RAW 重建；无 |
| dive_0051 | 震频器（微型） | 整条删除 | web/index.html（RAW 行，步 3 重建即清）；美术登记簿孤儿化无害（见 §四.5） | RAW 重建；无 |
| dive_0057 | 重力训练舱（极限负重） | 整条删除 | web/index.html（RAW 行，步 3 重建即清）；美术登记簿孤儿化无害（见 §四.5） | RAW 重建；无 |
| dive_0059 | 曜元（空腹） | 整条删除 | web/index.html（RAW 行，步 3 重建即清）；美术登记簿孤儿化无害（见 §四.5） | RAW 重建；无 |
| dive_0060 | 黑曜采掘·无氧班次 | 整条删除 | web/index.html（RAW 行，步 3 重建即清）；美术登记簿孤儿化无害（见 §四.5） | RAW 重建；无 |
| dive_0061 | 巡线灯 | 整条删除 | web/index.html（RAW 行，步 3 重建即清）；美术登记簿孤儿化无害（见 §四.5） | RAW 重建；无 |
| dive_0062 | 凿屑袋 | 整条删除 | web/index.html（RAW 行，步 3 重建即清）；美术登记簿孤儿化无害（见 §四.5） | RAW 重建；无 |
| dive_0064 | 星髓矿业·矿脉图 | 整条删除 | web/index.html（RAW 行，步 3 重建即清）；美术登记簿孤儿化无害（见 §四.5） | RAW 重建；无 |
| dive_0072 | 星髓矿业·二号钻台 | 整条删除 | web/index.html（RAW 行，步 3 重建即清）；美术登记簿孤儿化无害（见 §四.5） | RAW 重建；无 |
| dive_0073 | 抗共振司·白噪机 | 整条删除 | web/index.html（RAW 行，步 3 重建即清）；美术登记簿孤儿化无害（见 §四.5） | RAW 重建；无 |
| dive_0074 | 黑曜采掘·计件工资 | 整条删除 | web/index.html（RAW 行，步 3 重建即清）；美术登记簿孤儿化无害（见 §四.5） | RAW 重建；无 |
| dive_0077 | 抗共振司·导波索（并联） | 整条删除 | web/index.html（RAW 行，步 3 重建即清）；美术登记簿孤儿化无害（见 §四.5） | RAW 重建；无 |
| dive_0078 | 红渊研究院·频谱印章 | 整条删除 | web/index.html（RAW 行，步 3 重建即清）；美术登记簿孤儿化无害（见 §四.5） | RAW 重建；无 |
| dive_0079 | 红渊贸易局·苦水配给（双份） | 整条删除 | web/index.html（RAW 行，步 3 重建即清）；美术登记簿孤儿化无害（见 §四.5） | RAW 重建；无 |
| dive_0083 | 坠轨的清单 | 整条删除 | web/index.html（RAW 行，步 3 重建即清）；美术登记簿孤儿化无害（见 §四.5）；**tools/_t63_check.js / _t63_data.js 硬编码此 id** | RAW 重建；同步清理 _t63 清单（可留，脚本会跳过失效 id） |

## 二、cards/tremor.json（26 条，整条删除）

| 卡 id | 名称 | 删除方式 | cards 外影响面（grep 实测） | 连带操作 |
|---|---|---|---|---|
| trem_0007 | 震语铃 | 整条删除 | 同 §一：RAW 重建即清；美术登记簿孤儿化无害 | RAW 重建；无 |
| trem_0008 | 震语：问地 | 整条删除 | 同 §一：RAW 重建即清；美术登记簿孤儿化无害 | RAW 重建；无 |
| trem_0012 | 历法刻盘 | 整条删除 | 同 §一：RAW 重建即清；美术登记簿孤儿化无害 | RAW 重建；无 |
| trem_0021 | 埋骨礼 | 整条删除 | 同 §一：RAW 重建即清；美术登记簿孤儿化无害 | RAW 重建；无 |
| trem_0032 | 震语：引流 | 整条删除 | 同 §一：RAW 重建即清；美术登记簿孤儿化无害 | RAW 重建；无 |
| trem_0036 | 辨矿 | 整条删除 | 同 §一：RAW 重建即清；美术登记簿孤儿化无害 | RAW 重建；无 |
| trem_0040 | 五脉符 | 整条删除 | 同 §一：RAW 重建即清；美术登记簿孤儿化无害 | RAW 重建；无 |
| trem_0041 | 震语：淡忘 | 整条删除 | 同 §一：RAW 重建即清；美术登记簿孤儿化无害 | RAW 重建；无 |
| trem_0042 | 震语：断忆 | 整条删除 | 同 §一：RAW 重建即清；美术登记簿孤儿化无害 | RAW 重建；无 |
| trem_0048 | 震语：连震 | 整条删除 | 同 §一：RAW 重建即清；美术登记簿孤儿化无害 | RAW 重建；无 |
| trem_0049 | 三震（回声） | 整条删除 | 同 §一：RAW 重建即清；美术登记簿孤儿化无害 | RAW 重建；无 |
| trem_0051 | 震语：润喉 | 整条删除 | 同 §一：RAW 重建即清；美术登记簿孤儿化无害 | RAW 重建；无 |
| trem_0053 | 震语：五声 | 整条删除 | 同 §一：RAW 重建即清；美术登记簿孤儿化无害 | RAW 重建；无 |
| trem_0054 | 光导石（串珠） | 整条删除 | 同 §一：RAW 重建即清；美术登记簿孤儿化无害 | RAW 重建；无 |
| trem_0062 | 震语：叩问 | 整条删除 | 同 §一：RAW 重建即清；美术登记簿孤儿化无害 | RAW 重建；无 |
| trem_0063 | 涌喉·深潜 | 整条删除 | 同 §一：RAW 重建即清；美术登记簿孤儿化无害 | RAW 重建；无 |
| trem_0064 | 历法刻盘（补页） | 整条删除 | 同 §一：RAW 重建即清；美术登记簿孤儿化无害 | RAW 重建；无 |
| trem_0065 | 静底·灰烬 | 整条删除 | 同 §一：RAW 重建即清；美术登记簿孤儿化无害 | RAW 重建；无 |
| trem_0068 | 埋骨布（裹身） | 整条删除 | 同 §一：RAW 重建即清；美术登记簿孤儿化无害 | RAW 重建；无 |
| trem_0072 | 震语：回礼 | 整条删除 | 同 §一：RAW 重建即清；美术登记簿孤儿化无害 | RAW 重建；无 |
| trem_0073 | 静底·翻灰 | 整条删除 | 同 §一：RAW 重建即清；美术登记簿孤儿化无害 | RAW 重建；无 |
| trem_0074 | 涌喉·潮契 | 整条删除 | 同 §一：RAW 重建即清；美术登记簿孤儿化无害 | RAW 重建；无 |
| trem_0077 | 五脉符（浮位） | 整条删除 | 同 §一：RAW 重建即清；美术登记簿孤儿化无害 | RAW 重建；无 |
| trem_0079 | 震台石碑（无字） | 整条删除 | 同 §一：RAW 重建即清；美术登记簿孤儿化无害 | RAW 重建；无 |
| trem_0081 | 值班交接 | 整条删除 | 同 §一：RAW 重建即清；美术登记簿孤儿化无害；**_t63 两脚本硬编码** | RAW 重建；同步 _t63 |
| trem_0083 | 谐振的余音 | 整条删除 | 同 §一：RAW 重建即清；美术登记簿孤儿化无害；**_t63 两脚本硬编码** | RAW 重建；同步 _t63 |

## 三、cards/anmin.json（3 条）/ cards/cangmin.json（3 条）

| 卡 id | 文件 | 删除方式 | 影响面 | 连带操作 |
|---|---|---|---|---|
| anm_0005 | cards/anmin.json | 整条删除 | RAW 重建即清；美术登记簿孤儿化无害 | RAW 重建 |
| anm_0034 | cards/anmin.json | 整条删除 | RAW 重建即清；美术登记簿孤儿化无害 | RAW 重建 |
| anm_0038 | cards/anmin.json | 整条删除 | RAW 重建即清；美术登记簿孤儿化无害 | RAW 重建 |
| cng_0022 | cards/cangmin.json | 整条删除 | RAW 重建即清；美术登记簿孤儿化无害 | RAW 重建 |
| cng_0029 | cards/cangmin.json | 整条删除 | RAW 重建即清；美术登记簿孤儿化无害 | RAW 重建 |
| cng_0031 | cards/cangmin.json | 整条删除 | RAW 重建即清；美术登记簿孤儿化无害 | RAW 重建 |

## 四、共有的影响面结论（58 条逐一 grep 的汇总）

1. **web/index.html：58/58 命中**——全部在第 6391 行 RAW 内联数据里，重建即清，不需要手改 9137 行的文件。
2. **tools/sim.js：0/58**——它运行时 require(cards/*.json)（[tools/sim.js:10]-[tools/sim.js:13]），删卡自动同步。
3. **零命中的关键文件**：tools/starter_decks.json（R1 排除）、EASTER_EGGS 表（R2 排除）、tools/mapgen_bindings.json（只绑敌人/事件）、events|relics|layers|enemies/*.json、glossary.json、DESIGN.md——删卡不会踩中任何运行时硬引用。
4. **tools/_t63_check.js / _t63_data.js：3/58**（dive_0083、trem_0081、trem_0083）——T63 文本修复脚本的 id 清单。不删不崩（按 id 查不到时跳过），建议顺手删清单项保持账面干净。
5. **美术登记簿 58/58**（data/zh_prompts_full.json、art_catalog.json、art_families.json、qa_auto.json、final_manifest.json、motifs.json、lint*.json、picks.json、lore_index.json、jobs_*.json、_ver_state.json、tools/art_manifest.json、card_audit.json、card_power.json、text_lint.json）：T335 已把这些卡的**图**安排回收（reuse_for 列），登记簿保留原样即「孤儿记录」，无运行时危害；要账面干净需重导出（不在本单范围）。

## 五、回滚

- 四份 .bak-20261104 覆盖回去 → 重跑 _t46_wire.js → 重跑步 4-6 确认。
- 本单 58 条 id/name 与 T335_PRUNE.csv 一致；执行时若在 cards 里找不到某 id，先停下核对是否已有他人改动。
