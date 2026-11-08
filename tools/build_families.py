# -*- coding: utf-8 -*-
"""从游戏数据建素材清单，再让 qwen-max 归族并写中文提示词。

阶段：
  --catalog   只建清单（data/art_catalog.json），不调模型
  --gen       调 qwen-max 归族 + 写提示词（--limit 控制条数，先小样试）
输出：
  data/art_catalog.json   全部对象：id / 类别 / 名称 / 描述
  data/zh_prompts_full.json  [{id, prompt, family, name}]
"""
import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
WS = Path(r'C:\Users\Administrator\Documents\deepseek-harness\default-workspace')
GAME = Path(__file__).resolve().parents[1]
KEY = json.loads((WS / 'tools' / 'free_llm_keys.json').read_text(encoding='utf-8'))['DASHSCOPE_API_KEY']
URL = 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions'
MODEL = 'qwen-max'

# ---- 提示词规范（docs/ART_PROMPT_SPEC.md 第一至七节的浓缩版）----
RULES = """你在为一款「地底红光」题材的卡牌 Roguelike 写**中文生图提示词**，供阿里万相模型出图。
世界设定只有一条铁律：「倒吊和红光」—— 红光从地底深处往上打，生物把取食/生殖器官长在身体最下面，
倾向从顶上垂下来。

【必须遵守】
1. 主体必须是**可数单体**：写「一个／一只／一根／一具／一盘」，绝不写「一片／一丛／一群／一些」。
2. 主体用**实物类比名词**：写「皮革状的卵囊」「断掉的软管口」「鱼钩一样的爪」，
   不要用「囊」「口器」「几丁质钩」这种抽象词。
3. 结构顺序：场景与位置 → 主体与占比（「这个X是画面的主体，占满画面中部」）→
   次要物（「Y只是画面上方一条细细的边」）→ 倒吊与红光 → 排除句 → 画法。
4. 红光段固定照抄这段（X 换主体称呼）：
   洞底是一整片深红的光，从下往上照。红光铺满画面下三分之一，整个洞底、岩壁的下半截都被染红，
   红色浓到发暗。光的颜色是纯正的深红，没有橙色，没有黄光。X的下缘被染成朱红，上部沉入黑暗，
   阴影投向岩顶。暗面也带红，不是死黑。
5. 结尾固定照抄：
   背景留大片纯黑，但整幅画铺满整个画面，没有画框，没有边框，没有装裱，没有留白纸边。
   没有天空，没有地平线，没有文字。
   整幅画用石版画的方式绘制：细密排线，深墨轮廓，赭黄与烟灰只用在岩壁和器物上，
   画面的光全部是血红，红色是画面里最饱和的颜色。
6. **主体那一段必须写足 60 字以上，包含 2–3 个具体的实物细节**（材质、接缝、裂口、编号、锈斑、黏膜、
   骨头、线圈……），细节要能想象出实物的形状。只写「一只皮革状的菌」不合格。
7. **原设如果是菌膜／菌落／苔毯／气团这类没有边界的形态，必须改写成一块有边界的单体**，
   例如「一块巴掌大、隆起的硬壳块」。禁止出现「一层」「一片」「一团」「一丛」「一群」。
8. **禁止复用样本里的名词**：不许再用「硬壳团块」「盐脉」「取食口器」「玻璃面罩」这些词。
   每个对象都要用**它自己专属**的实物细节来描述；同一批里两条提示词的主体描写不能雷同。
9. 只输出 JSON，不要解释。

【两条已通过验收的样本，照这个密度写】
样本一（敌人 · 嗜热菌落）：
地底洞窟里，一个暗橙褐色的硬壳团块倒挂在一根钢制管道下方。这个团块是画面的主体，占满画面中部，
壳面布满苍白的盐脉，底面聚着一圈圆形的取食口器，热气从口器向下翻滚。管道只是画面上方一条细细的边。
（后接红光段与画法段）

样本二（事件 · 穿防护服的遗体）：
地底走廊的岩壁边，一具穿着完整防护服的遗体靠着墙坐在地上。这具遗体是画面的主体，占满画面中部，
膝盖屈起，圆形的玻璃面罩内侧有几道浅浅的划痕，肩头落满灰尘，手套的手指抠在膝盖上。
身后的走廊是空的，只在上方留一条细窄的黑缝。

【按类别微调】
- 敌人：生物要倒挂或贴地爬，器官在最下面。
- 事件：画面里要有「人留下的痕迹」（半截手套、值班表、拖痕、留下的灯），可以有遗骸。
- 卡面：画**一件物件**（武器/工具/装置），倒挂或摆在工作台上，红光在下方，物件下缘被染红。
"""

SCHEMA = """输出 JSON 数组，每个元素：
{"id": "<原样照抄输入的 id>", "family": "<族名，中文，2-6字>", "prompt": "<完整中文提示词，180-260字>"}
形态相近的对象用同一个 family，但**同一族最多 3 个成员**，超过就拆族。"""


def load_catalog():
    rows = []
    enemies = json.loads((GAME / 'enemies' / 'all.json').read_text(encoding='utf-8'))
    for e in enemies:
        rows.append({'id': e['id'], 'kind': 'foe', 'name': e['name'],
                     'desc': (e.get('flavor') or '')[:120],
                     'extra': '层%d %s %s' % (e.get('layer', 0), e.get('tier', ''),
                                              ','.join(e.get('traits') or []))})
    events = json.loads((GAME / 'events' / 'all.json').read_text(encoding='utf-8'))
    for e in events:
        rows.append({'id': e['id'], 'kind': 'evt', 'name': e['title'],
                     'desc': (e.get('body') or '')[:140], 'extra': '层%d' % e.get('layer', 0)})
    for f in sorted((GAME / 'cards').glob('*.json')):
        for c in json.loads(f.read_text(encoding='utf-8')):
            rows.append({'id': c['id'], 'kind': 'card', 'name': c['name'],
                         'desc': (c.get('flavor') or '')[:120],
                         'extra': '%s %s %s' % (c.get('class', ''), c.get('type', ''),
                                                '/'.join(c.get('veins') or []))})
    return rows


def chat(messages, retries=2):
    body = {'model': MODEL, 'messages': messages, 'temperature': 0.4,
            'response_format': {'type': 'json_object'}}
    for i in range(retries + 1):
        req = urllib.request.Request(URL, data=json.dumps(body).encode(),
                                     headers={'Authorization': 'Bearer ' + KEY,
                                              'Content-Type': 'application/json'}, method='POST')
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                d = json.loads(r.read())
            return d['choices'][0]['message']['content']
        except urllib.error.HTTPError as e:
            msg = (e.read() or b'')[:200].decode('utf-8', 'replace')
            print('  HTTP %s %s' % (e.code, msg), flush=True)
            if e.code in (429, 500, 503):
                time.sleep(8 * (i + 1))
                continue
            return None
        except Exception as ex:
            print('  异常', str(ex)[:120], flush=True)
            time.sleep(5)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--catalog', action='store_true')
    ap.add_argument('--gen', action='store_true')
    ap.add_argument('--limit', type=int, default=0)
    ap.add_argument('--chunk', type=int, default=16)
    ap.add_argument('--kind', default='', help='只跑某一类：foe / evt / card')
    a = ap.parse_args()

    rows = load_catalog()
    cat = GAME / 'data' / 'art_catalog.json'
    cat.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding='utf-8')
    from collections import Counter
    cnt = Counter(r['kind'] for r in rows)
    print('清单已写 %s：共 %d 条 %s' % (cat.name, len(rows), dict(cnt)))

    if not a.gen:
        return 0
    todo = rows[:a.limit] if a.limit else rows
    if a.kind:
        todo = [r for r in todo if r['kind'] == a.kind]
    out_path = GAME / 'data' / 'zh_prompts_full.json'
    done = []
    if out_path.exists():
        done = json.loads(out_path.read_text(encoding='utf-8'))
    have = {d['id'] for d in done}
    todo = [r for r in todo if r['id'] not in have]
    print('待生成 %d 条，分 %d 批' % (len(todo), (len(todo) + a.chunk - 1) // a.chunk), flush=True)

    for i in range(0, len(todo), a.chunk):
        part = todo[i:i + a.chunk]
        lines = '\n'.join('- id=%s | 类别=%s | 名称=%s | %s | %s'
                          % (r['id'], r['kind'], r['name'], r['extra'], r['desc']) for r in part)
        content = chat([{'role': 'system', 'content': RULES + '\n' + SCHEMA},
                        {'role': 'user', 'content': '为下面这些对象各写一条提示词：\n' + lines}])
        if not content:
            print('  批次失败，跳过', part[0]['id'], flush=True)
            continue
        try:
            got = json.loads(content)
            if isinstance(got, dict):
                got = got.get('items') or got.get('list') or []
        except Exception as ex:
            print('  解析失败 %s: %s' % (str(ex)[:60], content[:120]), flush=True)
            continue
        name_of = {r['id']: r['name'] for r in part}
        added = 0
        for g in got:
            if not isinstance(g, dict) or 'id' not in g or 'prompt' not in g:
                continue
            done.append({'id': g['id'], 'name': name_of.get(g['id'], ''),
                         'family': g.get('family', ''), 'prompt': g['prompt']})
            added += 1
        out_path.write_text(json.dumps(done, ensure_ascii=False, indent=1), encoding='utf-8')
        print('  [%d/%d] +%d 条，累计 %d' % (min(i + a.chunk, len(todo)), len(todo), added, len(done)),
              flush=True)
        time.sleep(1.5)
    print('完成，累计 %d 条 → %s' % (len(done), out_path.name))
    return 0


if __name__ == '__main__':
    sys.exit(main())
