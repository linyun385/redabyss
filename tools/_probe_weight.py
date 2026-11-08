# -*- coding: utf-8 -*-
"""探针：万相到底认不认「权重」，以及 prompt_extend 是不是元凶。

只产出到 art\\_probe\\，不进游戏素材。不打印 key。
四个实验，同一主体（上次画失败的那片嗜热菌落）：
  P1 原提示词 + prompt_extend=false      → 关掉自动改写，看是否还画成管道
  P2 原提示词 + A1111 权重括号           → 看括号是被解析还是被当成文字
  P3 原提示词 + negative_prompt          → 看接口收不收负面词
  P4 可数单体改写（一个，不是一片）+ 权重 → 权重对「没有实体名词」有没有用
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
LUFA = ('地底洞窟顶部的钢制管道上，一整片嗜热菌落向下倒挂着生长，橙褐色的硬壳表面布满苍白的盐脉，'
        '取食的口器聚在菌落的底面，热气向下翻滚，地面被下方升起的深红光照亮，菌落下缘被染成朱红，'
        '上部沉入黑暗，阴影投向岩顶。没有天空，没有地平线，没有文字。')
# P4：把「一片菌落」改写成可数单体，并给它压权重、给管道降权重
LUFA_ONE = ('地底洞窟顶部的钢制管道下方，一个拳头大的橙褐色硬壳团块倒挂着，'
            '壳面布满苍白的盐脉，底面聚着一圈取食口器，热气向下翻滚，'
            '地面被下方升起的深红光照亮，团块下缘被染成朱红，上部沉入黑暗，阴影投向岩顶。'
            '没有天空，没有地平线，没有文字。')

TESTS = [
    ('P1_noextend', STYLE + LUFA,
     {'prompt_extend': False}),
    ('P2_weight', STYLE + '（(一整片嗜热菌落:1.8)）倒挂在（(钢制管道:0.6)）下方。' + LUFA,
     {'prompt_extend': False}),
    ('P3_negative', STYLE + LUFA,
     {'prompt_extend': False,
      'negative_prompt': '管道，钟乳石，石柱，岩石，风景，纯背景，文字'}),
    ('P4_one_with_weight', STYLE + '（(橙褐色硬壳团块:1.8)）' + LUFA_ONE,
     {'prompt_extend': False}),
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
        return False, time.time() - t0, '无 task_id %s' % json.dumps(d, ensure_ascii=False)[:200]
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
        print('%-20s %s %5.1fs %s' % (tid, 'ok' if ok else 'FAIL', sec, err), flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
