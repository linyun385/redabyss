# -*- coding: utf-8 -*-
"""批量生成每素材的备选版本（v1、v2），写进 art/versions/。

为什么要单独一个脚本而不改 wanx_gen.py：
  wanx_gen 固定把结果写到 web/assets/art/<id>.webp（会覆盖现用图），
  这里要的是「新增备选、不动现用图」，输出到 art/versions/<id>_vN.webp，
  正好被 tools/pick_studio.py 读出来并在同一张卡片里并排显示。

断点续跑：已存在的版本跳过，随时可以再跑一次接着做。
用法：
  python tools/gen_versions.py                 # 全部 461 条 × 2 版
  python tools/gen_versions.py --limit 20      # 只做前 20 条（试跑）
  python tools/gen_versions.py --only trem_0001,dive_0023
  python tools/gen_versions.py --workers 4
"""
import argparse
import json
import sys
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
WS = Path(r'C:\Users\Administrator\Documents\deepseek-harness\default-workspace')
GAME = Path(__file__).resolve().parents[1]
RAW = GAME / 'art' / 'versions_raw'
VERS = GAME / 'art' / 'versions'
PROG = GAME / 'data' / 'gen_progress.json'
KEY = json.loads((WS / 'tools' / 'free_llm_keys.json').read_text(encoding='utf-8'))['DASHSCOPE_API_KEY']
MODEL = 'wanx2.1-t2i-turbo'
VERSIONS = [1, 2]        # 每条生成几个备选

_lock = threading.Lock()
_done = {'ok': 0, 'fail': 0, 'skip': 0, 't0': time.time()}
_abort = threading.Event()   # 账号级硬失败（欠费/鉴权）时立刻停手，别空烧
_abort_reason = ['']


def _hard_fail(d):
    """百炼返回的业务 code 里，哪些属于「再试也没用，还会烧完剩下全部请求」。"""
    code = str(d.get('code') or '')
    msg = str(d.get('message') or '').lower()
    if code in ('Arrearage', 'InvalidApiKey', 'Unauthorized', 'AccessDenied'):
        return code or 'denied'
    if 'overdue-payment' in msg or 'not in good standing' in msg:
        return code or 'arrearage'
    return ''


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


def gen_one(aid, v, prompt):
    out = VERS / ('%s_v%d.webp' % (aid, v))
    if out.exists():
        return ('skip', aid, v)
    if _abort.is_set():
        return ('skip', aid, v)
    t0 = time.time()
    # 提交阶段：429 是账号级限流（实测 4 并发全被拒），退避重试
    st, d = -1, {}
    for attempt, wait in enumerate([0, 6, 18, 40]):
        if wait:
            time.sleep(wait)
        st, d = post('https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis', {
            'model': MODEL,
            'input': {'prompt': prompt},
            'parameters': {'size': '1024*1024', 'n': 1, 'prompt_extend': False},
        })
        if st == 200:
            break
        if st != 429:
            break
    if st != 200:
        hard = _hard_fail(d)
        if hard:
            with _lock:
                if not _abort.is_set():
                    _abort_reason[0] = '%s %s' % (hard, str(d.get('message') or '')[:80])
            _abort.set()
        code = str(d.get('code') or '') or str(d.get('err') or '')
        msg = str(d.get('message') or '')[:70]
        return ('fail', aid, v, ('submit %s %s %s' % (st, code, msg)).strip())
    tid = (d.get('output') or {}).get('task_id')
    if not tid:
        return ('fail', aid, v, 'no tid')
    for _ in range(140):
        time.sleep(2.5)
        st2, d2 = get('https://dashscope.aliyuncs.com/api/v1/tasks/' + tid)
        o = (d2.get('output') or {}) if st2 == 200 else {}
        s = o.get('task_status')
        if s == 'SUCCEEDED':
            url = ((o.get('results') or [{}])[0]).get('url')
            if not url:
                return ('fail', aid, v, 'no url')
            try:
                png = RAW / ('%s_v%d.png' % (aid, v))
                png.parent.mkdir(parents=True, exist_ok=True)
                png.write_bytes(urllib.request.urlopen(url, timeout=180).read())
                from PIL import Image
                im = Image.open(png).convert('RGB')
                im.thumbnail((768, 768), Image.LANCZOS)
                out.parent.mkdir(parents=True, exist_ok=True)
                im.save(out, 'WEBP', quality=82, method=6)
                return ('ok', aid, v, time.time() - t0)
            except Exception as e:
                return ('fail', aid, v, 'save %s' % str(e)[:80])
        if s in ('FAILED', 'CANCELED', 'UNKNOWN'):
            return ('fail', aid, v, str(o.get('message') or s)[:100])
    return ('fail', aid, v, 'timeout')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--limit', type=int, default=0)
    ap.add_argument('--only', default='')
    ap.add_argument('--workers', type=int, default=1)
    a = ap.parse_args()

    cat = json.loads((GAME / 'data' / 'art_catalog.json').read_text(encoding='utf-8'))
    P = {r['id']: r['prompt'] for r in json.loads((GAME / 'data' / 'zh_prompts_full.json').read_text(encoding='utf-8'))}
    ids = [r['id'] for r in cat]
    if a.only:
        keep = {x.strip() for x in a.only.split(',') if x.strip()}
        ids = [i for i in ids if i in keep]
    if a.limit:
        ids = ids[:a.limit]

    jobs = [(i, v) for i in ids for v in VERSIONS]
    todo = [(i, v) for i, v in jobs if not (VERS / ('%s_v%d.webp' % (i, v))).exists()]
    print('素材 %d 条 × %d 版 = %d 张；已存在 %d 张；本次要做 %d 张'
          % (len(ids), len(VERSIONS), len(jobs), len(jobs) - len(todo), len(todo)), flush=True)
    if not todo:
        print('没有要做的了。')
        return 0
    print('并发 %d，预计 %d–%d 分钟' % (a.workers,
          len(todo) * 8 // a.workers // 60, len(todo) * 15 // a.workers // 60), flush=True)

    fails = []
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs = {ex.submit(gen_one, i, v, P.get(i, '')): (i, v) for i, v in todo}
        n = 0
        for f in as_completed(futs):
            r = f.result()
            n += 1
            with _lock:
                if r[0] == 'ok':
                    _done['ok'] += 1
                elif r[0] == 'fail':
                    _done['fail'] += 1
                    fails.append(r)
                else:
                    _done['skip'] += 1
            if n % 10 == 0 or r[0] == 'fail':
                el = time.time() - _done['t0']
                rate = n / el if el else 0
                left = (len(todo) - n) / rate / 60 if rate else 0
                print('[%d/%d] ok=%d fail=%d | %.1f 张/分 | 剩约 %.0f 分 %s'
                      % (n, len(todo), _done['ok'], _done['fail'], rate * 60, left,
                         '' if r[0] == 'ok' else str(r)), flush=True)
    el = time.time() - _done['t0']
    print('\n完成：成功 %d，失败 %d，跳过 %d，用时 %.1f 分钟'
          % (_done['ok'], _done['fail'], _done['skip'], el / 60), flush=True)
    if _abort.is_set():
        print('\n*** 账号级硬失败，已提前停手：%s' % _abort_reason[0], flush=True)
        print('*** 这不是提示词的问题 —— 去阿里云控制台看费用/欠费状态。', flush=True)
    if fails:
        (GAME / 'data' / 'gen_failed.json').write_text(
            json.dumps([{'id': x[1], 'v': x[2], 'err': x[3]} for x in fails], ensure_ascii=False, indent=1),
            encoding='utf-8')
        print('失败明细 → data/gen_failed.json（重跑同一命令会只补失败的）', flush=True)
    (PROG).write_text(json.dumps({'ok': _done['ok'], 'fail': _done['fail'], 'skip': _done['skip'],
                                  'total': len(todo), 'minutes': round(el / 60, 1),
                                  'at': time.strftime('%Y-%m-%d %H:%M:%S')},
                                 ensure_ascii=False, indent=1), encoding='utf-8')
    return 0


if __name__ == '__main__':
    sys.exit(main())
