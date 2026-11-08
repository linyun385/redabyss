# -*- coding: utf-8 -*-
"""探针：百炼（DashScope）现在能不能用、能用哪些模型。

只打印状态码与模型名，**绝不打印 key**。
测三件事：
  1) 文本模型（qwen-turbo）是否 200
  2) 图像模型（wanx2.1-t2i-turbo）任务能否提交成功
  3) 若成功，下 1 张图到 art/_bailian/ 看质量
"""
import json
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
WS = Path(r'C:\Users\Administrator\Documents\deepseek-harness\default-workspace')
GAME = Path(r'C:\Users\Administrator\Desktop\杂七杂八\红渊\game')
OUT = GAME / 'art' / '_bailian'
OUT.mkdir(parents=True, exist_ok=True)

KEY = json.loads((WS / 'tools' / 'free_llm_keys.json').read_text(encoding='utf-8'))['DASHSCOPE_API_KEY']
H = {'Authorization': 'Bearer ' + KEY, 'Content-Type': 'application/json'}


def post(url, body, extra=None):
    h = dict(H)
    if extra:
        h.update(extra)
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=h, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b'{}')
    except Exception as e:
        return -1, {'err': str(e)[:120]}


def get(url):
    req = urllib.request.Request(url, headers={'Authorization': 'Bearer ' + KEY})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b'{}')
    except Exception as e:
        return -1, {'err': str(e)[:120]}


def main():
    # 1) 文本
    st, d = post('https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation', {
        'model': 'qwen-turbo',
        'input': {'messages': [{'role': 'user', 'content': '用一句中文回答：你是什么模型？'}]},
        'parameters': {'max_tokens': 60},
    })
    txt = ''
    if st == 200:
        txt = (d.get('output') or {}).get('text', '')[:80]
    print('[文本 qwen-turbo] status=%s  %s' % (st, txt or json.dumps(d, ensure_ascii=False)[:160]))

    # 2) 图像任务提交
    st2, d2 = post('https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis', {
        'model': 'wanx2.1-t2i-turbo',
        'input': {'prompt': 'a pale leathery egg-pod hanging from a rock ceiling in a red-lit cave, '
                            'antique lithograph print, ochre paper, red glow from below'},
        'parameters': {'size': '1024*1024', 'n': 1},
    }, {'X-DashScope-Async': 'enable'})
    tid = ((d2.get('output') or {}).get('task_id')) if st2 == 200 else None
    print('[图像 提交] status=%s task_id=%s  %s'
          % (st2, tid, '' if tid else json.dumps(d2, ensure_ascii=False)[:200]))

    # 3) 轮询
    if tid:
        for i in range(30):
            time.sleep(4)
            st3, d3 = get('https://dashscope.aliyuncs.com/api/v1/tasks/' + tid)
            o = d3.get('output') or {}
            status = o.get('task_status')
            if i % 3 == 0 or status == 'SUCCEEDED':
                print('  轮询 %2d status=%s %s' % (i + 1, status, o.get('message', '')))
            if status == 'SUCCEEDED':
                url = (o.get('results') or [{}])[0].get('url')
                print('  图片 URL:', (url or '')[:100])
                if url:
                    p = OUT / 'wanx_test_1.png'
                    p.write_bytes(urllib.request.urlopen(url, timeout=120).read())
                    print('  已下载:', p, round(p.stat().st_size / 1024), 'KB')
                break
            if status in ('FAILED', 'CANCELED', 'UNKNOWN'):
                print('  失败详情:', json.dumps(o, ensure_ascii=False)[:300])
                break


if __name__ == '__main__':
    main()
