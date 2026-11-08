# -*- coding: utf-8 -*-
"""写 T80 的汇总结果到 tools/art_perf.json（数字全部来自实测）。"""
import json
from pathlib import Path

GAME = Path(__file__).resolve().parents[1]
OUT = GAME / 'tools' / 'art_perf.json'

DATA = {
    "task": "T80",
    "date": "2026-11-01",
    "gpu": "NVIDIA GeForce RTX 4060 Laptop GPU (8GB)",
    "verdict": "640×936 ≤60s 在 8GB 卡上不可达；交付 512×752 ≈110s/张；下一根杠杆是 fp16-safe VAE",
    "trap": {
        "what": "VAE 转 fp16（force_upcast=False）",
        "symptom": "输出全黑图（mean=0, std=0）",
        "evidence": ["art/_perf/640_fp16vae.png (std=0.0)",
                     "art/_perf/fast_2_512x752.png (std=0.0)"],
        "why": "SDXL VAE 在 fp16 下 latent 溢出（日志出现 invalid value encountered in cast）",
        "consequence": "GLM 之前记录的『fp16 VAE 215s / 7.93GB』是黑图换来的假速度，不可采信"
    },
    "measurements": [
        {"config": "旧链路 fp32 VAE，无优化", "size": "640x936", "sec": "193–737", "peak_gb": 9.11, "valid": True, "source": "GLM probe"},
        {"config": "旧链路 fp32 VAE，无优化", "size": "512x752", "sec": "109–119", "peak_gb": 8.34, "valid": True, "source": "GLM probe"},
        {"config": "fp16 VAE（错误路线）", "size": "640x936", "sec": 340.4, "peak_gb": 7.35, "valid": False, "source": "我实测"},
        {"config": "fp16 VAE（错误路线）", "size": "512x752", "sec": 35.6, "peak_gb": 7.35, "valid": False, "source": "我实测"},
        {"config": "fp32 VAE + 编码器释放 + tiling/slicing（当前推荐）", "size": "512x752", "sec": "≈110", "peak_gb": 8.0, "valid": True, "source": "我实测 + GLM 交叉"}
    ],
    "current_config": [
        "fp16 UNet (from_single_file torch_dtype=float16)",
        "VAE 保持 fp32（force_upcast=True）+ enable_tiling + enable_slicing",
        "文本编码器用完即释放（省 ~1.2GB）",
        "cudnn.benchmark=True + tf32 matmul",
        "不启用 attention slicing",
        "默认尺寸 512x752（卡面显示 190px 宽，够用）"
    ],
    "next_lever": {
        "what": "madebyollin/sdxl-vae-fp16-fix（fp16 安全 VAE，约 335MB）",
        "expected": "512×752 有机会回到 40–60 秒",
        "status": "本机 hf-mirror 下载未成功（拉取卡住后终止），脚本已留 --vae 入口",
        "must_verify": "换 VAE 后必须检查出图 std>3（不能是黑图）"
    },
    "batch_estimate": {
        "family_images": 280,
        "at_110s": "约 8.5 小时",
        "at_60s_if_fp16_vae_works": "约 4.7 小时"
    }
}

OUT.write_text(json.dumps(DATA, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
print('写出', OUT)
