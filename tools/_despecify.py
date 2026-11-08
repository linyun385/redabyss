# -*- coding: utf-8 -*-
"""规则 VIII：提示词里禁用现实物种名词，改写成形态描述。

依据（用户 2026-11-02 观察）：提示词写现实里有的形象（蜘蛛、蜥蜴、鱼），
模型会直接调现实参考、画得太"像那个东西"；写没有现实对应物的形态描述，
模型才会自己造，效果明显更好。

用法：python tools/_despecify.py [--apply]
只替换名词本身，保留量词与句式。替换表在 DESC 里，可随时加。
"""
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
GAME = Path(__file__).resolve().parents[1]
P = GAME / 'data' / 'zh_prompts_full.json'

# 现实物种/常见物象  →  形态描述（避免出现现实对应物）
DESC = [
    ('蜘蛛', '有多条关节长腿和细密绒毛的节肢捕食者'),
    ('跳蛛', '有多条关节长腿和细密绒毛的节肢捕食者'),
    ('螨', '扁而多足、背甲带横纹的微小节肢食腐者'),
    ('甲虫', '背覆硬鞘翅的六足椭圆体'),
    ('蚂蚁', '分节、六足、带头角的小型节肢体'),
    ('蝎', '有分节尾与末端钩的节肢体'),
    ('蜈蚣', '身体分成许多环、每环一对短足的细长节肢体'),
    ('蟹', '有横向硬甲和双钳的甲壳体'),
    ('虾', '半透明分节甲壳、多对细足的体'),
    ('蛇', '无足、细长、覆鳞的盘曲体'),
    ('蜥蜴', '四足、长尾、背覆鳞棘的爬行捕食者'),
    ('螈', '皮肤湿黏、四足短尾的两栖捕食者'),
    ('蛙', '皮肤湿滑、后腿粗壮的四足跳跃体'),
    ('蟾', '皮厚多疣、四肢粗短的四足体'),
    ('鱼', '身覆鳞、有鳍、眼在两侧的水生体'),
    ('鳗', '细长无足、周身环节骨节的水生体'),
    ('水母', '半透明伞状、拖着一圈长须的漂浮体'),
    ('海葵', '下端固定、顶上一圈触手张开的软体'),
    ('珊瑚', '分叉的硬骨质团块'),
    ('蝠', '有膜翼、倒挂着休息的飞体'),
    ('鸟', '有喙和羽的飞体'),
    ('鼠', '短毛、尖吻、长尾的小型哺乳体'),
    ('兔', '耳长、后腿粗壮的小型哺乳体'),
    ('猫', '四足、掌有肉垫的小型猎食体'),
    ('犬', '四足、吻长、耳立的猎食体'),
    ('蠕虫', '环节、无足、细长的软体'),
    ('蛭', '两端有吸盘、环节柔软的细长体'),
    ('蜗牛', '背着螺旋硬壳的软体'),
    ('蛞蝓', '无壳、湿滑、身体扁长的软体'),
    ('蘑菇', '有柄有伞、底面排着薄褶的菌体'),
    ('真菌', '由菌丝和伞状菌盖组成的菌体'),
    ('苔藓', '细密绒垫状的矮植物'),
    ('蕨', '叶片卷曲、羽状分裂的丛生植物'),
    ('藤', '缠绕、有节、垂挂的细长植物'),
    ('草', '细长叶片成丛的矮植物'),
    ('树', '有木质主干和分叉枝条的植物'),
    ('眼珠', '圆而湿亮的球体'),
    ('人形', '直立的双足轮廓'),
]

# 替换后可能出现的病句修补
FIXUPS = [('这只有多条关节长腿和细密绒毛的节肢捕食者是画面的主体', '这个多足节肢捕食者是画面的主体')]


def main():
    apply = '--apply' in sys.argv
    rows = json.loads(P.read_text(encoding='utf-8'))
    total = 0
    touched = []
    for r in rows:
        p = r['prompt']
        n = 0
        for old, new in DESC:
            if old in p:
                n += p.count(old)
                p = p.replace(old, new)
        for a, b in FIXUPS:
            p = p.replace(a, b)
        if n:
            r['prompt'] = p
            touched.append((r['id'], r.get('name', ''), n))
            total += n
    print('命中 %d 条，共替换 %d 处' % (len(touched), total))
    for t in touched[:10]:
        print('  - %-14s %-12s %d 处' % t)
    if touched:
        ex = next(x for x in rows if x['id'] == touched[0][0])
        i = ex['prompt'].find('洞底是一整片')
        print('\n样例：', ex['prompt'][:i if i > 0 else 160])
    if apply:
        P.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding='utf-8')
        print('\n已写入', P.name)
    else:
        print('\n(演练；加 --apply 才写)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
