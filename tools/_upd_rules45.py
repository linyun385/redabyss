from pathlib import Path
p = Path('docs/ART_PROMPT_SPEC.md'); s = p.read_text(encoding='utf-8')
add = """
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
"""
s = s.replace('## 二、三层写法（一条 prompt = 三段拼起来）', add + '\n## 二、三层写法（一条 prompt = 三段拼起来）')
p.write_text(s, encoding='utf-8')
print('规则 IV/V 已写入规范；A5 已拷入 art/_review/12')
