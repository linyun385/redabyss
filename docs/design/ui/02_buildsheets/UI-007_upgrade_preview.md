# UI-007_upgrade_preview.md%.md 升级后效果预览缺失

## 现状
见 00_inventory.md 对应区域。

## 问题
见 01_issues.md 对应条目（UI-007_upgrade_preview.md%.md 前缀）。

## 改法
openCardDetail 里追加 upgradeCard 差量

## 影响面
第 5 区域。

## 验收
- node tools/check_web.js → 全绿
- 视觉部分需设计机在浏览器确认

## 风险
低——只改 web/index.html 的 CSS 或 JS，不改数据/引擎。
