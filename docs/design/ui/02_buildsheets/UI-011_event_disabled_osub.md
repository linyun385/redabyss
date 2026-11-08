# UI-011_event_disabled_osub.md%.md 事件禁用选项原因写进 osub

## 现状
见 00_inventory.md 对应区域。

## 问题
见 01_issues.md 对应条目（UI-011_event_disabled_osub.md%.md 前缀）。

## 改法
showEvent 里 disabled 时加 .osub

## 影响面
第 8 区域。

## 验收
- node tools/check_web.js → 全绿
- 视觉部分需设计机在浏览器确认

## 风险
低——只改 web/index.html 的 CSS 或 JS，不改数据/引擎。
