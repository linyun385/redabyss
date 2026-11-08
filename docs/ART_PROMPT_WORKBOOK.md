# 提示词工作手册（骨架 + 异化词库 + 30 条样板）

> 配套：`docs/ART_PROMPT_SPEC.md`（规范）· `docs/ART_DIRECTION_V2.md`（方向与复用规则）
> 本文件是**可直接照填的生产手册**：骨架填空 → 选异化标记 → 拼风格 → 跑校验。
> 每条英文提示词都附**中文对照**，方便你审。

---

## 一、四套句式骨架（填空式，中英对照）

### 1. 生物类敌人（动物形）
```
a <体型形容> <生物类属> that <异化标记 1>, <异化标记 2 可选>,
<关键肢体/器官>, hanging <姿态：倒挂在天花板/腹面朝上>, its feeding organs on the underside,
lit from below by a red glow, <环境痕迹>
```
> 中文：**一只〈体型〉的〈属类〉，它的〈部位〉〈异化〉，〈肢体/器官〉，倒挂在〈位置〉、取食器官朝下，
> 被下方的红光照着，〈环境〉。**
> ⚠ 生物类**必须**含倒吊/器官朝下 + 自下而上的红光，缺一即打回（规范 §一之二）。

反例：`a frog`（地球物种直译）；`a creature of the abyss`（无形态）。

### 2. 非动物敌人（菌/苔/晶体/膜）
```
a <扩散方式> <材质主体> spreading <方向/部位>, <表面质感>, <内部结构>, <它留下的痕迹>
```
> 中文：**一丛〈扩散方式〉的〈材质〉，〈表面〉，〈内部〉，〈痕迹〉。**

这类**不许有脸、不许有眼睛**（除非异化标记明确写"长出了眼"）。

### 3. 工具/物件卡
```
a <用途可读的物件>, <材质与磨损>, <异化标记>, <使用痕迹>, <摆放方式>
```
> 中文：**一件〈用途能看出来的物件〉，〈材质与磨损〉，〈异化〉，〈使用痕迹〉，〈怎么放着的〉。**

### 4. 事件
```
<谁/什么> <处在什么状态>, <正在发生或已经发生的事>, <一处关键细节>, <环境>
```
> 中文：**〈谁〉〈状态〉，〈发生的事〉，〈关键细节〉，〈环境〉。**

事件**必须有"事"**：不能只是空景，也不能只是符号。

---

## 二、异化词库（红渊化标记，中英对照）

> 每条 prompt 取 **1–2 个**。同生态里不要连续用同一个，避免整套图千篇一律。

### A 材料替代（生物长出非生物材料）

| # | 英文语块 | 中文 | 适用层 |
|---|---|---|---|
| A1 | back split into overlapping salt-crystal plates | 背部分裂成层叠的盐晶板 | D1–D3 |
| A2 | hide replaced by a crust of rusted iron scales | 皮肤换成锈铁鳞壳 | D6–D7 |
| A3 | limbs fused into copper fins | 四肢熔成铜质鳍 | D5 |
| A4 | eyes replaced by glass beads, no pupils | 眼睛换成玻璃珠，没有瞳孔 | 通用 |
| A5 | bone grown through the skin like white coral branches | 骨头穿出皮肤，像白色珊瑚枝 | D4 |
| A6 | flesh turned to translucent wax, organs visible | 血肉变成半透明蜡质，内脏可见 | D4–D5 |
| A7 | spine exposed as a segmented steel rod | 脊柱外露成一节节钢杆 | D6–D7 |
| A8 | mouth sealed with a brass valve | 嘴被黄铜阀门封住 | D5–D6 |
| A9 | fins turned to thin papery sheets that tear | 鳍变成会撕裂的薄纸片 | D2–D3 |
| A10 | shell laminated from pressed debris and bone dust | 壳由压实的碎屑与骨粉层积而成 | D1–D2 |

### C 工艺寄生（身体被"维修/登记"过）

| # | 英文语块 | 中文 |
|---|---|---|
| C1 | stitched along the spine with copper wire | 沿脊柱用铜线缝合 |
| C2 | a brass maintenance tag bolted to its shoulder | 肩上铆着一块黄铜维修牌 |
| C3 | serial numbers cut into the carapace | 甲壳上刻着编号 |
| C4 | hoses grafted into its sides, still dripping | 侧面接进软管，还在滴 |
| C5 | a hand-forged iron brace bolted around one leg | 一条腿铆着手打铁支架 |
| C6 | seams of tar and thread crossing its belly | 腹部横过沥青与线的缝口 |
| C7 | a small glass gauge embedded in its flank | 侧腹嵌着一只小玻璃表 |
| C8 | patches of another animal's hide sewn on | 缝着别的兽皮补丁 |
| C9 | a ring of nails driven in a circle around its head | 头周钉着一圈钉子 |
| C10 | chains threaded through its ribs | 肋骨间穿过锁链 |

### B 器官错位（少量使用，一条 prompt 最多 1 个）

| # | 英文语块 | 中文 |
|---|---|---|
| B1 | six small eyes set in a ring around a wide flat head | 宽扁的头上一圈六只小眼 |
| B2 | a second smaller skeleton curled inside a translucent belly | 半透明腹中蜷着第二具小骨架 |
| B3 | two mouths, the lower one stitched shut | 两张嘴，下面那张被缝住 |
| B4 | too many thin fingers on each limb | 每条肢体上过多细指 |
| B5 | a second heart beating outside its chest | 第二颗心脏在胸腔外跳动 |

---

## 三、30 条样板（10 敌 / 10 卡 / 10 事件）

> 每条都自带异化标记；`STYLE` = 规范 §五 的固定后缀（下面省略不写）。
> 校验规则见 §四，这 30 条应当全部通过。

### 敌人（10）

**1. 嗜热古菌（D1）** — A1
> a crusted colony of thermophilic bacteria hanging down from a ceiling pipe, its blistering orange-brown crust shot through with pale salt-veins (A1), feeding mouths clustered on its underside, steam curling downward, lit from below by a deep red glow, water seeping off its tips
> **中文**：一丛从顶上的管道**倒挂下来**的嗜热菌落，橙褐硬壳布满苍白盐脉（A1），**取食口聚在底面**，热气向下卷，**被下方深红的红光照着**，尖端渗着水。

**2. 腐生菌（D1）** — C8
> a saprophytic fungus erupting from a small carcass, pale stalks and a blackened cap, patches of another animal's hide sewn onto its stem (C8), spores dusting the floor, threads rooting into bone, lit from below by a red glow rising from the floor, hanging inverted, feeding organs on the underside
> **中文**：从一具小兽尸骸上爆出的腐生菌，菌柄苍白、菌盖发黑，菌柄上缝着另一只兽的皮补丁（C8），孢子落满地面，菌丝扎进骨头。

**3. 隙居螨（D1）** — A10
> a flat many-legged mite wedged in a wall seam, shell laminated from pressed debris and bone dust (A10), eight jointed legs splayed sideways, mouthparts probing the crack, salt crystals packed around it, lit from below by a red glow rising from the floor, hanging inverted, feeding organs on the underside
> **中文**：卡在墙缝里的扁平多足螨，壳由压实的碎屑与骨粉层积而成（A10），八条节肢向两侧张开，口器探进裂缝，周围塞满盐晶。

**4. 管廊苔毯（D1）** — C9
> a dense pale moss carpeting a corroded corridor floor, raised into a lumpy body with no face, a ring of nails driven in a circle where a head should be (C9), tendrils creeping along pipe joints, lit from below by a red glow rising from the floor, hanging inverted, feeding organs on the underside
> **中文**：铺满腐蚀管廊地面的苍白苔层，隆起成没有脸的身体；本该是头的位置钉着一圈钉子（C9），藤蔓沿管道接口蔓延。

**5. 管壁钟乳盐（D1）** — A1
> a cluster of salt stalactites growing from a pipe wall, faceted needles banded with pale salt-veins (A1), mineral crust flaking away, condensation dripping from the tips, lit from below by a red glow rising from the floor, hanging inverted, feeding organs on the underside
> **中文**：管壁上长出的一簇盐钟乳，多面针状、带着苍白的盐脉条纹（A1），矿壳正在剥落，尖端滴着冷凝水。

**6. 冷洞食腐鳗（D2）** — A4
> a long eyeless eel coiled in black water, ring of small teeth in a round mouth, eyes replaced by glass beads, no pupils (A4), pale scarred skin, weed twisted around its middle, only the head breaking the surface, lit from below by a red glow rising from the floor, hanging inverted, feeding organs on the underside
> **中文**：盘在黑水里的一条细长鳗，圆嘴一圈细齿，眼睛换成没有瞳孔的玻璃珠（A4），皮肤苍白带疤，水草缠在腰部，只有头露出水面。

**7. 冷洞跳蛛（D2）** — B1
> a heavy jumping spider clinging upside down to a wet ceiling, eight thick hairy legs hooked into the stone, six small eyes ringed around two large ones (B1), abdomen marked with a pale skull-like mottle, silk anchor line hanging down, lit from below by red light
> **中文**：**倒挂在湿顶面上**的粗壮跳蛛，八条毛腿钩进石头，六只小眼环着两只大眼（B1），腹部有骷髅状斑纹，**丝线向下垂**，被下方红光照着。

**8. 墟蟹（D2）** — A10 + C3
> a crab-like scavenger wearing a shell laminated from scrap plates and bone dust (A10), serial numbers cut into the carapace (C3), one claw wrapped in cable, a broken gauge wired to its back, lit from below by a red glow rising from the floor, hanging inverted, feeding organs on the underside
> **中文**：背着废板与骨粉层积壳的蟹状拾荒者（A10），甲壳上刻着编号（C3），一只钳子缠着电缆，背上绑着一只破表。

**9. 休眠两栖类（D2）** — B2
> a pale frog-like amphibian half-submerged in seepage water, wet mottled skin, visible gills, a second smaller skeleton curled inside a translucent belly (B2), one eye half open, crouched low, lit from below by a red glow rising from the floor, hanging inverted, feeding organs on the underside
> **中文**：半泡在渗水里的苍白蛙形生物，湿斑皮肤、可见鳃，半透明的腹中蜷着第二具较小的骨架（B2），一只眼半睁，伏得很低。

**10. 干旱肺鱼（D3）** — A9
> a lungfish curled inside a dried mud cocoon at the bottom of an empty pool, heavy scaled body, fins turned into thin papery sheets that tear (A9), mouth sealed with mucus, cracks radiating through the mud, lit from below by a red glow rising from the floor, hanging inverted, feeding organs on the underside
> **中文**：蜷在空池底干泥茧里的肺鱼，身体厚重有鳞，鳍变成会撕裂的薄纸片（A9），嘴被黏液封住，泥面裂出放射状纹。

### 卡牌（10）

**11. 例检条款（anm_0004）** — C3
> a worn metal clipboard holding an inspection checklist, a mechanical stamp arm pressed onto the sheet, serial numbers cut into its back plate (C3), hanging pencil on twine, oil stains and a chipped corner, lit from below by a red glow rising from the floor
> **中文**：一块旧金属夹板夹着检查单，机械印章压在纸上，背板刻着编号（C3），铅笔用细绳吊着，油渍与磕破的边角。

**12. 备用照明电池（anm_0003）** — A2
> a heavy salvaged battery pack wired to a cracked work lamp, casing crusted with rusted iron scales (A2), corroded terminals, coiled cable, one red diode still lit, lit from below by a red glow rising from the floor, hanging inverted, feeding organs on the underside
> **中文**：一只接在破裂工作灯上的旧电池组，外壳结着锈铁鳞（A2），接线柱腐蚀，电缆盘着，一颗红灯还亮着。

**13. 聚能枪（dive_0002）** — A8
> a handheld energy rifle heated from within, segmented barrel whose muzzle is sealed with a brass valve (A8), pressure gauge on the grip, scorched glove beneath it, heat shimmer above the seam, lit from below by a red glow rising from the floor, hanging inverted, feeding organs on the underside
> **中文**：一把从内部发热的手持能量枪，分段枪管的枪口被黄铜阀门封住（A8），握把上有压力表，下面压着一只烧焦的手套，接缝上方有热浪。

**14. 氧气再生器（dive_0005）** — C7
> a compact oxygen recycler with a fresh filter cartridge screwed in, ribbed hoses and brass couplings, a small glass gauge embedded in its side (C7), condensation on the canister, on a scratched bench, lit from below by a red glow rising from the floor, hanging inverted, feeding organs on the underside
> **中文**：一台紧凑型氧气再生器，新滤芯拧进一半，罗纹软管与铜接头，侧面嵌着一只小玻璃表（C7），罐体有冷凝水，放在刮花的台面上。

**15. 震频器（dive_0025）** — B5
> a pocket tremor meter, round dial with a needle stopped between two ticks, ribbed brass housing, a second tiny heart-like bulb pulsing on its underside (B5), strap hanging down, held inverted so its scale faces the floor, lit from below by a red glow rising from the floor
> **中文**：一只口袋震频仪，圆表盘上的指针停在两个刻度之间，罗纹黄铜外壳，底面一颗心跳般搏动的小灯泡（B5），皮带别在扣上。

**16. 猎巫者的绳（cng_0043）** — C1
> a coil of braided rope tied in a reusable slip noose, one strand spliced with copper wire stitches (C1), frayed end, knots darkened by handling, lying on bare stone, lit from below by a red glow rising from the floor, hanging inverted, feeding organs on the underside
> **中文**：一盘编绳打的活结绳圈，其中一股用铜线缝合拼接（C1），末端磨散，绳结被摸得发黑，摊在裸石上。

**17. 光导透镜（残）（dive_0001）** — A4
> a cracked light-conduit lens mounted in a brass ring, fracture running across the glass, along the crack small glass beads set like pupils (A4), leather grip worn smooth, lit from below by a red glow rising from the floor, hanging inverted, feeding organs on the underside
> **中文**：一枚嵌在黄铜环里的裂透镜，裂纹横穿镜面，裂缝上嵌着几颗像瞳孔的玻璃珠（A4），皮质握把磨得发亮。

**18. 巡夜灯（cng_0005）** — C2
> a small patrol lamp with a hooded shade, brass maintenance tag bolted to its handle (C2), wick trimmed short, soot on the rim, resting on a stone step, lit from below by a red glow rising from the floor, hanging inverted, feeding organs on the underside
> **中文**：一盏带罩的小巡夜灯，提手上铆着黄铜维修牌（C2），灯芯修得很短，灯沿有烟熏，搁在石阶上。

**19. 王国账簿（cng_0002）** — C9
> a thick ledger bound in cracked leather, pages ruled but mostly blank after the first third, nails driven in a ring around the spine (C9), ribbon marker, dust in the gutter, lit from below by a red glow rising from the floor, hanging inverted, feeding organs on the underside
> **中文**：一本厚账簿，龟裂皮革封面，前三分之一之后大多空白，书脊一圈钉着钉子（C9），夹着丝带书签，书槽里积灰。

**20. 红渊研究院·频谱印章（dive_0078）** — A5
> a stamp carved from a single piece of bone-white coral (A5), handle banded with copper wire, ink pad dried to a crust, one test impression on scrap paper showing a ragged spectrum, lit from below by a red glow rising from the floor, hanging inverted, feeding organs on the underside
> **中文**：一枚用骨白珊瑚整块雕成的印章（A5），柄上缠着铜丝，印泥干成硬壳，废纸上留着一道毛糙的频谱试印。

### 事件（10）

**21. 矿道口的碎石（event_d2_1）**
> freshly moved rubble blocking a mine entrance, half a glove caught between the stones, drag marks leading out of the dark, a lantern left behind still warm
> **中文**：新搬开的碎石堵住矿道口，石缝里卡着半截手套，拖痕从黑暗里拖出来，旁边搁着一盏还温的灯。

**22. 会自己开关的矿灯（event_d2_2）**
> a single mining lamp hanging by its cable in an empty tunnel, lit although no one is there, its beam on bare rock, a duty roster nailed nearby with one name scratched out, lit from below by a red glow rising from the floor
> **中文**：空隧道里一盏挂在电缆上的矿灯亮着，没有人；光打在裸岩上，旁边钉着值班表，一个名字被划掉。

**23. 穿防护服的遗体（event_d3_1）**
> a body in an intact protective suit slumped against the rock wall, knees up, round glass faceplate with faint scratches on its inner side, dust on the shoulders, the corridor ahead washed in a red glow rising from the floor, lit from below by a red glow rising from the floor
> **中文**：一具穿着完整防护服的遗体靠着岩壁坐在地上，膝盖屈起，圆形玻璃面罩内侧划着小字，肩头落灰，身后是空走廊。

**24. 一池不流动的水（event_d3_2）**
> a pool of still water flat as wax, clear to the bottom, a second layer of water beneath moving downward, small stones settled on it without sinking, lit from below by a red glow rising from the floor
> **中文**：一池平得像蜡的水，清可见底，底下还有一层水在向下流动，小石子搁在水面上却没沉下去。

**25. 渊民的埋骨布（event_d4_1）**
> a burial cloth spread in a hollow of the cave wall, four corners weighted with stones, the cloth empty but folded with ceremony, ash and a single red thread on it, lit from below by a red glow rising from the floor
> **中文**：摊在洞壁凹处的埋骨布，四角压着石头，布是空的却叠得很郑重，上面有灰和一根红线。

**26. 烧过又长回来的红蕨（event_d4_2）**
> a patch of red ferns that burned and grew back, ash clinging to the roots, new fronds pushing up redder than the rest, charred stone underneath, lit from below by a red glow rising from the floor
> **中文**：一片烧过又长回来的红蕨，灰还沾在根上，新叶比别处更红，下面是烧焦的石头。

**27. 反应堆城的废弃管道（event_d5_2）**
> a thick pipe hanging from the ceiling through a banded metal joint, its open end pointed upward, a puff of hot air leaking out at regular intervals, condensation running down its outside, lit from below by a red glow rising from the floor
> **中文**：一根从顶上垂下来的粗管，开口朝天，每隔一阵漏出一口热气，外壁淌着冷凝水。

**28. 一块有字的相石（event_d6_1）**
> a fist-sized stone on the ground with shallow markings cut into one face, its edges polished by handling, a thin layer of dust disturbed around it, lit from below by a red glow rising from the floor
> **中文**：地上的一块拳头大石头，一面刻着浅痕，边缘被摸得很光，周围薄灰被动过。

**29. 震台上的旧刻痕（event_d7_1）**
> shallow tally marks cut into a stone platform, decades of them layered over each other, one fresh scratch among the old ones, dust settled in the grooves
> **中文**：石台上刻着的浅记数痕，几十年的刻痕彼此覆盖，旧痕里有一道是新的，沟槽里积着灰。

**30. 还在转的旧光者自动门（event_d7_2）**
> a circular automatic door still turning slowly in a dark hall, its iris of metal plates half open, light leaking from the seam, dust spiralling in the draft it makes, lit from below by a red glow rising from the floor
> **中文**：一扇仍在暗厅里缓慢转动的圆形自动门，金属虹膜半开，缝隙漏光，它带起的气流卷着灰尘打转。

---

## 四、机械校验（写完必跑）

```powershell
node tools\check_prompts.js            # 扫 data/art_families.json + 本手册里的样板
```

规则（任一不过就打回）：

| # | 规则 |
|---|---|
| 1 | 具体名词 ≥3（legs/plates/valve/stitched/gauge…）|
| 2 | 无抽象词：`symbol|emblem|abstract|essence|embodiment` = 0 |
| 3 | 无素描词：`pencil|graphite|charcoal` = 0 |
| 4 | 无排版词：`diagram|callout|inset|multiple views|study sheet` = 0 |
| 5 | 有异化标记：命中 A/C/B 词库至少 1 个 |
| 6 | 无画面内文字：`text|letters|labels|signature` = 0（风格段里的 `no text` 除外）|
| 7 | 跨类不复用：同一 prompt 不服务两个类别 |
| 8 | 族内成员 ≤3 |

---

## 五、生产 SOP（谁做、怎么分批）

| 步骤 | 谁 | 产出 |
|---|---|---|
| 1 | 本手册 + 规范 | 骨架、词库、30 条样板（已完成）|
| 2 | 你审这 30 条 | 「对味 / 不对味 + 哪句不对」|
| 3 | GLM（有额度时）或新 DSH 会话 | 按手册批量产出 280 族 |
| 4 | 我 | 跑校验 → 抽 20 条给你 → 过了才进生成队列 |
| 5 | 夜间脚本 | `night_gen.py --start 23:00 --end 08:00` |
| 6 | 你 | 工作台审图 / 标记 / 回队 |

**分批粒度**：敌人 60–90 族一批、事件 102 一批、卡牌 100–150 一批（每批出完先审再下一批）。
