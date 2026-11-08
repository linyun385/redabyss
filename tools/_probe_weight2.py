# -*- coding: utf-8 -*-
"""探针2：决定性判定 ①权重是否被解析 ②negative_prompt 是否真的生效 ③自然语言描述分量是否有效。

判定逻辑：
  WA/WB = 同一个画面，权重完全反向。若两张构图无差别 → 权重只是噪声文本，没被解析。
  NF    = 提示词要求「深红光」，负面词写「红色，红光，橙色，火焰」。
          若出图没有红 → 负面词生效；若照样红 → 接口收了但不理。
  WC    = 不用任何括号，只用大白话写「主体占画面四分之三，管道只是一条细边」→ 对照自然语言控制力。
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
OUT = GAME / 'art' / '_probe'
KEY = json.loads((WS / 'tools' / 'free_llm_keys.json').read_text(encoding='utf-8'))['DASHSCOPE_API_KEY']
MODEL = 'wanx2.1-t2i-turbo'
API = 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis'

STYLE = '古老的石版画，米黄做旧纸张，细密排线，深墨轮廓，赭黄与烟灰色调，一点朱红。'
TAIL = ('壳面布满苍白的盐脉，底面聚着一圈取食口器，地面被下方升起的深红光照亮，'
        '下缘被染成朱红，上部沉入黑暗。没有天空，没有地平线，没有文字。')

WA = STYLE + '（一整片嗜热菌落:3.0）倒挂在一根（钢制管道:0.2）下方。' + TAIL
WB = STYLE + '一根（钢制管道:3.0）横在画面上方，下方挂着（一小块嗜热菌落:0.2）。' + TAIL
NF = STYLE + '地底洞窟里，一个橙褐色硬壳团块倒挂在管道下方。' + TAIL
WC = (STYLE + '地底洞窟顶部横着一根钢制管道。管道下面挂着一个橙褐色的硬壳团块，'
      '它是画面的主体，占满画面四分之三，细节清晰；管道只是画面顶上一条细细的边。'
      '壳面布满苍白的盐脉，底面聚着一圈取食口器。' + TAIL)

TESTS = [
    ('WA_colony_hi', WA, {'prompt_extend': False}),
    ('WB_pipe_hi', WB, {'prompt_extend': False}),
    ('NF_no_red', NF, {'prompt_extend': False,
                       'negative_prompt': '红色，红光，橙色，火焰，炭火，熔岩'}),
    ('WC_prose', WC, {'prompt_extend': False}),
]


def post(body):
    h = {'Authorization': 'Bearer ' + KEY, 'Content-Type': 'application/json',
         'X-DashScope-Async': 'enable'}
    req = urllib.request.Request(API, data=json.dumps(body).encode(), headers=h, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b'{}')


def get(url):
    req = urllib.request.Request(url, headers={'Authorization': 'Bearer ' + KEY})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b'{}')


def run(tid, prompt, params):
    t0 = time.time()
    st, d = post({'model': MODEL, 'input': {'prompt': prompt}, 'parameters': params})
    if st != 200:
        return False, time.time() - t0, 'HTTP %s %s' % (st, json.dumps(d, ensure_ascii=False)[:300])
    task = (d.get('output') or {}).get('task_id')
    if not task:
        return False, time.time() - t0, '无 task_id'
    for _ in range(40):
        time.sleep(3)
        _, d2 = get('https://dashscope.aliyuncs.com/api/v1/tasks/' + task)
        o = d2.get('output') or {}
        s = o.get('task_status')
        if s == 'SUCCEEDED':
            url = (o.get('results') or [{}])[0].get('url')
            OUT.mkdir(parents=True, exist_ok=True)
            (OUT / (tid + '.png')).write_bytes(urllib.request.urlopen(url, timeout=180).read())
            return True, time.time() - t0, ''
        if s in ('FAILED', 'CANCELED', 'UNKNOWN'):
            return False, time.time() - t0, '任务失败 %s' % json.dumps(o, ensure_ascii=False)[:300]
    return False, time.time() - t0, '轮询超时'


def main():
    for tid, prompt, params in TESTS:
        ok, sec, err = run(tid, prompt, params)
        print('%-16s %s %5.1fs %s' % (tid, 'ok' if ok else 'FAIL', sec, err), flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
