# -*- coding: utf-8 -*-
"""探针6：以用户点名的三张（P1 硬壳伞褶 / P2 管道下垂菌褶 / P3 去纸）为形态基准，把红光加强。

用户判据：「红光不够」。加强手段（都写进去，再逐项看效果）：
  · 明说光的颜色是纯正深红、没有橙色
  · 明说红光的覆盖面：画面下三分之一／整个洞底浸在红光里
  · 主体的暗面也带红，不只下缘一条
  · 亮部不许是橙黄
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

RED = ('洞底是一整片深红的光，从下往上照。红光铺满画面下三分之一，整个洞底、岩壁的下半截都被染红，'
       '红色浓到发暗。光的颜色是纯正的深红，没有橙色，没有黄光。'
       '下缘被染成朱红，上部沉入黑暗，阴影投向岩顶。暗面也带红，不是死黑。')
TAIL = ('背景留大片的黑。没有天空，没有地平线，没有文字。'
        '整幅画用石版画的方式绘制：细密排线，深墨轮廓，赭黄与烟灰只用在岩壁和旧纸上，'
        '画面的光全部是血红，红色是画面里最饱和的颜色，像米黄旧纸上的老印刷品。')

# 对应 P1：一大片硬壳伞褶从顶部垂下
S1 = ('地底洞窟顶部，一个巨大的硬壳伞褶从岩顶垂下。这个伞褶是画面的主体，占满画面中部，'
      '壳面分成一条条纵向的厚褶，褶的边缘粗糙，底面挂着一排排短小的取食须，须头是软的，'
      '须上凝着水珠。岩顶只是画面最上方一条暗边。' + RED + TAIL)

# 对应 P2：管道横在上方，菌褶从下面垂下来（不含纸）
S2 = ('地底洞窟里，一根粗钢管道横在画面上方，管道下方垂着一丛薄而宽的菌褶。这丛菌褶是画面的主体，'
      '占满画面中部，褶片层层叠叠向外张开，褶的边缘卷起，从褶间垂下许多细长的根须，根须末端发亮。'
      '管道只是画面上方一条细细的边。' + RED + TAIL)

# 对应 P3：同样垂挂的菌褶团块，明确不要纸、不要任何纸页
S3 = ('地底洞窟里，一个橙褐色的硬壳菌褶团块从管道下方垂着。这个团块是画面的主体，占满画面中部，'
      '表面是一圈圈放射状的薄褶，褶的边缘卷起，团块表面有苍白的盐脉，底面聚着一圈细小的取食口器。'
      '管道只是画面上方一条细细的边。画面里没有任何纸张、没有信纸、没有单页文件。' + RED + TAIL)

TESTS = [
    ('S1_umbrella_red', S1, {'prompt_extend': False}),
    ('S2_gills_red', S2, {'prompt_extend': False}),
    ('S3_gills_nopaper_red', S3, {'prompt_extend': False}),
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
        print('%-24s %s %5.1fs %s' % (tid, 'ok' if ok else 'FAIL', sec, err), flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
