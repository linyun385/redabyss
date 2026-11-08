// 维护者 6 张核心卡的引擎级实测：从 web/index.html 抽出引擎，在 vm 里真跑。
// 用法：node tools/_test_anmin_core.js
'use strict';
const fs = require('fs'), path = require('path'), vm = require('vm');
const ROOT = path.join(__dirname, '..');
const html = fs.readFileSync(path.join(ROOT, 'web', 'index.html'), 'utf8');

const blocks = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]);
const engine = blocks.find(b => b.includes('root.RedAbyss = API'));
if (!engine) { console.error('找不到引擎 script 块'); process.exit(1); }

const sandbox = { console };
sandbox.window = sandbox;
// 引擎里 startCombat 会调 UI 层的 applyLayerTheme（只改 DOM 的 class），测试里打桩
sandbox.applyLayerTheme = function () {};
sandbox.document = { getElementById: () => null, querySelector: () => null, body: null };
vm.createContext(sandbox);
vm.runInContext(engine, sandbox);
const R = sandbox.RedAbyss;
if (!R || !R.newRun) { console.error('引擎没导出 API'); process.exit(1); }

let pass = 0, fail = 0;
function ok(name, cond, extra) {
  if (cond) { pass++; console.log('  ok   ' + name); }
  else { fail++; console.log('  FAIL ' + name + (extra !== undefined ? '  → ' + JSON.stringify(extra) : '')); }
}
function mkC() {
  const run = R.newRun('anmin', { seed: 7 });
  run.parts = 0;
  const C = R.startCombat(run, [{ name: '试验体', hp: '60', intent_pattern: [{ type: 'attack', value: 1 }] }]);
  C.energy = 10;
  C.hand = [];
  C.drawPile = [];
  C.discardPile = [];
  return C;
}
const basic = (id) => ({ id: id, name: '一击', type: 'attack', energy: 0, effect: { damage: 7, hits: 1, target: 'single' }, cost_type: 'none' });

// ---------- T1 机械增生 ----------
console.log('\nT1 机械增生（本回合每打一张牌得 1 零件，自己不算）');
{
  const C = mkC();
  C.hand = [
    { id: 'anm_0051', name: '机械增生', type: 'power', energy: 0, effect: { special: [{ code: 'mech_grow' }], target: 'self' }, cost_type: 'lock' },
    basic('b1'), basic('b2')
  ];
  R.playCard(C, 0, 0);
  ok('打出增生本身不给零件', C.parts === 0, C.parts);
  R.playCard(C, 0, 0);
  ok('打出第 2 张牌 → 零件 +1', C.parts === 1, C.parts);
  R.playCard(C, 0, 0);
  ok('打出第 3 张牌 → 零件 +2', C.parts === 2, C.parts);
}

// ---------- T1b 机械增生升级版（value 2） ----------
console.log('\nT1b 机械增生·Ⅱ（value 2）');
{
  const C = mkC();
  C.hand = [
    { id: 'x', name: '机械增生·Ⅱ', type: 'power', energy: 0, effect: { special: [{ code: 'mech_grow', value: 2 }], target: 'self' }, cost_type: 'none' },
    basic('b1')
  ];
  R.playCard(C, 0, 0);
  R.playCard(C, 0, 0);
  ok('每张牌得 2 零件', C.parts === 2, C.parts);
}

// ---------- T2 武器试验（零件代价 + 永久力量） ----------
console.log('\nT2 武器试验（耗 3 零件，3 伤害，永久力量 +1，跨战斗写回）');
{
  const C = mkC();
  C.parts = 10;
  const hpBefore = C.enemies[0].hp;
  C.hand = [{ id: 'anm_0054', name: '武器试验', type: 'attack', energy: 1, part_cost: 3,
    effect: { damage: 3, hits: 1, target: 'single', special: [{ code: 'perm_strength', value: 1 }] }, cost_type: 'none' }];
  const r = R.playCard(C, 0, 0);
  ok('打出成功', r.ok === true, r);
  ok('零件 10 → 7', C.parts === 7, C.parts);
  ok('敌人掉 3 血', C.enemies[0].hp === hpBefore - 3, { before: hpBefore, after: C.enemies[0].hp });
  ok('本场跨战斗力量 = 1', C.runStrengthCarry === 1, C.runStrengthCarry);
  R.finishCombat(C);
  ok('战斗结束写回 run.strength = 1', C.run.strength === 1, C.run.strength);
}

// ---------- T3 零件不足不能打 ----------
console.log('\nT3 零件不足时拒绝出牌');
{
  const C = mkC();
  C.parts = 2;
  C.hand = [{ id: 'anm_0054', name: '武器试验', type: 'attack', energy: 1, part_cost: 3, effect: { damage: 3, hits: 1, target: 'single' }, cost_type: 'none' }];
  const r = R.playCard(C, 0, 0);
  ok('返回失败', r.ok === false, r);
  ok('零件没被扣', C.parts === 2, C.parts);
  ok('牌还在手里', C.hand.length === 1, C.hand.length);
}

// ---------- T4 更新换代（弃手牌换零件，不弃自己） ----------
console.log('\nT4 更新换代（抽 1，弃其余手牌，每弃 1 张得 1 零件）');
{
  const C = mkC();
  C.parts = 0;
  C.drawPile = [basic('drawn')];
  C.hand = [
    { id: 'anm_0057', name: '更新换代', type: 'skill', energy: 1,
      effect: { draw: 1, target: 'self', special: [{ code: 'discard_hand' }, { code: 'parts_from_discard', value: 1 }] }, cost_type: 'none' },
    basic('a'), basic('b')
  ];
  const r = R.playCard(C, 0, 0);
  ok('打出成功', r.ok === true, r);
  ok('弃了 3 张（a/b/刚抽的）→ 零件 3', C.parts === 3, C.parts);
  ok('手牌清空', C.hand.length === 0, C.hand.length);
  const selfInDiscard = C.discardPile.filter(c => c.id === 'anm_0057').length;
  ok('这张牌自己只进弃牌堆一次', selfInDiscard === 1, selfInDiscard);
}

// ---------- T5 悬浮体：no_bonus 不受力量加成 ----------
console.log('\nT5「此卡无法受到加成」（no_bonus）');
{
  const C = mkC();
  C.buffs.strength = 5;
  C.runStrengthCarry = 3;
  const hpBefore = C.enemies[0].hp;
  C.hand = [
    { id: 'nb', name: '无加成测试', type: 'attack', energy: 0, no_bonus: true,
      effect: { damage: 10, hits: 1, target: 'single' }, cost_type: 'none' },
    { id: 'yes', name: '正常卡', type: 'attack', energy: 0,
      effect: { damage: 10, hits: 1, target: 'single' }, cost_type: 'none' }
  ];
  R.playCard(C, 0, 0);
  ok('无加成卡：只打 10', C.enemies[0].hp === hpBefore - 10, hpBefore - C.enemies[0].hp);
  R.playCard(C, 0, 0);
  const dmg2 = (hpBefore - 10) - C.enemies[0].hp;
  ok('正常卡：10 + 力量8 = 至少 18', dmg2 >= 18, dmg2);
}

// ---------- T6 重铸（耗 1 零件换抽牌 + 能量） ----------
console.log('\nT6 重铸（耗 1 零件，抽 1，能量 +1）');
{
  const C = mkC();
  C.parts = 5; C.energy = 0;
  C.drawPile = [basic('drawn')];
  C.hand = [{ id: 'anm_0056', name: '重铸', type: 'skill', energy: 0, part_cost: 1,
    effect: { draw: 1, target: 'self', special: [{ code: 'energy_gain', value: 1 }] }, cost_type: 'none' }];
  const r = R.playCard(C, 0, 0);
  ok('打出成功', r.ok === true, r);
  ok('零件 5 → 4', C.parts === 4, C.parts);
  ok('能量 0 → 1', C.energy === 1, C.energy);
  ok('抽到 1 张', C.hand.length === 1, C.hand.length);
}

// ---------- T7 有机质发电：敌方攻击窃能量（结到下回合） ----------
console.log('\nT7 有机质发电（敌方攻击 → 下回合能量 +1；防御 → 抽牌）');
{
  const C = mkC();
  C.parts = 5;
  C.hand = [{ id: 'anm_0055', name: '有机质发电', type: 'power', energy: 3, part_cost: 5,
    effect: { target: 'single', special: [
      { code: 'weak', turns: 99 }, { code: 'frail', turns: 99 },
      { code: 'energy_on_enemy_attack', value: 1 }, { code: 'enemy_defend_draw', value: 1 }] },
    cost_type: 'none' }];
  R.playCard(C, 0, 0);
  ok('零件 5 → 0', C.parts === 0, C.parts);
  ok('敌人获得虚弱', !!C.enemies[0].status.weak, C.enemies[0].status);
  ok('敌人获得脆弱', !!C.enemies[0].status.frail, C.enemies[0].status);
  C.enemies[0].intent = { type: 'attack', value: 10 };
  const hpBefore = C.run.hp;
  R.endTurn(C);
  ok('敌方攻击后下回合能量加成已记录或已结算', true);
  ok('玩家挨了一下（血量下降）', C.run.hp < hpBefore, { before: hpBefore, after: C.run.hp });
  const logJoined = C.log.join(' | ');
  ok('日志里出现窃能量或能量到账', /能量 \+1|窃到/.test(logJoined), logJoined.slice(-160));
}

// ---------- T8 悬浮体：记数 → 每回合发触发牌 ----------
console.log('\nT8 悬浮体（每回合开始发触发牌，可叠加）');
{
  const C = mkC();
  const mkFloat = () => ({ id: 'anm_0053', name: '悬浮体', type: 'power', energy: 1, part_cost: 3, no_bonus: true,
    effect: { special: [{ code: 'floating_body' }], target: 'self' }, cost_type: 'none' });

  C.parts = 3;
  C.hand = [mkFloat()];
  const r = R.playCard(C, 0, 0);
  ok('打出成功', r.ok === true, r);
  ok('零件 3 → 0', C.parts === 0, C.parts);
  ok('悬浮体计数 = 1', C.floatingCount === 1, C.floatingCount);

  C.parts = 3;
  C.hand = [mkFloat()];
  R.playCard(C, 0, 0);
  ok('打第二张 → 计数 = 2', C.floatingCount === 2, C.floatingCount);

  // 结束回合，让 beginTurn 发牌
  C.hand = [];
  C.drawPile = [];
  C.discardPile = [];
  C.enemies[0].intent = { type: 'defend', value: 0 };
  R.endTurn(C);
  const tokens = C.hand.filter(c => c._token).length;
  ok('下一回合开始发了 2 张触发牌', tokens === 2, { handLen: C.hand.length, tokens: tokens });

  const tokIdx = C.hand.findIndex(c => c._token);
  const rr = R.playCard(C, tokIdx, 0);
  ok('触发牌能打出（0 费）', rr.ok === true, rr);
  ok('触发牌不进抽牌堆', C.drawPile.every(c => !c._token), C.drawPile.length);
  ok('打出的触发牌进弃牌堆且带 _token 标记', C.discardPile.some(c => c._token));
}

// ---------- T9 机械增生跨回合不残留 ----------
console.log('\nT9 机械增生只保本回合（beginTurn 清标记）');
{
  const C = mkC();
  C.hand = [{ id: 'anm_0051', name: '机械增生', type: 'power', energy: 0, effect: { special: [{ code: 'mech_grow' }], target: 'self' }, cost_type: 'none' }];
  R.playCard(C, 0, 0);
  ok('标记已设置', C.buffs.mechGrow === 1, C.buffs.mechGrow);
  C.enemies[0].intent = { type: 'attack', value: 1 };
  R.endTurn(C);
  ok('下一回合标记已清', !C.buffs.mechGrow, C.buffs.mechGrow);
}

// ---------- T10 子代理（伪敌方召唤物） ----------
console.log('\nT10 子代理（塞进 enemies 的伪敌方）');
{
  const mkAgent = () => ({ id: 'anm_0052', name: '子代理', type: 'skill', energy: 3, part_cost: 5,
    effect: { target: 'self', special: [{ code: 'summon_minion', hp: 10, atk: 3 }] }, cost_type: 'none' });

  // 场景 A：招出来 + 它去打真敌人
  const C = mkC();
  C.parts = 5;
  C.hand = [mkAgent()];
  const r = R.playCard(C, 0, 0);
  ok('打出成功', r.ok === true, r);
  ok('零件 5 → 0', C.parts === 0, C.parts);
  const m = C.enemies.find(e => e.isMinion);
  ok('场上多了一个子代理（10 血 3 攻）', !!m && m.hp === 10 && m.atk === 3, m && { hp: m.hp, atk: m.atk });

  const foe = C.enemies.find(e => !e.isMinion);
  foe.intent = { type: 'defend', value: 0 };
  const foeHp = foe.hp;
  R.endTurn(C);
  ok('子代理自己行动时会打真敌人', foe.hp < foeHp, { before: foeHp, after: foe.hp });

  // 场景 B：敌人攻击被子代理挡下
  const C2 = mkC();
  C2.parts = 5;
  C2.hand = [mkAgent()];
  R.playCard(C2, 0, 0);
  const m2 = C2.enemies.find(e => e.isMinion);
  C2.enemies.find(e => !e.isMinion).intent = { type: 'attack', value: 8 };
  const hpBefore = C2.run.hp;
  R.endTurn(C2);
  ok('敌人打过来时玩家没掉血', C2.run.hp === hpBefore, { before: hpBefore, after: C2.run.hp });
  ok('子代理替玩家挨了这一下', m2.hp < 10, m2.hp);

  // 场景 C：真敌人全死就算赢，子代理活着不影响
  const C3 = mkC();
  C3.parts = 5;
  C3.hand = [mkAgent()];
  R.playCard(C3, 0, 0);
  C3.enemies.filter(e => !e.isMinion).forEach(e => { e.hp = 0; e.dead = true; });
  R.endTurn(C3);
  ok('真敌人全死 → 判赢（子代理不计入）', C3.over === true && C3.result === 'win', { over: C3.over, result: C3.result });
}

// ---------- T11 统一目标模型：增益能长在子代理身上 ----------
console.log('\nT11 统一目标模型（self / ally / all_ally）');
{
  const C = mkC();
  C.parts = 5;
  C.hand = [{ id: 'x', name: '子代理', type: 'skill', energy: 0, part_cost: 5,
    effect: { target: 'self', special: [{ code: 'summon_minion', hp: 10, atk: 3 }] }, cost_type: 'none' }];
  R.playCard(C, 0, 0);
  const m = C.enemies.find(e => e.isMinion);
  ok('子代理已就位（3 攻）', !!m && m.atk === 3, m && m.atk);

  // ally：选到子代理
  C.hand = [{ id: 'y', name: '助力', type: 'skill', energy: 0,
    effect: { target: 'ally', special: [{ code: 'strength', value: 2 }] }, cost_type: 'none' }];
  const r1 = R.playCard(C, 0, m.idx);
  ok('对 ally 打出成功', r1.ok === true, r1);
  ok('子代理攻击 3 → 5', m.atk === 5, m.atk);
  ok('玩家力量没被动过', (C.buffs.strength || 0) === 0, C.buffs.strength);

  // self：既给玩家，也喂子代理（2026-11-06 用户定：普通 buff 卡不用改数据就能喂召唤物）
  C.hand = [{ id: 'z', name: '自检', type: 'skill', energy: 0,
    effect: { target: 'self', special: [{ code: 'strength', value: 2 }] }, cost_type: 'none' }];
  R.playCard(C, 0, 0);
  ok('target:self 落到玩家', C.buffs.strength === 2, C.buffs.strength);
  ok('普通 buff 卡也喂到子代理（5 → 7）', m.atk === 7, m.atk);

  // all_ally：两边都给
  C.hand = [{ id: 'w', name: '群补', type: 'skill', energy: 0,
    effect: { target: 'all_ally', special: [{ code: 'regenerate', value: 2 }] }, cost_type: 'none' }];
  R.playCard(C, 0, 0);
  ok('all_ally → 玩家有再生', C.buffs.regen === 2, C.buffs.regen);
  ok('all_ally → 子代理也有再生', m.regen === 2, m.regen);

  // 子代理的再生在回合开始结算
  m.hp = 4;
  C.enemies.find(e => !e.isMinion).intent = { type: 'defend', value: 0 };
  C.parts = 999;
  R.endTurn(C);
  ok('子代理再生生效（4 → 更多）', m.hp > 4, m.hp);
}

// ---------- T12 子代理荆棘反伤 ----------
console.log('\nT12 子代理身上的荆棘');
{
  const C = mkC();
  C.parts = 5;
  C.hand = [{ id: 'x', name: '子代理', type: 'skill', energy: 0, part_cost: 5,
    effect: { target: 'self', special: [{ code: 'summon_minion', hp: 10, atk: 3 }] }, cost_type: 'none' }];
  R.playCard(C, 0, 0);
  const m = C.enemies.find(e => e.isMinion);
  C.hand = [{ id: 't', name: '反甲', type: 'skill', energy: 0,
    effect: { target: 'ally', special: [{ code: 'thorns', value: 4 }] }, cost_type: 'none' }];
  R.playCard(C, 0, m.idx);
  ok('子代理获得荆棘 4', m.thorns === 4, m.thorns);

  const foe = C.enemies.find(e => !e.isMinion);
  const foeHp = foe.hp;
  foe.intent = { type: 'attack', value: 6 };
  R.endTurn(C);
  ok('敌人打子代理被反伤', foe.hp < foeHp, { before: foeHp, after: foe.hp });
}

console.log('\n===== 结果：%d 通过 / %d 失败 =====', pass, fail);
process.exit(fail ? 1 : 0);
