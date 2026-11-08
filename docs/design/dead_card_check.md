# T447 · 空转卡检查（效果可能是空的卡）

> 检查口径（三选一命中即列）：
> 1. `effect` 为空或只有 `{"target":"self"}`
> 2. effect 引用了**引擎未实现的键 / special 码**
> 3. 效果键被引擎实现，但**结算路径从不读取**（死状态）
> 引擎事实基准 = `web/index.html` 内联副本（实跑版，2026-11-04 已修 value 归一化）。
> 复算：`python data/audit/gen_t447.py`（或按文末片段）。

## 空转清单（4 张）

### 1. `u_0016` 越权的批文 —— effect 字段空，但**不是死卡**（更正）

- 全量数据：effect `{"target":"self"}` 为空，**但卡带 `anmin_mark: {kind:"protocol", protocol:"purge"}`**——引擎 `web/index.html:5754` 读它 `activateProtocol`，打出即激活清剿协议（每回合自伤 2、剩余敌人攻击 +3，`core.js:289`/`:462` 双向实现）。
- **更正前文**：本卡在 T500/T516/T520 初版被判「完全空转/未确认」——错在只看了 effect 字段。实际功能生效，问题反转成**呈现问题**：effect 空 → cardDesc 无效果文本 → 玩家不知道这是协议开关牌。
- 保留的问题：rare 稀有度 + 无效果描述 + purge 的自伤代价没有任何卡面提示——三件事叠在一起，玩家第一次打出大概率以为卡坏了。

### 2. `u_0009` 倒转圣痕 —— 半空转（共振部分失效）

- effect：`special: [{code: gaze_reduce, value: 2}, {code: resonance_gain, value: 3}]`
- 为什么判定为空转：**special 码 `resonance_gain` 在引擎里没有 case**——`web/index.html` applySpecial 的 switch 只实现了 burn/poison/weak/frail/strength/dexterity/regenerate/thorns/resonance_lock/gaze_reduce/delete_random/exhaust/retain/rule_bypass；`resonance_gain` 落进 default 分支，打牌时红字「这张牌有个效果这一版还没做（resonance_gain）」，共振 +3 不生效。
- 洗凝视 −2 那半边是好的（case 'gaze_reduce' 有实现）。
- 修法参照：效果键 `resonance_gain` 本身有实现（`if (e.resonance_gain) C.resonance += ...`）——把 special 码改成效果键即可，或给 switch 补 case。

### 3. `dive_0022` 硬矿钻（重型）—— 脆弱挂件空转

- effect：`{"damage": 13, "special": [{"code": "frail", "value": 1, "turns": 1}], "target": "single"}`
- 为什么判定为空转：**脆弱（frail）是死状态**——`dealToEnemy`（玩家→敌人伤害结算）只扣格挡和血，全引擎没有一处读取敌人的 `status.frail` 来放大或改写伤害；frail 只在 applySpecial（施加）和回合递减（减到 0 删除）两处出现。施加了、倒计时了、然后什么都没发生。
- 主效果（13 伤）有效；空转的是脆弱挂件——这张卡的定价里脆弱是占了一部分价值的。

### 4. `trem_0034` 震语：断流 —— 同上（脆弱挂件空转）

- effect：`{"damage": 14, "resonance_cost": 6, "special": [{"code": "frail", "value": 1}], "target": "single"}`
- 同 #3：脆弱部分零结算；主体 14 伤 + 共振支付有效。

## 引擎键支持面对账（全部核过）

| 效果键（卡池实际用到的全部 12 个） | 引擎实现 |
|---|---|
| damage / hits | ✅ `web/index.html` playCard 伤害分支（多段循环） |
| block | ✅（含 bright +2、敏捷加成） |
| draw | ✅ |
| heal | ✅ |
| resonance_gain / resonance_drain | ✅ |
| resonance_cost | ✅ `:5713` 查量 + `:5733` 扣除 |
| gaze_cost | ✅ `:5709` 门槛（查完不扣） |
| gaze_gain | ✅ |
| special（15 个码） | 14 个有实现；**resonance_gain 无 case**（见 #2） |

cost_type：none / memory / vitality / mark / lock 全部有实现；`custom` 只出现在 `cards/_draft.json`（不在实装池）。

## 顺带发现：engine/core.js 副本过期（不是空转，但要报）

- `engine/core.js` 的 applySpecial **没有** 2026-11-04 的 value→V 归一化修复（web 副本有，注释写明「卡片数据里写的是 value，老代码只读 v」）——模块副本里 strength/dexterity/regenerate/thorns/gaze_reduce/burn 全部按默认值结算。
- 同类不同步：BASE_ENERGY（core=3 / web=4，见 `all_numbers.md` §9）。
- **未确认：engine/core.js 的定位**——如果它只是 web 的历史副本则无 gameplay 影响；如果有任何路径实际加载它（如测试/sim），这些数值 bug 是活的。建议设计者确认它的用途。

## 复算片段

```python
import sys; sys.path.insert(0, 'data/audit')
from audit_common import load_cards, all_cards
for cls, c in all_cards(load_cards()):
    e = c.get('effect') or {}
    if not any(k for k in e if k != 'target'):
        print('empty:', c['id'], c['name'])
# special 码支持面对照：web/index.html applySpecial 的 case 列表
# frail 死状态对照：engine/core.js dealToEnemy 不读 status.frail（grep 'status.frail' 全库核对）
```
