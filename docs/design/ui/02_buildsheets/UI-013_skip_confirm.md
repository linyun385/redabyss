# UI-013_skip_confirm.md%.md 跳过三选一加确认

## 现状
见 00_inventory.md 对应区域。

## 问题
见 01_issues.md 对应条目（UI-013_skip_confirm.md%.md 前缀）。

## 改法
showCardChoice 里 skip 加 confirm

## 影响面
第 9 区域。

## 验收
- node tools/check_web.js → 全绿
- 视觉部分需设计机在浏览器确认

## 风险
低——只改 web/index.html 的 CSS 或 JS，不改数据/引擎。
