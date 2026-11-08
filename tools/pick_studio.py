# -*- coding: utf-8 -*-
"""pick_studio.py —— 素材挑选台（一素材多版本、点选采用、打回写理由）。

为什么重写而不用 art_studio.py：
  旧页面读的是 _manifest 的 607 条旧清单（face_eco_* / card_zh2_* 那批早废弃），
  数据源、提示词、图片路径三处都对不上，缩略图还全 404。修补不如重来。

数据源（全部是当前在用的）：
  data/art_catalog.json      461 条：id / kind / name / desc
  data/zh_prompts_full.json  461 条提示词
  web/assets/art/<id>.webp   每个素材的当前版本（v0）
  art/versions/<id>_v1.webp  将来批量生成的备选（v1、v2…按需出现）

选择记录：
  data/picks.json  { "<id>": {"chosen": 0, "rejected": [{"v":1,"reason":"..."}], "updated": "..."} }

用法：python tools/pick_studio.py [--port 8770]
"""
import argparse
import json
import sys
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse

sys.stdout.reconfigure(encoding='utf-8')
GAME = Path(__file__).resolve().parents[1]
ART = GAME / 'web' / 'assets' / 'art'
VERS = GAME / 'art' / 'versions'
PICKS = GAME / 'data' / 'picks.json'
CAT = GAME / 'data' / 'art_catalog.json'
PROMPTS = GAME / 'data' / 'zh_prompts_full.json'


def load(p, default):
    try:
        return json.loads(p.read_text(encoding='utf-8'))
    except Exception:
        return default


def save(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding='utf-8')


def versions_of(aid):
    """v0 = 当前 webp；v1.. = art/versions/<id>_vN.webp。返回存在的版本号列表。"""
    out = []
    if (ART / (aid + '.webp')).exists():
        out.append(0)
    if VERS.exists():
        for f in sorted(VERS.glob(aid + '_v*.webp')):
            try:
                n = int(f.stem.rsplit('_v', 1)[1])
            except Exception:
                continue
            out.append(n)
    return out


def build_items():
    cat = load(CAT, [])
    prompts = {r['id']: r.get('prompt', '') for r in load(PROMPTS, [])}
    picks = load(PICKS, {})
    items = []
    for r in cat:
        aid = r['id']
        vs = versions_of(aid)
        p = picks.get(aid, {})
        chosen = p.get('chosen')
        rejected = p.get('rejected', [])
        rej_vs = {x.get('v') for x in rejected}
        # 状态机：
        #   done  = 已选定（整张卡片退出待定视图）
        #   regen = 没选，且能看得的候选只剩 ≤1 张（全打回了/打回后剩一张又没选）→ 要重新生成
        #   open  = 还有 ≥2 张候选没被打回
        alive = [v for v in vs if v not in rej_vs]
        # 状态机：
        #   done  = 已选定（整张卡片退出待定视图，其余候选一并收起）
        #   regen = 没选，且已经到了「没得选」的地步：
        #             · 全被打回（alive 为 0），或
        #             · 本来有多张候选（>=2），被否到只剩最后 1 张又没选
        #           注意：只有 1 张、还没生成备选的，属于 open（等备选），不是 regen。
        if chosen is not None:
            state = 'done'
        elif len(alive) == 0:
            state = 'regen'
        elif len(vs) >= 2 and len(alive) <= 1:
            state = 'regen'
        else:
            state = 'open'
        items.append({
            'id': aid,
            'kind': aid.split('_')[0],
            'name': r.get('name', ''),
            'desc': r.get('desc', ''),
            'prompt': prompts.get(aid, ''),
            'versions': vs,
            'alive': alive,          # 还该显示的版本（打回的不再显示）
            'chosen': chosen,
            'confirmed': bool(p.get('confirmed')),
            'rejected': rejected,
            'state': state,
            'size_kb': round((ART / (aid + '.webp')).stat().st_size / 1024, 1) if (ART / (aid + '.webp')).exists() else None,
        })
    return items


PAGE = r"""<!doctype html><html lang="zh"><head><meta charset="utf-8">
<title>红渊 · 素材挑选台</title><style>
*{box-sizing:border-box}body{margin:0;background:#12141a;color:#dfe3ec;
 font:13px/1.6 "Microsoft YaHei",system-ui,sans-serif}
header{position:sticky;top:0;z-index:9;background:#181b23;border-bottom:1px solid #262b36;
 padding:10px 14px;display:flex;gap:10px;align-items:center;flex-wrap:wrap}
h1{font-size:15px;margin:0 8px 0 0;color:#ff5f5f;font-weight:600}
.chip{background:#20242e;border:1px solid #2c3240;color:#aeb6c6;border-radius:14px;
 padding:3px 11px;cursor:pointer;font-size:12px}
.chip.on{background:#c03030;border-color:#c03030;color:#fff}
.stat{margin-left:auto;color:#8b94a6;font-size:12px}
.stat b{color:#e8ecf4}
main{padding:14px;display:grid;gap:14px;grid-template-columns:repeat(auto-fill,minmax(300px,1fr))}
.card{background:#181b23;border:1px solid #262b36;border-radius:10px;overflow:hidden;display:flex;flex-direction:column}
.card.done{border-color:#2f6b45}
.card.regen{border-color:#7a5a1e}
.hint{padding:6px 10px;background:#2a2312;color:#e0c070;font-size:11px;border-top:1px solid #3a3118}
.rejline{padding:4px 10px;color:#b87070;font-size:11px}
.hd{padding:8px 10px;border-bottom:1px solid #222731;display:flex;gap:8px;align-items:baseline}
.hd .id{font-family:ui-monospace,Consolas,monospace;font-size:11px;color:#7d8798}
.hd .nm{font-size:13px;color:#e8ecf4;font-weight:600}
.hd .kb{margin-left:auto;font-size:11px;color:#5f6878}
.vs{display:flex;gap:6px;padding:8px;background:#14171e}
.vw{flex:1;position:relative;cursor:pointer}
.vw img{width:100%;aspect-ratio:1;object-fit:cover;border-radius:6px;display:block;
 border:2px solid transparent;background:#0d0f14}
.vw:hover img{border-color:#3a4356}
.vw.pick img{border-color:#3ecf72}
.vw.rej img{border-color:#c03030;opacity:.45}
.vw span{position:absolute;left:5px;top:5px;background:#000a;color:#fff;font-size:10px;
 padding:1px 5px;border-radius:4px}
.vw.empty{aspect-ratio:1;border:1px dashed #2c3240;border-radius:6px;display:flex;
 align-items:center;justify-content:center;color:#4b5464;font-size:11px}
.ft{padding:8px 10px;border-top:1px solid #222731;display:flex;gap:6px;flex-wrap:wrap;align-items:center}
.ft input{flex:1;min-width:90px;background:#0f1218;border:1px solid #2a3040;color:#dfe3ec;
 border-radius:6px;padding:4px 7px;font-size:12px}
.ft button{background:#242a36;border:1px solid #303747;color:#c6cede;border-radius:6px;
 padding:4px 10px;cursor:pointer;font-size:12px}
.ft button:hover{background:#2e3543}
.ft .ok{background:#1e5c37;border-color:#2a7a4a;color:#c8f0d8}
.ft .no{background:#5c1e1e;border-color:#7a2a2a;color:#f0c8c8}
#q{background:#0f1218;border:1px solid #2a3040;color:#dfe3ec;border-radius:6px;padding:4px 9px;font-size:12px;width:160px;margin-left:6px}
#q:focus{outline:none;border-color:#c03030}
.pr{padding:0 10px 8px;font-size:11px;color:#6d7688;max-height:64px;overflow:auto;
 font-family:ui-monospace,Consolas,monospace;line-height:1.5}
</style></head><body>
<header>
 <h1>红渊 · 素材挑选台</h1>
 <span class="chip on" data-f="open">待定</span>
 <span class="chip" data-f="regen">待重生成</span>
 <span class="chip" data-f="done">已选</span>
 <span class="chip" data-f="all">全部</span>
 <span class="chip" data-f="review">待复核</span>
 <span class="chip" data-f="anm">卡面·anm</span><span class="chip" data-f="cng">卡面·cng</span>
 <span class="chip" data-f="dive">卡牌·dive</span><span class="chip" data-f="trem">卡牌·trem</span>
 <span class="chip" data-f="enemy">敌人</span><span class="chip" data-f="event">事件</span>
 <input id="q" placeholder="搜 id / 名字">
 <span class="stat" id="stat"></span>
</header>
<main id="grid"></main>
<script>
let ITEMS=[],FILTER='open',Q='';
const KINDS=['anm','cng','dive','trem','enemy','event'];
const $=s=>document.querySelector(s);
function esc(s){return (s||'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]))}
function shown(){
  let list=ITEMS;
  if(Q){
    // 搜索时状态筛选让位 —— 否则「待复核」里搜一张已确认的卡会搜不到
    if(KINDS.includes(FILTER))list=list.filter(x=>x.kind===FILTER);
    const q=Q.toLowerCase();
    return list.filter(x=>x.id.toLowerCase().includes(q)||(x.name||'').toLowerCase().includes(q));
  }
  if(FILTER==='all')return list;
  if(FILTER==='open')return list.filter(x=>x.state==='open');
  if(FILTER==='regen')return list.filter(x=>x.state==='regen');
  if(FILTER==='done')return list.filter(x=>x.state==='done');
  if(FILTER==='review')return list.filter(x=>x.state==='done'&&!x.confirmed);
  if(KINDS.includes(FILTER))return list.filter(x=>x.kind===FILTER);
  return list;
}
function render(){
  const list=shown(),g=$('#grid');
  g.innerHTML=list.length?list.map(it=>{
    const vs=it.alive||[];   // 打回的版本不再显示
    const imgs=vs.length?vs.map(v=>{
      const cls=it.chosen===v?'pick':'';
      return `<div class="vw ${cls}" data-id="${it.id}" data-v="${v}">
        <img loading="lazy" src="/img/${it.id}/${v}" alt="v${v}"><span>v${v}</span></div>`;
    }).join(''):'<div class="vw empty">全部打回，待重生成</div>';
    const cls=it.state==='done'?'done':(it.state==='regen'?'regen':'');
    const hint=it.state==='regen'&&vs.length===1
      ? '<div class="hint">只剩这一张没选；不选它就会进「待重生成」</div>' : '';
    const rjLine=it.rejected.length
      ? `<div class="rejline">已打回 ${it.rejected.length} 张` +
        (it.rejected[it.rejected.length-1].reason?`：${it.rejected[it.rejected.length-1].reason}`:'')+'</div>' : '';
    return `<div class="card ${cls}">
      <div class="hd"><span class="id">${it.id}</span><span class="nm">${esc(it.name)}</span>
        <span class="kb">${it.size_kb?it.size_kb+'KB':'—'}</span></div>
      <div class="vs">${imgs}</div>${hint}${rjLine}
      <div class="ft">${it.state==='done'
        ? `<button class="${it.confirmed?'':'ok'}" data-act="confirm" data-id="${it.id}">${it.confirmed?'已复核 ✓':'确认通过'}</button>
           <button class="no" data-act="unconfirm" data-id="${it.id}">退回重选</button>`
        : `<button class="ok" data-act="choose" data-id="${it.id}">采用选中的</button>
           <input data-r="${it.id}" placeholder="打回理由">
           <button data-act="reject" data-id="${it.id}">打回选中</button>`}</div>
      <div class="pr">${esc(it.prompt).slice(0,300)}</div>
    </div>`;
  }).join(''):`<div style="color:#5f6878;padding:24px">${Q?'没有匹配「'+esc(Q)+'」的条目。':'这一类现在是空的。'}</div>`;
  const open=ITEMS.filter(x=>x.state==='open').length;
  const regen=ITEMS.filter(x=>x.state==='regen').length;
  const done=ITEMS.filter(x=>x.state==='done').length;
  const conf=ITEMS.filter(x=>x.state==='done'&&x.confirmed).length;
  $('#stat').innerHTML=Q
    ? `搜「${esc(Q)}」命中 <b>${list.length}</b> 条`
    : `共 <b>${ITEMS.length}</b> ｜ 待定 <b>${open}</b> ｜ 待重生成 <b>${regen}</b> ｜ 已选 <b>${done}</b> ｜ 已复核 <b>${conf}</b>`;
}
let SEL={};
document.addEventListener('click',async e=>{
  const vw=e.target.closest('.vw[data-id]');
  if(vw){SEL[vw.dataset.id]=parseInt(vw.dataset.v);
    vw.parentElement.querySelectorAll('.vw').forEach(x=>x.classList.remove('pick'));
    vw.classList.add('pick');return;}
  const b=e.target.closest('button[data-act]');
  if(!b)return;
  const id=b.dataset.id,act=b.dataset.act;
  if(act==='confirm'||act==='unconfirm'){
    const r=await fetch('/api/pick',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({id,action:act})});
    if(!r.ok){alert('保存失败');return;}
    const it=ITEMS.find(x=>x.id===id);
    it.confirmed=(act==='confirm');
    if(act==='unconfirm'){it.chosen=null;it.state='open';}
    render();return;
  }
  const v=SEL[id];
  if(v===undefined){alert('先点一张图选中');return;}
  const reasonInput=document.querySelector(`input[data-r="${id}"]`);
  const reason=reasonInput?reasonInput.value.trim():'';
  if(b.dataset.act==='reject'&&!reason){alert('打回要写理由');reasonInput&&reasonInput.focus();return;}
  const r=await fetch('/api/pick',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({id,v,action:b.dataset.act==='choose'?'choose':'reject',reason})});
  if(!r.ok){alert('保存失败');return;}
  const it=ITEMS.find(x=>x.id===id);
  if(b.dataset.act==='choose'){it.chosen=v;}
  else{it.rejected.push({v,reason});if(it.chosen===v)it.chosen=null;}
  render();
});
document.querySelectorAll('.chip').forEach(c=>c.onclick=()=>{
  document.querySelectorAll('.chip').forEach(x=>x.classList.remove('on'));
  c.classList.add('on');FILTER=c.dataset.f;render();});
$('#q').oninput=e=>{Q=e.target.value.trim();render();};
$('#q').onkeydown=e=>{if(e.key==='Escape'){e.target.value='';Q='';render();}};
fetch('/api/items').then(r=>r.json()).then(d=>{ITEMS=d;render();});
</script></body></html>"""


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
        if u.path == '/api/picks':
            return self._send(200, json.dumps(load(PICKS, {}), ensure_ascii=False))
        if u.path == '/api/queue_regen':
            # 待重生成队列：没选定、候选被否到只剩 <=1 张的素材
            items = [x for x in build_items() if x['state'] == 'regen']
            q = [{'id': x['id'], 'kind': x['kind'], 'name': x['name'],
                  'rejected': [{'v': r.get('v'), 'reason': r.get('reason')} for r in x['rejected']],
                  'alive': x['alive'], 'prompt': x['prompt']} for x in items]
            return self._send(200, json.dumps(q, ensure_ascii=False))
        if u.path == '/api/export_regen':
            items = [x for x in build_items() if x['state'] == 'regen']
            q = [{'id': x['id'], 'kind': x['kind'], 'name': x['name'],
                  'rejected': [{'v': r.get('v'), 'reason': r.get('reason')} for r in x['rejected']],
                  'alive': x['alive'], 'prompt': x['prompt']} for x in items]
            out = GAME / 'data' / 'queue_regen.json'
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(q, ensure_ascii=False, indent=1), encoding='utf-8')
            return self._send(200, json.dumps({'ok': True, 'count': len(q), 'file': str(out)}, ensure_ascii=False))
        if u.path.startswith('/img/'):
            parts = [p for p in u.path.split('/') if p]
            if len(parts) < 3:
                return self._send(404, 'bad path', 'text/plain; charset=utf-8')
            aid, v = parts[1], int(parts[2]) if parts[2].isdigit() else 0
            f = (ART / (aid + '.webp')) if v == 0 else (VERS / ('%s_v%d.webp' % (aid, v)))
            if not f.exists():
                return self._send(404, 'not found', 'text/plain; charset=utf-8')
            return self._send(200, f.read_bytes(), 'image/webp')
        return self._send(404, 'not found')

    def do_POST(self):
        n = int(self.headers.get('Content-Length') or 0)
        try:
            data = json.loads(self.rfile.read(n) or b'{}')
        except Exception:
            return self._send(400, '{"error":"bad json"}')
        u = urlparse(self.path)
        if u.path == '/api/pick':
            aid = data.get('id')
            v = data.get('v')
            act = data.get('action')
            if not aid or act not in ('choose', 'reject', 'confirm', 'unconfirm'):
                return self._send(400, '{"error":"bad payload"}')
            if act in ('choose', 'reject') and v is None:
                return self._send(400, '{"error":"bad payload"}')
            picks = load(PICKS, {})
            e = picks.setdefault(aid, {'chosen': None, 'rejected': []})
            if act == 'confirm':
                e['confirmed'] = True
            elif act == 'unconfirm':
                e['confirmed'] = False
                e['chosen'] = None
            elif act == 'choose':
                e['confirmed'] = False
                e['chosen'] = v
                e['rejected'] = [r for r in e.get('rejected', []) if r.get('v') != v]
            else:
                e.setdefault('rejected', []).append({'v': v, 'reason': data.get('reason', '')})
                if e.get('chosen') == v:
                    e['chosen'] = None
            e['updated'] = datetime.now().isoformat(timespec='seconds')
            save(PICKS, picks)
            return self._send(200, json.dumps({'ok': True, 'saved': e}, ensure_ascii=False))
        return self._send(404, 'not found')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--port', type=int, default=8770)
    a = ap.parse_args()
    VERS.mkdir(parents=True, exist_ok=True)
    items = build_items()
    multi = sum(1 for i in items if len(i['versions']) > 1)
    print('条目 %d，其中有备选版本的 %d 条' % (len(items), multi))
    print('打开 http://127.0.0.1:%d' % a.port)
    HTTPServer(('127.0.0.1', a.port), H).serve_forever()


if __name__ == '__main__':
    main()
