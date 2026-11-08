import re
from pathlib import Path

# ---------- 1) ART_PROMPT_SPEC.md：加入两条核心世界规则 ----------
spec = Path('docs/ART_PROMPT_SPEC.md'); s = spec.read_text(encoding='utf-8')
insert = """
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
"""
s = s.replace('## 二、三层写法（一条 prompt = 三段拼起来）', insert + '\n## 二、三层写法（一条 prompt = 三段拼起来）')
spec.write_text(s, encoding='utf-8')

# ---------- 2) WORKBOOK：骨架与词库更新 ----------
wb = Path('docs/ART_PROMPT_WORKBOOK.md'); t = wb.read_text(encoding='utf-8')
t = t.replace("""### 1. 生物类敌人（动物形）
```
a <体型形容> <生物类属> that <异化标记 1>, <异化标记 2 可选>,
<关键肢体/器官 1>, <关键肢体/器官 2>, <姿态或动作>, <环境痕迹>
```
> 中文：**一只〈体型〉的〈属类〉，它的〈部位〉〈异化〉，〈关键肢体/器官〉，〈姿态〉，〈环境〉。**""",
"""### 1. 生物类敌人（动物形）
```
a <体型形容> <生物类属> that <异化标记 1>, <异化标记 2 可选>,
<关键肢体/器官>, hanging <姿态：倒挂在天花板/腹面朝上>, its feeding organs on the underside,
lit from below by a red glow, <环境痕迹>
```
> 中文：**一只〈体型〉的〈属类〉，它的〈部位〉〈异化〉，〈肢体/器官〉，倒挂在〈位置〉、取食器官朝下，
> 被下方的红光照着，〈环境〉。**
> ⚠ 生物类**必须**含倒吊/器官朝下 + 自下而上的红光，缺一即打回（规范 §一之二）。""")

t = t.replace("""**通用负面词**""", """**倒吊与红光的固定尾巴（附在风格段后面）**
```
hanging inverted or organs facing down, lit from below by a red glow
```
**通用负面词**""")

# 3) 样板改写 3 条（示范倒吊 + 底光）
t = t.replace("""> a crusted colony of thermophilic bacteria climbing a steel conduit, blistering orange-brown crust shot through with pale salt-veins (A1), steam curling off the surface, no eyes and no limbs — a growth, not an animal, seeping water at its foot""",
"""> a crusted colony of thermophilic bacteria hanging down from a ceiling pipe, its blistering orange-brown crust shot through with pale salt-veins (A1), feeding mouths clustered on its underside, steam curling downward, lit from below by a deep red glow, water seeping off its tips""")
t = t.replace("""**中文**：一丛爬在钢制管道上的嗜热菌落，橙褐色的硬壳上布满苍白的盐脉（A1），表面冒着热气；没有眼没有肢——它是"长出来的东西"，不是动物；脚边有渗出的水。""",
"""**中文**：一丛从顶上的管道**倒挂下来**的嗜热菌落，橙褐硬壳布满苍白盐脉（A1），**取食口聚在底面**，热气向下卷，**被下方深红的红光照着**，尖端渗着水。""")

t = t.replace("""> a heavy jumping spider crouched on wet stone, eight thick hairy legs, six small eyes ringed around two large ones (B1), abdomen marked with a pale skull-like mottle, silk anchor line trailing behind""",
"""> a heavy jumping spider clinging upside down to a wet ceiling, eight thick hairy legs hooked into the stone, six small eyes ringed around two large ones (B1), abdomen marked with a pale skull-like mottle, silk anchor line hanging down, lit from below by red light""")
t = t.replace("""**中文**：蹲在湿石上的粗壮跳蛛，八条毛腿，六只小眼环着两只大眼（B1），腹部有苍白的骷髅状斑纹，身后拖着丝。""",
"""**中文**：**倒挂在湿顶面上**的粗壮跳蛛，八条毛腿钩进石头，六只小眼环着两只大眼（B1），腹部有骷髅状斑纹，**丝线向下垂**，被下方红光照着。""")

t = t.replace("""> a body in an intact protective suit slumped against the rock wall, sitting on the ground with knees up, round glass faceplate with faint scratches on its inner side, dust on the shoulders, an empty corridor behind""",
"""> a body in an intact protective suit slumped against the rock wall, knees up, round glass faceplate with faint scratches on its inner side, dust on the shoulders, the corridor ahead washed in a red glow rising from the floor""")
wb.write_text(t, encoding='utf-8')

# ---------- 4) 校验器：新增两条硬规则 ----------
p = Path('tools/check_prompts.js'); j = p.read_text(encoding='utf-8')
j = j.replace("let fails = 0, warns = 0;",
"""const INVERT = /upside down|inverted|hanging|belly-up|organs? (?:on|towards?) the underside|feeding organs clustered on the underside|mouth opening downward|trailing downward/i;
const UNDERLIGHT = /lit from below|red glow rising|red glow from below|red haze rising|underlight/i;
let fails = 0, warns = 0;""")
j = j.replace("""  const nouns = (p.match(new RegExp(CONCRETE.source, 'gi')) || []).length;""",
"""  if (!UNDERLIGHT.test(p)) errs.push('缺"红光自下而上"');
  if ((kind === 'foe' || kind === 'card') && !INVERT.test(p)) errs.push('缺"倒吊/器官朝下"');
  const nouns = (p.match(new RegExp(CONCRETE.source, 'gi')) || []).length;""")
p.write_text(j, encoding='utf-8')
print('已写入：倒吊 + 红光两条核心规则（规范/手册/校验器）')
