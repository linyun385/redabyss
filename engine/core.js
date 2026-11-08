/* 《红渊：下潜》战斗引擎核心 v1.0
 * 纯逻辑，无 DOM 依赖。浏览器与 node 均可加载。
 * 依据 DESIGN.md v1.0，所有数值以此为准。
 */

(function (root) {
  'use strict';

  // ============ 常量 ============
  const VEINS = ['light', 'water', 'heat', 'tremor', 'mineral'];
  const VEIN_CN = { light: '光', water: '水', heat: '热', tremor: '震', mineral: '矿' };
  const HAND_LIMIT = 10;
  const DRAW_PER_TURN = 5;
  const BASE_ENERGY = 3;

  // 各层定义（与 DESIGN.md §4 一致）
  const LAYERS = [
    { id: 1, name: '地表死寂区', protocol: 'L0–L1', res: 1, mode: 'dormant',  rule: 'no_light' },
    { id: 2, name: '外层冷洞',   protocol: 'L1',    res: 2, mode: 'dormant',  rule: 'cold' },
    { id: 3, name: '干旱空洞区', protocol: 'L1–L2', res: 3, mode: 'steady',   rule: 'dry' },
    { id: 4, name: '稳定空洞海', protocol: 'L2–L3', res: 4, mode: 'pulse',    rule: 'bright' },
    { id: 5, name: '热泉裂带',   protocol: 'L2–L4', res: 5, mode: 'resonant', rule: 'heat_tick' },
    { id: 6, name: '辐射矿石区', protocol: 'L4–L5', res: 6, mode: 'overload', rule: 'rad_tick' },
    { id: 7, name: '核心高热区', protocol: 'L5',    res: 7, mode: 'locked',   rule: 'burn_hand' },
    { id: 8, name: '红渊核心',   protocol: 'L6',    res: 8, mode: 'void',     rule: 'final' }
  ];

  // 七种模式的共振阈值反应
  const MODE_REACTION = {
    dormant:  { text: '共振之底没有回应。', apply: () => {} },
    steady:   { text: '红光稳定下来。', apply: (C) => { healPlayer(C, 3); } },
    pulse:    { text: '红光脉冲扫过。', apply: (C) => { C.enemies.forEach(e => dealToEnemy(C, e, 5)); } },
    resonant: { text: '震语清晰。', apply: (C) => { draw(C, 2); } },
    overload: { text: '局部失控。', apply: (C) => { C.enemies.forEach(e => { e.buffAtk = (e.buffAtk || 0) + 3; e.buffTurns = 1; }); } },
    locked:   { text: '时间感异常。', apply: (C) => { C.energyPenalty = 1; } },
    void:     { text: '红光消失。', apply: (C) => { C.veinLocked = true; } }
  };

  // ============ RNG（可种子化，便于复现） ============
  function makeRng(seed) {
    let s = (seed === undefined ? Date.now() : seed) >>> 0;
    return function () {
      s = (s * 1664525 + 1013904223) >>> 0;
      return s / 4294967296;
    };
  }
  function shuffle(arr, rng) {
    for (let i = arr.length - 1; i > 0; i--) {
      const j = Math.floor(rng() * (i + 1));
      [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    return arr;
  }
  function randInt(rng, a, b) { return a + Math.floor(rng() * (b - a + 1)); }
  function parseHp(rng, hp) {
    if (typeof hp === 'number') return hp;
    const m = String(hp).split('-').map(Number);
    return m.length === 2 ? randInt(rng, m[0], m[1]) : Number(hp);
  }

  // ============ Run（整局） ============
  function newRun(classId, opts) {
    opts = opts || {};
    const rng = opts.rng || makeRng(opts.seed);
    const base = classId === 'diver'
      ? { hp: 80, deck: null }
      : classId === 'anmin'
        ? { hp: 76, deck: null }
        : classId === 'cangmin'
          ? { hp: 30, deck: null }
          : { hp: 72, deck: null };

    const run = {
      classId: classId,          // 'diver' | 'tremor'
      hp: base.hp,
      maxHp: base.hp,
      energyMax: BASE_ENERGY,
      gaze: 0,                   // 凝视
      depth: 0,                  // 当前层
      node: 0,
      gold: 0,
      clarity: (classId === 'cangmin') ? 3 : undefined,
      clarityMax: (classId === 'cangmin') ? 5 : undefined,
      dreamMaxHp: (classId === 'cangmin') ? 60 : undefined,
      deck: [],                  // 牌组（card 对象数组，含 uid）
      relics: [],
      rng: rng,
      log: [],
      dead: false,
      won: false
    };
    run.deck = buildStarterDeck(classId, run.rng);
    return run;
  }

  function buildStarterDeck(classId, rng) {
    const list = [];
    let uid = 0;
    function add(card, n) {
      for (let i = 0; i < n; i++) {
        list.push(Object.assign({}, card, { uid: 'u' + (uid++) }));
      }
    }
    const atk = { id: 'basic_atk', name: '一击', type: 'attack', rarity: 'common', veins: [], energy: 1,
      effect: { damage: 7, block: 0, hits: 1, target: 'single' },
      cost_type: 'none', flavor: '你把手上的东西砸下去。它是在动的。',
      upgrade: { name_suffix: '·固', effect: { damage: 9 }, flavor_add: '砸了很多年之后，你知道往哪里砸。' } };
    const def = { id: 'basic_def', name: '缩起', type: 'skill', rarity: 'common', veins: [], energy: 1,
      effect: { damage: 0, block: 5, target: 'self' },
      cost_type: 'none', flavor: '你把自己收窄。红光从你身边绕过去。',
      upgrade: { name_suffix: '·旧', effect: { block: 8 }, flavor_add: '收窄的次数多了，红光自己绕路。' } };

    if (classId === 'cangmin') {
      const wAtk = { id: 'cng_w_atk', name: '石矛', type: 'attack', rarity: 'common', veins: [], energy: 1,
        effect: { damage: 5, target: 'single' }, cost_type: 'none', dream: false, flavor: '醒着的时候，这就够用了。' };
      const wDef = { id: 'cng_w_def', name: '缩进岩洞', type: 'skill', rarity: 'common', veins: [], energy: 1,
        effect: { block: 5, target: 'self' }, cost_type: 'none', dream: false, flavor: '岩洞是最后的墙。' };
      const dAtk = { id: 'cng_d_atk', name: '火母的低语', type: 'attack', rarity: 'common', veins: ['heat'], energy: 1,
        effect: { damage: 9, target: 'single' }, cost_type: 'none', dream: true, flavor: '梦里打人，用想念。' };
      const dDef = { id: 'cng_d_def', name: '火母的注视', type: 'skill', rarity: 'common', veins: ['heat'], energy: 1,
        effect: { block: 8, target: 'self' }, cost_type: 'none', dream: true, flavor: '被她看着的伤口，不敢流血。' };
      add(wAtk, 2); add(wDef, 3); add(dAtk, 3); add(dDef, 2);
    } else if (classId === 'anmin') {
      add(atk, 5);
      add(def, 4);
      add({ id: 'anmin_sign', name: '登记工号牌', type: 'skill', rarity: 'common', veins: ['mineral'], energy: 0,
        effect: { draw: 1, target: 'self' },
        cost_type: 'none', flavor: '编号确认。系统认出了你。这不算好事。' }, 1);
    } else if (classId === 'diver') {
      add(atk, 5);
      add(def, 4);
      add({ id: 'diver_sign', name: '死亡合同副本', type: 'skill', rarity: 'common', veins: ['mineral'], energy: 0,
        effect: { damage: 0, block: 0, draw: 1, target: 'self' },
        cost_type: 'none', flavor: '第三条写着：不保证返程。你签的时候没细看。' }, 1);
    } else {
      add(atk, 5);
      add(def, 4);
      add({ id: 'tremor_sign', name: '静日触杖', type: 'skill', rarity: 'common', veins: ['tremor'], energy: 0,
        effect: { damage: 0, block: 0, draw: 1, target: 'self' },
        cost_type: 'none', flavor: '杖头是温的。今天不该说话。' }, 1);
    }
    return list;
  }

  // ============ Combat（战斗） ============
  function startCombat(run, enemyDefs) {
    const layer = LAYERS[run.depth - 1] || LAYERS[0];
    const C = {
      run: run,
      layer: layer,
      turn: 1,
      energy: run.energyMax,
      energyPenalty: 0,
      resonance: 0,
      resonanceFired: 0,        // 已触发过的阈值档数
      hand: [],
      drawPile: [],
      discardPile: [],
      exhaustPile: [],
      block: 0,
      buffs: {},                // strength / dexterity / thorns / regen ...
      debuffs: {},
      veinChain: {},            // 各脉连携计数
      lastVein: null,
      enemies: [],
      parts: 0,
      activeProtocol: null,
      threatLevel: 0,
      world: (run.classId === 'cangmin') ? 'wake' : undefined,
      dreamHp: (run.classId === 'cangmin') ? (run.dreamMaxHp || 60) : undefined,
      dreamMaxHp: (run.classId === 'cangmin') ? (run.dreamMaxHp || 60) : undefined,
      omens: [],
      veinLocked: false,
      over: false,
      result: null,
      rng: run.rng,
      log: []
    };

    // 敌人实例化
    C.enemies = enemyDefs.map((d, i) => {
      const hp = parseHp(C.rng, d.hp);
      return {
        idx: i,
        def: d,
        name: d.name,
        hp: hp,
        maxHp: hp,
        block: 0,
        buffAtk: 0,
        buffTurns: 0,
        intentIdx: 0,
        intent: null,
        status: {},
        dead: false,
        phases: Array.isArray(d.phases) && d.phases.length ? d.phases : null,
        phaseIdx: -1
      };
    });

    // 洗牌
    if (run.classId === 'cangmin') {
      C.pileWake = shuffle(run.deck.filter(c => !c.dream).map(c => Object.assign({}, c)), C.rng);
      C.pileDream = shuffle(run.deck.filter(c => c.dream).map(c => Object.assign({}, c)), C.rng);
      C.drawPile = C.pileWake;
      C.pileWake = [];
    } else {
      C.drawPile = shuffle(run.deck.map(c => Object.assign({}, c)), C.rng);
    }
    C.enemies.forEach(e => { applyPhase(C, e); e.intent = nextIntent(e); });
    // Boss 入场白（第一阶段的 log）
    C.enemies.forEach(e => { if (e.phases && e.phases[0] && e.phases[0].log) log(C, e.phases[0].log); });

    // 遗物：战斗开始
    (run.relics || []).forEach(r => {
      (r.effect_code || []).forEach(ec => {
        if (ec.trigger === 'combat_start') {
          if (ec.action === 'draw') draw(C, ec.value || 1);
          if (ec.action === 'gaze') addGaze(run, ec.value || 1);
          if (ec.action === 'block') gainBlock(C, ec.value || 0);
        }
      });
    });

    beginTurn(C);
    return C;
  }

  function beginTurn(C) {
    if (C.over) return;
    const run = C.run;

    // 1. 弃掉未保留手牌
    C.hand = C.hand.filter(c => {
      // 保留：顶层 effect.retain 或 special 里的 retain（静日/埋骨布等）都算
      if (c.effect && (c.effect.retain || (c.effect.special || []).some(sp => sp.code === 'retain'))) return true;
      C.discardPile.push(c);
      return false;
    });
    // 2. 抽牌（封锁协议：双方各少抽 1 张——敌方无抽牌，表现为意图不再升级由静默协议处理）
    draw(C, DRAW_PER_TURN - (C.activeProtocol === 'lockdown' ? 1 : 0));
    // 3. 共振 += 层深度
    C.resonance += C.layer.res;
    // 苍民：梦中心跳（清醒度消耗）与预兆
    if (C.run.classId === 'cangmin') {
      if (C.world === 'dream' && C.turn % 3 === 0 && C.turn > 0) {
        C.run.clarity = Math.max(0, C.run.clarity - 1);
        log(C, '〔梦太深〕清醒度 -1（余 ' + C.run.clarity + '）。');
        if (C.run.clarity <= 0) forceWake(C, '清醒度耗尽。本场不能再入梦。');
      }
      if (!C.over) tickOmens(C);
    }
    // 4. 回合开始效果
    tickStartOfTurn(C);
    // 5. 阈值检查
    checkResonance(C);
    // 6. 能量
    C.energy = Math.max(0, run.energyMax + (run.energyBonus || 0) - (C.energyPenalty || 0));
    C.veinLocked = false;
    C._lockWarned = false;   // 锁脉每回合重来，那句提示也跟着重来
    C.playedThisTurn = false;   // 冷洞只罚每回合的第一张
    C.ruleBypass = false;       // 强行供能只保一个回合
    C.veinChain = {};
    C.lastVein = null;

    log(C, '── 第 ' + C.turn + ' 回合 ──');
  }

  function tickStartOfTurn(C) {
    const run = C.run;
    const layer = C.layer;

    // 灼烧（热脉层）
    if (layer.rule === 'heat_tick') {
      C.heat = (C.heat || 0) + 1;
      if (C.heat % 3 === 0) { damagePlayer(C, 2, '灼烧'); }
    }
    // 辐射
    if (layer.rule === 'rad_tick') {
      damagePlayer(C, 1, '辐射');
      draw(C, 1);
    }
    // 核心高热：烧手牌
    if (layer.rule === 'burn_hand' && C.hand.length) {
      const i = Math.floor(C.rng() * C.hand.length);
      const burned = C.hand.splice(i, 1)[0];
      C.exhaustPile.push(burned);
      log(C, '「' + burned.name + '」在高温里卷曲、发黑。');
    }
    // 清剿协议：每回合受 2 点
    if (C.activeProtocol === 'purge') damagePlayer(C, 2, '清剿');
    // 玩家状态
    ['poison', 'burn'].forEach(k => {
      if (C.debuffs[k]) {
        damagePlayer(C, C.debuffs[k].v, k === 'poison' ? '毒' : '灼烧');
      }
    });
    if (C.buffs.regen) healPlayer(C, C.buffs.regen);
  }

  function checkResonance(C) {
    const thresholds = [10, 20, 30];
    for (let i = 0; i < thresholds.length; i++) {
      if (C.resonance >= thresholds[i] && C.resonanceFired <= i) {
        C.resonanceFired = i + 1;
        const mode = MODE_REACTION[C.layer.mode] || MODE_REACTION.dormant;
        log(C, '〔共振 ' + thresholds[i] + '〕' + mode.text);
        mode.apply(C);
      }
    }
    if (C.resonance >= 30) {
      damagePlayer(C, C.layer.res, '过载');
    }
  }

  // ============ 抽牌 / 弃牌 ============
  function draw(C, n) {
    if (C.activeProtocol === 'silence') return; // 静默协议：玩家不能抽牌
    for (let i = 0; i < n; i++) {
      if (C.hand.length >= HAND_LIMIT) break;
      if (!C.drawPile.length) {
        if (!C.discardPile.length) break;
        C.drawPile = shuffle(C.discardPile, C.rng);
        C.discardPile = [];
        log(C, '弃牌堆洗回抽牌堆。');
      }
      C.hand.push(C.drawPile.pop());
    }
  }

  // ============ 出牌 ============
  function playCard(C, handIndex, targetIdx) {
    if (C.over) return { ok: false, msg: '战斗已结束' };
    const card = C.hand[handIndex];
    if (!card) return { ok: false, msg: '没有这张牌' };

    // 能量
    // 2026-11-03：层规则额外加价时必须说明白，否则玩家只看到「莫名其妙多扣了 1 点」
    if (C.layer.rule === 'dry' && card.veins && card.veins.indexOf('water') >= 0 && !C._dryWarned) {
      C._dryWarned = true;
      log(C, '这里的空气干得能喝 —— 水脉牌在这一层要多花 1 点能量。', 'warn');
    }
    const cost = cardCost(C, card);
    if (C.energy < cost) return { ok: false, msg: '能量不足' };

    // 凝视门槛
    if (card.effect && card.effect.gaze_cost && C.run.gaze < card.effect.gaze_cost) {
      return { ok: false, msg: '凝视不足（需要 ' + card.effect.gaze_cost + '）' };
    }
    // 共振消耗
    if (card.effect && card.effect.resonance_cost) {
      if (C.resonance < card.effect.resonance_cost) return { ok: false, msg: '共振不足' };
    }
    // 锁死卡
    if (card._locked) return { ok: false, msg: '这张牌已锁死' };
    // 苍民双世界：世界不匹配的牌不能打
    if (C.run.classId === 'cangmin' && C.world) {
      const wantDream = C.world === 'dream';
      if (!!card.dream !== wantDream) {
        return { ok: false, msg: card.dream ? '这来自梦里，醒着的手握不住' : '醒着的东西进不了这个深度' };
      }
    }
    // 黯民协议：不可重复激活
    if (card.anmin_mark && card.anmin_mark.kind === 'protocol' && C.activeProtocol === card.anmin_mark.protocol) {
      return { ok: false, msg: '协议已生效，不可撤销' };
    }

    // 扣费
    C.energy -= cost;
    C.playedThisTurn = true;
    if (card.effect && card.effect.resonance_cost) {
      C.resonance = Math.max(0, C.resonance - card.effect.resonance_cost);
    }

    // 连携
    // 2026-11-03：脉被锁死时连携加成恒为 0，第一次必须告诉玩家，否则以为连打没生效
    if (C.veinLocked && !C._lockWarned) {
      C._lockWarned = true;
      log(C, '红光断了 —— 这一回合同一脉连着打也叠不出连携加成。', 'warn');
    }
    const chainBonus = veinChainBonus(C, card);

    // 结算效果
    applyCardEffect(C, card, targetIdx, chainBonus);

    // 代价
    if (card.cost_type && card.cost_type !== 'none') {
      applyCardCost(C, card);
    }

    // 黯民协议激活
    if (card.anmin_mark && card.anmin_mark.kind === 'protocol') activateProtocol(C, card.anmin_mark.protocol);
    // 移出手牌
    C.hand.splice(handIndex, 1);
    if (card.effect && card.effect.exhaust) C.exhaustPile.push(card);
    else C.discardPile.push(card);

    C.playedCount = (C.playedCount || 0) + 1;
    checkCombatEnd(C);
    return { ok: true, chain: chainBonus };
  }

  function cardCost(C, card) {
    let c = card.energy || 0;
    // 干旱区：水脉费用 +1
    if (C.layer.rule === 'dry' && card.veins && card.veins.indexOf('water') >= 0) c += 1;
    // 2026-11-03 用户定：第二层换成「冷洞」—— 每回合第一张牌多花 1 点（手冻僵了）
    if (C.layer.rule === 'cold' && !C.playedThisTurn) {
      if (!C._coldWarned) {
        C._coldWarned = true;
        log(C, '冷洞 —— 这里每一回合打出的第一张牌都要多花 1 点能量。手冻僵了，得先搓热。', 'warn');
      }
      c += 1;
    }
    // 遗物改则：某脉费用修正（如水脉 -1）
    (C.run.relics || []).forEach(r => {
      const m = r.mod || {};
      if (m.vein_cost && card.veins && card.veins.indexOf(m.vein_cost) >= 0) {
        c = Math.max(0, c + m.vein_cost_delta);
      }
    });
    return c;
  }

  function veinChainBonus(C, card) {
    if (C.veinLocked) return 0;
    const vs = (card.veins || []).filter(v => VEINS.indexOf(v) >= 0);
    if (vs.length === 0) { C.lastVein = null; return 0; }
    const primary = vs[0];
    const prev = C.veinChain[primary] || 0;
    const n = prev + 1;
    C.veinChain[primary] = n;
    C.lastVein = primary;
    // 遗物改则：连携加成提高（可跨遗物叠加）
    let cb = 0;
    (C.run.relics || []).forEach(r => {
      const m = r.mod || {};
      if (m.chain_bonus && (!m.chain_vein || m.chain_vein === primary)) cb += m.chain_bonus;
    });
    if (n === 1) return 0;
    if (n === 2) return 1 + cb;
    return 2 + cb;
  }

  function applyCardEffect(C, card, targetIdx, chainBonus) {
    const e = card.effect || {};
    const layer = C.layer;
    let bonus = chainBonus * 2;

    // 层规则对卡牌效果的影响
    if (layer.rule === 'no_light' && !C.ruleBypass && (card.veins || []).indexOf('light') >= 0) {
      // 2026-11-03 用户定：整张牌失效必须在事件栏里给一行红字。
      // 原来那句「没有红光。这张牌什么也没做。」太轻，玩家只看到卡面「伤害 8×2」却没掉血，
      // 会当成 bug。这里要说清三件事：哪张牌、为什么、能量已经花掉了。
      log(C, '『' + (card.name || '这张牌') + '』没有生效 —— 这一层断了红光，光脉牌一点也打不出来。能量已经扣掉了。', 'warn');
      return;
    }
    if (layer.rule === 'bright' && (card.veins || []).indexOf('light') >= 0) bonus += 2;

    // 伤害
    if (e.damage) {
      const hits = e.hits || 1;
      const dmgEach = Math.max(0, e.damage + bonus + (C.buffs.strength || 0) + (C.activeProtocol === 'purge' ? 3 : 0));
      const targets = e.target === 'all'
        ? C.enemies.filter(x => !x.dead)
        : [C.enemies[targetIdx === undefined ? 0 : targetIdx]].filter(x => x && !x.dead);
      for (let h = 0; h < hits; h++) {
        targets.forEach(t => dealToEnemy(C, t, dmgEach));
      }
    }
    // 格挡
    if (e.block) {
      gainBlock(C, Math.max(0, e.block + bonus + (C.buffs.dexterity || 0)));
    }
    // 抽牌
    if (e.draw) draw(C, e.draw);
    // 共振增减
    if (e.resonance_gain) C.resonance += e.resonance_gain;
    if (e.resonance_drain) C.resonance = Math.max(0, C.resonance - e.resonance_drain);
    // 凝视
    if (e.gaze_gain) addGaze(C.run, e.gaze_gain);
    if (e.gaze_reduce) C.run.gaze = Math.max(0, C.run.gaze - e.gaze_reduce);
    // 生命
    if (e.heal) healPlayer(C, e.heal);

    // 特殊效果
    (e.special || []).forEach(sp => applySpecial(C, sp, targetIdx));
  }

  function applySpecial(C, sp, targetIdx) {
    const t = C.enemies[targetIdx === undefined ? 0 : targetIdx];
    if (typeof sp === 'string') sp = { code: sp };
    switch (sp.code) {
      case 'burn':    if (t) { t.status.burn = { v: sp.v || 3, turns: sp.turns || 3 }; } break;
      case 'poison':  if (t) { t.status.poison = { v: sp.v || 3 }; } break;
      case 'weak':    if (t) { t.status.weak = sp.turns || 2; } break;
      case 'frail':   if (t) { t.status.frail = sp.turns || 2; } break;
      case 'strength': C.buffs.strength = (C.buffs.strength || 0) + (sp.v || 1); break;
      case 'dexterity': C.buffs.dexterity = (C.buffs.dexterity || 0) + (sp.v || 1); break;
      case 'regenerate': C.buffs.regen = (C.buffs.regen || 0) + (sp.v || 2); break;
      case 'thorns':  C.buffs.thorns = (C.buffs.thorns || 0) + (sp.v || 3); break;
      case 'resonance_lock': C.resonanceLock = true; break;
      case 'gaze_reduce': C.run.gaze = Math.max(0, C.run.gaze - (sp.v || 1)); break;
      case 'delete_random': deleteRandomCard(C.run, C.rng); break;
      case 'exhaust': break; // 由 playCard 处理
      case 'rule_bypass':
        // 2026-11-03：强行供能 —— 本回合层规则压不住这张牌
        C.ruleBypass = true;
        log(C, '你强行给牌供上了能 —— 这一回合，这一层的规矩压不住它。', 'warn');
        break;
      case 'retain': break;  // 由 beginTurn 处理
      default:
        // 2026-11-03：未实现的卡牌效果必须红字说出来 —— 原来那行灰字玩家以为是自己没看懂
        log(C, '这张牌有个效果这一版还没做（' + sp.code + '），这部分没有生效。', 'warn');
        break;
    }
  }

  // ============ 代价 ============
  function applyCardCost(C, card) {
    const run = C.run;
    // 遗物改则：代价改写为凝视（锁死类仍照常）
    if (card.cost_type !== 'lock') {
      let redirect = false;
      (run.relics || []).forEach(r => { if (r.mod && r.mod.cost_redirect) redirect = true; });
      if (redirect) {
        addGaze(run, 2);
        log(C, '「' + card.name + '」的代价被批文改写了。凝视 +2。');
        return;
      }
    }
    switch (card.cost_type) {
      case 'memory':
        deleteRandomCard(run, C.rng);
        log(C, '「' + card.name + '」' + (card.cost_text || '某段记忆变薄了。'));
        break;
      case 'vitality':
        run.maxHp = Math.max(1, run.maxHp - 1);
        run.hp = Math.min(run.hp, run.maxHp);
        log(C, '「' + card.name + '」皮肤更透明了一点。最大生命 -1。');
        break;
      case 'mark':
        addGaze(run, 1);
        log(C, '「' + card.name + '」有什么东西记下了你。凝视 +1。');
        break;
      case 'lock':
        card._locked = true;
        log(C, '「' + card.name + '」本层内无法再用了。');
        break;
    }
  }

  function deleteRandomCard(run, rng) {
    if (!run.deck.length) return null;
    const i = Math.floor(rng() * run.deck.length);
    const gone = run.deck.splice(i, 1)[0];
    return gone;
  }

  // ============ 伤害 / 格挡 ============
  function dealToEnemy(C, enemy, amount) {
    if (enemy.dead) return;
    let dmg = amount;
    const absorbed = Math.min(enemy.block, dmg);
    enemy.block -= absorbed;
    dmg -= absorbed;
    enemy.hp -= dmg;
    if (dmg > 0) log(C, enemy.name + ' 受到 ' + dmg + ' 伤害。');
    if (enemy.hp <= 0) {
      enemy.hp = 0;
      enemy.dead = true;
      log(C, enemy.name + ' 停下了。');
      if (C.run.classId === 'anmin') {
        const tier = (enemy.def && enemy.def.tier) || 'normal';
        const drop = tier === 'boss' ? 10 : tier === 'elite' ? 4 : randInt(C.rng, 1, 2);
        C.parts += drop;
        log(C, '回收登记：零件 +' + drop + '（库存 ' + C.parts + '）。');
      }
    }
  }

  function gainBlock(C, n) {
    C.block += n;
  }

  function damagePlayer(C, amount, source) {
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
  }

  function healPlayer(C, n) {
    const run = C.run;
    if (run.classId === 'cangmin' && C.world === 'dream') {
      C.dreamHp = Math.min(C.dreamMaxHp, C.dreamHp + n);
      return;
    }
    run.hp = Math.min(run.maxHp, run.hp + n);
  }

  function addGaze(run, n) {
    run.gaze += n;
  }

  // ============ 回合结束 / 敌人行动 ============
  function endTurn(C) {
    if (C.over) return;

    // 供「模仿」类意图参考：上一回合玩家打出了几张牌
    C.lastTurnPlayed = C.playedCount || 0;
    C.playedCount = 0;

    // 玩家回合结束效果
    if (C.buffs.thorns) { /* 在敌人攻击时结算 */ }

    // 敌人行动
    C.enemies.forEach(e => {
      if (e.dead) return;
      enemyAct(C, e);
    });

    // 敌人状态结算
    C.enemies.forEach(e => {
      if (e.dead) return;
      if (e.status.burn) {
        dealToEnemy(C, e, e.status.burn.v);
        e.status.burn.turns--;
        if (e.status.burn.turns <= 0) delete e.status.burn;
      }
      if (e.status.poison) dealToEnemy(C, e, e.status.poison.v);
      if (e.status.weak) { e.status.weak--; if (e.status.weak <= 0) delete e.status.weak; }
      if (e.status.frail) { e.status.frail--; if (e.status.frail <= 0) delete e.status.frail; }
      if (e.buffTurns) { e.buffTurns--; if (e.buffTurns <= 0) e.buffAtk = 0; }
    });

    // 遗物改则：格挡保留（2026-10-29 与 web 对齐：不再无限累积，只留一半）
    let keepBlock = false;
    (C.run.relics || []).forEach(r => { if (r.mod && r.mod.keep_block) keepBlock = true; });
    if (keepBlock) C.block = Math.floor(C.block / 2); else C.block = 0;
    C.turn++;

    checkCombatEnd(C);
    if (!C.over) {
      C.enemies.forEach(e => { if (!e.dead) applyPhase(C, e); });
      C.enemies.forEach(e => { if (!e.dead) e.intent = nextIntent(e); });
      beginTurn(C);
    }
  }

  function nextIntent(e) {
    const pat = currentPattern(e);
    const intent = pat[e.intentIdx % pat.length];
    e.intentIdx++;
    return intent;
  }

  // 当前血量区间对应的出招表（无 phases 的敌人退回 intent_pattern）
  function currentPattern(e) {
    if (!e.phases || !e.phases.length) {
      return e.def.intent_pattern || [{ type: 'attack', value: 5 }];
    }
    const ratio = e.maxHp > 0 ? e.hp / e.maxHp : 0;
    for (let i = 0; i < e.phases.length; i++) {
      if (ratio >= (e.phases[i].hp_above || 0)) return e.phases[i].intent_pattern;
    }
    return e.phases[e.phases.length - 1].intent_pattern;
  }

  // 每回合开始前检查阶段；切换时重置出招序号并输出叙事
  function applyPhase(C, e) {
    if (!e.phases || !e.phases.length || e.dead) return;
    const ratio = e.maxHp > 0 ? e.hp / e.maxHp : 0;
    let idx = e.phases.length - 1;
    for (let i = 0; i < e.phases.length; i++) {
      if (ratio >= (e.phases[i].hp_above || 0)) { idx = i; break; }
    }
    if (idx !== e.phaseIdx) {
      const first = e.phaseIdx === -1;
      e.phaseIdx = idx;
      e.intentIdx = 0;
      if (!first && e.phases[idx].log) log(C, e.phases[idx].log);
    }
  }

  function enemyAct(C, e) {
    const it = e.intent;
    if (!it) return;
    const gazeMul = 1 + Math.floor(C.run.gaze / 10) * 0.1;

    if (it.type === 'attack') {
      let base = it.value + (e.buffAtk || 0) + (C.activeProtocol === 'purge' ? 3 : 0);
      if (it.mirror) {
        base += 3 * (C.lastTurnPlayed || 0);
        if (C.lastTurnPlayed) log(C, e.name + ' 复刻了你上一回合的节奏。');
      }
      if (it.drain_discard && C.discardPile.length) {
        const di = Math.floor(C.rng() * C.discardPile.length);
        const eaten = C.discardPile.splice(di, 1)[0];
        C.exhaustPile.push(eaten);
        log(C, e.name + ' 把「' + eaten.name + '」织进了自己身上。');
      }
      if (e.status.weak) base = Math.floor(base * 0.75);
      const times = it.times || 1;
      for (let i = 0; i < times; i++) {
        let dmg = Math.ceil(base * gazeMul);
        if (it.pierce) {
          damagePlayer(C, dmg, e.name + '的贯骨振动');
          log(C, e.name + ' 的振动从骨头里响起来，' + dmg + ' 点，格挡不住。');
        } else {
          const absorbed = Math.min(C.block, dmg);
          C.block -= absorbed;
          dmg -= absorbed;
          if (dmg > 0) {
            C.run.hp -= dmg;
            log(C, e.name + ' 击中你，' + dmg + ' 点伤害。');
          }
        }
        if (C.run.hp <= 0) {
          C.run.hp = 0; C.over = true; C.result = 'lose'; C.run.dead = true;
          log(C, '你在第 ' + C.layer.id + ' 层停下了。');
          return;
        }
        if (C.buffs.thorns) dealToEnemy(C, e, C.buffs.thorns);
      }
    } else if (it.type === 'defend') {
      e.block += it.value;
      log(C, e.name + ' 合拢了。');
    } else if (it.type === 'buff') {
      if (C.activeProtocol === 'silence') { log(C, '静默协议生效：' + e.name + ' 的增益被驳回。'); return; }
      e.buffAtk = (e.buffAtk || 0) + (it.value || 2);
      e.buffTurns = 99;
      log(C, e.name + ' 变得更快了。');
    } else if (it.type === 'debuff') {
      if (it.status === 'steal') {
        if (C.hand.length) {
          const si = Math.floor(C.rng() * C.hand.length);
          const taken = C.hand.splice(si, 1)[0];
          C.discardPile.push(taken);
          log(C, e.name + ' 把「' + taken.name + '」从你手里抽走了。');
        } else {
          log(C, e.name + ' 伸过来。你手里已经没有它要的东西。');
        }
        return;
      }
      if (it.status === 'gift') {
        draw(C, 1);
        addGaze(C.run, 1);
        log(C, e.name + ' 亮了一下。你多看了一眼，多抽了一张。凝视 +1。');
        return;
      }
      if (it.status === 'weak') C.debuffs.weak = 2;
      else if (it.status === 'poison') C.debuffs.poison = { v: it.value || 3 };
      else if (it.status === 'burn') C.debuffs.burn = { v: it.value || 3 };
      log(C, e.name + ' 朝你吐了什么。');
    }
  }

  function checkCombatEnd(C) {
    if (C.over) return;
    if (C.enemies.every(e => e.dead)) {
      C.over = true;
      C.result = 'win';
      log(C, '这一层安静下来了。');
    }
    if (C.run.hp <= 0) {
      C.over = true;
      C.result = 'lose';
      C.run.dead = true;
    }
  }

  // ============ 战斗结束奖励 ============
  function finishCombat(C) {
    const run = C.run;
    if (run.classId === 'cangmin' && C.world === 'dream') {
      run.clarity = Math.min(run.clarityMax || 5, run.clarity + 2);
      log(C, '〔梦醒〕清醒度 +2（余 ' + run.clarity + '）。你带着梦的重量睁开眼。');
    }
    if (C.result === 'win') {
      if (run.classId !== 'anmin') run.gold += randInt(run.rng, 20, 40); // 黯民以零件结算，不发金币
      return { result: 'win', gold: run.classId === 'anmin' ? 0 : 20 };
    }
    return { result: 'lose' };
  }

  // ============ 结局 ============
  // 通关结局按凝视值分三种；职业决定收尾那一句。
  const ENDINGS = {
    watched: {
      id: 'watched', title: '长审',
      text: '你停下来。红光没有等你。它把你从头到尾又数了一遍，这一次数得很慢，像在核对什么。\n数完了。它没有放开你，也没有收回你。你就站在那里，被看成了它的一部分。'
    },
    averted: {
      id: 'averted', title: '背身',
      text: '谐振器没有声音。你走过最后一层的时候一直看着自己的鞋尖。\n红光在你身后亮了很久，像有人在门口留了一盏灯。你没有回头。回头的人要留下来解释。'
    },
    walked: {
      id: 'walked', title: '同行',
      text: '谐振器没有声音。你的骨头跟着它转了很久，转到分不清是它在动，还是你在动。\n红光把你的影子接了过去，替你站着。\n你数了数自己还剩下的部分。够用。\n下面没有更深的层了。你还是往下迈了一步。'
    }
  };
  const CLASS_LAST_LINE = {
    diver: '你把手上的东西收好。合同第三页的空白处，有人替你签了收。',
    tremor: '你把最后一句震语留在台阶上。城邦不会收到它，岩层收到了。'
  };
  function pickEnding(gaze, classId) {
    let e;
    if (gaze >= 20) e = ENDINGS.watched;
    else if (gaze <= 5) e = ENDINGS.averted;
    else e = ENDINGS.walked;
    return { id: e.id, title: e.title, text: e.text, lastLine: CLASS_LAST_LINE[classId] || '' };
  }

  // ============ 黯民：回收 ============
  // 改造：花 2 零件，给一张手牌永久（本局）+2 伤害或 +3 格挡，同步改 run.deck 原卡
  function salvageUpgrade(C, handIdx, stat) {
    if (C.run.classId !== 'anmin') return { ok: false, msg: '非黯民职业' };
    const card = C.hand[handIdx];
    if (!card) return { ok: false, msg: '没有这张牌' };
    const cost = 2;
    if (C.parts < cost) return { ok: false, msg: '零件不足' };
    const amount = stat === 'damage' ? 2 : 3;
    const target = stat === 'damage' ? 'damage' : 'block';
    C.parts -= cost;
    const apply = (c) => { c.effect[target] = (c.effect[target] || 0) + amount; c._salvaged = c._salvaged || {}; c._salvaged[target] = (c._salvaged[target] || 0) + amount; };
    apply(card);
    const origin = (C.run.deck || []).find(x => x.uid === card.uid);
    if (origin) apply(origin);
    log(C, '改装登记：「' + card.name + '」' + (target === 'damage' ? '伤害 +2' : '格挡 +3') + '（零件 -' + cost + '）。');
    return { ok: true };
  }
  // 拆解：花 3 零件，威胁等级 +1（剩余敌人攻击永久 +1），战后结算 1 件随机遗物
  function dismantle(C) {
    if (C.run.classId !== 'anmin') return { ok: false, msg: '非黯民职业' };
    if (C.parts < 3) return { ok: false, msg: '零件不足（需要 3）' };
    C.parts -= 3;
    C.threatLevel += 1;
    C.enemies.forEach(e => { if (!e.dead) { e.buffAtk = (e.buffAtk || 0) + 1; } });
    C.run._relicReward = (C.run._relicReward || 0) + 1;
    log(C, '威胁等级上调报文已送达。剩余单元攻击 +1。战后将有 1 件设备转入你的库存。');
    return { ok: true };
  }

  // ============ 苍民：双世界 ============
  function rebuildWorldPiles(C, fromWorld, target) {
    // 把原世界的抽/弃堆归位，再从目标世界的堆洗出新抽牌堆
    if (fromWorld === 'wake') C.pileWake = C.pileWake.concat(C.drawPile, C.discardPile);
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
    const oldWorld = C.world;
    if (target === 'dream') {
      if (C.dreamLocked) return { ok: false, msg: '本场已强制醒来，不能再入梦' };
      if (C.run.clarity <= 0) return { ok: false, msg: '清醒度耗尽，无法入梦' };
      C.run.clarity -= 1;
      C.dreamHp = C.dreamMaxHp;
      log(C, '〔入梦〕清醒度 -1（余 ' + C.run.clarity + '）。火母的领地还认得你。');
    } else {
      C.run.hp = Math.min(C.run.maxHp, C.run.hp + 3);
      log(C, '〔醒来〕身体 +3。枕头边放着一个没做完的梦。');
    }
    // 手牌与旧堆按【原世界】归位，再重建目标世界牌堆
    const hand = C.hand.splice(0, C.hand.length);
    if (oldWorld === 'wake') C.pileWake = C.pileWake.concat(hand);
    else C.pileDream = C.pileDream.concat(hand);
    C.world = target;
    rebuildWorldPiles(C, oldWorld, target);
    C.hand = [];
    draw(C, DRAW_PER_TURN);
    return { ok: true };
  }
  function forceWake(C, reason) {
    if (C.world !== 'dream') return;
    const hand = C.hand.splice(0, C.hand.length);
    C.pileDream = C.pileDream.concat(hand);
    rebuildWorldPiles(C, 'dream', 'wake');
    C.world = 'wake';
    C.run.clarity = Math.min(C.run.clarityMax || 5, C.run.clarity + 1); // 强迫醒也回神，但只回一半
    C.dreamLocked = true; // 本场不能再入梦
    C.hand = [];
    draw(C, DRAW_PER_TURN);
    log(C, '〔强制醒来〕' + reason + ' 清醒度 +1（余 ' + C.run.clarity + '）。');
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

  function activateProtocol(C, name) {
    C.activeProtocol = name;
    const T = { lockdown: '封锁', purge: '清剿', silence: '静默' };
    log(C, '〔协议〕' + (T[name] || name) + ' 已下达。不可撤销。');
  }

  // ============ 卡牌升级 ============
  // 返回升级后的新卡对象，不修改原卡。upgrade.effect 的数值为最终值；
  // special 为追加条目（空数组表示清空原特殊效果）；cost_type 可改写代价。
  function upgradeCard(card) {
    const up = card && card.upgrade;
    if (!up || card.upgraded) return null;
    const c = Object.assign({}, card, {
      name: card.name + (up.name_suffix || '+'),
      effect: Object.assign({}, card.effect),
      cost_type: up.cost_type !== undefined ? up.cost_type : card.cost_type,
      upgraded: true
    });
    if (up.effect) {
      Object.keys(up.effect).forEach(k => {
        const v = up.effect[k];
        if (k === 'special' && Array.isArray(v)) {
          c.effect.special = v.length ? (c.effect.special || []).concat(v) : [];
        } else {
          c.effect[k] = v;
        }
      });
    }
    if (up.flavor_add) c.flavor = card.flavor + '\n' + up.flavor_add;
    return c;
  }

  // ============ 日志 ============
  // lv='warn' 的行在事件栏里单独渲染成红字（2026-11-03：层规则让整张牌失效时必须看得见）
  function log(C, msg, lv) {
    C.log.push(lv ? '\u0001' + msg : msg);
    if (C.log.length > 300) C.log.shift();
  }

  // ============ 导出 ============
  const API = {
    VEINS: VEINS,
    VEIN_CN: VEIN_CN,
    LAYERS: LAYERS,
    MODE_REACTION: MODE_REACTION,
    makeRng: makeRng,
    shuffle: shuffle,
    newRun: newRun,
    startCombat: startCombat,
    playCard: playCard,
    endTurn: endTurn,
    draw: draw,
    finishCombat: finishCombat,
    upgradeCard: upgradeCard,
    salvageUpgrade: salvageUpgrade,
    dismantle: dismantle,
    activateProtocol: activateProtocol,
    switchWorld: switchWorld,
    damagePlayer: damagePlayer,
    pickEnding: pickEnding,
    ENDINGS: ENDINGS,
    LAYER_AT: (d) => LAYERS[d - 1]
  };

  if (typeof module !== 'undefined' && module.exports) module.exports = API;
  if (root) root.RedAbyss = API;

})(typeof window !== 'undefined' ? window : this);
