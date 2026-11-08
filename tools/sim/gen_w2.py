# -*- coding: utf-8 -*-
"""W2 敌人描述文案（夜班版）→ docs/design/enemy_lore_night.md
任务书（自拟）：145 只敌人各一段 ≤60 字，角度=「闭眼听」——从声音/触感/节奏读出攻击方式。
区别于 F4（逐只考什么/罚什么的机械判读）：本篇用感官线索写，避免重复 F4 的措辞。
生成引擎：从意图数据取三要素（节奏/力度/异常信号），按层配感官词库生成散文体。
boss 15 只手写校准。
"""
import io, sys, json, random
from pathlib import Path
GAME = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(GAME / 'data' / 'audit'))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
CN_CLASS = {'diver':'下潜者','tremor':'震语者','anmin':'维护者','cangmin':'疯先知','shared':'通用'}

OUT = GAME / 'docs' / 'design' / 'enemy_lore_night.md'
raw = json.loads((GAME / 'data/audit/raw_all.json').read_text(encoding='utf-8'))
CN_TIER = {'normal': '普通', 'elite': '精英', 'boss': 'boss'}

# 感官词库（按层配环境音色）
SOUND = {
 1: ('空管里的嗡鸣', '真空吸尘般的嘶声', '干燥的摩擦'),
 2: ('滴水间隙的回声', '雪层下闷闷的蠕动', '冷脆的碎裂'),
 3: ('沙粒滑落的沙沙', '壳片相碰的咔嗒', '旱地裂缝的嘶声'),
 4: ('水面的细碎波纹', '鳞片滑水的咕噜', '气泡上涌的咕声'),
 5: ('热泉间歇的喷射', '硫质气泡的破裂', '蒸汽泄压的尖啸'),
 6: ('金属摩擦的低鸣', '辐射计的滴答', '铅壳碰撞的钝响'),
 7: ('高频共振的尖鸣', '光柱扫过的嗡——', '多声部叠唱'),
 8: ('巨型结构体的低频呼吸', '所有方向的回声同时到达', '万物的底噪'),
}
BOSS_CUSTOM = {
 'enemy_d1_b1': '先是一段很轻的盐粒落沙声，然后整个重量压下来——换形时的闷响像什么塌了。塌完之后，节奏比之前重一倍。',
 'enemy_d1_b2': '最后一次广播的背景音。两段讲话之间夹着一段「音乐」——收下的东西不属于这里。',
 'enemy_d2_b1': '翻页声。每一页比上一页重，最后那页翻开时整层都在跟着翻。',
 'enemy_d2_b2': '写字的沙沙声夹着从远处取东西的闷响。它翻你的弃牌堆翻得很熟练。',
 'enemy_d3_b1': '没有防备的声音，只有规律的踩踏。踩踏间隔不变，力度阶梯式加重——最后一脚最响。',
 'enemy_d3_b2': '先送礼物的叮当声，然后是抢夺的碎裂，最后是量尺碰撞地面的笃笃声。',
 'enemy_d4_b1': '水流声很轻。轻是因为它薄——三层形态切换时水流反向一瞬。它偷东西的时候完全无声。',
 'enemy_d5_b1': '空腔共鸣的低音，像管风琴。中段多了一段复刻——是你自己上一回合的动作在回放。末段改走骨头传导，声音从体内响起。',
 'enemy_d6_b1': '鳞片立起的金属刷声。立完之后不设防——只有攻击节奏，没有防御拍。',
 'enemy_d6_b2': '先偷后送——偷的时候无声，送的时候叮当响。最后一轮连拍带着鳞片刷刷声。',
 'enemy_d7_b1': '倒挂的网在极高频振动。蓄力阶段两个增益拍完全安静——安静之后的那一下，从网心炸开。',
 'enemy_d7_b2': '网颤的节奏比本体急。三段连压夹着一份「礼物」——礼物的落地声很轻。',
 'enemy_d8_b1': '茧的低频呼吸中混入核算滴答声。中段从你的弃牌堆里抽丝——沙沙声来自你的牌。末段茧壳裂开，三段穿透拍。',
 'anmenemy_16': '机器语音循环播放备案。每一段以「保运行」开头，火力升级前有一段全静默——那是它在加载。',
 'cngenemy_16': '和你一模一样的声音。第一段是你的，第二段也是。最后一段多了一层回音——那是他松手的声音。',
}

def prose(e, L):
    its = list(e.get('intent_pattern') or [])
    for ph in e.get('phases') or []:
        its.extend(ph.get('intent_pattern') or [])
    atks = [i for i in its if i.get('type') == 'attack']
    defs = [i for i in its if i.get('type') == 'defend']
    buffs = [i for i in its if i.get('type') == 'buff']
    debuffs = [i for i in its if i.get('type') == 'debuff']
    multi = [i for i in atks if (i.get('times') or 1) >= 2]
    pierce = any(i.get('pierce') for i in its)
    steal = any(i.get('status') == 'steal' for i in its)
    mirror = any(i.get('mirror') for i in its)
    drain = any(i.get('drain_discard') for i in its)
    gift = any(i.get('status') == 'gift' for i in its)
    burn = any(i.get('status') == 'burn' for i in its)
    poison = any(i.get('status') == 'poison' for i in its)
    weak = any(i.get('status') == 'weak' for i in its)
    s1, s2, s3 = SOUND[L]
    parts = []
    if atks:
        vals = sorted(set(i.get('value') or 0 for i in atks))
        if multi:
            parts.append('%s，分好几下送过来' % random.choice([s1, s2]))
        else:
            parts.append('%s，一下%s一下' % (random.choice([s1, s2]), '重' if max(vals, default=0) >= 8 else '轻'))
    if pierce:
        parts.append('有一段从骨头里过——挡不住')
    if mirror:
        parts.append('它在回放你上一拍的动作')
    if drain:
        parts.append('它从你丢掉的东西里取料')
    if defs:
        parts.append('偶尔停下来 hardened')
    if buffs:
        parts.append('每过几拍会给自己上一次发条')
    if steal:
        parts.append('趁你不注意摸走一样东西')
    if gift:
        parts.append('会先递给你一样东西')
    if weak:
        parts.append('附带削弱性的震荡')
    if burn and L != 5:
        parts.append('碰到会着火')
    if poison and L != 3:
        parts.append('带着毒')
    if not parts:
        parts.append(s3)
    return '。'.join(parts[:3]) + '。节奏 %d 拍。' % len(its)

def attacks_feel(e):
    """攻击力描述词"""
    its = list(e.get('intent_pattern') or [])
    for ph in e.get('phases') or []:
        its.extend(ph.get('intent_pattern') or [])
    atks = [i.get('value') or 0 for i in its if i.get('type') == 'attack']
    if not atks: return ''
    m = max(atks)
    if m >= 16: return '最重一击在骨头里'
    if m >= 10: return '重击要有准备才挡得住'
    if m >= 5: return '打得准但不重'
    return '轻得像在试探'

buf = []
buf.append('# W2 · 敌人描述（夜班版 · 闭眼听）')
buf.append('')
buf.append('> 任务书（自拟）：145 只敌人各一段 ≤60 字，角度=**闭眼听**——从声音/触感/节奏读出攻击方式。')
buf.append('> 区别于 F4（逐只判考什么）：本篇用感官线索写，普通敌用生成引擎从意图数据取三要素（节奏/力度/异常信号）配层音色，boss 15 只手写校准。')
buf.append('> 全部为估算。复算：`python tools/sim/gen_w2.py`。')
buf.append('')
for L in range(1, 9):
    buf.append('## 第 %d 层\n' % L)
    for pk, pn in [('enemies', '通用'), ('anminEnemies', '维护者'), ('cngEnemies', '疯先知')]:
        es = [e for e in raw[pk] if e['layer'] == L]
        if not es: continue
        for e in sorted(es, key=lambda x: {'normal': 0, 'elite': 1, 'boss': 2}[x['tier']]):
            if e['id'] in BOSS_CUSTOM:
                desc = BOSS_CUSTOM[e['id']]
            else:
                desc = prose(e, L)
                feel = attacks_feel(e)
                if feel and random.random() < 0.5:
                    desc = feel + '。' + desc
            if len(desc) > 60:
                desc = desc[:59] + '…'
            buf.append('- **%s**（%s）：%s' % (e['name'], CN_TIER[e['tier']], desc))
    buf.append('')

buf.append('## 复算\n')
buf.append('`python tools/sim/gen_w2.py`（boss 手写 15 条在 BOSS_CUSTOM；普通敌生成引擎从意图数据取节奏/力度/异常信号配层音色）。')
OUT.write_text('\n'.join(buf) + '\n', encoding='utf-8')
print('written', OUT, 'bosses', len(BOSS_CUSTOM))
