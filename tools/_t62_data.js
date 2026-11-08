/* T62 生态事件落地（一次性，幂等）：向 events/all.json 追加 10 条新事件（T60 配额：surface +5 / nexus +5）。
   效果只用引擎已支持字段（heal/damage/gaze/gold/maxhp/card_reward/relic + veins 标签）。
   每条带 eco（生态标签）与 bands（适用深度带，口径 B：母本带 ±1）。
   每个选项都有可见代价与不可见后果，每条事件至少一个「看起来更划算但更危险」的陷阱项。
   用法：node tools/_t62_data.js */
'use strict';
const fs = require('fs');
const path = require('path');
const FILE = path.join(__dirname, '..', 'events', 'all.json');
const list = JSON.parse(fs.readFileSync(FILE, 'utf8'));
const have = new Set(list.map(x => x.id));

const NEW = [
  // ── eco_surface 死寂壳层（D1 批次，bands 1–2）──
  {
    id: 'event_d1_4', layer: 1, eco: 'eco_surface', bands: [1, 2],
    title: '气闸的对答',
    body: '气闸一开一合，合上的力道比开的时候大。门边的对讲器沙沙响，像在等一句对得上的暗号。守夜的那位已经换过四版规程，它还在等第一版。',
    options: [
      { text: '按规程敲三下，等回音。', veins: ['mineral'],
        result: { gold: 30, heal: 4 },
        result_text: '回音来了，比广播里的年轻。储物柜自己弹开一格，里面的补给码得整整齐齐，像在等领的人。' },
      { text: '直接进去，快一点。', veins: [],
        result: { heal: 12, damage: 6 },
        result_text: '补给是全的，动作也快。只有气闸合上的时候没等你收手——规程里没有快这一项，它是照规程办事的。' },
      { text: '把门固定住，让它开不全。', veins: ['tremor'],
        result: { gaze: -1 },
        result_text: '你用撬棍别住门轴。里面的一切停在半开：你看了看门框，没有看门里。它没有记住你。' }
    ]
  },
  {
    id: 'event_d1_5', layer: 1, eco: 'eco_surface', bands: [1, 2],
    title: '第三层防护服',
    body: '挂钩上一排防护服，按挂的年头排。最外面那件晒得发脆，最里面那件几乎没见过光。每一件的胸口都有一串编号，编号后面都跟着一句话：不保证返程。',
    options: [
      { text: '穿最外面那件，最旧的。', veins: ['water'],
        result: { heal: 8 },
        result_text: '脆的地方正好透风。旧有成旧的好处——该坏的它都坏完了，剩下的部分靠得住。' },
      { text: '穿最里面那件，几乎没晒过。', veins: ['light'],
        result: { gold: 40, damage: 7 },
        result_text: '衣服是新的，口袋是满的：矿票、氧气罐、一枚别人的戒指。口袋的主人挂在第三排，你替他把这些东西背进了地下。' },
      { text: '都不穿，站远一点。', veins: [],
        result: { gaze: 1 },
        result_text: '真空把影子收得很短。多看这一眼，眼底的蓝斑过了很久才散。' }
    ]
  },
  {
    id: 'event_d1_6', layer: 1, eco: 'eco_surface', bands: [1, 2],
    title: '晒了五百年的水箱',
    body: '水箱立在陨击坑的阴影里，裂了一道缝。渗出来的水在坑沿结成一串圆珠，五百年的日头都晒在里面。谁接的谁喝，这里没有别的规矩。',
    options: [
      { text: '喝一口。', veins: ['water'],
        result: { heal: 6, damage: 4 },
        result_text: '水是甜的，甜里带着一点晒过的钝痛。五百年攒下来的东西，一起进了喉咙。' },
      { text: '把水箱整个搬走。', veins: ['mineral'],
        result: { gold: 35 },
        result_text: '深层的人按毫升收这个。你只是搬运，搬运不算喝。' },
      { text: '把裂口对准自己，等渗漏。', veins: ['light'],
        result: { gaze: 2, heal: 3 },
        result_text: '圆珠一颗一颗落进领口。你数着数着，就忘了自己在等什么——红光替你记着，它也看着。' }
    ]
  },
  {
    id: 'event_d1_7', layer: 1, eco: 'eco_surface', bands: [1, 2],
    title: '按规程应答',
    body: '广播醒着。第三页念完又从头念，字与字之间隔着标准的停顿。规程第十一条：听到问询，应答。它问到的第几条了，没人数。',
    options: [
      { text: '报自己的编号。', veins: ['light'],
        result: { gaze: 3 },
        result_text: '编号报得很标准。广播停了一拍——从来没有人答得这么准。从这一拍起，它记住你了。' },
      { text: '报一个死人的编号。', veins: ['mineral'],
        result: { gold: 45 },
        result_text: '死人的编号对得上，死人的遗物费还没人领。手续齐全，款项当场结清。' },
      { text: '让静默继续。', veins: [],
        result: {},
        result_text: '你从广播底下走过去。第三页念完了，翻回第一页。没有名字的事，不算发生过。' }
    ]
  },
  {
    id: 'event_d1_8', layer: 1, eco: 'eco_surface', bands: [1, 2],
    title: '坠轨的清单',
    body: '残骸散了一坡，清单卡在货舱的夹层里，塑封完好。每一行货物后面都有一栏签收人。签收人那一栏，从上到下都是空的。',
    options: [
      { text: '按清单清点货物。', veins: ['mineral'],
        result: { gold: 50, damage: 3 },
        result_text: '一件一件对，对到最后一件的时候手被划了。清单上有它的名字，它就照清单办事。' },
      { text: '只拿清单上没有的。', veins: ['tremor'],
        result: { card_reward: 'rare', damage: 5 },
        result_text: '没登记的东西压在最底下，比清单上所有的都好。它比看上去重，也没看上去老实。' },
      { text: '把清单烧了。', veins: ['heat'],
        result: { gaze: 2, heal: 3 },
        result_text: '塑封烧起来的时候有声音，很轻。没有清单，就没有欠账。你胸口那点旧伤先松了。' }
    ]
  },

  // ── eco_nexus 核心回路（D8 批次，bands 7–8）──
  {
    id: 'event_d8_4', layer: 8, eco: 'eco_nexus', bands: [7, 8],
    title: '值班交接',
    body: '走廊里那位把班表递了过来。班表上的排班排到八万年后，每一个格子都签了字，只有一个格子空着——就是今天这一格。它站着，等一个接班的人。',
    options: [
      { text: '接下班表。', veins: ['light'],
        result: { gaze: 3, heal: 4 },
        result_text: '笔在你手里的时候很轻。它松开的那一下，八万年的站姿散了架。位置是你的了，走廊从你站的地方重新开始。' },
      { text: '替它站一班。', veins: ['mineral'],
        result: { gold: 60, damage: 6 },
        result_text: '它把八万年攒下的东西全数交给你，交接单一式两份。站班的滋味它没写——腿是自己的，麻也是自己的。' },
      { text: '从旁边绕过去。', veins: ['tremor'],
        result: {},
        result_text: '走廊不宽，你侧着身。它的目光跟着你走了三步，第四步起就不归它管了。' }
    ]
  },
  {
    id: 'event_d8_5', layer: 8, eco: 'eco_nexus', bands: [7, 8],
    title: '四种字的告示',
    body: '告示钉死了，旧光者文字、渊民震语、殖民者通用语、还有谁也不认得的第四种，写的是同一句话。钉子是新的。这句话不许关闭。',
    options: [
      { text: '照告示做。', veins: ['light'],
        result: { heal: 9 },
        result_text: '你照做了。做完之后呼吸顺了一截，像是有什么替你把姿势校准了。它说做什么，你就该做什么。' },
      { text: '闭着眼走过去。', veins: [],
        result: { gaze: 3 },
        result_text: '闭着眼反而看得更清楚。四种字在眼皮底下排着队走，你多看了三眼，眼眼都记了档。' },
      { text: '把告示念出声。', veins: ['tremor'],
        result: { maxhp: -2, gold: 35 },
        result_text: '念到第二种字的时候声音就不像你的了。工钱按次结，当场付清——嗓子里的那点余量，算你入的股。' }
    ]
  },
  {
    id: 'event_d8_6', layer: 8, eco: 'eco_nexus', bands: [7, 8],
    title: '签到处',
    body: '簿子摊开在台上，笔用链子拴着。八万年来这里的人签了一整本又换一本，换下来的那摞码得像地基。簿子的最后一页是空的，正对着你。',
    options: [
      { text: '签自己的名字。', veins: ['light'],
        result: { gaze: 3 },
        result_text: '签名的时候手很稳。这一页只有一个名字，整本簿子都在替这个笔画作证。' },
      { text: '签上一个来过的人。', veins: ['mineral'],
        result: { gold: 40, damage: 4 },
        result_text: '上一个来过的人不会来对笔迹。链子够长，笔够快——账要平，划伤就算利息。' },
      { text: '把笔收进兜里。', veins: ['tremor'],
        result: { card_reward: 'rare', damage: 5 },
        result_text: '笔尖是谐振器上磨下来的，写出来的字比人活得久。它在你兜里不老实，攥一下，疼一下。' }
    ]
  },
  {
    id: 'event_d8_7', layer: 8, eco: 'eco_nexus', bands: [7, 8],
    title: '八万年前的休息室',
    body: '休息室的门没有锁。柜子按编号排，柜门上的名字磨没了，编号还在。椅子保持着有人刚起身的样子，烟灰缸是空的，烟灰缸不许有烟。',
    options: [
      { text: '打开写着编号的柜子。', veins: [],
        result: { gold: 30 },
        result_text: '柜子里的东西按用途分好，连绳子都绕好了圈。都拿走也不算偷——按规程，失效满八万年即视为无主。' },
      { text: '只拿过了保质期还能吃的。', veins: ['water'],
        result: { heal: 7, gaze: 1 },
        result_text: '八万年不算短。味道也过了八万年。你吃着，感觉到有什么在看你吃东西，看得很仔细。' },
      { text: '把柜门轻轻带上。', veins: ['light'],
        result: {},
        result_text: '柜门合上的声音只有你听见。椅子还是刚起身的样子。有的东西不惊动，就还能一直维持着。' }
    ]
  },
  {
    id: 'event_d8_8', layer: 8, eco: 'eco_nexus', bands: [7, 8],
    title: '呼吸口',
    body: '走廊尽头风往上走。风里什么都没有，只有谐振器透出来的那点余温。从这里上去，就到它跟前了。风是凉的，往上走的东西没有凉的。',
    options: [
      { text: '把手伸进风里。', veins: ['light'],
        result: { gaze: 2, maxhp: -2 },
        result_text: '风从指缝里过去，数得清每一根。少的那点东西没有感觉——它拿走的部分，本来就不归手管。' },
      { text: '贴着墙听它呼吸。', veins: ['tremor'],
        result: { heal: 8 },
        result_text: '墙的这面是热的。呼吸很长，你跟着调了两轮，伤处跟着松开了。它没有察觉，或者习以为常。' },
      { text: '往风里放一枚矿票。', veins: ['mineral'],
        result: { damage: 3, heal: 10 },
        result_text: '矿票打着旋往上走。风顿了一下——收下了。烫是找零，顺过来的那口呼吸是真的。' }
    ]
  }
];

let added = 0;
NEW.forEach(e => {
  if (have.has(e.id)) { console.log('跳过（已存在）: ' + e.id); return; }
  list.push(e); added++;
});
fs.writeFileSync(FILE, JSON.stringify(list, null, 1));
console.log('新增 ' + added + ' 条，总数 ' + list.length);
