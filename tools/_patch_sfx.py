# -*- coding: utf-8 -*-
"""把音效播放器接进 web/index.html。

做法：不动 playSfx（它已经会转发给 window.RedAbyssSFX），只做两件事——
  1. setLayerAmbience 里加一行转发到 window.RedAbyssAmbience
  2. 在它后面插入播放器实现（IIFE，自包含）

先演练：python tools/_patch_sfx.py
真写：  python tools/_patch_sfx.py --apply
"""
import sys
import shutil
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
GAME = Path(__file__).resolve().parents[1]
HTML = GAME / 'web' / 'index.html'

OLD_AMB = '''/* 氛围音预留：按层切换背景循环音。空实现，清单见 docs/SFX_LIST.md。 */
function setLayerAmbience(depth) {
  if (window.__SFX_LOG) window.__SFX_LOG.push('ambience.depth' + depth);
}'''

NEW_AMB = '''/* 氛围音：按层切换背景循环音（2026-11-05 接上实现，清单见 docs/SFX_LIST.md）。 */
function setLayerAmbience(depth) {
  if (window.__SFX_LOG) window.__SFX_LOG.push('ambience.depth' + depth);
  try { if (typeof window.RedAbyssAmbience === 'function') window.RedAbyssAmbience(depth); } catch (e) {}
}
/* ───────── 音效播放器（2026-11-05）─────────
   通道约定是 T41 定的，这里只补实现，不改接口：
     window.RedAbyssSFX(code, opts)    播一个短音效（playSfx 会自动转发过来）
     window.RedAbyssAmbience(depth)    切氛围层，1..8；0 或越界 = 停
     window.RedAbyssVolume(0..1)       总音量，存 localStorage
     window.__SFX_MUTED                静音（playSfx 里已经拦了）
   浏览器限制：AudioContext 必须等用户第一次交互后才能出声，所以 ctx 是懒建的。
   音频文件：web/sfx/<code>.wav，28 个（20 音效 + 8 氛围），由 tools/sfx_synth_full.py 生成。 */
(function () {
  var AC = window.AudioContext || window.webkitAudioContext;
  if (!AC) return;
  var ctx = null, master = null, buffers = {};
  var ambSrc = null, ambGain = null, ambDepth = 0;
  var VOL = 0.7;
  try { var sv = localStorage.getItem('redabyss_volume'); if (sv != null) VOL = Math.max(0, Math.min(1, +sv)); } catch (e) {}

  function ensure() {
    if (ctx) return true;
    try {
      ctx = new AC();
      master = ctx.createGain();
      master.gain.value = VOL;
      master.connect(ctx.destination);
    } catch (e) { ctx = null; return false; }
    return true;
  }
  function resume() { if (ctx && ctx.state === 'suspended') { try { ctx.resume(); } catch (e) {} } }

  function load(name) {
    if (buffers[name]) return Promise.resolve(buffers[name]);
    return fetch('sfx/' + name + '.wav')
      .then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.arrayBuffer(); })
      .then(function (ab) { return ctx.decodeAudioData(ab); })
      .then(function (b) { buffers[name] = b; return b; })
      .catch(function () { return null; });
  }

  window.RedAbyssSFX = function (code, opts) {
    if (!ensure()) return;
    resume();
    load(code).then(function (buf) {
      if (!buf) return;
      var src = ctx.createBufferSource();
      src.buffer = buf;
      var g = ctx.createGain();
      g.gain.value = (opts && opts.gain != null) ? opts.gain : 1;
      src.connect(g); g.connect(master);
      src.start();
    });
  };

  window.RedAbyssAmbience = function (depth) {
    if (!ensure()) return;
    resume();
    depth = depth | 0;
    if (depth === ambDepth) return;
    if (ambSrc) { try { ambSrc.stop(); } catch (e) {} ambSrc = null; }
    if (ambGain) { try { ambGain.disconnect(); } catch (e) {} ambGain = null; }
    ambDepth = depth;
    if (depth < 1 || depth > 8) return;
    if (window.__SFX_MUTED) return;
    load('ambience.depth' + depth).then(function (buf) {
      if (!buf || ambDepth !== depth) return;
      var src = ctx.createBufferSource();
      src.buffer = buf; src.loop = true;
      var g = ctx.createGain();
      g.gain.value = 0.0001;
      g.gain.exponentialRampToValueAtTime(0.55, ctx.currentTime + 1.5);
      src.connect(g); g.connect(master);
      src.start();
      ambSrc = src; ambGain = g;
    });
  };

  window.RedAbyssVolume = function (v) {
    VOL = Math.max(0, Math.min(1, +v || 0));
    if (master) master.gain.value = VOL;
    try { localStorage.setItem('redabyss_volume', VOL); } catch (e) {}
  };

  // 第一次交互时解锁 ctx + 预载全部短音效（氛围音按层加载，不占首屏）
  document.addEventListener('pointerdown', function once() {
    ensure(); resume();
    var list = ['card.play.attack', 'card.play.skill', 'card.play.power', 'card.play.cost',
      'combat.start', 'enemy.hit', 'combat.hurt', 'combat.block', 'combat.kill',
      'state.resonance', 'state.gaze', 'state.energy_empty',
      'ui.click', 'ui.open', 'ui.close',
      'special.boss_phase', 'special.world_switch', 'special.egg', 'special.victory', 'special.death'];
    for (var i = 0; i < list.length; i++) load(list[i]);
    document.removeEventListener('pointerdown', once);
  }, { once: true });
})();'''


def main():
    apply = '--apply' in sys.argv
    src = HTML.read_text(encoding='utf-8')

    n_old = src.count(OLD_AMB)
    n_play = src.count('function playSfx(code, opts)')
    n_log = src.count('window.__SFX_LOG')
    print('index.html: %d 字节，%d 行' % (len(src.encode('utf-8')), src.count('\n') + 1))
    print('OLD_AMB 匹配: %d 次（必须是 1）' % n_old)
    print('playSfx 存在: %d 次（必须是 1）' % n_play)
    print('__SFX_LOG 出现: %d 次' % n_log)

    if n_old != 1:
        print('\n!! OLD_AMB 不是恰好 1 次，停下。')
        return 2

    out = src.replace(OLD_AMB, NEW_AMB, 1)
    if not apply:
        print('\n[演练] 替换后 %d 字节（+%d）。加 --apply 才真写。'
              % (len(out.encode('utf-8')), len(out.encode('utf-8')) - len(src.encode('utf-8'))))
        print('预览新插入片段首行：')
        print('\n'.join(NEW_AMB.split('\n')[:6]))
        return 0

    bak = HTML.with_name('index.html.bak-%s-sfx' % datetime.now().strftime('%Y%m%d-%H%M%S'))
    shutil.copy2(str(HTML), str(bak))
    print('\n备份:', bak.name)
    HTML.write_text(out, encoding='utf-8')
    print('已写入，%d 字节' % len(out.encode('utf-8')))

    # 立刻自检：改完再读一遍确认
    chk = HTML.read_text(encoding='utf-8')
    print('复查 RedAbyssSFX:', chk.count('window.RedAbyssSFX'), '次')
    print('复查 RedAbyssAmbience:', chk.count('window.RedAbyssAmbience'), '次')
    print('复查 setLayerAmbience 转发:', chk.count("typeof window.RedAbyssAmbience === 'function'"), '次')
    return 0


if __name__ == '__main__':
    sys.exit(main())
