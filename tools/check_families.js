#!/usr/bin/env node
/* -*- coding: utf-8 -*-
 * T79 校验器：素材形态族表（data/art_families.json）只读检查。
 *
 * 断言（对应 tasks/T79.md 验收表）：
 *   A1 三类覆盖率 100%（口径以 data/art_catalog.json 实际为准）
 *   A2 跨类别复用 = 0（同 id 出现在多类别 / 成员类别与族类别不符 / 重复成员）
 *   A3 每族 members ≤ 3
 *   A4 族内成员（≥2 时）至少共享 1 个「形态关键词」（词表启发式）
 *   A5 prompt 质量：每条 ≥3 个具体物名词；0 条命中 abstract/symbol/emblem 禁语
 *   A6 族 id 命名：foe_family_* / card_family_* / evt_<eventId>
 *   A7 style 档位：族表内一律 A（BOSS/结局 C 档不进族表）
 *
 * 统计输出：三类族数 / 覆盖率 / 复用率（成员数/族数）/ 单成员族占比 / 被最多共用的前 10 族。
 *
 * 只读：本脚本不写任何数据文件。退出码 0=全部断言通过，1=存在失败。
 */
'use strict';

const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const CATALOG = path.join(ROOT, 'data', 'art_catalog.json');
const FAMILIES = path.join(ROOT, 'data', 'art_families.json');

// families 的类目键 与 catalog 的 kind 的对应（事件在 catalog 里记作 evt）
const CAT_KEY = { foe: 'foe', card: 'card', event: 'event' };
const KIND_OF_CAT = { foe: 'foe', card: 'card', event: 'evt' };

/* ---------- 词表（启发式，人工可再补） ---------- */

// A4 形态关键词：中文名/描述里能当「同族证据」的形态/材质/器官词
const FORM_KEYWORDS = [
  // 生物形态
  '菌', '霉', '苔', '藻', '螨', '虫', '蛛', '鳗', '鱼', '蟹', '蛙', '龟', '蛇', '蠕', '蛆', '蝇', '蛾',
  '甲壳', '外骨骼', '壳', '触手', '触须', '须', '复眼', '单眼', '眼', '鳃', '鳍', '鳞', '爪', '足', '腿',
  '吸盘', '口器', '齿', '骨', '血', '肉', '皮', '膜', '囊', '伞', '孔', '腔', '翼', '刺', '毛',
  '卵', '蛹', '茧', '幼体', '人形', '直立', '四足', '多足', '无眼', '盲', '发光',
  // 非生物形态/材质
  '晶', '结晶', '盐', '锈', '裂', '铁', '铜', '钢', '铝', '玻璃', '胶', '绳', '纸', '印', '章', '墨',
  '灯', '管', '阀', '镜', '屏', '针', '线', '钉', '铆钉', '罐', '瓶', '桶', '布', '绷带', '面罩',
  '手套', '梯', '牌', '板', '匣', '柜', '棺', '碑', '尸', '遗体', '碎石', '蕨', '藤', '根', '灰', '尘', '雾',
  // 功能/姿态
  '倒挂', '倒吊', '攀附', '寄生', '共生', '食腐', '滤食', '钻孔', '挖掘', '悬浮', '漂浮', '贴附',
];

// A5 具体物名词（prompt 里可画的东西）：英文单数词干（匹配时自动含复数）+ 中文
const CONCRETE_NOUNS = [
  // 身体/器官
  'leg', 'gill', 'carapace', 'shell', 'chitin', 'armor', 'eye', 'tooth', 'teeth', 'jaw', 'claw',
  'limb', 'fin', 'scale', 'bone', 'skull', 'skin', 'rib', 'throat', 'belly', 'tail', 'tentacle',
  'tendril', 'sac', 'pore', 'mouth', 'organ', 'frond', 'spore', 'blister', 'membrane', 'spine',
  'spike', 'wing', 'stalk', 'bud', 'root', 'bud', 'blood',
  // 材质
  'metal', 'iron', 'steel', 'brass', 'copper', 'glass', 'cloth', 'fabric', 'leather', 'rope',
  'thread', 'strand', 'wire', 'cable', 'chain', 'paper', 'ink', 'wax', 'salt', 'crystal',
  'rust', 'dust', 'grime', 'slime', 'mold', 'moss', 'ash', 'soot', 'resin', 'mucus',
  // 器物
  'stamp', 'seal', 'valve', 'gauge', 'lens', 'hook', 'rivet', 'bracket', 'canister', 'jar',
  'bottle', 'tin', 'drum', 'lamp', 'lantern', 'candle', 'pencil', 'pen', 'clip', 'clamp', 'hinge',
  'latch', 'handle', 'grip', 'barrel', 'muzzle', 'rifle', 'gun', 'blade', 'knife', 'needle', 'pin',
  'bolt', 'gear', 'spring', 'coil', 'tank', 'pipe', 'conduit', 'duct', 'shaft', 'ladder', 'crate',
  'bucket', 'sack', 'sheet', 'page', 'book', 'ledger', 'card', 'tag', 'label', 'bandage', 'suit',
  'helmet', 'mask', 'faceplate', 'glove', 'boot', 'coat', 'apron', 'cart', 'rail', 'track', 'beam',
  'plank', 'brick', 'stone', 'rubble', 'gravel', 'sand', 'handwriting', 'knot', 'seam', 'scar',
  'weed', 'mine', 'cage', 'basket', 'funnel', 'noose', 'straw', 'reed', 'lichen', 'fungus',
  // 痕迹/纹理/状态（可画形容词）
  'crack', 'fissure', 'vein', 'crust', 'stain', 'mark', 'steam', 'droplet', 'frayed', 'scorched',
  'charred', 'burnt', 'scarred', 'warped', 'brittle', 'swollen', 'segmented', 'ribbed', 'braided',
  'knotted', 'encrusted', 'peeling', 'chipped', 'corroded', 'rusted', 'rusty', 'dusty', 'damp',
  // 环境
  'wall', 'floor', 'ceiling', 'corridor', 'tunnel', 'cavern', 'water', 'pool', 'growth',
  // 中文具体物
  '腿', '鳃', '甲', '锈', '裂', '血', '绳', '纸', '印', '章', '管', '阀', '镜', '屏', '针', '线',
  '钉', '罐', '瓶', '布', '绷带', '面罩', '手套', '梯', '牌', '板', '骨', '眼', '口', '齿', '爪',
  '鳍', '鳞', '膜', '囊', '孔', '苔', '霉', '盐', '晶', '灰', '尘', '铁', '钢', '铜', '玻璃',
];

// A5 禁语（T79 验收 #5：0 条命中）
const FORBIDDEN_RE = /\b(abstract|symbol|emblem)s?\b|\ba symbol of\b|abstract embodiment|minimal emblem/i;

/* ---------- 工具 ---------- */

function loadJson(p) {
  return JSON.parse(fs.readFileSync(p, 'utf8'));
}

// 从中文文本里抽取命中的形态关键词集合
function formKeywordsOf(text) {
  const hit = new Set();
  for (const kw of FORM_KEYWORDS) if (text.includes(kw)) hit.add(kw);
  return hit;
}

// 从 prompt 里数具体物名词命中数（按词形去重）
function concreteNounsOf(prompt) {
  const hit = new Set();
  for (const noun of CONCRETE_NOUNS) {
    if (noun === '中文') continue; // 分隔标记
    if (/[a-z]/.test(noun)) {
      const re = new RegExp('\\b' + noun.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + 's?\\b', 'i');
      if (re.test(prompt)) hit.add(noun);
    } else if (prompt.includes(noun)) {
      hit.add(noun);
    }
  }
  return hit;
}

/* ---------- 主流程 ---------- */

function main() {
  const cat = loadJson(CATALOG);
  const fam = loadJson(FAMILIES);
  const problems = [];   // 每条：[断言号, 消息]
  const warns = [];

  // 目录索引
  const byId = new Map();
  for (const it of cat) byId.set(it.id, it);
  const totals = { foe: 0, card: 0, evt: 0 };
  for (const it of cat) if (totals[it.kind] !== undefined) totals[it.kind]++;

  // 收集族表
  const usedIds = new Map();        // memberId -> [category, familyId]
  const covered = { foe: new Set(), card: new Set(), evt: new Set() };
  const famStats = { foe: [], card: [], event: [] };

  for (const category of ['foe', 'card', 'event']) {
    const bucket = fam[category] || {};
    for (const [fid, f] of Object.entries(bucket)) {
      const members = Array.isArray(f.members) ? f.members : [];
      famStats[category].push({ fid, name: f.name, members, style: f.style, prompt: f.prompt || '' });

      // A0/A2：成员存在性 + 类别归属 + 重复
      for (const m of members) {
        const item = byId.get(m);
        if (!item) {
          problems.push(['A2', `成员 ${m}（族 ${category}/${fid}）不在 art_catalog.json 里`]);
          continue;
        }
        if (item.kind !== KIND_OF_CAT[category]) {
          problems.push(['A2', `成员 ${m} 挂在「${category}」族 ${fid} 下，但 catalog 里 kind=${item.kind}（跨类别）`]);
        }
        if (usedIds.has(m)) {
          problems.push(['A2', `成员 ${m} 同时出现在 ${usedIds.get(m)} 和 ${category}/${fid}（跨类别/重复复用）`]);
        } else {
          usedIds.set(m, `${category}/${fid}`);
        }
        covered[item.kind].add(m);
      }

      // A3：成员 ≤3
      if (members.length > 3) {
        problems.push(['A3', `族 ${category}/${fid} 有 ${members.length} 个成员（>3，须拆族）`]);
      }

      // A4：≥2 成员时共享 ≥1 个形态关键词
      if (members.length >= 2) {
        const kwSets = members.map((m) => {
          const it = byId.get(m);
          return it ? formKeywordsOf(`${it.name || ''} ${it.desc || ''} ${it.extra || ''}`) : new Set();
        });
        let shared = [...kwSets[0]];
        for (let i = 1; i < kwSets.length; i++) shared = shared.filter((k) => kwSets[i].has(k));
        if (shared.length === 0) {
          problems.push(['A4', `族 ${category}/${fid}（${members.join(' , ')}）未共享任何形态关键词（词表启发式，请人工复核）`]);
        }
      }

      // A6：族 id 命名
      const okName =
        category === 'foe' ? /^foe_family_[a-z][a-z0-9_]*$/.test(fid) :
        category === 'card' ? /^card_family_[a-z][a-z0-9_]*$/.test(fid) :
        /^evt_[a-z0-9_]+$/.test(fid);
      if (!okName) problems.push(['A6', `族 id「${fid}」不符合命名规则（${category}）`]);

      // A5 + A7：prompt 质量 / style
      const prompt = (f.prompt || '').trim();
      if (!prompt) {
        problems.push(['A5', `族 ${category}/${fid} 缺 prompt`]);
      } else {
        const nouns = concreteNounsOf(prompt);
        if (nouns.size < 3) {
          problems.push(['A5', `族 ${category}/${fid} prompt 具体物名词仅 ${nouns.size} 个（<3）：[${[...nouns].join('、')}]`]);
        }
        if (FORBIDDEN_RE.test(prompt)) {
          problems.push(['A5', `族 ${category}/${fid} prompt 命中禁语（abstract/symbol/emblem）`]);
        }
      }
      if (f.style !== 'A') {
        warns.push(`族 ${category}/${fid} style=${JSON.stringify(f.style)}（族表内应为 A 档）`);
      }
    }
  }

  // A1：覆盖率
  const covRows = [];
  for (const [category, kind] of Object.entries(KIND_OF_CAT)) {
    const total = totals[kind] || 0;
    const cov = covered[kind].size;
    const pct = total ? (cov / total) * 100 : 0;
    covRows.push({ category, kind, total, cov, pct });
    if (cov !== total) {
      const miss = cat.filter((it) => it.kind === kind && !covered[kind].has(it.id));
      const show = miss.slice(0, 8).map((it) => it.id).join(', ');
      problems.push(['A1', `${category} 覆盖 ${cov}/${total}（${pct.toFixed(1)}%），缺 ${miss.length} 个，如：${show}${miss.length > 8 ? ' …' : ''}`]);
    }
  }

  /* ---------- 统计 ---------- */
  const line = '='.repeat(72);
  console.log(line);
  console.log('T79 形态族表校验（tools/check_families.js，只读）');
  console.log(`目录：data/art_catalog.json（${cat.length} 条）｜族表：data/art_families.json`);
  console.log(line);

  console.log('\n—— 统计 ——');
  console.log('类别      目录数   已覆盖  覆盖率    族数   复用率(成员/族)  单成员族  最大族');
  for (const r of covRows) {
    const list = famStats[r.category];
    const memberSum = list.reduce((s, f) => s + f.members.length, 0);
    const reuse = list.length ? (memberSum / list.length).toFixed(2) : '0.00';
    const singles = list.filter((f) => f.members.length === 1).length;
    const maxN = list.reduce((m, f) => Math.max(m, f.members.length), 0);
    console.log(
      `${r.category.padEnd(8)} ${String(r.total).padStart(6)} ${String(r.cov).padStart(8)} ` +
      `${(r.pct.toFixed(1) + '%').padStart(8)} ${String(list.length).padStart(6)} ` +
      `${reuse.padStart(14)} ${String(singles).padStart(8)} ${String(maxN).padStart(6)}`
    );
  }
  const allFams = [...famStats.foe, ...famStats.card, ...famStats.event];
  const totalMembers = allFams.reduce((s, f) => s + f.members.length, 0);
  console.log(
    `合计      ${String(cat.length).padStart(6)} ${String(totalMembers).padStart(8)} ` +
    `${((totalMembers / cat.length) * 100).toFixed(1).padStart(7)}% ${String(allFams.length).padStart(6)} ` +
    `${(totalMembers / Math.max(allFams.length, 1)).toFixed(2).padStart(14)}`
  );

  // 被最多共用的前 10 族
  const top = allFams.slice().sort((a, b) => b.members.length - a.members.length || a.fid.localeCompare(b.fid)).slice(0, 10);
  console.log('\n—— 被最多共用的前 10 族 ——');
  if (top.every((f) => f.members.length <= 1)) {
    console.log('（当前族表无多成员族，全部为单成员，复用率为 1.00）');
  }
  for (const f of top) {
    console.log(`  ${f.fid}  成员=${f.members.length}  [${f.members.join(', ')}]`);
  }

  /* ---------- 断言结果 ---------- */
  console.log('\n—— 断言 ——');
  const byAssert = {};
  for (const [a, msg] of problems) (byAssert[a] = byAssert[a] || []).push(msg);
  const order = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7'];
  const labels = {
    A1: '覆盖率 100%（按 art_catalog.json 实际口径）',
    A2: '跨类别复用 = 0',
    A3: '每族 members ≤ 3',
    A4: '族内成员共享 ≥1 形态关键词（启发式）',
    A5: 'prompt：≥3 具体物名词 & 无 abstract/symbol/emblem 禁语',
    A6: '族 id 命名规则',
    A7: 'style 档位 = A（警告级）',
  };
  for (const a of order) {
    const list = byAssert[a] || [];
    if (a === 'A7') continue; // A7 只作警告
    const verdict = list.length === 0 ? 'PASS' : `FAIL x${list.length}`;
    console.log(`  [${verdict.padEnd(8)}] ${a} ${labels[a]}`);
    for (const msg of list.slice(0, 12)) console.log(`           - ${msg}`);
    if (list.length > 12) console.log(`           … 还有 ${list.length - 12} 条`);
  }
  for (const w of warns) console.log(`  [WARN    ] ${w}`);

  const failed = problems.length > 0;
  console.log('\n' + line);
  console.log(failed ? `结论：FAIL（${problems.length} 条断言未过）` : '结论：PASS（全部断言通过）');
  console.log(line);
  process.exitCode = failed ? 1 : 0;
}

main();
