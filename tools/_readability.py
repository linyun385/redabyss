# -*- coding: utf-8 -*-
"""T269 可辨识度审计（夜班美术审计）。

判什么：113 张敌人图，画面主体与卡名/desc 的可辨识度，三档：
  一眼认出 = 主体核心名词与卡名/desc 直接对应
  要想想   = 主体画出来了，但与卡名的关联需一步推理（同物不同词/属性缺画/换喻）
  认不出   = 画成另一类东西、卡名承诺的主体未画、或画面说不清

口径（与 data/readability.md 顶部一致）：
- 本脚本不做视觉判断。判断依据是两份「逐张真看图后写的」人工文档：
  1. data/qa/QA_001..047.md 第 ⑦ 列「主体一句话」（T81-T127，逐张目检 web/assets/art/<id>.webp）
  2. data/lore/LORE_*.md 每条的「画面：」段（T158，逐张看图写的图鉴文案）
  两源覆盖 113/113。
- 其中 13 张两源表述矛盾或语义存疑，由审计员逐张亲验 webp 定档：
  enemy_d1_e4, enemy_d2_b2, enemy_d2_e3, enemy_d4_05, enemy_d5_01, enemy_d5_e3,
  enemy_d6_e1, enemy_d8_02, enemy_d8_05, enemy_d8_09, enemy_d8_11, enemy_d8_12, enemy_d8_e2
  （d6_e1 的 QA⑦「圆顶舱」系误读，以 LORE 与亲验为准。）

流程：脚本按关键词表（KEYS）粗分 -> 人工逐条复核（MANUAL_REVIEW 记录最终档与一句理由，
不许纯脚本定档）-> 本脚本生成 data/readability.md。

复算：
  python -I tools/_readability.py          # 重新生成 data/readability.md 并打印计数与改档记录
  python -I tools/_readability.py --check  # 校验 data/readability.md 与重算结果一致
  python -I tools/_readability.py --dump   # 打印三源原文 + 粗判/终判（人工核对用）
"""
import json
import os
import re
import sys
from collections import Counter, OrderedDict

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, 'data')
MD_PATH = os.path.join(DATA, 'readability.md')

TIER_NAME = OrderedDict([('hit', '一眼认出'), ('think', '要想想'), ('miss', '认不出')])

# ---------------------------------------------------------------- 三源抽取

def load_foes():
    cat = json.load(open(os.path.join(DATA, 'art_catalog.json'), encoding='utf-8'))
    return [c for c in cat if c.get('kind') == 'foe']


def load_qa7():
    """QA_*.md 表格 -> {id: 第⑦列主体一句话}。列索引按表头动态定位。"""
    out = {}
    qa_dir = os.path.join(DATA, 'qa')
    for fn in sorted(os.listdir(qa_dir)):
        if not re.match(r'QA_\d+\.md$', fn):
            continue
        lines = open(os.path.join(qa_dir, fn), encoding='utf-8').read().splitlines()
        col7 = None
        for ln in lines:
            cells = [c.strip() for c in ln.strip().strip('|').split('|')]
            if any('⑦' in c for c in cells):
                col7 = [j for j, c in enumerate(cells) if '⑦' in c][0]
                continue
            if col7 is not None and ln.strip().startswith('|') \
                    and not re.match(r'^\|[\s\-|]+\|$', ln.strip()):
                cells = [c.strip() for c in ln.strip().strip('|').split('|')]
                if len(cells) > col7 and re.match(r'^[a-z]+[a-z0-9_]+$', cells[0]):
                    out[cells[0]] = cells[col7]
    return out


def load_lore_pic():
    """LORE_*.md -> {id: 「画面：」段}。"""
    out = {}
    lore_dir = os.path.join(DATA, 'lore')
    for fn in sorted(os.listdir(lore_dir)):
        if not re.match(r'LORE_\d+\.md$', fn):
            continue
        cur = None
        for ln in open(os.path.join(lore_dir, fn), encoding='utf-8').read().splitlines():
            m = re.match(r'^##\s+(\S+)[\s　]', ln + ' ')
            if m:
                cur = m.group(1)
                continue
            if cur and ln.startswith('画面：'):
                out[cur] = ln[len('画面：'):].strip()
                cur = None
    return out


# ---------------------------------------------------------------- 关键词粗分表
# 每条敌人：d = 直接关键词（主体描述里出现即粗判「一眼认出」），
# i = 间接关键词（只有形态/环境关联，粗判「要想想」）。都查不到 = 粗判「认不出」。
# 只查 QA⑦ + LORE画面 两源文本。粗分仅作底稿，终档以 MANUAL_REVIEW 为准。

KEYS = {
    'enemy_d1_01': {'d': ['菌'], 'i': ['管道', '球状', '团块', '鳞壳']},
    'enemy_d1_02': {'d': ['菌'], 'i': ['膜']},
    'enemy_d1_03': {'d': ['螨'], 'i': ['节肢', '多足', '甲壳小虫']},
    'enemy_d1_04': {'d': ['苔'], 'i': ['毯', '绒']},
    'enemy_d1_05': {'d': ['钟乳', '盐'], 'i': ['倒挂', '锥', '石笋']},
    'enemy_d1_06': {'d': ['防护服', '空服', '宇航服'], 'i': ['人形', '头盔', '面甲', '躯壳']},
    'enemy_d1_07': {'d': ['软管', '管'], 'i': ['破裂', '裂口', '橡胶']},
    'enemy_d1_08': {'d': ['旗'], 'i': ['旗杆', '布面', '编号']},
    'enemy_d2_01': {'d': ['鳗'], 'i': ['长条生物', '蛇形']},
    'enemy_d2_02': {'d': ['菌'], 'i': ['钟形', '岩棚', '青绿']},
    'enemy_d2_03': {'d': ['蟹', '螯'], 'i': ['甲壳', '多足']},
    'enemy_d2_04': {'d': ['两栖', '蛙'], 'i': ['四肢', '羽鳃', '外鳃']},
    'enemy_d2_05': {'d': ['骨', '菌丝', '菌'], 'i': ['白骨', '垂丝']},
    'enemy_d2_06': {'d': ['鱼'], 'i': ['鱼群', '群游']},
    'enemy_d2_07': {'d': ['蛛'], 'i': ['八足', '节肢']},
    'enemy_d2_08': {'d': ['雪', '苔'], 'i': ['背甲', '生物背部']},
    'enemy_d2_09': {'d': ['蛀', '虫', '历'], 'i': ['缺口', '石壁']},
    'enemy_d3_01': {'d': ['蛇'], 'i': ['鳞', '盘绕', '长条生物']},
    'enemy_d3_02': {'d': ['贝'], 'i': ['壳', '螺', '孔洞']},
    'enemy_d3_03': {'d': ['鱼', '肺鱼'], 'i': ['鳍', '洞顶倒挂']},
    'enemy_d3_04': {'d': ['蛛'], 'i': ['长腿', '八足', '细足']},
    'enemy_d3_05': {'d': ['鼹'], 'i': ['挖掘', '爪', '兽形', '隧道']},
    'enemy_d3_06': {'d': ['蜗'], 'i': ['螺旋', '壳', '年轮']},
    'enemy_d3_07': {'d': ['蝠', '蝙蝠'], 'i': ['翼膜', '倒挂群体', '翅']},
    'enemy_d3_08': {'d': ['账', '算盘'], 'i': ['滴水', '天平']},
    'enemy_d3_09': {'d': ['缓步', '水熊'], 'i': ['八足', '皱缩小虫', '节肢']},
    'enemy_d4_01': {'d': ['鱼'], 'i': ['暗影', '悬停']},
    'enemy_d4_02': {'d': ['鱼'], 'i': ['鱼群', '环游', '滤食', '群']},
    'enemy_d4_03': {'d': ['蕨', '叶'], 'i': ['植物', '羽状叶']},
    'enemy_d4_04': {'d': ['鱼'], 'i': ['反光', '银色', '群']},
    'enemy_d4_05': {'d': ['鱼'], 'i': ['无眼', '暗影', '红']},
    'enemy_d4_06': {'d': ['蛭', '水母'], 'i': ['薄', '透光', '漂浮', '膜状', '环节']},
    'enemy_d4_07': {'d': ['水母'], 'i': ['伞状', '触须', '浮']},
    'enemy_d4_08': {'d': ['虫', '蠕'], 'i': ['藓', '发光', '长条生物']},
    'enemy_d4_09': {'d': ['影'], 'i': ['伏击', '暗处轮廓', '贴地']},
    'enemy_d4_10': {'d': ['须', '滤'], 'i': ['成排', '丝群', '刷状']},
    'enemy_d5_01': {'d': ['管虫', '触须', '虫'], 'i': ['管状', '羽状']},
    'enemy_d5_02': {'d': ['螈'], 'i': ['蝾螈', '池边', '四足']},
    'enemy_d5_03': {'d': ['菌', '塔'], 'i': ['塔状', '中空', '烟囱', '蘑菇']},
    'enemy_d5_04': {'d': ['蟾', '鸣'], 'i': ['鼓膜', '蛙形', '发声']},
    'enemy_d5_05': {'d': ['膜', '菌'], 'i': ['浅滩', '呼吸起伏', '覆盖']},
    'enemy_d5_06': {'d': ['喉', '管', '骨骼'], 'i': ['缠团', '空腔', '开合']},
    'enemy_d5_07': {'d': ['鳗'], 'i': ['泥中', '长条生物']},
    'enemy_d5_08': {'d': ['菌', '囊'], 'i': ['囊状', '鼓缩', '气囊']},
    'enemy_d5_09': {'d': ['丘', '菌', '火'], 'i': ['守泉', '泉口', '小丘']},
    'enemy_d5_10': {'d': ['管虫', '触须', '虫'], 'i': ['羽状', '管状']},
    'enemy_d6_01': {'d': ['菌'], 'i': ['发光', '菌群']},
    'enemy_d6_02': {'d': ['甲壳', '壳'], 'i': ['节肢', '垢']},
    'enemy_d6_03': {'d': ['鳄', '鳞'], 'i': ['爬行', '四足', '长吻']},
    'enemy_d6_04': {'d': ['锈', '菌'], 'i': ['指痕', '支撑柱', '锈迹']},
    'enemy_d6_05': {'d': ['鳄', '王', '鳞'], 'i': ['巨大', '爬行', '长吻']},
    'enemy_d6_06': {'d': ['蛞蝓', '铅'], 'i': ['软体', '爬痕', '裹壳']},
    'enemy_d6_07': {'d': ['藻'], 'i': ['垫', '暖', '覆盖']},
    'enemy_d6_08': {'d': ['鳞', '壳'], 'i': ['捡拾', '码放', '节肢']},
    'enemy_d6_09': {'d': ['菌'], 'i': ['低烧', '发光', '菌群']},
    'enemy_d7_01': {'d': ['残影', '人影', '影'], 'i': ['半透明', '轮廓', '对话']},
    'enemy_d7_02': {'d': ['蛇', '蜥', '光柱'], 'i': ['悬停', '长条生物']},
    'enemy_d7_03': {'d': ['杆菌', '杆', '皿', '分裂'], 'i': ['培养', '短棒']},
    'enemy_d7_04': {'d': ['孢子'], 'i': ['群', '漂浮颗粒', '雾']},
    'enemy_d7_05': {'d': ['苔'], 'i': ['墙', '丛', '覆盖']},
    'enemy_d7_06': {'d': ['网', '影'], 'i': ['倒挂', '发光', '穹顶']},
    'enemy_d7_07': {'d': ['记录', '无面', '脸'], 'i': ['人形', '空脸', '铭牌']},
    'enemy_d7_08': {'d': ['歌', '张嘴', '嘴'], 'i': ['人形', '雕像', '开口']},
    'enemy_d7_09': {'d': ['菌毯', '须', '三色'], 'i': ['毯', '丝', '黑红金']},
    'enemy_d7_10': {'d': ['影'], 'i': ['人形影子', '跟随', '慢半拍']},
    'enemy_d8_01': {'d': ['蛹', '茧'], 'i': ['计算', '纹路', '巨大茧']},
    'enemy_d8_02': {'d': ['行像', '像'], 'i': ['人形', '行进', '雕像', '石像']},
    'enemy_d8_03': {'d': ['防护服', '空壳', '服'], 'i': ['人形', '广播', '头盔']},
    'enemy_d8_04': {'d': ['虫', '丝'], 'i': ['吐丝', '纺器', '细长']},
    'enemy_d8_05': {'d': ['残片', '影'], 'i': ['碎片', '一角', '飘动', '破口']},
    'enemy_d8_06': {'d': ['腔', '壳'], 'i': ['空腔', '借壳', '容器']},
    'enemy_d8_07': {'d': ['班表', '表'], 'i': ['表格', '纸', '名单']},
    'enemy_d8_08': {'d': ['笔'], 'i': ['签到', '簿', '书写']},
    'enemy_d8_09': {'d': ['余音', '声', '波'], 'i': ['波形', '回声', '残响', '球']},
    'enemy_d8_10': {'d': ['告示', '告'], 'i': ['钉', '纸', '文字']},
    'enemy_d8_11': {'d': ['手', '检修窗'], 'i': ['窗', '仪表', '拨动']},
    'enemy_d8_12': {'d': ['噪音', '波形'], 'i': ['杂波', '雪花', '无形']},
    'enemy_d1_e1': {'d': ['防护服', '拾荒', '面甲'], 'i': ['人形']},
    'enemy_d1_e2': {'d': ['孢子', '清道'], 'i': ['扫拢', '堆积', '耙']},
    'enemy_d1_e3': {'d': ['气闸', '守夜'], 'i': ['门', '人形', '暗号']},
    'enemy_d1_e4': {'d': ['投影', '坠轨'], 'i': ['人影', '光像', '屏']},
    'enemy_d1_b1': {'d': ['钟乳', '盐'], 'i': ['塌落', '堆积', '锥体']},
    'enemy_d1_b2': {'d': ['广播', '静默号'], 'i': ['喇叭', '舰体', '声波']},
    'enemy_d2_e1': {'d': ['历', '虫'], 'i': ['甲壳', '节肢', '补痕']},
    'enemy_d2_e2': {'d': ['菌膜', '织'], 'i': ['纺', '丝', '膜']},
    'enemy_d2_e3': {'d': ['守历', '眠'], 'i': ['蜷', '守', '兽']},
    'enemy_d2_b1': {'d': ['历壁', '读'], 'i': ['壁', '刻痕', '守望']},
    'enemy_d2_b2': {'d': ['补写', '历'], 'i': ['笔', '刻写', '壁面', '瓮']},
    'enemy_d3_e1': {'d': ['贝'], 'i': ['孔洞', '成片', '壳阵']},
    'enemy_d3_e2': {'d': ['螈', '伏'], 'i': ['干缝', '蜷伏', '四足']},
    'enemy_d3_e3': {'d': ['干壳', '路'], 'i': ['壳', '爬行', '喉']},
    'enemy_d3_b1': {'d': ['封口', '壳', '泉'], 'i': ['塞', '脉口', '巨大壳']},
    'enemy_d3_b2': {'d': ['丈量', '泉'], 'i': ['量具', '触探', '水脉', '尺']},
    'enemy_d4_e1': {'d': ['藻', '伏击'], 'i': ['毯下', '埋伏', '突起', '毯']},
    'enemy_d4_e2': {'d': ['鱼', '巡游'], 'i': ['环游', '游动']},
    'enemy_d4_e3': {'d': ['鱼', '伏击'], 'i': ['暗处', '悬停', '红光闪烁']},
    'enemy_d4_b1': {'d': ['蛭', '水母', '逆流'], 'i': ['薄', '透光', '漂']},
    'enemy_d5_e1': {'d': ['喷息', '守卫'], 'i': ['喷口', '门卫', '节奏']},
    'enemy_d5_e2': {'d': ['硫沫', '赘生'], 'i': ['泡沫', '瘤状', '鼓包']},
    'enemy_d5_e3': {'d': ['汤', '执'], 'i': ['锅', '沸池', '人形', '勺']},
    'enemy_d5_b1': {'d': ['震喉', '空腔', '喉'], 'i': ['管骨缠团', '开合', '独奏']},
    'enemy_d6_e1': {'d': ['孢子'], 'i': ['团', '聚', '颗粒']},
    'enemy_d6_e2': {'d': ['鳄', '幼'], 'i': ['小型', '爬行', '鳞']},
    'enemy_d6_e3': {'d': ['铅鳞', '收藏'], 'i': ['仪表', '码放', '鳞甲']},
    'enemy_d6_b1': {'d': ['鳄', '蜕'], 'i': ['空壳', '蜕皮', '爬行']},
    'enemy_d6_b2': {'d': ['坛', '骨灰', '看守'], 'i': ['守', '骨']},
    'enemy_d7_e1': {'d': ['灰烬', '烧'], 'i': ['焦黑', '聚形', '手']},
    'enemy_d7_e2': {'d': ['祭司', '祭'], 'i': ['人形', '台', '仪式']},
    'enemy_d7_e3': {'d': ['水囊', '囊'], 'i': ['鼓', '透明', '沸腾']},
    'enemy_d7_b1': {'d': ['网', '影', '颤'], 'i': ['倒挂', '发光网', '垂']},
    'enemy_d8_e1': {'d': ['巡逻', '体'], 'i': ['机械', '循线', '旧形']},
    'enemy_d8_e2': {'d': ['残片', '影', '重奏'], 'i': ['碎片', '成对', '飘动']},
    'enemy_d8_b1': {'d': ['蛹', '茧'], 'i': ['计算', '未完成', '纹路']},
}

# ---------------------------------------------------------------- 人工复核（终档）
# 粗分后逐条人工对照（QA⑦ + LORE画面，存疑 13 张另亲验 webp）定档，每条一句理由。
# 档：hit=一眼认出 think=要想想 miss=认不出

MANUAL_REVIEW = {
    # ---- d1（14）
    'enemy_d1_01': ('hit', '管道下倒挂的层状球状菌团+环形古菌群，与「古菌贴管道」直接对应'),
    'enemy_d1_02': ('hit', '灰白菌膜罩红色长凳、垂粘液丝，与 desc「膜盖在座椅上」直接对应'),
    'enemy_d1_03': ('hit', '扁平螨形生物贴岩面爬行，与「住岩缝、身子比缝薄」直接对应'),
    'enemy_d1_04': ('hit', '黄绿厚苔毯翻搭岩台，与 desc「苔铺满整条管廊」直接对应'),
    'enemy_d1_05': ('hit', '倒挂在管道下的钟形盐体，与「盐从管壁倒着长」直接对应'),
    'enemy_d1_06': ('hit', '空的连帽防护服垂下、内里纯黑，与「防护服里早就没有人了」直接对应'),
    'enemy_d1_07': ('hit', '带双箍弯软管垂插红地、穿过碎裂圆环，与「晒裂的软管」直接对应'),
    'enemy_d1_08': ('hit', '褪色旗布直垂、旗下沿一列喇叭筒，与「记名的旗」直接对应'),
    'enemy_d1_e1': ('hit', '旧防护服人形倒挂、面甲带割出的横缝，与 desc「面甲上开了一条自己割的缝」直接对应'),
    'enemy_d1_e2': ('hit', '分节红虫尾端炸开须足、孢子被扫得飞散，与「孢子清道夫」直接对应'),
    'enemy_d1_e3': ('hit', '气闸服倒吊横梁、胸前亮屏垂进气闸口，与「气闸的守夜者」直接对应'),
    'enemy_d1_e4': ('hit', '亲验图：坠落人形半身没入岩层+轨道上一排发光屏，直接读作「投影在重演坠落」'),
    'enemy_d1_b1': ('hit', '崩落的盐体占满画幅、盐面红裂纵横，与「钟乳盐·塌落体」直接对应'),
    'enemy_d1_b2': ('hit', '双喇叭旧广播机吊洞顶、口吐两页稿纸，与 desc「广播稿念到第三页」直接对应'),
    # ---- d2（14）
    'enemy_d2_01': ('hit', '苍白鳗形生物自洞顶倒垂、尾尖卷钩，与「食腐鳗」直接对应'),
    'enemy_d2_02': ('hit', '青绿色钟形岩菌自顶垂压、下对红光斑，与「冷洞青菌」直接对应'),
    'enemy_d2_03': ('hit', '巨蟹正面张开双螯居中，与「墟蟹」直接对应'),
    'enemy_d2_04': ('hit', '带黄斑绿色两栖类趴岩台探向红水、颈侧羽鳃，与「休眠两栖类」直接对应'),
    'enemy_d2_05': ('hit', '巨兽骨斜悬、下缘垂菌丝、下方菌毯，与「噬骨菌群」直接对应'),
    'enemy_d2_06': ('hit', '通体正红鲈形大鱼张口悬水、细屑下沉，与「沉屑鱼」直接对应'),
    'enemy_d2_07': ('hit', '跳蛛占住洞口、八腿撑洞缘，与「冷洞跳蛛」直接对应'),
    'enemy_d2_08': ('hit', '雪脊覆顶的黑红肉体起伏，与 desc「雪落在它背上，落了八万年」及卡名「沉雪」直接对应'),
    'enemy_d2_09': ('think', '吊挂囊虫的豁口里积着纸页=吃进肚的历段，需借 desc「缺的那段在它肚子里」一步联上「蛀痕」'),
    'enemy_d2_e1': ('hit', '百节巨虫横跨坑口、节环密纹如历刻，与「历虫」直接对应'),
    'enemy_d2_e2': ('hit', '分节虫倒挂菌膜下、两根丝线垂落，与「菌膜织者」直接对应'),
    'enemy_d2_e3': ('think', '亲验图：倒挂昏睡的鳞兽对上「冷眠」，但画面无历壁/守读线索，「守历者」需借卡名一步'),
    'enemy_d2_b1': ('think', '扁长甲虫头抵壁根、口卷螺旋器伏于历壁红线之下，「守读」需一步推理'),
    'enemy_d2_b2': ('miss', '亲验图：画成洞顶垂落的黑陶巨瓮，无笔无历无写，与「历的补写者」语义不搭'),
    # ---- d3（14）
    'enemy_d3_01': ('hit', '红黑鳞蛇绕柱盘垂、头端吐信，与「硬矿洞蛇」直接对应'),
    'enemy_d3_02': ('hit', '蛋形巨贝布满成行圆孔半埋岩缝，与「钻孔贝」直接对应'),
    'enemy_d3_03': ('hit', '橙红肺鱼头下尾上垂入水洼、鳍肢如臂，与「干旱肺鱼」直接对应'),
    'enemy_d3_04': ('hit', '灰黑大蜘蛛倒挂洞顶、长腿弯拢，与「盲蛛」直接对应'),
    'enemy_d3_05': ('hit', '鼹形兽立碎石坡、张巨爪巨口，与「气腔洞鼹兽」直接对应'),
    'enemy_d3_06': ('hit', '螺旋壳蜗牛爬行、螺线一圈套一圈，与「硬壳蜗」及 desc「年轮一圈套一圈」直接对应'),
    'enemy_d3_07': ('hit', '无眼蝙蝠倒挂、双翼张开，与「空腔蝠」直接对应'),
    'enemy_d3_08': ('hit', '红肉关节珠的算盘悬账簿上方，与「滴水的账房」之「账」直接对应'),
    'enemy_d3_09': ('hit', '半透明缓步虫（水熊虫状）浮于红水，与「隐生的缓步」直接对应'),
    'enemy_d3_e1': ('hit', '数百枚卵圆壳挤成蜂窝状倒挂成片，与 desc「不是一只，是一片」直接对应'),
    'enemy_d3_e2': ('hit', '粒鳞蝾螈伏地皮、长颈折进裂口，与「旱螈伏兵」直接对应'),
    'enemy_d3_e3': ('hit', '滚圆干壳豁开、漏斗肉喉垂舌抵地，与「干壳」及 desc「修进你的喉咙」直接对应'),
    'enemy_d3_b1': ('hit', '圆背甲虫壳塞画顶洞口、六腿扒缘，与 desc「封口的东西是它自己的壳」直接对应'),
    'enemy_d3_b2': ('hit', '黄卷尺带铅锤垂入深坑量深，与「泉权的丈量者」直接对应'),
    # ---- d4（14）
    'enemy_d4_01': ('hit', '暗红色鱼悬洞内红黑水面，与「红腔鱼」直接对应'),
    'enemy_d4_02': ('think', '「滤食」直接对应，但「鱼群」画成倒挂的管状/须状生物，需一步推理'),
    'enemy_d4_03': ('hit', '亮绿蕨丛自洞顶倒垂、梢头转红，与「垂光蕨」直接对应'),
    'enemy_d4_04': ('hit', '银灰大鱼贴水线游、鱼身密排出光，与「光池银鱼」直接对应'),
    'enemy_d4_05': ('miss', '亲验图：画成有眼有臂的长尾软体兽，既无鱼形，画出的双眼也与「盲眼」相抵'),
    'enemy_d4_06': ('think', '悬空环节虫体壁透光对应 desc「薄得透光」，「蛭母」需从蠕虫状一步推理'),
    'enemy_d4_07': ('hit', '红色水母悬黑窟、垂腕足，与「浮光水母」直接对应'),
    'enemy_d4_08': ('hit', '淡黄绿鳗形蠕虫爬行、身后垂满红藓，与「光藓蠕虫」直接对应'),
    'enemy_d4_09': ('hit', '人形黑影踏红地、脚边黑环，与核心词「影」及 desc「影子先到」直接对应'),
    'enemy_d4_10': ('hit', '成片红须自岩檐垂落散成根须，与「滤食的须群」直接对应'),
    'enemy_d4_e1': ('hit', '橙红斑点毯状生物伏于谷底、毯心竖起细丝，与「藻毯」「伏击」直接对应'),
    'enemy_d4_e2': ('hit', '橙红鳞鱼在红水腔中游动、各鳍张开，与「红腔鱼·巡游种」直接对应'),
    'enemy_d4_e3': ('hit', '红鳞鱼倒悬暗水、嘴角垂液，与「红腔鱼的伏击手」直接对应'),
    'enemy_d4_b1': ('hit', '伞盖蛭母悬洞心、须上挂水滴状小灯，与「光蛭母·逆流」直接对应'),
    # ---- d5（14）
    'enemy_d5_01': ('miss', '亲验图：画成双丝悬吊的红色甲虫，管虫的管栖全无、羽冠只剩羽状肢可循'),
    'enemy_d5_02': ('hit', '巨型暗红蝾螈翻上丘坡、背脊锯齿，与「热泉螈」直接对应'),
    'enemy_d5_03': ('hit', '黄伞弯柄中空蘑菇、柄身开洞，与「硫塔菌」及 desc「硫塔中空」直接对应'),
    'enemy_d5_04': ('hit', '蟾形巨物四足扒壁、头顶悬发光体，与「震鸣蟾」直接对应'),
    'enemy_d5_05': ('hit', '暗红巨伞菌膜盖住浅滩、瘤突成排，与「铁细菌膜母体」直接对应'),
    'enemy_d5_06': ('hit', '灰绿波纹管绞成一球、球心黑色空腔，与 desc「管道骨骼缠成一团、中心空腔开合」直接对应'),
    'enemy_d5_07': ('hit', '白色小鳗卷附垂柱、柱下沸泥池开泡眼，与「沸泥鳗」直接对应'),
    'enemy_d5_08': ('hit', '赭褐球状囊菌立于坑口、囊底通红，与「硫雾囊菌」直接对应'),
    'enemy_d5_09': ('hit', '菌丘底下凹成红膛、膛顶倒挂看火生物，与「硫菌丘的看火者」直接对应'),
    'enemy_d5_10': ('hit', '巨管虫环节成排自檐缝探出、头端附肢，与「喷发期的管虫」直接对应'),
    'enemy_d5_e1': ('hit', '蟹扒在喷口前、口器张羽状小瓣，与「喷息守卫」两词直接对应'),
    'enemy_d5_e2': ('hit', '倒锥囊状生物带硫黄泡沫带、下挂球状赘生体，与「硫沫赘生体」直接对应'),
    'enemy_d5_e3': ('think', '亲验图：大汤勺吊管对准沸池，「执汤」场景直接，但「执汤者」主体未现，需一步换喻'),
    'enemy_d5_b1': ('hit', '钟形巨喉倒悬洞顶、底端开横缝、洞底红色波纹，与「震喉·空腔独奏」直接对应'),
    # ---- d6（14）
    'enemy_d6_01': ('hit', '倒垂绿伞菌悬亮红池穴上方，与「辐射合成菌」直接对应'),
    'enemy_d6_02': ('hit', '分节甲壳节肢虫带钳、节缝透红，与「抗辐射甲壳类」直接对应'),
    'enemy_d6_03': ('hit', '鳄形兽覆瓦状方鳞、鳞缝漏红，与「辐射金属鳞鳄」直接对应'),
    'enemy_d6_04': ('hit', '红边巨型蘑菇倒生洞顶、红液顺柄下淌，与「锈蚀菌」直接对应'),
    'enemy_d6_05': ('hit', '巨鳄倒挂洞顶、长吻针齿直指地面，与「辐射金属鳞鳄王」直接对应'),
    'enemy_d6_06': ('hit', '鳞皮蛞蝓倒吊、外缘裹灰黑厚皮，与 desc「铅皮是它自己裹的」直接对应'),
    'enemy_d6_07': ('hit', '深红圆顶藻垫坐落卵石滩，与「辐射藻垫」直接对应'),
    'enemy_d6_08': ('hit', '多节长虫倒挂、小肢拨弄贝壳，与「重鳞的拾壳者」直接对应'),
    'enemy_d6_09': ('hit', '巨型层叠菌团悬熔池上方、裂口红口透光，与「低烧的菌群」直接对应'),
    'enemy_d6_e1': ('hit', '亲验图：黑绒孢子挤成的半球丘压裂地、下缘一圈红杯口，与「休眠孢子群」直接对应（QA⑦「圆顶舱」系误读，以 LORE 与亲验为准）'),
    'enemy_d6_e2': ('hit', '幼鳄倒攀红壁、土黄鳞甲张口露齿，与「金属鳞鳄幼体」直接对应'),
    'enemy_d6_e3': ('hit', '梨形大囊嵌满仪表、方板、管件，与 desc「收仪表，收屏蔽板」直接对应'),
    'enemy_d6_b1': ('hit', '巨鳄背自洞顶探出、颈后一圈断壳开口，与 desc「王蜕了一次皮」直接对应'),
    'enemy_d6_b2': ('hit', '骸骨抱符带圆坛靠柱而坐，与「地神骨灰坛的看守」直接对应'),
    # ---- d7（14）
    'enemy_d7_01': ('hit', '拱龛内暗红人形无五官、手提浅钵，与「旧光者残影」直接对应'),
    'enemy_d7_02': ('hit', '鳞蛇垂悬、画顶一道旧光柱熄灭后的赭色裂缝，与「光柱蛇蜥」直接对应'),
    'enemy_d7_03': ('hit', '杆菌状巨蕈基部嵌深色圆皿，与「震杆菌」及 desc「培养皿碎了」直接对应'),
    'enemy_d7_04': ('hit', '红囊生纤毛细须、囊窗内红色颗粒挤作一团，与「孢子群」直接对应'),
    'enemy_d7_05': ('hit', '绿苔羽叶层层垂挂、末梢坠龟裂孢子盘，与「震语苔丛」直接对应'),
    'enemy_d7_06': ('hit', '漏斗形巨网自穹顶垂下、网口内亮红盘，与 desc「倒挂的发光网」直接对应'),
    'enemy_d7_07': ('hit', '灰白人形倒悬、头脸无五官、手托摊开小册，与「无面记录员」直接对应'),
    'enemy_d7_08': ('hit', '巨大虫首口腔深处纯黑、细牙两环，与 desc「张着嘴，不出声」直接对应'),
    'enemy_d7_09': ('hit', '细长菌须黑皮嵌金红斑块发光，与 desc「黑红金三色按顺序烫人」直接对应'),
    'enemy_d7_10': ('hit', '头形黑影三孔透红、画底另拱起半个黑影，与 desc「打的是你上一步的节奏」直接对应'),
    'enemy_d7_e1': ('hit', '纯黑灰烬疙瘩团悬半空、底下火柱烧上来，与「烧手的灰烬」直接对应'),
    'enemy_d7_e2': ('hit', '红袍祭司双臂高举撑黑布穹，与「震台祭司」直接对应'),
    'enemy_d7_e3': ('hit', '三节大水囊吊法兰下、筛纹囊嘴垂细流，与「超临界的水囊」直接对应'),
    'enemy_d7_b1': ('hit', '灰白巨网自洞顶收成倒锥、网面开孔衬红，与「穹顶之影·网颤」直接对应'),
    # ---- d8（15）
    'enemy_d8_01': ('hit', '巨大椭球茧蛹立红光洞穴、茧面纵纹密排，与「墟蛹」直接对应'),
    'enemy_d8_02': ('think', '亲验图：分节圆柱+箍环+孔端可读作行像的肢段（QA⑦读作石像肢体），「行」（自己在走）需借卡名一步'),
    'enemy_d8_03': ('hit', '旧防护服人形倒吊、面窗透黄光，与「空壳旧光者」直接对应'),
    'enemy_d8_04': ('hit', '灰白分节蠕虫自顶岩垂下探向坑底，与「茧丝虫」直接对应'),
    'enemy_d8_05': ('miss', '亲验图：画成内壁泛红的黑暗洞腔+垂丝，「墟蛹掉下来的一角（残片）」未画出'),
    'enemy_d8_06': ('hit', '圆口空壳侧卧、口内纯黑、侧面开小孔，与「墟腔」直接对应'),
    'enemy_d8_07': ('hit', '黄班表贴岩墙、格线排满小字数码，与「八万年前的班表」直接对应'),
    'enemy_d8_08': ('hit', '空签到大牌+管下倒悬长笔、笔尖垂直指地，与「签到簿的笔」直接对应'),
    'enemy_d8_09': ('think', '亲验图：悬杆圆球+球面环纹+洞口红光可一步读作共振球体，但无音波/余韵元素，联想偏弱'),
    'enemy_d8_10': ('hit', '木告示被横杆钉死、三行粗字拼不成词、弯臂灯照着，与「不许关闭的告示」直接对应'),
    'enemy_d8_11': ('miss', '亲验图：检修柜门关严、窗内空无一物，卡名「手」与 desc「有手拨仪表」均未画出'),
    'enemy_d8_12': ('miss', '亲验图：画成细绳倒吊的灰白肉囊，「白噪音」被实体肉块顶替，仅「无定形」勉强贴 desc'),
    'enemy_d8_e1': ('hit', '黑铁色钟形机体倒垂、环带+一圈筒状喷口烧橙红，与「循环的巡逻体」直接对应'),
    'enemy_d8_e2': ('miss', '亲验图：黑绒丘+一排橙红杯盘，与 d8_05 不成「同一片残影抄两遍」，画面读作菌卵丘'),
    'enemy_d8_b1': ('hit', '剖面构图：灰黑巨壳垂红须根、接住竖肋红茧，与「墟蛹·未完成」直接对应'),
}

# 「认不出」的修改建议（改图 / 改文案）
SUGGEST = {
    'enemy_d2_b2': '改图：瓮口对准刻满历纹的壁面、垂墨补写缺段，把「补写」画出来',
    'enemy_d4_05': '改图：改回鱼形+退化眼点、去掉手臂；或改文案去掉「鱼」',
    'enemy_d5_01': '改图：改管栖环节虫+羽状触冠，去悬丝与虫腿；或改文案改「管虫」为实画之物',
    'enemy_d8_05': '改文案：改成「墟蛹崩落的腔口」一类有据之名（改图补断口残片亦可）',
    'enemy_d8_11': '改图：柜门半开，露一只拨表的手',
    'enemy_d8_12': '改图：改雪花噪点/扭动的无形扰动带，去肉囊；或改文案改成有形之名',
    'enemy_d8_e2': '改图：与 d8_05 画成同一残片的两份拷贝（微差即可）',
}

# 亲验 webp 的 13 张（口径记录用）
EYEBALL_CHECKED = [
    'enemy_d1_e4', 'enemy_d2_b2', 'enemy_d2_e3', 'enemy_d4_05', 'enemy_d5_01',
    'enemy_d5_e3', 'enemy_d6_e1', 'enemy_d8_02', 'enemy_d8_05', 'enemy_d8_09',
    'enemy_d8_11', 'enemy_d8_12', 'enemy_d8_e2',
]


def sort_key(fid):
    m = re.match(r'enemy_d(\d+)(?:_([eb])(\d+)|_(\d+))?$', fid)
    layer = int(m.group(1))
    kind = {'e': 1, 'b': 2}.get(m.group(2), 0)
    num = int(m.group(3) or m.group(4) or 0)
    return (layer, kind, num)


def build_rows():
    foes = load_foes()
    qa7 = load_qa7()
    lore = load_lore_pic()
    assert len(foes) == 113, 'art_catalog foe 数应为 113，实际 %d' % len(foes)
    missing_q = [c['id'] for c in foes if c['id'] not in qa7]
    missing_l = [c['id'] for c in foes if c['id'] not in lore]
    assert not missing_q and not missing_l, '对照源缺: %s %s' % (missing_q, missing_l)
    assert set(MANUAL_REVIEW) == {c['id'] for c in foes}, 'MANUAL_REVIEW 覆盖与 113 张不一致'
    rows = []
    for c in sorted(foes, key=lambda c: sort_key(c['id'])):
        fid = c['id']
        q, l = qa7[fid], lore[fid]
        text = q + ' ' + l
        rough = 'miss'
        for k in KEYS[fid]['d']:
            if k in text:
                rough = 'hit'
                break
        if rough == 'miss':
            for k in KEYS[fid]['i']:
                if k in text:
                    rough = 'think'
                    break
        tier, reason = MANUAL_REVIEW[fid]
        rows.append({'id': fid, 'name': c['name'], 'tier': tier, 'reason': reason,
                     'rough': rough, 'qa7': q, 'lore': l})
    return rows


def pct(n, total):
    return '%.1f%%' % (100.0 * n / total)


def render_md(rows):
    total = len(rows)
    cnt = Counter(r['tier'] for r in rows)
    layers = []
    for d in range(1, 9):
        sub = [r for r in rows if r['id'].startswith('enemy_d%d_' % d)]
        c = Counter(r['tier'] for r in sub)
        layers.append((d, len(sub), c))
    L = []
    L.append('# 可辨识度审计（T269）')
    L.append('')
    L.append('生成：`tools/_readability.py`。复算：`python -I tools/_readability.py --check`（重算并与本文件比对）。')
    L.append('')
    L.append('## 口径')
    L.append('')
    L.append('- 判什么：113 张敌人图，画面主体与卡名/desc 的可辨识度，三档：**一眼认出 / 要想想 / 认不出**。')
    L.append('- 对照源（均覆盖 113/113）：① `data/qa/QA_001–047.md` 第⑦列「主体一句话」（T81–T127，逐张目检 `web/assets/art/<id>.webp` 后所写）；② `data/lore/LORE_*.md` 每条「画面：」段（T158，逐张看图所写）。脚本不做视觉判断，粗分只按关键词对这两源做匹配。')
    L.append('- 其中 %d 张两源表述矛盾或语义存疑（%s），由审计员逐张亲验 webp 定档；`enemy_d6_e1` 的 QA⑦「圆顶舱」系误读，以 LORE 与亲验为准。' % (len(EYEBALL_CHECKED), '、'.join('`%s`' % i for i in EYEBALL_CHECKED)))
    L.append('- 档次判据：一眼认出=主体核心名词与卡名/desc 直接对应；要想想=主体画出但关联需一步推理（同物不同词/属性缺画/换喻/抽象概念的具象化可读出）；认不出=画成另一类东西、卡名承诺的主体未画、或画面说不清。')
    L.append('- 流程：脚本按关键词表粗分 → 人工逐条复核定档（最终档与一句理由记录于脚本 `MANUAL_REVIEW`，非纯脚本定档）→ 本文件由脚本生成，数字可复算。')
    L.append('')
    L.append('## 计数')
    L.append('')
    L.append('| 一眼认出 | 要想想 | 认不出 | 合计 |')
    L.append('|---|---|---|---|')
    L.append('| %d（%s） | %d（%s） | %d（%s） | %d |' % (
        cnt['hit'], pct(cnt['hit'], total), cnt['think'], pct(cnt['think'], total),
        cnt['miss'], pct(cnt['miss'], total), total))
    L.append('')
    L.append('## 分层分布（d1–d8）')
    L.append('')
    L.append('| 层 | 张数 | 一眼认出 | 要想想 | 认不出 |')
    L.append('|---|---|---|---|---|')
    for d, n, c in layers:
        L.append('| d%d | %d | %d | %d | %d |' % (d, n, c['hit'], c['think'], c['miss']))
    L.append('| 合计 | %d | %d | %d | %d |' % (total, cnt['hit'], cnt['think'], cnt['miss']))
    L.append('')
    L.append('## 全表（113 行，每行：id | 卡名 | 档次 | 一句理由）')
    L.append('')
    L.append('| id | 卡名 | 档次 | 一句理由 |')
    L.append('|---|---|---|---|')
    for r in rows:
        L.append('| %s | %s | %s | %s |' % (r['id'], r['name'], TIER_NAME[r['tier']], r['reason']))
    L.append('')
    L.append('## 认不出名单与建议')
    L.append('')
    L.append('| id | 卡名 | 建议 |')
    L.append('|---|---|---|')
    for r in rows:
        if r['tier'] == 'miss':
            L.append('| %s | %s | %s |' % (r['id'], r['name'], SUGGEST[r['id']]))
    L.append('')
    miss_rows = [r for r in rows if r['tier'] == 'miss']
    weak_layers = [(d, n, c) for d, n, c in layers if c['hit'] < n]
    L.append('## 结论')
    L.append('')
    L.append('1. 113 张：一眼认出 %d（%s）、要想想 %d（%s）、认不出 %d（%s）。' % (
        cnt['hit'], pct(cnt['hit'], total), cnt['think'], pct(cnt['think'], total),
        cnt['miss'], pct(cnt['miss'], total)))
    L.append('2. 认不出集中在 d8 抽象物卡（%d/7）：%s；另 d4_05、d5_01 形态画错，d2_b2 画成无关巨瓮。' % (
        sum(1 for r in miss_rows if r['id'].startswith('enemy_d8_')),
        '、'.join(r['id'] for r in miss_rows if r['id'].startswith('enemy_d8_'))))
    L.append('3. 分层看：%s 全层一眼；d8 最弱（15 张中 %d 张一眼）。' % (
        '、'.join('d%d' % d for d, n, c in layers if c['hit'] == n),
        next(c['hit'] for d, n, c in layers if d == 8)))
    L.append('4. 认不出 7 张建议：%d 张改图、%d 张改文案更省（d8_05）；明细见上表。' % (
        sum(1 for k in SUGGEST if SUGGEST[k].startswith('改图')),
        sum(1 for k in SUGGEST if SUGGEST[k].startswith('改文案'))))
    L.append('5. 抽查验证：任取一行理由，可在 QA⑦ / LORE「画面：」/亲验图三源中直接对回；复算 `python -I tools/_readability.py --check`。')
    L.append('')
    return '\n'.join(L)


def main():
    rows = build_rows()
    md = render_md(rows)
    if '--dump' in sys.argv:
        for r in rows:
            mark = '' if r['rough'] == r['tier'] else '  [粗判%s→人工改%s]' % (
                TIER_NAME[r['rough']], TIER_NAME[r['tier']])
            print('%s\t%s\t%s\t%s%s' % (r['id'], r['name'], TIER_NAME[r['tier']], r['reason'], mark))
            print('  QA⑦: %s' % r['qa7'])
            print('  画面: %s' % r['lore'])
        return
    if '--check' in sys.argv:
        old = open(MD_PATH, encoding='utf-8').read() if os.path.exists(MD_PATH) else ''
        if old == md:
            print('CHECK OK: data/readability.md 与重算结果一致（113 行）。')
        else:
            print('CHECK FAIL: data/readability.md 与重算结果不一致。')
            sys.exit(1)
        return
    with open(MD_PATH, 'w', encoding='utf-8', newline='\n') as f:
        f.write(md)
    cnt = Counter(r['tier'] for r in rows)
    changed = [(r['id'], TIER_NAME[r['rough']], TIER_NAME[r['tier']])
               for r in rows if r['rough'] != r['tier']]
    print('已生成 %s' % MD_PATH)
    print('计数: 一眼认出 %d / 要想想 %d / 认不出 %d / 合计 %d' % (
        cnt['hit'], cnt['think'], cnt['miss'], len(rows)))
    print('粗判→人工改档 %d 条:' % len(changed))
    for fid, a, b in changed:
        print('  %s: %s -> %s' % (fid, a, b))


if __name__ == '__main__':
    main()
