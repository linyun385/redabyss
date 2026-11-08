# 素材工作台使用说明（自己生图 / 换图）

## 一、启动

```powershell
cd C:\Users\Administrator\Desktop\杂七杂八\红渊\game
python tools\art_studio.py
```

浏览器打开 **http://127.0.0.1:8770**（关掉黑窗口即停）。

> 不需要 ComfyUI（它的 torch 冲突别去修）。不需要联网。单张 640×936 / 20 步约 40–90 秒。

## 二、界面

- **左侧**：79 张素材缩略图网格，点任意一张选中
- **右侧**：
  - 图 id、生态、对象、文件体积
  - **使用者**：这张图现在挂在哪些卡牌 / 敌人 / 职业 / 结局上（一行一行列出来）
  - 大图预览
  - 可编辑：`prompt` / `negative` / 宽 / 高 / `seed`
  - **「重新生成并替换」** → 本地 diffusers 出图，直接覆盖，并自动同步到 `web/assets/art` + 重建 `window.ART` 表
  - **「上传图片替换…」** → 选本地图片（png/jpg/webp），自动转 webp、长边限 768、覆盖并同步
- 生成过程中顶部显示「生成中：<id>」，日志在右下角

## 三、素材在哪

| 内容 | 路径 |
|---|---|
| 游戏实际加载的图（唯一真相）| `game\web\assets\art\<id>.webp`（79 张） |
| 生成源文件（原图，可覆盖）| `game\art\eco\<eco>\*.webp`、`art\class\*.webp`、`art\ending\*.webp` |
| 清单（id / 提示词 / 尺寸 / 种子）| `game\tools\art_manifest.json` |
| **映射表（图 ↔ 卡牌/敌人/职业/结局）** | `game\docs\ART_MAP.md`、`game\docs\ART_MAP.csv` |
| 浏览器预览版（10 张）| `game\art\_previews\` |

映射表重新生成：`python tools\gen_art_map.py`（改代码或改卡牌后要重跑）。

## 四、三种换图方式（从省事到彻底）

1. **只换一张图、不想写提示词**：工作台 → 选中 →「上传图片替换…」
2. **想重出、微调风格**：工作台 → 改 prompt/seed →「重新生成并替换」
3. **批量**：直接替换 `web\assets\art\<id>.webp`，然后跑
   ```powershell
   python tools\art_sync.py     # 同步 art/ → web/assets/art + 重建 ART 表
   node tools\check_web.js      # 确认路径都能找到
   ```

## 五、现在的图为什么"和卡名没关系"（诊断）

`web/index.html` 里卡面 id 是这么算的（`cardArtId()`）：

```
face_<生态>_<1..6>
生态 = 卡牌首个脉：light→eco_sea / water→eco_arid / heat→eco_vent / tremor→eco_cold / mineral→eco_rad
序号 = 1 + sum(charCode(卡牌id)) % 6
```

也就是说**一张图被同生态的一大批卡共享**。实测共享情况：

| 图 id | 被多少张卡使用 |
|---|---|
| `face_eco_sea_5` | **17 张** |
| `face_eco_rad_2` | 15 张 |
| `face_eco_cold_3` | 13 张 |
| `face_eco_sea_1` | 12 张 |

另外有 **8 张图没有被任何卡/怪引用**（生成出来但没分配上）。

所以"密教味够、但和卡面名字无关"不是审美问题，是**分配粒度问题**：现在是"每生态 6 张共享"，要变成"每张卡一张专属图"，需要：

- 卡面图从 `face_<eco>_<n>` 改成 `face_<cardId>`（240+ 张，每张单独 prompt，prompt 里写清楚这张卡画什么）
- 敌人同理：`foe_<enemyId>`（113 只敌人专属图）
- 这需要一份 **per-card / per-enemy 的提示词清单**（现在 manifest 只有 79 条，是按生态写的）

要做这件事我可以排一个任务（约 350 条提示词 + 分批生成，按 50 秒/张算 ≈ 5 小时 GPU），你确认我再排。
