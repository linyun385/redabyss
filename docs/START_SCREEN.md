# START_SCREEN — T78 开始界面两步重构交付说明

> 2026-10-31。任务书 `tasks/T78.md`。改动：`web/index.html` 的 #screen-select HTML、选职业接线、
> .class-card 系列 CSS；资产 `web/assets/class/<id>.webp` ×4（从 art/class_*.webp 复制，相对路径、未内联）。

## 1. 两步流程

```
第一步 卡面页                        第二步 详情模态（点卡面才出现）
┌──────────────────────────┐      ┌─────────────────────────────────────┐
│      红渊：下潜            │      │ ┌────────┐  ┌─────────────────────┐ │
│  一句引导（选一张卡面…）      │      │ │        │  │ 疯先知               │ │
│                           │      │ │ 立绘    │  │ 一句话身份            │ │
│  [卡面] [卡面] [卡面] [卡面] │  →   │ │ (大图)  │  │ 初始生命/偏重/专属      │ │
│   img+职业名（无描述/数值）    │      │ │        │  │ ◆机制 ×3             │ │
│                           │      │ │        │  │ [以此身份下潜]         │ │
└──────────────────────────┘      └─×└────────┘  └─────────────────────┘─┘
```

- **首屏**：标题 + 一句引导 + 4 张**纯卡面**（`<img src="assets/class/<id>.webp">` + 职业名）。
  职业描述/生命/偏重/专属文本从首屏 DOM **移除**（probe 关键词 0 命中）。悬停上浮 4px + 边框亮起。
- **模态**：点卡面才构建内容（懒构建，首屏 DOM 无详情节点）。左 40% 立绘大图 / 右 60% 详情，
  固定顺序：职业名 → 一句话身份 → 初始生命/偏重/专属（列表）→ ◆核心机制 ×3 → 「以此身份下潜」。
- **确认才算开局**：卡面页点一下只开模态；`run` / 地图 region 在点「以此身份下潜」前保持未创建
  （probe 实测 `NewMap.st.region === null`）。
- **关闭三法**：× 按钮 / Esc / 点遮罩 → 回到卡面页（选择不丢失）。
- **键盘**：卡面是 `<button>`（Tab 聚焦 + Enter 打开）；打开后焦点自动落到确认按钮（Enter=开局）；
  Esc 关闭。

## 2. DOM 断言输出（probe 实测）

```
首屏: keywordHits: []            （殖民者/记忆者学徒/重新梦见/唯一的供应商/初始生命/偏重/专属/清醒度/双牌堆/醒 30 → 0 命中）
      cardfaces: 4
      imgs: assets/class/{diver,tremor,cangmin,anmin}.webp   （全部加载成功）
      modalInDom: false          （详情未懒构建）
      runCreated: false          （region 未生成）
模态: artLeftOfDetail: true       （左卡右详，art 375px ≈ 40%）
      statItems: 3  mechItems: 3  confirmBtn: true
确认后: phase 'map' / regionNodes 240 / depthText「深度带 D1/8 地表死寂区」/ deck 12 张
      modalClosed: true / selectHidden: true
```

## 3. 截图（docs/shots_t78/）

| 文件 | 内容 |
|---|---|
| 01_cardfaces.png | 卡面页：4 张纯卡面（真实立绘）+ 标题 + 一句引导 |
| 02_class_modal.png | 详情模态：左立绘大图 / 右详情（疯先知：身份/生命/清醒度/双牌堆/机制×3）+「以此身份下潜」 |
| 03_confirmed_map_d1.png | 确认后进入第 1 深度带（240 节点地图已生成） |

## 4. 复核方式

```bash
node tools/check_web.js && node tools/test_engine.js && node tools/pack_check.js all
```
浏览器（1280×720）：载入 → 首屏 probe → 点卡面 → 模态 probe → Esc/×/遮罩 三法 → 键盘 Tab+Enter →
确认 → 第 1 深度带。
