# A · 音效接线施工单

> 基于 09_sfx_touchpoints.md（更正版）的用户运行时实测：**13 个 code 被调，6 个孤儿，27 wav 全在**。
> 顺序按玩家最常经历排：每次出牌 > 每次战斗 > 每次事件 > 每次营火 > 每次拾取 > boss > 彩蛋。
> 全部为**建议**——落地由设计机执行。

---

### 1 · card.play.attack / skill / power — 三目表达式（每次出牌）

**现在**：`doPlay()`（:6977）里 `:6983` 调 `playSfx`，用三目按 `card.type` 选 code。**源码有**、但用户运行时报告未触发这三个 code。

**加什么**：先确认三目表达式是否真的在执行。用 `__SFX_LOG` 对账——如果 log 里也没有这三个 code，说明 `doPlay` 在 `:6983` 之前就 return 了（如 playBlockReason 拦截）。

**加什么（确认后）**：如果确认是 playBlockReason 提前 return 导致跳过，在 return 前也播音效：
```js
// :6977 doPlay 函数开头
function doPlay(handIdx, targetIdx) {
    const card = C.hand[handIdx];
    const reason = playBlockReason(card);
    if (reason) {
        playSfx('state.energy_empty');  // ← 加这行：打不出也给反馈
        toast(reason);
        ...
        return;
    }
    // 原有 playSfx 三目在 :6983
```

**时机**：在 `playBlockReason` 判断之后、return 之前——先播「打不出」的音，再弹 toast。

**风险**：连打多张能量不足的牌会连续触发。缓解：`playSfx` 内部如有去重逻辑可防；如无，加 `if (reason !== prevReason)` 守卫。

**怎么验**：`__SFX_LOG` 里出现 `state.energy_empty`；打能量不足的牌有声音。

---

### 2 · state.energy_empty — 孤儿音（能量不足）

**现在**：wav 存在（`state.energy_empty.wav`）、SFX_LIST 定义了、但全文件 grep 无 `playSfx('state.energy_empty')` 调用。shakeit 动画有（`:8048`），声音没有。

**加什么**：`:8048` 附近（shakeit 触发处）：
```js
// before
d.classList.remove('shakeit'); void d.offsetWidth; d.classList.add('shakeit');
// after
d.classList.remove('shakeit'); void d.offsetWidth; d.classList.add('shakeit');
playSfx('state.energy_empty');
```

**时机**：shakeit 动画触发时同步播音——视觉+听觉同时反馈「打不出」。

**风险**：连续拖多张能量不足的牌会连续触发。playSfx 内部如有频率限制可防；如无，加 100ms 节流。

**怎么验**：`__SFX_LOG` 出现 `state.energy_empty`；不进游戏可 grep 确认调用行存在。

---

### 3 · 事件选项被选中 — 无音效

**现在**：`chooseEventOption()`（`:7415`）处理事件选项点击。无 playSfx 调用。

**加什么**：在函数开头（`showScreen` 之前）：
```js
// before
function chooseEventOption(ev, i) {
    phase = 'reward';
    showScreen('#screen-flow');
// after
function chooseEventOption(ev, i) {
    playSfx('ui.click');
    phase = 'reward';
    showScreen('#screen-flow');
```

**时机**：在状态改变之前——玩家点击的瞬间就有反馈。

**风险**：低频事件（每局 ~6 次），不会叠成噪音。

**怎么验**：`__SFX_LOG` 出现 `ui.click`。

---

### 4 · 商店购买成功 — 无音效

**现在**：`showShop()`（`:6833`）的 click handler（`:6847`）在购买成功后没有 playSfx。

**加什么**：在 `run.gold -= item.price` 之后：
```js
// before
      run.gold -= item.price;
      item.sold = true;
// after
      run.gold -= item.price;
      item.sold = true;
      playSfx('ui.click');
```

**时机**：在金币扣除后——先确认交易成功，再响。

**风险**：低频（每局 ~2.5 次）。

**怎么验**：`__SFX_LOG` 出现 `ui.click`（商店购买时）。

---

### 5 · 营火升级确认 — 无音效

**现在**：`showCampfire()`（`:6682`）里升级选项的 click handler（`:6770` 附近）调 `upgradeCard` 后无 playSfx。

**加什么**：在 `onDone(card, run.deck[i])` 回调之前：
```js
// before
      run.deck[i] = RedAbyss.upgradeCard(card);
      onDone(card, run.deck[i]);
// after
      run.deck[i] = RedAbyss.upgradeCard(card);
      playSfx('ui.page');
      onDone(card, run.deck[i]);
```

**时机**：升级成功后、回调之前——「翻页」的音效暗示卡牌被重写了。

**风险**：低频（每局 ~2-3 次营火）。

**怎么验**：`__SFX_LOG` 出现 `ui.page`（营火升级时）。

---

### 6 · 遗物被拾取 — 无音效

**现在**：`grantRelic(r)`（`:7225`）把遗物加入 `run.relics` 但无 playSfx。

**加什么**：在 `run.relics.push(r)` 之后：
```js
// before
function grantRelic(r) {
    run.relics.push(r);
// after
function grantRelic(r) {
    run.relics.push(r);
    playSfx('ui.page');
```

**时机**：遗物入列后——「翻页」暗示新条目入册。

**风险**：低频（每局 ~4.5 次）。

**怎么验**：`__SFX_LOG` 出现 `ui.page`（拾取遗物时）。

---

### 7 · 层规则禁牌 — 无音效

**现在**：`doPlay()` 里层规则分支（no_light/cold/dry 判断，:7020 附近）log 红字但无 playSfx。

**加什么**：在 log 之后：
```js
// before
      log(C, '『' + card.name + '』没有生效 —— 这一层断了红光...', 'warn');
      return;
// after
      log(C, '『' + card.name + '』没有生效 —— 这一层断了红光...', 'warn');
      playSfx('state.energy_empty');   // 复用「打不出」的空握声
      return;
```

**时机**：在 log 之后、return 之前——先看到红字再听到「打不出」。

**风险**：低频（层规则只在特定层生效）。复用 energy_empty 的音效（同为「打不出」语义）。

**怎么验**：L1 打光脉牌 → `__SFX_LOG` 出现 `state.energy_empty`。

---

### 8 · special.boss_phase — 运行时未触发

**现在**：`:7965` 有 `playSfx('special.boss_phase')` 调用，但用户运行时报告未触发。触发条件是 boss 阶段切换（hp 阈值），可能用户的测试局未打 boss 或未打到阶段切换。

**加什么**：**不需要加代码**——调用点已存在。需要验证触发条件是否覆盖所有 boss。当前只在 `render()` 里检测 `e.hp <= 阈值 && 之前 > 阈值`。如果 boss 的 phases 数组格式异常，可能不触发。

**时机**：维持现状（render 检测时触发）。

**风险**：如果 boss phases 数据有 typo，不会触发。建议：用 `__SFX_LOG` 在 L4 boss 战确认。

**怎么验**：L4 打光蛭母到 66% 血以下 → `__SFX_LOG` 出现 `special.boss_phase`。

---

### 9 · special.world_switch — 仅苍民触发

**现在**：`:6928` `playSfx('special.world_switch')` 在 `#btn-world` click handler 内。`#btn-world` 只有苍民可见（`:894` class="hidden"）。其他三角色永远不触发。

**加什么**：**不需要加代码**——设计如此（world_switch 是苍民专属机制）。但如果要给其他角色一个通用版本，可以在层切换时播 `ui.page`。

**时机**：维持现状。

**风险**：无——设计决定。

**怎么验**：苍民角色按 W 切世界 → `__SFX_LOG` 出现 `special.world_switch`。

---

### 10 · card.play.attack / skill / power — 三目表达式排查

**现在**：`:6983` 三目表达式在 `doPlay()` 内。源码有这三个字符串，但用户运行时报告未触发。可能原因：
1. `doPlay` 在 `:6983` 之前已 return（playBlockReason 拦截）→ 参见条目 1 的修法
2. `playSfx` 函数内部有条件过滤
3. `RedAbyssSFX` override 接管后丢弃了这些 code

**加什么**：先排查根因——在 `:6983` 前后加 console.log：
```js
console.log('[SFX-DEBUG] card.type =', card.type, '| about to playSfx');
playSfx(card.type === 'attack' ? 'card.play.attack' : ...);
```
然后 `__SFX_LOG` 对账。如果 console.log 打了但 __SFX_LOG 没收到 → playSfx 内部或 RedAbyssSFX override 有过滤。

**时机**：排查用，不是最终方案。

**风险**：console.log 是临时调试代码，排查后删除。

**怎么验**：`__SFX_LOG` 出现 `card.play.attack`（打攻击牌时）。如果始终不出现，根因在 playSfx 内部或 override 层。

---

## 顺序总结（按玩家最常经历）

| 序 | 事件 | 频率 | code | 类型 |
|---|---|---|---|---|
| 1 | 每次出牌 | 每局 ~100 次 | card.play.attack/skill/power | 排查三目 |
| 2 | 能量不足 | 每局 ~10 次 | state.energy_empty | 加 1 行 |
| 3 | 事件选项 | 每局 ~6 次 | ui.click | 加 1 行 |
| 4 | 层规则禁牌 | 每局 ~2 次 | state.energy_empty（复用） | 加 1 行 |
| 5 | 商店购买 | 每局 ~2.5 次 | ui.click | 加 1 行 |
| 6 | 营火升级 | 每局 ~2.5 次 | ui.page | 加 1 行 |
| 7 | 遗物拾取 | 每局 ~4.5 次 | ui.page | 加 1 行 |
| 8 | boss 阶段 | 每局 ~5 次 | special.boss_phase | 排查触发条件 |
| 9 | 切世界 | 苍民专属 | special.world_switch | 维持 |
