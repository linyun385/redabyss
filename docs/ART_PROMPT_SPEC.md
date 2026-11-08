# 提示词语言规范 v1（红渊 · 素材）

> 用途：把「对象名 + 设定 + 异化语言」翻成**可生成、可校验**的英文提示词。
> 这是给写提示词的人/模型看的规范，不是给玩家看的文案。
> 上游：`docs/ART_DIRECTION_V2.md`（三档抽象度 + 复用规则 R1–R6）；本文件只规定**措辞语言**。

## 一、写之前必须先读（不许跳）

| 文档 | 取什么 |
|---|---|
| `docs/GLOSSARY.md` | 专有名词的正确写法（相石、震髓、凝视、共鸣、渊民…）|
| `docs/LAYERS.md` + `layers/layers.json` | 八层环境规则（no_light/dim/dry/bright/heat_tick/rad_tick/burn_hand）|
| `docs/ECO_ENEMIES.md` / `ECO_EVENTS.md` / `ECO_RELIC_CARD.md` | 每个生态的"气味"，避免写出不属于该层的生物 |
| `docs/ENEMY_DESIGN.md` / `docs/ENDINGS.md` | 生物与结局的既有设定，不许与之矛盾 |
| 对象自身 `flavor` / `body` / `intent_pattern` | 提示词的语义锚点（必须呼应）|


## 一之二、两条核心世界规则（2026-11-01 用户口述，最高优先级）

> 「倒吊与红光」是这个世界的原点，比任何风格词都重要。**每条 prompt 都必须体现其中至少一条，
> 生物类必须两条都体现。**

### 规则 I：倒吊（器官朝下）
红光自地核向上穿透，所以这个生态里的生物与植物，**把"吃光/生长/生殖"的器官长在身体最下方**，
以更好地吸收红光；与生态绑定的生物出现时也倾向这种怪异姿态。

- 生物：**必须**倒挂/攀附天花板，或腹面朝上（器官朝下）
- 植物：叶、花、孢子囊朝下长（枝条下垂）
- 工具/物件：被使用者按"器官朝下"的逻辑改装（握把在下方、镜头朝下、刻度朝下）
- 建筑/事件：顶面上有抓痕、垂挂物、下悬的结构

**可复用英文语块（必选其一）**
```
hanging upside down from the ceiling | clinging inverted to the ceiling above the corridor
its feeding organs clustered on the underside, the armored back facing up
fronds trailing downward toward the light | belly-up, mouth opening downward
```

### 规则 II：红光自下而上
- 光源**在画面下方**，从下往上打：底光、逆光、阴影向上投
- 越往地底红光越浓，颜料越饱和（D1 几乎无红 → D8 几乎全红）

**可复用英文语块（必选其一）**
```
lit from below by a deep red glow, shadows thrown upward
a red haze rising from the floor, strongest at the bottom of the frame
```

### 按层级的红光浓度（写进每条的风格段）
| 层 | 红光 | 画面表现 |
|---|---|---|
| D1 | 几乎无 | 冷灰褐，仅在接缝里透一线暗红 |
| D2–D3 | 微弱 | 纸面偏冷，底部有薄薄一层玫红 |
| D4–D5 | 中等 | 底部明显红光晕，主体下缘被染红 |
| D6–D7 | 强 | 整体偏暖红，阴影里全是红 |
| D8 | 极强 | 近乎单色红调，只有黑与朱红 |


## 一之三、地底空间约束 + 反写实（2026-11-01 23:13 用户判定后新增）

> 判定的原话：「09 太写实了，太类似现实世界里会出现的东西」「两张都隐隐有一种在地表的感觉」
> 「**08 完全符合需求，而且很适配**」——08 = `art/_review/08_垂挂苔毯_v2.png`。

### 结论：08 是唯一过关的基准
拆开看它为什么成立：

| 要素 | 08 怎么做的 | 为什么成立 |
|---|---|---|
| 形态 | 一片**垂挂的伞状囊体**，伞盖朝下（取食口在底面） | 不是地球物种，无法与任何现实生物对照 |
| 光 | **地面红光把下半部染成朱红**，上半部仍是纸色 | 光从下往上，且强度足够改写颜色 |
| 空间 | 没有地平线、没有天空、没有山形岩壁；背景被黑暗与结构填满 | 读起来是"洞窟内部"，不是"户外" |
| 陪衬 | 画面里出现了**器物**（铁罐、支架） | 立刻给出"有人在这里生活过"的地底文明感 |
| 质感 | 密集竖纹 + 网点，像印刷版画 | 不是照片、不是素描 |

### 新硬规则（写进每条 prompt）

1. **禁止地表感**：不许出现天空、地平线、远山、岩壁外轮廓、日照阴影。
   背景必须被**洞窟内壁/黑暗/管道/水面/盐层**填满：
   ```
   no sky, no horizon, no distant landscape; the frame is filled by dark cavern interior
   ```
2. **禁止写实动物解剖**：不要写"八条毛腿、两只大眼睛"这种可对照地球物种的结构。
   生物形态写成**半具象的器官异形**（囊、伞、钩、须、孔、膜、腔）：
   ```
   a hanging structure of pale sacs, each opening downward | a ring of soft mouths under the rim
   ```
3. **必须给"器物痕迹"**（地底文明感）：罐、管、支架、梯、牌、铆钉、缝线，任选一处：
   ```
   a rusted iron canister standing beneath it | iron brackets bolted to the wall behind
   ```
4. **红光改写颜色**：越靠下的部分越红，不能只是"有一点红光"：
   ```
   a deep red glow rising from the floor, staining the lower half crimson
   ```
5. **顶面/岩壁不要写成斜坡或山形**：要么是垂直内壁，要么是看不见顶的黑暗。

### 按「非动物」重写（原"苔毯"这类集合名词）
```
❌ a dense pale moss colony（一片苔藓 —— 集合名词，模型画不出结构）
✅ a hanging structure of pale sacs, each opening downward, tendrils trailing to the floor
```


### 规则 III：光的地底构图（2026-11-01 23:36 用户判定后新增）

> 原话：「这张的另一个问题是光学上还是正常的光线，没有那种**地底透出来的光**营造的光学构图。」

**光不是"打亮"，是"从下往上穿透"**。画面必须按这个来构图：

| 要素 | 要求 | 英文语块 |
|---|---|---|
| 光源位置 | **在画面之外的下方**（地缝/地底），看不见灯 | `a single light source below the frame, out of sight` |
| 最亮处 | **底部/地面最亮**，往上越暗 | `the floor is the brightest area, the upper half falls into darkness` |
| 主体受光 | 主体**下缘被红边勾亮**（轮廓光），上部沉进暗里 | `the lower edges of the subject rimmed with red, its upper parts lost in shadow` |
| 投影方向 | 阴影**向上**投到顶上/墙上（与日常相反） | `shadows thrown upward onto the ceiling` |
| 主体读数 | 主体多为**剪影**，靠边缘光辨形 | `reads mostly as a silhouette` |

**必须禁止**（否则就是"正常光照"）：
```
flat studio lighting, front light, daylight, softbox, even illumination, light from above
```

**注意**：这条与"倒吊"叠加时最出效果 —— 主体倒挂、光从下方把它的下缘照亮、阴影投在上方顶面。


### 规则 IV：形态词必须用「实物类比名词」（2026-11-02 00:0x 实测后新增）

> 实测：`pale leathery sacs` + `rings of soft lips` → 模型画成**一块红布帘**；
> 换成 `leathery egg-pods` + `round mouths like the ends of cut hoses` + `claws like fishhooks`
> → 一次就画对了（`art/_review/12_垂挂蛋囊_a5.png`）。

| 失败写法 | 模型理解 | 换成 |
|---|---|---|
| `pale leathery sacs` | 布 | `leathery egg-pods, each the size of a fist` |
| `rings of soft lips` | 唇形装饰 | `round mouths like the ends of cut hoses` |
| `hooks of hardened chitin` | 挂钩 | `thick curved claws like fishhooks` |
| `a dense moss colony` | 绒毛团 | `a cluster of pale caps hanging downward` |
| `a translucent belly` | 玻璃 | `a belly you can see through, holding a smaller skeleton` |

**原则**：每个部位都要能对应到模型认识的**实物**（蛋、豆荚、水袋、软管口、鱼钩、灯罩、伞盖、绳结）。
写完自检一句：**"这个词，模型见过它的照片吗？"** 没有就换掉。

### 规则 V：光与背景靠正向描述压不住（实测）

A5 同时写了"光源在画外下方、地面最亮、阴影向上"，出来的仍是**正面光**；写了 `no sky, no horizon`，
右上仍留了一片灰色天光。结论：**光和背景优先级高于形态**时，纯文生图控制不住。
→ 走 **img2img（拿已过关的 08 当参考图，锁住纸感/配色/光/背景）**，或用更强底模。

## 二、三层写法（一条 prompt = 三段拼起来）

```
[对象段]  <它是什么 + 1–2 个异化标记>
[姿态段]  <在做什么 / 留下什么痕迹 / 处在什么环境>
[风格段]  STYLE_V3（固定后缀，见 §五）
```
- **对象段必须能独立成立**：把风格段删掉，读者仍知道画的是什么。
- **异化标记**是"红渊化"的关键：每条 prompt **至少 1 个、至多 2 个**，从下面三种里取：

| 码 | 语言 | 写法示例 |
|---|---|---|
| **A 材料替代** | 生物长出非生物材料 / 器官被物件替代 | `back split into overlapping salt-crystal plates`、`eyes replaced by glass beads`、`fins fused into copper fins` |
| **C 工艺寄生** | 身体被"维修过"：缝合、铆钉、接管、编号 | `stitched along the spine with wire`、`a brass valve screwed into its side`、`serial numbers cut into the shell` |
| **B 器官错位**（少量）| 数量/位置不对 | `six small eyes in a ring`、`a second smaller skeleton curled inside a translucent belly` |

**禁止**：纯克苏鲁式随机增殖（无规则触手、满屏眼球）、把生物写成"人穿皮套"。

## 三、每类的语言要求

| 类别 | 必须有 | 不许有 |
|---|---|---|
| 敌人（生物）| 可辨认的体型/肢体/器官 + 1 个异化标记 | 人类衣服、现代器物（手机/手表）、卡通比例 |
| 敌人（菌/苔/晶体等非动物）| 材质与扩散方式（覆、裂、渗出）| "怪物脸"、眼睛乱贴 |
| 卡牌（工具/物件）| 用途可读（握把/镜片/阀门/绳结）+ 磨损痕迹 | 说明书式小图、标注线、多个视角 |
| 事件 | 有人/物 + 正在发生的事 + 一处关键细节 | 纯风景、纯符号、抽象寓意 |
| BOSS / 结局 | 允许象征，但仍要有具体承载物（门、灯、机器、巨物）| 纯几何图形 |

## 四、反面清单（出现即打回）

1. `a symbol of X` / `abstract embodiment of X` / `minimal emblem` —— 抽象化
2. `a frog` / `a spider` / `a crab` —— 地球物种直译（必须带红渊化标记）
3. `pencil sketch` / `graphite` / `dense hatching` 作为**主体语言** —— 素描感
4. `study sheet` / `multiple views` / `diagram` / `callouts` / `annotations` —— 图鉴排版
5. 画面内文字：`text` / `letters` / `labels` / `signature` / `chart` —— 一律禁止
6. 与对象 `flavor` 无任何语义呼应（写完自检：这条画面能不能对应那句 flavor）

## 五、风格段（固定，不许改）

**A/B 档（生物、工具、事件）**
```
antique lithograph print, flat blocks of ochre yellow and soot grey, fine stipple shading,
deep ink contours, aged yellowed paper, single vermilion accent, one single subject,
single view, no pencil sketch, no diagram, no text
```
**C 档（BOSS / 结局）**
```
dark print, one glowing area, muted ochre palette with a single hot red accent,
grainy texture, one single subject, no text, no border
```
**通用负面词**
```
pencil sketch, graphite, charcoal, cartoon, anime, 3d render, photograph, earth animal,
dog, cat, horse, modern clothing, text, letters, glyphs, labels, signature, diagram,
callouts, inset, multiple views, border, frame, watermark, bright saturated colors
```

## 六、机械校验（脚本可判，写完必跑）

| # | 规则 | 判据 |
|---|---|---|
| 1 | 可画名词 ≥3 | 扫 prompt 里的具体名词/形容词（legs/plates/valve/stitched/…）|
| 2 | 无抽象词 | 命中 `symbol\|emblem\|abstract\|essence\|embodiment` = 0 |
| 3 | 无素描词 | 命中 `pencil\|graphite\|charcoal` = 0 |
| 4 | 无排版词 | 命中 `diagram\|callout\|inset\|multiple views` = 0 |
| 5 | 有异化标记 | A/C/B 关键词至少命中 1 |
| 6 | 呼应 flavor | 与对象 flavor 至少共享 1 个语义元素（人工抽检 10%）|
| 7 | 跨类不复用 | 同一 prompt 不服务两个类别 |
| 8 | 族内成员 ≤3 | 见 R2 |

## 七、样板（照这个手感写）

**敌人 · 洞穴两栖类**
> a cave amphibian whose back has split into overlapping salt-crystal plates, six small eyes
> set in a ring around a wide flat head, forelimbs fused into one broad pad with too many thin
> fingers, translucent belly showing a second smaller skeleton curled inside, sitting
> half-submerged in seepage water + STYLE

**卡牌 · 能量枪**
> an energy weapon grown rather than manufactured: barrel of pale bone fused to copper pipe,
> a glass organ along its side pulsing red, grip wrapped in dried sinew and stitched leather,
> pressure gauge replaced by a single small eye, resting on a scratched metal table + STYLE

**事件 · 穿防护服的遗体**
> a body in an intact protective suit slumped against the rock wall, sitting on the ground with
> knees up, round glass faceplate with small handwriting scratched on its inner side, dust on
> the shoulders, an empty corridor behind + STYLE

---

## VI. 万相实测：权重无效，主次靠散文（2026-11-02，11 张图实证）

> 这一节是**在百炼万相 `wanx2.1-t2i-turbo` 上跑出来的**，不是 SD 的经验。
> 采样脚本：`tools\_probe_weight.py` / `_probe_weight2.py` / `_probe_weight3.py`，产物在 `art\_probe\`。

### 一、权重语法 `(词:1.8)` —— 不解析，而且有害

**做法**：同一画面，主体与管道权重完全反向（`(菌落:3.0)/(管道:0.2)` 与 `(管道:3.0)/(菌落:0.2)`）。

**结果**：两张构图**没有跟着权重反**，反而双双画成「一张贴在黑底上的旧纸样张」，
其中一张右侧还冒出红色竖排印章式乱码——括号、冒号、数字被当成画面内容吃进去了。

**机制**：A1111 / ComfyUI 的 `(word:1.8)` 是**前端提示词解析器（Compel 之类）**的功能，
它在把字符串送进文本编码器之前调整 token 嵌入。API 模型没有这一层，
整串字符原样进编码器 → 括号数字成了纯噪声 token，还会把画面往「图纸／说明图／样张」上带。

**结论：万相上永远不写权重括号。中文提示词里的 `（）：` 一律按字面风险对待。**

### 二、`negative_prompt` —— 接口收，但不生效

要求画面有「深红光」，负面词写 `红色，红光，橙色，火焰，炭火，熔岩`：出图**照样大面积橙红**。
接口返回 200，不报错，**但它管不住**（cfg 极低或根本没走负面分支）。

**结论：不要靠负面词去压制。** 「不要天空」这种要求只能靠正向构图描述绕开（见规则 IV/V）。

### 三、`prompt_extend` 是双刃，且第一批的菌落变管道就是它干的

| 设置 | 表现 |
|---|---|
| 默认（`true`，改写器介入） | 风格稳，但**主体会被改写成泛化的洞穴/肉壁/管道** —— 第一批 `foe_zh_thermophile` 画成管道钟乳就是这个 |
| `false`（原样送） | 主体保得住，但**风格词容易被实体化**：把「古老的石版画，米黄做旧纸张」理解成「画面里有一张旧纸」 |

**结论**：用 `false`，但必须配合下面第四、五条改写法。

### 四、风格词必须写在**末尾**，且要写成「怎么画这幅画」

**错**（开头当主语）：`古老的石版画，米黄做旧纸张，细密排线……地底洞窟里，一个硬壳团块倒挂着……`
→ 模型把「一张旧纸」画成画面里的物体，主体悬空贴在一张纸上。

**对**（末尾当画法）：`……没有天空，没有地平线，没有文字。整幅画用石版画的方式绘制：细密排线，深墨轮廓，赭黄与烟灰色调，一点朱红，像米黄旧纸上的老印刷品。`
→ 风格是**绘制方式**，不是被画的对象。

### 五、主次要靠**散文**写，写位置和占比

这是权重唯一真正有效的替代品，且实测生效：

> 这个团块是画面的主体，占满画面中部，壳面布满苍白的盐脉，底面聚着一圈取食口器。
> 管道只是画面上方一条细细的边。

模型真的照做了：主体占中部大半，管道缩成顶上一条线。

**可用句式**（任选 1–2 句，别堆）：
- 「X 是画面的主体，占满画面中部／占画面四分之三」
- 「Y 只是画面上方一条细细的边／只在角落露出一角」
- 「画面里只有 X 和 Y 两样东西」 ← 比「不要画别的」有效

### 六、定稿模板（规则 I–VI 合并）

```
【场景与位置】地底……，一个<可数单体的实物类比名词>在……的（下方/里面/旁边）。
【主体与占比】这个<它>是画面的主体，占满画面中部，<2–3 个实物类比细节>。
【次要物】<另一个东西>只是画面上方一条细细的边。
【倒吊与红光】<取食/生殖器官>在它的底面朝下，地面是最亮处，它下缘被染成朱红，上部沉入黑暗，阴影投向岩顶。
【排除】没有天空，没有地平线，没有文字。
【画法】整幅画用石版画的方式绘制：细密排线，深墨轮廓，赭黄与烟灰色调，一点朱红，像米黄旧纸上的老印刷品。
```

**验收**：X1 / X3 按此模板连跑两次，两张都命中（主体、倒挂、底部器官、地底红光、版画质感全对）。

### 七、边界声明

- **已验**：本页所有结论都来自 `wanx2.1-t2i-turbo` 上 11 张实拍，非推断。
- **未验**：`wanx2.1-t2i-plus` / 更高档模型是否解析权重（没跑）。
- **未验**：「散文写占比」在**非生物类**卡面/事件上是否同样有效（只在敌人图鉴上验过 2 次）。
- **样本量小**：每格 1–2 张，命中率是方向性的，不是统计量。批量跑完前 20 张要用 `art_studio.py` 复核命中率。


---

## VII. 红光怎么真的变红（2026-11-02，R1–R4 五张实证）

**症状**：要求「深红光从下往上照」，出图却是暖橙光，被用户判为「差一步就能用」。

**根因**：风格尾巴里的 **「赭黄」被模型拿去染光了**。提示词里同时出现「赭黄」和「深红」时，
模型把赭黄分配给光，红只在最底下压成一条边。

**实测对照**（同一场景，只动光的写法和配色词）：

| 编号 | 改法 | 光的结果 |
|---|---|---|
| R1 | 明说「唯一光源」「红色是唯一彩色」，**保留赭黄** | 还是暖橙 |
| R2 | 赭黄**限定只给岩壁和纸**，光写「纯正血红」 | 变红 |
| R3 | **去掉赭黄**，改成「暗红的墨与冷灰阴影」 | 最红，但主体退化 |
| R4 | R2 的配色 + 主体压成暗橙褐 + 「没有白色高光」「背景留大片黑」 | 两张都红，可用 |

**定稿写法（直接抄这几句）**：

```
洞底是一层深红的光，从下往上照，光从<主体的底面>下方的地面升起。
<主体>的下缘通红，上部沉入黑暗，阴影投向岩顶。
<主体>只有暗橙褐与暗红，没有白色高光。背景留大片的黑。
```

风格尾巴改成：

```
整幅画用石版画的方式绘制：细密排线，深墨轮廓，赭黄与烟灰只用在岩壁和旧纸上，
画面的光全部是血红，红色是画面里最饱和的颜色，像米黄旧纸上的老印刷品。
```

**两条容易忘的**：
- **「背景留大片的黑」** 是红光能跳出来的前提。不写它，模型会把整幅画铺满暖色。
- **「没有白色高光」** 要写在主体那一段里，不能只放在末尾的排除句里。

### 已验 / 未验

- **已验**：上述写法在生物类敌人图上连跑 2 张都出红光（R4a / R4b）。
- **未验**：卡面物件（金属、纸、玻璃）上「光全部是血红」会不会把金属也染红到失去质感 —— 20 族批次里看。
- **未验**：`wanx2.1-t2i-plus` 是否同样需要这套限定。


---

## VIII. 不许写现实物种名 —— 拆成形体描述（2026-11-02，用户观察后立规）

**这条是用户看完成图总结出来的**，重要性高于前七条里的任何一条技法。

> 提示词里写现实里有的形象（蜘蛛、蜥蜴、鱼），模型会直接调现实参考、照着画；
> 换成没有现实对应物的形态描述，它才会自己造 —— 后者明显好得多。

对照很直观：敌人批次里评价最好的几张（带圆斑的卵状体、圆吸盘嘴的爬行体、背甲分节的节肢体）
**都没有现实对应物**；而「跳蛛」那张长出了卡通大眼、「光藓蠕虫」画成一条纯绿的虫，都是被物种名带偏的。

### 写法

| 不写 | 改写 |
|---|---|
| 蜘蛛 | 扁而宽、八条关节长腿向两侧张开、背覆短绒毛的节肢捕食者 |
| 鳗 | 细长无足、周身环节骨节的水生体，圆嘴里的齿环朝下 |
| 蟹 | 有横向硬甲和双钳的甲壳体 |
| 蜥蜴 | 四足、长尾、背覆鳞棘的爬行捕食者 |
| 鱼 | 身覆鳞、有鳍、眼在两侧的水生体 |
| 蜗牛 | 背着螺旋硬壳的软体 |
| 蕨 | 叶片卷曲、羽状分裂的丛生植物 |
| 苔藓 | 细密绒垫状的矮植物 |

**要写的是四件事**：几条腿或几个体节 / 体表什么质地 / 器官长在哪一侧 / 有没有壳。
只要这四件事写清，模型会自己造出一个「像那个东西但不是那个东西」的形体 —— 这正是要的效果。

### 两个坑

1. **别用字符串替换**。实测机械替换会造出病句：「细长无足…的水生体身覆鳞、有鳍…的水生体钩一样的爪」
   —— 鳗和鱼都被替成「水生体」，句子就烂了。必须**整段重写**。
2. **尾部也会残留**。光照段如果写着「鳗鱼的下缘被染成朱红」，重写主体段之后这句还在。
   重写时要同步把尾部的「X的」改成「它的」。

### 写法模板（重写后的样子）

```
地底洞窟里，一只扁而宽、八条关节长腿向两侧张开、背覆短绒毛的节肢捕食者倒挂在岩壁上。
这个节肢捕食者是画面的主体，占满画面中部，背甲分成三节、接缝里塞着盐粒，
前面一对前肢的末端是弯钩，钩尖上挂着干掉的黏膜。
岩壁上方是一条细细的黑缝。
```

### 已验 / 未验

- **已验**：重写后的主体段不再出现物种名，且保留了原有的细节密度（6 条抽样）。
- **未验**：去物种化之后成图的「可辨识度」会不会掉 —— 形态描述比物种名更难一眼认出，
  下一批图要用「3 秒内能不能认出这是什么」重新验一次。

