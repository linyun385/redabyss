/* T61 生态敌人数据落地（一次性，保留供重建/幂等）：向 enemies/all.json 追加 33 只新敌。
   配额来自 docs/CONTENT_PLAN.md §3.1（口径 B）；意图只用引擎已有词汇
   （attack[times/pierce/mirror/drain_discard] / defend / buff / debuff[steal/gift/weak/poison/burn]）。
   幂等：已存在的 id 跳过。用法：node tools/_t61_data.js */
'use strict';
const fs = require('fs');
const path = require('path');
const FILE = path.join(__dirname, '..', 'enemies', 'all.json');
const list = JSON.parse(fs.readFileSync(FILE, 'utf8'));
const have = new Set(list.map(x => x.id));

const NEW = [
  // ── eco_surface 死寂壳层 D1（+3n/+2e/+1b）：真空、空壳、登陆设备。气味：壳先合后开 ──
  { id: 'enemy_d1_06', name: '空服的壳', layer: 1, tier: 'normal', eco: 'eco_surface', hp: '9-11',
    intent_pattern: [{ type: 'attack', value: 2 }, { type: 'defend', value: 4 }, { type: 'defend', value: 3 }, { type: 'attack', value: 3 }],
    traits: [], flavor: '防护服里早就没有人了。它照样按规程合拢，按规程张开。' },
  { id: 'enemy_d1_07', name: '晒裂的软管', layer: 1, tier: 'normal', eco: 'eco_surface', hp: '8-10',
    intent_pattern: [{ type: 'attack', value: 1, times: 2 }, { type: 'defend', value: 3 }, { type: 'attack', value: 2 }],
    traits: [], flavor: '管子裂着，漏出来的不是水。漏了五百年，还没漏完。' },
  { id: 'enemy_d1_08', name: '记名的旗', layer: 1, tier: 'normal', eco: 'eco_surface', hp: '10-12',
    intent_pattern: [{ type: 'buff', value: 2 }, { type: 'attack', value: 3 }, { type: 'defend', value: 3 }],
    traits: [], flavor: '旗面只剩编号。风根本没有，它还是展开一次，收起一次。' },
  { id: 'enemy_d1_e3', name: '气闸的守夜者', layer: 1, tier: 'elite', eco: 'eco_surface', hp: '27-31',
    intent_pattern: [{ type: 'defend', value: 6 }, { type: 'attack', value: 4 }, { type: 'debuff', status: 'weak' }, { type: 'attack', value: 4 }],
    traits: [], flavor: '它在等一个对不上暗号的人。等了这么久，暗号已经换过四版。' },
  { id: 'enemy_d1_e4', name: '坠轨的投影', layer: 1, tier: 'elite', eco: 'eco_surface', hp: '25-29',
    intent_pattern: [{ type: 'attack', value: 3, mirror: true }, { type: 'defend', value: 5 }, { type: 'attack', value: 5 }, { type: 'attack', value: 4 }],
    traits: [], flavor: '轨道上的人按过按钮。投影把他们落下来的样子，一遍一遍演给你看。' },
  { id: 'enemy_d1_b2', name: '静默号·最后一次广播', layer: 1, tier: 'boss', eco: 'eco_surface', hp: 60,
    intent_pattern: [{ type: 'attack', value: 4, times: 2 }, { type: 'defend', value: 8 }, { type: 'debuff', status: 'gift' }, { type: 'attack', value: 6 }, { type: 'defend', value: 6 }],
    traits: [], flavor: '广播稿念到第三页。第三页之后是空白。它还在念。' },

  // ── eco_cold 沉积冷洞 D2（+2n/+1e/+1b）：碎屑雪、慢、历壁 ──
  { id: 'enemy_d2_08', name: '沉雪的苔背', layer: 2, tier: 'normal', eco: 'eco_cold', hp: '12-14',
    intent_pattern: [{ type: 'defend', value: 5 }, { type: 'attack', value: 3 }, { type: 'defend', value: 4 }, { type: 'attack', value: 3 }, { type: 'defend', value: 3 }],
    traits: [], flavor: '雪落在它背上，落了八万年。它不动，雪替它记年。' },
  { id: 'enemy_d2_09', name: '历壁的蛀痕', layer: 2, tier: 'normal', eco: 'eco_cold', hp: '11-13',
    intent_pattern: [{ type: 'debuff', status: 'steal' }, { type: 'attack', value: 3 }, { type: 'defend', value: 3 }],
    traits: [], flavor: '历上缺了一小段。缺的那段在它肚子里，还没有消化。' },
  { id: 'enemy_d2_e3', name: '冷眠的守历者', layer: 2, tier: 'elite', eco: 'eco_cold', hp: '31-35',
    intent_pattern: [{ type: 'defend', value: 7 }, { type: 'attack', value: 5 }, { type: 'debuff', status: 'burn' }, { type: 'attack', value: 5 }, { type: 'defend', value: 6 }],
    traits: [], flavor: '它守的历不许火。谁带了火来，它就把火塞回谁的胸口。' },
  { id: 'enemy_d2_b2', name: '历的补写者', layer: 2, tier: 'boss', eco: 'eco_cold', hp: 66,
    intent_pattern: [{ type: 'attack', value: 4 }, { type: 'defend', value: 8 }, { type: 'attack', value: 5, drain_discard: true }, { type: 'defend', value: 6 }, { type: 'attack', value: 6 }],
    traits: [], flavor: '历上空着的年份要补齐。它看见你带了多少过去，就补多少。' },

  // ── eco_arid 泉眼干旱区 D3（+2n/+1e/+1b）：水按滴记、路权、隐生 ──
  { id: 'enemy_d3_08', name: '滴水的账房', layer: 3, tier: 'normal', eco: 'eco_arid', hp: '12-14',
    intent_pattern: [{ type: 'attack', value: 3 }, { type: 'defend', value: 4 }, { type: 'attack', value: 4 }, { type: 'defend', value: 3 }],
    traits: [], flavor: '它记账。一滴进，一滴出。你身上带的水，它已经记下了。' },
  { id: 'enemy_d3_09', name: '隐生的缓步', layer: 3, tier: 'normal', eco: 'eco_arid', hp: '10-12',
    intent_pattern: [{"type":"defend","value":6},{"type":"defend","value":4},{"type":"attack","value":2},{"type":"defend","value":5},{"type":"attack","value":3}]
    traits: [], flavor: '它死过很多次，每次都趁没人的时候活回来。这次它醒着。' },
  { id: 'enemy_d3_e3', name: '抢路的干壳', layer: 3, tier: 'elite', eco: 'eco_arid', hp: '30-34',
    intent_pattern: [{ type: 'attack', value: 4 }, { type: 'attack', value: 4 }, { type: 'defend', value: 5 }, { type: 'debuff', status: 'poison' }],
    traits: [], flavor: '水在这里有路权。它把自己的路，修进了你的喉咙。' },
  { id: 'enemy_d3_b2', name: '泉权的丈量者', layer: 3, tier: 'boss', eco: 'eco_arid', hp: 64,
    intent_pattern: [{ type: 'defend', value: 7 }, { type: 'attack', value: 5 }, { type: 'attack', value: 5 }, { type: 'debuff', status: 'gift' }, { type: 'buff', value: 2 }, { type: 'attack', value: 6 }],
    traits: [], flavor: '它量过每一眼泉。轮到你的时候，它量的不是水。' },

  // ── eco_sea 红蕨空洞海 D4（+2n/+1e）：丰盛、倒挂林、伏击 ──
  { id: 'enemy_d4_09', name: '藻毯的影子', layer: 4, tier: 'normal', eco: 'eco_sea', hp: '14-16',
    intent_pattern: [{ type: 'defend', value: 4 }, { type: 'attack', value: 4 }, { type: 'attack', value: 5 }, { type: 'defend', value: 4 }],
    traits: [], flavor: '影子先到，它后到。你看影子的那一眼，就是它等的全部。' },
  { id: 'enemy_d4_10', name: '滤食的须群', layer: 4, tier: 'normal', eco: 'eco_sea', hp: '13-15',
    intent_pattern: [{"type":"attack","value":2,"times":3},{"type":"defend","value":3},{"type":"attack","value":2,"times":2}]
    traits: [], flavor: '它们不吃你。它们只是把你和水一起滤一遍，留下的都算渣。' },
  { id: 'enemy_d4_e3', name: '红腔鱼的伏击手', layer: 4, tier: 'elite', eco: 'eco_sea', hp: '37-41',
    intent_pattern: [{ type: 'defend', value: 5 }, { type: 'attack', value: 7 }, { type: 'attack', value: 7 }, { type: 'debuff', status: 'weak' }],
    traits: [], flavor: '它在暗处悬着，悬了很久。红光每闪一次，它近一段。' },

  // ── eco_vent 热泉裂带 D5（+2n/+1e）：喷发周期、烫、汤 ──
  { id: 'enemy_d5_09', name: '硫菌丘的看火者', layer: 5, tier: 'normal', eco: 'eco_vent', hp: '15-17',
    intent_pattern: [{ type: 'defend', value: 5 }, { type: 'attack', value: 4 }, { type: 'attack', value: 4 }, { type: 'defend', value: 4 }, { type: 'attack', value: 4 }],
    traits: [], flavor: '它守着一口不开的泉。开泉的日子由不得它，也由不得你。' },
  { id: 'enemy_d5_10', name: '喷发期的管虫', layer: 5, tier: 'normal', eco: 'eco_vent', hp: '14-16',
    intent_pattern: [{ type: 'attack', value: 3, times: 2 }, { type: 'defend', value: 4 }, { type: 'attack', value: 3, times: 2 }],
    traits: [], flavor: '羽状触须张开的时候最好看。看完的人都这么说，说得很轻。' },
  { id: 'enemy_d5_e3', name: '热议会的执汤者', layer: 5, tier: 'elite', eco: 'eco_vent', hp: '39-43',
    intent_pattern: [{ type: 'attack', value: 5 }, { type: 'debuff', status: 'burn' }, { type: 'defend', value: 6 }, { type: 'attack', value: 6 }, { type: 'debuff', status: 'burn' }],
    traits: [], flavor: '汤是用活水煨的。你进了汤锅的事，就是全城的事。' },

  // ── eco_rad 辐射荒漠 D6（+2n/+1e/+1b）：低烧、壳、地神骨灰坛 ──
  { id: 'enemy_d6_08', name: '重鳞的拾壳者', layer: 6, tier: 'normal', eco: 'eco_rad', hp: '16-18',
    intent_pattern: [{ type: 'defend', value: 6 }, { type: 'defend', value: 4 }, { type: 'attack', value: 5 }, { type: 'attack', value: 4 }],
    traits: [], flavor: '它捡壳，一只一只码好。有的壳里还住着小东西，它也码。' },
  { id: 'enemy_d6_09', name: '低烧的菌群', layer: 6, tier: 'normal', eco: 'eco_rad', hp: '15-17',
    intent_pattern: [{"type":"buff","value":2},{"type":"attack","value":4},{"type":"attack","value":4},{"type":"defend","value":4},{"type":"attack","value":4},{"type":"defend","value":3}] flavor: '辐射是它的低烧。烧得越久，它越有精神。' },
  { id: 'enemy_d6_e3', name: '铅鳞的收藏家', layer: 6, tier: 'elite', eco: 'eco_rad', hp: '41-45',
    intent_pattern: [{ type: 'defend', value: 8 }, { type: 'attack', value: 6 }, { type: 'debuff', status: 'steal' }, { type: 'attack', value: 6 }],
    traits: [], flavor: '它收仪表，收屏蔽板，收到后来，收会走的东西。' },
  { id: 'enemy_d6_b2', name: '地神骨灰坛的看守', layer: 6, tier: 'boss', eco: 'eco_rad', hp: 72,
    intent_pattern: [{ type: 'attack', value: 6 }, { type: 'defend', value: 9 }, { type: 'attack', value: 5, times: 2 }, { type: 'debuff', status: 'gift' }, { type: 'buff', value: 3 }],
    traits: [], flavor: '坛子里的灰是地神剩下的。它守着，像守着一个还没凉透的名字。' },

  // ── eco_core 核心高热区 D7（+2n/+1e）：超临界、时间变慢、复刻 ──
  { id: 'enemy_d7_09', name: '三色菌毯的须', layer: 7, tier: 'normal', eco: 'eco_core', hp: '18-20',
    intent_pattern: [{ type: 'attack', value: 5 }, { type: 'defend', value: 6 }, { type: 'attack', value: 5 }, { type: 'defend', value: 5 }, { type: 'attack', value: 5 }],
    traits: [], flavor: '黑红金三色按顺序烫人。它换色的间隔，比你的呼吸慢半口。' },
  { id: 'enemy_d7_10', name: '慢半拍的影', layer: 7, tier: 'normal', eco: 'eco_core', hp: '17-19',
    intent_pattern: [{ type: 'attack', value: 6, mirror: true }, { type: 'defend', value: 5 }, { type: 'attack', value: 5 }],
    traits: [], flavor: '它打你的节奏，是你上一步的节奏。在这里，连影子都懒得自己动。' },
  { id: 'enemy_d7_e3', name: '超临界的水囊', layer: 7, tier: 'elite', eco: 'eco_core', hp: '45-49',
    intent_pattern: [{"type":"attack","value":6,"times":2},{"type":"defend","value":7},{"type":"attack","value":8},{"type":"attack","value":6}]
    traits: [], flavor: '囊里的水不在沸点以下。它鼓一下，走廊就暗一次。' },

  // ── eco_nexus 核心回路 D8（+6n）：谐振器走廊、八万年作息、不许关闭 ──
  { id: 'enemy_d8_05', name: '走廊的灯', layer: 8, tier: 'normal', eco: 'eco_nexus', hp: '20-22',
    intent_pattern: [{ type: 'defend', value: 6 }, { type: 'attack', value: 6 }, { type: 'defend', value: 5 }, { type: 'attack', value: 6 }, { type: 'defend', value: 4 }, { type: 'attack', value: 6 }],
    traits: [], flavor: '灯还亮着。按规程，它不许灭。你不许问为什么。' },
  { id: 'enemy_d8_06', name: '值班的影子', layer: 8, tier: 'normal', eco: 'eco_nexus', hp: '19-21',
    intent_pattern: [{ type: 'attack', value: 7 }, { type: 'defend', value: 5 }, { type: 'attack', value: 6 }, { type: 'debuff', status: 'gift' }],
    traits: [], flavor: '它按时上班。八万年没迟到过。你出现，算加班。' },
  { id: 'enemy_d8_07', name: '八万年前的班表', layer: 8, tier: 'normal', eco: 'eco_nexus', hp: '21-23',
    intent_pattern: [{ type: 'buff', value: 3 }, { type: 'attack', value: 6 }, { type: 'defend', value: 6 }, { type: 'attack', value: 6 }, { type: 'defend', value: 5 }, { type: 'attack', value: 6 }],
    traits: [], flavor: '班表上的名字都走光了。班表不认识走光，照常排班。' },
  { id: 'enemy_d8_08', name: '签到簿的笔', layer: 8, tier: 'normal', eco: 'eco_nexus', hp: '18-20',
    intent_pattern: [{ type: 'debuff', status: 'steal' }, { type: 'attack', value: 6 }],
    traits: [], flavor: '来的人都要签。笔不挑人，签什么都收，收走就不还。' },
  { id: 'enemy_d8_09', name: '谐振的余音', layer: 8, tier: 'normal', eco: 'eco_nexus', hp: '20-22',
    intent_pattern: [{ type: 'attack', value: 5, times: 2 }, { type: 'attack', value: 4, times: 2 }],
    traits: [], flavor: '声音停了以后还响着的那部分。它打的是你听到过的东西。' },
  { id: 'enemy_d8_10', name: '不许关闭的告示', layer: 8, tier: 'normal', eco: 'eco_nexus', hp: '22-24',
    intent_pattern: [{ type: 'defend', value: 8 }, { type: 'attack', value: 7 }, { type: 'debuff', status: 'gift' }, { type: 'defend', value: 6 }, { type: 'attack', value: 7 }],
    traits: [], flavor: '告示钉死了，四种字写同一句话。你多看的那几眼，都是它要的。' },
  { id: 'enemy_d8_11', name: '检修窗后的手', layer: 8, tier: 'normal', eco: 'eco_nexus', hp: '19-21',
    intent_pattern: [{"type":"attack","value":6},{"type":"attack","value":5,"times":2},{"type":"defend","value":5},{"type":"attack","value":5}]
    traits: [], flavor: '窗后有手在拨仪表。拨得很准。窗后没有人，这一点它不瞒你。' },
  { id: 'enemy_d8_12', name: '走廊尽头的白噪音', layer: 8, tier: 'normal', eco: 'eco_nexus', hp: '21-23',
    intent_pattern: [{ type: 'defend', value: 6 }, { type: 'attack', value: 5, times: 2 }, { type: 'attack', value: 5, times: 2 }, { type: 'defend', value: 6 }],
    traits: [], flavor: '它没有形状。你听多久，它就有多久。' }
];

let added = 0;
NEW.forEach(e => {
  if (have.has(e.id)) { console.log('跳过（已存在）: ' + e.id); return; }
  list.push(e); added++;
});
fs.writeFileSync(FILE, JSON.stringify(list, null, 1));
console.log('新增 ' + added + ' 只，总数 ' + list.length);
