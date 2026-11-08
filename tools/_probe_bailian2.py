# -*- coding: utf-8 -*-
"""第二轮探针：① 换文本模型看哪个不被限流；② 万相能否出「版画/铜版」质感的红渊图。

只打印状态与模型名，不打印 key。
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


def post(url, body, extra=None):
    h = {'Authorization': 'Bearer ' + KEY, 'Content-Type': 'application/json'}
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


TEXT_MODELS = ['qwen-plus', 'qwen-max', 'qwen-long', 'qwen3-max', 'qwen-turbo']

IMAGE_JOBS = [
    ('wanx_litho_1', 'wanx2.1-t2i-turbo',
     '古老的石版画风格，米黄做旧纸张，细密网格排线，深墨轮廓，赭黄与烟灰色调，一点朱红。'
     '地底洞窟内部，一只皮革质地的卵囊倒挂在天花板上，卵囊下端开着一圈软管口一样的孔，'
     '孔的下缘垂着细须。地面是最亮处，红光自下方升起，把卵囊下缘染成朱红，上半部沉进黑暗，'
     '阴影投向上方岩顶。画面里没有天空、没有地平线、没有文字。'),
    ('wanx_08redraw', 'wanx2.1-t2i-turbo',
     '米黄做旧纸张的石版画。地底洞窟顶部的环状开口垂下成群的苍白伞囊，伞盖朝下，'
     '取食口长在伞盖底面，细丝状的须向下垂向光。地面被深红的光照亮，下半部被染成朱红，'
     '上部沉入黑暗。孢子尘埃向下飘落。没有天空、没有地平线、没有文字。'),
]


def submit(model, prompt, size='1024*1024'):
    st, d = post('https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis', {
        'model': model, 'input': {'prompt': prompt},
        'parameters': {'size': size, 'n': 1},
    }, {'X-DashScope-Async': 'enable'})
    return st, (d.get('output') or {}).get('task_id'), d


def wait(tid, name):
    for i in range(40):
        time.sleep(3)
        st, d = get('https://dashscope.aliyuncs.com/api/v1/tasks/' + tid)
        o = d.get('output') or {}
        s = o.get('task_status')
        if s == 'SUCCEEDED':
            url = (o.get('results') or [{}])[0].get('url')
            p = OUT / (name + '.png')
            p.write_bytes(urllib.request.urlopen(url, timeout=180).read())
            print('  %s 成功 → %s（%d KB）' % (name, p.name, p.stat().st_size // 1024))
            return p
        if s in ('FAILED', 'CANCELED', 'UNKNOWN'):
            print('  %s 失败：%s' % (name, json.dumps(o, ensure_ascii=False)[:200]))
            return None
    print('  %s 超时' % name)
    return None


def main():
    print('=== 文本模型可用性 ===')
    for m in TEXT_MODELS:
        st, d = post('https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation', {
            'model': m,
            'input': {'messages': [{'role': 'user', 'content': '回答两个字：可用'}]},
            'parameters': {'max_tokens': 20},
        })
        detail = ''
        if st == 200:
            detail = (d.get('output') or {}).get('text', '')[:20]
        else:
            detail = (d.get('code') or d.get('err') or '')[:60]
        print('  %-12s status=%s  %s' % (m, st, detail))
        time.sleep(1)

    print('\n=== 万相：版画质感 + 中文世界观 ===')
    for name, model, prompt in IMAGE_JOBS:
        st, tid, d = submit(model, prompt)
        if st != 200 or not tid:
            print('  %s 提交失败 %s %s' % (name, st, json.dumps(d, ensure_ascii=False)[:150]))
            continue
        wait(tid, name)


if __name__ == '__main__':
    main()
