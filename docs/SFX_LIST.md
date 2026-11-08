# SFX_LIST — 音效钩子清单（T41，只留钩子不生成音频）

> 接口：`playSfx(code, opts)`（web/index.html）。`window.__SFX_LOG` 存在时收集全部 code 供对账；`window.__SFX_MUTED` 为静音开关入口（留位未实现）；接管通道 `window.RedAbyssSFX = function(code, opts){...}`。
> **本任务没有生成/下载/嵌入任何音频。** 以下每条都配了一句「不要什么」，供未来选音的人避坑。

## 卡牌

| code | 触发 | 描述 | 不要什么 |
|---|---|---|---|
| card.play.attack | 打出攻击牌 | 短促，有金属感 | 不要尖锐刺耳 |
| card.play.skill | 打出技能牌 | 闷响，像拍在石头上 | 不要电子感音效 |
| card.play.power | 打出能力牌 | 低而长的持续感 | 不要悠扬旋律 |
| card.play.cost | 打出带代价的牌（叠加在类型音之上） | 叠一层"东西被拿走"的抽离声 | 不要血腥 |

## 战斗

| code | 触发 | 描述 | 不要什么 |
|---|---|---|---|
| combat.start | 进入战斗 | 一下沉底的重音 | 不要激昂开场曲 |
| enemy.hit | 敌人受击 | 闷击，带一点湿 | 不要清脆的打击乐 |
| combat.hurt | 玩家受击 | 比 enemy.hit 更钝，贴近耳侧 | 不要惨叫 |
| combat.block | 获得格挡 | 金属盾面轻震 | 不要 helium 变声感 |
| combat.kill | 敌人死亡 | 塌落声，短 | 不要爆炸 |

## 状态

| code | 触发 | 描述 | 不要什么 |
|---|---|---|---|
| state.resonance | 共振跨阈值（配合屏幕闪红） | 低频轰鸣，一拍 | 不要爆炸 |
| state.gaze | 凝视 +1 | 极短的沙沙声 | 不要刺耳 |
| state.energy_empty | 点了能量不够的牌 | 空握的一声 | 不要错误提示蜂鸣 |

## 界面

| code | 触发 | 描述 | 不要什么 |
|---|---|---|---|
| ui.click | 选职业 / 点地图节点 | 轻石子相碰 | 不要鼠标电音 |
| ui.page | 打开 / 合上面板 | 纸页翻动的颗粒摩擦 | 不要抽屉声、不要重物声 |

## 特殊

| code | 触发 | 描述 | 不要什么 |
|---|---|---|---|
| special.boss_phase | Boss 切换阶段 | 一声很远的钟 | 不要号角 |
| special.world_switch | 入梦 / 醒来（苍民） | 惊醒式的短促转换（420ms：一下高频瞬态，然后快速沉下去） | 不要魔法叮、不要拖长 |
| special.egg | 彩蛋触发（T39，金色微闪同时） | 一声轻笑规模的短音 | 不要滑稽喜剧音 |
| special.victory | 通关结算 | 长而低的释放 | 不要凯旋号角 |
| special.death | 死亡结算 | 一口气呼尽 | 不要悲怆弦乐 |

## 氛围音（setLayerAmbience(depth)，空实现，只在 applyLayerTheme 里被调用）

接口已留：`setLayerAmbience(depth)` 会向 `__SFX_LOG` 写入 `ambience.depthN` 占位记录。每层的氛围按"越深越不像地表"设计：

| 层 | ambience.depthN | 应该有什么 | 不要什么 |
|---|---|---|---|
| 1 地表死寂区 | ambience.depth1 | 远处的风、地表电台的残响 | 不要鸟鸣 |
| 2 外层冷洞 | ambience.depth2 | 滴水、金属冷缩的咔声 | 不要音乐 |
| 3 干旱空洞区 | ambience.depth3 | 干燥的沙粒摩擦、岩层空腔回声 | 不要水声 |
| 4 稳定空洞海 | ambience.depth4 | 极低频嗡鸣、几乎听不见的合唱 | 不要旋律 |
| 5 热泉裂带 | ambience.depth5 | 蒸汽、金属呻吟、远处泵机 | 不要沸腾咕嘟声 |
| 6 辐射矿石区 | ambience.depth6 | 电流嘶嘶、盖革计数器式哒声 | 不要警报 |
| 7 核心高热区 | ambience.depth7 | 心跳般的低频脉冲、烧灼声 | 不要尖叫 |
| 8 红渊核心 | ambience.depth8 | 血声、所有层的回声叠在一起 | 不要合唱高潮 |

---

## 实现记录（2026-11-05 深夜，用户连续三轮反馈）

**代码**：`tools/sfx_synth_full.py`（生成）· `tools/sfx_check.py`（频谱校验）· `web/sfx_preview.html`（试听）
**接入**：`web/index.html` 里的 `window.RedAbyssSFX` / `window.RedAbyssAmbience` / `window.RedAbyssVolume`
**现状**：27 个 wav（19 音效 + 8 层氛围），全本地合成，零成本。

### 三轮改了什么

| 轮次 | 用户反馈 | 改动 |
|---|---|---|
| v1 | — | 首版：峰值归一化 0.85 |
| v2 | 「声音太小了，基本听不见」「入梦太长了」「通关太低」「界面只要一个」 | 峰值 0.85→0.95；低频全过 tanh 饱和（生成谐波，笔记本才听得见）；victory 44Hz→80Hz+谐波；world_switch 1100ms→420ms；ui.open/close 合并成 ui.page |
| v3 | 「不像书页翻动」 | ui.page 改成**颗粒包络**：一串 4–15ms 随机短脉冲去切噪声，而不是连续噪声乘平滑包络 |

### 两条踩过的技术弯（别再踩）

1. **纯低频 = 静音**。笔记本扬声器放不出 150Hz 以下。v1 的 victory 基频 44Hz，用户听不到。
   解法是饱和（tanh）生成谐波，或者直接把基频提上去。**不要用「频率低 = 沉重」这个直觉做音效。**
2. **连续噪声 + 平滑包络 ≠ 摩擦声**。摩擦声的物理特征是「颗粒」——大量短促脉冲。
   连续噪声无论怎么滤波都只会是「嘶——」。要碎，必须用颗粒包络。

### 已知不满意 / 没做完

- `ui.page` 用户评价「也行，虽然不像书页翻动，但还可以」。**不是最终版**，只是够用。
  真要做对，需要解一段真实书页录音的频谱包络来对照（当时系统里没有 ffmpeg，没做成；
  装了 `imageio-ffmpeg` 但下载太慢，用户说先这样，任务已取消）。
- 8 层氛围都在，但**没在游戏里实测过**：`setLayerAmbience` 只在 `applyLayerTheme` 里被调，
  切层时的交叉淡入淡出还没验证。
- 所有音效都**没有在真实战斗里听过**——音画同步、触发时机、连打时的重叠，全都未知。
