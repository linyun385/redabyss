# ART_PROMPTS_V2.md — 生图 prompt 模板定稿（T66 产出）

> 风格依据：`docs/REF_CULTIST_CLASSIFY.md`（**推翻木刻假设**：密教实际是扁平色块 + 硬边 + 1–3 高饱和色 + 颗粒噪点，不是排线铜版画）。三套模板与机器清单 `tools/art_manifest.json` 一一对应；批量执行 `tools/gen_art_batch.py`，版权闸门 `tools/art_similarity.py`。

## 0. 万前缀（所有模板共用，写在最后一段）

- 分辨率/步数：**768×1152 / 20 步**（实测 ~60s/张、8GB 卡安全）；只有语言 A 允许 **832×1216**（更慢，结局少才用得起）
- HF 镜像：`HF_ENDPOINT=https://hf-mirror.com` 必设
- 负面词在每张的 `negative` 字段里，模板只列正面骨架

## 1. 语言 B —— 象征/图案区（卡面图案 48 张 + 敌人 24 张）

```
minimal emblem on flat black background: {对象英文短语}, few tiny white sparks,
grainy risograph print texture, no outline, solid flat colors, high contrast,
centered, lots of negative space
```
负面：
```
engraving, cross-hatching, realistic, gradient, glow, text, border, frame, architecture, hand, person, photograph, 3d render, anime, blurry, lowres
```
对象取材：`art_manifest.json` 的 `obj` 字段（每生态 6 卡面 + 3 敌人，全部来自该生态的敌人/事件意象，如 nexus 的 chained signature quill ↔ 敌 d8_08 签到簿的笔）。

## 2. 语言 C —— 玩法卡/立绘（4 张职业）

```
flat minimal illustration on off-white paper: {对象}, thick uniform dark outline,
only three flat colors, no shading, no gradient, grainy print texture, centered,
generous margin
```
负面：
```
realistic skin, gradient shading, glow, text, watermark, photograph, 3d render, anime, busy background, lowres
```

## 3. 语言 A —— 塔罗式（结局 3 张）

```
tarot card illustration, dark scene with one glowing area: {场景},
heavy black border frame, roman numeral "I|II|III" at top and blank title bar at
bottom, muted palette with a single hot red accent, grainy print texture
```
负面：
```
text, watermark, photograph, 3d render, bright saturated colors, modern clothing, lowres
```
（罗马数字用引号包住让模型画形状；标题栏留空——标题由游戏 UI 叠加，避免模型写错字。）

## 4. 三条反面例子（会画崩的写法）

1. **风格前缀放最前**（T44 的坑）：`woodcut engraving, medieval occult..., a sealed airlock hatch` —— 风格词吃掉对象权重，出来的是「一张版画风格的任何东西」。**对象必须紧跟在容器短语后面**（`minimal emblem on flat black background: 对象`），风格细节全放后缀。
2. **语言混用**：给图案区（78px 缩略）用 A 语言「dark scene with…」——细节量太大，缩到 78px 糊成一团；图案区只能用 B 的单符号大留白。
3. **负面词漏掉 border/frame**：B 语言的卡面图案会自己长出一圈塔罗边框和罗马数字（训练集偏置），负面里没有 border/frame/text 时约三成图带框——框由游戏 UI 画，图里长框等于双框。

## 5. 断点续跑与闸门

- 批量：`python tools/gen_art_batch.py`（跳过已存在；`--only id1,id2` 子集；失败重试 1 次后记 `tools/art_failed.json`）
- 闸门：`python tools/art_similarity.py`——与 43 张参考图（用户 wiki 拉取目录，**只读不复制**）比对 dHash，汉明距离 ≤6 弃用重生成（阈值依据见脚本头注释：64bit dHash 随机对均值 32/σ≈4，≤6 在 8σ 外）
- 参考图边界：不进交付物、不入库、不训练会被发布的 LoRA（REF_CULTIST_CLASSIFY §五）
