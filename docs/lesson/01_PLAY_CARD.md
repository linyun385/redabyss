# 01 · 追一条完整的链：玩家打出一张攻击牌，屏幕上发生了什么

> 这篇从「手指按下卡牌」一路追到「敌人头上飘出 -6」，中间每一步都给真实行号和逐字代码。看完你能回答：点击被谁接住、能量怎么校验、伤害怎么算、血怎么扣、画面怎么重画。链路断在哪我会明说（音效就是个断点）。

## 0. 先给结论

打一张牌一共经过两层：**前端**（`index.html`，负责「玩家想干什么」）把动作交给**引擎**（`playCard`，[index.html:5694]），引擎改完数据返回结果，前端再**重画整个战斗界面**。这个游戏没有「局部更新」——每次出牌后是整屏重算（`render`，[index.html:7703]），飘出来的伤害数字是前后两次数据做差得到的。

## 1. 入口：手牌是怎么被按下的

战斗界面里每一张手牌都是 `render` 函数现场造出来的 DOM，造的时候就把「按下」事件绑上：

```js
    d.addEventListener('pointerdown', (ev) => startCardPointer(ev, d, card, i, worldMismatch));
```

（[index.html:7894]，位于手牌构建循环 [index.html:7874] 内。）注意绑的是 `pointerdown` 而不是 `click`——因为这个游戏出牌的主要方式是**拖**，`click` 只在松手时触发，抓不住「拖到哪里了」。

`startCardPointer`（[index.html:7966]）在按下瞬间记下起点坐标，之后指针移动超过 8 像素才算「开始拖」：

```js
    const dx = e2.clientX - startX, dy = e2.clientY - startY;
    if (!dragging && Math.hypot(dx, dy) > 8) {
      dragging = true;
      d.classList.add('dragging');
```

（[index.html:7982]。）一拖起来，如果这张牌需要指定目标，所有活着的敌人会被加上 `targetable` 样式（[index.html:7986]），右侧同时弹出卡牌详情（[index.html:7987]）。

**松手**是关键判定（`onUp`，[index.html:7999]）：松手时先算指针落在哪只敌人身上——不做 DOM 命中检测，而是手动算每个敌人矩形外扩后的距离：

```js
function dropEnemy(x, y) {
  const alive = [...document.querySelectorAll('#enemy-area .enemy:not(.dead)')];
  if (!alive.length) return null;
  const GIVE = alive.length === 1 ? 170 : 70;
```

（[index.html:8059]。）只有一个敌人时宽容 170 像素——「往上甩基本都算打它」；多个敌人时收紧到 70 像素取最近。为什么不用现成的 `elementFromPoint`：源码注释写在 [index.html:8023]——松手瞬间卡片还在回位动画里，命中检测会打到卡片自己。这是一个典型的「文档行为和动画时序打架，最后靠手算几何绕开」的例子。

真正交牌的分支在 `onUp` 末尾：

```js
    const ebox = dropEnemy(e2.clientX, e2.clientY);
    const onEnemy = !!ebox;
    if (needsTarget(card)) {
      if (onEnemy) { doPlay(i, +ebox.id.split('-')[1]); return; }
      pending = null;
      toast('把它拖到目标身上才算数。');
      render();
      return;
    }
    if (e2.clientY < startY - 24 || onEnemy) { doPlay(i, undefined); return; }
```

（[index.html:8025]。）读法：**需要目标**的牌（`needsTarget`，[index.html:7595]——effect 里 `target` 是 `single` 且有伤害或异常状态）必须拖到敌人上；**不需要目标**的牌（格挡/抽牌/全体伤害）往上甩超过 24 像素就行。`+ebox.id.split('-')[1]` 是把元素 id `enemy-2` 拆出敌人下标 2——DOM 的 id 在这里兼任了数据指针。

还有第二条路：单击卡牌不拖，右侧详情面板里点「打出」按钮（[index.html:8100]），需要目标时不立刻打，而是记住 `pending = i`（[index.html:8102]），等玩家点敌人——敌人的点击监听在 `render` 里（[index.html:7828]）：`if (pending !== null) doPlay(pending, e.idx);`。

## 2. 前端交牌：`doPlay` 做的四件事

不管从哪条路进来，最终都到 `doPlay`（[index.html:6966]）：

```js
function doPlay(handIdx, targetIdx) {
  const card = C.hand[handIdx];
  if (!card) return;
  const snapshot = {};
  C.enemies.forEach(e => { snapshot[e.idx] = e.hp; });
  flyCard(handIdx);
  playSfx(card.type === 'attack' ? 'card.play.attack' : card.type === 'power' ? 'card.play.power' : 'card.play.skill');
  if (card.cost_type && card.cost_type !== 'none') playSfx('card.play.cost');
  const r = RedAbyss.playCard(C, handIdx, targetIdx);
```

（[index.html:6966]。）四件事按顺序是：① 拍快照（`snapshot` 记下每个敌人打牌前的血量——后面飘字全靠它做差）；② 播飞出动画 `flyCard`（[index.html:7633]，克隆卡面 DOM 向上飞 320 毫秒后自删）；③ 播音效（这里是断点，见 §6）；④ 调引擎 `RedAbyss.playCard(C, handIdx, targetIdx)`——**前端与引擎的分界线**就是这一行：引擎只收「手牌下标 + 目标下标」两个数字，不碰任何 DOM。

引擎返回 `{ok: false, msg}` 时前端只弹提示（[index.html:6975]）；返回成功则做伤害差飘字再重画：

```js
  C.enemies.forEach(e => {
    if (snapshot[e.idx] !== undefined && snapshot[e.idx] > e.hp) {
      const node = $('#enemy-' + e.idx);
      if (node) floatText(node, '-' + (snapshot[e.idx] - e.hp));
    }
  });
  checkEasterEggs(card);
  if (r.chain > 0) toast('连携 +' + r.chain);
  pending = null;
  render();
```

（[index.html:6980]。）注意 `render()` 在最后——**数据先改完，界面一次重画**，这是整个前端的基本节奏。

## 3. 引擎校验：`playCard` 的六道门

`playCard`（[index.html:5694]）先查这张牌能不能打，六道门按序是：战斗已结束 → 没这张牌 → 能量不足 → 凝视不足 → 共振不足 → 锁死 → （疯先知）世界不匹配 → （黯民）协议重复。能量那一道调 `cardCost`（[index.html:5765]）现算：基础费用 + 干旱层水脉加 1 + 冷洞层首张加 1 + 遗物改费。六道门全过才开始花钱：

```js
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
```

（[index.html:5730]。）连携的算法在 `veinChainBonus`（[index.html:5787]）：同回合同主脉第 2 张加 1、第 3 张起加 2，脉被锁死时恒为 0。

## 4. 伤害是怎么算出来的

`applyCardEffect`（[index.html:5807]）逐条读 `effect` 字段。先过层规则：断光层（`no_light`）的光脉牌在这里整张作废（[index.html:5813]，能量照扣，日志写红字）；微光层给光脉牌加 2（[index.html:5820]）。然后是伤害段：

```js
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
```

（[index.html:5822]。）伤害公式一行说完：**每段伤害 = 牌面伤害 + 连携加成×2 + 力量 + 协议加成**，没有抗性、没有暴击、没有随机浮动——所以「改一个数值试试」的效果是完全可预期的（这正是 05 篇练习的落点）。段数 `hits` 是外层循环，力量加成对每一段都生效，这就是多段牌吃力量更狠的原因。

扣血在 `dealToEnemy`（[index.html:5923]）：

```js
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
```

（[index.html:5923]。）顺序是「先格挡后血量」，格挡吸收的部分直接丢掉（不打折扣也不溢出返还）。血到 0 后敌人标记 `dead`，引擎随即在 `playCard` 末尾调 `checkCombatEnd`（[index.html:6163]）看是不是全灭。

## 5. 玩家看到的那一下：两段飘字与整屏重画

出牌后的视觉反馈其实有**两段**。第一段在 `doPlay` 里（[index.html:6980]，§2 已引）：用出牌前的快照算差值，立刻往敌人身上塞一个 `-N` 飘字。第二段在随后的 `render` 里（[index.html:7835]）：`render` 自己也保留着上一帧的血量表 `prev.hps`，发现差值就往动画队列塞一个「受击白闪 + 飘字」：

```js
    if (!e.dead && prev.hps[e.idx] !== undefined && prev.hps[e.idx] > e.hp) {
      const dmg = prev.hps[e.idx] - e.hp;
      enqueueAnim((done) => {
        const box2 = document.getElementById('enemy-' + e.idx);
        if (!box2) { done(); return; }
        box2.classList.add('hitflash');
        playSfx('enemy.hit');
        setTimeout(() => box2.classList.remove('hitflash'), 130);
        const f = el('div', 'float', '-' + dmg);
        const off = floatOffsetFor('e' + e.idx);
        if (off) f.style.top = 'calc(30% + ' + off + 'px)';
        box2.appendChild(f);
        setTimeout(() => { f.remove(); done(); }, 430);
      });
    }
```

（[index.html:7835]。）动画队列（`enqueueAnim`，[index.html:7670]）的意义写在它的注释里——「动画依次播，输入不等动画」：多段伤害的飘字靠 `floatOffsetFor`（[index.html:7682]）错开高度，不至于叠成一团。

整屏重画 `render`（[index.html:7703]）从头到尾扫一遍：HUD 血量/格挡/能量/共振/金币（[index.html:7705]-[index.html:7730]）、遗物栏（[index.html:7768]）、敌人区逐个重建（[index.html:7787]）、手牌逐张重建（[index.html:7872]）、牌堆计数（[index.html:7916]）、日志倒序渲染（[index.html:7926]）。它大量使用「与上一帧比较」的技巧（`prev` 对象，[index.html:6888] 附近初始化）：血变少了给 body 加抖动 class、格挡变多给图标加脉冲、意图变了给意图行加闪光。**界面状态的「变化感」全部来自前后差分，而不是谁主动通知谁**——没有事件总线，没有观察者，就是每次全量比对。

## 6. 链路里的断点：音效

链路上每个动作都在调 `playSfx`（出牌 [index.html:6972]、受击 [index.html:7841]、死亡 [index.html:7832]），但它是空钩子：

```js
function playSfx(code, opts) {
  if (window.__SFX_LOG) window.__SFX_LOG.push(code);
  if (window.__SFX_MUTED) return;
  try { if (typeof window.RedAbyssSFX === 'function') window.RedAbyssSFX(code, opts); } catch (e) {}
}
```

（[index.html:7623]。）它只往调试日志推 code，真正发声要等 `window.RedAbyssSFX` 被谁赋值——全代码没有赋值的地方。所以「这里应该播放音效，但现在是空的」：调用点全接好了，发声器没做（注释 [index.html:7619] 写明「只留钩子，不生成音频」）。05 篇的练习三就是在这里加 `console.log` 验证调用链。

## 7. 流程图（每步带行号）

    手指按下卡牌
      └→ render 造手牌时绑的 pointerdown        [index.html:7894]
          └→ startCardPointer（记起点/8px 判拖）  [index.html:7966] [index.html:7983]
              └→ onUp 松手判定                    [index.html:7999]
                  ├→ dropEnemy 算命中             [index.html:8059] [index.html:8025]
                  └→ doPlay(i, 敌人下标)           [index.html:8028]（或 8034 / 经详情面板 8100）
    （单击路径：openCardDetail → 「打出」按钮 → pending 或 doPlay   [index.html:8100]-[index.html:8102]，敌人点击 [index.html:7830]）
    doPlay：
      ├→ 拍血量快照                              [index.html:6969]
      ├→ flyCard 飞出残影                        [index.html:6971] → [index.html:7633]
      ├→ playSfx（空钩子）                       [index.html:6972] → [index.html:7623]
      └→ RedAbyss.playCard(C, handIdx, targetIdx) [index.html:6974]
          └→ 引擎 playCard                       [index.html:5694]
              ├→ 六道校验门（含 cardCost）        [index.html:5695]-[index.html:5728]，费用 [index.html:5765]
              ├→ 扣能量/共振 + 连携加成           [index.html:5730]-[index.html:5743]
              ├→ applyCardEffect                  [index.html:5807]
              │   ├→ no_light 拦截 / bright 加成   [index.html:5813] [index.html:5820]
              │   ├→ 伤害 = damage+连携×2+力量+协议 [index.html:5823]-[index.html:5831]
              │   └→ dealToEnemy（格挡先吸）       [index.html:5923]-[index.html:5934]
              ├→ applyCardCost（代价）             [index.html:5882]
              └→ 移入弃牌堆/消耗堆 + 胜负检查      [index.html:5756]-[index.html:5761]
    返回前端：
      ├→ 快照差值 → floatText『-N』              [index.html:6980]-[index.html:6985]
      └→ render() 整屏重画                       [index.html:6989] → [index.html:7703]
          └→ prev.hps 差值 → 动画队列白闪+飘字    [index.html:7835]-[index.html:7848]
              └→ requestAnimationFrame 逐个播      [index.html:7671]
    玩家看到：卡飞出去、敌人白闪、-N 飘起、血条变短、日志多一行

## 自测题

1. 多段牌（hits=3）配 2 点力量，每段多打几点伤害？（提示看 [index.html:5825] 的 `dmgEach` 用在哪个循环里）
2. 只有一个敌人时，鼠标离它多远以内松手仍算命中？这个宽容度在哪一行定义？
3. 断光层（no_light）打出光脉牌，能量扣不扣？在哪一行决定「整张作废」？
4. 敌人身上有 4 点格挡，你打 9 点，它最终掉多少血、格挡剩多少？看 [index.html:5926] 的两行减法。
5. `playSfx('card.play.attack')` 会让玩家听到声音吗？为什么？

**答案**：1）力量加在 `dmgEach` 上、`dmgEach` 在 hits 循环内每段都生效，所以每段 +2、总共 +6。2）170 像素，定义在 [index.html:8062] 的 `GIVE`。3）扣——拦截发生在效果结算段 [index.html:5813]，而扣费早在 [index.html:5731] 已完成，红字日志专门提醒「能量已经扣掉了」。4）格挡吸 4 归 0，剩余 5 全部扣血；`absorbed = Math.min(4, 9)`，`dmg = 9 - 4`。5）不会——`playSfx`（[index.html:7623]）只把 code 推进调试日志，发声器 `window.RedAbyssSFX` 没有任何地方赋值。

## 决定记录

- 引擎代码在 `index.html`（[index.html:5694] 起）与 `engine/core.js`（[engine/core.js:332] 起）各有一份逐字相同的副本；本篇统一引用 `index.html` 的行号并从 `index.html` 摘录，避免读者在两个行号体系间跳。
- 「伤害公式无抗性无浮动」的结论来自对 `dmgEach` 一行（[index.html:5825]）与 `dealToEnemy`（[index.html:5923]）的全量阅读——两处都没有随机项；`randInt` 在战斗内只用于血量初始化（[index.html:5416]）与黯民零件掉落（[index.html:5937]），不参与伤害。
- 音效断点的表述依据 [index.html:7619]-[index.html:7627] 的注释与函数体，未做任何「大概以后会实现」的推测。

## 八、`playCard` 逐行拆（引擎侧，[index.html:5694] 到 [index.html:5763]）

主链路的核心函数一共 70 行。这一节按行号顺序把每一段在干什么讲完——左边是行号（区间内连续），右边是那一行的原文要点与解释。读的时候建议开着源文件对齐看。

| 行 | 原文要点 | 在干什么 |
|---|---|---|
| [index.html:5694] | `function playCard(C, handIndex, targetIdx)` | 函数签名：收战斗容器、手牌下标、目标下标三个参数——引擎对「玩家」的全部认知就这三个数 |
| [index.html:5695] | `if (C.over) return { ok: false, msg: '战斗已结束' }` | 门 0：战斗已结束。返回值约定为 `{ok, msg 或 chain}`，前端全靠它分流 |
| [index.html:5696] | `const card = C.hand[handIndex]` | 把下标换成卡对象——从这一行起引擎只认对象不认下标 |
| [index.html:5697] | `if (!card) return ... '没有这张牌'` | 门 1：下标越界防御。前端传错也不会崩 |
| [index.html:5701] | `if (C.layer.rule === 'dry' && ...water... && !C._dryWarned)` | 干旱层首次打水脉牌时，先补一句红字警告（`_dryWarned` 保证只说一次） |
| [index.html:5705] | `const cost = cardCost(C, card)` | 算当前实际费用（基础 + 层规则 + 遗物改费） |
| [index.html:5706] | `if (C.energy < cost) return ... '能量不足'` | 门 2：能量。**此时一分钱还没扣**——拒绝是免费的 |
| [index.html:5709]-[index.html:5711] | `gaze_cost` 门槛检查 | 门 3：凝视够不够。注意是「够不够」不是「扣多少」——gaze_cost 是门槛不是消耗 |
| [index.html:5713]-[index.html:5714] | `resonance_cost` 检查 | 门 4：共振余量够不够 |
| [index.html:5717] | `if (card._locked)` | 门 5：lock 代价卡本层已用过 |
| [index.html:5719]-[index.html:5724] | 世界匹配检查 | 门 6：疯先知只能在对应世界打对应侧的牌；错误文案本身就是叙事（「醒着的手握不住」） |
| [index.html:5726]-[index.html:5728] | 协议重复检查 | 门 7：同一协议不可叠。全项目 `anmin_mark` 只在这里被读（T330 诊断的「幽灵流派」根源） |
| [index.html:5731]-[index.html:5732] | `C.energy -= cost`、`C.playedThisTurn = true` | **开始花钱**。`playedThisTurn` 是冷洞层「首张 +1」的判断依据（[index.html:5769] 附近消费） |
| [index.html:5733]-[index.html:5735] | 扣共振 | resonance_cost 在这里真正扣除，下限 0（`Math.max(0, ...)` 防负数） |
| [index.html:5739]-[index.html:5742] | 锁脉首次警告 | 又一个「只说一次」的模式：`_lockWarned` 与 `_dryWarned` 同构 |
| [index.html:5743] | `const chainBonus = veinChainBonus(C, card)` | 连携加成（第 2 张 +1、第 3 张起 +2；脉锁死恒 0）。注意此刻**还没生效**，只是算出来 |
| [index.html:5746] | `applyCardEffect(C, card, targetIdx, chainBonus)` | 效果结算（下一节逐行拆）。引擎里唯一「把字段变成事实」的地方 |
| [index.html:5749]-[index.html:5751] | `applyCardCost(C, card)` | 代价结算：memory 删牌 / vitality 扣上限 / mark 加凝视 / lock 打锁 |
| [index.html:5754] | 协议激活 | `anmin_mark.kind === 'protocol'` 的卡在这里把协议写进 `C.activeProtocol` |
| [index.html:5756] | `C.hand.splice(handIndex, 1)` | 卡离开手牌。**先扣费后移牌**——中间任何 return 都不会出现「钱扣了牌还在」或反之 |
| [index.html:5757]-[index.html:5758] | 进消耗堆或弃牌堆 | `effect.exhaust` 为真进 `exhaustPile`，否则进弃牌堆 |
| [index.html:5760] | `C.playedCount += 1` | 本回合出牌计数——mirror 意图（「复刻你的节奏」）在 `endTurn` 读它 |
| [index.html:5761] | `checkCombatEnd(C)` | 全灭判定。可能当场把 `C.over` 置真 |
| [index.html:5762] | `return { ok: true, chain: chainBonus }` | 把连携值交还前端——`doPlay` 里那句 `toast('连携 +' + r.chain)` 吃的就是它（[index.html:6987]） |

读完这张表的收获：**校验全部前置、结算按「钱 → 效果 → 代价 → 归宿」固定顺序**。任何新加的拦截规则都该插在 [index.html:5706] 之前（免费拒绝区），任何新的结算都该插在 [index.html:5746] 前后——插错位置就会出现「扣了钱不生效」或「生效了没花钱」。

## 九、`applyCardEffect` 逐行拆（[index.html:5807] 到 [index.html:5850]）

| 行 | 原文要点 | 在干什么 |
|---|---|---|
| [index.html:5808] | `const e = card.effect \|\| {}` | 取效果对象；`\|\| {}` 让没有 effect 的卡不至于崩 |
| [index.html:5810] | `let bonus = chainBonus * 2` | 连携加成翻倍进伤害/格挡——「+1 连携」实际是 +2 数值 |
| [index.html:5813] | `no_light` 拦截 | 断光层光脉牌整张作废，红字日志后 **直接 return**——后面所有字段都不结算 |
| [index.html:5818] | `return` | 拦截的出口。能量已在 `playCard` 扣过，所以日志要专门说明 |
| [index.html:5820] | `bright` 层光脉 +2 | 微光层加成叠加进 `bonus` |
| [index.html:5823] | `if (e.damage)` | 伤害段入口。注意是**真值判断**——`damage: 0` 的卡进不了这段 |
| [index.html:5824] | `const hits = e.hits \|\| 1` | 段数缺省 1 |
| [index.html:5825] | `dmgEach = e.damage + bonus + strength + purge` | 伤害公式全貌：无抗性、无浮动、无随机 |
| [index.html:5826]-[index.html:5828] | 目标选择 | `all` 过滤活敌；单体取 `targetIdx` 指定的那只，未指定按 0 号 |
| [index.html:5829]-[index.html:5831] | 段数 × 目标双层循环 | 每段对每个目标各调一次 `dealToEnemy`——力量对每段生效的根源 |
| [index.html:5834]-[index.html:5835] | 格挡段 | `e.block + bonus + dexterity`，负数被 `Math.max(0, ...)` 钳住 |
| [index.html:5838] | `if (e.draw) draw(C, e.draw)` | 抽牌段 |
| [index.html:5840]-[index.html:5841] | 共振增减 | `resonance_gain` 与 `resonance_drain` 一加一减 |
| [index.html:5843]-[index.html:5844] | 凝视 | `gaze_gain` 加、`gaze_reduce` 减（下限 0） |
| [index.html:5846] | `if (e.heal) healPlayer(...)` | 回复段（疯先知在梦中回的是梦血条，见 [index.html:5997] 函数内分支） |
| [index.html:5849] | `(e.special \|\| []).forEach(...)` | 特殊效果逐条进 `applySpecial`（[index.html:5852]）按 `code` 分发 |

读完的收获：effect 是一张**平铺的字段清单**，结算顺序固定为「拦截 → 伤害 → 格挡 → 抽牌 → 共振 → 凝视 → 回复 → special」。字段之间的先后是写死的——想让「先灼烧再伤害」这种顺序存在，得动这段代码本身。

## 十、`doPlay` 逐行拆（前端侧，[index.html:6966] 到 [index.html:6990]）

| 行 | 原文要点 | 在干什么 |
|---|---|---|
| [index.html:6967] | `if (!card) return` | 前端第一道防御 |
| [index.html:6969]-[index.html:6970] | `snapshot` 记下每只敌人当前血 | 飘字的依据——引擎不汇报「扣了几点」，前端自己算差 |
| [index.html:6971] | `flyCard(handIdx)` | 克隆卡面 DOM 往上飞（纯视觉，[index.html:7633]） |
| [index.html:6972]-[index.html:6973] | 两声 `playSfx` | 按卡类型与是否有代价选音效——空钩子（第 6 节） |
| [index.html:6974] | `const r = RedAbyss.playCard(...)` | 交棒给引擎。**前后端唯一的接缝** |
| [index.html:6975] | `if (!r.ok) { toast(r.msg); ... return; }` | 失败：弹引擎给的理由，什么都不再发生 |
| [index.html:6976]-[index.html:6979] | 代价提示 | 有代价的卡补一声音效；前三场战斗弹一次性教学（`onceHint` [index.html:7609]） |
| [index.html:6980]-[index.html:6985] | 伤害差飘字 | `snapshot` 与现在的血做差，`floatText` 打到敌人框上 |
| [index.html:6986] | `checkEasterEggs(card)` | 组合彩蛋判定（配对表 [index.html:6994]） |
| [index.html:6987] | `if (r.chain > 0) toast('连携 +' + r.chain)` | 连携提示——引擎返回值第 3 节讲过 |
| [index.html:6988]-[index.html:6989] | `pending = null; render()` | 清选择态、整屏重画 |
| [index.html:6990] | `if (C.over) setTimeout(finishCombatFlow, 450)` | 战斗结束则 450 毫秒后进结算——留一拍让最后的飘字播完 |

前后端分工在这 24 行里看得最清楚：**前端负责「让玩家相信发生了」，引擎负责「让数据确实发生」**。飘字用差值而不是引擎返回值，就是这两套职责没有打通接口的结果——引擎不汇报「打了几点」，前端只好自己比对中国before/after。这是本项目最值得记住的一种取舍。

## 十一、你改这里会发生什么（三个真实修改点）

**修改点一：把 [index.html:5711] 凝视门槛改成「满足时扣除」。**
现在 gaze_cost 是门槛（查完不扣，[index.html:5709]-[index.html:5711]）。如果你在门后加一行 `C.run.gaze -= card.effect.gaze_cost;`，凝视从「永久负债门槛」变成「消耗型资源」——trem_0014 这类高门槛卡（gaze_cost 3）会从「一次解锁、反复用」变成「每打一次付一次」，凝视流强度大幅下沉，且 20 凝视结局（[index.html:6211] 的 `pickEnding`）更难触达。验证：给凝视 5 的号打两张 trem_0010（门槛 2），改前凝视不变、改后归 1。

**修改点二：把 [index.html:5829] 的段数循环改为「只有第一段吃力量」。**
把 `dmgEach` 的计算挪进循环、力量项乘 `h === 0 ? 1 : 0`。会发生的连锁：多段牌（dive_0069 三管、trem_0060 全体段）的强度大幅回落，「力量 × 多段」这个全游戏最肥的乘法组合消失，力量成长流（T332 矩阵的强/中格）集体降档。验证：2 力量下打三管，改前总伤 +6，改后 +2。这个点的教学价值：**一行公式的位置决定一个流派的价格**。

**修改点三：把 [index.html:5757]-[index.html:5758] 的进堆判断反过来（消耗堆与弃牌堆互换）。**
所有非消耗牌进 `exhaustPile`、消耗牌进弃牌堆。表面是玩笑，实际立刻连环爆：弃牌堆永不积累 → [index.html:5685] 的「弃牌堆洗回抽牌堆」永远不触发 → 牌库在几回合内抽干，每局都以「无牌可抽」告终；而「已消耗」计数（[index.html:7918]）暴涨。验证不用真打：改完刷新，任何一场战斗两回合内手牌抽空即为生效。这个修改点演示的是「一行看似对称的交换，摧毁的是一个资源循环」。

## 十二、附：两颗「扣血函数」对照

链路里其实有两个扣血函数，方向相反、结构对称，放在一起看才记得住：

| | `dealToEnemy`（[index.html:5923]，打敌人） | `damagePlayer`（[index.html:5948]，敌人打你） |
|---|---|---|
| 入口判断 | 敌人已死直接 return（[index.html:5924]） | 战斗已结束直接 return（引擎侧 [engine/core.js:587]） |
| 格挡吸收 | `Math.min(enemy.block, dmg)`，先扣格挡（[index.html:5926]-[index.html:5928]） | 同样的三行，扣的是玩家格挡（[engine/core.js:590]-[engine/core.js:592]） |
| 特殊分支 | 无——敌人只有格挡一种盾 | **梦境分支**：疯先知在梦中受伤扣的是 `dreamHp`，梦破时溢出的伤害按一半反噬真身（[engine/core.js:594]-[engine/core.js:620]） |
| 死亡处理 | `enemy.dead = true` + 黯民零件掉落（[index.html:5931]-[index.html:5940]） | `run.dead = true` + 全局结束（[engine/core.js:626]-[engine/core.js:633]） |
| 日志 | 「受到 X 伤害」 | 「击中你，X 点伤害」或「（来源）」 |

对称性里藏着一个不对称：敌人侧被 `pierce` 意图绕过（[index.html:6111] 的贯骨振动直接调 `damagePlayer`，不吃格挡），玩家侧没有「无视格挡的还击」——攻防两侧的规则从不镜像，读代码时不能想当然地互相套用。另有一处反向的不对称值得记住：玩家扣血的入口 `damagePlayer` 在「战斗已结束」时会直接拒收（引擎侧 [engine/core.js:587]），而敌人侧没有这层保护，只有「已死」判断——所以同屏多段伤害在胜负判定后仍可能对尸体结算，只是结果不可见。这类「看起来对称、细则各写各的」的地方，是改规则时最容易踩空的缝。

## 十三、同一条链的第二种走法：点选路径（补一张图）

第 7 节的流程图画的是拖拽主线。点选路径（不用拖）分岔在卡牌详情面板里，单独补一张：

    手指单击卡牌（未拖过 8px）
      └→ onUp 判定 !dragging → openCardDetail        [index.html:8010] → [index.html:8073]
          └→ 右侧面板出现，「打出」按钮在构造时绑定    [index.html:8100]
              ├→ needsTarget 为假 → 立即 doPlay(i, undefined)   [index.html:8103]
              └→ needsTarget 为真 → pending = i，toast 提示选目标  [index.html:8102]
                  └→ render 给所有活敌加 targetable 样式      [index.html:7790]
                      └→ 玩家点敌人框                          [index.html:7828]-[index.html:7831]
                          └→ doPlay(pending, e.idx)            [index.html:7830]
    取消路径：面板的 × / 收回按钮清 pending        [index.html:8095]

两条路径的汇合点是 `doPlay`，分流点在 `needsTarget`（[index.html:7595]）。值得注意的是 `pending` 只有一个槽位（[index.html:6437] 声明），所以「选中一张待定目标牌后直接去拖另一张牌」的行为没有被显式拦截——拖拽路径的 `doPlay` 会带着新的 handIdx 执行，而 pending 残留值在 [index.html:6988] 被统一清掉。这类「两条 UI 路径共享一个状态位」的设计在功能上成立，但每加一种新的出牌交互（比如右键快出），都要记得先审一遍 `pending` 的生命周期。
