// UI 截图器（CDP 直连，不依赖 puppeteer）
// 用法：node tools/_ui_capture.js
// 产出：docs/design/ui_shots/*.png
//
// 思路：headless Edge 开 remote-debugging-port，node 用内置 WebSocket 连上去，
// Runtime.evaluate 驱动游戏内部函数（顶层 function 声明在全局作用域，可直接调），
// Page.captureScreenshot 取图。
const fs = require('fs');
const os = require('os');
const path = require('path');
const { spawn } = require('child_process');

const ROOT = path.join(__dirname, '..');
const OUT = path.join(ROOT, 'docs', 'design', 'ui_shots');
const PORT = 9333;
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
    ws.addEventListener('error', e => rej(new Error('ws error')));
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

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'ui-cap-'));
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

    const shot = async (name) => {
      const { data } = await client.send('Page.captureScreenshot', { format: 'png' });
      const p = path.join(OUT, name + '.png');
      fs.writeFileSync(p, Buffer.from(data, 'base64'));
      console.log('  截图 ' + name + '.png (' + Math.round(fs.statSync(p).size / 1024) + ' KB)');
    };
    const run = async (expr, label) => {
      const r = await client.send('Runtime.evaluate', {
        expression: expr, returnByValue: true, awaitPromise: true
      });
      if (r.exceptionDetails) {
        console.log('  [失败] ' + label + ': ' + (r.exceptionDetails.exception || {}).description);
        return null;
      }
      const v = r.result && r.result.value;
      if (label) {
        const s = v === undefined ? 'undefined' : JSON.stringify(v);
        console.log('  [执行] ' + label + ' → ' + String(s).slice(0, 140));
      }
      return v;
    };

    console.log('打开: ' + URL_FILE);
    await client.send('Page.navigate', { url: URL_FILE });
    await sleep(2500);
    await shot('01_home');

    // 进入地图：直接调顶层 startRun
    await run("startRun('anmin')", 'startRun(anmin)');
    await sleep(1200);
    await shot('02_map');

    // 进战斗：取一个黯民敌人，直接开战
    const battleExpr = `
      (function () {
        try {
          var def = (RAW.anminEnemies || []).filter(function (e) { return e && e.layer === 1; })[0]
                 || (RAW.enemies || []).filter(function (e) { return e && e.layer === 1; })[0];
          if (!def) return 'no enemy def';
          startCombatFlow([def]);
          return 'ok:' + def.id;
        } catch (e) { return 'err:' + e.message; }
      })()`;
    await run(battleExpr, 'startCombatFlow');
    await sleep(1500);
    await shot('03_battle');

    // 实测各容器的水平中心，用来判断「没居中」到底是哪一层偏的
    const MEASURE = `(function () {
      function m(sel, key) {
        var el = document.querySelector(sel);
        if (!el) { return key + ':null'; }
        var b = el.getBoundingClientRect();
        return key + ': L' + Math.round(b.left) + ' W' + Math.round(b.width) + ' C' + Math.round(b.left + b.width / 2);
      }
      var out = [
        'winW=' + window.innerWidth,
        'clientW=' + document.documentElement.clientWidth,
        'scrollbar=' + (window.innerWidth - document.documentElement.clientWidth),
        m('#app', 'app'),
        m('#screen-combat', 'combat'),
        m('#enemy-area', 'enemyArea'),
        m('#log-wrap', 'logWrap'),
        m('#log', 'log'),
        m('#hand', 'hand'),
        m('#hand-area', 'handArea'),
        'enemies=' + document.querySelectorAll('#enemy-area .enemy').length
      ];
      var e = document.querySelector('#enemy-area .enemy');
      if (e) { var b = e.getBoundingClientRect(); out.push('enemy0: L' + Math.round(b.left) + ' W' + Math.round(b.width)); }
      return out.join(' | ');
    })()`;
    const meas = await client.send('Runtime.evaluate', { expression: MEASURE, returnByValue: true });
    console.log('  测量: ' + meas.result.value);

    // 牌局中：把手牌区单独截（滚动到可见）
    await run("document.getElementById('hand') && window.scrollTo(0, document.body.scrollHeight)", 'scroll');
    await sleep(500);
    await shot('04_battle_bottom');

    console.log('完成，输出目录: ' + OUT);
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
