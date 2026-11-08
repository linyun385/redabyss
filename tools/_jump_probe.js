// 跳动探针（CDP 直连）—— 查「点牌/出牌时画面跳一下」到底谁在动
// 用法：node tools/_jump_probe.js
// 不截图，只量矩形。输出每一步前后关键元素的坐标与宽度。
const fs = require('fs');
const os = require('os');
const path = require('path');
const { spawn } = require('child_process');

const ROOT = path.join(__dirname, '..');
const PORT = 9334;
const URL_FILE = 'file:///' + path.join(ROOT, 'web', 'index.html').replace(/\\/g, '/')
  .split('/').map(s => encodeURIComponent(s)).join('/').replace('file%3A//', 'file:///');

const EDGE = [
  'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
  'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe',
  'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'
].find(p => fs.existsSync(p));
if (!EDGE) { console.error('找不到浏览器'); process.exit(1); }

const sleep = ms => new Promise(r => setTimeout(r, ms));

function makeClient(wsUrl) {
  const ws = new WebSocket(wsUrl);
  let id = 0;
  const pending = new Map();
  const ready = new Promise((res, rej) => {
    ws.addEventListener('open', () => res());
    ws.addEventListener('error', () => rej(new Error('ws error')));
  });
  ws.addEventListener('message', ev => {
    let msg;
    try { msg = JSON.parse(ev.data); } catch (e) { return; }
    if (msg.id && pending.has(msg.id)) {
      const { res, rej } = pending.get(msg.id);
      pending.delete(msg.id);
      msg.error ? rej(new Error(msg.error.message)) : res(msg.result);
    }
  });
  const send = (method, params) => new Promise((res, rej) => {
    const myId = ++id;
    pending.set(myId, { res, rej });
    ws.send(JSON.stringify({ id: myId, method, params: params || {} }));
    setTimeout(() => {
      if (pending.has(myId)) { pending.delete(myId); rej(new Error('timeout: ' + method)); }
    }, 20000);
  });
  return { ready, send, close: () => ws.close() };
}

async function getWsUrl() {
  for (let i = 0; i < 40; i++) {
    try {
      const r = await fetch('http://127.0.0.1:' + PORT + '/json/list');
      const list = await r.json();
      const page = list.find(t => t.type === 'page');
      if (page && page.webSocketDebuggerUrl) return page.webSocketDebuggerUrl;
    } catch (e) {}
    await sleep(300);
  }
  throw new Error('CDP 端口没起来');
}

// 页面里的采样器：返回一行紧凑文本
const SAMPLER = `(function () {
  function r(sel) {
    var el = document.querySelector(sel);
    if (!el) return null;
    var b = el.getBoundingClientRect();
    return { l: Math.round(b.left * 10) / 10, t: Math.round(b.top * 10) / 10,
             w: Math.round(b.width * 10) / 10, h: Math.round(b.height * 10) / 10 };
  }
  var de = document.documentElement;
  var hand = document.getElementById('hand');
  var cards = [].map.call(document.querySelectorAll('#hand .card'), function (c) {
    var b = c.getBoundingClientRect();
    return Math.round(b.left * 10) / 10;
  });
  var cd = document.getElementById('card-detail');
  return {
    win: window.innerWidth,
    clientW: de.clientWidth,          // 出现纵向滚动条时会变小
    sbar: window.innerWidth - de.clientWidth,
    scale: (getComputedStyle(de).getPropertyValue('--ui-scale') || '').trim(),
    handW: hand ? hand.clientWidth : -1,
    app: r('#app'),
    handArea: r('#hand-area'),
    log: r('#log'),
    cdHidden: cd ? cd.classList.contains('hidden') : null,
    cdRect: r('#card-detail'),
    cardsLeft: cards
  };
})()`;

(async () => {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'jump-'));
  const proc = spawn(EDGE, [
    '--headless=new', '--disable-gpu', '--hide-scrollbars',
    '--remote-debugging-port=' + PORT,
    '--user-data-dir=' + tmp,
    '--window-size=1600,900',
    '--force-device-scale-factor=1',
    'about:blank'
  ], { stdio: 'ignore' });

  let client;
  try {
    const wsUrl = await getWsUrl();
    client = makeClient(wsUrl);
    await client.ready;
    await client.send('Page.enable');
    await client.send('Runtime.enable');
    await client.send('Emulation.setDeviceMetricsOverride', {
      width: 1600, height: 900, deviceScaleFactor: 1, mobile: false
    });

    const run = async (expr, label) => {
      const r = await client.send('Runtime.evaluate', {
        expression: expr, returnByValue: true, awaitPromise: true
      });
      if (r.exceptionDetails) {
        console.log('  [失败] ' + label + ': ' +
          ((r.exceptionDetails.exception || {}).description || '').split('\n')[0]);
        return null;
      }
      return r.result && r.result.value;
    };
    const sample = async () => run(SAMPLER);
    const line = (tag, s) => {
      if (!s) { console.log(tag + ' -> null'); return; }
      console.log(tag +
        ' | win=' + s.win + ' clientW=' + s.clientW + ' sbar=' + s.sbar +
        ' scale=' + s.scale + ' handW=' + s.handW +
        ' cdHidden=' + s.cdHidden +
        '\n    app=' + JSON.stringify(s.app) +
        '\n    handArea=' + JSON.stringify(s.handArea) +
        '\n    log=' + JSON.stringify(s.log) +
        '\n    cdRect=' + JSON.stringify(s.cdRect) +
        '\n    cardsLeft=' + JSON.stringify(s.cardsLeft));
    };
    // 连续采样 n 帧，报告是否与首帧不同
    const watch = async (tag, frames) => {
      const first = await sample();
      const diffs = [];
      for (let i = 0; i < frames; i++) {
        await run('new Promise(function(r){requestAnimationFrame(function(){r(1)})})');
        const s = await sample();
        const a = JSON.stringify({ app: s.app, ha: s.handArea, log: s.log, cl: s.cardsLeft, hw: s.handW, cw: s.clientW, cd: s.cdHidden });
        const b = JSON.stringify({ app: first.app, ha: first.handArea, log: first.log, cl: first.cardsLeft, hw: first.handW, cw: first.clientW, cd: first.cdHidden });
        if (a !== b) diffs.push({ f: i + 1, s: s });
      }
      if (!diffs.length) {
        console.log('  ' + tag + ': ' + frames + ' 帧无变化');
      } else {
        console.log('  ' + tag + ': ' + diffs.length + '/' + frames + ' 帧有变化');
        line('    首帧', first);
        line('    变化帧', diffs[0].s);
      }
      return first;
    };

    console.log('打开页面…');
    await client.send('Page.navigate', { url: URL_FILE });
    await sleep(2500);

    console.log('开局 anmin…');
    await run("startRun('anmin')", 'startRun');
    await sleep(1000);

    console.log('进战斗…');
    const bw = await run(`
      (function () {
        try {
          var def = (RAW.anminEnemies || []).filter(function (e) { return e && e.layer === 1; })[0]
                 || (RAW.enemies || []).filter(function (e) { return e && e.layer === 1; })[0];
          if (!def) return 'no enemy def';
          startCombatFlow([def]);
          return 'ok:' + def.id;
        } catch (e) { return 'err:' + e.message; }
      })()`, 'startCombatFlow');
    console.log('  ' + bw);
    await sleep(1500);

    const h0 = await sample();
    line('\n[基线]', h0);

    // ① 点牌：只调 openCardDetail，不拖动（复现「点击」路径）
    console.log('\n① openCardDetail(0) —— 模拟「点一下牌」');
    await run("openCardDetail(0)", 'openCardDetail');
    await watch('openCardDetail 后', 8);

    // ② 关掉详情
    console.log('\n② 收起详情');
    await run("document.getElementById('card-detail').classList.add('hidden')", 'hide cd');
    await watch('隐藏详情后', 8);

    // ③ 直接重排手牌：看 layoutFan 自己会不会挪牌
    console.log('\n③ layoutFan() 单独调用（不涉及任何状态变化）');
    await watch('layoutFan 后', 8);

    // ④ 真正打出一张牌
    console.log('\n④ doPlay(0) —— 真出牌');
    const played = await run(`
      (function () {
        try {
          if (typeof doPlay !== 'function') return 'doPlay 不是全局函数';
          doPlay(0, undefined);
          return 'ok';
        } catch (e) { return 'err:' + e.message; }
      })()`, 'doPlay(0)');
    console.log('  ' + played);
    await watch('doPlay 后', 10);

    console.log('\n完成');
  } catch (e) {
    console.error('失败: ' + e.message);
    process.exitCode = 1;
  } finally {
    if (client) client.close();
    try { proc.kill(); } catch (e) {}
    await sleep(500);
    try { fs.rmSync(tmp, { recursive: true, force: true }); } catch (e) {}
  }
})();
