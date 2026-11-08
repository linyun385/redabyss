# UI-014_font_em.md%.md 字号缩放改 em/rem

## 现状
见 00_inventory.md 对应区域。

## 问题
见 01_issues.md 对应条目（UI-014_font_em.md%.md 前缀）。

## 改法
卡牌字号从 px 改 em

## 影响面
第 10 区域。

## 验收
- node tools/check_web.js → 全绿
- 视觉部分需设计机在浏览器确认

## 风险
低——只改 web/index.html 的 CSS 或 JS，不改数据/引擎。
