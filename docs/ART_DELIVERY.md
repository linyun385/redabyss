# ART_DELIVERY.md — 素材交付说明（T67/T69）

> 素材清单：`tools/art_manifest.json`（79 条：48 卡面 B / 24 敌人 B / 4 立绘 C / 3 结局 A）。
> 生成：`tools/gen_art_batch.py`（断点续跑、失败重试 1 次、耗时与显存落盘 `tools/art_run.json`）。
> 版权闸门：`tools/art_similarity.py`（dHash vs 43 张参考图只读比对，汉明 ≤6 弃用重出）。
> 嵌入：`tools/art_embed.py`（长边 ≤512 降采样 + 类型体积帽 → base64 data URI → `web/index.html` 的 `window.ART` 常量表，幂等重跑即刷新）。

## 1. 接入方式（T67）

| 消费点 | 查表 key 派生 | 回落 |
|---|---|---|
| 卡面图案区 `appendArt` | 主脉→生态 face（光→sea/水→arid/热→vent/震→cold/料→rad）；素卡按职业语域（diver/anmin→surface，tremor/cangmin→nexus）；id 哈希选 6 张中的 1 张 | 脉色渐变符号（T50 方案原样） |
| 敌人图案区 `.eart` | layer→母本生态 foe（3 张取 1，id 哈希） | 剪影 symbol（T50 方案原样） |
| 职业立绘 `.portrait` | `class_<id>` 四张 | 首字符号 |
| 结局插画 `.ending-art` | `end_ending_<id>`（turned 复用 walked 画面） | 无图（纯文字） |

- 遗物图标**不用生图**：维持 T50 的内联 SVG 几何徽记（任务书授权）。
- 查不到 key（图未生成/未嵌入）时一律静默回落符号——新图逐步补齐不影响可玩性。
- data URI 经 `style.backgroundImage` 注入，**不产生 `<img>`、不产生 http 外链**（check_web 现行规则允许 `data:`，继续拦 `http(s)`，见 §3）。

## 2. 体积表（T67 时点，10 张样张嵌入）

| 项 | 数值 |
|---|---|
| index.html 总大小 | ~955 KB（接入前 ~528 KB，**素材增量 ≈ 418 KB**，预算 ≤1.6MB ✓） |
| 单图最大 | class_cangmin 45.7 KB（帽 60）|
| 单图最小 | class_anmin 22.4 KB |
| 类型帽 | 卡面 30 / 敌人 20 / 立绘 60 / 结局 120 KB——超帽逐级降 quality（82→78）→ 降尺寸（512→448→384→341→320→300） |
| 全量 79 张预估 | 按样张外推 base64 ≈ 2.4MB——**超 1.6MB 预算**，因此 T69 全量生成后按 §4 的降档规则压（卡面/敌人长边 512、flat 风格 webp 实测 8–20KB/张，全量预计 ≈1.3–1.6MB，嵌入时以 `art_embed_report.json` 实测为准，超了先降尺寸不降检查器） |

明细：`tools/art_embed_report.json`（每张 kb/帽/edge/q）。

## 3. 检查器改动（T67）与「它仍然会红」的证据

`tools/check_web.js` 两处修订（理由写在脚本注释里）：
1. **图片规则**：`<img>` 仍禁；`background-image:url(...)` 仅放行 `url(data:...)`，http(s)/相对路径 FAIL。
2. **网络规则新增**：任何 `http(s)://….png/jpg/webp/gif/svg` 的引用（含 JS 字符串）FAIL——素材内联后想从代码里塞外链图也会被拦。
3. **占位检测精度修正**：ART 表的 base64 数据体排除在「xxx 三连」占位扫描外（base64 随机串概率性含 xxx，~500KB 必现 1–2 次；目标是人工占位文字，不是数据）。

**仍然会红的证据**（注入 `background-image:url(https://evil.example.com/art.webp)` + `<img src=https://…>` 后实跑）：
```
FAIL  发现外部依赖：CSS 远程资源（必须自包含）
FAIL  发现外部依赖：外链素材引用（http 图片）（必须自包含）
FAIL  发现 <img> 标签（素材必须走 CSS background 内联）
```
还原后恢复全绿。**放宽的只有「data: 内联」一种形态；外链拦截比改前更严（多一条专用规则）。**

## 4. 如何替换单张图

1. 重生成/替换 `art/<out>` 对应的 webp（用 manifest 里的 seed 或换 seed）。
2. `python tools/art_embed.py`——幂等刷新 ART 表（只动嵌入块，别的块不动）。
3. `python tools/art_similarity.py` 复跑闸门（≤6 命中就换 seed）。
4. `node tools/check_web.js` 确认体积与自包含。

## 5. 主题兼容

素材图本身是黑底（B）或米白（C）语言，与三主题的关系：off/B 主题卡面本来就是深/纸双色，图案区图直接融合；C 主题纸面上 B 语言黑底图案区是「贴纸」效果（对照 REF 的 C 组横排合集里黑底小图嵌米白卡的做法，属参考风格内）。三主题战斗截图：`docs/artstyle/preview/final_off.png / final_B.png / final_C.png`。
