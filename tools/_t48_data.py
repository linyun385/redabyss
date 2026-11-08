# -*- coding: utf-8 -*-
"""T48：追加 8 层 ×（2 精英 + 1 Boss 变体）= 24 个敌人。一次性脚本。"""
import json, io, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

E = [
# L1 地表死寂区（气味：空壳与干燥）
{"id":"enemy_d1_e1","name":"盐壳拾荒者","layer":1,"tier":"elite","hp":30,
 "intent_pattern":[{"type":"attack","value":4},{"type":"defend","value":7},{"type":"attack","value":4},{"type":"buff","value":3}],
 "traits":[],"flavor":"改到第三代的防护服，面甲上开了一条自己割的缝。它靠什么呼吸，没人问过。"},
{"id":"enemy_d1_e2","name":"孢子清道夫","layer":1,"tier":"elite","hp":28,
 "intent_pattern":[{"type":"debuff","status":"gift","value":1},{"type":"attack","value":5},{"type":"attack","value":5},{"type":"defend","value":5}],
 "traits":[],"flavor":"它扫拢孢子不是为杀谁。扫干净的地方，红渊就看不见了。"},
{"id":"enemy_d1_b1","name":"钟乳盐·塌落体","layer":1,"tier":"boss","hp":46,
 "intent_pattern":[{"type":"attack","value":5},{"type":"defend","value":8},{"type":"attack","value":5},{"type":"attack","value":9}],
 "traits":[],"flavor":"钟乳盐长了几千年，长成了会自己塌下来的形状。",
 "phases":[{"hp_above":0.5,"log":"盐壳簌簌地掉。它在换一个更重的形状。","intent_pattern":[{"type":"attack","value":6},{"type":"defend","value":9},{"type":"attack","value":11}]}]},
# L2 外层冷洞（气味：慢、旧、历法）
{"id":"enemy_d2_e1","name":"历虫","layer":2,"tier":"elite","hp":42,
 "intent_pattern":[{"type":"defend","value":8},{"type":"attack","value":5},{"type":"defend","value":8},{"type":"attack","value":9}],
 "traits":[],"flavor":"它以年为进食间隔，以历痕为巢。你打它的时候，它正在补一段旧历。"},
{"id":"enemy_d2_e2","name":"菌膜织者","layer":2,"tier":"elite","hp":40,
 "intent_pattern":[{"type":"buff","value":3},{"type":"attack","value":6},{"type":"debuff","status":"steal","value":1},{"type":"attack","value":7}],
 "traits":[],"flavor":"冷洞的菌膜是它织的。织到密处，连你的手牌也归它安排。"},
{"id":"enemy_d2_b1","name":"历壁的守读者","layer":2,"tier":"boss","hp":58,
 "intent_pattern":[{"type":"attack","value":6},{"type":"defend","value":9},{"type":"attack","value":6},{"type":"attack","value":12}],
 "traits":[],"flavor":"它守着历壁最老的一段。读它要几百年，它已经开始读了。",
 "phases":[{"hp_above":0.5,"log":"它翻动了历壁上最深的一页。节奏变了。","intent_pattern":[{"type":"attack","value":7},{"type":"defend","value":10},{"type":"attack","value":14}]}]},
# L3 干旱空洞区（气味：干、硬、钻）
{"id":"enemy_d3_e1","name":"钻孔贝群","layer":3,"tier":"elite","hp":52,
 "intent_pattern":[{"type":"defend","value":10},{"type":"attack","value":7},{"type":"defend","value":10},{"type":"attack","value":10}],
 "traits":[],"flavor":"不是一只，是一片。它们钻了三代才钻成这个阵型。"},
{"id":"enemy_d3_e2","name":"旱螈伏兵","layer":3,"tier":"elite","hp":48,
 "intent_pattern":[{"type":"attack","value":7},{"type":"attack","value":7},{"type":"buff","value":4},{"type":"attack","value":11}],
 "traits":[],"flavor":"它在干缝里趴了整整一个水脉冲。你走到它面前，是它等的。"},
{"id":"enemy_d3_b1","name":"旱脉的封口者","layer":3,"tier":"boss","hp":62,
 "intent_pattern":[{"type":"attack","value":8},{"type":"defend","value":6},{"type":"attack","value":8},{"type":"attack","value":14}],
 "traits":[],"flavor":"哪条水脉干了，它就把哪条脉口封上。封口的东西是它自己的壳。"},
# L4 稳定空洞海（气味：丰盛、光、巨影）
{"id":"enemy_d4_e1","name":"藻毯伏击者","layer":4,"tier":"elite","hp":60,
 "intent_pattern":[{"type":"attack","value":9},{"type":"buff","value":4},{"type":"attack","value":9},{"type":"defend","value":8}],
 "traits":[],"flavor":"藻毯动了一下。不是水流。"},
{"id":"enemy_d4_e2","name":"红腔鱼·巡游种","layer":4,"tier":"elite","hp":64,
 "intent_pattern":[{"type":"attack","value":7,"times":2},{"type":"defend","value":8},{"type":"attack","value":7,"times":2},{"type":"buff","value":3}],
 "traits":[],"flavor":"巡游种不吃伏击。它绕着你游，一圈比一圈小。"},
{"id":"enemy_d4_b1","name":"光蛭母·逆流","layer":4,"tier":"boss","hp":130,
 "intent_pattern":[{"type":"attack","value":10},{"type":"defend","value":10},{"type":"attack","value":8},{"type":"debuff","status":"steal","value":1}],
 "traits":[],"flavor":"它逆着上升气流漂。被它照亮的东西会往下坠。",
 "phases":[
  {"hp_above":0.66,"log":"它把自己摊开在逆流里。数不清哪一层是它。","intent_pattern":[{"type":"attack","value":10},{"type":"defend","value":10},{"type":"attack","value":8},{"type":"debuff","status":"steal","value":1}]},
  {"hp_above":0.33,"log":"它薄得透光，开始分你一点光——多收一点利息。","intent_pattern":[{"type":"buff","value":5},{"type":"attack","value":12},{"type":"debuff","status":"gift","value":1},{"type":"attack","value":9}]},
  {"hp_above":0,"log":"逆流停了。它整片压下来。","intent_pattern":[{"type":"attack","value":10,"times":2},{"type":"attack","value":8},{"type":"buff","value":6},{"type":"attack","value":14}]}]},
# L5 热泉裂带（气味：周期、节奏、硫）
{"id":"enemy_d5_e1","name":"喷息守卫","layer":5,"tier":"elite","hp":62,
 "intent_pattern":[{"type":"defend","value":7},{"type":"attack","value":11},{"type":"defend","value":7},{"type":"attack","value":11}],
 "traits":[],"flavor":"喷议会的门卫不收钱，只收节奏。踩不对点的人会被请出去。"},
{"id":"enemy_d5_e2","name":"硫沫赘生体","layer":5,"tier":"elite","hp":60,
 "intent_pattern":[{"type":"attack","value":6,"times":2},{"type":"buff","value":4},{"type":"attack","value":6,"times":2},{"type":"attack","value":9}],
 "traits":[],"flavor":"它从一次大喷里长出来，身上还带着那个节奏。"},
{"id":"enemy_d5_b1","name":"震喉·空腔独奏","layer":5,"tier":"boss","hp":110,
 "intent_pattern":[{"type":"attack","value":9},{"type":"attack","value":6,"drain_discard":True},{"type":"defend","value":8},{"type":"attack","value":12}],
 "traits":[],"flavor":"它不广播别人的振动了。它只播自己的一段，翻来覆去。",
 "phases":[{"hp_above":0.5,"log":"独奏进了副歌。它开始从你的弃牌里取音。","intent_pattern":[{"type":"attack","value":9,"drain_discard":True},{"type":"attack","value":10},{"type":"attack","value":13}]}]},
# L6 辐射矿石区（气味：辐射、金属、骨灰坛）
{"id":"enemy_d6_e1","name":"辐射休眠孢子群","layer":6,"tier":"elite","hp":72,
 "intent_pattern":[{"type":"debuff","status":"steal","value":1},{"type":"attack","value":12},{"type":"attack","value":12},{"type":"buff","value":5}],
 "traits":[],"flavor":"孢子不该聚成团。聚成团的孢子已经开始记东西了。"},
{"id":"enemy_d6_e2","name":"金属鳞鳄幼体","layer":6,"tier":"elite","hp":76,
 "intent_pattern":[{"type":"attack","value":13},{"type":"defend","value":9},{"type":"attack","value":13}],
 "traits":[],"flavor":"王蜕下来的壳里孵出了它。它比王的壳更硬。"},
{"id":"enemy_d6_b1","name":"辐射金属鳞鳄王·蜕","layer":6,"tier":"boss","hp":150,
 "intent_pattern":[{"type":"attack","value":14},{"type":"defend","value":10},{"type":"attack","value":14},{"type":"buff","value":6}],
 "traits":[],"flavor":"王蜕了一次皮。蜕下来的那层也在爬。",
 "phases":[{"hp_above":0.4,"log":"旧鳞一片片立起来。它不打算防了。","intent_pattern":[{"type":"attack","value":16},{"type":"attack","value":12},{"type":"defend","value":12}]}]},
# L7 核心高热区（气味：烧、祭祀、锁死边缘）
{"id":"enemy_d7_e1","name":"烧手的灰烬","layer":7,"tier":"elite","hp":88,
 "intent_pattern":[{"type":"attack","value":15},{"type":"buff","value":6},{"type":"attack","value":15},{"type":"defend","value":10}],
 "traits":[],"flavor":"祭祀台上没烧尽的部分聚了起来。它烧你的手，和当年烧历书是同一个动作。"},
{"id":"enemy_d7_e2","name":"震台祭司","layer":7,"tier":"elite","hp":84,
 "intent_pattern":[{"type":"buff","value":7},{"type":"debuff","status":"steal","value":1},{"type":"attack","value":12},{"type":"attack","value":10}],
 "traits":[],"flavor":"它祭的已经不是地神。它祭的是自己即将成为的东西。"},
{"id":"enemy_d7_b1","name":"穹顶之影·网颤","layer":7,"tier":"boss","hp":72,
 "intent_pattern":[{"type":"attack","value":12},{"type":"attack","value":8,"times":2},{"type":"debuff","status":"gift","value":1},{"type":"attack","value":16}],
 "traits":[],"flavor":"穹顶之影的一角垂到了核心区。网在颤，颤的是网住的还是网，分不清。",
 "phases":[{"hp_above":0.5,"log":"网收紧了。颤动变成了抽搐。","intent_pattern":[{"type":"attack","value":14},{"type":"attack","value":10,"times":2},{"type":"attack","value":18}]}]},
# L8 红渊核心（气味：循环、锁死、自动化）
{"id":"enemy_d8_e1","name":"循环的巡逻体","layer":8,"tier":"elite","hp":98,
 "intent_pattern":[{"type":"attack","value":16},{"type":"defend","value":12},{"type":"attack","value":16},{"type":"buff","value":6}],
 "traits":[],"flavor":"它按八万年前的路线巡逻。路线上的东西换了几拨，路线没换。"},
{"id":"enemy_d8_e2","name":"墟影残片·重奏","layer":8,"tier":"elite","hp":102,
 "intent_pattern":[{"type":"attack","value":10,"times":2},{"type":"defend","value":10},{"type":"attack","value":10,"times":2},{"type":"buff","value":5}],
 "traits":[],"flavor":"同一片残影，抄了两遍。两遍都认为自己是真的。"},
{"id":"enemy_d8_b1","name":"墟蛹·未完成","layer":8,"tier":"boss","hp":200,
 "intent_pattern":[{"type":"attack","value":12},{"type":"defend","value":10},{"type":"attack","value":12},{"type":"debuff","status":"steal","value":1}],
 "traits":[],"flavor":"它比墟蛹小一圈，也新一层。有些程序还没算完，所以它还醒着。",
 "phases":[
  {"hp_above":0.33,"log":"茧上的纹路亮了。它在核对什么东西——核对到你了。","intent_pattern":[{"type":"attack","value":12},{"type":"defend","value":10},{"type":"attack","value":12},{"type":"debuff","status":"steal","value":1}]},
  {"hp_above":0,"log":"核算完毕。结果是一条旧的指令：清除外来模式。","intent_pattern":[{"type":"attack","value":14,"pierce":True},{"type":"attack","value":10},{"type":"defend","value":12},{"type":"attack","value":16,"pierce":True}]}]}
]

p = os.path.join(ROOT, 'enemies/all.json')
d = json.load(io.open(p, encoding='utf-8'))
arr = d['enemies'] if isinstance(d, dict) and 'enemies' in d else d
have = {x['id'] for x in arr} | {x['name'] for x in arr}
for x in E:
    assert x['id'] not in have and x['name'] not in have, x['id'] + ' / ' + x['name'] + ' 冲突'
arr.extend(E)
out = d if isinstance(d, dict) else arr
io.open(p, 'w', encoding='utf-8', newline='\n').write(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
print('enemies/all.json +', len(E), '->', len(arr))
