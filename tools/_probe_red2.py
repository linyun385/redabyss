# -*- coding: utf-8 -*-
"""探针5：定稿红光配方，同一配方跑两张验稳定。

依据 R1/R2/R3：
  · R1（单光源+唯一彩色，保留赭黄）→ 主体对、光还是暖橙
  · R2（赭黄只给岩壁/纸）→ 光红了
  · R3（去掉赭黄改血红主调）→ 光最红
  → 元凶确认：风格尾巴里的「赭黄」被用来染光。
R4：R1 的场景骨架 + 赭黄限定 + 主体压成暗橙褐（不出白色高光）+ 背景多留黑。
同一提示词跑两张（R4a/R4b）看抖动。
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

R4 = ('地底洞窟里，一个暗橙褐色的硬壳团块倒挂在一根钢制管道下方。这个团块是画面的主体，'
      '占满画面中部，壳面布满苍白的盐脉，底面聚着一圈圆形的取食口器，热气从口器向下翻滚。'
      '管道只是画面上方一条细细的边。'
      '洞底是一层深红的光，从下往上照，光从口器下方的地面升起。团块的下缘通红，上部沉入黑暗，阴影投向岩顶。'
      '壳面只有暗橙褐与暗红，没有白色高光。背景留大片的黑。'
      '没有天空，没有地平线，没有文字。'
      '整幅画用石版画的方式绘制：细密排线，深墨轮廓，赭黄与烟灰只用在岩壁和旧纸上，'
      '画面的光全部是血红，红色是画面里最饱和的颜色，像米黄旧纸上的老印刷品。')

TESTS = [
    ('R4a_recipe', R4, {'prompt_extend': False}),
    ('R4b_recipe', R4, {'prompt_extend': False}),
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
        print('%-14s %s %5.1fs %s' % (tid, 'ok' if ok else 'FAIL', sec, err), flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
