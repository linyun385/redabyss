# -*- coding: utf-8 -*-
"""T71 版式探针 v2：选职业 → 小图断言 → 打开总图 → 滚动/缩放断言。
   结果写 JSON 文件（避免控制台编码问题），截图存 tools/_probe_*.png。"""
import json
import re
import subprocess
import sys
import time
from pathlib import Path

GAME = Path(__file__).resolve().parents[1]
PROBE = GAME / 'web' / '_t71_probe.html'
RESULT = GAME / 'tools' / '_probe_t71.json'
CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
PORT = 8813

PROBE_HTML = r"""<!doctype html><meta charset="utf-8">
<style>html,body{margin:0;background:#111}#f{width:1280px;height:720px;border:0;display:block}</style>
<iframe id="f" src="index.html?mapseed=777"></iframe>
<script>
const R = {};
const sleep = ms => new Promise(r => setTimeout(r, ms));
function dump(){ document.title = 'R:' + JSON.stringify(R); }
async function main(){
  const f = document.getElementById('f');
  await new Promise(r => f.addEventListener('load', r, {once:true}));
  const d = f.contentDocument, w = f.contentWindow;
  // 选职业
  let picked = false;
  for (const el of d.querySelectorAll('[data-class]')) { el.click(); picked = true; break; }
  R.picked = picked;
  await sleep(1000);
  const dock = d.querySelector('#mm-dock');
  R.dock = dock ? dock.getBoundingClientRect().toJSON() : null;
  const body = d.querySelector('#mm-body');
  R.body = body ? body.getBoundingClientRect().toJSON() : null;
  const rows = d.querySelector('#mm-log-rows');
  R.logRows = rows ? rows.children.length : -1;
  R.logText = rows ? rows.textContent.replace(/\s+/g,' ').slice(0,200) : '';
  // 节点文本
  const nodes = [...d.querySelectorAll('#mm-body [data-nid]')];
  R.nodeCount = nodes.length;
  R.nodeGlyphs = nodes.slice(0, 30).map(n => (n.textContent||'').trim()).join(' ');
  R.forbidden = '战事随商英'.split('').filter(c => R.nodeGlyphs.includes(c));
  // 打开总图
  const fullBtn = [...d.querySelectorAll('button')].find(b => (b.textContent||'').includes('总图'));
  R.fullBtn = !!fullBtn;
  if (fullBtn) { fullBtn.click(); await sleep(700); }
  const full = d.querySelector('#mm-fulllayer, #mm-full, .mm-full-layer');
  R.fullLayer = full ? true : Object.keys(d.querySelectorAll('*')).length;
  const scroller = full ? (full.querySelector('[data-mm-scroll], .mm-scroll, div') || full) : null;
  if (scroller) {
    R.scroll = { h: scroller.scrollHeight, ch: scroller.clientHeight, top0: scroller.scrollTop };
    scroller.scrollTop = 400;
    await sleep(120);
    R.scroll.top1 = scroller.scrollTop;
  }
  // 缩放按钮
  const zin = [...d.querySelectorAll('button')].find(b => (b.textContent||'').trim() === '+');
  const zout = [...d.querySelectorAll('button')].find(b => (b.textContent||'').trim() === '−');
  R.zoomBtns = { in: !!zin, out: !!zout };
  if (zin) { for (let i=0;i<4;i++){ zin.click(); await sleep(80); } }
  const svg = d.querySelector('#mm-fulllayer svg, .mm-full-layer svg');
  R.svgAfterZoom = svg ? svg.getBoundingClientRect().toJSON() : null;
  dump();
}
main().catch(e => { R.err = String(e); dump(); });
</script>
"""


def main():
    PROBE.write_text(PROBE_HTML, encoding='utf-8')
    srv = subprocess.Popen([sys.executable, '-m', 'http.server', str(PORT), '--bind', '127.0.0.1'],
                           cwd=str(GAME), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2.5)
    try:
        url = 'http://127.0.0.1:%d/web/_t71_probe.html' % PORT
        shot = GAME / 'tools' / '_probe_t71_full.png'
        subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars',
                        '--window-size=1280,760', '--virtual-time-budget=9000',
                        '--screenshot=%s' % shot, url],
                       capture_output=True, timeout=150)
        r2 = subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--dump-dom',
                             '--virtual-time-budget=9000', url],
                            capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=150)
        m = re.search(r'<title>R:(\{.*?\})</title>', r2.stdout or '', re.S)
        if not m:
            print('没拿到结果'); return
        data = json.loads(m.group(1).replace('&quot;', '"').replace('&amp;', '&'))
        RESULT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
        print('写到', RESULT)
        for k in ('picked', 'dock', 'body', 'logRows', 'nodeCount', 'forbidden', 'fullBtn', 'scroll', 'zoomBtns', 'svgAfterZoom'):
            print(k, '=', json.dumps(data.get(k), ensure_ascii=False)[:160])
        print('截图', shot, shot.exists())
    finally:
        srv.terminate()


if __name__ == '__main__':
    main()
