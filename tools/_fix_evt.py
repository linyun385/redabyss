# -*- coding: utf-8 -*-
"""事件卡的「牌子/文字/纸类/现代电器」修复（规则 X）。

看图确认（art/_review_all/evt_all.png）：
  · 6 张画出了清晰文字：`TNGET.DO NOT OPEN.CLOSE`、`别数脚步声` 的中文木牌等
  · 5 张是现代小电器：带屏幕的盒子、收音机、喇叭、开关面板
  · 4 张是纸/书/信封/单据

规则 X（事件版，正向写法）：
  1. 「牌 / 告示 / 标语 / 记录」一律改写成「一块被反复划过的铁面」或「一片被工具刮得发亮的凹痕」，
     画面里不出现任何可读的字
  2. 不出现屏幕、收音机、喇叭、按钮面板、开关这些现代电器外形；
     要「发声/警示」就写「一只被敲得凹进去的生锈铁箱」或「一排挂着铁片的穿孔铁管」
  3. 不出现纸、册、书、信、单据
  4. 事件是「一幕」，可以有人，但人只占画面一侧，主体仍是那件东西或那处地方
  5. 必须写明镜头位置（贴地 / 齐腰平视 / 斜俯），平面物体一律斜放
  6. 80–140 字，一段，不分行

用法：python tools/_fix_evt.py [--apply] [--limit N]
"""
import json
import sys
import time
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

HIT = ['牌', '告示', '标语', '招牌', '字', '编号', '标签', '刻度', '铭文',
       '装置', '设备', '仪器', '开关', '仪表', '面板', '屏幕', '喇叭', '收音',
       '纸', '册', '书', '簿', '信']

SYS = """你在给一款地底废土卡牌游戏写中文生图提示词（百炼万相模型）。
你只改写事件卡的「主体段」，光照段和画法段由程序拼接，不要写。

世界观：红光从地底核心往上升，越深越浓；风格是石版画，细密排线、深墨轮廓、红光。
事件卡是「一幕情境」：可能有人在做事、有东西被留下、有地方出过事。

【必须遵守】
1. 任何「牌子 / 告示 / 标语 / 记录」都改写成：一块被反复划过的铁面，或一片被工具刮得发亮的凹痕。
   画面里不出现任何可读的字。
2. 不出现屏幕、收音机、喇叭、按钮面板、开关这些现代电器外形。
   要「发声 / 警示」就写成：一只被敲得凹进去的生锈铁箱，或一排挂着铁片的穿孔铁管。
3. 不出现纸、册、书、信、单据。
4. 可以有人，但人只占画面一侧，主体仍是那件东西或那处地方。
5. 写明镜头位置（贴地 / 齐腰平视 / 斜俯）；平面物体一律斜放，不许正对镜头。
6. 主体占画面中部约三分之二，四周是黑岩与碎石。
7. 80–140 字，一段话，不分行，不加引号。

只输出改写后的这一段文字。"""


def chat(messages, retries=2):
    body = {'model': MODEL, 'messages': messages, 'temperature': 0.85}
    for k in range(retries + 1):
        req = urllib.request.Request(
            URL, data=json.dumps(body).encode(),
            headers={'Authorization': 'Bearer ' + KEY, 'Content-Type': 'application/json'},
            method='POST')
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                d = json.loads(r.read())
            return (d['choices'][0]['message']['content'] or '').strip()
        except Exception as e:
            if k == retries:
                print('  调用失败', str(e)[:80])
                return ''
            time.sleep(2)


def main():
    apply = '--apply' in sys.argv
    lim = 40
    if '--limit' in sys.argv:
        lim = int(sys.argv[sys.argv.index('--limit') + 1])
    rows = json.loads(P.read_text(encoding='utf-8'))
    CAT = {r['id']: r for r in json.loads((GAME / 'data' / 'art_catalog.json').read_text(encoding='utf-8'))}

    targets = []
    for i, r in enumerate(rows):
        if not r['id'].startswith('event_'):
            continue
        j = r['prompt'].find(SPLIT)
        if j < 0:
            continue
        sub = r['prompt'][:j]
        if any(w in sub for w in HIT):
            targets.append((i, r, sub, r['prompt'][j:]))
    targets = targets[:lim]
    print('待改 %d 条' % len(targets))
    if not targets:
        return 0

    out, bad = [], 0
    for n, (i, r, sub, tail) in enumerate(targets, 1):
        c = CAT.get(r['id'], {})
        user = ('事件名：%s\n事件ID：%s\n事件说明：%s\n现在的主体段：\n%s\n\n请按规则重写这一段。'
                % (c.get('name', ''), r['id'], (c.get('desc') or '')[:90], sub))
        new = chat([{'role': 'system', 'content': SYS}, {'role': 'user', 'content': user}])
        if not new or len(new) < 40:
            print('  [%d/%d] %s 空返回' % (n, len(targets), r['id']))
            bad += 1
            continue
        out.append((i, r['id'], new + tail))
        print('  [%d/%d] %-14s %d → %d 字' % (n, len(targets), r['id'], len(sub), len(new)))
        time.sleep(0.4)

    if not apply:
        print('\n演练：前 2 条样本')
        for _, rid, txt in out[:2]:
            print('\n##', rid, '\n', txt.split(SPLIT)[0])
        return 0
    bak = P.with_suffix('.bak9.json')
    if not bak.exists():
        bak.write_text(P.read_text(encoding='utf-8'), encoding='utf-8')
    for i, rid, txt in out:
        rows[i]['prompt'] = txt
    P.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding='utf-8')
    print('写入 %d 条（跳过 %d）' % (len(out), bad))
    return 0


if __name__ == '__main__':
    sys.exit(main())
