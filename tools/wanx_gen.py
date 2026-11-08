# -*- coding: utf-8 -*-
"""百炼万相批量生图（中文提示词），产物直接进游戏素材目录。

为什么用它：
  · 10–20 秒/张（本地 SDXL 3–15 分钟）
  · 中文提示词直接可用，不用先翻英文（翻译会丢世界观）
  · 版画/排线质感一次就出（本地十几次没做出来）

用法：
  python tools\\wanx_gen.py --file data\\zh_prompts.json            # 跑文件里所有没生成的
  python tools\\wanx_gen.py --file data\\zh_prompts.json --only foe_x,card_y
  python tools\\wanx_gen.py --file data\\zh_prompts.json --dry

输入文件格式（JSON 数组）：
  [{"id": "foe_x", "prompt": "中文提示词……", "size": "1024*1024"}]

产出：
  · 原图  art\\_wanx\\<id>.png
  · 游戏用 web\\assets\\art\\<id>.webp（长边 768、q82）
  · 跑完自动跑 tools\\art_sync.py 重建 ART 表
"""
import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')
WS = Path(r'C:\Users\Administrator\Documents\deepseek-harness\default-workspace')
GAME = Path(__file__).resolve().parents[1]
RAW = GAME / 'art' / '_wanx'
WEB = GAME / 'web' / 'assets' / 'art'
LOG = GAME / 'tools' / 'wanx_run.json'
FAIL = GAME / 'tools' / 'wanx_failed.json'
KEY = json.loads((WS / 'tools' / 'free_llm_keys.json').read_text(encoding='utf-8'))['DASHSCOPE_API_KEY']
MODEL = 'wanx2.1-t2i-turbo'


def post(url, body, extra=None):
    h = {'Authorization': 'Bearer ' + KEY, 'Content-Type': 'application/json'}
    if extra:
        h.update(extra)
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=h, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b'{}')
    except Exception as e:
        return -1, {'err': str(e)[:150]}


def get(url):
    req = urllib.request.Request(url, headers={'Authorization': 'Bearer ' + KEY})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b'{}')
    except Exception as e:
        return -1, {'err': str(e)[:150]}


def gen_one(job):
    """提交 → 轮询 → 下载 → 转 webp。返回 (ok, 秒, 错误)。"""
    t0 = time.time()
    st, d = post('https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis', {
        'model': MODEL,
        'input': {'prompt': job['prompt']},
        # prompt_extend=False：默认的改写器会把主体改写成泛化洞穴/管道
        # （实测：第一批「一整片嗜热菌落」被改写成了管道钟乳）。见 docs/ART_PROMPT_SPEC.md 第六节。
        'parameters': {'size': job.get('size', '1024*1024'), 'n': 1,
                       'prompt_extend': job.get('prompt_extend', False)},
    }, {'X-DashScope-Async': 'enable'})
    tid = (d.get('output') or {}).get('task_id') if st == 200 else None
    if not tid:
        return False, time.time() - t0, '提交失败 %s %s' % (st, json.dumps(d, ensure_ascii=False)[:160])

    for _ in range(40):
        time.sleep(3)
        st2, d2 = get('https://dashscope.aliyuncs.com/api/v1/tasks/' + tid)
        o = d2.get('output') or {}
        s = o.get('task_status')
        if s == 'SUCCEEDED':
            url = (o.get('results') or [{}])[0].get('url')
            if not url:
                return False, time.time() - t0, '成功但无 URL'
            RAW.mkdir(parents=True, exist_ok=True)
            p = RAW / (job['id'] + '.png')
            p.write_bytes(urllib.request.urlopen(url, timeout=180).read())
            WEB.mkdir(parents=True, exist_ok=True)
            im = Image.open(p).convert('RGB')
            im.thumbnail((768, 768), Image.LANCZOS)
            im.save(WEB / (job['id'] + '.webp'), 'WEBP', quality=82, method=6)
            return True, time.time() - t0, ''
        if s in ('FAILED', 'CANCELED', 'UNKNOWN'):
            return False, time.time() - t0, '任务失败 %s' % json.dumps(o, ensure_ascii=False)[:200]
    return False, time.time() - t0, '轮询超时'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--file', required=True)
    ap.add_argument('--only', default='')
    ap.add_argument('--dry', action='store_true')
    ap.add_argument('--force', action='store_true', help='已存在的也重跑（默认跳过）')
    a = ap.parse_args()

    jobs = json.loads((GAME / a.file if not Path(a.file).is_absolute() else Path(a.file))
                      .read_text(encoding='utf-8'))
    if a.only:
        keep = {x.strip() for x in a.only.split(',') if x.strip()}
        jobs = [j for j in jobs if j['id'] in keep]
    todo = [j for j in jobs if a.force or not (WEB / (j['id'] + '.webp')).exists()]
    print('总 %d，已完成 %d，本次待跑 %d' % (len(jobs), len(jobs) - len(todo), len(todo)), flush=True)
    if a.dry:
        for j in todo:
            print('  将跑', j['id'], '|', j['prompt'][:40])
        return 0

    runs, fails = [], []
    for i, j in enumerate(todo, 1):
        ok, sec, err = gen_one(j)
        if not ok:
            print('  重试', j['id'], flush=True)
            ok, sec2, err = gen_one(j)
            sec += sec2
        runs.append({'id': j['id'], 'ok': ok, 'sec': round(sec, 1), 'err': err})
        if not ok:
            fails.append({'id': j['id'], 'err': err})
            FAIL.write_text(json.dumps(fails, ensure_ascii=False, indent=1), encoding='utf-8')
        print('[%d/%d] %-22s %s %5.1fs %s'
              % (i, len(todo), j['id'], 'ok' if ok else 'FAIL', sec, err[:60]), flush=True)
        LOG.write_text(json.dumps({'runs': runs}, ensure_ascii=False, indent=1), encoding='utf-8')

    ok_n = sum(1 for r in runs if r['ok'])
    print('\n完成 %d/%d，失败 %d，平均 %.1fs/张' %
          (ok_n, len(todo), len(fails), sum(r['sec'] for r in runs) / max(1, len(runs))))
    if ok_n:
        import subprocess
        print(subprocess.run([sys.executable, str(GAME / 'tools' / 'art_sync.py')],
                             cwd=str(GAME), capture_output=True, text=True,
                             encoding='utf-8', errors='replace').stdout[-200:])
    return 0


if __name__ == '__main__':
    sys.exit(main())
