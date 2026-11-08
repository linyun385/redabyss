from pathlib import Path
p = Path('docs/ART_PROMPT_SPEC.md'); s = p.read_text(encoding='utf-8')
add = """
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
"""
s = s.replace('## 二、三层写法（一条 prompt = 三段拼起来）', add + '\n## 二、三层写法（一条 prompt = 三段拼起来）')
p.write_text(s, encoding='utf-8')
print('规则 III（光的地底构图）已写入规范')
