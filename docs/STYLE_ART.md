# 美术风格规范：密教模拟器风

> 用途：给 SDXL / 未来 Qwen-Image 的生图提示词定标，也给 UI 配色定调。
> 2026-10-29 建立。灰机 wiki 图片有防盗链（567），本文基于对该作美术的已知特征整理。

---

## 一、核心特征

| 维度 | 特征 |
|---|---|
| **技法** | 木刻版画 / 铜版画（woodcut engraving） |
| **线条** | 粗细不一的手刻感线条，阴影用密集排线（cross-hatching），不用平滑渐变 |
| **配色** | 棕褐（sepia）+ 暗红 + 墨黑。最多三个色相，高对比 |
| **质感** | 老化纸张 / 羊皮纸，边缘暗角，印刷网点 |
| **构图** | 中心对称，主体明确，像一枚印章或一枚纹章 |
| **内容** | 象征物：眼睛、门、刀、杯、星、蛇、玫瑰、骷髅、手 |
| **时代感** | 中世纪手稿、文艺复兴解剖图、炼金术图谱、塔罗牌 |
| **禁止** | 照片感、3D 渲染、平滑渐变、动漫、现代设计感、彩色鲜艳 |

## 二、色板（UI 与图片统一用）

```
纸底   #d9cfbe   老化纸
棕墨   #6b5334   主线条
深褐   #2b2118   阴影/背景
暗红   #8b2a20   强调（血、火、凝视）
枯金   #a8834a   稀有/升华
```

游戏界面现在用的是深色底（#0a0506 系），
如果未来换成「羊皮纸底 + 棕墨」，整体会立刻像这个风格。
**这是一个可选的重大改造，先记着，不急着做。**

## 三、SDXL 提示词模板

### 通用前缀
```
woodcut engraving, medieval occult manuscript illustration,
sepia ink and dark crimson on aged parchment,
heavy cross-hatching, rough hand-carved lines,
```

### 通用后缀
```
centered symmetrical composition, dark vignette edges,
no text, no letters, no watermark
```

### 负面提示词（固定）
```
photograph, 3d render, cgi, smooth gradient, airbrush,
anime, manga, cartoon, colorful, saturated, neon,
modern design, flat vector, ui element, text, watermark, signature
```

### 尺寸
- 卡牌图案：**832 × 1216**（3:4 略窄，接近卡牌）
- 敌人立绘：**832 × 1216**
- 图标：**1024 × 1024**

---

## 四、按对象的提示词示例

### 光脉 · 光导透镜
```
woodcut engraving, medieval occult manuscript illustration,
an ancient brass lens held in a gloved hand, a thin line of crimson
light passing through it and splitting into three,
sepia ink and dark crimson on aged parchment,
heavy cross-hatching, rough hand-carved lines,
centered symmetrical composition, dark vignette edges, no text
```

### 矿脉 · 相石
```
woodcut engraving, an irregular translucent crystal with a pulsing
inner light, embedded in cracked rock,
sepia and dark crimson, heavy hatching, aged parchment,
centered, dark background, no text
```

### 震脉 · 震语：听骨
```
woodcut engraving, a figure pressing their forehead against a stone
wall, concentric vibration rings spreading through the rock,
sepia ink, dense cross-hatching, medieval manuscript style,
centered, dark vignette, no text
```

### 敌人 · 腐生菌
```
woodcut engraving of a pale fungal mass feeding on something larger
than itself, many small filaments reaching out,
sepia and dark crimson, heavy hatching, aged parchment,
centered, dark background, no text
```

### 巨怪 · 光蛭母
```
woodcut engraving of a gigantic translucent jellyfish-like creature
suspended in a shaft of crimson light, long tendrils hanging down,
sepia and dark crimson, dense cross-hatching,
centered, dark vignette, no text
```

---

## 五、验收：什么叫"对味"

生成一张图后，用这三条判断：

1. **缩小到 64px 还能看出是什么吗**？能，就是好图标；糊成一团就不行
2. **去掉颜色，只看黑白**？如果靠线条仍然成立，就是版画风；如果靠颜色才成立，就是错的
3. **它像不像一张从某本不该存在的书里撕下来的插图**？这是最高标准

---

## 六、图标策略（不依赖生图）

HUD 和意图这类**高频小图标**不要用生成的图，用 Unicode + CSS：

| 含义 | 符号 | 颜色 |
|---|---|---|
| 生命 | ♥ | `#8b2a20` |
| 格挡 | ⬢ | `#5a7fa0` |
| 能量 | ✦ | `#a8834a` |
| 共鸣 | ∿ | `#b05a1a` |
| 凝视 | ◉ | `#8b1a1a` |
| 金币 | ◈ | `#c9a35a` |

理由：体积为零、可随时改色、不会糊。
生成的图只用在**卡牌图案区 / 敌人立绘 / 职业立绘**这三处。
