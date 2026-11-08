# 主题拍板记录

**2026-10-30 06:52，用户确认：默认主题 = C（层色 + 纸纹，卡面用纸）。**

## 落地
`web/index.html` 根元素改成 `<html lang="zh-CN" data-theme="C">`。原文件备份：`web/index.html.bak-themeoff-0647`。

## 为什么是 C
| 方案 | 数据 | 结论 |
|---|---|---|
| A 全纸底 | 8 层色差最小 ΔE 1.4（要求 ≥5）；次要对比度 2.95 | 作废——层色信息丢失 |
| B 暗底贴纸 | ΔE 7.4、正文 10.21、次要 4.68 | 可用，但战斗区整块纸色面积过大，抢中间可点元素的注意力 |
| **C 层色 + 纸纹** | 同 B 的对比度数字，层色完全保留 | **采用**：暗底压旧纸纹理，卡面/日志用纸，既不丢层色也不抢焦点 |

## 切换
```js
document.documentElement.dataset.theme = 'C'   // 默认（现状）
document.documentElement.dataset.theme = 'B'   // 暗底贴纸
document.documentElement.dataset.theme = 'off' // 回到没有材质的深色版
delete document.documentElement.dataset.theme  // 等同 off
```

## 回归记录（改默认值后我自己跑的）
- `node tools/check_web.js` → 全部通过（0 警告）
- `node tools/pack_check.js all` → 全部通过（5 警告，与改前一致）
- `node tools/test_engine.js` → 全部通过
- 浏览器实测（1280×800，本地 http 服务）：职业选择 / 地图 / 战斗三屏正常；卡面纸底 + 棕墨文字，图案区边界清晰

## 待办
- **T50**（纯 CSS/SVG 质感）按 C 为目标做，B 只需不破相，A 已作废不再维护
- 深层次要文字对比度 2.07（off 时代的旧账）由 **T52** 处理
