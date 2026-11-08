# -*- coding: utf-8 -*-
"""生成「把生成图贴进真卡面」的对照页（一次性工具，不进交付物）。

输出 tools/_art_in_game.html：
  iframe 载入真游戏 → 自动点进战斗 → 把 5 张测试图塞进手牌图案区
  ?mode=ph  则还原占位符号，做基线对照
图片压到 256×384 JPEG 再内联，避免文件过大。
"""
import base64
import io
import sys
from pathlib import Path

from PIL import Image

GAME = Path(r'C:\Users\Administrator\Desktop\杂七杂八\红渊\game')
ART = GAME / 'tools' / 'art_test'
OUT = GAME / 'tools' / '_art_in_game.html'

PICKS = [
    ('lora_060.png', 'LoRA 0.6'),
    ('lora_000.png', '无 LoRA'),
    ('woodcut_lens.png', '木刻'),
    ('emblem_lens.png', '图鉴'),
    ('flat_card_lens.png', '扁平'),
]


def data_uri(p: Path):
    im = Image.open(p).convert('RGB')
    im.thumbnail((256, 384), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, 'JPEG', quality=82)
    b64 = base64.b64encode(buf.getvalue()).decode()
    return 'data:image/jpeg;base64,' + b64, im.size


def main():
    uris = []
    for fn, label in PICKS:
        p = ART / fn
        if not p.exists():
            print('missing', fn)
            continue
        u, size = data_uri(p)
        uris.append((label, u, size))
    print('embedded', len(uris), 'images')

    items = ','.join('{label:%r, uri:%r}' % (lbl, uri) for lbl, uri, _ in uris)
    items = items.replace('{', '{').replace("'", "'")

    html = """<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><title>卡面贴图对照</title>
<style>
 body{margin:0;background:#151515;color:#ddd;font:13px/1.6 "Segoe UI",system-ui,sans-serif}
 #bar{padding:6px 10px;background:#222;border-bottom:1px solid #333}
 #bar b{color:#e8b36a}
 #wrap{display:flex;gap:8px;padding:8px}
 iframe{width:1000px;height:640px;border:1px solid #333;background:#000;zoom:0.95}
 #side{width:300px;font-size:12px;color:#aaa}
 .sw{display:inline-block;width:10px;height:10px;margin-right:4px}
</style></head>
<body>
<div id="bar">卡面贴图对照 —— <b id="mode"></b>（图片缩到 256×384 再放进 78px 图案区）</div>
<div id="wrap">
  <iframe id="f" src="../web/index.html"></iframe>
  <div id="side">
    <p>观察点：</p>
    <p>1. 78px 图案区里能不能一眼认出是什么</p>
    <p>2. 五张不同风格放在一起，卡组是否像一个整体</p>
    <p>3. 和旁边占位符号版（?mode=ph）比，信息层级有没有变乱</p>
  </div>
</div>
<script>
const PICS = [ITEMS];
const qs = new URLSearchParams(location.search);
const mode = qs.get('mode') || 'img';
const fit = qs.get('fit') || 'cover';
const layout = qs.get('layout') || 'std';
const zoom = parseFloat(qs.get('zoom') || '1.25');
document.getElementById('mode').textContent = mode === 'ph' ? '占位符号（基线）' : '生成图（5 张）';

const f = document.getElementById('f');
const sleep = ms => new Promise(r => setTimeout(r, ms));

(async () => {
  await new Promise(r => f.addEventListener('load', r, { once: true }));
  const D = f.contentDocument, W = f.contentWindow;
  await sleep(300);
  const cls = [...D.querySelectorAll('button')].find(b => /下潜者/.test(b.textContent));
  if (cls) cls.click();
  await sleep(500);
  for (let i = 0; i < 8; i++) {
    const n = D.querySelector('.mnode.pickable');
    if (n) { n.click(); await sleep(600); }
    if (D.querySelector('#hand .card')) break;
    await sleep(300);
  }
  const applyAll = () => {
    const cs = [...D.querySelectorAll('#hand .card')];
    if (!cs.length) return;
    if (layout === 'fullbleed') {
      cs.forEach(c => {
        if (c.querySelector('.textslab')) return;      // 已经处理过
        const slab = D.createElement('div'); slab.className = 'textslab';
        ['.cname', '.cveins', '.ctext', '.cflavor'].forEach(sel => {
          const n = c.querySelector(sel); if (n) slab.appendChild(n);
        });
        c.appendChild(slab);
      });
    }
    cs.forEach((c, i) => {
      const pic = PICS[i % PICS.length];
      const art = c.querySelector('.art');
      if (!art) return;
      art.style.backgroundImage = 'url(' + pic.uri + ')';
      // zoom>1：把素材自带的黑边框裁掉（我们的测试图多数带密教式内框）
      art.style.backgroundSize = (fit === 'contain') ? 'contain' : (zoom + '00% auto');
      art.style.backgroundPosition = 'center';
      const ph = art.querySelector('.art-ph');
      if (ph) ph.style.display = 'none';
    });
    // 右侧信息区里的那张大卡，也贴上同一张图（按卡名在手牌里找同名牌）
    const info = D.querySelector('#card-detail');
    if (info && !info.classList.contains('hidden')) {
      const pc = info.querySelector('.card');
      const nm = pc && pc.querySelector('.cname');
      if (pc && nm) {
        const src = cs.find(h => {
          const n = h.querySelector('.cname');
          return n && n.textContent.trim() === nm.textContent.trim();
        });
        const a1 = src && src.querySelector('.art');
        const a2 = pc.querySelector('.art');
        if (a1 && a2 && a1.style.backgroundImage) {
          a2.style.backgroundImage = a1.style.backgroundImage;
          a2.style.backgroundSize = a1.style.backgroundSize;
          a2.style.backgroundPosition = 'center';
          const ph2 = a2.querySelector('.art-ph');
          if (ph2) ph2.style.display = 'none';
        }
      }
    }
  };

  // layout=fullbleed：图铺满整张卡，文字压在下方的纸片上（1a 方案 mock）
  if (layout === 'fullbleed') {
    const css = [
      '#hand .card{overflow:hidden;padding:0!important;}',
      '#hand .card .art{position:absolute!important;inset:0;height:auto!important;border-bottom:0!important;}',
      '#hand .card .cost{position:absolute;left:5px;top:5px;z-index:6;}',
      '#hand .card .ctype{position:absolute;right:6px;top:6px;z-index:6;}',
      '#hand .card .textslab{position:absolute;left:0;right:0;bottom:0;z-index:5;',
      'max-height:52%;overflow:hidden;padding:5px 7px 6px;',
      'background:rgba(217,207,190,.93);border-top:1px solid #8a7050;',
      'box-shadow:0 -4px 10px rgba(0,0,0,.35);}',
      '#hand .card .textslab .cname{font-size:12px;line-height:1.25;}',
      '#hand .card .textslab .cveins{margin-top:2px;}',
      '#hand .card .textslab .ctext{font-size:10.5px;line-height:1.3;margin-top:2px;}',
      '#hand .card .textslab .cflavor{display:none;}'
    ].join('');
    const st = D.createElement('style'); st.textContent = css; D.head.appendChild(st);
  }

  if (mode === 'ph') return;
  applyAll();
  // 出牌/抽牌会整体重渲染手牌，一次性注入会被冲掉 → 监听 #hand 变化后重贴
  const hand = D.querySelector('#hand');
  if (hand) {
    const mo = new MutationObserver(() => { clearTimeout(applyAll._t); applyAll._t = setTimeout(applyAll, 30); });
    mo.observe(hand, { childList: true, subtree: true });
  }
  // 右侧信息区显示/隐藏、换卡时也重贴一次
  const infoBox = D.querySelector('#card-detail');
  if (infoBox) {
    const mo2 = new MutationObserver(() => { clearTimeout(applyAll._t2); applyAll._t2 = setTimeout(applyAll, 30); });
    mo2.observe(infoBox, { childList: true, subtree: true, attributes: true, attributeFilter: ['class'] });
  }
})();
</script>
</body></html>
"""
    html = html.replace('[ITEMS]', '[' + items + ']')
    OUT.write_text(html, encoding='utf-8')
    print('wrote', OUT, round(OUT.stat().st_size / 1024), 'KB')


if __name__ == '__main__':
    main()
