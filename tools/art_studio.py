# -*- coding: utf-8 -*-
"""红渊 · 素材工作台（审图 / 重生成 / 标记回队）

启动：
    cd C:\\Users\\Administrator\\Desktop\\杂七杂八\\红渊\\game
    python tools\\art_studio.py
浏览器打开 http://127.0.0.1:8770

四件事：
  1) 看全部素材（缩略图 + 生态 + 对应对象 + 这些对象的原文，方便对照）
  2) 每张都能改 prompt / negative / 宽高 / seed →「重新生成并替换」
  3) 也可以「上传图片替换」（png/jpg/webp，自动转 webp + 长边 768）
  4) **标记不合格**（写 art/_rework.json）—— 标记的会进「重生成队列」，
     夜间脚本 tools/night_gen.py 下一轮优先重跑这些 id

判定标准（docs/art/ART_DIRECTION_V2.md）：不看文字，3 秒内能否认出“这是什么东西”。
"""
import base64
import json
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from PIL import Image

GAME = Path(__file__).resolve().parents[1]
TOOLS = GAME / 'tools'
ART = GAME / 'web' / 'assets' / 'art'
MANIFEST = TOOLS / 'art_manifest.json'
REWORK = GAME / 'art' / '_rework.json'
PORT = 8770

STATE = {'busy': False, 'last': '', 'log': []}
sys.path.insert(0, str(TOOLS))


def load_json(p, default):
    try:
        return json.loads(Path(p).read_text(encoding='utf-8'))
    except Exception:
        return default


def save_json(p, obj):
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    Path(p).write_text(json.dumps(obj, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')


def prompt_text(e):
    p = e.get('prompt')
    if isinstance(p, dict):
        return ' '.join(x for x in (p.get('prefix'), p.get('obj'), p.get('suffix')) if x)
    return str(p or '')


def load_object_texts():
    import gen_art_map as gm
    out = {}
    for c in gm.load_cards():
        out[c.get('id')] = {'name': c.get('name', ''), 'kind': '卡牌',
                            'text': (c.get('flavor') or '')}
    for e in gm.load_enemies():
        out[e.get('id')] = {'name': e.get('name', ''), 'kind': '敌人',
                            'text': (e.get('flavor') or '')}
    return out


def build_items():
    m = load_json(MANIFEST, {'entries': []})
    rework = load_json(REWORK, {})
    texts = load_object_texts()
    import gen_art_map as gm
    items = {}
    for e in m.get('entries', []):
        aid = e['id']
        f = ART / (aid + '.webp')
        items[aid] = {
            'id': aid, 'eco': e.get('eco', ''), 'obj': e.get('obj', ''),
            'prompt': prompt_text(e), 'negative': e.get('negative', ''),
            'size': e.get('size') or [640, 936], 'seed': e.get('seed', 0),
            'file': 'assets/art/%s.webp' % aid, 'exists': f.exists(),
            'kb': round(f.stat().st_size / 1024, 1) if f.exists() else 0,
            'users': [], 'ctx': [], 'rework': rework.get(aid),
        }

    def add(aid, label, oid=None):
        if aid not in items:
            return
        items[aid]['users'].append(label)
        if oid and oid in texts and texts[oid]['text']:
            t = texts[oid]
            items[aid]['ctx'].append({'who': t['name'], 'kind': t['kind'], 'text': t['text']})

    for c in gm.load_cards():
        add(gm.card_art_id(c), '卡牌：%s' % c.get('name', '?'), c.get('id'))
    for e in gm.load_enemies():
        add(gm.foe_art_id(e), '敌人：%s' % e.get('name', '?'), e.get('id'))
    for cid, cn in [('diver', '下潜者'), ('tremor', '震语者'), ('cangmin', '疯先知'), ('anmin', '维护者')]:
        add('class_' + cid, '职业：' + cn)
    for eid, en in [('ending_watched', '被注视'), ('ending_averted', '移开眼'), ('ending_walked', '并肩')]:
        add('end_' + eid, '结局：' + en)
    return items


def orig_path(aid):
    m = load_json(MANIFEST, {'entries': []})
    for e in m.get('entries', []):
        if e['id'] == aid:
            return GAME / e['out'], tuple(e.get('size') or (640, 936))
    return None, (640, 936)


def sync_after(aid):
    r = subprocess.run([sys.executable, str(TOOLS / 'art_sync.py')], cwd=str(GAME),
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    STATE['log'].append('art_sync: ' + (r.stdout or r.stderr or '')[-300:])


def do_generate(aid, prompt, negative, w, h, seed):
    STATE['busy'] = True
    STATE['last'] = aid
    try:
        out, _ = orig_path(aid)
        if out is None:
            STATE['log'].append('未知 id: %s' % aid)
            return
        out.parent.mkdir(parents=True, exist_ok=True)
        cmd = [sys.executable, str(TOOLS / 'gen_art_diffusers.py'), '--raw',
               '--prompt', prompt, '--neg', negative or '', '--out', str(out),
               '--width', str(w), '--height', str(h), '--steps', '20', '--seed', str(seed)]
        vae = GAME / 'models' / 'sdxl-vae-fp16-fix.safetensors'
        if vae.exists():
            cmd += ['--vae', str(vae)]
        t0 = time.time()
        r = subprocess.run(cmd, cwd=str(GAME), capture_output=True, text=True,
                           encoding='utf-8', errors='replace')
        STATE['log'].append('生成 %s 用时 %.0fs rc=%d' % (aid, time.time() - t0, r.returncode))
        if '疑似黑图' in (r.stdout or ''):
            STATE['log'].append('!! 黑图，已判失败')
        if r.returncode != 0:
            STATE['log'].append((r.stderr or '')[-400:])
        sync_after(aid)
    finally:
        STATE['busy'] = False


def do_upload(aid, dataurl):
    try:
        head, b64 = dataurl.split(',', 1)
        raw = base64.b64decode(b64)
        out, _ = orig_path(aid)
        out.parent.mkdir(parents=True, exist_ok=True)
        tmp = out.with_suffix('.upload.png')
        tmp.write_bytes(raw)
        im = Image.open(tmp).convert('RGB')
        im.thumbnail((768, 768), Image.LANCZOS)
        im.save(out, 'WEBP', quality=86, method=6)
        tmp.unlink(missing_ok=True)
        STATE['log'].append('上传替换 %s（%d KB）' % (aid, len(raw) // 1024))
        sync_after(aid)
    except Exception as ex:
        STATE['log'].append('上传失败: %s' % ex)


PAGE = r"""<!doctype html><html lang="zh-CN"><meta charset="utf-8">
<title>红渊 · 素材工作台</title>
<style>
:root{--bg:#14181d;--pan:#1c2229;--ink:#dfe4e8;--dim:#8b96a1;--red:#c8442f;--line:#2b333b;--warn:#d6a13a}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:13px/1.6 system-ui,"Microsoft YaHei",sans-serif}
header{position:sticky;top:0;background:#10141a;border-bottom:1px solid var(--line);padding:8px 14px;display:flex;gap:10px;align-items:center;z-index:5;flex-wrap:wrap}
header b{color:var(--red)} .st{color:var(--dim)}
.chip{cursor:pointer;border:1px solid var(--line);border-radius:14px;padding:2px 10px;color:var(--dim)}
.chip.on{background:var(--red);color:#fff;border-color:var(--red)}
main{display:grid;grid-template-columns:440px 1fr;gap:14px;padding:14px}
#list{display:grid;grid-template-columns:repeat(auto-fill,minmax(96px,1fr));gap:6px;max-height:calc(100vh - 96px);overflow:auto}
.thumb{border:1px solid var(--line);border-radius:4px;overflow:hidden;cursor:pointer;background:#0d1116}
.thumb img{width:100%;height:76px;object-fit:cover;display:block}
.thumb span{display:block;font-size:10px;color:var(--dim);padding:1px 3px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.thumb.sel{outline:2px solid var(--red)} .thumb.mark{outline:2px solid var(--warn)}
#work{background:var(--pan);border:1px solid var(--line);border-radius:6px;padding:12px;max-height:calc(100vh - 96px);overflow:auto}
#work h2{margin:0 0 6px;font-size:15px} .meta{color:var(--dim);font-size:12px;margin-bottom:8px;white-space:pre-wrap}
#prev{width:100%;max-height:42vh;object-fit:contain;background:#0b0e12;border:1px solid var(--line);border-radius:4px}
label{display:block;margin:8px 0 3px;color:var(--dim);font-size:12px}
textarea,input{width:100%;background:#0e1216;color:var(--ink);border:1px solid var(--line);border-radius:4px;padding:6px;font:12px/1.5 ui-monospace,Consolas,monospace}
.row{display:flex;gap:8px}.row>*{flex:1}
button{background:var(--red);color:#fff;border:0;border-radius:4px;padding:8px 14px;cursor:pointer;font-size:13px}
button.ghost{background:#232b33} button.warn{background:var(--warn);color:#1a1a1a} button:disabled{opacity:.45}
#log{margin-top:8px;color:var(--dim);font:11px/1.5 ui-monospace,monospace;white-space:pre-wrap;max-height:110px;overflow:auto}
.ctx{border-left:2px solid var(--line);padding:4px 0 4px 8px;margin:6px 0;font-size:12px;color:#c3cbd2}
.ctx b{color:#e8edf1}
</style>
<header><b>红渊 · 素材工作台</b><span class="st" id="st">就绪</span>
<span class="chip on" data-f="all">全部</span><span class="chip" data-f="face_">卡面</span>
<span class="chip" data-f="enemy_">敌人</span><span class="chip" data-f="event_">事件</span>
<span class="chip" data-f="class_">职业</span><span class="chip" data-f="end_">结局</span>
<span class="chip" data-f="mark">只看已标记（<span id="mk">0</span>）</span>
<span class="st">判定：3 秒内能不能认出“这是什么”</span></header>
<main><div id="list"></div><div id="work"><h2>选一张图</h2><div class="meta">左侧点缩略图。右侧会列出这张图对应的卡牌/怪物原文，方便对照。</div></div></main>
<script>
let ITEMS={},CUR=null,FILTER='all';
const $=s=>document.querySelector(s);
async function load(){
  const r=await fetch('/api/items');ITEMS=await r.json();
  $('#st').textContent=Object.keys(ITEMS).length+' 张素材';
  $('#mk').textContent=Object.values(ITEMS).filter(i=>i.rework).length;
  render();
}
function render(){
  const list=$('#list');list.innerHTML='';
  Object.values(ITEMS).sort((a,b)=>a.id.localeCompare(b.id)).forEach(it=>{
    if(FILTER==='mark'? !it.rework : (FILTER!=='all' && !it.id.startsWith(FILTER))) return;
    const d=document.createElement('div');
    d.className='thumb'+(it.rework?' mark':'')+(CUR&&CUR.id===it.id?' sel':'');
    d.dataset.id=it.id;
    d.innerHTML='<img src="/img/'+it.id+'.webp?t='+Date.now()+'"><span>'+it.id+'</span>';
    d.onclick=()=>select(it.id);list.appendChild(d);
  });
}
function esc(s){return (s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;')}
function select(id){
  CUR=ITEMS[id];render();
  const ctxs=(CUR.ctx||[]).map(c=>'<div class="ctx"><b>'+c.kind+'：'+esc(c.who)+'</b><br>'+esc(c.text)+'</div>').join('');
  $('#work').innerHTML=
    '<h2>'+id+'</h2>'+
    '<div class="meta">生态：'+(CUR.eco||'-')+'　对象：'+(CUR.obj||'-')+'　'+CUR.kb+'KB'+
    (CUR.rework?'\n<span style="color:var(--warn)">★ 已标记：'+esc(CUR.rework.note||'')+'</span>':'')+'</div>'+
    '<img id="prev" src="/img/'+id+'.webp?t='+Date.now()+'">'+
    '<div class="meta" style="margin-top:8px">对应对象（'+(CUR.users||[]).length+'）：'+((CUR.users||[]).join('、')||'（无）')+'</div>'+
    (ctxs||'<div class="meta">（没有对应的原文可对照）</div>')+
    '<label>不合格原因（标记时写，方便以后看为什么重做）</label><textarea id="note" rows="2" placeholder="例：不像怪物 / 太抽象 / 和卡名无关 / 构图太空">'+esc((CUR.rework&&CUR.rework.note)||'')+'</textarea>'+'<label>提示词 prompt</label><textarea id="p" rows="4">'+esc(CUR.prompt)+'</textarea>'+
    '<label>负面词 negative</label><textarea id="n" rows="2">'+esc(CUR.negative||'')+'</textarea>'+
    '<div class="row"><div><label>宽</label><input id="w" value="'+CUR.size[0]+'"></div>'+
    '<div><label>高</label><input id="h" value="'+CUR.size[1]+'"></div>'+
    '<div><label>种子 seed</label><input id="s" value="'+CUR.seed+'"></div></div><p></p>'+
    '<button id="gen">重新生成并替换</button> '+
    '<button class="ghost" id="up">上传替换…</button> '+
    '<button class="warn" id="mark">'+(CUR.rework?'取消标记':'标记不合格（进重生成队列）')+'</button>'+
    '<input type="file" id="file" accept="image/*" style="display:none"><div id="log"></div>';
  $('#gen').onclick=async()=>{
    const body={id:id,prompt:$('#p').value,negative:$('#n').value,w:+$('#w').value,h:+$('#h').value,seed:+$('#s').value};
    $('#gen').disabled=true;$('#log').textContent='生成中…';
    await fetch('/api/gen',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(body)});
    poll();
  };
  $('#up').onclick=()=>$('#file').click();
  $('#file').onchange=e=>{const f=e.target.files[0];if(!f)return;const rd=new FileReader();
    rd.onload=async()=>{$('#log').textContent='上传中…';
      await fetch('/api/upload',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({id:id,dataurl:rd.result})});poll();};
    rd.readAsDataURL(f);};
  $('#mark').onclick=async()=>{
    const note=($('#note')&&$('#note').value||'').trim();
    let url='/api/mark', payload={id:id,note:note};
    if(CUR.rework){url='/api/unmark';payload={id:id};}
    await fetch(url,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(payload)});
    await load();select(id);
  };
}
async function poll(){
  const r=await fetch('/api/status');const st=await r.json();
  $('#log').textContent=st.log.slice(-4).join('\n');
  $('#st').textContent=st.busy?('生成中：'+st.last):'就绪';
  if(st.busy){setTimeout(poll,1500);}
  else{const p=$('#prev');if(p&&CUR)p.src='/img/'+CUR.id+'.webp?t='+Date.now();if($('#gen'))$('#gen').disabled=false;}
}
document.querySelectorAll('.chip').forEach(c=>c.onclick=()=>{
  document.querySelectorAll('.chip').forEach(x=>x.classList.remove('on'));
  c.classList.add('on');FILTER=c.dataset.f;render();
});
load();
</script></html>"""


class H(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype='application/json; charset=utf-8'):
        if isinstance(body, str):
            body = body.encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass

    def do_GET(self):
        u = urlparse(self.path)
        if u.path == '/':
            return self._send(200, PAGE, 'text/html; charset=utf-8')
        if u.path == '/api/items':
            return self._send(200, json.dumps(build_items(), ensure_ascii=False))
        if u.path == '/api/status':
            return self._send(200, json.dumps(STATE, ensure_ascii=False))
        if u.path.startswith('/img/'):
            aid = Path(u.path[5:]).name.replace('.webp', '')
            f = ART / (aid + '.webp')
            if not f.exists():
                return self._send(404, 'not found', 'text/plain; charset=utf-8')
            return self._send(200, f.read_bytes(), 'image/webp')
        return self._send(404, 'not found')

    def do_POST(self):
        n = int(self.headers.get('Content-Length') or 0)
        data = json.loads(self.rfile.read(n) or b'{}')
        u = urlparse(self.path)
        if u.path == '/api/gen':
            if STATE['busy']:
                return self._send(409, json.dumps({'error': 'busy'}))
            threading.Thread(target=do_generate, daemon=True, args=(
                data.get('id'), data.get('prompt', ''), data.get('negative', ''),
                int(data.get('w') or 640), int(data.get('h') or 936),
                int(data.get('seed') or 0))).start()
            return self._send(200, json.dumps({'ok': True}))
        if u.path == '/api/upload':
            threading.Thread(target=do_upload, daemon=True,
                             args=(data.get('id'), data.get('dataurl', ''))).start()
            return self._send(200, json.dumps({'ok': True}))
        if u.path == '/api/mark':
            rw = load_json(REWORK, {})
            rw[data.get('id')] = {'note': data.get('note', ''),
                                  'when': time.strftime('%Y-%m-%d %H:%M:%S')}
            save_json(REWORK, rw)
            return self._send(200, json.dumps({'ok': True, 'count': len(rw)}))
        if u.path == '/api/unmark':
            rw = load_json(REWORK, {})
            rw.pop(data.get('id'), None)
            save_json(REWORK, rw)
            return self._send(200, json.dumps({'ok': True, 'count': len(rw)}))
        return self._send(404, 'not found')


def main():
    ART.mkdir(parents=True, exist_ok=True)
    print('素材工作台：http://127.0.0.1:%d' % PORT)
    print('素材目录：%s' % ART)
    print('标记文件：%s' % REWORK)
    ThreadingHTTPServer(('127.0.0.1', PORT), H).serve_forever()


if __name__ == '__main__':
    main()
