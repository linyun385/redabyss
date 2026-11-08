# 百炼（DashScope）接入结论（2026-11-02 实测）

## 一、可用性（key 在 `tools/free_llm_keys.json` 的 DASHSCOPE_API_KEY）

| 能力 | 模型 | 状态 | 备注 |
|---|---|---|---|
| 文本 | qwen-plus | ✅ 200 | 可批量写提示词 |
| 文本 | qwen-max | ✅ 200 | 质量更高，慢一些 |
| 文本 | qwen-long | ✅ 200 | 长文档（世界观）阅读 |
| 文本 | qwen-turbo | ❌ 429 Throttling.RateQuota | 免费档限流，别用 |
| 文本 | qwen3-max | ❌ 404 | 模型名不对 |
| **图像** | **wanx2.1-t2i-turbo** | ✅ 成功 | 1024×1024，10–20 秒/张 |

## 二、为什么这条路比本地 SDXL 好（实测对比）

| 维度 | 本地 SDXL（512×752） | 万相 wanx2.1 |
|---|---|---|
| 单张耗时 | 3–15 分钟（波动） | **10–20 秒** |
| 版画/排线质感 | 十几次都没做出来 | **一次就有**（细密排线 + 米黄纸 + 深墨轮廓） |
| 中文提示词 | 要先翻英文，翻完就漂 | **直接写中文世界观** |
| 倒吊/红光/地底 | 反复失败（写成布、写实动物、宫殿） | **第一版就成立** |
| 分辨率 | 512×752 | 1024×1024（缩到卡面更够） |
| 成本 | 本地 GPU + 电费 | 套餐额度（本月还有） |
| 显存 | 吃 7–8GB，影响你用电脑 | 0，纯远程 |

样例：`art/_review/13_万相_版画卵囊.png`、`14_万相_垂挂伞囊群.png`。

## 三、接入方式（脚本已写好骨架）

调用链（异步）：
```
POST https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis
     header X-DashScope-Async: enable
     body: {model, input:{prompt}, parameters:{size:'1024*1024', n:1}}
  → task_id
GET  https://dashscope.aliyuncs.com/api/v1/tasks/<task_id>   （轮询 3 秒一次）
  → output.task_status = SUCCEEDED，output.results[0].url 下载
```

## 四、建议的生产方案（替代本地批量）

1. **提示词用中文写**（`ART_PROMPT_SPEC` 的规则 I–V 原样适用，只是语言换成中文）
2. 每族一张 → 下载 → 压缩到 webp（长边 768、q82）→ `art_sync.py`
3. 批量脚本：`tools/wanx_gen.py`（待写）—— 读 `data/art_families.json`，逐族出图，断点续跑
4. 成本控制：先跑 20 族看一致性，再全量；每张失败重试 1 次
5. 文本模型（qwen-plus/max）用来**批量生成 280 族中文提示词**，我审规则校验

## 五、风险与边界

- 套餐本月到期后不能再用 → 现在优先把**最重要的资产**（敌人 60–90 族 + 事件 102 张）跑完，卡面 266 张看额度
- 万相产出的是 RGB 插画，不是印刷文件；**它没有"纸"的物理质感**，但排线感已经足够像版画
- 需要人工审图（工作台已就绪：标记 → 回队 → 重跑）
- 不要把它当"最终美术"，它是**可用的第一版素材**
