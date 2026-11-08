# -*- coding: utf-8 -*-
"""T46：追加 24 个事件（每层 3 个）与 16 个遗物（每层 2 个）。一次性脚本。"""
import json, io, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

EV = [
# D1 地表死寂区
{"id":"event_d1_1","layer":1,"title":"降落的旧舱","body":"登陆基地外围有一只废弃的返回舱，舱门半开，气闸的灯还亮着一格。八百年了，那一格没灭。","options":[
 {"text":"钻进去翻物资。","veins":["mineral"],"result":{"gold":45,"damage":3},"result_text":"舱里的储物箱码得很整齐，翻到最后一样的时候，割破的手套在真空边缘渗出血珠。血珠是圆的，滚走了。"},
 {"text":"把氧气罐留给下一个人。","veins":["water"],"result":{"heal":10},"result_text":"舱里的人早就走了，走之前把水壶挂在门边。壶是满的。你替他把壶又挂正了一点。"},
 {"text":"走开。","veins":[],"result":{},"result_text":"舱皮在热胀冷缩，一声一声，像有人在敲。这里没有风，你把这件事记成了风。"}]},
{"id":"event_d1_2","layer":1,"title":"帝星的影子","body":"站在裂隙边能看到帝星，很小，很亮。这里没有大气，它的光不散，是一根细线，直直扎进石头缝里。","options":[
 {"text":"对着光站一会儿。","veins":["light"],"result":{"gaze":1,"heal":5},"result_text":"帝星不管这里。看它一会儿，是为了记得上面还有别的东西。"},
 {"text":"顺着裂隙往下听。","veins":["tremor"],"result":{"card_reward":"common"},"result_text":"裂隙把地底的震动送上来一丝。你听懂了半句：更深的地方，有东西活着。"},
 {"text":"盖上石板。","veins":[],"result":{},"result_text":"光被关在外面。这种黑和闭上眼不一样——闭上眼是自己愿意的。"}]},
{"id":"event_d1_3","layer":1,"title":"休眠的孢子","body":"陨击坑的阴影里积着一层粉末，是耐辐射的休眠孢子。它们在等一个不是这里的地方，等了几万年。","options":[
 {"text":"带一撮下去。","veins":["mineral"],"result":{"card_reward":"uncommon"},"result_text":"你把孢子扫进空罐。它们不响也不动。带它们下去的人很多，带它们活着下去的人很少。"},
 {"text":"绕开，别踩。","veins":[],"result":{"heal":6},"result_text":"有些等待与你无关。你把脚印收轻了。"},
 {"text":"用靴子碾过去。","veins":["heat"],"result":{"gold":30,"damage":6},"result_text":"粉末溅起来又落下，一点声音也没有。靴底缝里嵌进一点发亮的东西，抠不出来。"}]},
# D2 外层冷洞
{"id":"event_d2_1","layer":2,"title":"刻在岩壁上的历","body":"一面岩壁刻满细密的刻痕，深浅不一，最老的那些被菌膜盖住一半。是记忆者的历，记到上一次大塌为止。","options":[
 {"text":"把最新的一道补上。","veins":["tremor"],"result":{"card_reward":"uncommon"},"result_text":"你不知道今天算什么日子，就照着手感刻了一道。刻完才发现岩壁是温的。"},
 {"text":"抄下最老的一段。","veins":["mineral"],"result":{"gold":25,"gaze":1},"result_text":"有几段刻痕的意思已经没人认得。抄下来的东西也许值钱，也许只是重。"},
 {"text":"什么都不刻。","veins":[],"result":{},"result_text":"历不缺你这一道。你把手收回来，掌心里留着一点别人的旧震动。"}]},
{"id":"event_d2_2","layer":2,"title":"不动的邻居","body":"湿岩缝里伏着一只休眠的两栖类，皮皱得像干了的水囊。它可以几年不吃不动。你路过三回，它都在。","options":[
 {"text":"贴着它的呼吸走。","veins":["water"],"result":{"heal":8},"result_text":"它呼吸很慢，慢得能对上你的步子。走完这段路，你的喘也匀了。"},
 {"text":"把碎屑分它一点。","veins":["heat"],"result":{"card_reward":"common"},"result_text":"它不吃。碎屑沉进缝里，喂了别的小东西。这一段路的灯光亮了一些。"},
 {"text":"别吵醒它。","veins":[],"result":{},"result_text":"有些安静是借来的。你把借来的原样放回。"}]},
{"id":"event_d2_3","layer":2,"title":"沉下来的东西","body":"冷洞的吃食全靠上面沉降。碎屑落了八万年，铺出一层软的。软层里露出一角金属，不是矿。","options":[
 {"text":"挖出来看看。","veins":["mineral"],"result":{"relic":True},"result_text":"旧光者的东西，落了八万年也没锈完。它比你更早到这里。"},
 {"text":"别碰，让软层盖回去。","veins":[],"result":{"heal":6},"result_text":"你把软层按回去。这层里埋的东西，睡得比你好。"},
 {"text":"循着碎屑往上找源头。","veins":["light"],"result":{"gold":40},"result_text":"碎屑的来路也是你往下要走的去路。一路上捡到几样还能用的。"}]},
# D3 干旱空洞区
{"id":"event_d3_1","layer":3,"title":"泉眼的水囊","body":"泉眼里悬着一个水囊，两栖类在里面繁殖。水在这里是按滴记的，一滴一滴，记了不知多少年。","options":[
 {"text":"只取一口。","veins":["water"],"result":{"heal":10},"result_text":"你按规矩取了一口。水囊晃了晃，又满了。这里的规矩是够用就好。"},
 {"text":"把随身的空罐灌满。","veins":["mineral"],"result":{"gold":35,"gaze":1},"result_text":"你多拿了。回声在空洞里传得很远，不知道谁听见了。"},
 {"text":"给水囊让路。","veins":[],"result":{},"result_text":"你从别的缝绕过去。石头记不住人，水记得。"}]},
{"id":"event_d3_2","layer":3,"title":"干死的通道","body":"一条水道干了几十年，河床上的贝类还张着壳。有人的行李摊在河床中间，人不在。","options":[
 {"text":"翻翻行李。","veins":["mineral"],"result":{"gold":30,"damage":4},"result_text":"行李里有干粮和票子。翻到一半，头顶落了些灰，落得很匀，像下了一场不着急的雪。"},
 {"text":"沿着河床找痕迹。","veins":["tremor"],"result":{"card_reward":"uncommon"},"result_text":"走的人往深处去了，脚步很稳。你顺着那条路走了一段，路比刚才好走。"},
 {"text":"把行李摆整齐。","veins":[],"result":{"heal":5},"result_text":"你把摊开的东西收拢摆好。谁的东西谁认得，摆整齐了认起来快。"}]},
{"id":"event_d3_3","layer":3,"title":"硬矿石上的牙印","body":"硬矿石表面有一排牙印，深得能放进手指。钻孔贝干的，钻了几代。最深的牙印里嵌着一点发亮的矿屑。","options":[
 {"text":"抠出矿屑。","veins":["mineral"],"result":{"gold":45},"result_text":"矿屑是好东西。贝钻了三代才攒下的，你一次拿完了。"},
 {"text":"学着它的路线找缝。","veins":["tremor"],"result":{"card_reward":"common"},"result_text":"牙印是路标。顺着最深的那个，你找到一条缝，缝里有风，风是活的。"},
 {"text":"在牙印旁边刻个记号。","veins":[],"result":{},"result_text":"你刻了一道短的。后来的东西看得懂就看，看不懂，就当石头长了个疤。"}]},
# D4 稳定空洞海
{"id":"event_d4_1","layer":4,"title":"涌喉的市集","body":"巢城的市集开在水线上方，客议会说话算数。摊位挂着各家的灯，渊民和上面来的东西摆在同一个架子上。","options":[
 {"text":"用矿票换干红蕨。","veins":["water"],"result":{"heal":12},"result_text":"摊主按客议会的价收的钱，没抬价。涌喉的规矩是市集里不问来路。"},
 {"text":"打听往深处的路。","veins":["tremor"],"result":{"card_reward":"uncommon"},"result_text":"一个客语者给你画了半张图。剩下半张他说：下面的路，图不如腿。"},
 {"text":"只看不买。","veins":[],"result":{},"result_text":"你逛完了没买。摊主也不恼，把灯往你这边挪了挪，算是照明。"}]},
{"id":"event_d4_2","layer":4,"title":"倒挂林的暗处","body":"红蕨林从洞顶垂下来，深红紫黑金红。林子深处的红光被叶子滤成暗的。暗处有个很大的形状，随热对流慢慢漂。","options":[
 {"text":"退回光里。","veins":["light"],"result":{"heal":6},"result_text":"你退回亮处。那形状没跟来。它漂它的，你走你的。"},
 {"text":"趁它没注意穿过林子。","veins":["tremor"],"result":{"card_reward":"rare","damage":8},"result_text":"你从林子里过去了，带了点东西出来。林子在你身后合拢，像水合拢。"},
 {"text":"对着它站定。","veins":[],"result":{"gaze":2,"damage":5},"result_text":"它把你记了一下。被记过的地方现在有点凉。"}]},
{"id":"event_d4_3","layer":4,"title":"旧城的街灯","body":"水下的旧城市残骸，街灯还立着。稳定空洞海的废墟保存完好——结构层替它们挡了八万年。","options":[
 {"text":"拆一盏灯。","veins":["mineral"],"result":{"gold":50,"damage":5},"result_text":"灯座拆下来的时候，整条街的灯闪了一下。只闪了一下。也可能是错觉。"},
 {"text":"数一数有几盏还亮。","veins":["light"],"result":{"card_reward":"uncommon"},"result_text":"三十七盏。你数了两遍。这种事没人会知道，除了你数过的那条街。"},
 {"text":"在灯下坐一会儿。","veins":[],"result":{"heal":8},"result_text":"灯下的位置比别处暖。八万年没人的地方，暖是从石头里渗出来的。"}]},
# D5 热泉裂带
{"id":"event_d5_1","layer":5,"title":"喷息的汤","body":"绿洲城邦的汤锅架在温泉支流上，汤是菌和管虫尖熬的。喷议会的中立挂在门口：卖汤，不卖立场。","options":[
 {"text":"喝一碗。","veins":["water"],"result":{"heal":14},"result_text":"汤很烫，辣得很实在。碗底沉着几粒盐——墟盐，融在红光里才算数。"},
 {"text":"问最近喷发的日子。","veins":["heat"],"result":{"card_reward":"uncommon"},"result_text":"热议会的历上写着：大喷在两个喷之后。你把日子记在手背上。"},
 {"text":"白喝一碗就走。","veins":[],"result":{"damage":6},"result_text":"锅边守卫的棍子比语言快。中立不等于没脾气。"}]},
{"id":"event_d5_2","layer":5,"title":"硫菌丘之间","body":"黑色菌丘一座一座立在裂缝边，像塔群。最近的一座在冒新芽——它要长高了，长高就挡光。","options":[
 {"text":"掐掉新芽。","veins":["heat"],"result":{"gold":40,"damage":4},"result_text":"菌芽的汁液是硬通货。断口喷了你一手硫沫，火辣辣的。"},
 {"text":"给它量个高。","veins":["light"],"result":{"card_reward":"common"},"result_text":"你用步子量了量，记在心里。这块地方的高度表，比你先知道地震。"},
 {"text":"从丘群中间穿过去。","veins":["tremor"],"result":{"gold":20},"result_text":"丘群之间的风道是现成的路。你走过去，什么都没发生。什么都没发生就是好事。"}]},
{"id":"event_d5_3","layer":5,"title":"冷却池边的卵","body":"冷却池边粘着一排卵，靠余温孵化。一次地震就能让这池水凉掉。凉掉的那天，这排卵就到日子了。","options":[
 {"text":"守到它们出膜。","veins":["water"],"result":{"heal":12},"result_text":"你守了半场。出膜的幼体往水里游，有一只回头看了你一眼。也许没有。"},
 {"text":"捡两颗揣走。","veins":["mineral"],"result":{"gold":35,"gaze":1},"result_text":"卵在怀里是温的，卖到有炉子的地方是好价钱。身后有东西在看你，看了一会儿，走了。"},
 {"text":"绕开这池水。","veins":[],"result":{},"result_text":"你的脚印没往池边去。这一趟你什么都没带，也什么都没欠。"}]},
# D6 辐射矿石区
{"id":"event_d6_1","layer":6,"title":"挂着骨头的警示","body":"矿区入口的岩架上挂着一串骨头，间隔摆得很匀。是人的骨头。摆骨头的人想让你数清楚再进去。","options":[
 {"text":"数清楚再进去。","veins":["light"],"result":{"card_reward":"uncommon"},"result_text":"二十六根。你进去的路程比摆骨头的人短，收获也比他短。"},
 {"text":"不进去，沿边缘收矿。","veins":["mineral"],"result":{"gold":50,"damage":6},"result_text":"边缘的辐射矿成色够。皮肤开始发痒的时候你收手了。"},
 {"text":"把骨头放下来，埋了。","veins":[],"result":{"gaze":1},"result_text":"你把骨头收拢理好，埋了。做这件事的时候红光很亮。有人看着你做了这件事。"}]},
{"id":"event_d6_2","layer":6,"title":"抗辐射的壳","body":"一只重金属鳞的甲壳类死在矿缝里，壳还完整。这身壳是它活命的本钱。现在是谁的本钱，就是谁的。","options":[
 {"text":"剥壳做护具。","veins":["mineral"],"result":{"damage":6,"card_reward":"uncommon"},"result_text":"壳割手。做出来的东西糙，但管用。"},
 {"text":"把壳留给更小的东西。","veins":[],"result":{"heal":8},"result_text":"缝里钻出来一只小的，住进了壳里。你看着它住进去的。这里连庇护都是接力。"},
 {"text":"整只搬走卖。","veins":["heat"],"result":{"gold":55},"result_text":"生物科技公司收这个，按克算。你没问它拿来做什么。"}]},
{"id":"event_d6_3","layer":6,"title":"反应堆的余温","body":"旧反应堆的外壳上还有温度。上面的人两百年前建的东西，渊民叫它地神的骨灰坛。仪表都死了，风从管子里过，呜呜的。","options":[
 {"text":"拆一块屏蔽板。","veins":["mineral"],"result":{"gold":60,"damage":8},"result_text":"屏蔽板是好料。拆的时候你在管子的呜呜声里听见一个词，不像震语，也不像上面的话。"},
 {"text":"把歪掉的仪表拨正。","veins":["light"],"result":{"heal":8,"gaze":1},"result_text":"仪表亮了一下，又灭了。灭之前那一瞬间的绿光，你记到现在。"},
 {"text":"原样离开。","veins":[],"result":{},"result_text":"有些东西不缺你这一动。你退出去了，门没关，风继续呜呜。"}]},
# D7 核心高热区
{"id":"event_d7_1","layer":7,"title":"祭祀台的灰","body":"震语者的祭祀台在热液边缘，台上积着灰，灰是烧完的历书。是敬意还是恐惧烧的，台上分不出来。","options":[
 {"text":"照着残灰续一炷。","veins":["heat"],"result":{"heal":10,"gaze":1},"result_text":"你把手边能烧的都烧了。灰落下去的地方，热液亮了一下。"},
 {"text":"把台上的灰扫走。","veins":["mineral"],"result":{"gold":45},"result_text":"灰里烧剩的东西不少。扫灰的人没回来收，你来收了。"},
 {"text":"背对祭台坐一会儿。","veins":[],"result":{"heal":6},"result_text":"你坐了会儿。背对着它，反而听得清它的动静。像很大的东西在很慢地呼吸。"}]},
{"id":"event_d7_2","layer":7,"title":"钻探队的末端","body":"深层钻探队的管子伸到这里就停了。设备烂在原地，管口朝着核心的方向。停机原因的记录屏早就读不出来了。","options":[
 {"text":"拆管口的合金。","veins":["mineral"],"result":{"gold":65,"damage":5},"result_text":"合金是这趟最值钱的东西。拆的时候管子里掉出来一副手套，手骨还在里面，姿势是朝着外爬的。"},
 {"text":"读记录屏的残句。","veins":["tremor"],"result":{"card_reward":"rare"},"result_text":"只读得出半句：不要回。后面的字被热液洗掉了。你把这句也带上了。"},
 {"text":"把管口封死。","veins":["heat"],"result":{"gaze":1},"result_text":"你用随身的料把管口封了。封完之后这里安静了些。安静得像有什么换了个地方继续。"}]},
{"id":"event_d7_3","layer":7,"title":"墟蛹的外壳","body":"废墟深处立着一只墟蛹，金属管道和骨骼把它缠成茧。茧里的红光是脉动的，慢，但是有节奏。它在重新运行一套八万年前的程序。","options":[
 {"text":"贴着外壳听。","veins":["tremor"],"result":{"gaze":2,"damage":6},"result_text":"你听见了排好的、成句的震动。它们穿过你的手往骨头里去。你抽手抽得够快，没有全留下。"},
 {"text":"贴着最远的墙根绕过去。","veins":["light"],"result":{"heal":8},"result_text":"墟蛹不追东西。它只是在那里算，算你经过了。"},
 {"text":"拿石头敲一下外壳。","veins":[],"result":{"damage":8,"card_reward":"uncommon"},"result_text":"茧里的节奏停了一拍，又继续。停的那一拍里，你手边多了样东西——从茧上剥落的。你不想知道它为什么剥落。"}]},
# D8 红渊核心
{"id":"event_d8_1","layer":8,"title":"还在运转的走廊","body":"核心的走廊有灯。八万年了，灯还亮着，自动化的东西还在按旧光者的作息运行。门在你面前开，像你回来迟了。","options":[
 {"text":"走进去。","veins":["light"],"result":{"card_reward":"rare","damage":5},"result_text":"门里的一切都在等一个不会回来的人。你路过的时候，有东西把你的步数记进了某个八万年没人翻的账本。"},
 {"text":"在窗台上留一样自己的东西。","veins":[],"result":{"heal":8,"gaze":1},"result_text":"你放下一件小东西。它被扫了一遍，没有被清掉。这里总算有一样不是旧光者的东西了。"},
 {"text":"抄近路穿过去。","veins":["tremor"],"result":{"gold":55},"result_text":"你没走该走的道。账本没记你，角落里被遗漏的东西归了你。"}]},
{"id":"event_d8_2","layer":8,"title":"不许关闭的告示","body":"谐振器外围的墙上刻着一行旧光者的字，下面有人用震语刻了翻译。翻译是：不要试图关闭它。不要试图控制它。它已经是你们的一部分了。","options":[
 {"text":"把这句抄下来。","veins":["tremor"],"result":{"card_reward":"uncommon"},"result_text":"你抄了。抄完发现手是自己动的。这句话不该由手记，该由骨头记。"},
 {"text":"往墙上补一句。","veins":["light"],"result":{"gaze":2},"result_text":"你在下面刻了自己的话：我看到了。刻完四周的灯亮了一瞬，像是有人回了一句：看到了。"},
 {"text":"绕开那面墙。","veins":[],"result":{},"result_text":"墙上的字不缺读者，缺的是信的人。你信不信，往后的路会问你。"}]},
{"id":"event_d8_3","layer":8,"title":"核心的红光","body":"最深处没有声音。谐振器的红光把整个穹腔照透，红光穿过你，你的影子是透的。站在这里，像站在一样东西的注意力的正中间。","options":[
 {"text":"在光里站到底。","veins":["heat"],"result":{"maxhp":2,"damage":6},"result_text":"你站到红光把你从头到脚数完。数完之后你轻了一点，也硬了一点。它把你记成了这里的东西。"},
 {"text":"掬一捧红光带走。","veins":["light"],"result":{"card_reward":"rare","gaze":2},"result_text":"红光捧不起来。你带走的只是手心里多一点的热。但你说你带走了，红渊没有反驳。"},
 {"text":"转身往回走。","veins":["tremor"],"result":{"heal":10},"result_text":"你转身走了。红光在你背后留了一路。走得快的话，可以一直借着这点亮。"}]}
]

RL = [
{"id":"relic_61","name":"着陆点的盐钉","rarity":"common","veins":["light"],"effect_text":"每场战斗开始时，获得 4 点格挡。","effect_code":[{"trigger":"combat_start","action":"block","value":4}],"flavor":"钉是从旧返回舱外壳上起的。盐把它咬死了，撬下来费了半只手套。"},
{"id":"relic_62","name":"帝星一线","rarity":"rare","veins":["light"],"effect_text":"每回合开始时，凝视 +1。","effect_code":[{"trigger":"turn_start","action":"gaze","value":1}],"flavor":"一根细线扎进石头缝里，不动。你后来才发现自己一直朝着它走。"},
{"id":"relic_63","name":"历壁的拓片","rarity":"uncommon","veins":["tremor"],"effect_text":"每回合开始时，回复 1 点生命。","effect_code":[{"trigger":"turn_start","action":"heal","value":1}],"flavor":"最老那段刻痕拓下来贴在胸口。摸到它就想起有人比你有耐心得多。"},
{"id":"relic_64","name":"冷洞的慢","rarity":"common","veins":[],"effect_text":"最大生命 +4。","effect_code":[{"trigger":"run_start","action":"maxhp","value":4}],"flavor":"不吃不动，几年过去。你学不来，但可以带着。"},
{"id":"relic_65","name":"泉眼的滴水","rarity":"uncommon","veins":["water"],"effect_text":"每回合开始时，回复 2 点生命。","effect_code":[{"trigger":"turn_start","action":"heal","value":2}],"flavor":"水按滴记的地方，滴也是恩情。囊口塞着一种草，漏得刚好。"},
{"id":"relic_66","name":"干河床的行李","rarity":"common","veins":["mineral"],"effect_text":"击败敌人后，回复 2 点生命。","effect_code":[{"trigger":"on_kill","action":"heal","value":2}],"flavor":"主人往深处去了，脚步很稳。行李里最重的那样，他没带走。"},
{"id":"relic_67","name":"涌喉的客牌","rarity":"uncommon","veins":["water"],"effect_text":"每场战斗开始时，获得 5 点格挡。","effect_code":[{"trigger":"combat_start","action":"block","value":5}],"flavor":"客议会的牌子。市集里不问来路，牌子只问规矩。"},
{"id":"relic_68","name":"街灯的灯芯","rarity":"rare","veins":["light"],"effect_text":"击败敌人后，回复 3 点生命。","effect_code":[{"trigger":"on_kill","action":"heal","value":3}],"flavor":"三十七盏里的一盏。灯芯换过，火种是同一个。"},
{"id":"relic_69","name":"喷息的汤勺","rarity":"rare","veins":["heat"],"effect_text":"每回合开始时，共振额外 +2。","effect_code":[{"trigger":"turn_start","action":"resonance","value":2}],"flavor":"勺柄上刻着喷议会的价目。中立是明码标价的。"},
{"id":"relic_70","name":"管虫的触须","rarity":"uncommon","veins":["heat"],"effect_text":"每场战斗开始时，凝视 +1。","effect_code":[{"trigger":"combat_start","action":"gaze","value":1}],"flavor":"触须在红光里微微发光。过滤硫，也过滤别的东西。"},
{"id":"relic_71","name":"重金属的鳞","rarity":"uncommon","veins":["mineral"],"effect_text":"每场战斗开始时，获得 6 点格挡。","effect_code":[{"trigger":"combat_start","action":"block","value":6}],"flavor":"铅钡铋长在壳上。壳的主人活了很多年，死在别处。"},
{"id":"relic_72","name":"仪表的绿光","rarity":"rare","veins":["light"],"effect_text":"每回合开始时，回复 3 点生命。","effect_code":[{"trigger":"turn_start","action":"heal","value":3}],"flavor":"全死的仪表里有一块还活着。灭之前的那一下绿光，被它记住了。"},
{"id":"relic_73","name":"祭台的余温","rarity":"uncommon","veins":["heat"],"effect_text":"每场战斗开始时，获得 4 点格挡，凝视 +1。","effect_code":[{"trigger":"combat_start","action":"block","value":4},{"trigger":"combat_start","action":"gaze","value":1}],"flavor":"祭祀台上什么都没有，只有热。热穿过你，替你把多余的东西烧掉了些。"},
{"id":"relic_74","name":"茧上剥落的","rarity":"rare","veins":["tremor"],"effect_text":"每场战斗开始时，抽 2 张牌。","effect_code":[{"trigger":"combat_start","action":"draw","value":2}],"flavor":"从茧上剥落的一片。上面的纹路不是刻的，是自己长出来的。它还在长。"},
{"id":"relic_75","name":"账本上的一页","rarity":"uncommon","veins":[],"effect_text":"最大生命 +3。","effect_code":[{"trigger":"run_start","action":"maxhp","value":3}],"flavor":"八万年没人翻的账本翻到了新的一页。页码是你。"},
{"id":"relic_76","name":"透的影子","rarity":"rare","veins":["heat"],"effect_text":"每场战斗开始时，获得 3 点格挡；每回合开始时，回复 2 点生命。","effect_code":[{"trigger":"combat_start","action":"block","value":3},{"trigger":"turn_start","action":"heal","value":2}],"flavor":"红光把影子照透了。透的那部分跟着你走，厚的部分留在了原地。"}
]

# D2–D7 已有事件编号（各层数量不一），动态取每层现有最大序号顺延
import re as _re
_existing = json.load(io.open(os.path.join(ROOT, 'events/all.json'), encoding='utf-8'))
_existing = _existing['events'] if isinstance(_existing, dict) and 'events' in _existing else _existing
_maxseq = {}
for e in _existing:
    m = _re.match(r'event_d(\d+)_(\d+)$', e['id'])
    if m:
        L, n = int(m.group(1)), int(m.group(2))
        _maxseq[L] = max(_maxseq.get(L, 0), n)
_seq = dict(_maxseq)
for ev in EV:
    L = ev['layer']
    if L in (2, 3, 4, 5, 6, 7):
        _seq[L] = _seq.get(L, 0) + 1
        ev['id'] = 'event_d%d_%d' % (L, _seq[L])

for rel, key, add in [('events/all.json', 'events', EV), ('relics/all.json', 'relics', RL)]:
    p = os.path.join(ROOT, rel)
    d = json.load(io.open(p, encoding='utf-8'))
    arr = d[key] if isinstance(d, dict) and key in d else d
    have = {x['id'] for x in arr}
    new_ids = {x['id'] for x in add}
    assert not have & new_ids, 'id 冲突: ' + str(have & new_ids)
    arr.extend(add)
    out = d if isinstance(d, dict) else arr
    io.open(p, 'w', encoding='utf-8', newline='\n').write(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
    print(rel, '+', len(add), '->', len(arr))
