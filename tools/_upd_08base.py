from pathlib import Path
p = Path('docs/ART_PROMPT_SPEC.md'); s = p.read_text(encoding='utf-8')
add = """
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
"""
s = s.replace('## 二、三层写法（一条 prompt = 三段拼起来）', add + '\n## 二、三层写法（一条 prompt = 三段拼起来）')
p.write_text(s, encoding='utf-8')

h = Path('docs/HANDOFF_ART_20261101.md'); t = h.read_text(encoding='utf-8')
t = t.replace("""- v6 已跑完（21:20），结论：**A3 成立、B3 不成立**""",
"""- **用户判定（23:13）：09、10 都不过；08 完全过关，作为基准样本**
  - 09 失败原因：太写实，像现实世界的蜘蛛；两张都有"地表感"（岩壁像山坡、有天光）
  - 08 成功原因：垂挂伞囊（无法对应地球物种）+ 地面红光染红下半部 + 无地平线/天空 + 铁罐等器物陪衬
  - **基准图：`art/_review/08_垂挂苔毯_v2.png`**；规则写进 `ART_PROMPT_SPEC.md` §一之三
- v6（21:20）结论存档：A3 偏写实不通过、B3 变成绒毛钟乳不通过""")
h.write_text(t, encoding='utf-8')
print('规范与交接已更新：地底空间约束 + 反写实 + 08 基准')
