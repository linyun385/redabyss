# -*- coding: utf-8 -*-
"""追加 T80 记录到 TASK_DONE.md（我自己收尾，不采信 GLM 未完成的口径）。"""
from pathlib import Path

GAME = Path(__file__).resolve().parents[1]
DOC = GAME / 'TASK_DONE.md'

ENTRY = """
## T80 完成（生图提速，2026-11-01 由 DeepSeek 接手收尾）
- status: **部分达成** —— 640×936 ≤60s 在本机不可达；512×752 稳定 ≈110s/张
- 关键发现（推翻 GLM 的旧结论）：**VAE 转 fp16 会输出全黑图**。
  实测 `art/_perf/640_fp16vae.png` 与 `fast_2_512x752.png` 均为 mean=0 / std=0；
  日志里有 `invalid value encountered in cast`，说明 SDXL VAE 的 latent 在 fp16 下溢出。
  所以 GLM 之前记的「VAE fp16 → 215s / 峰值 7.93GB」是**黑图换来的假速度**，不能采信。
- 正确配置（已写入 `tools/gen_art_diffusers.py`）：fp16 UNet + **VAE 保持 fp32**（force_upcast=True）
  + VAE tiling/slicing + 文本编码器用完即释放（省 ~1.2GB）+ cudnn.benchmark + tf32；
  默认尺寸改为 **512×752**；新增 `--vae` 入口给 fp16-safe VAE。
- 实测（同 prompt / seed=501 / 20 步 / cfg 6）：
  · 512×752 推荐配置 ≈ 110s，峰值 ≤8.0GB，图有效
  · 640×936 旧链路 193–737s（波动极大，峰值 9.1GB 已溢出换页）
  · fp16 VAE 路线 512×752 只要 35.6s —— 但**全黑**，不可用
- 新增黑图自检：`gen_art_diffusers.py` 出图后计算像素 std，<3 直接打印警告（防再次踩坑）。
- 下一根杠杆：`madebyollin/sdxl-vae-fp16-fix`（fp16 安全 VAE，~335MB）。本机 hf-mirror 下载未成功
  （拉取卡住，已终止），拿到后走 `--vae` 切换，**切换后必须验证 std>3**。
- 对批量的影响：280 族图按 110s/张 ≈ 8.5 小时（若 fp16-safe VAE 生效可降到 ~4.7 小时）。
- check: `node tools/check_web.js` 0 警告 / `node tools/test_engine.js` 全过 / `gen_art_diffusers.py` 语法 ok；
  汇总数字落盘 `tools/art_perf.json`，说明文档 `docs/ART_PERF.md`
- notes/边界：所有数字来自本机 RTX 4060 Laptop 8GB + torch 2.6.0+cu124 + diffusers 0.42.1；
  首图含预热（模型加载 18s），稳态值取第 2 张；未测 CUDA graphs / TensorRT 等激进路线。
"""

if __name__ == '__main__':
    with DOC.open('a', encoding='utf-8') as f:
        f.write(ENTRY)
    print('T80 记录已追加')
