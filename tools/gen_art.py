#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""本地生图工具：封装 ComfyUI HTTP API，供 GLM 批量调用。

用法：
  python tools/gen_art.py --probe                      # 检查环境（torch/模型/ComfyUI 是否就绪）
  python tools/gen_art.py --prompt "..." --out x.png   # 生成一张
  python tools/gen_art.py --batch plan.json            # 批量（每项含 prompt/out/width/height）
  python tools/gen_art.py --check art/                 # 检查目录里的图（尺寸/非空白）

设计原则：
  - 所有机械验证都能自动做（尺寸、文件大小、像素方差）
  - 风格好不好看，本工具判断不了，会输出 NEEDS_HUMAN_REVIEW
  - 找不到 ComfyUI 时报明确错误，不静默失败
"""
import sys, io, os, json, time, argparse, subprocess, urllib.request, urllib.error, urllib.parse
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

COMFY = Path(r'D:\ComfyUI')
API = 'http://127.0.0.1:8188'
DEFAULT_CKPT = 'sd_xl_base_1.0.safetensors'


def log(m):
    print(m, flush=True)


def http_json(url, data=None, timeout=30):
    req = urllib.request.Request(url, data=data)
    if data is not None:
        req.add_header('Content-Type', 'application/json')
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode('utf-8'))


def comfy_alive():
    try:
        http_json(API + '/system_stats', timeout=3)
        return True
    except Exception:
        return False


def start_comfy(wait=180):
    """启动 ComfyUI 并等它就绪。"""
    if comfy_alive():
        return True
    log('启动 ComfyUI...')
    py = sys.executable
    subprocess.Popen([py, 'main.py', '--listen', '127.0.0.1', '--port', '8188'],
                     cwd=str(COMFY),
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    t0 = time.time()
    while time.time() - t0 < wait:
        time.sleep(3)
        if comfy_alive():
            log('ComfyUI 就绪（%ds）' % int(time.time() - t0))
            return True
    log('ComfyUI 启动超时')
    return False


def build_workflow(prompt, negative, out_name, width, height, steps, cfg, ckpt, seed):
    """SDXL 文生图，API 格式。"""
    return {
        "4": {"class_type": "CheckpointLoaderSimple",
              "inputs": {"ckpt_name": ckpt}},
        "6": {"class_type": "CLIPTextEncode",
              "inputs": {"text": prompt, "clip": ["4", 1]}},
        "7": {"class_type": "CLIPTextEncode",
              "inputs": {"text": negative, "clip": ["4", 1]}},
        "5": {"class_type": "EmptyLatentImage",
              "inputs": {"width": width, "height": height, "batch_size": 1}},
        "3": {"class_type": "KSampler",
              "inputs": {"seed": seed, "steps": steps, "cfg": cfg,
                         "sampler_name": "euler_ancestral",
                         "scheduler": "normal", "denoise": 1.0,
                         "model": ["4", 0], "positive": ["6", 0],
                         "negative": ["7", 0], "latent_image": ["5", 0]}},
        "8": {"class_type": "VAEDecode",
              "inputs": {"samples": ["3", 0], "vae": ["4", 2]}},
        "9": {"class_type": "SaveImage",
              "inputs": {"filename_prefix": out_name, "images": ["8", 0]}},
    }


def wait_result(pid, timeout=300):
    t0 = time.time()
    while time.time() - t0 < timeout:
        time.sleep(2)
        try:
            h = http_json('%s/history/%s' % (API, pid))
        except Exception:
            continue
        if pid in h:
            return h[pid]
    return None


def fetch_image(info, dest):
    """把生成结果下载到 dest。"""
    outs = info.get('outputs', {})
    for node in outs.values():
        for img in node.get('images', []):
            q = '?filename=%s&subfolder=%s&type=%s' % (
                urllib.parse.quote(img['filename']),
                urllib.parse.quote(img.get('subfolder', '')),
                img.get('type', 'output'))
            with urllib.request.urlopen(API + '/view' + q, timeout=60) as r:
                data = r.read()
            Path(dest).parent.mkdir(parents=True, exist_ok=True)
            Path(dest).write_bytes(data)
            return len(data)
    return 0


def verify_image(path):
    """机械验证：能不能解码、尺寸、是不是空白。"""
    try:
        from PIL import Image
        import numpy as np
        im = Image.open(path)
        a = np.array(im.convert('L'))
        var = float(a.var())
        return {'ok': True, 'w': im.width, 'h': im.height,
                'kb': round(os.path.getsize(path) / 1024, 1),
                'var': round(var, 1),
                'blank': var < 30}
    except Exception as e:
        return {'ok': False, 'err': str(e)[:100]}


def gen_one(prompt, negative, out, width, height, steps, cfg, ckpt, seed):
    if not start_comfy():
        return {'ok': False, 'err': 'ComfyUI 起不来'}
    name = Path(out).stem
    wf = build_workflow(prompt, negative, name, width, height, steps, cfg, ckpt, seed)
    try:
        r = http_json(API + '/prompt', data=json.dumps({'prompt': wf}).encode('utf-8'))
    except urllib.error.HTTPError as e:
        return {'ok': False, 'err': '提交失败 %s: %s' % (e.code, e.read().decode('utf-8', 'replace')[:300])}
    pid = r.get('prompt_id')
    if not pid:
        return {'ok': False, 'err': '没有 prompt_id: %s' % r}
    info = wait_result(pid)
    if not info:
        return {'ok': False, 'err': '等待超时'}
    n = fetch_image(info, out)
    if not n:
        return {'ok': False, 'err': '没有输出图片'}
    v = verify_image(out)
    v['path'] = str(out)
    return v


def cmd_probe():
    log('=== 环境检查 ===')
    log('ComfyUI 目录: %s  %s' % (COMFY, 'OK' if COMFY.exists() else '缺失'))
    try:
        import torch
        log('torch: %s | cuda: %s' % (torch.__version__, torch.cuda.is_available()))
        if torch.cuda.is_available():
            log('GPU: %s' % torch.cuda.get_device_name(0))
    except Exception as e:
        log('torch 不可用: %s' % str(e)[:100])
    ck = COMFY / 'models' / 'checkpoints' / DEFAULT_CKPT
    log('模型 %s: %s' % (DEFAULT_CKPT,
                        '%.2f GB' % (ck.stat().st_size / 1024**3) if ck.exists() else '缺失'))
    log('ComfyUI 服务: %s' % ('运行中' if comfy_alive() else '未启动'))
    ok = ck.exists() and comfy_alive()
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--probe', action='store_true')
    ap.add_argument('--prompt')
    ap.add_argument('--negative', default='')
    ap.add_argument('--out')
    ap.add_argument('--batch')
    ap.add_argument('--check')
    ap.add_argument('--width', type=int, default=832)
    ap.add_argument('--height', type=int, default=1216)
    ap.add_argument('--steps', type=int, default=28)
    ap.add_argument('--cfg', type=float, default=7.0)
    ap.add_argument('--ckpt', default=DEFAULT_CKPT)
    ap.add_argument('--seed', type=int, default=-1)
    a = ap.parse_args()

    if a.seed < 0:
        a.seed = int(time.time() * 1000) % (2**31)

    if a.probe:
        return cmd_probe()

    if a.check:
        d = Path(a.check)
        files = sorted(list(d.rglob('*.png')) + list(d.rglob('*.webp')))
        log('检查 %d 个文件' % len(files))
        bad = 0
        for f in files:
            v = verify_image(f)
            if not v.get('ok') or v.get('blank'):
                log('  BAD  %s  %s' % (f.name, v))
                bad += 1
            else:
                log('  ok   %-40s %dx%d  %.0fKB  var=%.0f' %
                    (f.name, v['w'], v['h'], v['kb'], v['var']))
        log('')
        log('结果：%d 张，%d 张有问题' % (len(files), bad))
        log('NOTE: 本检查只看尺寸与是否空白，**不判断风格**。风格需人工/多模态复核。')
        return 0 if bad == 0 else 1

    if a.batch:
        plan = json.loads(Path(a.batch).read_text(encoding='utf-8'))
        ok = 0
        for i, it in enumerate(plan):
            log('[%d/%d] %s' % (i + 1, len(plan), it.get('out')))
            r = gen_one(it.get('prompt', ''), it.get('negative', a.negative),
                        it['out'], it.get('width', a.width), it.get('height', a.height),
                        it.get('steps', a.steps), it.get('cfg', a.cfg),
                        it.get('ckpt', a.ckpt), it.get('seed', a.seed + i))
            log('   -> %s' % r)
            if r.get('ok') and not r.get('blank'):
                ok += 1
        log('')
        log('批量完成：%d/%d 成功且非空白' % (ok, len(plan)))
        log('NEEDS_HUMAN_REVIEW: 风格需人工确认')
        return 0 if ok == len(plan) else 1

    if a.prompt and a.out:
        r = gen_one(a.prompt, a.negative, a.out, a.width, a.height,
                    a.steps, a.cfg, a.ckpt, a.seed)
        log(json.dumps(r, ensure_ascii=False, indent=2))
        return 0 if r.get('ok') and not r.get('blank') else 1

    ap.print_help()
    return 2


if __name__ == '__main__':
    sys.exit(main())
