// T24：苍民双世界引擎。锚点替换，test_engine 必须全绿。
'use strict';
const fs = require('fs');
const path = require('path');
const ROOT = path.join(__dirname, '..');
let core = fs.readFileSync(path.join(ROOT, 'engine/core.js'), 'utf8');
function rep(anchor, replacement, tag) {
  if (!core.includes(anchor)) { console.error('FAIL 锚点未找到: ' + tag); process.exit(1); }
  core = core.replace(anchor, replacement);
}

// 1. newRun：cangmin 分支（醒 30 / 梦 60 / 清醒度 3）
rep(`      : classId === 'anmin'
        ? { hp: 76, deck: null }
        : { hp: 72, deck: null };`,
`      : classId === 'anmin'
        ? { hp: 76, deck: null }
        : classId === 'cangmin'
          ? { hp: 30, deck: null }
          : { hp: 72, deck: null };`, 'cangmin hp');
rep(`    if (classId === 'anmin') {`,
`    if (classId === 'cangmin') {
      run.clarity = 3;
      run.clarityMax = 5;
      run.dreamMaxHp = 60;
    }
    if (classId === 'anmin') {`, 'cangmin clarity');
// 苍民初始牌：醒 5（弱）+ 梦 5（强）
rep(`    if (classId === 'anmin') {`,
`    if (classId === 'cangmin') {
      const wAtk = { id: 'cng_w_atk', name: '石矛', type: 'attack', rarity: 'common', veins: [], energy: 1,
        effect: { damage: 5, target: 'single' }, cost_type: 'none', dream: false, flavor: '醒着的时候，这就够用了。' };
      const wDef = { id: 'cng_w_def', name: '缩进岩洞', type: 'skill', rarity: 'common', veins: [], energy: 1,
        effect: { block: 5, target: 'self' }, cost_type: 'none', dream: false, flavor: '岩洞是最后的墙。' };
      const dAtk = { id: 'cng_d_atk', name: '火母的低语', type: 'attack', rarity: 'common', veins: ['heat'], energy: 1,
        effect: { damage: 9, target: 'single' }, cost_type: 'none', dream: true, flavor: '梦里打人，用想念。' };
      const dDef = { id: 'cng_d_def', name: '火母的注视', type: 'skill', rarity: 'common', veins: ['heat'], energy: 1,
        effect: { block: 8, target: 'self' }, cost_type: 'none', dream: true, flavor: '被她看着的伤口，不敢流血。' };
      add(wAtk, 2); add(wDef, 3); add(dAtk, 3); add(dDef, 2);
    } else if (classId === 'anmin') {`, 'cangmin starter');

// 2. startCombat：双世界状态
rep(`      parts: 0,
      activeProtocol: null,
      threatLevel: 0,
      veinLocked: false,`,
`      parts: 0,
      activeProtocol: null,
      threatLevel: 0,
      world: (run.classId === 'cangmin') ? 'wake' : undefined,
      dreamHp: (run.classId === 'cangmin') ? (run.dreamMaxHp || 60) : undefined,
      dreamMaxHp: (run.classId === 'cangmin') ? (run.dreamMaxHp || 60) : undefined,
      omens: [],
      veinLocked: false,`, 'combat world state');
// 双牌堆初始化（苍民）：把 run.deck 按 dream 字段拆进 pileWake / pileDream
rep(`    // 洗牌
    C.drawPile = shuffle(run.deck.map(c => Object.assign({}, c)), C.rng);`,
`    // 洗牌
    if (run.classId === 'cangmin') {
      C.pileWake = shuffle(run.deck.filter(c => !c.dream).map(c => Object.assign({}, c)), C.rng);
      C.pileDream = shuffle(run.deck.filter(c => c.dream).map(c => Object.assign({}, c)), C.rng);
      C.drawPile = C.pileWake;
      C.pileWake = [];
    } else {
      C.drawPile = shuffle(run.deck.map(c => Object.assign({}, c)), C.rng);
    }`, 'dual piles init');

// 3. 打牌世界校验
rep(`    // 黯民协议：不可重复激活`,
`    // 苍民双世界：世界不匹配的牌不能打
    if (C.run.classId === 'cangmin' && C.world) {
      const wantDream = C.world === 'dream';
      if (!!card.dream !== wantDream) {
        return { ok: false, msg: card.dream ? '这来自梦里，醒着的手握不住' : '醒着的东西进不了这个深度' };
      }
    }
    // 黯民协议：不可重复激活`, 'world gate');

// 4. 切世 API + 预兆
rep(`  function activateProtocol(C, name) {`,
`  // ============ 苍民：双世界 ============
  function rebuildWorldPiles(C, target) {
    // 把当前世界的抽/弃堆归位，再从目标世界的堆洗出新抽牌堆
    if (C.world === 'wake') C.pileWake = C.pileWake.concat(C.drawPile, C.discardPile);
    else C.pileDream = C.pileDream.concat(C.drawPile, C.discardPile);
    C.discardPile = [];
    if (target === 'dream') {
      C.drawPile = shuffle(C.pileDream, C.rng);
      C.pileDream = [];
    } else {
      C.drawPile = shuffle(C.pileWake, C.rng);
      C.pileWake = [];
    }
  }
  function switchWorld(C, target) {
    if (C.run.classId !== 'cangmin' || C.world === target) return { ok: false, msg: '无效切世' };
    if (target === 'dream') {
      if (C.dreamLocked) return { ok: false, msg: '本场已强制醒来，不能再入梦' };
      if (C.run.clarity <= 0) return { ok: false, msg: '清醒度耗尽，无法入梦' };
      C.run.clarity -= 1;
      C.world = 'dream';
      C.dreamHp = C.dreamMaxHp;
      log(C, '〔入梦〕清醒度 -1（余 ' + C.run.clarity + '）。火母的领地还认得你。');
    } else {
      C.world = 'wake';
      C.run.hp = Math.min(C.run.maxHp, C.run.hp + 3);
      log(C, '〔醒来〕身体 +3。枕头边放着一个没做完的梦。');
    }
    // 手牌归还当前世界堆，重建目标世界牌堆，抽满
    const hand = C.hand.splice(0, C.hand.length);
    if (C.world === 'dream') C.pileDream = C.pileDream.concat(hand);
    else C.pileWake = C.pileWake.concat(hand);
    rebuildWorldPiles(C, target);
    C.hand = [];
    draw(C, DRAW_PER_TURN);
    return { ok: true };
  }
  function forceWake(C, reason) {
    if (C.world !== 'dream') return;
    C.world = 'wake';
    if (C.run.clarity <= 0) C.dreamLocked = true;
    const hand = C.hand.splice(0, C.hand.length);
    C.pileDream = C.pileDream.concat(hand);
    rebuildWorldPiles(C, 'wake');
    C.hand = [];
    draw(C, DRAW_PER_TURN);
    log(C, '〔强制醒来〕' + reason);
  }
  // 预兆：每回合开始抽一张，3 回合后结算，最多同时 3 张
  const OMENS = [
    { name: '吉兆：火母的余温', good: true, apply: (C) => { C.energy += 1; log(C, '〔预兆〕火母的余温：本回合能量 +1。'); } },
    { name: '凶兆：影子先行', good: false, apply: (C) => { const e = C.enemies.find(x => !x.dead); if (e) { e.buffAtk = (e.buffAtk || 0) + 1; log(C, '〔预兆〕影子先行：' + e.name + ' 攻击 +1。'); } } },
    { name: '吉兆：浅海的渔获', good: true, apply: (C) => { healPlayer(C, 3); log(C, '〔预兆〕浅海的渔获：回复 3 点。'); } },
    { name: '凶兆：名字被念到', good: false, apply: (C) => { if (C.hand.length) { const i = Math.floor(C.rng() * C.hand.length); log(C, '〔预兆〕名字被念到：「' + C.hand[i].name + '」被弃置。'); C.hand.splice(i, 1); } } }
  ];
  function tickOmens(C) {
    if (C.run.classId !== 'cangmin') return;
    for (let i = C.omens.length - 1; i >= 0; i--) {
      C.omens[i].turnsLeft -= 1;
      if (C.omens[i].turnsLeft <= 0) {
        C.omens[i].def.apply(C);
        C.omens.splice(i, 1);
      }
    }
    if (C.omens.length < 3) {
      const def = OMENS[Math.floor(C.rng() * OMENS.length)];
      C.omens.push({ def: def, turnsLeft: 3 });
      log(C, '〔预兆〕' + def.name + '（3 回合后应验）。');
    }
  }

  function activateProtocol(C, name) {`, 'switch world + omens');

// 5. beginTurn：梦中心跳（每 3 回合清醒度 -1）+ 预兆
rep(`    // 3. 共振 += 层深度
    C.resonance += C.layer.res;`,
`    // 3. 共振 += 层深度
    C.resonance += C.layer.res;
    // 苍民：梦中心跳（清醒度消耗）与预兆
    if (C.run.classId === 'cangmin') {
      if (C.world === 'dream' && C.turn % 3 === 0 && C.turn > 0) {
        C.run.clarity = Math.max(0, C.run.clarity - 1);
        log(C, '〔梦太深〕清醒度 -1（余 ' + C.run.clarity + '）。');
        if (C.run.clarity <= 0) forceWake(C, '清醒度耗尽。本场不能再入梦。');
      }
      if (!C.over) tickOmens(C);
    }`, 'beginTurn dream tick');

// 6. 伤害/治疗路由到对应身体
rep(`function damagePlayer(C, amount, source) {
    if (C.over) return;
    const run = C.run;
    let dmg = amount;
    const absorbed = Math.min(C.block, dmg);
    C.block -= absorbed;
    dmg -= absorbed;
    if (dmg > 0) {
      run.hp -= dmg;
      log(C, '你受到 ' + dmg + ' 伤害' + (source ? '（' + source + '）' : '') + '。');
    }
    if (run.hp <= 0) {
      run.hp = 0;
      C.over = true;
      C.result = 'lose';
      run.dead = true;
      log(C, '你的血在红光里流尽了。');
    }
  }`,
`function damagePlayer(C, amount, source) {
    if (C.over) return;
    const run = C.run;
    let dmg = amount;
    const absorbed = Math.min(C.block, dmg);
    C.block -= absorbed;
    dmg -= absorbed;
    // 苍民：梦中受伤打的是梦的身体
    if (run.classId === 'cangmin' && C.world === 'dream') {
      if (dmg > 0) {
        C.dreamHp -= dmg;
        log(C, '梦中的身体受到 ' + dmg + ' 伤害' + (source ? '（' + source + '）' : '') + '。');
      }
      if (C.dreamHp <= 0) {
        const overflow = -C.dreamHp;
        const back = Math.ceil(overflow * 0.5);
        C.dreamHp = 0;
        C.world = 'wake';
        if (run.clarity <= 0) C.dreamLocked = true;
        const hand = C.hand.splice(0, C.hand.length);
        C.pileDream = C.pileDream.concat(hand);
        rebuildWorldPiles(C, 'wake');
        C.hand = [];
        draw(C, DRAW_PER_TURN);
        run.hp = Math.max(0, run.hp - back);
        log(C, '梦破了。反噬 ' + back + ' 点涌向醒着的身体，你醒了。');
        if (run.hp <= 0) {
          run.hp = 0;
          C.over = true;
          C.result = 'lose';
          run.dead = true;
          log(C, '反噬带走了最后一点生命。你再也没有醒来。');
        }
      }
      return;
    }
    if (dmg > 0) {
      run.hp -= dmg;
      log(C, '你受到 ' + dmg + ' 伤害' + (source ? '（' + source + '）' : '') + '。');
    }
    if (run.hp <= 0) {
      run.hp = 0;
      C.over = true;
      C.result = 'lose';
      run.dead = true;
      log(C, '你的血在红光里流尽了。');
    }
  }`, 'damage route');
rep(`function healPlayer(C, n) {
    const run = C.run;
    run.hp = Math.min(run.maxHp, run.hp + n);
  }`,
`function healPlayer(C, n) {
    const run = C.run;
    if (run.classId === 'cangmin' && C.world === 'dream') {
      C.dreamHp = Math.min(C.dreamMaxHp, C.dreamHp + n);
      return;
    }
    run.hp = Math.min(run.maxHp, run.hp + n);
  }`, 'heal route');
// 贯穿伤害（pierce）路由
rep(`        if (it.pierce) {
          C.run.hp -= dmg;
          log(C, e.name + ' 的振动从骨头里响起来，' + dmg + ' 点，格挡不住。');
        } else {`,
`        if (it.pierce) {
          damagePlayer(C, dmg, e.name + '的贯骨振动');
          log(C, e.name + ' 的振动从骨头里响起来，' + dmg + ' 点，格挡不住。');
        } else {`, 'pierce route');
// 阈值过载掉血（damagePlayer 已路由）；共振过载与灼烧都走 damagePlayer ✓

fs.writeFileSync(path.join(ROOT, 'engine/core.js'), core, 'utf8');
console.log('T24 引擎补丁完成');
delete require.cache[require.resolve(path.join(ROOT, 'engine/core.js'))];
const RA = require(path.join(ROOT, 'engine/core.js'));
const run = RA.newRun('cangmin', { rng: RA.makeRng(1) });
console.log('cangmin 建局自测: hp=' + run.hp + '/' + run.maxHp + ' clarity=' + run.clarity + ' dreamMax=' + run.dreamMaxHp + ' 牌组=' + run.deck.length);
