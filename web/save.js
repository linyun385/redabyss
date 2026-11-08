/* 红渊 · 存档模块 v1
 *
 * 定位：纯数据处理，不碰 UI、不依赖 index.html 里的任何变量。
 * index.html 负责「什么时候存 / 什么时候读」，这里只负责「怎么变成字符串 / 怎么变回来」。
 *
 * 为什么这么做：
 *   run 里唯一的非数据成员是 rng（闭包里藏着 LCG 状态），不能 JSON 化。
 *   引擎的 makeRng 已加 getState()/setState()，所以存档只存一个整数种子状态，
 *   恢复时把状态塞回去，后续随机序列与刷新前完全一致。
 *
 * 存档粒度：只在「安全点」存（回到地图时）。战斗中刷新 = 回到该场战斗之前，
 *   不会丢整局，但会丢这一场。战斗对象 C 含大量运行时引用，序列化它风险远大于收益。
 */
(function (global) {
  'use strict';

  var VERSION = 2;                       // 存档格式版本，牌池结构变了就 +1，旧档自动作废
  var KEY = 'redabyss_run_save';
  var LOG_KEEP = 40;                     // 战斗日志只留最后 40 条
  var MAX_BYTES = 3 * 1024 * 1024;       // 超过 3MB 就拒绝写，避免污染 localStorage

  var _lastError = null;

  function _err(where, e) {
    _lastError = where + ': ' + (e && e.message ? e.message : String(e));
    return null;
  }

  /* 深拷贝并丢掉一切不可序列化的东西（函数、DOM、循环引用）。循环引用直接放弃该字段。 */
  function _plain(val) {
    if (val === null || typeof val !== 'object') return val;
    try {
      return JSON.parse(JSON.stringify(val));
    } catch (e) {
      return undefined;
    }
  }

  /* run → 存档对象
   * 白名单式会漏字段（newRun 和 startRun 各补一批，将来还会加），所以反过来做排除：
   * 遍历所有自有属性，只特殊处理 rng 和 log，其余一锅端。
   */
  function snapshot(run) {
    if (!run || typeof run !== 'object') return null;
    var fields = {};
    var skipped = [];
    for (var k in run) {
      if (!Object.prototype.hasOwnProperty.call(run, k)) continue;
      if (k === 'rng' || k === 'log') continue;
      var v = run[k];
      if (v === undefined) continue;                 // undefined 不存，恢复时 newRun 给默认值
      if (typeof v === 'function') { skipped.push(k); continue; }
      var p = _plain(v);
      if (p === undefined) { skipped.push(k); continue; }
      fields[k] = p;
    }

    var out = {
      v: VERSION,
      ts: Date.now(),
      fields: fields,
      logTail: _plain((run.log || []).slice(-LOG_KEEP)) || [],
      rngState: (run.rng && typeof run.rng.getState === 'function') ? run.rng.getState() : null
    };
    if (skipped.length) out._skipped = skipped;
    return out;
  }

  /* 存档对象 → 还原到 run 上（就地改，不新建对象）
   * run 必须是引擎真正 newRun 出来的实例，否则 rng 没有 setState。
   */
  function applyTo(run, data) {
    if (!run || !data || data.v !== VERSION) return null;
    if (!data.fields) return null;
    for (var k in data.fields) {
      if (!Object.prototype.hasOwnProperty.call(data.fields, k)) continue;
      run[k] = data.fields[k];
    }
    if (data.logTail) run.log = data.logTail;
    if (data.rngState != null && run.rng && typeof run.rng.setState === 'function') {
      run.rng.setState(data.rngState);
    }
    return run;
  }

  /* 校验：能读出来、版本对、有 classId、牌组非空。读不出来就当没存过。 */
  function load() {
    var raw;
    try {
      raw = global.localStorage.getItem(KEY);
    } catch (e) {
      return _err('localStorage.getItem', e);
    }
    if (!raw) return null;
    var data;
    try {
      data = JSON.parse(raw);
    } catch (e) {
      clear();                                        // 坏了就清掉，别每次启动都报错
      return _err('JSON.parse', e);
    }
    if (!data || data.v !== VERSION) { clear(); return null; }
    if (!data.fields || !data.fields.classId) { clear(); return null; }
    if (!Array.isArray(data.fields.deck) || !data.fields.deck.length) { clear(); return null; }
    return data;
  }

  function save(run) {
    var data = snapshot(run);
    if (!data) return false;
    var json;
    try {
      json = JSON.stringify(data);
    } catch (e) {
      return _err('JSON.stringify', e) || false;
    }
    if (json.length > MAX_BYTES) {
      _lastError = '存档过大: ' + json.length + ' 字节';
      return false;
    }
    try {
      global.localStorage.setItem(KEY, json);
      _lastError = null;
      return true;
    } catch (e) {
      // 配额满（QuotaExceededError）：清掉自己的旧档再试一次，仍失败就放弃
      try { global.localStorage.removeItem(KEY); } catch (e2) {}
      try {
        global.localStorage.setItem(KEY, json);
        return true;
      } catch (e3) {
        return _err('localStorage.setItem', e3) || false;
      }
    }
  }

  function clear() {
    try { global.localStorage.removeItem(KEY); } catch (e) {}
    return true;
  }

  function has() {
    return !!load();
  }

  /* 给人看的一行摘要：职业、层、血量、牌数、多久之前 */
  var CLASS_NAMES = { diver: '潜行者', tremor: '震民', anmin: '黯民', cangmin: '苍民' };
  function info() {
    var d = load();
    if (!d) return null;
    var f = d.fields;
    return {
      classId: f.classId,
      className: CLASS_NAMES[f.classId] || f.classId,
      depth: f.depth || 1,
      hp: f.hp,
      maxHp: f.maxHp,
      deckSize: (f.deck || []).length,
      relics: (f.relics || []).length,
      ts: d.ts,
      ageText: ageText(d.ts)
    };
  }

  function ageText(ts) {
    if (!ts) return '';
    var s = Math.floor((Date.now() - ts) / 1000);
    if (s < 60) return '刚刚';
    if (s < 3600) return Math.floor(s / 60) + ' 分钟前';
    if (s < 86400) return Math.floor(s / 3600) + ' 小时前';
    return Math.floor(s / 86400) + ' 天前';
  }

  function _debug() {
    return {
      version: VERSION,
      key: KEY,
      has: (function () { try { return !!global.localStorage.getItem(KEY); } catch (e) { return false; } })(),
      bytes: (function () { try { var r = global.localStorage.getItem(KEY); return r ? r.length : 0; } catch (e) { return -1; } })(),
      lastError: _lastError,
      info: info()
    };
  }

  global.Save = {
    VERSION: VERSION,
    KEY: KEY,
    snapshot: snapshot,
    applyTo: applyTo,
    save: save,
    load: load,
    clear: clear,
    has: has,
    info: info,
    ageText: ageText,
    _debug: _debug
  };
})(typeof window !== 'undefined' ? window : this);
