# -*- coding: utf-8 -*-
"""按规则 VIII 重写主体段（去现实物种名词）+ 卡牌构图轮换。

只重写「主体段」= 从开头到「洞底是一整片深红的光」之前；红光段与画法段原样保留。
用法：python tools/_rewrite_prompts.py [--apply] [--limit N] [--kind foe|card|evt]
"""
import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
WS = Path(r'C:\Users\Administrator\Documents\deepseek-harness\default-workspace')
GAME = Path(__file__).resolve().parents[1]
P = GAME / 'data' / 'zh_prompts_full.json'
KEY = json.loads((WS / 'tools' / 'free_llm_keys.json').read_text(encoding='utf-8'))['DASHSCOPE_API_KEY']
URL = 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions'
MODEL = 'qwen-max'
SPLIT = '洞底是一整片深红的光'

SPECIES = re.compile(r'蜘蛛|跳蛛|螨|甲虫|蚂蚁|蝎|蜈蚣|蟹|虾|蛇|蜥蜴|螈|蛙|蟾|鱼|鳗|水母|海葵|珊瑚|蝠|鸟|鼠|兔|猫|犬|蠕虫|蛭|蜗牛|蛞蝓|蘑菇|真菌|苔藓|蕨|藤|草|树')

# 卡牌五套构图，按序号轮换
CARD_FRAMES = [
    '地底工作台上，{s}倒挂在台面边缘。',
    '地底工作台上，{s}平放在刮花的台面上。',
    '地底铁皮墙的墙角，{s}立着靠在墙边。',
    '地底洞窟的碎石堆里，{s}半埋在碎石中，露出上半个。',
    '地底木板上，{s}被一枚铁钉钉在板面上。',
]

RULES = """你是生图提示词改写器。只改写输入的「主体段」，输出改写后的主体段。
硬规则：
1. **禁止出现现实物种名词**。不许写蜘蛛、跳蚤、甲虫、蟹、虾、蛇、蜥蜴、螈、蛙、鱼、鳗、水母、鼠、蝠、
   蠕虫、蛭、蜗牛、蛞蝓、菌菇、苔藓、蕨等具体物种名；一律改写为**形态描述**：
   写清几条腿、身体分成几节、表皮是什么质地（湿亮/干裂/覆鳞棘/覆盖绒毛）、器官长在哪一侧。
   例：不写「蜘蛛」，写「一只扁而宽、八条关节长腿向两侧张开、背覆短绒毛的节肢捕食者」。
2. 主体必须是**可数单体**，用「一个/一只/一根/一块/一具/一盘」；不许用「一片/一丛/一群/一些」。
3. 主体段必须写足 50 字以上，含 **2–3 个实物细节**（接缝、裂口、编号刻痕、黏膜、盐粒、断口、骨节……）。
4. 句式固定为：
   「<场景与位置>，<量词+形态描述>在<某处>。<这个X>是画面的主体，占满画面中部，<2-3 个细节>。<次要物>只是<某处>的一条细边。」
5. 若给了「指定构图」，必须按它写第一句。
6. 只输出改写后的这一段文字本身，不要解释、不要引号、不要 JSON。"""


CARD_RULES = """卡牌额外硬约束（优先于其他规则）：
1. 主体只能是地底工业遗物：金属、骨、管线、玻璃、陶瓷、橡胶这类材质。
2. **禁止出现纸张、单据、书本、现代电子产品、车辆、塑料瓶、机器人手臂。**
   卡名里的「协议／评估／库存／运料」不等于要画纸或画车。
3. 抽象卡名必须实物化，例：
   协议 → 一块刻满凹槽的金属铭牌；评估 → 一副带刻度的黄铜量规；
   库存 → 一排封了蜡的金属罐；运料 → 带铁轮的低矮钢制推斗（不是卡车）；
   照明 → 罩着厚玻璃的灯；回收 → 一堆压扁的金属件。
4. 主体必须占满画面中部约三分之二，四周不要大片空黑。"""


def chat(messages, retries=2):
    body = {'model': MODEL, 'messages': messages, 'temperature': 0.7}
    for i in range(retries + 1):
        req = urllib.request.Request(URL, data=json.dumps(body).encode(),
                                     headers={'Authorization': 'Bearer ' + KEY,
                                              'Content-Type': 'application/json'}, method='POST')
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                d = json.loads(r.read())
            return d['choices'][0]['message']['content'].strip()
        except urllib.error.HTTPError as e:
            print('  HTTP %s' % e.code, flush=True)
            if e.code in (429, 500, 503):
                time.sleep(8 * (i + 1))
                continue
            return None
        except Exception as ex:
            print('  异常', str(ex)[:80], flush=True)
            time.sleep(5)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--limit', type=int, default=0)
    ap.add_argument('--kind', default='')
    a = ap.parse_args()

    rows = json.loads(P.read_text(encoding='utf-8'))
    targets = []
    for i, r in enumerate(rows):
        p = r['prompt']
        j = p.find(SPLIT)
        head = p[:j] if j > 0 else p
        kind = 'foe' if r['id'].startswith('enemy_') else ('evt' if r['id'].startswith('event_') else 'card')
        if a.kind and kind != a.kind:
            continue
        need = kind == 'card' or bool(SPECIES.search(head))
        if need:
            targets.append((i, r, kind, head))
    if a.limit:
        targets = targets[:a.limit]
    print('待重写 %d 条（卡牌全部 + 命中物种词的）' % len(targets), flush=True)

    done = 0
    for idx, r, kind, head in targets:
        frame = ''
        if kind == 'card':
            frame = CARD_FRAMES[idx % len(CARD_FRAMES)]
        user = '原主体段：\n%s' % head
        if frame:
            user += '\n\n指定构图（第一句照这个写，{s} 换成物件的形态描述）：\n%s' % frame
            user += '\n\n' + CARD_RULES
        out = chat([{'role': 'system', 'content': RULES}, {'role': 'user', 'content': user}])
        if not out:
            print('  跳过', r['id'], flush=True)
            continue
        out = out.strip().strip('"').replace('\n', '')
        j = r['prompt'].find(SPLIT)
        tail = r['prompt'][j:] if j > 0 else ''
        # 尾部光照段里可能残留物种名（「鳗鱼的下缘」），统一换成「它」
        tail = re.sub(r'(?:' + SPECIES.pattern + r')的', '它的', tail)
        r['new_prompt'] = out + tail
        done += 1
        if done % 10 == 0:
            print('  已重写 %d/%d' % (done, len(targets)), flush=True)
        time.sleep(0.6)

    print('重写完成 %d 条' % done)
    samples = [(r['id'], r['new_prompt']) for i, r, kind, head in targets if 'new_prompt' in r][:4]
    for i, r, kind, head in targets:
        if 'new_prompt' in r:
            rows[i]['prompt'] = r['new_prompt']
            del rows[i]['new_prompt']
    if a.apply:
        P.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding='utf-8')
        print('已写入', P.name)
    else:
        print('(演练；加 --apply 才写)')
    for sid, sp in samples:
        print('\n[%s]\n%s' % (sid, sp[:220]))
    return 0


if __name__ == '__main__':
    sys.exit(main())
