# -*- coding: utf-8 -*-
"""确定 GLM-5.3-Flash 的确切模型 id（用户口述 5.3 flash，id 写法要探）。

沿用智谱 OpenAI 兼容端点；max_tokens 给足，避免被思维链吃掉导致空回复。
只报状态与回复，不打印 key。
"""
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
WS = Path(r'C:\Users\Administrator\Documents\deepseek-harness\default-workspace')
KEY = json.loads((WS / 'tools' / 'free_llm_keys.json').read_text(encoding='utf-8'))['ZHIPU_API_KEY']
URL = 'https://open.bigmodel.cn/api/paas/v4/chat/completions'

CAND = ['glm-5.3-flash', 'glm-5.3', 'glm-5-flash', 'glm-5', 'glm-flash',
        'glm-4.6-flash', 'glm-5.3-flash-preview', 'glm-5.3-flash-free']


def probe(m):
    body = {'model': m, 'messages': [{'role': 'user', 'content': '用一句话说明什么是石版画'}],
            'max_tokens': 400, 'temperature': 0.7}
    req = urllib.request.Request(
        URL, data=json.dumps(body).encode(),
        headers={'Authorization': 'Bearer ' + KEY, 'Content-Type': 'application/json'},
        method='POST')
    op = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with op.open(req, timeout=90) as r:
            d = json.loads(r.read())
        msg = (d.get('choices') or [{}])[0].get('message', {})
        c = (msg.get('content') or '').strip()
        u = d.get('usage') or {}
        return 'OK', '%d 字 | token %d/%d | %s' % (len(c), u.get('prompt_tokens', 0),
                                                   u.get('completion_tokens', 0), c[:50].replace('\n', ' '))
    except urllib.error.HTTPError as e:
        raw = e.read()[:200].decode('utf-8', 'replace')
        return 'HTTP %d' % e.code, raw.replace('\n', ' ')[:150]
    except Exception as e:
        return 'ERR', str(e)[:120]


for m in CAND:
    st, info = probe(m)
    print('%-24s %-10s %s' % (m, st, info))
