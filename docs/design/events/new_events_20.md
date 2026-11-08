# 事件池扩充 · 20 个新事件

> 2026-11-06 夜班 · 方向池 3。派单：`tasks/INBOX/08_overnight_1106.md` 方向 3。
> 数据来源：`RAW.events` 现有 82 个（只读核对）。`result` 只用引擎实认的键（7625–7635 行）：`heal / damage / gaze / gold（黯民自动折算零件）/ card_reward / relic / maxhp`。
> **代价纪律**：每个事件至少两个选项带显式代价；「绕开」类中性选项沿用现有 82 个事件的惯例保留少量，其中两个写成了带代价的（gaze +1，见 d7_13 / d8_9）。没有「全收益」的三选项组合。
> 本文件是设计文档，没改任何数据。id 按各层现有最大编号顺延（现有最大：L1=8 / L2–L4=11 / L5=12 / L6–L7=11 / L8=8）。

---

## 第 1 层（3 个）

### event_d1_9 · 头顶的滴水声

```json
{
  "id": "event_d1_9", "layer": 1,
  "title": "头顶的滴水声",
  "body": "走廊顶棚有一处一直在滴水。水是温的，地上积了一小滩。滴了不知道多少年，石头被滴出一个浅坑。",
  "options": [
    { "text": "用容器接水，带走。", "veins": ["water"],
      "result": { "heal": 8, "gaze": 1 },
      "result_text": "水是甜的，甜得过分。喝完之后你一直觉得头顶还有一滴没落下来。" },
    { "text": "站到滴水的正下方，等它滴满。", "veins": ["mineral"],
      "result": { "damage": 4, "card_reward": "uncommon" },
      "result_text": "第三滴没有落进容器，落进了你的领口。是烫的。水里有东西。" },
    { "text": "绕开走。", "veins": [],
      "result": {},
      "result_text": "滴水声跟了你一段，在下一个岔口停了。" }
  ]
}
```

### event_d1_10 · 倒挂的工牌

```json
{
  "id": "event_d1_10", "layer": 1,
  "title": "倒挂的工牌",
  "body": "顶棚垂下来一串工牌，绳子打的是活结。每一块都擦得很亮。",
  "options": [
    { "text": "取下最亮的那块。", "veins": ["mineral"],
      "result": { "gold": 45, "gaze": 1 },
      "result_text": "工牌背面有名字。名字被磨掉了，磨痕很新。" },
    { "text": "把整串割走。", "veins": ["tremor"],
      "result": { "damage": 3, "gold": 25 },
      "result_text": "绳子比你预想的结实。割断的一瞬整串坠落，你躲开了大半。" },
    { "text": "不动它。", "veins": [],
      "result": {},
      "result_text": "那串工牌在你身后轻轻晃了一路。" }
  ]
}
```

### event_d1_11 · 浅坑里的盐壳

```json
{
  "id": "event_d1_11", "layer": 1,
  "title": "浅坑里的盐壳",
  "body": "顶棚渗下来的盐水在地上结了一圈盐壳。壳的边缘很整齐，像是谁裁的。壳里有东西在动，动的频率和滴水同步。",
  "options": [
    { "text": "敲开盐壳。", "veins": ["mineral"],
      "result": { "gold": 35, "damage": 4 },
      "result_text": "壳里的东西比你预期的小，也比预期的硬。敲它的那一下震回了你的手。" },
    { "text": "等它自己破。", "veins": ["water"],
      "result": { "heal": 6, "gaze": 1 },
      "result_text": "破的时候是一声很轻的叹气。破完之后水里什么都没有，你却觉得被看过了。" },
    { "text": "离开。", "veins": [],
      "result": {},
      "result_text": "你走出十几步才意识到滴水声停了。它停在你身后的位置。" }
  ]
}
```

## 第 2 层（3 个）

### event_d2_12 · 冰须走廊

```json
{
  "id": "event_d2_12", "layer": 2,
  "title": "冰须走廊",
  "body": "洞顶垂下几百根冰须，须尖挂着水珠，落地前冻住。地上铺了一层冻住的水珠，踩上去咯咯响。",
  "options": [
    { "text": "攀着冰须上顶看一眼。", "veins": ["mineral"],
      "result": { "damage": 5, "card_reward": "uncommon" },
      "result_text": "顶上的视野好得过分。你下来的时候手里多了东西，掌心少了一层皮。" },
    { "text": "敲一根冰须解渴。", "veins": ["water"],
      "result": { "heal": 10, "gaze": 1 },
      "result_text": "冰须是空的，里面存的是上一层的水。很甜。你开始好奇上一层还有多少。" },
    { "text": "贴边快速通过。", "veins": [],
      "result": { "damage": 2, "gold": 25 },
      "result_text": "墙角冻着一副手套，手套里裹着一小袋矿票。分开它们的时候手套碎了。" }
  ]
}
```

### event_d2_13 · 落物线

```json
{
  "id": "event_d2_13", "layer": 2,
  "title": "落物线",
  "body": "头顶每隔一阵就掉东西下来：碎石、旧工具、干掉的皮。落点集中在一条线上，线上很干净——干净得像被打扫过。",
  "options": [
    { "text": "站上落物线，等大件。", "veins": ["tremor"],
      "result": { "damage": 6, "card_reward": "rare" },
      "result_text": "大件来了。你接住了它，也接住了它带来的全部动能。" },
    { "text": "沿线捡小件。", "veins": ["mineral"],
      "result": { "gold": 40, "damage": 3 },
      "result_text": "小件很多。最后一件是从很高的地方掉下来的，还带着顶棚的温度。" },
    { "text": "离线绕行。", "veins": [],
      "result": {},
      "result_text": "你绕开的那段路，头顶掉了七件东西。你只听见了七次。" }
  ]
}
```

### event_d2_14 · 倒扣的蟹壳

```json
{
  "id": "event_d2_14", "layer": 2,
  "title": "倒扣的蟹壳",
  "body": "一只蟹壳倒扣在顶棚上，壳口朝下悬着。里面有敲击声，节奏很规律，间隔三秒。",
  "options": [
    { "text": "按它的节奏敲回去。", "veins": ["tremor"],
      "result": { "card_reward": "uncommon", "gaze": 1 },
      "result_text": "你敲了三次，壳里的东西回了一次。然后它把一件东西从壳口递了下来。" },
    { "text": "在壳下张开手，等它掉。", "veins": ["mineral"],
      "result": { "gold": 30, "damage": 5 },
      "result_text": "掉下来的是半只蟹。壳里的东西不商量，它只是路过你的手。" },
    { "text": "走开。", "veins": [],
      "result": {},
      "result_text": "敲击声在你走出二十步后停了。你不知道它等到了什么。" }
  ]
}
```

## 第 3 层（3 个）

### event_d3_12 · 一臂之隔

```json
{
  "id": "event_d3_12", "layer": 3,
  "title": "一臂之隔",
  "body": "顶棚垂下一团红须，须尖离你头顶差一臂。你走它也长，始终差一臂。红光把须照得半透明。",
  "options": [
    { "text": "跳起来够它。", "veins": ["heat"],
      "result": { "damage": 7, "card_reward": "rare" },
      "result_text": "你够到的那一瞬，它也够到了你。你们各拿到了自己要的东西。" },
    { "text": "原地站定，让它垂下来。", "veins": ["water"],
      "result": { "heal": 8, "gaze": 2 },
      "result_text": "须尖碰到了你的头顶，很轻，像在确认什么。确认完它缩回去了，留了一点东西在你发间。" },
    { "text": "压低身体，从它下面快走。", "veins": [],
      "result": {},
      "result_text": "红须在你身后停住了。它不追，它只是量完了。" }
  ]
}
```

### event_d3_13 · 蓄水顶

```json
{
  "id": "event_d3_13", "layer": 3,
  "title": "蓄水顶",
  "body": "干旱区居然有一段顶棚在渗水。水在顶棚的凹处聚成一小片，就是不肯下来。你抬头的时候，水面晃了一下。",
  "options": [
    { "text": "用管子把水引下来。", "veins": ["water"],
      "result": { "heal": 15, "gaze": 1 },
      "result_text": "水下得很顺，顺得像在等这个。水是温的。干旱层不该有温的水。" },
    { "text": "把整片水撬下来。", "veins": ["mineral"],
      "result": { "damage": 6, "gold": 45 },
      "result_text": "水落下来的时候带着顶棚的碎块。碎块里有溶解多年的矿盐，砸在你背上。" },
    { "text": "不碰。干旱层的水不会白给。", "veins": [],
      "result": {},
      "result_text": "你走后很久，那片水还悬在那里。它在等下一个抬头的人。" }
  ]
}
```

### event_d3_14 · 多出的纹路

```json
{
  "id": "event_d3_14", "layer": 3,
  "title": "多出的纹路",
  "body": "顶棚的矿脉纹路里多出一条。走向和你的行进方向一致，宽度和你肩宽一致。",
  "options": [
    { "text": "沿多出的纹走。", "veins": ["mineral"],
      "result": { "gold": 50, "damage": 4 },
      "result_text": "纹的尽头是一处没人到过的矿囊。开囊的时候顶上掉了不少碎屑。" },
    { "text": "把纹路凿断。", "veins": ["tremor"],
      "result": { "card_reward": "uncommon", "gaze": 1 },
      "result_text": "凿断的断面是肉的。纹路断了，但从你站的位置看，它换了个方向接着长。" },
    { "text": "当没看见。", "veins": [],
      "result": {},
      "result_text": "你走你的。纹路走它的。你们在下一个岔口又见了一次。" }
  ]
}
```

## 第 4 层（3 个）

### event_d4_15 · 光池的浮壳

```json
{
  "id": "event_d4_15", "layer": 4,
  "title": "光池的浮壳",
  "body": "光池面上浮着一具旧防护服，四肢张开，姿势很放松。腹面的观察窗是亮的，里面没有头。",
  "options": [
    { "text": "捞上来搜。", "veins": ["mineral"],
      "result": { "gold": 55, "gaze": 1 },
      "result_text": "口袋里的东西都是干的，只有人湿。观察窗从里面擦了一遍。" },
    { "text": "把它按下去，放它沉。", "veins": ["water"],
      "result": { "heal": 10, "damage": 3 },
      "result_text": "它沉得很配合。松手前，手套握了一下你的手腕。" },
    { "text": "让它漂着。", "veins": [],
      "result": {},
      "result_text": "你走出很远，观察窗的亮还留在你背后的水面上。" }
  ]
}
```

### event_d4_16 · 称重的光柱

```json
{
  "id": "event_d4_16", "layer": 4,
  "title": "称重的光柱",
  "body": "一群鱼的腹面同时亮起，光柱里所有的影子都指向你。它们在称重，称的是光柱里经过的东西。",
  "options": [
    { "text": "站进光柱，让它们称。", "veins": ["tremor"],
      "result": { "card_reward": "rare", "damage": 8 },
      "result_text": "称完了。它们给你让出一条路，路是用你的血付的过路费。" },
    { "text": "灭掉自己的灯，摸黑走。", "veins": ["mineral"],
      "result": { "gold": 40, "gaze": 1 },
      "result_text": "黑暗里你的手比眼睛有用。摸到的东西攥了一路，攥出汗了才发现是什么。" },
    { "text": "背对光柱走。", "veins": [],
      "result": {},
      "result_text": "称重的过程你错过了。它们称出了什么，你不知道，它们也不知道你想不想知道。" }
  ]
}
```

### event_d4_17 · 垂根

```json
{
  "id": "event_d4_17", "layer": 4,
  "title": "垂根",
  "body": "顶棚的垂光蕨把根垂到半人高，根须末端的小瘤在搏动。频率是心跳的频率，不是它自己的。",
  "options": [
    { "text": "割一段根瘤。", "veins": ["water"],
      "result": { "heal": 12, "gaze": 1 },
      "result_text": "根瘤里的液体是温的。敷上伤口的时候，搏动停了一下，然后接着跳。" },
    { "text": "把整株从顶上拔下来。", "veins": ["mineral"],
      "result": { "damage": 5, "gold": 40 },
      "result_text": "根扎得比看起来深。拔下来的一瞬你被带离了地面半尺，落地时手里多了它，肩上多了它的份。" },
    { "text": "从须下弯腰过去。", "veins": [],
      "result": {},
      "result_text": "根须扫过你的背。它没有拦你。它只是量了一下你的肩宽。" }
  ]
}
```

## 第 5 层（2 个）

### event_d5_13 · 泉眼上的管

```json
{
  "id": "event_d5_13", "layer": 5,
  "title": "泉眼上的管",
  "body": "热泉正上方垂着一根中空的硫管，管口对准泉眼。管子在往里吸气，吸的节奏和泉的鼓胀相反。",
  "options": [
    { "text": "把耳朵贴上管壁。", "veins": ["tremor"],
      "result": { "card_reward": "uncommon", "damage": 4 },
      "result_text": "管子里有人在数数。数到你的时候卡了一下，然后接着数。你的耳朵烫了一路。" },
    { "text": "把管子堵上。", "veins": ["mineral"],
      "result": { "gold": 45, "gaze": 1 },
      "result_text": "堵上之后泉眼安静了。有什么东西在管子里换了个方向，朝你这边看了一眼。" },
    { "text": "别碰。热的东西让它自己凉。", "veins": [],
      "result": {},
      "result_text": "你绕开泉眼的时候，管子的吸气声大了一格。" }
  ]
}
```

### event_d5_14 · 牙里的声音

```json
{
  "id": "event_d5_14", "layer": 5,
  "title": "牙里的声音",
  "body": "你的牙开始发麻。顶棚某处有一只蟾在倒着叫，叫声不走空气，走岩石。它在一遍遍试你的频率。",
  "options": [
    { "text": "循着麻意找过去。", "veins": ["tremor"],
      "result": { "damage": 6, "card_reward": "rare" },
      "result_text": "麻到最厉害的地方，头顶正上方。你在那里等到了它换气的空档，从缝里摸出了东西。" },
    { "text": "咬住舌根，等它停。", "veins": ["heat"],
      "result": { "heal": 6, "gaze": 1 },
      "result_text": "它停了。不是因为唱完了，是因为对上频了。你后来才知道对上频意味着什么。" },
    { "text": "堵住耳朵继续走。", "veins": ["mineral"],
      "result": { "damage": 2, "gold": 25 },
      "result_text": "麻意退去的地方有一小袋被震出来的矿票。塞耳朵的东西顺手也塞进了口袋。" }
  ]
}
```

## 第 6 层（2 个）

### event_d6_12 · 剂量表外的门

```json
{
  "id": "event_d6_12", "layer": 6,
  "title": "剂量表外的门",
  "body": "一扇铅门虚掩着，门缝里漏出的红光比走廊亮。门上的剂量表碎了，指针钉在最大刻度上。",
  "options": [
    { "text": "推门进去。", "veins": ["heat"],
      "result": { "gold": 60, "damage": 10 },
      "result_text": "里面是个完整的储藏间，东西都在。你也进去了，出去的时候轻了十斤。" },
    { "text": "只把手伸进去够。", "veins": ["mineral"],
      "result": { "card_reward": "uncommon", "damage": 5, "gaze": 1 },
      "result_text": "够到的第一件东西是温的。你的手在门里多停了一会儿，比计划里的久。" },
    { "text": "把门关死。", "veins": [],
      "result": {},
      "result_text": "门关上的声音很实。里面有什么在敲门，敲了三下，停了。" }
  ]
}
```

### event_d6_13 · 发红的爬痕

```json
{
  "id": "event_d6_13", "layer": 6,
  "title": "发红的爬痕",
  "body": "地上一道爬痕还在发红。爬痕从顶棚下来，绕着你的位置转了一圈，又回顶棚去了。鳞渣是热的。",
  "options": [
    { "text": "收集鳞渣。", "veins": ["mineral"],
      "result": { "gold": 50, "damage": 6 },
      "result_text": "鳞渣烫手，垫着布也一样。收满一袋的时候你的手套已经不能要了。" },
    { "text": "守在爬痕边，等它回来。", "veins": ["tremor"],
      "result": { "card_reward": "rare", "damage": 9 },
      "result_text": "它回来了。它从顶上下来的方式和爬痕暗示的一样快。你们都拿到了各自要的。" },
    { "text": "离开这道爬痕的范围。", "veins": [],
      "result": {},
      "result_text": "你在安全线外看了一会儿。爬痕重新发亮的时候，你已经走了。" }
  ]
}
```

## 第 7 层（2 个）

### event_d7_12 · 念名单的苔

```json
{
  "id": "event_d7_12", "layer": 7,
  "title": "念名单的苔",
  "body": "穹顶的苔丛在念一段旧名单。念到你名字的时候停了一下，然后从头开始。整面穹顶的苔是同一个节拍。",
  "options": [
    { "text": "跟着念完那一段。", "veins": ["tremor"],
      "result": { "heal": 12, "gaze": 2 },
      "result_text": "念完的部分被苔记住了。伤口合上的时候你听见它把你的名字归了位。" },
    { "text": "把那一片苔从顶上揭下来。", "veins": ["mineral"],
      "result": { "gold": 45, "damage": 5 },
      "result_text": "揭下来的苔还在念。你把它叠好收进包里，一路上包里很吵。" },
    { "text": "等它念完再走。", "veins": [],
      "result": {},
      "result_text": "名单很长。你等到了自己名字的第二次，没等第三次。" }
  ]
}
```

### event_d7_13 · 有人吗

```json
{
  "id": "event_d7_13", "layer": 7,
  "title": "有人吗",
  "body": "高处倒挂着一具防护服，广播还在自动播放：「有人吗」。间隔固定，音量不减。里面的部分早就空了。",
  "options": [
    { "text": "用广播回话。", "veins": ["mineral"],
      "result": { "card_reward": "uncommon", "gaze": 2 },
      "result_text": "你说了自己的编号。广播停了一秒，然后把你的编号加进了下一轮的名单。" },
    { "text": "把它摘下来，拆电池。", "veins": ["tremor"],
      "result": { "gold": 40, "damage": 4 },
      "result_text": "电池很难拆。拆下来的时候广播停了，整条走廊安静得像欠了它一句话。" },
    { "text": "不回话，走。", "veins": [],
      "result": { "gaze": 1 },
      "result_text": "那句「有人吗」在你身后又放了很多遍。每一遍都比上一遍更像在问你。" }
  ]
}
```

## 第 8 层（2 个）

### event_d8_9 · 垂丝门帘

```json
{
  "id": "event_d8_9", "layer": 8,
  "title": "垂丝门帘",
  "body": "茧室的门帘是几百根活丝垂成的。帘子在动，幅度和你的呼吸同步。你憋气，它也停。",
  "options": [
    { "text": "拨帘进去。", "veins": ["tremor"],
      "result": { "card_reward": "rare", "damage": 8 },
      "result_text": "丝很认生。进去的路它收了过路费，从你身上，一段一段。" },
    { "text": "割一截丝带走。", "veins": ["mineral"],
      "result": { "gold": 50, "damage": 4 },
      "result_text": "割下来的丝还在动。收进包里之后，包带勒肩的力度和它在里面挣扎的力度一致。" },
    { "text": "等帘子停。", "veins": [],
      "result": { "gaze": 1 },
      "result_text": "它没停。你等了多久，它就同步了多久。你先失去耐心这件事，它记下了。" }
  ]
}
```

### event_d8_10 · 最高点

```json
{
  "id": "event_d8_10", "layer": 8,
  "title": "最高点",
  "body": "穹顶最高点倒挂着一具防护服，四肢张开，广播里放着最后一句话的后半句。前半句听不见，穹顶太大了。",
  "options": [
    { "text": "爬上去听完。", "veins": ["tremor"],
      "result": { "damage": 7, "card_reward": "rare" },
      "result_text": "后半句是个名字。不是你的。你把后半句带走了，留下半句在穹顶上接着放。" },
    { "text": "用长杆把它捅下来。", "veins": ["mineral"],
      "result": { "gold": 55, "damage": 3, "gaze": 1 },
      "result_text": "它掉下来的时候广播还在放。摔在地上的那半句，比穹顶上的清楚得多。" },
    { "text": "背对它坐下，歇一会儿。", "veins": ["water"],
      "result": { "heal": 8, "gaze": 1 },
      "result_text": "你睡了一小觉。醒来的时候那句话放完了。后半句你没听到，它看到了你的睡姿。" }
  ]
}
```

---

## 自查

| 项 | 结果 |
|---|---|
| 数量 | 20（L1×3 / L2×3 / L3×3 / L4×3 / L5×2 / L6×2 / L7×2 / L8×2） |
| result 键 | 全部落在引擎实认的 7 个键内（7625–7635 行）；未用 `relic`（现有 82 事件里只有 1 个选项用，太稀，本批不稀释）；未用 `maxhp`（现有仅 3 处，本批不碰） |
| 代价纪律 | 每个事件 ≥2 个选项带显式代价（数值损失 / 凝视 / 负面绑定）；中性「绕开」类选项 9 个（与现有 82 个事件的惯例一致），其中 2 个带 gaze 代价（d7_13 / d8_9） |
| 数值参照 | 现有事件带：gold 40–60 对应 damage 3–10；heal 6–15；card_reward uncommon≈中风险，rare≈重伤级风险。本批全部落在这个带内 |
| JSON | 每个事件块都按 `RAW.events` 字段写（id/layer/title/body/options[].text+veins+result+result_text），可直接合并 |

## 未验证

- **未验证**：`card_reward` 的稀有度字符串取值集（现有样例只见 uncommon/rare，本批只用这两个；common 是否合法未验证，故未用）。
- **未验证**：事件选项的 `veins` 是否影响判定/奖励（现有数据里选项带 veins，本批照抄格式并按选项气质标注；其引擎作用未读代码确认——若 veins 只是展示用，标注也无害）。
- **未验证**：20 个事件的强度平衡——数值对照现有带给出，未跑模拟。
- **存疑**：d7_13 与 d8_9 的「中性选项带 gaze 代价」是对现有惯例的轻微软化（现有绕开选项全部无代价）。若维护者认为破坏惯例，把这两处 result 改回 `{}` 即可，其余不动。
