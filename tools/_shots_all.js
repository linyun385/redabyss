// 全屏截图器（CDP 直连）—— 把战斗屏以外的所有界面各截一张
// 用法：node tools/_shots_all.js
// 产出：docs/design/ui_shots/v4/*.png
const fs = require('fs');
const os = require('os');
const path = require('path');
const { spawn } = require('child_process');

const ROOT = path.join(__dirname, '..');
const OUT = path.join(ROOT, 'docs', 'design', 'ui_shots', 'v4');
const PORT = 9335;
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

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'shots-'));
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
      console.log('  ' + name + '.png (' + Math.round(fs.statSync(p).size / 1024) + ' KB)');
    };
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

    await client.send('Page.navigate', { url: URL_FILE });
    await sleep(2600);

    console.log('① 选人页');
    await shot('a_home');

    console.log('② 职业详情（维护者）');
    await run("document.querySelector('.classface[data-class=\"anmin\"]').click()", 'open class modal');
    await sleep(700);
    await shot('b_classmodal');
    await run("document.getElementById('class-modal-close').click()", 'close class modal');
    await sleep(400);

    console.log('③ 地图');
    await run("startRun('anmin')", 'startRun');
    await sleep(1400);
    await shot('c_map');

    console.log('④ 地图（悬停一个可选节点）');
    await run(`(function(){
      var n = document.querySelector('#flow-panel .mnode.pickable');
      if (!n) return 'no pickable node';
      n.dispatchEvent(new MouseEvent('mouseenter', {bubbles:true}));
      n.classList.add('hover');
      return n.textContent.slice(0,20);
    })()`, 'hover node');
    await sleep(500);
    await shot('d_map_hover');

    console.log('⑤ 帮助页');
    await run("document.getElementById('help-overlay').classList.remove('hidden')", 'show help');
    await sleep(500);
    await shot('e_help');
    await run("document.getElementById('help-overlay').classList.add('hidden')", 'hide help');

    console.log('⑥ 地图整体滚动高度（如果可滚）');
    const dims = await run(`(function(){
      var fp = document.getElementById('flow-panel');
      var sp = document.getElementById('screen-flow');
      var svg = document.querySelector('#flow-panel svg') || document.querySelector('#flow-panel .mapwrap');
      function r(el){ if(!el) return null; var b=el.getBoundingClientRect();
        return {l:Math.round(b.left),t:Math.round(b.top),w:Math.round(b.width),h:Math.round(b.height),
                sw:el.scrollWidth,sh:el.scrollHeight}; }
      return { flowPanel: r(fp), screenFlow: r(sp), mapSvg: r(svg),
               children: fp ? fp.children.length : -1 };
    })()`, 'measure map');
    console.log('  ' + JSON.stringify(dims));

    console.log('完成 → ' + OUT);
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
