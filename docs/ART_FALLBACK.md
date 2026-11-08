# ART_FALLBACK — 纯 CSS / SVG 的卡面质感（T50）

> 2026-10-30。默认主题 C（层色+纸纹，见 docs/THEME_DECISION.md）。本任务在 C 的基础上加质感，**不依赖任何生图**，单文件自包含（无 img / 无 background-image:url / 无外部字体）。
> 截图：docs/artstyle/SVG_cards_off.png / SVG_cards_B.png / SVG_cards_C.png / SVG_enemy.png / SVG_relics.png（1440×900）。

## 一、卡牌图案区底纹（纯 CSS 渐变，0 个新 DOM 节点）

实现：图案区按第一脉挂类名 `v-light / v-water / v-heat / v-tremor / v-mineral / v-none`（`appendArt()` 里加，落点 web/index.html），CSS 用多层 `repeating-linear-gradient` + `radial-gradient` 叠出「手工印刷」肌理。线色走 `--art-line` 变量：off 主题给浅线（深底），B/C 主题给墨线（纸底）——三主题自动换色。

| 类名 | 脉 | 画法 | 「像」什么 |
|---|---|---|---|
| .art.v-light | 光 | 中心径向光斑 + 两组 ±60° 斜线 | 版画里的放射光芒 |
| .art.v-water | 水 | 两组不同间距的横向水纹线 | 水层沉积纹 |
| .art.v-heat | 热 | 底部径向热斑 + 竖向细线 | 热流上升 |
| .art.v-tremor | 震 | 45°/-45° 双向交叉排线 | 铜版画交叉阴影（唯一「真印刷结构」的一组） |
| .art.v-mineral | 矿 | 纵横方格 + 角部矿斑 | 晶格网格 |
| .art.v-none | 无脉 | 8px 点网 | 印刷网点 |

诚实标注：只有 tremor 的交叉排线是真正的版画技法结构；light/heat 的「光芒/热流」是氛围近似；mineral 的方格更像晶格而非木刻。全部是「像」，不是「真印刷」。

## 二、敌人卡剪影（内联 SVG symbol × 5，按层级换构图）

实现：HTML 末尾内联 `<svg><defs><symbol>` 精灵图（5 个 path，24×24 viewBox，全部 `currentColor` 描边）；敌人图案区（`.eart`）渲染时按 tier 插 `<use>`：

| tier | symbol | 构图类名 | 画法 |
|---|---|---|---|
| 普通 | #sym-eye（眼） | .esym-n | 单图形 22px，置灰 |
| 精英 | #sym-door（门） | .esym-e | 28px + 圆环边框（CSS 画框） |
| Boss | #sym-snake（蛇） | .esym-b | 34px + 单线框 + 双线下缘（CSS border） |

落点：`render()` 的敌人循环（原 tier 字符 span 替换为 `<svg><use>`，每次渲染每敌 1 个 svg 节点）。眼=「它在看你」（凝视主题）、门=「精英是一扇要过的门」、蛇=「巨怪的蜿蜒」——几何象征物对应 STYLE_ART.md 的象征物清单。

## 三、遗物徽记（内联 SVG symbol × 12，× 6 旋角 = 72 种视觉变体）

实现：`relicBadge(id)` 把遗物 id 做稳定散列 → 12 个几何 symbol（圆/三角/方/菱/星/十字/波/山/六边/月/门框/双环）之一 + 6 档旋角之一；同一遗物永远同一个徽记。替换了三处纯文字：HUD 遗物行（原「◆+名字」）、relicrow 遗物奖励卡、（商店遗物暂未加，见边界）。

## 四、DOM 与性能

- 常驻新增：SVG 精灵 17 个 symbol 定义（display:none，一次性）；每敌 1 个 svg；每遗物 1 个 svg。一局典型画面新增节点 < 60（上限 200）。
- 首屏实测：DOMContentLoaded **69ms**；选职业点击到渲染完成 **8ms**（performance.now 差值，Chrome）。
- 不用模糊/滤镜；纹理全部是渐变与线条，不压暗任何文字。

## 五、接入真图时的替换点

1. **卡面图案**：T36 已留接口——给 `.art` 元素加内联背景样式（`style="background-image:url(art/x.webp)"`）即覆盖底纹与符号（T44 的 `[style*="background"]` 开关会自动隐藏占位符号）。真图接入时在 `appendArt()` 里把内联样式换成 `card.art` 字段驱动即可，CSS 纹理类可以保留在无图卡的兜底。
2. **敌人剪影**：`render()` 敌人循环里 `eart.innerHTML` 一处替换为 `<img>`/背景图（注意 check_web 的图片禁令需要同步放开——那是发布策略决定）。
3. **遗物徽记**：`relicBadge()` 一处替换为按遗物 id 映射的真徽记图。

## 六、边界声明

- 「手工印刷感」里只有 tremor 交叉排线接近真实铜版画技法；其余五组是氛围近似——「像」与「真印刷结构」的区分如上表。
- 敌人剪影按 tier 分三档构图，同层同 tier 的敌人共用同一图形（未按敌人个体区分——需要 88 张剪影，超出本次范围）。
- 遗物徽记是「id→几何符号」的稳定散列，不编码遗物含义（外观与效果无语义关联，纯识别用）。
- 商店里的遗物商品（.shopitem）未加徽记（三处中的第三处只做了 HUD 与 relicrow）——后续补齐落点相同。
- 截图为主题 C/B/off 的奖励界面 + C 的战斗/HUD；SVG_enemy.png 同时含卡面纹理与敌人剪影。
