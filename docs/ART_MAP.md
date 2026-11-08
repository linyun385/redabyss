# 素材映射表（哪张图被谁用）

> 自动生成：`python tools/gen_art_map.py`。规则以 `web/index.html` 里的 `cardArtId()` / 敌人查表为准，改代码要同步改脚本。

## 一页速查

| 类别 | 图 id 规则 | 数量 |
|---|---|---|
| 卡面 | `face_<生态>_<1..6>`（按卡牌首脉取生态，id 哈希取序号）| 40 |
| 敌人 | `foe_<层对应生态>_<1..3>`（按敌人 layer + id 哈希）| 24 |
| 职业立绘 | `class_<职业id>` | 4 |
| 结局 | `end_ending_<结局id>` | 3 |

## 卡面（face_*）

| 图 id | 生态 | 使用者 | 文件 |
|---|---|---|---|
| `face_eco_arid_1` | eco_arid | 维修凝胶（anm_0012） / 保运行批文（anm_0036） / 忆盐（cng_0010） / 红渊贸易局·净水配给（dive_0036） / 震语：引流（trem_0032） / 震语：淡忘（trem_0041） / 涌喉·潮契（trem_0074） | web/assets/art/face_eco_arid_1.webp |
| `face_eco_arid_2` | eco_arid | 协议：保运行（anm_0022） / 缓冲库存（anm_0031） / 协议：例外条款（anm_0040） / 红渊研究院·水样档案（dive_0037） / 红渊贸易局·苦水配给（双份）（dive_0079） / 涌喉·水契（trem_0033） / 震语：润喉（trem_0051） | web/assets/art/face_eco_arid_2.webp |
| `face_eco_arid_3` | eco_arid | 氧气核算（anm_0029） / 闭环利用（anm_0032） / 保运行优先级（anm_0041） / 母亲的祷文（cng_0012） / 氧气再生器（满压）（dive_0038） / 震语：断流（trem_0034） | web/assets/art/face_eco_arid_3.webp |
| `face_eco_arid_4` | eco_arid | 菌婪者组织样本（anm_0039） / 灰藻汤（cng_0004） / 灰藻供品（cng_0013） / 尝水（深井）（trem_0035） / 五脉符（浮位）（trem_0077） | web/assets/art/face_eco_arid_4.webp |
| `face_eco_arid_5` | eco_arid | 潮汐锁（cng_0023） / 红藻花园（cng_0041） / 疯先知的笔记（cng_0050） / 涌喉·深潜（trem_0063） | web/assets/art/face_eco_arid_5.webp |
| `face_eco_arid_6` | eco_arid | 协议：最小代价原则（anm_0026） / 尝水（trem_0031） | web/assets/art/face_eco_arid_6.webp |
| `face_eco_cold_1` | eco_cold | 协议：优先级翻转（anm_0021） / 星髓矿业·钻杆（dive_0027） / 抗共振司·镇爆弹（dive_0030） / 红渊研究院·共振采样（dive_0045） / 红渊研究院·频谱印章（dive_0078） / 震语：双声（trem_0005） / 听地神脉搏（trem_0014） / 震台石碑（残诵）（trem_0047） | web/assets/art/face_eco_cold_1.webp |
| `face_eco_cold_2` | eco_cold | 震频器（校准）（dive_0028） / 星髓矿业·深部震源（dive_0046） / 震台石碑（拓片）（trem_0006） / 震语：断忆（trem_0042） / 震语：连震（trem_0048） / 历法刻盘（倒页）（trem_0075） | web/assets/art/face_eco_cold_2.webp |
| `face_eco_cold_3` | eco_cold | 运料井下坠（anm_0038） / 通风守卫·代班（anm_0047） / 红渊研究院·震谱仪（dive_0029） / 震频器（并联）（dive_0041） / 深红资源集团·谐振井（dive_0047） / 震语：听骨（trem_0001） / 震语铃（trem_0007） / 震语：三震（trem_0010） / 三震（回声）（trem_0049） / 震语：合鸣（trem_0052） / 震语：数息（trem_0061） / 震语：低语（trem_0070） / 震语：双唱（trem_0076） | web/assets/art/face_eco_cold_3.webp |
| `face_eco_cold_4` | eco_cold | 运输井规程（anm_0048） / 影语（cng_0037） / 墟语（cng_0040） / 震髓探测器（阵列）（dive_0042） / 震频器（微型）（dive_0051） / 听震（trem_0002） / 震语：问地（trem_0008） / 震台石碑（trem_0011） / 震语：五声（trem_0053） / 震台石碑（注视）（trem_0059） / 震语：叩问（trem_0062） / 震语：试井（trem_0071） | web/assets/art/face_eco_cold_4.webp |
| `face_eco_cold_5` | eco_cold | 静默段徵章（anm_0043） / 震喉（cng_0038） / 震频器（dive_0025） / 震髓残响（dive_0067） / 震语：压息（trem_0003） / 震语：断脉（trem_0009） / 历法刻盘（trem_0012） / 震台石碑（新碑）（trem_0069） / 震语：回礼（trem_0072） | web/assets/art/face_eco_cold_5.webp |
| `face_eco_cold_6` | eco_cold | 震髓装药（dive_0026） / 抗共振司·导波索（dive_0044） / 抗共振司·导波索（并联）（dive_0077） / 震语：回响（trem_0004） / 震语：崩齿（trem_0013） / 震语：舍字（trem_0046） / 历法刻盘（补页）（trem_0064） / 震台石碑（无字）（trem_0079） | web/assets/art/face_eco_cold_6.webp |
| `face_eco_nexus_1` | eco_nexus | 谐振的余音（trem_0083） | web/assets/art/face_eco_nexus_1.webp |
| `face_eco_nexus_2` | eco_nexus | 埋骨布（trem_0039） / 五脉符（逆位）（trem_0060） | web/assets/art/face_eco_nexus_2.webp |
| `face_eco_nexus_3` | eco_nexus | 静底·深阅（trem_0058） | web/assets/art/face_eco_nexus_3.webp |
| `face_eco_nexus_4` | eco_nexus | 埋骨布（裹身）（trem_0068） | web/assets/art/face_eco_nexus_4.webp |
| `face_eco_nexus_5` | eco_nexus | 值班交接（trem_0081） | web/assets/art/face_eco_nexus_5.webp |
| `face_eco_nexus_6` | eco_nexus | 五脉符（trem_0040） / 不许关闭（trem_0082） | web/assets/art/face_eco_nexus_6.webp |
| `face_eco_rad_1` | eco_rad | 料仓取件（anm_0009） / 威胁等级·评估员（anm_0018） / 协议：静默段·延长（anm_0027） / 运料车残骸（anm_0030） / 沉默权柄（cng_0025） / 猎巫者的绳（cng_0043） / 岩洞集会（cng_0049） / 墟盐（dive_0018） / 星髓矿业·定向爆破（dive_0021） / 抗共振司·静音瓦（dive_0063） / 星髓矿业·二号钻台（dive_0072） / 相石·满录（trem_0038） | web/assets/art/face_eco_rad_1.webp |
| `face_eco_rad_2` | eco_rad | 例检条款（anm_0004） / 料径校准（anm_0013） / 例检手套（anm_0019） / 协议：注销（anm_0028） / 动用储备（anm_0037） / 例检清单（残）（anm_0046） / 王国账簿（cng_0002） / 猎巫者的谎（cng_0011） / 城墙梦（cng_0020） / 硬矿钻（dive_0013） / 抗共振司·锚桩（dive_0019） / 硬矿钻（重型）（dive_0022） / 星髓矿业·矿脉图（dive_0064） / 抗共振司·白噪机（dive_0073） / 相石·对视（trem_0057） | web/assets/art/face_eco_rad_2.webp |
| `face_eco_rad_3` | eco_rad | 巡逻体残骸（anm_0014） / 巨神的欠条（cng_0003） / 巨神的凝视（cng_0018） / 巨神的欠账（cng_0021） / 晨昏带地图（cng_0045） / 震髓探测器（dive_0014） / 抗共振司·静默规程（dive_0023） / 死亡合同（增补条款）（dive_0056） / 黑曜采掘·计件工资（dive_0074） / 五脉符（缺位）（trem_0067） | web/assets/art/face_eco_rad_3.webp |
| `face_eco_rad_4` | eco_rad | 库存盘点（anm_0006） / 主控授权·工程线（anm_0015） / 协议：库存封存（anm_0024） / 王权梦（cng_0019） / 卫星轨道（cng_0022） / 星髓矿业·爆破执照（dive_0015） / 深红资源集团·钻探平台（dive_0024） / 黑曜采掘·无氧班次（dive_0060） / 深红资源集团·地契（dive_0075） / 相石·封忆（trem_0044） | web/assets/art/face_eco_rad_4.webp |
| `face_eco_rad_5` | eco_rad | 现场回收（anm_0001） / 调节螺栓（anm_0007） / 主控授权·安全线（anm_0016） / 协议：终端确认（anm_0025） / 共振抑制仪（dive_0016） / 硬矿钻（手持）（dive_0049） / 回收员的账本（dive_0070） / 辨矿（trem_0036） | web/assets/art/face_eco_rad_5.webp |
| `face_eco_rad_6` | eco_rad | 扳手规程（anm_0002） / 报废清单（anm_0008） / 回收协议·总则（anm_0017） / 协议：静默段（anm_0020） / 死者的工号牌（anm_0044） / 暗盘俯瞰（cng_0024） / 猎巫巡逻·换防（cng_0048） / 星髓矿业·深地车（dive_0017） / 黑曜采掘·加班条例（dive_0020） / 凿屑袋（dive_0062） / 相石·初刻（trem_0037） | web/assets/art/face_eco_rad_6.webp |
| `face_eco_sea_1` | eco_sea | 备用照明电池（anm_0003） / 读图纸的人（anm_0045） / 守夜（cng_0001） / 星表检索（cng_0007） / 火母历第一页（cng_0016） / 曜元（dive_0003） / 聚能枪（双管）（dive_0009） / 轨道炮支援（dive_0012） / 聚能枪（超载）（dive_0054） / 聚能枪（三管）（dive_0069） / 观红（深相）（trem_0029） / 震语：回望（trem_0056） | web/assets/art/face_eco_sea_1.webp |
| `face_eco_sea_2` | eco_sea | 历法之争（cng_0008） / 地下学院讲义（cng_0017） / 光父的钟摆（cng_0026） / 三体历残卷（cng_0044） / 光苔矿培植舱（dive_0004） / 辐射弹（裸装）（dive_0055） / 震语：回声定位（trem_0066） | web/assets/art/face_eco_sea_2.webp |
| `face_eco_sea_3` | eco_sea | 协议：信息隔离（anm_0023） / 主控密钥（烧毁）（anm_0050） / 光父的准点（cng_0009） / 红矮星风（cng_0027） / 星光残照（cng_0030） / 氧气再生器（dive_0005） / 氧气再生器（便携）（dive_0050） / 渊光重工·接地缆（dive_0065） / 观红（trem_0025） | web/assets/art/face_eco_sea_3.webp |
| `face_eco_sea_4` | eco_sea | 血统册摘录（anm_0033） / 基因修复台（anm_0042） / 五十日（cng_0028） / 光父的审判（cng_0031） / 渊光重工·工作灯（dive_0006） / 曜元（高浓）（dive_0066） / 光导石（trem_0026） | web/assets/art/face_eco_sea_4.webp |
| `face_eco_sea_5` | eco_sea | 应急照明协议（anm_0010） / 辐射防护衬层（anm_0034） / 撤销程序残片（anm_0049） / 巡夜灯（cng_0005） / 伊格的方向（cng_0014） / 准时的心跳（cng_0032） / 不醒者的名单（cng_0047） / 光导透镜（残）（dive_0001） / 渊光重工·导光索（dive_0007） / 聚变鱼雷（dive_0010） / 曜元（共振型）（dive_0043） / 光苔矿（盆栽）（dive_0052） / 巡线灯（dive_0061） / 震语：明目（trem_0027） / 震语：照骨（trem_0030） / 光导石（串珠）（trem_0054） / 观红（对影）（trem_0078） | web/assets/art/face_eco_sea_5.webp |
| `face_eco_sea_6` | eco_sea | 守夜人的表（cng_0006） / 守望席（cng_0015） / 昴宿低语（cng_0033） / 光导（cng_0039） / 聚能枪（dive_0002） / 红渊研究院·数据回传（dive_0008） / 辐射弹（dive_0011） / 渊光重工·备用电源（dive_0053） / 渊光重工·灯序表（dive_0071） / 渊光重工·断路闸（dive_0080） / 涌喉·光池倒影（trem_0028） / 震语：直视（trem_0055） | web/assets/art/face_eco_sea_6.webp |
| `face_eco_surface_1` | eco_surface | 气闸的规程（dive_0081） | web/assets/art/face_eco_surface_1.webp |
| `face_eco_surface_2` | eco_surface | 重力训练舱（dive_0040） / 按规程应答（dive_0082） | web/assets/art/face_eco_surface_2.webp |
| `face_eco_surface_3` | eco_surface | 坠轨的清单（dive_0083） | web/assets/art/face_eco_surface_3.webp |
| `face_eco_surface_4` | eco_surface | 矿票（dive_0039） / 矿票（回收藏）（dive_0048） / 重力训练舱（极限负重）（dive_0057） | web/assets/art/face_eco_surface_4.webp |
| `face_eco_vent_1` | eco_vent | 火母的怀抱（cng_0034） / 震语：沸息（trem_0023） / 震语：传温（trem_0050） / 静底·灰烬（trem_0065） | web/assets/art/face_eco_vent_1.webp |
| `face_eco_vent_2` | eco_vent | 伊格的痛苦（cng_0035） / 聚能枪（过热）（dive_0031） / 触温（trem_0015） / 震语：熔名（trem_0024） | web/assets/art/face_eco_vent_2.webp |
| `face_eco_vent_3` | eco_vent | 焊缝补强（anm_0005） / 归乡（cng_0036） / 曜元（缓释）（dive_0032） / 喷息·热池边（trem_0016） / 静底·焚忆（trem_0043） | web/assets/art/face_eco_vent_3.webp |
| `face_eco_vent_4` | eco_vent | 火母的小像（cng_0046） / 圣火武器（dive_0033） / 震语：焚名（trem_0017） / 静日触杖（trem_0020） / 震语：长夜（trem_0080） | web/assets/art/face_eco_vent_4.webp |
| `face_eco_vent_5` | eco_vent | 耀斑记忆（cng_0029） / 反走私局·焚烧记录（dive_0034） / 圣火武器（殉爆）（dive_0058） / 曜元（夜班型）（dive_0076） / 静日（trem_0018） / 埋骨礼（trem_0021） / 埋骨礼（合葬）（trem_0045） | web/assets/art/face_eco_vent_5.webp |
| `face_eco_vent_6` | eco_vent | 焊接臂·民用型（anm_0011） / 超频保养（anm_0035） / 火母的回应（cng_0042） / 深红资源集团·地热井口（dive_0035） / 曜元（空腹）（dive_0059） / 深红资源集团·冷却协议（dive_0068） / 禁声日（trem_0019） / 回归墟骨（trem_0022） / 静底·翻灰（trem_0073） | web/assets/art/face_eco_vent_6.webp |

## 敌人（foe_*）

| 图 id | 生态 | 使用者 | 文件 |
|---|---|---|---|
| `foe_eco_arid_1` | eco_arid | 钻孔贝（enemy_d3_02） / 气腔洞鼹兽（enemy_d3_05） / 滴水的账房（enemy_d3_08） / 抢路的干壳（enemy_d3_e3） / 运料车（失控）（anmenemy_10） / 修复体·终末型（anmenemy_13） / 三号避难所自动防御主控（anmenemy_16） / 自己的镜像（cngenemy_11） / 光导残光（cngenemy_14） | web/assets/art/foe_eco_arid_1.webp |
| `foe_eco_arid_2` | eco_arid | 干旱肺鱼（enemy_d3_03） / 硬壳蜗（enemy_d3_06） / 钻孔贝群（enemy_d3_e1） / 旱脉的封口者（enemy_d3_b1） / 隐生的缓步（enemy_d3_09） / 通风守卫（anmenemy_11） / 哨戒网中枢（anmenemy_14） / 影语投影（cngenemy_12） / 墟语残章（cngenemy_15） | web/assets/art/foe_eco_arid_2.webp |
| `foe_eco_arid_3` | eco_arid | 硬矿洞蛇（enemy_d3_01） / 盲蛛（enemy_d3_04） / 空腔蝠（enemy_d3_07） / 旱螈伏兵（enemy_d3_e2） / 泉权的丈量者（enemy_d3_b2） / 维护单元-12（叛变）（anmenemy_12） / 菌婪母巢（anmenemy_15） / 震喉回声（cngenemy_13） / 不醒者·初代疯先知（cngenemy_16） | web/assets/art/foe_eco_arid_3.webp |
| `foe_eco_cold_1` | eco_cold | 墟蟹（enemy_d2_03） / 沉屑鱼（enemy_d2_06） / 历虫（enemy_d2_e1） / 历壁的守读者（enemy_d2_b1） / 历壁的蛀痕（enemy_d2_09） / 巡逻体-3（anmenemy_07） / 猎巫巡逻队（cngenemy_05） / 热泉梦泡（cngenemy_08） | web/assets/art/foe_eco_cold_1.webp |
| `foe_eco_cold_2` | eco_cold | 冷洞食腐鳗（enemy_d2_01） / 休眠两栖类（enemy_d2_04） / 冷洞跳蛛（enemy_d2_07） / 菌膜织者（enemy_d2_e2） / 历的补写者（enemy_d2_b2） / 扫探虫群（anmenemy_05） / 隔离门（anmenemy_08） / 饥荒影（cngenemy_06） / 水脉回声（cngenemy_09） | web/assets/art/foe_eco_cold_2.webp |
| `foe_eco_cold_3` | eco_cold | 冷洞青菌（enemy_d2_02） / 噬骨菌群（enemy_d2_05） / 沉雪的苔背（enemy_d2_08） / 冷眠的守历者（enemy_d2_e3） / 焊接臂·军用型（anmenemy_06） / 菌婪者（anmenemy_09） / 红蕨幻影（cngenemy_07） / 巨怪投影（cngenemy_10） | web/assets/art/foe_eco_cold_3.webp |
| `foe_eco_core_1` | eco_core | 旧光者残影（enemy_d7_01） / 孢子群（enemy_d7_04） / 无面记录员（enemy_d7_07） / 震台祭司（enemy_d7_e2） / 慢半拍的影（enemy_d7_10） | web/assets/art/foe_eco_core_1.webp |
| `foe_eco_core_2` | eco_core | 光柱蛇蜥（enemy_d7_02） / 震语苔丛（enemy_d7_05） / 静默歌者（enemy_d7_08） / 超临界的水囊（enemy_d7_e3） | web/assets/art/foe_eco_core_2.webp |
| `foe_eco_core_3` | eco_core | 震杆菌（enemy_d7_03） / 穹顶之影（enemy_d7_06） / 烧手的灰烬（enemy_d7_e1） / 穹顶之影·网颤（enemy_d7_b1） / 三色菌毯的须（enemy_d7_09） | web/assets/art/foe_eco_core_3.webp |
| `foe_eco_nexus_1` | eco_nexus | 空壳旧光者（enemy_d8_03） / 墟腔（enemy_d8_06） / 循环的巡逻体（enemy_d8_e1） / 墟蛹·未完成（enemy_d8_b1） / 谐振的余音（enemy_d8_09） / 走廊尽头的白噪音（enemy_d8_12） | web/assets/art/foe_eco_nexus_1.webp |
| `foe_eco_nexus_2` | eco_nexus | 墟蛹（enemy_d8_01） / 茧丝虫（enemy_d8_04） / 墟影残片·重奏（enemy_d8_e2） / 八万年前的班表（enemy_d8_07） / 不许关闭的告示（enemy_d8_10） | web/assets/art/foe_eco_nexus_2.webp |
| `foe_eco_nexus_3` | eco_nexus | 墟尘行像（enemy_d8_02） / 墟影残片（enemy_d8_05） / 签到簿的笔（enemy_d8_08） / 检修窗后的手（enemy_d8_11） | web/assets/art/foe_eco_nexus_3.webp |
| `foe_eco_rad_1` | eco_rad | 抗辐射甲壳类（enemy_d6_02） / 辐射金属鳞鳄王（enemy_d6_05） / 重鳞的拾壳者（enemy_d6_08） / 铅鳞的收藏家（enemy_d6_e3） | web/assets/art/foe_eco_rad_1.webp |
| `foe_eco_rad_2` | eco_rad | 辐射金属鳞鳄（enemy_d6_03） / 铅皮蛞蝓（enemy_d6_06） / 辐射休眠孢子群（enemy_d6_e1） / 辐射金属鳞鳄王·蜕（enemy_d6_b1） / 低烧的菌群（enemy_d6_09） | web/assets/art/foe_eco_rad_2.webp |
| `foe_eco_rad_3` | eco_rad | 辐射合成菌（enemy_d6_01） / 锈蚀菌（enemy_d6_04） / 辐射藻垫（enemy_d6_07） / 金属鳞鳄幼体（enemy_d6_e2） / 地神骨灰坛的看守（enemy_d6_b2） | web/assets/art/foe_eco_rad_3.webp |
| `foe_eco_sea_1` | eco_sea | 红腔鱼（enemy_d4_01） / 光池银鱼（enemy_d4_04） / 浮光水母（enemy_d4_07） / 红腔鱼·巡游种（enemy_d4_e2） / 滤食的须群（enemy_d4_10） | web/assets/art/foe_eco_sea_1.webp |
| `foe_eco_sea_2` | eco_sea | 滤食鱼群（enemy_d4_02） / 盲眼红腔鱼（enemy_d4_05） / 光藓蠕虫（enemy_d4_08） / 红腔鱼的伏击手（enemy_d4_e3） | web/assets/art/foe_eco_sea_2.webp |
| `foe_eco_sea_3` | eco_sea | 垂光蕨（enemy_d4_03） / 光蛭母（enemy_d4_06） / 藻毯伏击者（enemy_d4_e1） / 光蛭母·逆流（enemy_d4_b1） / 藻毯的影子（enemy_d4_09） | web/assets/art/foe_eco_sea_3.webp |
| `foe_eco_surface_1` | eco_surface | 嗜热古菌（enemy_d1_01） / 管廊苔毯（enemy_d1_04） / 孢子清道夫（enemy_d1_e2） / 晒裂的软管（enemy_d1_07） / 静默号·最后一次广播（enemy_d1_b2） / 维护单元-7（anmenemy_01） / 警报器（旧式）（anmenemy_04） / 岩洞猎手（cngenemy_02） | web/assets/art/foe_eco_surface_1.webp |
| `foe_eco_surface_2` | eco_surface | 腐生菌（enemy_d1_02） / 管壁钟乳盐（enemy_d1_05） / 记名的旗（enemy_d1_08） / 气闸的守夜者（enemy_d1_e3） / 哨戒塔（旧式）（anmenemy_02） / 盐虫群（cngenemy_03） | web/assets/art/foe_eco_surface_2.webp |
| `foe_eco_surface_3` | eco_surface | 隙居螨（enemy_d1_03） / 盐壳拾荒者（enemy_d1_e1） / 钟乳盐·塌落体（enemy_d1_b1） / 空服的壳（enemy_d1_06） / 坠轨的投影（enemy_d1_e4） / 清障机·残（anmenemy_03） / 浅海鳗（cngenemy_01） / 灰藻采集者（cngenemy_04） | web/assets/art/foe_eco_surface_3.webp |
| `foe_eco_vent_1` | eco_vent | 硫塔菌（enemy_d5_03） / 震喉（enemy_d5_06） / 喷息守卫（enemy_d5_e1） / 震喉·空腔独奏（enemy_d5_b1） / 硫菌丘的看火者（enemy_d5_09） | web/assets/art/foe_eco_vent_1.webp |
| `foe_eco_vent_2` | eco_vent | 热泉管虫（enemy_d5_01） / 震鸣蟾（enemy_d5_04） / 沸泥鳗（enemy_d5_07） / 硫沫赘生体（enemy_d5_e2） / 喷发期的管虫（enemy_d5_10） | web/assets/art/foe_eco_vent_2.webp |
| `foe_eco_vent_3` | eco_vent | 热泉螈（enemy_d5_02） / 铁细菌膜母体（enemy_d5_05） / 硫雾囊菌（enemy_d5_08） / 热议会的执汤者（enemy_d5_e3） | web/assets/art/foe_eco_vent_3.webp |

## 职业立绘（class_*）

| 图 id | 生态 | 使用者 | 文件 |
|---|---|---|---|
| `class_anmin` | - | 维护者 | web/assets/art/class_anmin.webp |
| `class_cangmin` | - | 疯先知 | web/assets/art/class_cangmin.webp |
| `class_diver` | - | 下潜者 | web/assets/art/class_diver.webp |
| `class_tremor` | - | 震语者 | web/assets/art/class_tremor.webp |

## 结局（end_*）

| 图 id | 生态 | 使用者 | 文件 |
|---|---|---|---|
| `end_ending_averted` | - | ending_averted | web/assets/art/end_ending_averted.webp |
| `end_ending_walked` | - | ending_walked | web/assets/art/end_ending_walked.webp |
| `end_ending_watched` | - | ending_watched | web/assets/art/end_ending_watched.webp |
