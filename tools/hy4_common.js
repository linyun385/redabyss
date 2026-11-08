// HY4 批次 3 共用解析工具
// 用途：从 web/index.html 里把 `const RAW = {...}` 这一整行 JSON 抠出来，并读取 cards/*.json。
// 解析方式与 tools/_sync_cards.js 完全一致：字符串定位 + 大括号深度扫描（不用正则）。
'use strict';
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const WEB = path.join(ROOT, 'web', 'index.html');
const CARDS = path.join(ROOT, 'cards');
const MARK = 'const RAW = ';

// 卡池的 5 个数组键（其余 enemies/relics/events/layers/... 不是卡牌，不计入卡池）
const POOL_KEYS = ['diver', 'tremor', 'anmin', 'cangmin', 'shared'];
// 四个玩家职业（shared 为共用牌，Y5 的横向对比不把它当职业）
const CLASS_KEYS = ['diver', 'tremor', 'anmin', 'cangmin'];

function readWeb() {
  return fs.readFileSync(WEB, 'utf8');
}

// 返回 { raw, rawText, bodyStart, bodyEnd, webText }
function readRaw() {
  const s = readWeb();
  const start = s.indexOf(MARK);
  if (start < 0) throw new Error('找不到 const RAW = ');
  const bodyStart = start + MARK.length;
  let depth = 0, inStr = false, esc = false, i = bodyStart;
  for (; i < s.length; i++) {
    const ch = s[i];
    if (inStr) {
      if (esc) esc = false;
      else if (ch === '\\') esc = true;
      else if (ch === '"') inStr = false;
      continue;
    }
    if (ch === '"') inStr = true;
    else if (ch === '{') depth++;
    else if (ch === '}') { depth--; if (depth === 0) { i++; break; } }
  }
  if (depth !== 0) throw new Error('RAW 括号未闭合，depth=' + depth);
  const bodyEnd = i;
  const rawText = s.slice(bodyStart, bodyEnd);
  return { raw: JSON.parse(rawText), rawText, bodyStart, bodyEnd, webText: s };
}

function readCardJson(cls) {
  const p = path.join(CARDS, cls + '.json');
  return { text: fs.readFileSync(p, 'utf8'), data: JSON.parse(fs.readFileSync(p, 'utf8')), path: p };
}

// 去掉 JSON 文本中「字符串字面量之外」的所有空白，用于逐字节级文本比对
function stripJsonWhitespace(text) {
  let out = '', inStr = false, esc = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (inStr) {
      out += c;
      if (esc) esc = false;
      else if (c === '\\') esc = true;
      else if (c === '"') inStr = false;
    } else if (c === '"') { inStr = true; out += c; }
    else if (/\s/.test(c)) { /* 跳过 */ }
    else out += c;
  }
  return out;
}

// 稳定序列化：键按字典序排列，消除两份数据「键顺序不同」带来的假差异
function stable(v) {
  if (Array.isArray(v)) return '[' + v.map(stable).join(',') + ']';
  if (v && typeof v === 'object') {
    return '{' + Object.keys(v).sort().map(k => JSON.stringify(k) + ':' + stable(v[k])).join(',') + '}';
  }
  return JSON.stringify(v);
}

// 把 RAW 中属于卡池的所有卡摊平，带职业标签
function flatPool(raw, keys) {
  const out = [];
  for (const k of (keys || POOL_KEYS)) {
    if (!Array.isArray(raw[k])) continue;
    for (const c of raw[k]) out.push({ pool: k, card: c });
  }
  return out;
}

// 取一张卡所有 special 条目：主效果 + 升级效果
function specialsOf(card) {
  const out = [];
  const push = (arr, where) => {
    if (!Array.isArray(arr)) return;
    arr.forEach((s, idx) => out.push({ where, idx, code: s && s.code, raw: s }));
  };
  push(card && card.effect && card.effect.special, 'effect');
  push(card && card.upgrade && card.upgrade.effect && card.upgrade.effect.special, 'upgrade.effect');
  return out;
}

module.exports = {
  ROOT, WEB, CARDS, MARK, POOL_KEYS, CLASS_KEYS,
  readWeb, readRaw, readCardJson, stripJsonWhitespace, stable, flatPool, specialsOf
};
