# -*- coding: utf-8 -*-
"""修 dive/trem 段跑成「现代工业制品」的问题（规则 IX）。

看图确认的失败模式（art/_review_all/card_all_3.png、4.png）：
  · 出现路由器/对讲机/机顶盒/音箱/现代仪表/枪/玻璃酒瓶 —— 提示词里写了
    「装置 / 设备 / 仪器 / 开关 / 仪表 / 面板 / 屏幕」，模型直接调现代工业产品参考
  · 出现「书 / 纸册 / 红板」—— 提示词写「金属铭牌」，平面正对镜头就被画成一块板
  · 画面上真的画出文字 —— 提示词里有「编号 / 标签 / 刻度 / 刻字 / 铭文」

规则 IX（正面写法，不用禁止词——万相对负面词免疫）：
  1. 物件只写「几块厚铁皮用铆钉钉成的方斗 / 一段铸铁管 / 一块铸成的铁盖板 /
     一只粗陶罐 / 一截骨管」，即「手工拼焊的粗糙铁件」；不写装置、设备、仪器、开关、
     仪表、面板、屏幕、机器、工具这些会把外形拉到现代工业品上的词
  2. 表面必须写工艺痕迹：锈穿的洞、歪斜的焊缝、砸扁的边、铆钉头、淌到地面的锈水 ——
     让模型画「做旧的手工铁件」而不是「设计过的产品」
  3. 不写任何文字线索；要表达「记录」就写「一片被工具刮得发亮的凹痕」
  4. 必须写镜头位置（贴地仰视 / 斜俯 / 斜侧），平面物体一律不许正对镜头
  5. 主体占画面中部约三分之二，四周是黑岩
  6. 只输出改写后的这一段文字

用法：
  python tools/_fix_device.py            # 演练，打印 3 条样本
  python tools/_fix_device.py --apply    # 真改
  python tools/_fix_device.py --apply --only dive,trem --limit 40
"""
import json
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

DEV = ['装置', '设备', '仪器', '开关', '仪表', '面板', '屏幕', '机器', '机械']
TXT = ['编号', '标签', '刻度', '刻字', '铭文']

SYS = """你在给一款地底废土卡牌游戏写中文生图提示词（百炼万相模型）。
你只改写「主体段」，光照段和画法段由程序拼接，不要写。

这个世界的规则：红光从地底核心往上升，所以万物把取食/生殖器官长在**下侧**、倒挂在顶上；
越深红越浓。风格是石版画：细密排线、深墨轮廓、红光。

【必须遵守的写法】
1. 物件只写这几类实物：几块厚铁皮用铆钉钉成的方斗 / 一段铸成的厚铁管 /
   一块铸成整块的铁盖板 / 一只粗陶罐 / 一截骨管 / 一副铁链与挂钩 / 一摞铁环。
   不要写「装置、设备、仪器、开关、仪表、面板、屏幕、机器、工具、柜、盒」这些词。
2. 每个物件都要写工艺痕迹：锈穿的洞、歪斜的焊缝、砸扁的边角、铆钉头、
   锈水淌到地面、接缝里塞着碎渣。
3. 不写任何文字线索（编号、标签、刻度、刻字、铭文、字）。
   要表达「记录」就写「一片被工具刮得发亮的凹痕」。
4. 必须写明镜头位置：贴地仰视、斜俯、或斜侧；平面物体一律斜放，不许正对镜头。
5. 主体占画面中部约三分之二，四周是黑岩与碎石。
6. 80–140 字，一段话，不分行，不加引号。

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

    only = ('dive_', 'trem_', 'anm_', 'cng_')
    if '--only' in sys.argv:
        only = tuple(x.strip() + '_' for x in sys.argv[sys.argv.index('--only') + 1].split(','))

    targets = []
    for i, r in enumerate(rows):
        if not r['id'].startswith(only):
            continue
        j = r['prompt'].find(SPLIT)
        if j < 0:
            continue
        sub = r['prompt'][:j]
        # 已经按规则 IX 改过的段落带着这些工艺痕迹词，跳过，别二次重写
        if any(w in sub for w in ('锈穿', '焊缝', '砸扁', '铆钉头')):
            continue
        if any(w in sub for w in DEV) or any(w in sub for w in TXT) or '牌' in sub:
            targets.append((i, r, sub, r['prompt'][j:]))
    targets = targets[:lim]
    print('待改 %d 条' % len(targets))
    if not targets:
        return 0

    done, out = 0, []
    for n, (i, r, sub, tail) in enumerate(targets, 1):
        c = CAT.get(r['id'], {})
        user = ('卡名：%s\n卡ID：%s\n原卡面说明：%s\n现在的主体段：\n%s\n\n请按规则重写这一段。'
                % (c.get('name', ''), r['id'], (c.get('desc') or '')[:80], sub))
        new = chat([{'role': 'system', 'content': SYS}, {'role': 'user', 'content': user}])
        if not new or len(new) < 40:
            print('  [%d/%d] %s 空返回，跳过' % (n, len(targets), r['id']))
            continue
        if any(w in new for w in DEV[:6]):
            print('  [%d/%d] %s 仍含设备词，跳过' % (n, len(targets), r['id']))
            continue
        out.append((i, r['id'], new + tail))
        done += 1
        print('  [%d/%d] %-12s %d → %d 字' % (n, len(targets), r['id'], len(sub), len(new)))
        if not apply and len(out) >= 3:
            print('\n演练模式，只改前 3 条作样本：')
            for _, rid, txt in out:
                print('\n##', rid, '\n', txt.split(SPLIT)[0])
            return 0
        time.sleep(0.4)

    if not apply:
        print('\n演练结束（未写入）。加 --apply 真改。')
        return 0
    bak = P.with_suffix('.bak6.json')
    if not bak.exists():
        bak.write_text(P.read_text(encoding='utf-8'), encoding='utf-8')
    for i, rid, txt in out:
        rows[i]['prompt'] = txt
    P.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding='utf-8')
    print('写入 %d 条（备份 %s）' % (len(out), bak.name))
    return 0


if __name__ == '__main__':
    sys.exit(main())
