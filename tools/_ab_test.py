# -*- coding: utf-8 -*-
"""A/B 验证：加「无高光无灰阶」约束能不能治好「质感不对」。

背景：用户标了 77 条打回，其中 43 条理由是「质感不对」。看图对比后判断：
  万相对「金属 + 强红光」会走 3D/照片渲染，提示词尾部的「石版画、细密排线」压不住。
  而提示词层面的统计找不到差异（打回/采用两组的构图词、尾部词比例几乎一样），
  所以只能靠图像实证：同一 prompt，加一条显式排他约束，看出图是否变平。

设计：5 个被打回的金属题材 × 2 版
  A = 原提示词（对照组，重跑一次排除随机性）
  B = 原提示词 + 「无高光无灰阶」约束句
  两版都写进 art/versions/<id>_vN.webp，挑选台里同一张卡片并排显示。

  v0 = 旧图（web/assets/art）
  v1 = B 版（加约束）
  v2 = A 版（原提示词重跑）

用法：python tools/_ab_test.py [--dry]
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
AB = GAME / 'art' / 'ab'
VERS = GAME / 'art' / 'versions'
KEY = json.loads((WS / 'tools' / 'free_llm_keys.json').read_text(encoding='utf-8'))['DASHSCOPE_API_KEY']
MODEL = 'wanx2.1-t2i-turbo'

# 5 个被打回、且主体是金属的题材
PICK = ['trem_0001', 'trem_0035', 'trem_0051', 'dive_0023', 'dive_0033']

# 正向排他约束（万相不认负面词，全部写成「是什么」）
EXTRA = ('整幅画只用墨黑与血红两种色块，中间没有灰阶过渡；所有表面都是哑光的，'
         '没有高光，没有反光，没有金属亮斑；形体只靠硬边轮廓和排线分开，不靠明暗塑形。')


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


def gen(prompt, out_png):
    t0 = time.time()
    st, d = post('https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis', {
        'model': MODEL,
        'input': {'prompt': prompt},
        'parameters': {'size': '1024*1024', 'n': 1, 'prompt_extend': False},
    })
    if st != 200:
        return False, 0, 'submit %s %s' % (st, str(d)[:120])
    tid = (d.get('output') or {}).get('task_id')
    if not tid:
        return False, 0, 'no task_id'
    for _ in range(120):
        time.sleep(3)
        st2, d2 = get('https://dashscope.aliyuncs.com/api/v1/tasks/' + tid)
        o = (d2.get('output') or {}) if st2 == 200 else {}
        s = o.get('task_status')
        if s == 'SUCCEEDED':
            url = ((o.get('results') or [{}])[0]).get('url')
            if not url:
                return False, time.time() - t0, 'no url'
            out_png.parent.mkdir(parents=True, exist_ok=True)
            out_png.write_bytes(urllib.request.urlopen(url, timeout=180).read())
            return True, time.time() - t0, ''
        if s in ('FAILED', 'CANCELED', 'UNKNOWN'):
            return False, time.time() - t0, str(o.get('message') or s)[:120]
    return False, time.time() - t0, 'timeout'


def main():
    P = {r['id']: r['prompt'] for r in json.loads((GAME / 'data' / 'zh_prompts_full.json').read_text(encoding='utf-8'))}
    dry = '--dry' in sys.argv
    AB.mkdir(parents=True, exist_ok=True)
    VERS.mkdir(parents=True, exist_ok=True)
    log = []
    for aid in PICK:
        base = P.get(aid)
        if not base:
            print('缺 id', aid); continue
        jobs = [
            ('A', base, VERS / ('%s_v2.webp' % aid)),                 # 对照组：原提示词
            ('B', base.rstrip('。') + '。' + EXTRA, VERS / ('%s_v1.webp' % aid)),  # 实验组：加约束
        ]
        for tag, prompt, dest_webp in jobs:
            png = AB / ('%s_%s.png' % (aid, tag))
            print('%-10s %s  %s' % (aid, tag, '干跑' if dry else '生成中…'), flush=True)
            if dry:
                continue
            ok, sec, err = gen(prompt, png)
            if ok:
                from PIL import Image
                im = Image.open(png).convert('RGB')
                im.thumbnail((768, 768), Image.LANCZOS)
                im.save(dest_webp, 'WEBP', quality=82, method=6)
                print('  ok  %.1fs → %s' % (sec, dest_webp.name), flush=True)
                log.append({'id': aid, 'tag': tag, 'ok': True, 'sec': round(sec, 1), 'out': dest_webp.name})
            else:
                print('  FAIL %.1fs %s' % (sec, err), flush=True)
                log.append({'id': aid, 'tag': tag, 'ok': False, 'sec': round(sec, 1), 'err': err})
    if not dry:
        (GAME / 'art' / 'ab' / 'ab_log.json').write_text(json.dumps(log, ensure_ascii=False, indent=1), encoding='utf-8')
        ok = sum(1 for x in log if x['ok'])
        print('\n完成 %d/%d，耗时合计 %.0f 秒' % (ok, len(log), sum(x['sec'] for x in log)))
        print('挑选台里刷新即可看到：v0 旧图 / v1 加约束 / v2 原提示词重跑')
    return 0


if __name__ == '__main__':
    sys.exit(main())
