# -*- coding: utf-8 -*-
"""W4 遗物来历（夜班版）→ docs/design/relic_lore_night.md
任务书（自拟）：107 件遗物各一段 ≤60 字来历，角度=「它被谁用了多久」——使用痕迹叙事（区别于 F6 的审计口径）。
生成引擎从 mod 字段 / effect_code / 层 / 稀有度 推出身世类型，按类型配叙事模板。
boss 3 件、rare 带 mod 的 5 件手写校准。
"""
import io, sys, json, random
from pathlib import Path
GAME = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(GAME / 'data' / 'audit'))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


OUT = GAME / 'docs' / 'design' / 'relic_lore_night.md'
random.seed(42)

raw = json.loads((GAME / 'data/audit/raw_all.json').read_text(encoding='utf-8'))
CN_R = {'common': '普通', 'uncommon': '精良', 'rare': '稀有', 'boss': 'boss'}
CN_POOL = {'relics': '通用', 'anminRelics': '维护者', 'cngRelics': '疯先知'}

# 手写校准（稀有/boss/有 mod 且叙事特别的）
HAND = {
 'relic_20': '瓶塞上的牙印属于某个试过打开它的人。蜡封完好的意思是：没人成功。你的凝视在瓶里积了几十年——它知道怎么不让你看见。',
 'relic_27': '圣火烧到只剩底座就灭了。底座的温度维持了一千三百年——不升不降，刚好是「不灭」的定义。',
 'relic_34': '晶簇的两条主枝各指一个方向。它在你身上选了第三个方向——在你醒来之后才长出来的那面。',
 'relic_35': '回程票的孔位有人打过。打孔的人把票反着插进验票口——机器认了。回程的方向是上。没有人从上面下来过。',
 'relic_55': '结打在两块布之间。两块布各自裹过一个人。结替你扛住的部分，是两个人都没来得及说的那句话的重量。',
 'relic_62': '帝星线的尾部系在石头缝里。线的另一头不在视野内，但拉力恒定——你一直朝着它走，只是没有量过角度。',
 'relic_77': '泉权的账戳盖在水票上。印泥是红色岩浆冷却后磨的。盖章那天，干旱带的雨表改了一次数值。',
 'relic_28': '批文正文被划掉了。划掉之后盖了一个章——章上的字比原文有效。效力来源不详，规程也认。',
 'anrelic_01': '三级权限卡覆盖三号避难所全部常用门。全部常用门的门后走廊都是死的。门能开这件事，本身就是一种内容。',
 'cngrelic_13': '最后一页梦记的字迹褪了。褪色不是因为时间——是因为写它的那场梦还在继续。',
}

def provenance(r, pool, i):
    mods = r.get('mod') or {}
    et = r.get('effect_text') or ''
    rar = r.get('rarity')
    # 从效果类型推出叙事母题
    acts = [ec.get('action') for ec in r.get('effect_code') or []]
    if 'keep_block' in mods or '格挡留' in et:
        return '这块东西被同一个人用了很久。用到最后，该散的散了——它把散不掉的那一半留给了下一个用的人。'
    if 'cost_redirect' in mods:
        return '这件物品改变了规则。改变的方式很安静——没有人注意到代价去了哪里，直到账单变成另一种形式。'
    if 'vein_cost' in mods:
        v = mods.get('vein_cost', '')
        return '物品的印章盖在某种通行凭证上。盖章之后，%s 的路费降了——不是免费，是有人替你垫了一部分。' % v
    if 'chain_bonus' in mods:
        return '同一道纹路被刻了两遍。第二遍比第一遍深——刻的人已经知道它管用，所以刻得认真。'
    if 'on_kill' in acts:
        return '每完成一次某种作业，它的读数就跳一格。跳的方式像在计数。它数的东西比你想的多。'
    if 'turn_start' in acts and ('heal' in acts or 'block' in acts):
        return '它一直在运转。运转的声音很轻，轻到只有在安静的时候才注意得到——但它从来没停过。'
    if 'combat_start' in acts and 'draw' in acts:
        return '翻开它的那一刻，里面的东西比上次多一件。上次是谁用的没有记载。多出来的那件没有被登记。'
    if 'maxhp' in acts:
        v = 0
        for ec in r.get('effect_code') or []:
            if ec.get('action') == 'maxhp':
                v = ec.get('value') or 0
        if v > 0:
            return '它让装着它的人撑得更久。撑的意思不是治伤，是让身体的底数变大——变的那部分从哪里来，没有说明。'
        return '它拿走了一些东西。拿走的部分不会回来——但换来的那部分，比你失去的更耐用。'
    if 'gaze' in acts:
        v = 0
        for ec in r.get('effect_code') or []:
            if ec.get('action') == 'gaze':
                v = ec.get('value') or 0
        if v > 0:
            return '它一直在看。看的方式很被动——不追、不扫、不照。它只是在。被它看久了的人会知道区别。'
        return '它替你挡住了一部分目光。挡住的那部分去了哪里，说明书写得很含糊。'
    if 'resonance' in acts:
        return '它与环境持续共振。共振的频率不高不低——刚好是那种让人以为一切正常的频率。'
    return '来历没有记载。但它的磨损方式说明它被某种手握了很长时间——手的形状决定了它现在的样子。'

buf = []
buf.append('# W4 · 遗物来历（夜班版 · 107 件）')
buf.append('')
buf.append('> 任务书（自拟）：107 件各一段 ≤60 字来历，角度=**它被谁用了多久**——使用痕迹叙事。')
buf.append('> 区别于 F6（审计连接强度+补写 6 件）：本篇广度覆盖 107 件全部，叙事母题从 mod 字段与效果类型自动归类。')
buf.append('> rare/boss/特殊叙事 10 件手写校准（HAND），其余按母题模板生成。全部为提案。')
buf.append('')
for pk, pn in [('relics', '通用池'), ('anminRelics', '维护者池'), ('cngRelics', '疯先知池')]:
    buf.append('## %s\n' % pn)
    for i, r in enumerate(raw[pk]):
        if r['id'] in HAND:
            desc = HAND[r['id']]
        else:
            desc = provenance(r, pn, i)
        if len(desc) > 60:
            desc = desc[:59] + '…'
        buf.append('- **%s %s**（%s）：%s' % (r['id'], r['name'], CN_R.get(r.get('rarity'), ''), desc))
    buf.append('')
buf.append('## 复算\n')
buf.append('`python tools/sim/gen_w4.py`（HAND 手写 10 条在顶部；其余按 mod/effect_code 母题模板生成，seed=42 不适用——本脚本无随机）。')
OUT.write_text('\n'.join(buf) + '\n', encoding='utf-8')
print('written', OUT)
