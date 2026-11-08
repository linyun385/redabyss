# -*- coding: utf-8 -*-
"""第二步探测：思考模型能不能正常出文 + glm-4.5v 能不能看图。

为什么必须测：
  · 上一步 glm-4.6 / 4.5 / 4.5v 都返回 200 但 content 为空 —— 它们带思维链，
    max_tokens=8 全被 reasoning 吃掉。得确认加大上限后 content 正常。
  · 图质检是今晚最有价值的活（461 张），但必须先用已知答案的图校准：
    anm_0043（画面里有清晰文字，我在拼图上亲眼看到）当正例，
    anm_0001（干净的铁片 + 红光，没有字）当负例。
    两个都判对，才敢把这活交给它。
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


def post(body, timeout=120):
    req = urllib.request.Request(
        URL, data=json.dumps(body).encode(),
        headers={'Authorization': 'Bearer ' + KEY, 'Content-Type': 'application/json'},
        method='POST')
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with opener.open(req, timeout=timeout) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b'{}')
    except Exception as e:
        return -1, {'err': str(e)[:150]}


def b64(path, side=512):
    im = Image.open(path).convert('RGB')
    im.thumbnail((side, side), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, 'JPEG', quality=80)
    return base64.b64encode(buf.getvalue()).decode()


def main():
    # 1) 思考模型能不能出文
    print('== 1. 思考模型出文测试 ==')
    for m in ('glm-4.6', 'glm-4.5', 'glm-4.5-air'):
        st, d = post({'model': m, 'messages': [{'role': 'user', 'content': '用一句话说明什么是石版画'}],
                      'max_tokens': 400, 'temperature': 0.7})
        if st != 200:
            print('%-12s HTTP %s %s' % (m, st, json.dumps(d, ensure_ascii=False)[:120]))
            continue
        msg = (d.get('choices') or [{}])[0].get('message', {})
        c = (msg.get('content') or '').strip()
        u = d.get('usage') or {}
        print('%-12s content %d 字 | reasoning %s | token %d/%d'
              % (m, len(c), 'yes' if msg.get('reasoning_content') else 'no',
                 u.get('prompt_tokens', 0), u.get('completion_tokens', 0)))
        if c:
            print('    ', c[:60].replace('\n', ' '))

    # 2) 视觉模型校准
    print('\n== 2. glm-4.5v 看图校准 ==')
    cases = [('anm_0043', '正例：画面里有清晰的文字'), ('anm_0001', '负例：没有字')]
    q = ('这是一张游戏卡的插图。请只回答两点，用一行：'
         '① 画面里有没有出现可读的文字、字母或数字？答「有」或「没有」；'
         '② 主体是什么物件（5 个字以内）。')
    for rid, tag in cases:
        p = ART / (rid + '.webp')
        if not p.exists():
            print(rid, '缺图')
            continue
        st, d = post({'model': 'glm-4.5v', 'messages': [{'role': 'user', 'content': [
            {'type': 'image_url', 'image_url': {'url': 'data:image/jpeg;base64,' + b64(p)}},
            {'type': 'text', 'text': q}]}], 'max_tokens': 300, 'temperature': 0.2})
        if st != 200:
            print('%-10s HTTP %s %s' % (rid, st, json.dumps(d, ensure_ascii=False)[:160]))
            continue
        c = ((d.get('choices') or [{}])[0].get('message', {}).get('content') or '').strip()
        u = d.get('usage') or {}
        print('%-10s %s' % (rid, tag))
        print('    判定：', c[:120].replace('\n', ' '))
        print('    token %d/%d' % (u.get('prompt_tokens', 0), u.get('completion_tokens', 0)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
