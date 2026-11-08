# -*- coding: utf-8 -*-
"""试点：用新提示词（规则 XII）重生 2 张器械卡，存成 v3 候选。

为什么要等：百炼 4 并发会 100% 429（实测），必须等当前批次跑完再提交。
这里先用文件数判断批次是否结束，稳定 90 秒后自动开跑，不用人盯。

产出：art/versions/dive_0002_v3.webp（聚能枪）
      art/versions/dive_0025_v3.webp（震频器）
不覆盖任何现有图。
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
VERS = GAME / 'art' / 'versions'
RAW = GAME / 'art' / 'versions_raw'
KEY = json.loads((WS / 'tools' / 'free_llm_keys.json').read_text(encoding='utf-8'))['DASHSCOPE_API_KEY']
MODEL = 'wanx2.1-t2i-turbo'
VER = 8
TRIAL = ['dive_0025']     # 第 2 轮：只重试震频器（改成机械特征 + 防产品图条款）


def post(url, body):
    h = {'Authorization': 'Bearer ' + KEY, 'Content-Type': 'application/json',
         'X-DashScope-Async': 'enable'}
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


def wait_batch_idle(stable_sec=90, max_min=40):
    """等 art/versions 的文件数连续 stable_sec 秒不变 → 认为批次跑完。"""
    t0 = time.time()
    last, last_change = -1, time.time()
    while time.time() - t0 < max_min * 60:
        n = len(list(VERS.glob('*.webp')))
        if n != last:
            last, last_change = n, time.time()
            print('  [等] 已有 %d 张，继续观察…' % n, flush=True)
        elif time.time() - last_change >= stable_sec:
            print('  [等] 已稳定 %d 秒（%d 张），开始试点' % (stable_sec, n), flush=True)
            return True
        time.sleep(15)
    print('  [等] 超时，直接开跑', flush=True)
    return False


def gen_one(aid, prompt):
    out = VERS / ('%s_v%d.webp' % (aid, VER))
    if out.exists():
        print('  %s 已有 v%d，跳过' % (aid, VER), flush=True)
        return ('skip', aid)
    st, d = -1, {}
    for wait in (0, 6, 18, 40, 60):
        if wait:
            time.sleep(wait)
        st, d = post('https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis', {
            'model': MODEL,
            'input': {'prompt': prompt},
            'parameters': {'size': '1024*1024', 'n': 1, 'prompt_extend': False},
        })
        if st == 200:
            break
        print('    submit %s，退避 %ds' % (st, wait), flush=True)
        if st != 429:
            break
    if st != 200:
        return ('fail', aid, str(d.get('code') or d.get('err') or st)[:60])
    tid = (d.get('output') or {}).get('task_id')
    if not tid:
        return ('fail', aid, 'no tid')
    for _ in range(140):
        time.sleep(2.5)
        st2, d2 = get('https://dashscope.aliyuncs.com/api/v1/tasks/' + tid)
        o = (d2.get('output') or {}) if st2 == 200 else {}
        s = o.get('task_status')
        if s == 'SUCCEEDED':
            url = ((o.get('results') or [{}])[0]).get('url')
            if not url:
                return ('fail', aid, 'no url')
            try:
                png = RAW / ('%s_v%d.png' % (aid, VER))
                png.parent.mkdir(parents=True, exist_ok=True)
                png.write_bytes(urllib.request.urlopen(url, timeout=180).read())
                from PIL import Image
                im = Image.open(png).convert('RGB')
                im.thumbnail((768, 768), Image.LANCZOS)
                out.parent.mkdir(parents=True, exist_ok=True)
                im.save(out, 'WEBP', quality=82, method=6)
                return ('ok', aid, str(out))
            except Exception as e:
                return ('fail', aid, 'save %s' % str(e)[:70])
        if s in ('FAILED', 'CANCELED', 'UNKNOWN'):
            return ('fail', aid, str(o.get('message') or s)[:70])
    return ('fail', aid, 'timeout')


def main():
    prompts = json.loads((GAME / 'data' / 'zh_prompts_tech.json').read_text(encoding='utf-8'))
    ids = [i for i in TRIAL if i in prompts]
    print('试点 %d 张：%s' % (len(ids), ', '.join(ids)), flush=True)
    wait_batch_idle()
    ok = fail = 0
    for i in ids:
        print('  生成 %s …' % i, flush=True)
        r = gen_one(i, prompts[i])
        print('   → %s' % (r,), flush=True)
        if r[0] == 'ok':
            ok += 1
        elif r[0] == 'fail':
            fail += 1
    print('\n试点完成：成功 %d，失败 %d' % (ok, fail), flush=True)
    print('看这里：art/versions/%s_v%d.webp' % (ids[0], VER), flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
