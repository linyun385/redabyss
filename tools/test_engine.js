// 引擎冒烟测试：验证 core.js 能跑通一场完整战斗
const path = require('path');
const RA = require(path.join(__dirname, '..', 'engine', 'core.js'));

function assert(cond, msg) {
  if (!cond) { console.error('FAIL: ' + msg); process.exitCode = 1; }
  else console.log('  ok  ' + msg);
}

console.log('=== 引擎冒烟测试 ===\n');

// 1. 建局
let run = RA.newRun('diver', { seed: 42 });
assert(run.hp === 80, '下潜者初始生命 80');
assert(run.deck.length === 10, '初始牌组 10 张：' + run.deck.length);
assert(run.gaze === 0, '凝视初始 0');

let run2 = RA.newRun('tremor', { seed: 7 });
assert(run2.hp === 72, '震语者初始生命 72');

// 1b. special 形式的 retain：回合结束留在手上（静日/埋骨布一类）
{
  const runR = RA.newRun('tremor', { seed: 99 });
  runR.depth = 1;
  const retainCard = { id: 'test_retain', name: '静日（测试）', class: 'tremor', type: 'skill',
    rarity: 'common', veins: [], energy: 1, effect: { block: 9, target: 'self', special: [{ code: 'retain' }] } };
  runR.deck = [Object.assign({}, retainCard)];
  const CR = RA.startCombat(runR, [{ name: '隙居螨', hp: '8-8', tier: 'normal',
    intent_pattern: [{ type: 'defend', value: 3 }] }]);
  CR.hand = [Object.assign({}, retainCard)];
  CR.hand[0].uid = 'rt0';
  RA.endTurn(CR);
  assert(CR.hand.some(c => c.id === 'test_retain'), 'special retain：回合结束留在手上');
  assert(CR.discardPile.every(c => c.id !== 'test_retain'), 'special retain：没有进弃牌堆');
}

// 2. 开战
run.depth = 4;
const enemies = [
  { name: '红腔鱼', hp: '18-24', tier: 'normal',
    intent_pattern: [{ type: 'attack', value: 6 }, { type: 'defend', value: 5 }] }
];
let C = RA.startCombat(run, enemies);
assert(C.hand.length === 5, '开战抽 5 张：' + C.hand.length);
assert(C.energy === 3, '能量 3');
assert(C.resonance === 4, 'D4 回合开始共振 +4：' + C.resonance);
assert(C.enemies[0].hp >= 18 && C.enemies[0].hp <= 24, '敌人血量在区间内：' + C.enemies[0].hp);
assert(C.enemies[0].intent !== null, '敌人有意图：' + JSON.stringify(C.enemies[0].intent));

// 3. 出牌
let played = 0;
for (let i = 0; i < C.hand.length; i++) {
  const r = RA.playCard(C, 0, 0);
  if (r.ok) played++;
  if (C.energy <= 0) break;
}
assert(played > 0, '至少打出一张牌（打出 ' + played + ' 张）');

// 4. 结束回合，走 10 个回合
let turns = 0;
while (!C.over && turns < 20) {
  RA.endTurn(C);
  turns++;
  // 每回合都出牌
  for (let k = 0; k < 5; k++) {
    const r = RA.playCard(C, 0, 0);
    if (!r.ok) break;
  }
}
assert(C.over || turns >= 10, '战斗在 20 回合内结束或推进到 10 回合（实际 ' + turns + ' 回合）');
assert(C.result === 'win' || C.result === 'lose' || C.result === null, '结果为 win/lose/null：' + C.result);

// 5. 共振阈值触发
let run3 = RA.newRun('diver', { seed: 99 });
run3.depth = 8;
let C3 = RA.startCombat(run3, [{ name: '墟蛹', hp: 200, tier: 'boss',
  intent_pattern: [{ type: 'attack', value: 10 }] }]);
for (let t = 0; t < 4; t++) RA.endTurn(C3);
assert(C3.resonance >= 20, 'D8 四回合后共振达到 20+：' + C3.resonance);
const firedLogs = C3.log.filter(l => l.indexOf('共振') >= 0);
assert(firedLogs.length > 0, '共振阈值有触发日志：' + firedLogs.length + ' 条');

// 6. 代价系统
let run4 = RA.newRun('tremor', { seed: 5 });
run4.depth = 3;
const beforeDeck = run4.deck.length;
run4.deck.push(Object.assign({}, {
  id: 'test_cost', name: '读一段别人的记忆', type: 'attack', rarity: 'rare',
  veins: ['tremor'], energy: 1,
  effect: { damage: 12, block: 0, hits: 1, target: 'single' },
  cost_type: 'memory', flavor: '它会记得你读过它。'
}));
let C4 = RA.startCombat(run4, [{ name: '硬矿洞蛇', hp: 30, tier: 'normal',
  intent_pattern: [{ type: 'attack', value: 4 }] }]);
// 找到那张代价牌
let idx = C4.hand.findIndex(c => c.cost_type === 'memory');
if (idx < 0) {
  // 手动抽到手上
  idx = C4.drawPile.findIndex(c => c.cost_type === 'memory');
  if (idx >= 0) { C4.hand.push(C4.drawPile.splice(idx, 1)[0]); idx = C4.hand.length - 1; }
}
if (idx >= 0) {
  const before = run4.deck.length;
  RA.playCard(C4, idx, 0);
  assert(run4.deck.length === before - 1, 'memory 代价删掉 1 张牌：' + before + ' → ' + run4.deck.length);
} else {
  console.log('  --  代价牌未进手牌，跳过断言');
}

// 7. 凝视加成
let run5 = RA.newRun('diver', { seed: 11 });
run5.depth = 2;
run5.gaze = 30;
let C5 = RA.startCombat(run5, [{ name: '冷洞食腐鳗', hp: 999, tier: 'normal',
  intent_pattern: [{ type: 'attack', value: 10 }] }]);
const hpBefore = run5.hp;
RA.endTurn(C5);
const dmgTaken = hpBefore - run5.hp;
assert(dmgTaken >= 13, '凝视 30 时 10 点攻击放大到 13+（实际 ' + dmgTaken + '）');

// 8. 层规则：D1 无红光
let run6 = RA.newRun('diver', { seed: 3 });
run6.depth = 1;
let C6 = RA.startCombat(run6, [{ name: '耐辐射孢子', hp: 10, tier: 'normal',
  intent_pattern: [{ type: 'attack', value: 1 }] }]);
C6.hand.push({ id: 'light_test', name: '光导透镜', type: 'attack', veins: ['light'],
  energy: 1, effect: { damage: 99, target: 'single' }, cost_type: 'none' });
const ehpBefore = C6.enemies[0].hp;
RA.playCard(C6, C6.hand.length - 1, 0);
assert(C6.enemies[0].hp === ehpBefore, 'D1 光脉卡无效（敌人未掉血）');

// 9. 卡牌升级
const baseCard = {
  id: 'test_up', name: '测试牌', type: 'attack', rarity: 'common', veins: [], energy: 1,
  effect: { damage: 10, hits: 1, target: 'single', special: [{ code: 'exhaust' }] },
  cost_type: 'none', flavor: '原来的样子。',
  upgrade: { name_suffix: '·改', effect: { damage: 15, special: [] }, flavor_add: '后来的样子。' }
};
const up = RA.upgradeCard(baseCard);
assert(up !== null && up !== baseCard, 'upgradeCard 返回新对象');
assert(baseCard.effect.damage === 10 && !baseCard.upgraded, '原卡未被修改');
assert(up.name === '测试牌·改', '名字加了后缀：' + up.name);
assert(up.effect.damage === 15, 'effect 数值合并：' + up.effect.damage);
assert(Array.isArray(up.effect.special) && up.effect.special.length === 0, '空 special 清空原特殊效果');
assert(up.flavor.indexOf('后来的样子。') >= 0, 'flavor_add 已追加');
assert(up.cost_type === 'none', '未指定的 cost_type 保持原样');
const upCost = RA.upgradeCard(Object.assign({}, baseCard, { upgrade: { name_suffix: '·新', effect: {}, cost_type: 'mark' } }));
assert(upCost.cost_type === 'mark', 'cost_type 可改写');
assert(RA.upgradeCard(up) === null, '已升级的卡不能再升级');
assert(RA.upgradeCard({ name: '无升级' }) === null, '无 upgrade 字段返回 null');

// 11. 苍民双世界（T24）
{
  const runC = RA.newRun('cangmin', { seed: 21 });
  assert(runC.hp === 30 && runC.clarity === 3 && runC.dreamMaxHp === 60, '苍民建局：醒 30 / 清醒 3 / 梦 60');
  runC.depth = 1;
  let CC = RA.startCombat(runC, [{ name: '浅海鳗', hp: 999, tier: 'normal', intent_pattern: [{ type: 'attack', value: 1 }] }]);
  assert(CC.world === 'wake', '开局在醒侧');
  const clarityBefore = runC.clarity;
  const sw = RA.switchWorld(CC, 'dream');
  assert(sw.ok && runC.clarity === clarityBefore - 1 && CC.world === 'dream', '入梦消耗清醒度');
  assert(CC.dreamHp === 60, '入梦时梦体回满');
  CC.hand.push({ id: 'wt', name: '石矛', type: 'attack', veins: [], energy: 0, effect: { damage: 5, target: 'single' }, cost_type: 'none', dream: false });
  const rW = RA.playCard(CC, CC.hand.length - 1, 0);
  assert(!rW.ok && rW.msg.indexOf('醒着') >= 0, '梦中不能打清醒牌：' + rW.msg);
  // 对照：梦中的世界能打梦牌
  CC.hand.push({ id: 'dt0', name: '火母的低语', type: 'attack', veins: [], energy: 0, effect: { damage: 5, target: 'single' }, cost_type: 'none', dream: true });
  const ehp0 = CC.enemies[0].hp;
  const rOK = RA.playCard(CC, CC.hand.length - 1, 0);
  assert(rOK.ok && CC.enemies[0].hp === ehp0 - 5, '梦中可以打梦牌');
  // 醒侧不能打梦牌
  RA.switchWorld(CC, 'wake');
  CC.hand.push({ id: 'dt2', name: '火母的低语', type: 'attack', veins: [], energy: 0, effect: { damage: 5, target: 'single' }, cost_type: 'none', dream: true });
  const rD2 = RA.playCard(CC, CC.hand.length - 1, 0);
  assert(!rD2.ok && rD2.msg.indexOf('梦') >= 0, '醒侧不能打梦牌：' + rD2.msg);
  RA.switchWorld(CC, 'dream');
  CC.dreamHp = 5;
  const wakeBefore = runC.hp;
  RA.damagePlayer(CC, 12, '测试');
  assert(CC.world === 'wake', '梦破强制醒来');
  assert(runC.hp === wakeBefore - 4, '反噬 50%：' + wakeBefore + '→' + runC.hp + '（溢出 7，反噬 4）');
  assert(!runC.dead, '梦死不真死');
  runC.clarity = 0;
  const rEx = RA.switchWorld(CC, 'dream');
  assert(!rEx.ok && rEx.msg.indexOf('清醒度') >= 0, '清醒度耗尽无法入梦');
  // 梦中耗尽路径：clarity=1 入梦，3 回合后强制醒 + 锁梦
  runC.clarity = 1;
  const rRe = RA.switchWorld(CC, 'dream');
  assert(rRe.ok && runC.clarity === 0, '以最后 1 点清醒度入梦');
  RA.endTurn(CC);
  RA.endTurn(CC);
  RA.endTurn(CC);
  assert(CC.world === 'wake' && CC.dreamLocked === true, '梦中清醒度耗尽 → 强制醒 + 本场锁梦');
  const rLock = RA.switchWorld(CC, 'dream');
  assert(!rLock.ok, '锁梦后不能再入梦');
}

console.log('\n=== 测试结束 ===');
if (process.exitCode) console.error('\n有失败项');
else console.log('\n全部通过');
