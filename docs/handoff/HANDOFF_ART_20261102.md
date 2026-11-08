# 交接：百炼接管素材生产（2026-11-02 10:25）

> 上下文水位高，这份是落盘快照。恢复后先读这份，再看 `docs/art/ART_BAILIAN.md` 与 `docs/art/ART_PROMPT_SPEC.md`。

## 一、已确认可用（实测）

| 能力 | 模型 | 结果 |
|---|---|---|
| 文本 | qwen-plus / qwen-max / qwen-long | ✅ 200 |
| 文本 | qwen-turbo | ❌ 429（免费档限流） |
| 文本 | qwen3-max | ❌ 404（名字不对） |
| 图像 | wanx2.1-t2i-turbo | ✅ 1024×1024，**11–39 秒/张，均值 18.4 秒** |

## 二、管线（已跑通）

```
tools/wanx_gen.py --file data/zh_prompts.json
```
- 输入：`[{"id","prompt","size"}]`（**中文提示词**）
- 产出：原图 `art/_wanx/<id>.png` + 游戏用 `web/assets/art/<id>.webp`（长边 768、q82）
- 断点续跑（已存在跳过）、失败重试 1 次、日志 `tools/wanx_run.json` / `wanx_failed.json`
- 跑完自动 `art_sync.py` 重建 ART 表

## 三、首批 6 张结果（10:21 跑完，6/6 成功）

| id | 类型 | 结果 |
|---|---|---|
| `evt_zh_body_in_suit` | 事件 · 防护服遗体 | ✅ **完全命中**（靠壁坐地、面罩划痕、地形红光、版画排线） |
| `foe_zh_eyeless_eel` | 敌人 · 无眼鳗 | 待看 |
| `foe_zh_waste_crab` | 敌人 · 废料蟹 | 待看 |
| `foe_zh_salt_column` | 敌人 · 盐柱 | 待看 |
| `card_zh_inspection_board` | 卡牌 · 检查板 | 待看 |
| `foe_zh_thermophile` | 敌人 · 嗜热菌落 | ❌ 跑题（画成管道钟乳，主体丢了 —— “一整片菌落”又是集合名词） |

**结论**：事件类/单体物件类命中率高；**集合名词依旧失败**（规则 IV 再次验证）。

## 四、下一步（按优先级）

1. **用 qwen-max 批量生成 280 族中文提示词**
   - 输入：`ART_PROMPT_SPEC` 规则 I–V + 世界观文档（GLOSSARY/LAYERS/ECO_*）+ 对象清单
   - 输出：`data/zh_prompts_full.json`（格式同 `zh_prompts.json`）
   - 我逐批跑 `check_prompts.js`（规则需补中文版）+ 抽查
2. **分批生成**：先敌人 60–90 族（20 分钟）→ 审图 → 事件 102 → 卡面按额度
3. **审图**：`python tools/art_studio.py` → 标记不合格 → 回队重跑
4. **限流应对**：把百炼成图当训练集，训 SDXL LoRA 离线跑（用户提的方案）

## 五、成本与风险

- 18.4 秒/张 → 280 族 ≈ **86 分钟**；30 元套餐能撑多少未知，先跑敌人批试探
- 万相产出是 RGB 插画（无纸纹物理质感），但排线感已足够像版画
- 若额度耗尽：本地 SDXL（512×752、110 秒/张）仍可用，作为兜底
- **禁止**：不要把 key 写进任何提交物（key 在 `tools/free_llm_keys.json`，只读不打印）

## 六、边界

- 六张里我只逐张看过 2 张（事件命中、菌落跑题），其余四张未看
- 18.4 秒是 6 张均值，样本小；大批判量可能受 RPM 限制
- 万相不支持负向词，规则 V（光/背景）靠正向描述，命中率待大批量验证
