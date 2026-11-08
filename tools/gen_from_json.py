# -*- coding: utf-8 -*-
"""通用生成器：从任意 prompt json 生成指定版本号的候选图。

用法：
  python tools/gen_from_json.py --json data/zh_prompts_fix10.json --ver 3
  python tools/gen_from_json.py --json xxx.json --ver 3 --ids dive_0009,dive_0055

产出：art/versions/<id>_v<N>.webp
不覆盖任何现有图；已存在的版本自动跳过。
"""
import argparse
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
MODEL = 'wanx2.1-t2i-turbo'


def key():
    return json.loads((WS / 'tools' / 'free_llm_keys.json').read_text(encoding='utf-8'))['DASHSCOPE_API_KEY']


def post(url, body, K):
    h = {'Authorization': 'Bearer ' + K, 'Content-Type': 'application/json',
         'X-DashScope-Async': 'enable'}
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=h, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b'{}')
    except Exception as e:
        return -1, {'err': str(e)[:120]}


def get(url, K):
    req = urllib.request.Request(url, headers={'Authorization': 'Bearer ' + K})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b'{}')
    except Exception as e:
        return -1, {'err': str(e)[:120]}


def gen_one(aid, prompt, ver, K):
    out = VERS / ('%s_v%d.webp' % (aid, ver))
    if out.exists():
        return ('skip', aid)
    st, d, code, msg = -1, {}, '', ''
    for wait in (0, 6, 18, 40, 60):
        if wait:
            time.sleep(wait)
        st, d = post('https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis', {
            'model': MODEL,
            'input': {'prompt': prompt},
            'parameters': {'size': '1024*1024', 'n': 1, 'prompt_extend': False},
        }, K)
        if st == 200:
            break
        code = str(d.get('code') or '')
        msg = str(d.get('message') or d.get('err') or '')[:80]
        print('    submit %s %s %s' % (st, code, msg), flush=True)
        if st != 429:
            break
    if st != 200:
        return ('fail', aid, ('submit %s %s %s' % (st, code, msg)).strip())
    tid = (d.get('output') or {}).get('task_id')
    if not tid:
        return ('fail', aid, 'no tid')
    for _ in range(150):
        time.sleep(2.5)
        st2, d2 = get('https://dashscope.aliyuncs.com/api/v1/tasks/' + tid, K)
        o = (d2.get('output') or {}) if st2 == 200 else {}
        s = o.get('task_status')
        if s == 'SUCCEEDED':
            url = ((o.get('results') or [{}])[0]).get('url')
            if not url:
                return ('fail', aid, 'no url')
            try:
                png = RAW / ('%s_v%d.png' % (aid, ver))
                png.parent.mkdir(parents=True, exist_ok=True)
                png.write_bytes(urllib.request.urlopen(url, timeout=180).read())
                from PIL import Image
                im = Image.open(png).convert('RGB')
                im.thumbnail((768, 768), Image.LANCZOS)
                out.parent.mkdir(parents=True, exist_ok=True)
                im.save(out, 'WEBP', quality=82, method=6)
                return ('ok', aid)
            except Exception as e:
                return ('fail', aid, 'save %s' % str(e)[:70])
        if s in ('FAILED', 'CANCELED', 'UNKNOWN'):
            return ('fail', aid, str(o.get('message') or s)[:70])
    return ('fail', aid, 'timeout')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', required=True)
    ap.add_argument('--ver', type=int, required=True)
    ap.add_argument('--ids', default='')
    a = ap.parse_args()

    P = json.loads((GAME / a.json).read_text(encoding='utf-8'))
    P = {k: v for k, v in P.items() if not k.startswith('_')}
    ids = [i.strip() for i in a.ids.split(',') if i.strip()] or list(P)
    K = key()
    print('共 %d 张，版本 v%d，串行提交' % (len(ids), a.ver), flush=True)
    ok = fail = skip = 0
    t0 = time.time()
    for n, i in enumerate(ids, 1):
        if i not in P:
            print('  [%d/%d] %s 不在 json 里，跳过' % (n, len(ids), i), flush=True)
            continue
        r = gen_one(i, P[i], a.ver, K)
        print('  [%d/%d] %s → %s%s' % (n, len(ids), i, r[0],
                                       (' ' + str(r[1])) if len(r) > 1 and r[0] != 'ok' else ''), flush=True)
        if r[0] == 'ok':
            ok += 1
        elif r[0] == 'fail':
            fail += 1
            if len(r) > 1 and any(x in str(r[1]) for x in
                                  ('Arrearage', 'InvalidApiKey', 'Unauthorized', 'AccessDenied', 'overdue')):
                print('!! 硬错误，中止', flush=True)
                break
        else:
            skip += 1
    print('\n完成：成功 %d，失败 %d，跳过 %d，用时 %.1f 分钟'
          % (ok, fail, skip, (time.time() - t0) / 60), flush=True)
    return 0 if fail == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
