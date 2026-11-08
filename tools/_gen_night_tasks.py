# -*- coding: utf-8 -*-
"""生成今晚（23:00–09:00）给 ZCode/GLM 的任务包。

为什么用脚本生成而不是手写：
  · 任务要落到**具体 id**上（做哪些图、改哪几条提示词），手写容易漏、容易和磁盘不符
  · 每条的输入/产出路径要真实存在或可创建
  · 断点续跑：已经产出过的分组自动跳过，重跑一次只补没做的

产出：
  tasks/NIGHT_TASKS_1102.md     任务清单（GLM 读这个）
  tasks/NIGHT_OPENING_1102.txt  开场白（用户粘贴进 ZCode）

用法：python tools/_gen_night_tasks.py
"""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
GAME = Path(__file__).resolve().parents[1]
CAT = {r['id']: r for r in json.loads((GAME / 'data' / 'art_catalog.json').read_text(encoding='utf-8'))}
PROMPTS = {r['id']: r['prompt'] for r in json.loads((GAME / 'data' / 'zh_prompts_full.json').read_text(encoding='utf-8'))}
ART = GAME / 'web' / 'assets' / 'art'
SPLIT = '洞底是一整片深红的光'

# 规则特征词：已按 IX 改过的段落带这些词
IX = ('锈穿', '焊缝', '砸扁', '铆钉头')
# 规则 X（事件版）特征
X = ('反复划过', '刮得发亮', '凹痕')
# 高风险词（提示词里出现就会拉到现实参照物）
BAD_WORDS = ['装置', '设备', '仪器', '开关', '仪表', '面板', '屏幕', '机器', '机械',
             '编号', '标签', '刻度', '刻字', '铭文', '玻璃', '纸', '册', '簿', '信',
             '牌', '告示', '标语']
SPECIES = ['管虫', '蜘蛛', '蜥蜴', '壁虎', '鳗', '鱼', '虫', '蕨', '苔', '菌']


def sub(rid):
    return PROMPTS[rid].split(SPLIT)[0]


def kind_of(rid):
    return rid.split('_')[0]


def chunks(seq, n):
    for i in range(0, len(seq), n):
        yield seq[i:i + n]


def main():
    ids = [r['id'] for r in json.loads((GAME / 'data' / 'art_catalog.json').read_text(encoding='utf-8'))]
    have = [i for i in ids if (ART / (i + '.webp')).exists()]
    missing = [i for i in ids if i not in have]

    # 待重写：dive/trem 未按 IX；event 未按 X
    rw = []
    for i in ids:
        k = kind_of(i)
        s = sub(i)
        if k in ('dive', 'trem') and not any(w in s for w in IX):
            rw.append(i)
        elif k == 'event' and not any(w in s for w in X):
            rw.append(i)
        elif k in ('anm', 'cng') and any(w in s for w in ['编号', '标签', '刻度', '刻字', '铭文', '玻璃瓶']):
            rw.append(i)

    # 高风险词命中清单（只报告，不自动改）
    risky = {i: [w for w in BAD_WORDS if w in sub(i)] for i in ids}
    risky = {i: w for i, w in risky.items() if w}

    lines = []
    A = lines.append
    A('# 今晚任务清单（2026-11-02 23:00 → 11-03 09:00）\n')
    A('> 共 %d 条。**做不完是正常的**，按顺序往下做，不要跳着挑简单的做。\n' % 0)  # 占位，最后回填
    A('工作目录：`C:\\Users\\Administrator\\Desktop\\杂七杂八\\红渊\\game`\n')
    A('## 现状（脚本从磁盘算出来的，不是估计）\n')
    A('| 项 | 数 |\n|---|---|')
    A('| 素材总数 | %d |' % len(ids))
    A('| 已有图 | %d |' % len(have))
    A('| 缺图 | %d |' % len(missing))
    A('| 待按规则重写的提示词 | %d |' % len(rw))
    A('| 提示词里仍有高风险词的条目 | %d |' % len(risky))
    A('')

    n = 0
    staged = []   # (编号, 标题, 正文行列表)

    def add(title, body):
        nonlocal n
        n += 1
        staged.append(('N%03d' % n, title, body))

    # ---- A 段：图质检，每 20 张一组 ----
    A('## A 段 · 逐张图质检（每 20 张一组，产出 Markdown 台账）\n')
    A('每组做法：对每组每张图，打开 `web/assets/art/<id>.webp` 看，逐条判：')
    A('① 画面里有没有可读文字；② 有没有现代电器外形（屏幕/按钮/收音机/音响）；')
    A('③ 有没有白画框或边框；④ 主体是否占画面中部三分之二；⑤ 有没有明显偏绿/偏蓝；')
    A('⑥ 像不像纸/书/册；⑦ 一句话说主体是什么。\n')
    A('产出：`data/qa/QA_<组号>.md`，表格一行一张，末尾写「本组不合格：id, id …」。\n')
    for gi, grp in enumerate(chunks(have, 10), 1):
        add('图质检 第 %02d 组（%d 张）' % (gi, len(grp)),
            ['输入：`web/assets/art/<id>.webp`', '产出：`data/qa/QA_%03d.md`' % gi,
             '本组 id：', '```', ' '.join(grp), '```'])
    A('（%d 组，见下方任务条目）\n' % gi)

    # ---- B 段：提示词重写 ----
    A('## B 段 · 待重写提示词（每 10 条一组）\n')
    A('规则（必须照做，不许自创）：')
    A('- 只改「主体段」（`洞底是一整片深红的光` 之前的部分），尾部光照/画法段原样保留')
    A('- 主体只能是：厚铁皮铆成的方斗 / 铸成的铁管 / 铸成整块的铁盖板 / 粗陶罐 / 骨管 / 铁链挂钩')
    A('- 必须写工艺痕迹：锈穿的洞、歪斜的焊缝、砸扁的边角、铆钉头、锈水淌地')
    A('- 不许出现：装置 设备 仪器 开关 仪表 面板 屏幕 机器 编号 标签 刻度 刻字 铭文 字')
    A('- 必须写镜头位置（贴地仰视 / 斜俯 / 斜侧），平面物体一律斜放')
    A('- 80–140 字，一段，不分行')
    A('- 事件卡额外要求：任何牌子/告示 → 写成「一块被反复划过的铁面」，画面里不出现可读的字')
    A('\n产出：`data/rewrite/RW_<组号>.json`，格式 `[{"id":"...","prompt":"<主体段>"}]`（只写主体段）\n')
    for gi, grp in enumerate(chunks(rw, 5), 1):
        add('重写提示词 第 %02d 组（%d 条）' % (gi, len(grp)),
            ['输入：`data/zh_prompts_full.json` 里这些 id 的 `prompt`',
             '产出：`data/rewrite/RW_%03d.json`' % gi,
             'id：', '```', ' '.join(grp), '```'])
    A('（%d 组）\n' % gi if rw else '（无待改条目）\n')

    # ---- C 段：高风险管理 ----
    A('## C 段 · 高风险词清理报告\n')
    A('把上面「提示词里仍有高风险词的条目」逐条读主体段，判断这个词是**真风险**还是误报'
      '（例如「铁片」里的片不算），产出 `data/risky_audit.md`：一条一行，写 id / 命中词 / 判定（改/不改）/ 理由。\n')
    for gi, grp in enumerate(chunks(list(risky), 30), 1):
        add('风险词审计 第 %02d 组（%d 条）' % (gi, len(grp)),
            ['产出：`data/risky_audit_%03d.md`' % gi, 'id：', '```', ' '.join(grp), '```'])
    A('（%d 组）\n' % gi if risky else '')

    # ---- D 段：图鉴文案 ----
    A('## D 段 · 图鉴文案（每 20 条一组，纯写作，最耗时间的一段）\n')
    A('每条写三段，共 120–180 字：')
    A('① 画面里实际画了什么（看 `web/assets/art/<id>.webp`，照实写，不许编）')
    A('② 它在这个世界里的用途/来历（查 `data/art_catalog.json` 的 name/desc）')
    A('③ 为什么这样画（对应世界规则：红光从地底升、万物倒挂、取食器官长在下侧）')
    A('\n产出：`data/lore/LORE_<组号>.md`，每条一节，标题 `## <id> <卡名>`\n')
    for gi, grp in enumerate(chunks(have, 10), 1):
        add('图鉴文案 第 %02d 组（%d 条）' % (gi, len(grp)),
            ['输入：图 + `data/art_catalog.json`', '产出：`data/lore/LORE_%03d.md`' % gi,
             'id：', '```', ' '.join(grp), '```'])
    A('（%d 组）\n' % gi)

    # ---- E 段：工具化 ----
    A('## E 段 · 工具化（写脚本，以后每晚都能复用）\n')
    E = [
        ('art_qa.py', '批量图质检器：`python tools/art_qa.py --dir web/assets/art --limit 20`，'
                      '输出每张图的尺寸/红占比/亮度/冷色占比/是否近黑，存 `data/qa_auto.json`。'
                      '不做主观判断，只做可复算的数字。'),
        ('prompt_lint.py', '提示词合规扫描：扫 `data/zh_prompts_full.json`，'
                           '按规则 VIII/IX/X 的禁用词表逐条报命中，输出 `data/lint.json` + 控制台摘要。'),
        ('job_builder.py', '出图任务生成器：读 `data/rewrite/*.json` + `data/qa/*.md` 里判不合格的 id，'
                           '合成 `data/jobs_night.json`（wanx_gen 能直接吃）。'),
        ('artctl.py', '把 build_families / _make_jobs / wanx_gen / art_sync 串成一个入口：'
                      '`python tools/artctl.py gen card --limit 30`。只做编排，不复制它们的逻辑。'),
        ('qa_report.py', '把 `data/qa/*.md` 汇总成一张总表 `data/qa_report.md`：'
                         '不合格总数、按缺陷类型分布、按卡组分布。'),
        ('lore_index.py', '把 `data/lore/*.md` 汇总成一个 `data/lore_index.json`（id → 文案）。'),
        ('dup_finder.py', '图重复度：对 461 张算感知哈希，输出相似度 >0.9 的组到 `data/dups.json`。'),
        ('art/*.md 索引', '写 `docs/ART_PIPELINE.md`：把今晚所有脚本的用途、参数、产出写清楚，'
                          '要求后来的人只看这一页就能跑。'),
    ]
    for name, desc in E:
        add('写 `tools/%s`' % name, ['要求：%s' % desc,
                                    '约束：只读不写原始素材；输出到 `data/` 或 `docs/`',
                                    '验收：能跑通，产物真实落盘'])

    # ---- F 段：游戏本体 ----
    A('## F 段 · 游戏本体（T 系列剩下的）\n')
    for t in ['T27', 'T28', 'T29', 'T30', 'T31', 'T32', 'T33', 'T34', 'T68', 'T79', 'T81']:
        p = GAME / 'tasks' / ('%s.md' % t)
        if p.exists():
            add('%s：读 `tasks/%s.md` 并严格照做' % (t, t),
                ['做完跑 `node tools/check_web.js`，通过后写进 `TASK_DONE.md`'])
        else:
            add('%s：先补任务书再做' % t,
                ['`tasks/%s.md` 不存在。先按游戏当前状态写一份任务书，再照做，'
                 '写进 `TASK_DONE.md` 时注明「任务书为本夜补写」' % t])
    A('（11 条）\n')

    # ---- G 段：回归与健壮性 ----
    A('## G 段 · 回归与健壮性\n')
    G = [
        ('全量回归', '依次跑 `node tools/check_web.js` / `node tools/test_engine.js` / '
                    '`node tools/pack_check.js all` / `node tools/sim.js --class diver --runs 300`，'
                    '把每条的输出落盘到 `data/regress/`，失败的**逐个修**，修完复跑。'),
        ('存档健壮性', '写 `tools/_save_stress.js`：连续存/读 200 次、在中途塞入损坏 JSON、'
                      '在空存档上读，验证不崩且有兜底。产出 `data/regress/save.md`。'),
        ('小分辨率适配', '把 `web/index.html` 在 1024×640 / 1280×720 / 1920×1080 三档下检查布局'
                        '（可用 `tools/check_web.js` 的现有能力，或写一个纯文本断点审查），'
                        '产出 `docs/LAYOUT_AUDIT.md` 列出会溢出的元素。'),
        ('首屏体积', '统计 `web/index.html` + 首屏必需素材的字节数，找出 >200KB 的单项，'
                    '产出 `docs/PERF.md` 并给三条可行优化（不必实施）。'),
        ('异常路径', '列出玩家可能触发的 20 个异常操作（连点、空手牌、0 血、满手牌、退出重进…），'
                    '逐个在 `web/index.html` 里找对应处理，缺的记下来，产出 `docs/EDGE_CASES.md`。'),
    ]
    for name, desc in G:
        add(name, ['要求：%s' % desc, '产出必须落盘，不许只在对话里说'])

    # ---- H 段：统计与分析 ----
    A('## H 段 · 统计与分析（把主观判断变成数字）\n')
    H = [
        ('色调分布', '统计 461 张的 R/G/B 均值与红占比分位数，产出 `data/stat_tone.json` + 一段结论'
                    '（哪一段偏暗/偏暖，按 anm/cng/dive/trem/event/enemy 分组）。'),
        ('雷同分组', '用 `tools/dup_finder.py` 的结果，把相似度高的图按组列出，'
                    '产出 `docs/DUP_GROUPS.md`，并给「哪一张保留、哪几张要重画」的建议。'),
        ('母题标签', '给 112 条已按规则 IX 改过的提示词打母题标签（吊挂/半埋/斜靠/散落/悬挂链），'
                    '产出 `data/motifs.json`，并统计分布是否失衡。'),
        ('可辨识度', '对敌人 113 张，把画面主体与 `desc` 的一句话做对照，'
                    '逐条判「一眼能认出 / 要想想 / 认不出」，产出 `data/readability.md`。'),
        ('规则覆盖率', '统计 461 条提示词里，符合规则 VIII（无物种名）/IX（工艺痕迹）/X（无文字）的比例，'
                      '产出 `docs/RULE_COVERAGE.md`。'),
    ]
    for name, desc in H:
        add(name, ['要求：%s' % desc, '数字必须可复算，脚本一起交'])

    # ---- I 段：文案（纯写作，量最大） ----
    A('## I 段 · 文案（纯写作，这一段最容易耗时间）\n')
    A('为什么写：游戏里卡面要一句副标题、敌人图鉴要一句战斗台词、事件卡要一句开场句。')
    A('现在 `desc` 只有一行，太单薄。\n')
    A('统一要求：每条 20–35 字，一句，不分行，不用感叹号堆砌，语气要冷、像记录不像宣传。')
    A('不许和 `desc` 原文重复，要往前推一步（写后果、写来源、写它对人做了什么）。\n')
    cards = [i for i in have if i.startswith(('anm_', 'cng_', 'dive_', 'trem_'))]
    foes = [i for i in have if i.startswith('enemy_')]
    evts = [i for i in have if i.startswith('event_')]
    for gi, grp in enumerate(chunks(cards, 20), 1):
        add('卡面副标题 第 %02d 组（%d 条）' % (gi, len(grp)),
            ['输入：`data/art_catalog.json` 的 name/desc + 图', '产出：`data/copy/card_%03d.md`' % gi,
             'id：', '```', ' '.join(grp), '```'])
    for gi, grp in enumerate(chunks(foes, 20), 1):
        add('敌人战斗台词 第 %02d 组（%d 条）' % (gi, len(grp)),
            ['输入：`data/art_catalog.json` 的 name/desc',
             '产出：`data/copy/foe_%03d.md`（一行一条：`<id> | <台词>`）' % gi,
             'id：', '```', ' '.join(grp), '```'])
    for gi, grp in enumerate(chunks(evts, 20), 1):
        add('事件开场句 第 %02d 组（%d 条）' % (gi, len(grp)),
            ['输入：`data/art_catalog.json` 的 name/desc', '产出：`data/copy/evt_%03d.md`' % gi,
             'id：', '```', ' '.join(grp), '```'])
    A('（卡牌 %d 组 / 敌人 %d 组 / 事件 %d 组）\n'
      % (len(list(chunks(cards, 20))), len(list(chunks(foes, 20))), len(list(chunks(evts, 20)))))

    # ---- J 段：第二轮交叉复检 ----
    A('## J 段 · 第二轮复检（换一套判据，专挑第一轮放过的）\n')
    A('第一轮看的是「有没有违规物件」。这一轮看三件第一轮不看的事：')
    A('① 材质读得出来吗（是铁、是陶、是骨，还是「一坨红色」）；')
    A('② 厚度与透视对不对（有没有被红光糊成一块平板）；')
    A('③ 和卡名对不对得上（名字说的和画面画的是不是冤家）。')
    A('每条给 1–5 分 + 一句理由。产出：`data/qa2/QA2_<组号>.md`\n')
    for gi, grp in enumerate(chunks(have[:120], 10), 1):
        add('第二轮复检 第 %02d 组（%d 张）' % (gi, len(grp)),
            ['输入：`web/assets/art/<id>.webp` + `data/art_catalog.json`',
             '产出：`data/qa2/QA2_%03d.md`' % gi, 'id：', '```', ' '.join(grp), '```'])
    A('（%d 组，先做前 120 张；做完再按「自我扩写」往后扩）\n' % gi)

    # ---- K 段：自繁殖层（保证做不完） ----
    A('## I 段 · 自繁殖（这一段最重要，永远不许空转）\n')
    A('做完上面任何一段的 10 条，就回到这一段做一次「滚动检查」，然后再回去继续。\n')
    I = [
        ('滚动检查 ①', '重算一次「待重写提示词」条数（用 `tools/prompt_lint.py`），'
                      '如果比开工时少了，说明改写有效，把新清单写到 `data/rewrite_open.md`。'),
        ('滚动检查 ②', '重算一次「不合格图」条数（用 `tools/qa_report.py`），'
                      '并把新增的不合格 id 追加进 `data/jobs_night.json` 待跑队列。'),
        ('自我扩写', '如果 `data/rewrite_open.md` 或 `data/jobs_night.json` 空了，'
                    '就自己从 `data/art_catalog.json` 里挑 20 条**还没被质检两遍**的，'
                    '追加成新任务，编号接着上次往下排，写进 `tasks/NIGHT_EXTRA.md`。'),
        ('写夜班日志', '每做完 20 条，在 `docs/NIGHT_LOG_1102.md` 追加一节：'
                      '做了哪几条、发现什么、下一步打算做什么。**这一条是给早上验收的人看的，必须写。**'),
        ('修自己造的坑', '回头看今晚自己写过的脚本，凡是没写 docstring、没有错误处理、'
                        '或者输出路径不在 `data/` 下的，补上。'),
        ('再扩写一条', '重复「自我扩写」：再造 20 条与你今晚做过的事不重复的任务，追加到 `tasks/NIGHT_EXTRA.md`。'),
    ]
    for name, desc in I:
        add(name, ['要求：%s' % desc])

    # ---- 回填总数 ----
    lines[2] = ('> 共 %d 条。**做不完是正常的**，按顺序往下做，不要跳着挑简单的做。\n' % n)

    body = []
    for num, title, bl in staged:
        body.append('### %s %s' % (num, title))
        for x in bl:
            body.append(x)
        body.append('')
    out = GAME / 'tasks' / 'NIGHT_TASKS_1102.md'
    out.write_text('\n'.join(lines + ['## 任务条目\n'] + body), encoding='utf-8')

    # ---- 开场白 ----
    opening = (GAME / 'tasks' / 'NIGHT_OPENING.md').read_text(encoding='utf-8')
    taskline = ('`tasks/NIGHT_TASKS_1102.md` 里 N001–N%03d 共 %d 条，从 N001 开始，按顺序做，'
                '不挑不跳。每条都有输入/产出路径，照着写。' % (n, n))
    opening = opening.replace('{{任务清单}}', taskline)
    (GAME / 'tasks' / 'NIGHT_OPENING_1102.txt').write_text(opening, encoding='utf-8')

    print('任务 %d 条 → tasks/NIGHT_TASKS_1102.md' % n)
    print('开场白 → tasks/NIGHT_OPENING_1102.txt')
    print('质检组 %d / 重写组 %d / 风险组 %d / 图鉴组 %d'
          % (len(list(chunks(have, 10))), len(list(chunks(rw, 5))) if rw else 0,
             len(list(chunks(list(risky), 30))) if risky else 0, len(list(chunks(have, 10)))))
    return 0


if __name__ == '__main__':
    sys.exit(main())
