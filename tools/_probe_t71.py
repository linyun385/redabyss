# -*- coding: utf-8 -*-
"""T71 版式探针：在 iframe 里加载 index.html，模拟选职业 → 进地图 → 打开总图，
   逐个断言尺寸/图标/行程列表，并把截图存到 tools/_probe_*.png。

做法：生成一个同源探针页（web/_t71_probe.html），用 headless Chrome 截图；
      探针自己把断言结果写进 document.title 和页面上的 <pre id="out">，再从截图/DOM 里读。
"""
import re
import subprocess
import sys
import time
from pathlib import Path

GAME = Path(__file__).resolve().parents[1]
PROBE = GAME / 'web' / '_t71_probe.html'
CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
PORT = 8812

PROBE_HTML = r"""<!doctype html><meta charset="utf-8">
<style>html,body{margin:0;background:#111}#f{width:1280px;height:720px;border:0;display:block}
#out{position:fixed;left:0;bottom:0;color:#0f0;font:12px/1.4 monospace;background:#000c;padding:6px;white-space:pre;max-height:220px;overflow:auto}</style>
<iframe id="f" src="index.html?mapseed=777"></iframe><pre id="out">running...</pre>
<script>
const log = [];
function say(s){ log.push(s); }
async function main(){
  const f = document.getElementById('f');
  await new Promise(r => f.addEventListener('load', r, {once:true}));
  const d = f.contentDocument, w = f.contentWindow;
  // 1) 选职业
  const cls = d.querySelectorAll('.class-card, [data-class], button');
  let picked = false;
  for (const el of cls) { if ((el.getAttribute('data-class')||'') && el.click) { el.click(); picked = true; break; } }
  say('选职业: ' + (picked ? 'ok' : 'fail'));
  await new Promise(r => setTimeout(r, 900));
  // 2) 小图尺寸
  const dock = d.querySelector('#mm-dock');
  if (!dock) { say('mm-dock 不存在'); finish(); return; }
  const r = dock.getBoundingClientRect();
  say('小图 dock: ' + Math.round(r.width) + 'x' + Math.round(r.height));
  // 3) 地图区是否填满（空白率）
  const body = d.querySelector('#mm-body');
  if (body) { const rb = body.getBoundingClientRect(); say('地图区: ' + Math.round(rb.width) + 'x' + Math.round(rb.height)); }
  // 4) 行程列表
  const logRows = d.querySelector('#mm-log-rows');
  say('行程列表行数: ' + (logRows ? logRows.children.length : 'none'));
  // 5) 节点图标（看不到类型字段）
  const nodes = d.querySelectorAll('#mm-body svg [data-nid], #mm-body [data-nid]');
  const txt = [...nodes].slice(0, 40).map(n => (n.textContent||'').trim()).join('');
  say('节点数: ' + nodes.length + ' | 文本样本: ' + txt.slice(0, 60));
  say('禁字命中: ' + ('战事随商英'.split('').filter(c => txt.includes(c)).join('') || '无'));
  finish();
}
function finish(){
  document.getElementById('out').textContent = log.join('\n');
  document.title = 'PROBE:' + log.join(' | ');
}
main().catch(e => { document.getElementById('out').textContent = 'ERR ' + e.message; document.title='PROBE:ERR'; });
</script>
"""


def main():
    PROBE.write_text(PROBE_HTML, encoding='utf-8')
    srv = subprocess.Popen([sys.executable, '-m', 'http.server', str(PORT), '--bind', '127.0.0.1'],
                           cwd=str(GAME), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2.5)
    try:
        out = GAME / 'tools' / '_probe_t71.png'
        url = 'http://127.0.0.1:%d/web/_t71_probe.html' % PORT
        r = subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars',
                            '--window-size=1280,900', '--virtual-time-budget=9000',
                            '--screenshot=%s' % out, url],
                           capture_output=True, text=True, timeout=120)
        print('截图:', out, out.exists())
        # 再跑一次拿 DOM 文本
        r2 = subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--dump-dom',
                             '--virtual-time-budget=9000', url],
                            capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=120)
        m = re.search(r'<pre id="out">(.*?)</pre>', r2.stdout or '', re.S)
        print('--- 探针输出 ---')
        print((m.group(1) if m else '(没读到 out)')[:1200])
    finally:
        srv.terminate()


if __name__ == '__main__':
    main()
