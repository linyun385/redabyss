# -*- coding: utf-8 -*-
"""探针3：坐实「风格词位置」+「散文式主次」+「prompt_extend」三者的正确配方。

依据探针1/2：
  · 括号权重不解析，且会把画面带成「贴在黑底上的旧纸样张」（有害）
  · negative_prompt 收了但没收住
  · 风格词写在开头当主语 → 模型把「一张旧纸」画成画面里的物体
  · 散文写「主体占画面四分之三、管道只是顶上一条细边」→ 真的生效了

三个实验：
  X1 风格后置 + 散文主次 + extend=false
  X2 同一提示词 + extend=true（默认）  → 看改写器会不会又把风格词实体化
  X3 X1 原样重跑一遍                      → 测抖动，判断「一次命中」是不是运气
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

# 风格词后置：说「怎么画这幅画」，而不是「画面里有一张纸」
P = ('地底洞窟里，一个橙褐色的硬壳团块倒挂在一根钢制管道下方。这个团块是画面的主体，'
     '占满画面中部，壳面布满苍白的盐脉，底面聚着一圈取食口器，热气从口器向下翻滚。'
     '管道只是画面上方一条细细的边。地面有深红的光从下往上照，团块的下缘被染成朱红，'
     '上部沉入黑暗，阴影投向岩顶。没有天空，没有地平线，没有文字。'
     '整幅画用石版画的方式绘制：细密排线，深墨轮廓，赭黄与烟灰色调，一点朱红，像米黄旧纸上的老印刷品。')

TESTS = [
    ('X1_style_tail', P, {'prompt_extend': False}),
    ('X2_extend_on', P, {'prompt_extend': True}),
    ('X3_repeat', P, {'prompt_extend': False}),
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
