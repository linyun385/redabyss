# -*- coding: utf-8 -*-
"""glm-5.3-flash 能力校准（排任务前必须做）。

三件事：
  A 文本重写质量：拿一条真实 dive 提示词 + 规则 IX 让它重写，人眼看够不够用
  B 看图能力：给 anm_0043（画面里有清晰文字，正例）问有没有可读文字
  C JSON 稳定性：要求只回 JSON，看能不能直接解析（批量质检的必要条件）

只报结果，不打印 key。
"""
import base64
import io
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')
WS = Path(r'C:\Users\Administrator\Documents\deepseek-harness\default-workspace')
GAME = Path(__file__).resolve().parents[1]
ART = GAME / 'web' / 'assets' / 'art'
KEY = json.loads((WS / 'tools' / 'free_llm_keys.json').read_text(encoding='utf-8'))['ZHIPU_API_KEY']
URL = 'https://open.bigmodel.cn/api/paas/v4/chat/completions'
M = 'glm-5.3-flash'
SPLIT = '洞底是一整片深红的光'

RULE = """你在给地底废土卡牌游戏写中文生图提示词（万相模型）。只改写「主体段」，光照段由程序拼接。
写法要求：
1 物件只写这几类实物：几块厚铁皮用铆钉钉成的方斗 / 一段铸成的厚铁管 / 一块铸成整块的铁盖板 /
  一只粗陶罐 / 一截骨管 / 铁链与挂钩。不要写装置、设备、仪器、开关、仪表、面板、屏幕、机器。
2 每个物件都写工艺痕迹：锈穿的洞、歪斜的焊缝、砸扁的边角、铆钉头、锈水淌到地面。
3 不写任何文字线索（编号、标签、刻度、刻字、铭文、字）。
4 写明镜头位置（贴地仰视 / 斜俯 / 斜侧），平面物体一律斜放。
5 主体占画面中部约三分之二，四周是黑岩。80–140 字，一段，不分行。
只输出改写后的这一段文字。"""


def post(body, timeout=180):
    req = urllib.request.Request(
        URL, data=json.dumps(body).encode(),
        headers={'Authorization': 'Bearer ' + KEY, 'Content-Type': 'application/json'},
        method='POST')
    op = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with op.open(req, timeout=timeout) as r:
            return 200, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b'{}')
    except Exception as e:
        return -1, {'err': str(e)[:150]}


def content(d):
    return ((d.get('choices') or [{}])[0].get('message', {}).get('content') or '').strip()


def b64(path, side=512):
    im = Image.open(path).convert('RGB')
    im.thumbnail((side, side), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, 'JPEG', quality=80)
    return base64.b64encode(buf.getvalue()).decode()


def main():
    rows = {r['id']: r['prompt'] for r in
            json.loads((GAME / 'data' / 'zh_prompts_full.json').read_text(encoding='utf-8'))}

    print('== A 文本重写（dive_0041，这条还没按规则 IX 改过）==')
    old = rows['dive_0041'].split(SPLIT)[0]
    print('原：', old[:80])
    st, d = post({'model': M, 'messages': [
        {'role': 'system', 'content': RULE},
        {'role': 'user', 'content': '原主体段：\n' + old}], 'max_tokens': 4000, 'temperature': 0.85})
    if st == 200:
        new = content(d)
        print('新（%d 字）：' % len(new), new)
    else:
        print('失败', st, json.dumps(d, ensure_ascii=False)[:150])

    print('\n== B 看图（anm_0043，画面里有清晰文字）==')
    p = ART / 'anm_0043.webp'
    st, d = post({'model': M, 'messages': [{'role': 'user', 'content': [
        {'type': 'image_url', 'image_url': {'url': 'data:image/jpeg;base64,' + b64(p)}},
        {'type': 'text', 'text': '这张图里有没有出现可读的文字、字母或数字？只回答「有」或「没有」。'}]}],
        'max_tokens': 4000, 'temperature': 0.1})
    print('状态', st, '→', content(d)[:120] if st == 200 else json.dumps(d, ensure_ascii=False)[:150])

    print('\n== C JSON 稳定性 ==')
    st, d = post({'model': M, 'messages': [
        {'role': 'user', 'content': '只回 JSON，不要解释：{"has_text": true 或 false, "subject": "5字以内"}\n'
                                    '题目：一张图里画着一块锈铁板，板上有两行很小的刻字。'}],
        'max_tokens': 4000, 'temperature': 0.1})
    raw = content(d) if st == 200 else ''
    print('原始：', raw[:160].replace('\n', ' '))
    try:
        obj = json.loads(raw[raw.find('{'):raw.rfind('}') + 1])
        print('解析成功：', obj)
    except Exception as e:
        print('解析失败：', str(e)[:60])
    return 0


if __name__ == '__main__':
    sys.exit(main())
