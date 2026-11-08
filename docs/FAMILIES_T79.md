# T79 补做核查报告：素材「形态族」划分与逐族提示词清单

> 补做核查：2026-11-03 夜班补做号。
> 背景：TASK_DONE.md 无 T79 记录，但 `data/art_families.json` 已存在。核查结论：**该文件只是 2026-11-01 的 20 族样张（文件内 `_about`/`_note_members` 自述"草稿/样张"），T79 未完成。**
> 本次铁律遵守：未改 `data/art_families.json`、`web/`、`engine/`；仅新增 `tools/check_families.js`（原缺失，本次补写，只读校验）与本文档。

## 一、口径说明（任务书数字 vs 现状）

| 项 | tasks/T79.md 写的 | 实际（以 data/art_catalog.json 为准） |
|---|---|---|
| 敌人 | 145 | **113**（`enemy_*`，kind=foe）|
| 卡牌 | 266 | **266**（`anm_/cng_/dive_/trem_`，kind=card）|
| 事件 | 102 | **82**（`event_*`，kind=evt）|
| 合计 | 513 | **461** |

- 任务书的 145/266/102 来自 `docs/art/ART_DIRECTION_V2.md` §四的旧"一对象一图"表，与现目录不符；**校验器一律按 art_catalog.json 实际条数断言**。
- 类目键名：目录里事件的 kind 记作 `evt`，族表里的类目键记作 `event`；校验器已做等价映射（不算跨类别冲突）。

## 二、验收点清单与判定

| # | 断言（T79 验收表） | 通过线 | 现状 | 判定 |
|---|---|---|---|---|
| 1 | 三类覆盖率 | 100%（按实际口径 113/266/82）| foe 10/113（8.8%）、card 6/266（2.3%）、event 4/82（4.9%）；合计 20/461（4.3%）| **FAIL** |
| 2 | 跨类别复用 | 0 | 0 冲突（含：成员类别与族类别、同 id 跨类、重复成员三项均 0）| PASS |
| 3 | 每族成员数 | ≤3 | 最大 1（20 族全部单成员）| PASS |
| 4 | 族数带 | foe 60–90 / card 100–150 / event 102±10% | foe 10 / card 6 / event 4，全部低于下限 | **FAIL** |
| 5 | prompt 具体名词 | 每条 ≥3 个具体物名词；0 条命中 abstract/symbol/emblem | 20/20 条 ≥3（词表扫描）；禁语命中 0 | PASS |
| 6 | 抽样 15 族人工判"同族同类" | 人工 | 样张全部单成员，「同族相似性」无从检验（空转通过）；抽读 20 条 prompt 与对象 `desc` 语义均吻合 | N/A（待成品复验）|

补充检查（校验器附加项）：

| 项 | 判定 |
|---|---|
| 族 id 命名（`foe_family_*` / `card_family_*` / `evt_<eventId>`）| PASS（20/20）|
| style 档位 = A（BOSS/结局 C 档不进族表）| PASS（20/20 为 A）|
| 事件族 = 一事件一族 | PASS（4 族均 1:1，尚无反例）|
| 成员 id 必须存在于 art_catalog.json | PASS（0 缺失）|

## 三、统计（node tools/check_families.js 实跑输出，2026-11-03）

```text
类别      目录数   已覆盖  覆盖率    族数   复用率(成员/族)  单成员族  最大族
foe         113       10     8.8%     10           1.00       10      1
card        266        6     2.3%      6           1.00        6      1
event        82        4     4.9%      4           1.00        4      1
合计         461       20     4.3%     20           1.00

被最多共用的前 10 族：（当前族表无多成员族，复用率 1.00，Top10 亦全为 1 成员）
  card_family_battery_lamp [anm_0003] / card_family_energy_gun [dive_0002] /
  card_family_inspection_board [anm_0004] / card_family_noose_rope [cng_0043] /
  card_family_oxygen_rig [dive_0005] / card_family_tremor_meter [dive_0025] /
  evt_event_d2_1 / evt_event_d2_2 / evt_event_d3_1 / evt_event_d4_2

结论：FAIL（3 条断言未过：A1 覆盖率 ×3 类；退出码 1）
```

- **复用率**（T79 口径 = 成员数/族数）：三类均 1.00 —— 样张阶段完全没有发生复用，R2 的"一张图服务 ≤3 个对象"尚无实际案例。
- **Top10 共用族**：全为 1 成员（见上），无多成员族可比。

## 四、缺口清单

1. **覆盖缺口（主缺口）**：缺 441 个对象的族归属 —— foe 缺 103、card 缺 260、event 缺 78。
2. **族数缺口**：按验收带需 foe 60–90 族（现 10，还差 ≥50）、card 100–150 族（现 6，还差 ≥94）、event 92–112 族（现 4，还差 ≥78，即一事件一族补齐）。
3. **交付物 3 缺失**：`docs/art/ART_FAMILIES.md`（族表文档：族名/成员/提示词/为什么算同族）不存在。
4. **登记缺失**：TASK_DONE.md 无 T79 条目（含 T79 要求的「先读文档取到什么」一句）。
5. **多成员族为零**：R1–R6 的复用规则实际未被演练，`check_families.js` 的 A4（共享形态关键词）目前空转。

## 五、补做路径建议（给下一位执行者）

1. **可复用的底稿**：`data/zh_prompts_full.json` 已有全部 461 对象的中文 prompt（359 个族）。逐对象 prompt 语义可用，但**族划分不可沿用**：它按功能/系列归组，11 个族超 3 上限（工具卡 17、协议卡 10、震语卡牌 9、文书 7、潜水者技能/震语族/震语系列各 6、鱼类/火母系列/潜水者攻击各 5、矿道事件 4），且把 4 个事件并成"矿道事件"族，违反 R2/R3/R4 与"一事件一族"。
2. **按形态重新归族**：foe 按"同目/同材质/同功能"（R3），命名/形态差异大必须拆族（R4）；card 按物件形态归（检查单/枪/绳/仪/罐…）；event 严格一事件一族（族 id `evt_<eventId>`）。
3. **逐族英文 prompt** 按 `docs/art/ART_PROMPT_SPEC.md` §三模板（对象段 → 姿态段 → 风格段），每条带 1–2 个异化标记（材料替代/工艺寄生/器官错位）+ 倒吊/红光语块，禁 `a symbol of / abstract embodiment / minimal emblem`。
4. 每改一轮跑 `node tools/check_families.js`，A1–A6 全 PASS（退出码 0）再交付。
5. 交付时补 `docs/art/ART_FAMILIES.md` 并在 TASK_DONE.md 登记 T79。

## 附录：现有 20 族样张清单（data/art_families.json，未改动）

| 族 id | 族名 | 成员 | style | prompt（全文）|
|---|---|---|---|---|
| foe_family_thermophile_mat | 嗜热菌落 | enemy_d1_01 | A | a crusted colony of thermophilic bacteria spreading up a steel conduit, blistering orange-brown crust with pale veins of slime, steam curling off it, droplets beading on the crust, no eyes no limbs — a growth, not an animal |
| foe_family_saprophyte | 腐生菌 | enemy_d1_02 | A | a saprophytic fungus erupting from a small animal carcass, pale stalks and a blackened cap, spores dusting the floor around it, threads rooting into the bone, wet gleam on the cap |
| foe_family_gap_mite | 隙居螨 | enemy_d1_03 | A | a flat many-legged mite wedged in a wall crack, eight jointed legs splayed sideways, hard ridged carapace, mouthparts probing the seam, dust and salt crystals packed around it |
| foe_family_moss_mat | 苔毯（植物性）| enemy_d1_04 | A | a dense carpet of pale moss carpeting a corroded corridor floor, raised lumpy body with no face, tendrils creeping along the pipe joints, one small red bloom at its center |
| foe_family_salt_formation | 盐壳结晶 | enemy_d1_05 | A | a cluster of salt stalactites growing from a pipe wall, faceted crystal needles, mineral crust flaking away, faint red veins inside the crystal, condensation dripping off the tips |
| foe_family_eyeless_eel | 无眼鳗形 | enemy_d2_01 | A | a long eyeless eel coiled in black water, smooth ribbed body, ring of small teeth in a round mouth, pale scarred skin, water weeds twisted around its middle, only the head breaking the surface |
| foe_family_waste_crab | 废料蟹 | enemy_d2_03 | A | a crab-like scavenger carrying a shell built from scrap plates and a broken gauge, uneven claw arms, joints wrapped in cable, rust streaks down its belly, one red glowing instrument still wired to its back |
| foe_family_jumping_spider | 跳蛛 | enemy_d2_04 | A | a heavy jumping spider crouched on wet stone, eight thick hairy legs, two large forward eyes and six small ones, abdomen marked with a pale skull-like pattern, silk anchor line trailing behind it |
| foe_family_cave_amphibian | 洞穴两栖类 | enemy_d2_05 | A | a pale frog-like amphibian half-submerged in shallow seepage water, wet mottled skin, four splayed legs with disc toes, visible gills, one eye half open, low crouched posture |
| foe_family_lungfish | 肺鱼 | enemy_d3_03 | A | a lungfish curled inside a dried mud cocoon at the bottom of an empty pool, thick scaled body, fleshy fin limbs, mouth sealed with mucus, cracks radiating through the dried mud around it |
| card_family_inspection_board | 例检板（检查单+印章）| anm_0004 | A | a worn metal clipboard holding an inspection checklist, a mechanical stamp arm pressed onto the sheet, hanging pencil on a string, oil stains and a chipped corner, object study centered |
| card_family_battery_lamp | 电池/照明 | anm_0003 | A | a heavy salvaged battery pack wired to a cracked work lamp, taped seams, corroded terminals, coiled cable, the lamp glass fogged and one red diode still lit, object study |
| card_family_energy_gun | 能量枪 | dive_0002 | A | a handheld energy rifle heated from within, segmented barrel with red-hot seams, pressure gauge on the grip, scorched gloves resting under it, faint heat shimmer above the muzzle, weapon study |
| card_family_oxygen_rig | 氧气再生器 | dive_0005 | A | a compact oxygen recycler unit with a fresh filter cartridge screwed in, ribbed hoses and brass couplings, condensation on the canister, small red indicator, object study on a scratched bench |
| card_family_tremor_meter | 震频仪 | dive_0025 | A | a pocket tremor meter, round dial with a needle stopped between two ticks, ribbed brass housing, pinned leather strap, faint red mark at the lower scale, object study |
| card_family_noose_rope | 绳 / 活结 | cng_0043 | A | a coil of braided rope tied in a reusable slip noose, frayed end, knots darkened by handling, small red thread wound into one strand, lying on stone |
| evt_event_d3_1 | 穿防护服的遗体 | event_d3_1 | A | a body in an intact protective suit slumped sitting against a rock wall, round glass faceplate with small handwriting on its inner side, dust on the shoulders, an empty corridor behind, scene drawing |
| evt_event_d2_1 | 矿道口的碎石 | event_d2_1 | A | freshly moved rubble blocking a mine entrance, half a glove caught in the stones, drag marks on the ground, a lantern left behind still warm, scene drawing |
| evt_event_d2_2 | 会自己开关的矿灯 | event_d2_2 | A | a single mining lamp hanging by its cable in an empty tunnel, lit even though no one is there, its beam on bare rock, a duty roster nailed nearby with one name scratched out, scene drawing |
| evt_event_d4_2 | 烧过的红蕨 | event_d4_2 | A | a patch of red ferns that burned and grew back, ash clinging to the roots, new fronds pushing up redder than the rest, charred stone underneath, scene drawing |

> 样张质量印象：prompt 均为对象优先、具体名词充足、无禁语，方向可用；但均未包含 ART_PROMPT_SPEC 一之二的「倒吊/红光」必选语块与异化标记，正式成品时应按 §规范补齐。
