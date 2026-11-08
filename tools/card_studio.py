# -*- coding: utf-8 -*-
"""红渊 · 卡牌设计工作台

启动：
    cd C:\\Users\\Administrator\\Desktop\\杂七杂八\\红渊\\game
    python tools\\card_studio.py
浏览器打开 http://127.0.0.1:8771

设计原则：**所有改动只进草稿，不碰游戏数据。**
  - 草稿存 cards/_draft.json
  - 「导出补丁」生成 cards/_patch.json + 变更说明（给人/GLM 看）
  - 「应用到游戏」是显式按钮，会先备份 cards/*.json

四件事：
  1) 看全部 209 张卡（按职业/稀有度/类型/费用筛选，可搜名字和效果）
  2) 改：点开一张，表单编辑或直接改 JSON
  3) 增：从任意现有卡「另存为新的」或空白模板
  4) 删：标记删除（草稿里是 delete 操作，不立刻删）

右侧常驻「效果字段速查」——哪些 effect 键引擎真的支持（从现有 209 张统计出来的），
照着填就不会写出引擎不认的字段。
"""
import json
import shutil
import sys
import time
from collections import Counter, OrderedDict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, str(Path(__file__).resolve().parent))
from card_desc import describe_card, describe_upgrade  # noqa: E402

GAME = Path(__file__).resolve().parents[1]
CARDS = GAME / 'cards'
DRAFT = CARDS / '_draft.json'
PATCH = CARDS / '_patch.json'
PORT = 8771
CLASSES = ['diver', 'tremor', 'anmin', 'cangmin', 'shared']

CLASS_CN = {'diver': '下潜者', 'tremor': '震语者', 'anmin': '维护者', 'cangmin': '疯先知', 'shared': '通用'}


# ---------------- 数据层 ----------------

def load_cards():
    """返回 {class: [cards]}"""
    out = OrderedDict()
    for cls in CLASSES:
        p = CARDS / (cls + '.json')
        if not p.exists():
            out[cls] = []
            continue
        try:
            out[cls] = json.loads(p.read_text(encoding='utf-8'))
        except Exception as e:
            print('读 %s 失败: %s' % (p.name, e))
            out[cls] = []
    return out


def load_draft():
    if DRAFT.exists():
        try:
            return json.loads(DRAFT.read_text(encoding='utf-8'))
        except Exception:
            pass
    return {'ops': [], 'updated': ''}


def save_draft(d):
    d['updated'] = time.strftime('%Y-%m-%d %H:%M:%S')
    CARDS.mkdir(exist_ok=True)
    DRAFT.write_text(json.dumps(d, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')


def effect_keys_of(card):
    """把一张卡的 effect 展平成 ['damage','hits',...] 便于统计"""
    out = []
    e = card.get('effect')
    if isinstance(e, dict):
        for k, v in e.items():
            out.append(k)
            if k == 'special' and isinstance(v, list):
                for item in v:
                    if isinstance(item, dict) and item.get('code'):
                        out.append('special:' + str(item['code']))
    return out


def build_index():
    """全池统计：effect 键频次、cost_type 频次、稀有度/费用分布"""
    allcards = []
    for cls, arr in load_cards().items():
        for c in arr:
            c = dict(c)
            c['_cls'] = cls
            allcards.append(c)
    ek = Counter()
    ct = Counter()
    rar = Counter()
    en = Counter()
    for c in allcards:
        c['_desc'] = describe_card(c)
        c['_updesc'] = describe_upgrade(c)
        for k in effect_keys_of(c):
            ek[k] += 1
        ct[c.get('cost_type', 'none')] += 1
        rar[c.get('rarity', '')] += 1
        en[str(c.get('energy', 0))] += 1
    return allcards, {
        'effect_keys': ek.most_common(),
        'cost_type': ct.most_common(),
        'rarity': rar.most_common(),
        'energy': sorted(en.items(), key=lambda x: int(x[0])),
        'total': len(allcards),
        'by_class': {cls: len(arr) for cls, arr in load_cards().items()},
    }


def apply_draft():
    """把草稿真写进 cards/*.json（先备份）"""
    d = load_draft()
    ops = d.get('ops', [])
    if not ops:
        return {'ok': False, 'msg': '草稿是空的，没有可应用的操作'}

    data = load_cards()
    # 备份
    bak = CARDS / ('_bak-' + time.strftime('%Y%m%d-%H%M%S'))
    bak.mkdir(exist_ok=True)
    for cls in CLASSES:
        p = CARDS / (cls + '.json')
        if p.exists():
            shutil.copy2(p, bak / p.name)

    # 建 id → (class, index)
    where = {}
    for cls, arr in data.items():
        for i, c in enumerate(arr):
            where[c.get('id')] = (cls, i)

    done = []
    for op in ops:
        kind = op.get('op')
        cid = op.get('id')
        cls = op.get('cls')
        card = op.get('card')
        if kind == 'add':
            target = cls or (card or {}).get('class') or 'shared'
            data.setdefault(target, []).append(card)
            done.append('+ %s → %s' % (cid, target))
        elif kind == 'edit':
            if cid in where:
                c, i = where[cid]
                data[c][i] = card
                done.append('~ %s' % cid)
            else:
                t = cls or (card or {}).get('class') or 'shared'
                data.setdefault(t, []).append(card)
                done.append('+ %s（编辑目标不存在，按新增处理）' % cid)
        elif kind == 'delete':
            if cid in where:
                c, i = where[cid]
                data[c].pop(i)
                # 重建索引
                where = {}
                for cc, arr in data.items():
                    for ii, xx in enumerate(arr):
                        where[xx.get('id')] = (cc, ii)
                done.append('- %s' % cid)

    for cls in CLASSES:
        p = CARDS / (cls + '.json')
        arr = data.get(cls, [])
        p.write_text(json.dumps(arr, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')

    # 清空草稿
    save_draft({'ops': [], 'updated': ''})
    return {'ok': True, 'msg': '已应用 %d 条操作' % len(ops), 'detail': done, 'backup': str(bak)}


# ---------------- HTTP ----------------

PAGE = r'''<!doctype html>
<html lang="zh"><head><meta charset="utf-8">
<title>红渊 · 卡牌工作台</title>
<style>
*{box-sizing:border-box}
body{margin:0;background:#141011;color:#d8c9c4;font:13px/1.5 "Consolas","Microsoft YaHei",monospace}
header{padding:8px 14px;background:#1d1618;border-bottom:1px solid #3a2b2e;display:flex;gap:10px;align-items:center;flex-wrap:wrap}
header b{color:#e8a08a;font-size:15px}
header .sp{flex:1}
button{background:#2a1f21;color:#d8c9c4;border:1px solid #4a363a;padding:5px 12px;cursor:pointer;border-radius:3px;font:inherit}
button:hover{background:#3a2a2d;border-color:#6a4a50}
button.pri{background:#5a2a2a;border-color:#8a4a4a;color:#ffd8cc}
button.pri:hover{background:#7a3a3a}
button.warn{border-color:#7a5a2a;color:#e8c08a}
#wrap{display:flex;height:calc(100vh - 45px)}
#left{width:420px;border-right:1px solid #3a2b2e;display:flex;flex-direction:column}
#filters{padding:8px;border-bottom:1px solid #3a2b2e;display:flex;gap:6px;flex-wrap:wrap}
select,input{background:#1d1618;color:#d8c9c4;border:1px solid #4a363a;padding:4px 6px;border-radius:3px;font:inherit}
input[type=text]{flex:1;min-width:100px}
#list{flex:1;overflow:auto}
table{width:100%;border-collapse:collapse;font-size:12px}
th{position:sticky;top:0;background:#241a1c;text-align:left;padding:5px 6px;border-bottom:1px solid #3a2b2e;font-weight:normal;color:#a89088}
td{padding:3px 6px;border-bottom:1px solid #241a1c;cursor:pointer}
tr:hover td{background:#241a1c}
tr.sel td{background:#3a2426}
tr.del td{opacity:.4;text-decoration:line-through}
tr.new td{color:#9ad8a0}
.tag{display:inline-block;padding:0 4px;border-radius:2px;font-size:11px}
.diver{background:#1f2f3f;color:#8ab8e0}
.tremor{background:#2f2430;color:#c8a0d8}
.anmin{background:#243024;color:#9ad8a0}
.cangmin{background:#302a20;color:#e0c890}
.shared{background:#2a2a2a;color:#c0c0c0}
#right{flex:1;display:flex;flex-direction:column;overflow:hidden}
#editor{flex:1;overflow:auto;padding:12px}
#stats{width:260px;border-left:1px solid #3a2b2e;overflow:auto;padding:10px;font-size:12px}
#stats h4{margin:10px 0 4px;color:#e8a08a;font-size:12px;font-weight:normal}
#stats .k{display:flex;justify-content:space-between;padding:1px 0;border-bottom:1px dotted #2a1f21}
#stats .k span:last-child{color:#8ab8e0}
.row{display:flex;gap:8px;margin-bottom:8px;align-items:flex-start}
.row label{width:90px;flex:none;color:#a89088;padding-top:4px}
.row .f{flex:1}
.row input,.row select,.row textarea{width:100%}
textarea{background:#0f0c0d;color:#d8c9c4;border:1px solid #4a363a;padding:6px;font:12px/1.5 Consolas,monospace;border-radius:3px;min-height:60px}
.hint{color:#6a5a58;font-size:11px;margin:-4px 0 8px 98px}
#status{padding:6px 14px;background:#1d1618;border-top:1px solid #3a2b2e;font-size:12px;color:#a89088}
#status b{color:#e8a08a}
.sec{border-top:1px solid #3a2b2e;margin:14px 0 0;padding-top:10px}
.sec h3{margin:0 0 8px;font-size:13px;color:#e8a08a;font-weight:normal}
.ops{font-size:12px}
.ops li{margin:2px 0}
</style></head><body>

<header>
  <b>红渊 · 卡牌工作台</b>
  <span id="cnt" style="color:#8a7a78"></span>
  <span class="sp"></span>
  <button onclick="newCard()">＋ 新建卡</button>
  <button onclick="exportPatch()" class="warn">导出补丁</button>
  <button onclick="applyDraft()" class="pri">应用到游戏</button>
  <button onclick="revertDraft()">清空草稿</button>
</header>

<div id="wrap">
  <div id="left">
    <div id="filters">
      <select id="fCls" onchange="render()"><option value="">全部职业</option></select>
      <select id="fRar" onchange="render()"><option value="">稀有度</option></select>
      <select id="fType" onchange="render()"><option value="">类型</option></select>
      <select id="fEn" onchange="render()"><option value="">费用</option></select>
      <input type="text" id="fQ" placeholder="搜 id / 名字 / 效果" oninput="render()">
    </div>
    <div id="list"></div>
  </div>
  <div id="right">
    <div id="editor"><div style="color:#6a5a58;padding:40px;text-align:center">← 从左边选一张卡</div></div>
  </div>
  <div id="stats"></div>
</div>

<div id="status">就绪</div>

<script>
let DATA = [], STATS = {}, DRAFT = {ops: []}, CUR = null, CUR_JSON = '';
const CN = {diver:'下潜者',tremor:'震语者',anmin:'维护者',cangmin:'疯先知',shared:'通用'};
// 枚举中文名（值仍是英文，引擎只认英文；这里只管显示）
// rarity / type 是游戏里不露给玩家的内部字段，中文名是我按语义定的
// cost_type 的中文直接照引擎 switch 的实际后果写，改了它就会改行为
const E = {
  type: {attack:'攻击', skill:'技能', power:'能力'},
  rarity: {common:'普通', uncommon:'精良', rare:'稀有', special:'特殊'},
  cost_type: {
    none:'无代价',
    memory:'弃牌 — 随机删掉牌库 1 张',
    vitality:'生命 — 最大生命 -1',
    mark:'凝视 — 凝视 +1',
    lock:'锁死 — 本场战斗内只能用一次',
    custom:'其他（自己填，代码待实现）'
  },
  cost_short: {none:'无代价', memory:'弃牌', vitality:'掉上限', mark:'凝视', lock:'锁死', custom:'自定义'},
  veins: {light:'光', water:'水', heat:'热', tremor:'震', mineral:'矿'}
};
function cn(map, v){ return (E[map] && E[map][v]) || v || ''; }
// option 文本：中文在前，英文垫在后面（方便对照导出 JSON）
function opts(map, cur){
  return Object.keys(E[map]).map(k=>`<option value="${k}" ${cur===k?'selected':''}>${E[map][k]} · ${k}</option>`).join('');
}

function st(msg, err){ const e=document.getElementById('status'); e.innerHTML = err? '<b style="color:#e08a8a">'+msg+'</b>' : msg; }
function esc(s){ return String(s==null?'':s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c])); }

async function boot(){
  const r = await fetch('/api/data'); const j = await r.json();
  DATA = j.cards; STATS = j.stats; DRAFT = j.draft;
  // 填充筛选器
  const cls = [...new Set(DATA.map(c=>c._cls))];
  document.getElementById('fCls').innerHTML = '<option value="">全部职业</option>' + cls.map(c=>`<option value="${c}">${CN[c]||c}</option>`).join('');
  const rar = [...new Set(DATA.map(c=>c.rarity).filter(Boolean))];
  document.getElementById('fRar').innerHTML = '<option value="">稀有度</option>' + rar.map(x=>`<option value="${esc(x)}">${cn('rarity',x)}</option>`).join('');
  const typ = [...new Set(DATA.map(c=>c.type).filter(Boolean))];
  document.getElementById('fType').innerHTML = '<option value="">类型</option>' + typ.map(x=>`<option value="${esc(x)}">${cn('type',x)}</option>`).join('');
  const en = [...new Set(DATA.map(c=>c.energy).filter(x=>x!=null))].sort((a,b)=>a-b);
  document.getElementById('fEn').innerHTML = '<option value="">费用</option>' + en.map(x=>`<option>${x}</option>`).join('');
  render(); renderStats(); renderDraft();
}

function opsMap(){
  const m = {};
  for(const o of DRAFT.ops){ m[o.id] = o; }
  return m;
}

// DATA（已存在的卡）+ 草稿里新增的卡（新增的还没进 DATA，左边列表原来根本看不到）
function allCards(){
  const out = DATA.slice();
  for(const o of DRAFT.ops){
    if(o.op === 'add' && !DATA.some(x => x.id === o.id)){
      const card = o.card || {};
      out.push(Object.assign({}, card, {id: o.id, _cls: o.cls || card.class || 'shared', _op: 'add', _card: card}));
    }
  }
  return out;
}

function filtered(){
  const c = document.getElementById('fCls').value;
  const r = document.getElementById('fRar').value;
  const t = document.getElementById('fType').value;
  const e = document.getElementById('fEn').value;
  const q = document.getElementById('fQ').value.trim().toLowerCase();
  const om = opsMap();
  return allCards().filter(x=>{
    if(c && x._cls!==c) return false;
    if(r && x.rarity!==r) return false;
    if(t && x.type!==t) return false;
    if(e!=='' && String(x.energy)!==e) return false;
    if(q){
      const hay = (x.id+' '+(x.name||'')+' '+JSON.stringify(x.effect||{})).toLowerCase();
      if(!hay.includes(q)) return false;
    }
    return true;
  }).map(x=>{
    const o = om[x.id];
    return o ? Object.assign({}, x, {_op: o.op, _edited: o.op==='edit', _card: o.card}) : x;
  });
}

function render(){
  const arr = filtered();
  document.getElementById('cnt').textContent = `共 ${arr.length} / ${allCards().length} 张`;
  let h = '<table><thead><tr><th style="width:34px">费</th><th style="width:60px">职业</th><th>名字</th><th style="width:52px">稀有</th><th style="width:44px">类型</th></tr></thead><tbody>';
  for(const x of arr){
    const card = x._card || x;
    const cls = card._cls || x._cls;
    const trCls = x._op==='delete'?'del':(x._op==='add'?'new':(CUR&&CUR.id===x.id?'sel':''));
    h += `<tr class="${trCls}" onclick="pick('${esc(x.id)}')">`
      + `<td>${card.energy!=null?card.energy:'-'}</td>`
      + `<td><span class="tag ${cls}">${CN[cls]||cls}</span></td>`
      + `<td>${card.core?'<span style="color:#e0c060" title="核心卡">★</span>':''}${esc(card.name)}${(card.design_note||'').trim()?' <span style="color:#c8a0d8">✎</span>':''}${x._op==='add'?' <span style="color:#9ad8a0">新</span>':''}${x._op==='delete'?' <span style="color:#e08a8a">删</span>':''}</td>`
      + `<td>${esc(cn('rarity',card.rarity))}</td><td>${esc(cn('type',card.type))}</td></tr>`;
  }
  h += '</tbody></table>';
  document.getElementById('list').innerHTML = h;
}

function pick(id){
  const om = opsMap();
  const base = DATA.find(x=>x.id===id);
  const o = om[id];
  const card = o ? (o.card || {}) : (base || {id: id, name: id});
  CUR = JSON.parse(JSON.stringify(card));
  CUR._cls = (o && o.cls) || (base && base._cls) || card.class || 'shared';
  CUR_JSON = JSON.stringify(CUR, null, 1);
  renderEditor(o);
  render();
}

function renderEditor(op){
  const c = CUR;
  const ek = STATS.effect_keys.map(x=>x[0]);
  let h = `<div class="sec"><h3>${esc(c.id)}  ${esc(c.name||'')}
    <span style="color:#6a5a58">(${CN[c._cls]||c._cls})</span></h3>`;

  // 引擎代码自动翻译（服务端算好塞进来的，只读）
  if(c._desc){
    h += `<div style="background:#1d1618;border-left:3px solid #8a4a4a;padding:8px 10px;margin:8px 0;font:13px/1.7 'Microsoft YaHei',sans-serif;color:#c8b8b2">`;
    h += `<div style="color:#8a7a78;font-size:11px;margin-bottom:4px">这版卡的实际效果（按引擎结算代码翻译，不是猜的）　<span style="color:#6a5a58">—— 是你最后保存时的数据；刚改的数字这里不会跟着变</span></div>`;
    h += `<div>${esc(c._desc)}</div>`;
    if(c._updesc) h += `<div style="margin-top:6px;color:#a89890">升级后：${esc(c._updesc)}</div>`;
    h += `</div>`;
  }

  h += field('id','id 标识', `<input id="f_id" value="${esc(c.id)}" oninput="upd('id',this.value)">`, '唯一，不许和任何现有卡撞');
  h += field('name','名字', `<input id="f_name" value="${esc(c.name)}" oninput="upd('name',this.value)">`);
  h += field('cls','职业', `<select id="f_cls">${Object.entries(CN).map(([k,v])=>`<option value="${k}" ${c._cls===k?'selected':''}>${v}</option>`).join('')}</select>`, '', `updcls`);
  h += field('type','类型', `<select id="f_type">${opts('type', c.type)}</select>`, '', null, 'type');
  h += field('rarity','稀有度', `<select id="f_rarity">${opts('rarity', c.rarity)}</select>`, '', null, 'rarity');
  h += field('energy','费用', `<input id="f_energy" type="number" min="0" max="5" value="${c.energy!=null?c.energy:1}" oninput="updNum('energy',this.value)">`);
  h += field('cost_type','代价类型', `<select id="f_cost_type">${opts('cost_type', c.cost_type)}</select>`, '选了代价类型才会结算代价；<b>无代价</b> 就是普通卡', 'ct', 'cost_type');
  const costHint = (c.cost_type === 'custom')
    ? '⚠ 你选的是「其他」—— 引擎没有这个代价类型，现在打出来<b>什么都不扣</b>。把代价写清楚在这里，导出后由 GLM 或我实现。'
    : '代价类型不是「无代价」时，玩家鼠标悬停会看到这句';
  h += field('cost_text','代价文案', `<input id="f_cost_text" value="${esc(c.cost_text||'')}" oninput="upd('cost_text',this.value)">`, costHint);
  h += field('veins','属性脉', `<input id="f_veins" value="${esc((c.veins||[]).map(v=>E.veins[v]||v).join(','))}" oninput="updVeins(this.value)" placeholder="光,水,热,震,矿 —— 可多选，逗号分隔；写中文或英文都认">`, '存到卡里的是英文键，这里是中文显示');
  h += field('flavor','风味文本', `<textarea id="f_flavor" oninput="upd('flavor',this.value)">${esc(c.flavor||'')}</textarea>`, '冷、短、像记录。不许出现「造成/获得/点伤害/恭喜/解锁」');

  h += '</div>';

  // ==== 你写的那部分：人话描述 ====
  h += `<div class="sec"><h3>这张牌做什么</h3>`;
  h += `<div class="row"><label>核心卡</label><div class="f"><label style="display:inline-flex;align-items:center;gap:6px;cursor:pointer"><input type="checkbox" id="f_core" ${c.core?'checked':''} onchange="upd('core', this.checked)"> 这张是核心卡（决定 build 方向的那种）</label></div></div>`;
  h += `<div class="hint">勾了之后：卡面带「核心」标记、进奖励池受保底保护、第一层不会出。不勾就是普通牌。</div>`;
  h += `<div class="row"><label>想让玩家怎么玩</label><div class="f"><input id="f_playidea" value="${esc(c.play_idea||'')}" oninput="upd('play_idea',this.value)" placeholder="一句话，例：让玩家舍不得打牌，一直攒着格挡"></div></div>`;
  h += `<div class="hint">选填。核心卡建议写 —— 我审卡时靠这句判断它有没有做到自己想做的事。</div>`;
  h += `<div class="hint" style="margin:0 0 8px 0">用你自己的话说，不用管代码。写得含糊也行 —— 有歧义我和 GLM 会回来问你，不猜。</div>`;
  h += `<textarea id="f_note" style="min-height:130px;font:13px/1.7 'Microsoft YaHei',sans-serif" oninput="upd('design_note',this.value)" placeholder="例：抽 1 张牌。如果这是本回合打出的第一张牌，再抽 1 张。打完这张牌，你损失 2 点生命。">${esc(c.design_note||'')}</textarea>`;
  h += `</div>`;

  h += `<div class="sec"><h3>升级后变成什么</h3>`;
  h += `<div class="hint" style="margin:0 0 8px 0">什么都不写 = 这张牌不升级。名字后缀、风味文本要不要变也在这里说。</div>`;
  h += `<textarea id="f_upnote" style="min-height:90px;font:13px/1.7 'Microsoft YaHei',sans-serif" oninput="upd('upgrade_note',this.value)" placeholder="例：改成抽 2 张。名字加「·Ⅱ」。">${esc(c.upgrade_note||'')}</textarea>`;
  h += `</div>`;

  // ==== 引擎数据：默认折叠，你暂时不用碰 ====
  h += `<details class="sec"><summary style="cursor:pointer;color:#8a7a78;font-size:12px">▸ 引擎数据（折叠着，不用管 —— 除非你想看这张牌现在的实现长什么样）</summary>`;

  h += `<div style="margin-top:10px"><h3 style="margin:6px 0 4px;font-size:12px;color:#a89088;font-weight:normal">effect（引擎支持的键）</h3>`;
  h += `<div class="hint" style="margin:0 0 6px 0">带数字的是全池用过的次数；0 次的不要用（引擎可能不认）。</div>`;
  h += `<textarea id="f_effect" style="min-height:120px" oninput="updEffectText(this.value)">${esc(JSON.stringify(c.effect||{}, null, 1))}</textarea>`;
  h += `<div style="color:#6a5a58;font-size:11px;margin-top:4px">${ek.slice(0,40).map(k=>`<code style="cursor:pointer;padding:0 3px;background:#241a1c" onclick="insKey('${esc(k)}')">${esc(k)}</code>`).join(' ')}</div>`;
  h += `</div>`;

  h += `<div style="margin-top:10px"><h3 style="margin:6px 0 4px;font-size:12px;color:#a89088;font-weight:normal">upgrade（可选）</h3>`;
  h += `<textarea id="f_upgrade" style="min-height:70px" oninput="updUpgradeText(this.value)">${esc(JSON.stringify(c.upgrade||{}, null, 1))}</textarea>`;
  h += `</div>`;

  h += `</details>`;

  // 操作
  h += `<div class="sec" style="display:flex;gap:8px;flex-wrap:wrap">`;
  h += `<button onclick="saveEdit()" class="pri">保存到草稿</button>`;
  h += `<button onclick="dupCard()">另存为新的</button>`;
  h += `<button onclick="delCard()" class="warn">${op&&op.op==='delete'?'撤销删除':'标记删除'}</button>`;
  h += `<span class="sp" style="flex:1"></span>`;
  h += `<span style="color:#6a5a58;font-size:12px">原始 JSON ↓</span>`;
  h += `</div>`;

  h += `<div class="sec"><textarea id="f_rawjson" style="min-height:300px" oninput="rawChanged()">${esc(CUR_JSON)}</textarea>`;
  h += `<div style="margin-top:6px"><button onclick="loadRaw()">从 JSON 载入</button> <span id="rawmsg" style="color:#8ab8e0"></span></div></div>`;

  document.getElementById('editor').innerHTML = h;
  // select 事件（因为没有 oninput 统一处理）
  ['type','rarity'].forEach(k=>{
    const el = document.getElementById('f_'+k);
    if(el) el.onchange = ()=>upd(k, el.value);
  });
  const ctEl = document.getElementById('f_cost_type');
  if(ctEl) ctEl.onchange = ()=>{
    upd('cost_type', ctEl.value);
    if(ctEl.value === 'custom') st('「其他」是设计态：引擎不认这个代价，现在打出来不会扣任何东西。把代价写清在「代价文案」里，导出后实现。');
  };
  const clsEl = document.getElementById('f_cls');
  if(clsEl) clsEl.onchange = ()=>{ CUR._cls = clsEl.value; syncRaw(); };
}

function field(id, label, inner, hint, kind, key){
  return `<div class="row"><label>${label}</label><div class="f">${inner}</div></div>`
    + (hint?`<div class="hint">${hint}</div>`:'');
}

function upd(k, v){ CUR[k] = v; syncRaw(); }
function updNum(k, v){ CUR[k] = v===''?0:Number(v); syncRaw(); }
function updVeins(v){
  // 中文名 → 英文键；英文原样留
  const rev = {}; Object.keys(E.veins).forEach(k=>rev[E.veins[k]]=k);
  CUR.veins = v.split(',').map(x=>x.trim()).filter(Boolean).map(x=>rev[x]||x);
  syncRaw();
}
function updEffectText(v){ try{ CUR.effect = JSON.parse(v); syncRaw(); document.getElementById('f_effect').style.borderColor='#4a363a'; }catch(e){ document.getElementById('f_effect').style.borderColor='#a04040'; } }
function updUpgradeText(v){ try{ CUR.upgrade = JSON.parse(v); syncRaw(); document.getElementById('f_upgrade').style.borderColor='#4a363a'; }catch(e){ document.getElementById('f_upgrade').style.borderColor='#a04040'; } }
function insKey(k){
  if(k.startsWith('special:')){ st('special 的 code 请直接在 JSON 里写', true); return; }
  const t = document.getElementById('f_effect');
  try{ const o = JSON.parse(t.value||'{}'); o[k] = 1; t.value = JSON.stringify(o,null,1); CUR.effect=o; syncRaw(); }catch(e){}
}

function syncRaw(){
  const c = {};
  for(const k in CUR) if(k.charAt(0) !== '_') c[k] = CUR[k];
  CUR_JSON = JSON.stringify(c, null, 1);
  const el = document.getElementById('f_rawjson'); if(el) el.value = CUR_JSON;
}

function rawChanged(){ CUR_JSON = document.getElementById('f_rawjson').value; }
function loadRaw(){
  try{
    const o = JSON.parse(CUR_JSON);
    const cls = CUR._cls;
    CUR = o; CUR._cls = cls;
    renderEditor(opsMap()[CUR.id]);
    document.getElementById('rawmsg').textContent = '已载入';
  }catch(e){ document.getElementById('rawmsg').textContent = 'JSON 错误：'+e.message; }
}

function clean(c){
  // 下划线开头的是界面用的临时字段（_cls / _desc / _updesc / _op ...），一律不写进草稿
  const o = {};
  for(const k in c) if(k.charAt(0) !== '_') o[k] = c[k];
  return {card: o, cls: c._cls};
}

function saveEdit(){
  const {card, cls} = clean(CUR);
  if(!card.id){ st('id 不能为空', true); return; }
  const dupe = DATA.find(x=>x.id===card.id);
  const isEdit = dupe && dupe._cls===cls;
  const op = {op: isEdit?'edit':'add', id: card.id, cls, card};
  const idx = DRAFT.ops.findIndex(o=>o.id===card.id);
  if(idx>=0) DRAFT.ops[idx]=op; else DRAFT.ops.push(op);
  pushDraft();
}

function dupCard(){
  const {card, cls} = clean(CUR);
  const nid = prompt('新卡的 id（同职业前缀，如 dive_0084 / trem_0084 / u_0018）', (cls==='diver'?'dive_':cls==='tremor'?'trem_':cls==='anmin'?'anm_':cls==='cangmin'?'cng_':'u_') + '00xx');
  if(!nid) return;
  if(DATA.find(x=>x.id===nid) || DRAFT.ops.find(o=>o.id===nid)){ st('id 已存在：'+nid, true); return; }
  const c2 = Object.assign({}, card, {id: nid, class: cls, name: (card.name||'新卡')+'·改'});
  DRAFT.ops.push({op:'add', id: nid, cls, card: c2});
  pushDraft();
  setTimeout(()=>{ CUR = JSON.parse(JSON.stringify(c2)); CUR._cls = cls; renderEditor(null); render(); }, 100);
}

function delCard(){
  const {card, cls} = clean(CUR);
  const exists = DRAFT.ops.findIndex(o=>o.id===card.id && o.op==='delete');
  if(exists>=0){ DRAFT.ops.splice(exists,1); pushDraft(); return; }
  const base = DATA.find(x=>x.id===card.id);
  if(!base){ // 新增的卡还没保存过，直接从草稿里去掉 add
    const ai = DRAFT.ops.findIndex(o=>o.id===card.id && o.op==='add');
    if(ai>=0){ DRAFT.ops.splice(ai,1); pushDraft(); return; }
  }
  DRAFT.ops.push({op:'delete', id: card.id, cls});
  pushDraft();
}

// 该职业下一个没被占用的编号（避免「u_00xx」这种占位 id 撞车把别的卡覆盖掉）
function nextId(cls){
  const pre = cls==='diver'?'dive_':cls==='tremor'?'trem_':cls==='anmin'?'anm_':cls==='cangmin'?'cng_':'u_';
  let max = 0;
  const ids = DATA.map(x=>x.id).concat(DRAFT.ops.filter(o=>o.op==='add').map(o=>o.id));
  for(const id of ids){
    if(!id || id.indexOf(pre) !== 0) continue;
    const m = String(id).slice(pre.length).match(/^(\d+)$/);
    if(m) max = Math.max(max, parseInt(m[1], 10));
  }
  return pre + String(max + 1).padStart(4, '0');
}

function newCard(){
  const rev = {}; Object.keys(CN).forEach(k=>rev[CN[k]]=k);
  const ans = (prompt('哪个职业？\n下潜者 / 震语者 / 维护者 / 疯先知 / 通用','通用')||'').trim();
  const cls = rev[ans] || (CN[ans] ? ans : null);
  if(!cls) { st('没认出这个职业：'+ans, true); return; }
  const nid = (prompt('新卡 id（建议用下面这个，改也行）', nextId(cls))||'').trim();
  if(!nid) return;
  // 撞车必须拦：原来不拦，同 id 一保存就把草稿里那张覆盖掉了（2026-11-04 真实事故）
  if(DATA.find(x=>x.id===nid) || DRAFT.ops.find(o=>o.id===nid)){
    st('id 已被占用：'+nid+'　—— 换个 id，或者直接点右侧草稿里那张改', true);
    return;
  }
  // effect 先留空：你只写描述，实现交给 GLM/我
  const tpl = {id: nid, name:'新卡', class: cls, type:'attack', rarity:'common', veins:[], energy:1,
               effect:{}, cost_type:'none', cost_text:'',
               flavor:'', design_note:'', upgrade_note:'', core:false, play_idea:''};
  CUR = JSON.parse(JSON.stringify(tpl)); CUR._cls = cls;
  renderEditor(null);
  st('已创建。先填「这张牌做什么」，引擎数据留空没关系。');
}

async function pushDraft(){
  await fetch('/api/draft', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(DRAFT)});
  renderDraft(); render(); st('草稿已保存，共 '+DRAFT.ops.length+' 条操作');
}

function renderDraft(){
  const box = document.getElementById('stats');
  let h = '';
  // 统计
  h += `<h4>卡池（${STATS.total} 张）</h4>`;
  for(const [cls,n] of Object.entries(STATS.by_class)){
    h += `<div class="k"><span>${CN[cls]||cls}</span><span>${n}</span></div>`;
  }
  h += `<h4>稀有度</h4>`;
  for(const [k,n] of STATS.rarity) h += `<div class="k"><span>${cn('rarity',k)}</span><span>${n}</span></div>`;
  h += `<h4>费用</h4>`;
  for(const [k,n] of STATS.energy) h += `<div class="k"><span>${k} 费</span><span>${n}</span></div>`;
  h += `<h4>代价类型</h4>`;
  for(const [k,n] of STATS.cost_type) h += `<div class="k"><span>${cn('cost_short',k)}</span><span>${n}</span></div>`;
  h += `<h4>effect 键（用过的次数）</h4>`;
  h += `<div class="hint" style="margin:0 0 4px 0">这些是引擎的内部键名，<b>必须照抄英文</b>，写中文引擎不认。</div>`;
  for(const [k,n] of STATS.effect_keys) h += `<div class="k"><span>${esc(k)}</span><span>${n}</span></div>`;
  // 草稿
  h += `<h4 style="margin-top:16px">草稿（${DRAFT.ops.length} 条）</h4>`;
  if(DRAFT.ops.length){
    h += '<ul class="ops">';
    for(const o of DRAFT.ops){
      const name = o.card ? o.card.name : '';
      const mark = o.op==='add'?'+':o.op==='delete'?'-':'~';
      const col = o.op==='add'?'#9ad8a0':o.op==='delete'?'#e08a8a':'#8ab8e0';
      h += `<li style="cursor:pointer;padding:2px 0" onclick="pick('${esc(o.id)}')" title="点一下打开这张草稿">`
        + `<span style="color:${col}">${mark}</span> ${esc(o.id)} ${esc(name||'')}</li>`;
    }
    h += '</ul>';
    h += `<div style="color:#6a5a58;margin-top:6px">${DRAFT.updated||''}</div>`;
  } else {
    h += '<div style="color:#6a5a58">（空）</div>';
  }
  box.innerHTML = h;
}

async function exportPatch(){
  const r = await fetch('/api/export', {method:'POST'});
  const j = await r.json();
  if(j.ok) st('已导出：cards/_patch.json（'+j.count+' 条）');
  else st(j.msg, true);
}

async function applyDraft(){
  if(!DRAFT.ops.length){ st('草稿是空的', true); return; }
  if(!confirm('真的写进游戏数据？\n会先自动备份 cards/*.json 到 cards/_bak-时间戳/\n\n共 '+DRAFT.ops.length+' 条操作')) return;
  const r = await fetch('/api/apply', {method:'POST'});
  const j = await r.json();
  if(j.ok){ st(j.msg+'，备份在 '+j.backup); boot(); }
  else st(j.msg, true);
}

async function revertDraft(){
  if(!confirm('清空全部草稿操作？')) return;
  DRAFT.ops = [];
  await pushDraft();
  st('草稿已清空');
}

boot();
</script></body></html>
'''


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype='application/json; charset=utf-8'):
        if isinstance(body, str):
            body = body.encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        u = urlparse(self.path)
        if u.path in ('/', '/index.html'):
            return self._send(200, PAGE, 'text/html; charset=utf-8')
        if u.path == '/api/data':
            cards, stats = build_index()
            return self._send(200, json.dumps(
                {'cards': cards, 'stats': stats, 'draft': load_draft()}, ensure_ascii=False))
        return self._send(404, '{"ok":false}')

    def do_POST(self):
        u = urlparse(self.path)
        n = int(self.headers.get('Content-Length') or 0)
        raw = self.rfile.read(n) if n else b'{}'
        try:
            body = json.loads(raw.decode('utf-8')) if raw else {}
        except Exception:
            body = {}

        if u.path == '/api/draft':
            save_draft(body if isinstance(body, dict) else {'ops': []})
            return self._send(200, '{"ok":true}')

        if u.path == '/api/export':
            d = load_draft()
            ops = d.get('ops', [])
            PATCH.write_text(json.dumps(ops, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
            # 附一份人读的说明
            lines = ['# 卡牌变更补丁（%s）\n' % d.get('updated', ''),
                     '共 %d 条操作。给 GLM 或人实现时用这份说明。\n' % len(ops)]
            for o in ops:
                t = {'add': '新增', 'edit': '修改', 'delete': '删除'}.get(o.get('op'), o.get('op'))
                c = o.get('card') or {}
                lines.append('- **%s** `%s` %s（%s）' % (t, o.get('id'), c.get('name', ''), o.get('cls', '')))
                dn = (c.get('design_note') or '').strip()
                un = (c.get('upgrade_note') or '').strip()
                if dn:
                    lines.append('')
                    lines.append('  这张牌做什么：')
                    for ln in dn.splitlines():
                        lines.append('  > ' + ln)
                if un:
                    lines.append('')
                    lines.append('  升级后：')
                    for ln in un.splitlines():
                        lines.append('  > ' + ln)
                if dn or un:
                    lines.append('')
            (CARDS / '_patch.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
            return self._send(200, json.dumps({'ok': True, 'count': len(ops)}))

        if u.path == '/api/apply':
            try:
                r = apply_draft()
            except Exception as e:
                r = {'ok': False, 'msg': '应用失败：%s' % e}
            return self._send(200, json.dumps(r, ensure_ascii=False))

        return self._send(404, '{"ok":false}')


def main():
    print('红渊 · 卡牌工作台')
    print('  浏览器打开 http://127.0.0.1:%d' % PORT)
    print('  草稿文件 cards/_draft.json')
    print('  Ctrl+C 停止')
    srv = ThreadingHTTPServer(('127.0.0.1', PORT), H)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print('\n停止')


if __name__ == '__main__':
    main()
