# -*- coding: utf-8 -*-
"""探测智谱这条通道今晚能用哪些模型（只报状态，不打印 key）。

为什么先探：免费档一直用的是 glm-4-flash；用户说今晚有额度，
但额度落在哪个模型、走哪个端点（paas/v4 还是 anthropic 兼容）没确认过。
不同模型能力差得多（glm-4.5v 能看图，glm-4-flash 不能），排任务前必须知道。

用法：python tools\\_probe_glm.py
"""
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
WS = Path(r'C:\Users\Administrator\Documents\deepseek-harness\default-workspace')
KEY = json.loads((WS / 'tools' / 'free_llm_keys.json').read_text(encoding='utf-8'))['ZHIPU_API_KEY']

CANDIDATES = [
    ('glm-4.6', 'https://open.bigmodel.cn/api/paas/v4/chat/completions'),
    ('glm-4.5', 'https://open.bigmodel.cn/api/paas/v4/chat/completions'),
    ('glm-4.5-air', 'https://open.bigmodel.cn/api/paas/v4/chat/completions'),
    ('glm-4-plus', 'https://open.bigmodel.cn/api/paas/v4/chat/completions'),
    ('glm-4-flash', 'https://open.bigmodel.cn/api/paas/v4/chat/completions'),
    ('glm-4.5v', 'https://open.bigmodel.cn/api/paas/v4/chat/completions'),
]


def probe(model, url):
    body = {'model': model, 'messages': [{'role': 'user', 'content': '回一个字：好'}],
            'max_tokens': 8, 'temperature': 0}
    req = urllib.request.Request(
        url, data=json.dumps(body).encode(),
        headers={'Authorization': 'Bearer ' + KEY, 'Content-Type': 'application/json'},
        method='POST')
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))  # 绕开注册表代理
    try:
        with opener.open(req, timeout=45) as r:
            d = json.loads(r.read())
        txt = (d.get('choices') or [{}])[0].get('message', {}).get('content', '')
        u = d.get('usage') or {}
        return 'OK', '回复=%r 输入%d/输出%d token' % (txt.strip()[:10], u.get('prompt_tokens', 0),
                                                u.get('completion_tokens', 0))
    except urllib.error.HTTPError as e:
        raw = e.read()[:300].decode('utf-8', 'replace')
        try:
            j = json.loads(raw)
            msg = j.get('error', {}).get('message') or j.get('message') or raw
        except Exception:
            msg = raw
        return 'HTTP %d' % e.code, str(msg)[:120]
    except Exception as e:
        return 'ERR', str(e)[:120]


def main():
    print('探测 %d 个模型\n' % len(CANDIDATES))
    ok = []
    for m, u in CANDIDATES:
        st, info = probe(m, u)
        print('%-14s %-12s %s' % (m, st, info))
        if st == 'OK':
            ok.append(m)
    print('\n可用：', ok or '（无）')
    return 0


if __name__ == '__main__':
    sys.exit(main())
