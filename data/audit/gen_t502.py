# -*- coding: utf-8 -*-
"""T502 每层主题一致性 → docs/design/layer_theme.md

方法：把每层的「层名 / 主池敌人(无 eco) / 副池敌人(带 eco) / 事件标题(通用池+维护者池+疯先知池)」
排在一起，逐层人工判读主题是否统一；跳脱点单独列。
层↔eco 对照：L1 surface / L2 cold / L3 arid / L4 sea / L5 vent / L6 rad / L7 core / L8 nexus。

用法：python data/audit/gen_t502.py
"""
import io, sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_common import GAME

OUT = GAME / 'docs' / 'design' / 'layer_theme.md'
RAW = json.load(open(GAME / 'data' / 'audit' / 'raw_all.json', encoding='utf-8'))

ECO = {1: 'eco_surface', 2: 'eco_cold', 3: 'eco_arid', 4: 'eco_sea',
       5: 'eco_vent', 6: 'eco_rad', 7: 'eco_core', 8: 'eco_nexus'}
LAYERS = {l['id']: l for l in RAW['layers']['layers']}

JUDGE = {
1: ('一致', '主题：被放弃的地表与「等待」。敌名（菌毯/软管/空服的壳）+ 事件（降落的旧舱/晒了五百年的水箱/坠轨的清单）都在讲同一件事：人类走了，留下的东西还在按流程运转。两个 boss（钟乳盐·塌落体 / 静默号·最后一次广播）分别是「地质继续」和「广播还在播」，双线都扣题。'),
2: ('基本一致，一处前置', '主题：冷洞矿道与前人的痕迹。主池是冷洞生物（鳗/蟹/青菌），副池是雪原痕迹（沉雪的苔背/历壁的蛀痕），事件一半是矿道遗物（碎石/矿灯/安全绳/更衣柜）。跳脱点：疯先知池「深海里的一盏灯」——「海」的主题要到第 4 层「稳定空洞海」才展开，这里是主题前置。'),
3: ('一致', '主题：干旱与水的政治。主池（洞蛇/肺鱼/蜗）+ 副池（滴水的账房/隐生的缓步）+ 事件（倒在旱地的井/会长字的墙/干死的通道）+ 疯先知池（灰藻歉收/历法之争投票）——「缺水」同时是生态题和文明题，两边都扣住。'),
4: ('一致', '主题：水下世界与渊民文明。主池全是水生生物（红腔鱼/滤食鱼群/银鱼），副池是藻毯，事件（渊民的埋骨布/涌喉的市集/旧城街灯/浮在光池上的信）全是渊民生活痕迹。层名「稳定空洞海」与全部素材零冲突，全游戏最齐的一层。'),
5: ('一致', '主题：热泉生态与旧光者工业。主池（管虫/螈/硫塔菌）+ 副池（看火者/喷发管虫）+ 事件（还在计时的高压锅/排班表白板/净化者圣火堆）——热泉是生态现场，白板和高压锅是它曾被人使用过的证据，双线扣题。'),
6: ('一致', '主题：辐射与「防它的人」。主池（合成菌/甲壳类/鳞鳄）+ 副池（重鳞拾壳者/低烧菌群）+ 事件（剂量表挂在走廊正中/没拆封的辐射药/一墙贴到天花板的剂量条）——「辐射」不只是环境伤害，事件在讲有人在这里防了很多年。'),
7: ('一致', '主题：核心高热区与旧光者的余音。主池（残影/蛇蜥/震杆菌）+ 副池（三色菌毯须/慢半拍的影）+ 事件（循环播放的告别/反着装修的宿舍/自我删除的日志/没有观众的演出）——事件密度偏「旧光者的私人生活」，敌人偏「它们变成的东西」，互为因果，不跳。'),
8: ('一致', '主题：不许关闭的核心。敌人（墟蛹/墟尘行像/空壳旧光者）与事件（不许关闭的告示/值班交接/签到处/八万年前的休息室）共同讲「设施还认为有人在上班」。层名「红渊核心」直接点题。'),
}

buf = io.StringIO()
buf.write('# T502 · 每层主题一致性\n\n')
buf.write('> 数据源：`data/audit/raw_all.json`（layers/enemies/anminEnemies/cngEnemies/events/anminEvents/cngEvents）。\n')
buf.write('> 方法：每层列出 层名 / 主池敌人（不带 eco）/ 副池敌人（带 eco）/ 事件标题（通用 82 + 维护者 10 + 疯先知 10），逐层判读。')
buf.write('判定为人工判读，素材列表与层↔eco 对照为脚本输出，可复算。\n\n')

buf.write('## 层 ↔ eco 对照\n\n| 层 | 层名 | eco |\n|---|---|---|\n')
for i in range(1, 9):
    buf.write('| %d | %s | %s |\n' % (i, LAYERS[i]['name'], ECO[i]))

for i in range(1, 9):
    main_e = [e['name'] for e in RAW['enemies'] if e['layer'] == i]
    sub_e = [e['name'] for e in RAW['enemies'] + RAW['anminEnemies'] + RAW['cngEnemies']
             if e['layer'] == i and e.get('eco') == ECO[i]]
    evs = ['%s（%s）' % (e['title'], p) for p, pool in
           [('通', 'events'), ('维', 'anminEvents'), ('疯', 'cngEvents')] for e in RAW[pool] if e['layer'] == i]
    verdict, note = JUDGE[i]
    buf.write('\n---\n\n## 第 %d 层 · %s —— 判定：%s\n\n' % (i, LAYERS[i]['name'], verdict))
    buf.write('- 主池敌人（%d）：%s\n' % (len(main_e), '、'.join(main_e) or '—'))
    buf.write('- 副池敌人（%d，eco=%s）：%s\n' % (len(sub_e), ECO[i], '、'.join(sub_e) or '—'))
    buf.write('- 事件（%d）：%s\n' % (len(evs), '、'.join(evs)))
    buf.write('- 判读：%s\n' % note)

buf.write('\n---\n\n## 主题跳脱清单（只有两处，都是小跳）\n\n')
buf.write('1. **cngevent_05「深海里的一盏灯」在第 2 层**：层是冷洞，「海」要到第 4 层才展开。可辩护为渊民遗迹本就来自海（第 4 层渊民文明），属于主题前置，不是错。\n')
buf.write('2. **cngenemy_01「浅海鳗」在第 1 层（疯先知池）**：同上，海的意象提前出现。疯先知池第 1 层还有「猎巫火堆的灰」「守夜换岗」，地表层里塞了一个文明侧的鱼——是全游戏最明显的一处层位与题材错位。\n')
buf.write('\n除以上两处外，8 层的层名/eco/敌人/事件四元组全部对得上；每层都是「主池=生物，副池=环境与人造物」的双线结构。\n')
buf.write('\n复算：`python data/audit/gen_t502.py`（素材清单自动生成；判定文字为人工判读）。\n')

OUT.write_text(buf.getvalue(), encoding='utf-8')
print('written', OUT)
