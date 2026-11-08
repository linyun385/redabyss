# T80 结论：生图提速（2026-11-01 实测，我自己收尾）

## 一句话结论
**在 8GB 笔记本 4060 上，「640×936 ≤60 秒」不可达**；能交付的是 **512×752 ≈ 110 秒/张**（比 640 快约 43%），
下一根真正的杠杆是**换 fp16-safe VAE**，不是调参数。

## 二、踩到的坑（这条最重要，别再重复）
GLM 之前的 probe 记录里有一条「VAE 转 fp16 → 215s / 峰值 7.93GB」，看起来是提速路线。

**它是假的**：VAE 转 fp16 后输出**全黑图**。
我实测两张都验证过：
```
art/_perf/640_fp16vae.png    mean 0.0  std 0.0   ← 黑图
art/_perf/fast_2_512x752.png mean 0.0  std 0.0   ← 黑图
```
SDXL 的 VAE 在 fp16 下 latent 会溢出（日志里 `RuntimeWarning: invalid value encountered in cast` 就是征兆），
所以**必须保留 `force_upcast=True`（VAE fp32）**，然后用 tiling/slicing 控显存。

> 教训：只看耗时和显存会得出错误的"最优配置"。**提速的每一版都必须验证出图不是黑的**（std > 3）。

## 三、实测数据（同一 prompt / seed=501 / 20 步 / cfg 6）

| 配置 | 尺寸 | 单张耗时 | 峰值显存 | 图是否有效 |
|---|---|---|---|---|
| 旧链路（fp32 VAE，无优化） | 640×936 | 193–737s（波动极大） | 8.9–9.1 GB | ✓ |
| 旧链路 | 512×752 | 109–119s | 8.34 GB | ✓ |
| **fp16 VAE**（错误路线） | 640×936 | ~340s | 7.35 GB | ✗ 黑图 |
| **fp16 VAE**（错误路线） | 512×752 | **35.6s** | 7.35 GB | ✗ 黑图 |
| **fp32 VAE + 编码器释放 + tiling/slicing**（当前推荐） | 512×752 | **≈110s** | ≤8.0 GB | ✓ |

关键点：8GB 卡上 640×936 的**解码**阶段会溢出换页，耗时从 190s 跳到 700s；512×752 稳得多。

## 四、当前推荐配置（已写进 `tools/gen_art_diffusers.py`）
```
fp16 UNet（from_single_file torch_dtype=float16）
VAE 保持 fp32（force_upcast=True）+ enable_tiling() + enable_slicing()
文本编码器用完即释放（省 ~1.2GB）
cudnn.benchmark = True；tf32 matmul 允许
不做 attention slicing（它会把速度拖到 10 分钟）
默认尺寸 512×752（卡面只显示 190px 宽，够；敌人图 ~90px）
```

## 五、下一根杠杆（未完成，需要网络）
`madebyollin/sdxl-vae-fp16-fix`（fp16 安全的 VAE，约 335MB）：
- 换它之后 VAE 可以真正用 fp16，按上面的对照表，512×752 有机会回到 **40–60 秒**
- 本机 `hf-mirror.com` 下载**没成功**（拉取卡住，我已终止）；等网络好时再试：
  ```powershell
  $env:HF_ENDPOINT='https://hf-mirror.com'
  python -c "from huggingface_hub import hf_hub_download; print(hf_hub_download('madebyollin/sdxl-vae-fp16-fix','diffusion_pytorch_model.safetensors'))"
  ```
- 脚本已留 `--vae <路径>` 入口，拿到文件即可切换（**切换后必须验证不是黑图**）

## 六、对批量任务的现实影响
- 按 280 族图估算：**512×752 ≈ 110s/张 → 约 8.5 小时**；640 则要 20 小时以上，不可行
- 建议批量一律用 **512×752**，需要大图（结局/立绘）单独用 640 且接受慢

## 七、边界声明
- 所有数字来自本机 RTX 4060 Laptop（8GB）、torch 2.6.0+cu124、diffusers 0.42.1
- 首次生成含预热（模型加载 18s + 首图 340s），稳态值取第 2 张
- 没有测 CUDA graphs / TensorRT / 关 cudnn 等更激进的路线（收益不明、风险高）
