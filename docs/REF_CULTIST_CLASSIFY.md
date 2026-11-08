# 密教素材分类（对照风格用）· 2026-10-30

来源目录：`C:\Users\Administrator\Desktop\杂七杂八\红渊\密教图片素材（对照风格用）`（用户从 wiki 拉取，共 43 个文件）
**仅作风格对照，不进交付物、不入库。**

## 一、分类结果

| 组 | 数量 | 尺寸/比例 | 内容 | 用途 |
|---|---|---|---|---|
| **A 塔罗式神祇/时刻卡** | 25（0.68–0.69） | 192×278/280/281，另有 1 张 288×420 高清 | 黑边框 + 顶部罗马数字 + 底部标题；画面是暗色绘景（人物/场景） | 只在做「神祇/结局/时刻」时参考；**不适合**塞进 78px 的卡面图案区 |
| **A′ 稍方的长方形** | 2（0.83） | 192×230 | Vault 类 | 次参考 |
| **B 象征/图鉴卡** | 属 A 尺寸，例：Despair | 黑底 + 单一高饱和色符号 + 少量白色点缀 + 颗粒噪点 | **最接近我们卡牌的图案区**（缩到 78px 仍可辨识） |
| **C 玩法小卡（游戏内）** | 1 张横排合集 615×116 | 米白卡面 + 扁平彩色小插画 + 黑色中文名 + 细边框 | **卡牌 UI 的整体语言应为这一层**（我们的卡就是这个位置） |
| **D 角色头像** | 15 | 75×75 | 纯色底 + 黑白双色扁平面孔，硬边、无渐变 | 职业立绘/人物占位参考 |

## 二、真实风格结论（推翻 STYLE_ART.md 的木刻假设）

看了真图之后，`docs/STYLE_ART.md` 里那套「木刻版画 + 棕褐 + 密集排线」**不是密教的卡面语言**，差别就在这里：

| 维度 | 密教实际 | 我们之前做的 |
|---|---|---|
| 技法 | **扁平色块 + 硬边**，几乎不排线；少量颗粒噪点（risograph 感） | 铜版画/木刻，密集排线 |
| 配色 | 黑底或米白底 + **1–3 个高饱和色**（朱红/品红/橙金/苍紫） | 棕褐单色 + 一点暗红 |
| 构图 | 单符号/单场景，**大留白**，无景深、无背景环境 | 中心对称徽章，常带环境（建筑、台座） |
| 元信息 | 卡面自带**边框 + 罗马数字 + 标题**（塔罗式） | 无边框无编号 |
| 细节量 | 极低，缩到 78px 依然一眼认出 | 细节过密，缩小后糊成一团 |

**所以「味道差得大」不是模型不行，是风格规范本身写偏了。**

## 三、按新结论重写的生图提示词骨架

### B 象征卡（卡面图案区，推荐）
```
minimal emblem on flat black background: <一个物件/符号>, few tiny white sparks,
grainy risograph print texture, no outline, solid flat colors, high contrast,
centered, lots of negative space
负面：engraving, cross-hatching, realistic, gradient, glow, text, border, frame, architecture, hand, person
```

### C 玩法卡（卡面整体观感）
```
flat minimal illustration on off-white paper: <物件>, thick uniform dark outline,
only three flat colors, no shading, no gradient, grainy print texture, centered, generous margin
```

### A 塔罗式（只在结局/神祇时用）
```
tarot card illustration, dark scene with one glowing area, heavy black border frame,
roman numeral at top and title bar at bottom, muted palette with a single hot accent
```

## 四、取舍建议
1. **卡面图案区（78px）走 B**：黑底 + 一色符号 + 颗粒。缩略辨识度最高，也最像密教。
2. **卡牌整体走 C 的结构**：米白纸面 + 图案区 + 黑字名 + 细边；这正是 T50 CSS 已经做出来的骨架，只需要把图换成扁平风。
3. **塔罗式 A 留给结局/神祇**（T51 三结局），那才是它的用武之地。

## 五、版权边界
这些图是 Weather Factory 的作品，**只做内部风格对照**：
- 不进游戏包、不进 repo、不随项目发布
- 不拿它们训练会被发布的 LoRA（要训就用公有领域古版画，Wellcome Collection 可达）
