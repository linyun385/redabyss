# -*- coding: utf-8 -*-
"""glm-5.3-flash 连打 10 次：看是否稳定、有没有限速、token 怎么记。

背景：用户那边控制台显示 5.3-flash 到 23:00 才开放，但我 21:47 已经调通。
先确认「调通」不是偶发——若 10/10 成功且无限速报错，说明现在这条通道确实可用；
再看响应里有没有能辨识计费归属的字段（id / usage / 是否有免费标记）。
"""
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
WS = Path(r'C:\Users\Administrator\Documents\deepseek-harness\default-workspace')
KEY = json.loads((WS / 'tools' / 'free_llm_keys.json').read_text(encoding='utf-8'))['ZHIPU_API_KEY']
URL = 'https://open.bigmodel.cn/api/paas/v4/chat/completions'
M = 'glm-5.3-flash'


def one(i):
    body = {'model': M, 'messages': [{'role': 'user', 'content': '第%d次：只回数字 %d' % (i, i)}],
            'max_tokens': 3000, 'temperature': 0.3}
    req = urllib.request.Request(
        URL, data=json.dumps(body).encode(),
        headers={'Authorization': 'Bearer ' + KEY, 'Content-Type': 'application/json'},
        method='POST')
    op = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    t0 = time.time()
    try:
        with op.open(req, timeout=120) as r:
            d = json.loads(r.read())
        msg = (d.get('choices') or [{}])[0].get('message', {})
        c = (msg.get('content') or '').strip()
        u = d.get('usage') or {}
        return True, time.time() - t0, c[:12], u.get('prompt_tokens', 0), u.get('completion_tokens', 0), \
            (d.get('id') or '')[:24], sorted((d.get('usage') or {}).keys())
    except urllib.error.HTTPError as e:
        return False, time.time() - t0, 'HTTP %d' % e.code, 0, 0, e.read()[:100].decode('utf-8', 'replace'), []
    except Exception as e:
        return False, time.time() - t0, str(e)[:60], 0, 0, '', []


def main():
    ok = 0
    tin = tout = 0
    for i in range(1, 11):
        good, sec, txt, pi, po, extra, keys = one(i)
        ok += good
        tin += pi
        tout += po
        print('%2d %s %5.1fs 回复=%-12s token %d/%d  %s' % (i, 'OK ' if good else 'FAIL', sec, txt, pi, po,
                                                          extra if not good else ''))
        if keys:
            print('     usage 字段：', keys)
    print('\n成功 %d/10，合计 token 输入 %d 输出 %d' % (ok, tin, tout))
    return 0


if __name__ == '__main__':
    sys.exit(main())
