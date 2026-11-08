# -*- coding: utf-8 -*-
"""把维护者（黯民）6 张核心卡写进 cards/anmin.json。
默认干跑；加 --apply 才写。已存在的 id 会被替换（幂等）。
2026-11-06：除 anm_0052（召唤物，引擎不支持）外全部落地。
"""
import json, sys, io, os, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'cards', 'anmin.json')
APPLY = '--apply' in sys.argv

CARDS = [
    {
        "id": "anm_0051", "name": "机械增生", "class": "anmin", "type": "power",
        "rarity": "uncommon", "veins": ["light"], "energy": 0,
        "effect": {"special": [{"code": "mech_grow"}], "target": "self"},
        "cost_type": "lock",
        "cost_text": "这张牌本场锁死，只能长出这一回。",
        "flavor": "像血肉一样膨胀。它不知道自己在长什么，只知道该长。",
        "upgrade": {"name_suffix": "·Ⅱ",
                    "effect": {"special": [{"code": "mech_grow", "value": 2}]},
                    "flavor_add": "第二轮的增生更急，掉下来的零件也更多。"}
    },
    {
        "id": "anm_0052", "name": "子代理", "class": "anmin", "type": "skill",
        "rarity": "uncommon", "veins": ["mineral"], "energy": 3,
        "part_cost": 5,
        "effect": {"target": "self", "special": [
            {"code": "summon_minion", "hp": 10, "atk": 3}
        ]},
        "cost_type": "none", "cost_text": "零件 -5",
        "flavor": "它替你站着。你站着，看它站着。",
        "upgrade": {"name_suffix": "·强",
                    "effect": {"special": [{"code": "summon_minion", "hp": 15, "atk": 5}]},
                    "flavor_add": "它比上一批高出一个头，也更沉默。"}
    },
    {
        "id": "anm_0053", "name": "悬浮体", "class": "anmin", "type": "power",
        "rarity": "uncommon", "veins": ["tremor"], "energy": 1,
        "no_bonus": True,
        "part_cost": 3,
        "effect": {"special": [{"code": "floating_body"}], "target": "self"},
        "cost_type": "none", "cost_text": "零件 -3",
        "flavor": "它没有在飞。它只是还没决定往哪边掉。",
        "upgrade": {"name_suffix": "·轻", "part_cost": 1,
                    "flavor_add": "拆掉一半配重之后，它掉得更慢了。"}
    },
    {
        "id": "anm_0054", "name": "武器试验", "class": "anmin", "type": "attack",
        "rarity": "uncommon", "veins": ["mineral"], "energy": 1,
        "part_cost": 3,
        "effect": {"damage": 3, "hits": 1, "target": "single",
                   "special": [{"code": "perm_strength", "value": 1}]},
        "cost_type": "lock",
        "cost_text": "零件 -3，这张牌本场锁死。",
        "flavor": "试出来的东西留在你身上，试废的东西留在它身上。",
        "upgrade": {"name_suffix": "·Ⅲ",
                    "effect": {"damage": 3, "special": [{"code": "perm_strength", "value": 2}]},
                    "flavor_add": "第三次之后，你已经分不清那是武器还是你的手臂。"}
    },
    {
        "id": "anm_0055", "name": "有机质发电", "class": "anmin", "type": "power",
        "rarity": "common", "veins": ["heat"], "energy": 3,
        "part_cost": 5,
        "effect": {"target": "single", "special": [
            {"code": "weak", "turns": 99},
            {"code": "frail", "turns": 99},
            {"code": "energy_on_enemy_attack", "value": 1},
            {"code": "enemy_defend_draw", "value": 1}
        ]},
        "cost_type": "none", "cost_text": "零件 -5",
        "flavor": "他们称之为残忍，我们称之为高效。",
        "upgrade": {"name_suffix": "·省", "part_cost": 3,
                    "flavor_add": "改良之后，烧的东西少了两成。"}
    },
    {
        "id": "anm_0056", "name": "重铸", "class": "anmin", "type": "skill",
        "rarity": "uncommon", "veins": ["water"], "energy": 0,
        "part_cost": 1,
        "effect": {"draw": 1, "target": "self",
                   "special": [{"code": "energy_gain", "value": 1}]},
        "cost_type": "none", "cost_text": "零件 -1",
        "flavor": "把拆下来的东西按原来的顺序装回去，它就又新了一次。",
        "upgrade": {"name_suffix": "·顺",
                    "effect": {"draw": 2, "special": [{"code": "energy_gain", "value": 1}]},
                    "flavor_add": "第二次装得比第一次快，因为不用再看图纸。"}
    },
    {
        "id": "anm_0057", "name": "更新换代", "class": "anmin", "type": "skill",
        "rarity": "common", "veins": ["water"], "energy": 1,
        "effect": {"draw": 1, "target": "self", "special": [
            {"code": "discard_hand"},
            {"code": "parts_from_discard", "value": 1}
        ]},
        "cost_type": "none", "cost_text": "",
        "flavor": "旧的那一批扫进漏斗。漏斗底下接着的，是下一批。",
        "upgrade": {"name_suffix": "·接",
                    "effect": {"draw": 1, "special": [
                        {"code": "discard_hand"},
                        {"code": "parts_from_discard", "value": 1},
                        {"code": "energy_gain", "value": 1}
                    ]},
                    "flavor_add": "换代的时候顺手把电也接了过来。"}
    },
]

raw = json.load(io.open(P, 'r', encoding='utf-8'))
existing = {c['id']: i for i, c in enumerate(raw)}
added, replaced = [], []
for c in CARDS:
    if c['id'] in existing:
        raw[existing[c['id']]] = c
        replaced.append(c['id'])
    else:
        raw.append(c)
        added.append(c['id'])

print('原有 %d 张' % len(existing))
print('新增: %s' % (', '.join(added) or '无'))
print('替换: %s' % (', '.join(replaced) or '无'))
print('结果: %d 张' % len(raw))
for c in raw:
    if c['id'] in ('anm_0051', 'anm_0053', 'anm_0054', 'anm_0055', 'anm_0056', 'anm_0057'):
        print('  %s %-6s %-6s veins=%s energy=%s part_cost=%s' % (
            c['id'], c['name'], c['type'], c.get('veins'), c.get('energy'), c.get('part_cost', 0)))

if not APPLY:
    print('\n[干跑] 加 --apply 写回 cards/anmin.json')
    sys.exit(0)

bak = P + '.bak-20261106-0125-anmin-core'
shutil.copy2(P, bak)
io.open(P, 'w', encoding='utf-8').write(json.dumps(raw, ensure_ascii=False, indent=1) + '\n')
print('\n已写回 %s（备份 %s）' % (P, os.path.basename(bak)))
