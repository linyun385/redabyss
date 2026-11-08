# 本地生图管线（2026-10-30 建立）

## 一、ComfyUI 为什么放弃（结论）

`D:\ComfyUI` 是 2026-10-29 的 master（commit `fd7639f`）。它的新依赖 `comfy-kitchen`
在 torch 2.6.0+cu124 上直接崩：

```
ValueError: infer_schema(func): Parameter stride has unsupported type list[int].
The valid types are: ... Got func with signature (x: torch.Tensor, weight: torch.Tensor,
bias: torch.Tensor | None, residual: ..., stride: list[int], out: torch.Tensor)
```

`torch.fx` 的 schema 推导不认 C++ 融合算子里的 `list[int]`。要修只有两条路：

| 路 | 代价 | 风险 |
|---|---|---|
| 升级 torch 到 2.7/2.8（cu126） | 2.5–3 GB 下载 + 重装 ComfyUI 依赖 | comfy-kitchen 对 torch 版本很挑，可能连环崩 |
| 把 ComfyUI 退回旧 tag（无 comfy-kitchen 的版本） | 小 | 旧版对新 checkpoint/LoRA 支持差，且要重装旧 requirements |

**决定：不走这两条，改用 diffusers 直接加载 SDXL 单文件**（底模已在盘上，6.46 GB）。
ComfyUI 目录保留不动，将来想可视化再回头修。

## 二、实际可跑的管线

脚本：`tools/gen_art_diffusers.py`（自动套 `docs/STYLE_ART.md` 的前缀/后缀/负面词）

```powershell
$env:HF_ENDPOINT='https://hf-mirror.com'      # 必须：huggingface.co 直连超时，hf-mirror 可用
python tools\gen_art_diffusers.py `
  --prompt "an ancient brass lens held in a gloved hand, thin crimson light splitting into three" `
  --out tools\art_test\lens.png --width 768 --height 1152 --steps 20 --seed 7
```

### 实测数据（RTX 4060 Laptop 8 GB）
| 配置 | 耗时 | 显存峰值 |
|---|---|---|
| 832×1216 / 25 步 / 开 attention slicing | **644 s**（10.7 分钟） | 9.78 GB（溢到共享内存） |
| 768×1152 / 20 步 / 关 attention slicing | **60 s** | 9.55 GB |

**关键教训**：`enable_attention_slicing()` 是主要拖慢项（10 倍差距），8 GB 上不要开；
`enable_vae_slicing/tiling` 要开（diffusers 0.42 起在 `pipe.vae` 上，不在 `pipe` 上）。

### 依赖
`diffusers 0.42.1` + `accelerate 1.15.0`（阿里云镜像装成功；清华镜像对 diffusers 0.42.1 返回 403）。

## 三、提示词结构（踩过的坑）

- **风格前缀放最前面会把内容带跑**：`woodcut engraving, medieval occult manuscript illustration...`
  开头 + `centered symmetrical composition` → SDXL 稳定画出十字架/圣物/脸，而不是透镜。
- 改成：**对象先写、风格后写**，并把宗教符号赶进负面词：
  `cross, crucifix, religious symbol, face, portrait, skull, frame, border`
- 暗红要在负面词里排除 `color`，只在 prompt 里点明 `dark crimson accents only on the light`，
  否则整体会变灰（第一张就完全没红）。
- `gloved hand` 基本不听话（出来是裸手）；要么接受，要么改成更硬的描述 + 试多 seed。

## 四、还没做的
- 批量脚本（`tools/art_plan.json` + 循环）与 LoRA 提速（SDXL-Lightning 4 步，约 150 MB）
- 图接入卡牌图案区（T50 留的接口：`.card .art` 的 background-image）
- 8 GB 下的显存优化（832×1216 仍溢出；768×1152 也到 9.55 GB）

---

# 素材流水线总入口（2026-11-03 夜班 T249 追加）

> 后来的人只看这一页就能跑。所有脚本 `python -I tools/<名>.py --help` 都有自带说明；输出一律落 `data/`，不改 `web/assets/art/` 原图。（原「本地生图管线」章节保留在下方，未删改；改动前的旧版留档 `docs/ART_PIPELINE.md.bak`。）

## 0. 流水线全景

```
提示词 zh_prompts_full.json
   │  prompt_lint.py（禁用词扫描）→ data/lint.json
   │  job_builder.py（合成任务）  → data/jobs_night.json
   ▼
生图（三选一）
   · 万相远端：artctl.py gen      （串 wanx_gen.py）
   · 本地 GPU：tools/gen_art_diffusers.py（不在 artctl 内，参数见其 --help 与本文下半部）
   · 单张调试：tools/art_gen_one.py
   ▼
成图 web/assets/art/<id>.webp
   │  art_sync.py（artctl.py sync）
   ▼
质检回路（2026-11-02/03 夜班的完整走法）
   ① 人/模型逐张目检 → data/qa/QA_001–047.md（7 项判定）
   ② tools/qa_report.py → data/qa_report.md（不合格数/缺陷分布/按卡组分布）
   ③ 不合格 id → data/rewrite/RW_001–030.json（只写新主体段）
   ④ tools/job_builder.py → data/jobs_night.json（新主体段+原尾部=可执行 prompt）
   ⑤ 重画 → 第二轮复检 data/qa/RC_001–012.md（材质/厚度/对题 1–5 分）
   ▼
配套产物
   · tools/art_qa.py      → data/qa_auto.json（纯数字：尺寸/红占比/亮度/冷色/近黑）
   · tools/lore_index.py  → data/lore_index.json（图鉴文案索引）
   · tools/dup_finder.py  → data/dups.json（感知哈希雷同组）
```

## 1. 各脚本速查

| 脚本 | 用途 | 关键参数 | 产出 |
|---|---|---|---|
| `tools/artctl.py` | **编排入口**：families→jobs→gen→sync 只做编排 | 子命令 `families/jobs/gen/sync/plan`；`--night`（jobs 走 job_builder）；`--run` 真执行（缺省干跑） | 各子脚本产物 + `data/artctl_last_run.json` |
| `tools/art_qa.py` | 批量图数字质检（不出判断） | `--dir --ids --out` | `data/qa_auto.json` |
| `tools/prompt_lint.py` | 提示词禁用词扫描 | `--in --ids --full --out` | `data/lint.json`（`--full` 扫整条→`data/lint_full.json`） |
| `tools/job_builder.py` | rewrite+QA 不合格 → 出图任务 | `--rw-dir --out --limit` | `data/jobs_night.json` |
| `tools/qa_report.py` | 汇总 QA/RC 表格 | `--qa-dir --out` | `data/qa_report.md` |
| `tools/lore_index.py` | 图鉴文案索引 | `--lore-dir --out` | `data/lore_index.json` |
| `tools/dup_finder.py` | 感知哈希找雷同 | `--dir --threshold --out` | `data/dups.json` |
| `tools/_check_rw.py` | 校验 RW_*.json（验收用） | 组号… | 终端报告 |
| `tools/_check_lore.py` | 校验 LORE_*.md | 组号… | 终端报告 |
| `tools/_check_copy.py` | 校验 card/foe/evt 文案 | `card\|foe\|evt` 组号… | 终端报告 |

带 `_` 前缀的是一次性/校验脚本，不带 `_` 的是可复用工具。

## 2. 复跑全流程（示例）

```bash
cd C:\Users\Administrator\Desktop\杂七杂八\红渊\game

# 1) 提示词体检
python -I tools/prompt_lint.py                 # 主体段 → data/lint.json
python -I tools/prompt_lint.py --full          # 整条   → data/lint_full.json

# 2) 出图任务（rewrite 147 条 + QA 不合格 67 条 = 214 条）
python -I tools/job_builder.py                 # → data/jobs_night.json
python -I tools/artctl.py jobs --night         # 同上（走编排入口）

# 3) 生图（万相远端）
python -I tools/artctl.py gen --run            # 真跑需自行确认 wanx 配置

# 4) 同步进 web
python -I tools/artctl.py sync --run

# 5) 数字质检 + 汇总
python -I tools/art_qa.py                      # → data/qa_auto.json
python -I tools/qa_report.py                   # → data/qa_report.md
python -I tools/dup_finder.py                  # → data/dups.json
python -I tools/lore_index.py                  # → data/lore_index.json
```

## 3. 规则与口径（为何这样做）

- **分组口径**：图质检/图鉴文案 47 组 = `data/art_catalog.json` 顺序每 10 条（46×10+1=461）；映射在 `data/qa/_groups.json`。第二轮复检 12 组 = 第一轮不合格 125 张取 catalog 序前 120（`data/qa/_recheck_groups.json`）。
- **rewrite 清单口径**：主体段（「洞底是一整片深红的光」前半）命中禁用词/电器名词、或缺镜头词、或缺工艺痕迹词 → 127 条 + QA 对题补充 20 条 = 147 条，见 `data/rewrite/_targets.json` 的 `rule` 字段。
- **prompt_lint 词表**：任务书说的「规则 VIII/IX/X」落地为文档里实际存在的表——`mech`=ART_PROMPT_SPEC §六禁词、`appliance`=电器名词（第一轮翻车源）、`species`=§VIII 物种名、另加 `en_bad`=§四英文禁词；每条命中带 `rule` 字段可分开统计。
- **只出数字 vs 判断**：`art_qa.py` 只出数字（任务书红线）；「合格与否」的判断永远在 QA_*.md / RC_*.md 的复核里。
- **改图规则**：任何时候不许直接改 `web/assets/art/` 成品；要换图走 jobs → 重画 → art_sync 的链路。

## 4. 夜班基线数字（2026-11-03 凌晨）

- 一轮质检：461 张，不合格 125（27.1%）；缺陷 Top：电器外形、可读文字、主体偏移。
- 二轮复检（120 张最差样本）：建议重画 0、改提示词后重画 20、保留 80；三项均 ≤2 的为 0。
- rewrite：147 条主体段重写完毕（RW_001–030），`_check_rw.py` 全过。
- lint：主体段命中 133 条（rewrite 前口径，147 条重写已覆盖其中 dive/trem/event 部分）。
- jobs_night：214 条待重画任务（rewrite 147 + QA-only 67）。
- 雷同检测：>0.9 相似对 109 个、成组 6 组（data/dups.json，重画批次注意避让）。
