# -*- coding: utf-8 -*-
"""按项目原有规矩重排今晚任务：T81 起，一任务一份 tasks/T<n>.md。

为什么重写：之前生成的 NIGHT_TASKS_1102.md 是自创体例（N001…），
和项目里既有的 T* 队列、`tasks/queue.json`、`TASK_DONE.md` 的验收格式对不上，
早班接手的人得学两套。这里改成完全贴合原体例：

  任务书 → `# T<n> 标题` + 实测问题 / 目标 / 做法 / 禁止 / 验收表 / 交付
  完成记录 → `## T<n> 完成` + `- status: done` / `- output:` / `- check:` / `- notes:`
  队列 → `tasks/queue.json`（本次追加，旧条目保留）

用法：python tools/_gen_night_tasks_v2.py
"""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
GAME = Path(__file__).resolve().parents[1]
TASKS = GAME / 'tasks'
CAT = {r['id']: r for r in json.loads((GAME / 'data' / 'art_catalog.json').read_text(encoding='utf-8'))}
PROMPTS = {r['id']: r['prompt'] for r in json.loads((GAME / 'data' / 'zh_prompts_full.json').read_text(encoding='utf-8'))}
ART = GAME / 'web' / 'assets' / 'art'
SPLIT = '洞底是一整片深红的光'
START = 81          # 上一批做到 T80
IX = ('锈穿', '焊缝', '砸扁', '铆钉头')
XF = ('反复划过', '刮得发亮', '凹痕')


def sub(rid):
    return PROMPTS[rid].split(SPLIT)[0]


def chunks(seq, n):
    for i in range(0, len(seq), n):
        yield seq[i:i + n]


def main():
    ids = list(CAT)
    have = [i for i in ids if (ART / (i + '.webp')).exists()]
    rw = []
    for i in ids:
        k = i.split('_')[0]
        s = sub(i)
        if k in ('dive', 'trem') and not any(w in s for w in IX):
            rw.append(i)
        elif k == 'event' and not any(w in s for w in XF):
            rw.append(i)
        elif k in ('anm', 'cng') and any(w in s for w in ['编号', '标签', '刻度', '刻字', '铭文']):
            rw.append(i)
    cards = [i for i in have if i.startswith(('anm_', 'cng_', 'dive_', 'trem_'))]
    foes = [i for i in have if i.startswith('enemy_')]
    evts = [i for i in have if i.startswith('event_')]

    made = []

    def add(title, problem, goal, steps, forbid, accept, deliver):
        n = START + len(made)
        body = ['# T%d %s' % (n, title), '', '## 实测问题', problem, '', '## 目标', goal, '',
                '## 做法（按优先级）']
        body += ['%d. %s' % (i, s) for i, s in enumerate(steps, 1)]
        body += ['', '## 禁止', forbid, '', '## 验收', '| # | 指标 | 门槛 |', '|---|---|---|']
        body += ['| %d | %s | %s |' % (i, a, b) for i, (a, b) in enumerate(accept, 1)]
        body += ['', '## 交付', deliver, '']
        (TASKS / ('T%d.md' % n)).write_text('\n'.join(body), encoding='utf-8')
        made.append({'n': n, 'title': title, 'deliver': deliver})
        return n

    NO_TOUCH = ('不许改 `web/assets/art/` 里的成品图；不许删任何文件；'
                '要改先在旁边留一份 `.bak`。')

    # ---- A 图质检：每 10 张一份 ----
    for gi, grp in enumerate(chunks(have, 10), 1):
        add('图质检 第 %d 组（%d 张）' % (gi, len(grp)),
            '461 张素材已全部生成，但**没有一张经过逐张核查**。之前只有整张总览的目测，'
            '已知的翻车类型有：画出可读文字、画出屏幕与按钮、出现白画框、主体缩到画面边缘。',
            '本组 %d 张，每张给出 7 项判定 + 一句话主体描述，全部落盘成表格。' % len(grp),
            ['打开 `web/assets/art/<id>.webp` 逐张看，不要只看文件名猜',
             '每张判：① 有无可读文字 ② 有无现代电器外形 ③ 有无白画框 ④ 主体是否占中部三分之二 '
             '⑤ 是否明显偏绿/偏蓝 ⑥ 是否像纸/书/册 ⑦ 一句话说主体是什么',
             '不合格的，在表格最后加一列写「建议改法」（是重画，还是只改提示词）',
             '写完统计：本组不合格几个、各缺陷类型各几个'],
            NO_TOUCH,
            [('表格完整', '%d 行，一行不缺' % len(grp)),
             ('每行 7 项都有值', '不许留空、不许写「正常」敷衍'),
             ('末尾统计', '不合格数与缺陷分布对得上表格')],
            '`data/qa/QA_%03d.md`' % gi)

    # ---- B 提示词重写：每 5 条一份 ----
    for gi, grp in enumerate(chunks(rw, 5), 1):
        add('提示词重写 第 %d 组（%d 条）' % (gi, len(grp)),
            'dive/trem 段有 54 条、event 段有 59 条还没按新规则改过，'
            '仍带着「装置 / 设备 / 铭牌 / 编号」这类会把画面拉到现代工业品上的词。',
            '本组 %d 条，把主体段按规则重写，尾部光照段和画法段**原样保留**。' % len(grp),
            ['读 `data/zh_prompts_full.json` 里这些 id 的 `prompt`',
             '以 `洞底是一整片深红的光` 为界，只改前半段',
             '主体只写实物：厚铁皮铆成的方斗 / 铸成的铁管 / 铸成整块的铁盖板 / 粗陶罐 / 骨管 / 铁链挂钩',
             '必须写工艺痕迹：锈穿的洞、歪斜的焊缝、砸扁的边角、铆钉头、锈水淌地',
             '必须写镜头位置（贴地仰视 / 斜俯 / 斜侧），平面物体一律斜放',
             '事件卡把「牌子 / 告示」写成「一块被反复划过的铁面」',
             '80–140 字，一段，不分行'],
            '不许出现这些词：装置 设备 仪器 开关 仪表 面板 屏幕 机器 编号 标签 刻度 刻字 铭文 字。'
            '不许用字符串替换（会造病句），必须整段重写。',
            [('条数', '正好 %d 条，id 与清单一致' % len(grp)),
             ('禁用词', '0 命中（写完自己 grep 一遍）'),
             ('尾部未动', '与原文逐字相同'),
             ('字数', '每条 80–140 字')],
            '`data/rewrite/RW_%03d.json`（格式 `[{"id":"...","prompt":"<主体段>"}]`）' % gi)

    # ---- C 图鉴文案：每 10 条一份 ----
    for gi, grp in enumerate(chunks(have, 10), 1):
        add('图鉴文案 第 %d 组（%d 条）' % (gi, len(grp)),
            '`data/art_catalog.json` 里每条只有一行 `desc`，撑不起图鉴界面；'
            '而且没人写过「画面为什么是这样」。',
            '本组 %d 条，每条 120–180 字，三段：画面照实写 / 它在世界里的用途 / 为什么这样画。' % len(grp),
            ['先看 `web/assets/art/<id>.webp`，照实描述画面，不许凭 desc 编',
             '再查 `data/art_catalog.json` 的 name/desc 补来历',
             '第三段对世界规则：红光从地底升、万物把取食器官长在下侧、倒挂',
             '每条一节，标题 `## <id> <卡名>`'],
            '三段缺一不可。不许写成宣传语，语气要像记录。不许复制 desc 原句。',
            [('条数', '%d 条，id 一致' % len(grp)),
             ('字数', '每条 120–180 字'),
             ('三段齐全', '抽查 3 条，三段都在')],
            '`data/lore/LORE_%03d.md`' % gi)

    # ---- D 第二轮复检：每 10 张一份 ----
    for gi, grp in enumerate(chunks(have[:120], 10), 1):
        add('第二轮复检 第 %d 组（%d 张）' % (gi, len(grp)),
            '第一轮查的是「有没有违规物件」。还有三类问题第一轮查不出来：'
            '材质读不出来（一坨红）、被红光糊成平板、画面和卡名对不上。',
            '本组 %d 张，三项各打 1–5 分并给理由。' % len(grp),
            ['材质：看得出是铁、陶、骨，还是什么都没有',
             '厚度：有没有透视、有没有被糊成一块平板',
             '对题：卡名说的是不是画面画的',
             '三项都 ≤2 分的，标成「建议重画」'],
            '不许拿第一轮的结论抄过来，必须自己看。',
            [('条数', '%d 张' % len(grp)),
             ('每张三个分 + 三句理由', '缺一不可'),
             ('标出建议重画的', '与分数一致')],
            '`data/qa2/QA2_%03d.md`' % gi)

    # ---- E 文案三连 ----
    for gi, grp in enumerate(chunks(cards, 20), 1):
        add('卡面副标题 第 %d 组（%d 条）' % (gi, len(grp)),
            '卡面只有卡名和规则文本，缺一句副标题；`desc` 是说明不是味道。',
            '本组 %d 条，每条 20–35 字一句，冷、短、像记录。' % len(grp),
            ['读 name/desc 与图', '写一句往前推的话：写后果、写来源、写它对人做了什么',
             '不许和 desc 原句重复'],
            '不用感叹号堆砌，不写宣传口气。',
            [('条数', '%d 条' % len(grp)), ('长度', '每条 20–35 字')],
            '`data/copy/card_%03d.md`' % gi)
    for gi, grp in enumerate(chunks(foes, 20), 1):
        add('敌人战斗台词 第 %d 组（%d 条）' % (gi, len(grp)),
            '敌人图鉴缺一句「它出现时会说的话」，战斗里没有压迫感的文字钩子。',
            '本组 %d 条，一行一条 `id | 台词`，20–30 字。' % len(grp),
            ['读 name/desc', '写它对人说的话，不写旁白', '不带引号'],
            '不许写成中二台词，要冷。',
            [('条数', '%d 条' % len(grp)), ('格式', '每行都有 id | 台词')],
            '`data/copy/foe_%03d.md`' % gi)
    for gi, grp in enumerate(chunks(evts, 20), 1):
        add('事件开场句 第 %d 组（%d 条）' % (gi, len(grp)),
            '事件卡只有标题与选项，进入事件时缺一句落地的话。',
            '本组 %d 条，每条 25–40 字，一句话交代「你看见了什么」。' % len(grp),
            ['读 name/desc 与图', '写玩家第一眼看到的东西，不写心理活动'],
            '不许剧透选项结果。',
            [('条数', '%d 条' % len(grp)), ('长度', '每条 25–40 字')],
            '`data/copy/evt_%03d.md`' % gi)

    # ---- F 工具 ----
    tools_task = [
        ('art_qa.py', '批量图质检器：尺寸 / 红占比 / 亮度 / 冷色占比 / 是否近黑，输出 `data/qa_auto.json`。只出数字不做判断。'),
        ('prompt_lint.py', '提示词合规扫描：按规则 VIII/IX/X 的禁用词表逐条报命中，输出 `data/lint.json`。'),
        ('job_builder.py', '出图任务生成器：读 `data/rewrite/*.json` 与质检不合格 id，合成 `data/jobs_night.json`。'),
        ('artctl.py', '把 build_families / _make_jobs / wanx_gen / art_sync 串成一个入口，只做编排。'),
        ('qa_report.py', '把 `data/qa/*.md` 汇总成 `data/qa_report.md`：不合格数、缺陷分布、按卡组分布。'),
        ('lore_index.py', '把 `data/lore/*.md` 汇总成 `data/lore_index.json`。'),
        ('dup_finder.py', '461 张图的感知哈希，相似度 >0.9 的组输出到 `data/dups.json`。'),
        ('ART_PIPELINE.md', '把今晚所有脚本的用途、参数、产出写成 `docs/ART_PIPELINE.md`，后来的人只看这一页就能跑。'),
    ]
    for name, desc in tools_task:
        add('写 %s' % name,
            '今晚要反复做的是同一批操作（质检 → 判不合格 → 改提示词 → 重画 → 再质检），'
            '现在全靠一次性小脚本，每换一次人就重写一遍。',
            '把这一条流程固化成一个可复用脚本。%s' % desc,
            ['先读现有的同名或同类脚本，能复用就不重写',
             '命令行参数要给 --help，输出路径一律落在 `data/` 下',
             '写完自己先跑一次，把真实输出贴进 TASK_DONE 的 check 行'],
            '只读原始素材，不许改 `web/assets/art/`。不许复制别人的逻辑再改名字。',
            [('能跑通', '`python tools/<名字> --help` 有输出'),
             ('有真实产物', '对应输出文件存在且非空'),
             ('有 docstring', '文件头说明用途、参数、产出')],
            '`tools/%s`' % name if name.endswith('.py') else '`docs/ART_PIPELINE.md`')

    # ---- G 游戏本体剩余 ----
    for t in [27, 28, 29, 30, 31, 32, 33, 34, 68, 79, 81]:
        p = TASKS / ('T%d.md' % t)
        if p.exists():
            title = '补做 T%d（任务书已有）' % t
            problem = '`TASK_DONE.md` 里没有 T%d 的完成记录，但 `tasks/T%d.md` 存在。' % (t, t)
            steps = ['读 `tasks/T%d.md`，严格照做' % t, '做完跑 `node tools/check_web.js`', '把结果写进 `TASK_DONE.md`']
            deliver = '见 `tasks/T%d.md`' % t
        else:
            title = 'T%d（缺任务书，先补写）' % t
            problem = '`TASK_DONE.md` 里没有 T%d，且 `tasks/T%d.md` 不存在。' % (t, t)
            steps = ['先按游戏当前状态写一份任务书，格式照 `tasks/T80.md`',
                     '再照自己写的任务书做', '写进 `TASK_DONE.md` 时注明「任务书为本夜补写」']
            deliver = '`tasks/T%d.md` + 对应产出' % t
        add(title, problem,
            '把这一号补齐，让 T1–T%d 的序列没有洞。' % (START + len(made)),
            steps, NO_TOUCH,
            [('完成记录', '`TASK_DONE.md` 里有 `## T%d 完成`' % t),
             ('回归通过', '`node tools/check_web.js` 0 警告')],
            deliver)

    # ---- H 回归与健壮性 ----
    regress = [
        ('全量回归', '依次跑 check_web / test_engine / pack_check / sim，输出落 `data/regress/`，失败项逐个修完复跑。'),
        ('存档压力', '写 `tools/_save_stress.js`：连存/读 200 次、塞损坏 JSON、空存档读，验证不崩。'),
        ('小分辨率适配', '1024×640 / 1280×720 / 1920×1080 三档查布局溢出，产出 `docs/LAYOUT_AUDIT.md`。'),
        ('首屏体积', '统计 index.html 与首屏素材字节数，找 >200KB 的单项，产出 `docs/PERF.md`。'),
        ('异常路径', '列 20 个异常操作（连点/空手牌/0 血/满手牌/退出重进），逐个找处理代码，缺的记下。'),
    ]
    for name, desc in regress:
        add(name,
            'T 系列做了 80 个任务，但**没有一份今晚这种强度的整体回归记录**；'
            '人工改过 `web/index.html` 七处（见 `docs/HANDOFF_D2.md`），改完没跑全量。',
            desc,
            ['按顺序跑，每条输出都落盘，不许只看最后一行',
             '失败的先判断是代码问题还是数据问题，再动手',
             '修不好的写进交付文档的「未解决」一节'],
            '不许为了让它通过而放宽检查条件。', 
            [('有落盘', '输出文件存在'),
             ('失败项有结论', '修了 / 未解决，二选一，不许含糊')],
            '`data/regress/` 或 `docs/` 下对应文件')

    # ---- I 统计与分析 ----
    stats = [
        ('色调分布', '统计 461 张 R/G/B 均值与红占比分位，按卡组分开，产出 `data/stat_tone.json`。'),
        ('雷同分组', '按 dup_finder 结果列相似组，给「保留哪张、重画哪张」建议，产出 `docs/DUP_GROUPS.md`。'),
        ('母题标签', '给已按规则 IX 改过的提示词打母题标签（吊挂/半埋/斜靠/散落/链挂），产出 `data/motifs.json`。'),
        ('可辨识度', '敌人 113 张，画面主体与 desc 对照，判「一眼认出 / 要想想 / 认不出」，产出 `data/readability.md`。'),
        ('规则覆盖率', '统计规则 VIII/IX/X 的覆盖率，产出 `docs/RULE_COVERAGE.md`。'),
    ]
    for name, desc in stats:
        add(name,
            '美术这块的判断一直是「我觉得行」，没有数字。出事时说不清是这批图的问题还是判据的问题。',
            desc,
            ['能算的都写成脚本，数字要能复算',
             '结论不超过 5 行，数字全放表里'],
            '不许用「大约」「感觉」代替数字。',
            [('可复算', '别人跑同样脚本得同样数'),
             ('结论与数字一致', '抽查 1 条')],
            '`data/` 或 `docs/` 下对应文件')

    # ---- J 自繁殖 ----
    selfgen = [
        ('滚动检查 ①', '重算「待重写提示词」条数，与开工时对比，写 `data/rewrite_open.md`。'),
        ('滚动检查 ②', '重算「不合格图」条数，新增的追加进 `data/jobs_night.json`。'),
        ('自我扩写', '队列空了就从 `art_catalog.json` 挑 20 条还没复检两遍的，写成新的 T 任务追加进 `tasks/queue.json`。'),
        ('写夜班日志', '每做完 20 个任务，在 `docs/NIGHT_LOG_1102.md` 追加一节：做了哪些、发现什么、下一步。'),
        ('修自己造的坑', '回头看今晚写过的脚本：缺 docstring、缺错误处理、产物没落在 `data/` 的，补上。'),
    ]
    for name, desc in selfgen:
        add(name,
            '上次夜班的教训是**任务做完就空转**。队列一旦见底，必须能自己造出下一批。',
            desc,
            ['做完上面任一段的 10 个任务，就回来执行一次本段',
             '本段做完立刻回主线，不许停在这里'],
            '不许把「无任务可做」当结论。',
            [('有产物', '对应文件存在'),
             ('队列不空', '`tasks/queue.json` 里始终有未完成任务')],
            '见做法里的路径')

    # ---- 写 queue.json ----
    qpath = TASKS / 'queue.json'
    old = []
    if qpath.exists():
        try:
            old = json.loads(qpath.read_text(encoding='utf-8'))
        except Exception:
            old = []
    if isinstance(old, dict):
        old = old.get('queue', [])
    bak = qpath.with_suffix('.json.bak')
    if not bak.exists() and qpath.exists():
        bak.write_text(qpath.read_text(encoding='utf-8'), encoding='utf-8')
    done = [t['n'] for t in made]
    q = {'start': START, 'end': done[-1], 'count': len(made),
         'note': '2026-11-02 夜班批次，按顺序做；做完一个在 TASK_DONE.md 追加一节',
         'queue': [{'t': t['n'], 'title': t['title'], 'deliver': t['deliver']} for t in made],
         'prev': old}
    qpath.write_text(json.dumps(q, ensure_ascii=False, indent=1), encoding='utf-8')

    # ---- 开场白 ----
    opening = TASKS / 'NIGHT_OPENING_1102.txt'
    txt = (TASKS / 'NIGHT_OPENING.md').read_text(encoding='utf-8')
    txt = txt.replace('{{任务清单}}',
                      '`tasks/queue.json` 里 T%d–T%d，共 %d 个。从 T%d 开始按顺序做，不挑不跳。'
                      '每个任务书在 `tasks/T<n>.md`，验收标准写在任务书最后一节。'
                      % (START, done[-1], len(made), START))
    opening.write_text(txt, encoding='utf-8')

    print('生成 %d 份任务书：tasks/T%d.md … tasks/T%d.md' % (len(made), START, done[-1]))
    print('队列：tasks/queue.json（T%d–T%d）' % (START, done[-1]))
    print('开场白：tasks/NIGHT_OPENING_1102.txt')
    return 0


if __name__ == '__main__':
    sys.exit(main())
