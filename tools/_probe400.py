# -*- coding: utf-8 -*-
"""诊断 submit 400：原样重发一张失败素材的提交请求，把响应体打出来（不打印 key）。"""
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
WS = Path(r'C:\Users\Administrator\Documents\deepseek-harness\default-workspace')
GAME = Path(__file__).resolve().parents[1]
KEY = json.loads((WS / 'tools' / 'free_llm_keys.json').read_text(encoding='utf-8'))['DASHSCOPE_API_KEY']

P = {r['id']: r['prompt']
     for r in json.loads((GAME / 'data' / 'zh_prompts_full.json').read_text(encoding='utf-8'))}

aid = sys.argv[1] if len(sys.argv) > 1 else 'cng_0028'
prompt = P[aid]
print('素材', aid, '提示词长度', len(prompt))
print('---')
print(prompt[:200])
print('---')

h = {'Authorization': 'Bearer ' + KEY, 'Content-Type': 'application/json',
     'X-DashScope-Async': 'enable'}
body = {'model': 'wanx2.1-t2i-turbo',
        'input': {'prompt': prompt},
        'parameters': {'size': '1024*1024', 'n': 1, 'prompt_extend': False}}
req = urllib.request.Request(
    'https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis',
    data=json.dumps(body).encode(), headers=h, method='POST')
try:
    with urllib.request.urlopen(req, timeout=60) as r:
        print('status', r.status)
        print(r.read().decode('utf-8', 'replace')[:2000])
except urllib.error.HTTPError as e:
    print('status', e.code)
    print(e.read().decode('utf-8', 'replace')[:2000])
except Exception as e:
    print('err', type(e).__name__, str(e)[:300])
