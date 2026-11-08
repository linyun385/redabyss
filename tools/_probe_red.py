# -*- coding: utf-8 -*-
"""探针4：把暖橙光改成红光。用户指定基准 = X2_extend_on（prose 版，extend=true）。

诊断：风格尾巴的「赭黄与烟灰色调」被模型拿来染光，把「深红」冲成了暖橙。
三种改法，只动光那一句 / 风格尾巴：
  R1 单光源 + 唯一彩色：明说画面里唯一的光就是地面那层红光，红色是唯一的彩色
  R2 限定赭黄不给光：赭黄灰只用于岩壁，光的部分必须是纯正血红
  R3 去掉赭黄，主调改血红：更激进的改法
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

SCENE = ('地底洞窟里，一个橙褐色的硬壳团块倒挂在一根钢制管道下方。这个团块是画面的主体，'
         '占满画面中部，壳面布满苍白的盐脉，底面聚着一圈取食口器，热气从口器向下翻滚。'
         '管道只是画面上方一条细细的边。')
STYLE_BASE = ('整幅画用石版画的方式绘制：细密排线，深墨轮廓，赭黄与烟灰色调，一点朱红，像米黄旧纸上的老印刷品。')

R1 = (SCENE + '画面里唯一的光源是洞底那一层从下往上照的红光，红色是整幅画里唯一的彩色。'
      '团块的下缘被染成朱红，上部沉入黑暗，阴影投向岩顶。没有天空，没有地平线，没有文字。' + STYLE_BASE)
R2 = (SCENE + '洞底是一片深红色的光，从下往上照，团块的下缘被染成朱红，上部沉入黑暗。'
      '没有天空，没有地平线，没有文字。'
      '整幅画用石版画的方式绘制：细密排线，深墨轮廓，赭黄与烟灰只用在岩壁和纸上，'
      '光的部分是纯正的血红，像米黄旧纸上的老印刷品。')
R3 = (SCENE + '洞底是一片猩红色的光，从下往上冲，把整个洞底染成血红，团块的下缘通红，上部沉入黑暗。'
      '没有天空，没有地平线，没有文字。'
      '整幅画用石版画的方式绘制：细密排线，深墨轮廓，暗红的墨与冷灰的阴影，'
      '红色是画面里最饱和的颜色，像米黄旧纸上的老印刷品。')

TESTS = [
    ('R1_single_light', R1, {'prompt_extend': False}),
    ('R2_limit_ochre', R2, {'prompt_extend': False}),
    ('R3_blood_tone', R3, {'prompt_extend': False}),
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
        print('%-18s %s %5.1fs %s' % (tid, 'ok' if ok else 'FAIL', sec, err), flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
