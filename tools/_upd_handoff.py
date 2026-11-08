import re
from pathlib import Path
p = Path('docs/HANDOFF_ART_20261101.md'); s = p.read_text(encoding='utf-8')
s = s.replace("""- v5/v6 两轮样张正在验证「倒吊 + 红光 + 纸感 + 岩壁背景」的组合：
  - `art/_samples_v5/A2_inverted_spider.png`、`B2_hanging_moss.png`（v2：倒吊成立但背景跑偏）
  - `art/_samples_v6/A3_inverted_spider.png`、`B3_hanging_moss.png`（v3：锁岩壁背景 + 禁道具，**尚未看到结果**）""",
"""- v6 已跑完（21:20），结论：**A3 成立、B3 不成立**
  - `art/_samples_v6/A3_inverted_spider.png`：岩壁背景锁住了、倒挂成立、红光偏朱、纸面颗粒在。
    仍有两处：①顶面读起来像"斜坡"而不是天花板，倒吊感靠腿撑；②嘴部/螯肢退化成一团黑。
  - `art/_samples_v6/B3_hanging_moss.png`：变成一团绒毛状钟乳，**没有生态结构**（丢了"群落"）。
  - 评审副本：`art/_review/09_倒挂跳蛛_v3.png`、`10_垂挂苔毯_v3.png`
- 定论：**岩壁背景 + 单主体 + 底光**这套组合对"有明确解剖结构的对象"有效（跳蛛）；
  对"没有固定形状的群体"（苔毯/菌落）失效 —— 这类需要改写成"具象的个体形态"再画
  （例：不是"一片苔毯"，而是"一株垂下来的苔，带伞状孢囊与根须"）。这条写进规范：
  **非动物类也必须给一个"可数的主体"**，不许用"一片/一丛/一层"这种集合名词。""")
p.write_text(s, encoding='utf-8')
print('交接文档已更新 v3 结论')
