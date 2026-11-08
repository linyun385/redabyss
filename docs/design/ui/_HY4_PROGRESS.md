# HY4 队列进度

| 完成时间 | 文件 | 一句话结论 |
|---|---|---|
| 2026-11-05 21:15:07 | `h1_invisible_status.md` | 枚举 35 个状态 key：14 个界面可见、6 个只能靠日志/瞬时反馈、15 个完全看不见；玩家 buff/debuff 全部无 DOM、无 CSS 类，另有 3 个 key 写入后全文无读取。 |
| 2026-11-05 21:18:40 | `h2_keyboard.md` | 7 个 keydown 监听全绑 document；局内 Tab 被 9063 全局劫持，事件/商店/营火/奖励/结算无键盘推进入口，战斗缺敌人目标选择，数字键 1–9 调 `.click()` 但手牌只绑 `pointerdown`。 |
| 2026-11-05 21:21:51 | `h3_spec_drift.md` | 对账 UI.md 的 35 条数值规范：33 一致、1 部分一致（HUD `.v` 无显式字号）、1 未验证（帮助角标 11px）、0 不一致；z-index 全表吻合，但文档引用的代码行号已整体漂移 41–53 行。 |
| 2026-11-05 21:25:32 | `h4_interaction_states.md` | 25 类可交互元素 × 5 态 = 125 位，已定义 60、缺 65；`:active` 全表 0 处，19 类缺选中态、16 类缺禁用态；`#btn-world` 五态全缺，JS 所加交互类 0 个缺 CSS。 |
| 2026-11-06 00:22:14 | `x1_sizes.md` | 十区域按 CSS 算完 1280×720/1920×1080 尺寸：全文无宽度 @media，字号 0 处视口差异（仅 vh/vw 类高宽上限变）；低于可读线 16 项（去重；卡牌线 3、正文线 9、按钮线 5，`.fontbtns` 同时违反正文线与按钮线），另 3 处 `font:12px/1.4 inherit` 简写按规范失效存疑、2 处按钮无 font-size 未验证；顺带订正 00_inventory 两处算式（立绘 198×264 非 200×267；敌人 5/6 只=1230/1480 非 1190/1420）。 |
| 2026-11-06 00:31:23 | `x2_css_vars.md` | 25 个 CSS 变量 / 49 处定义 / 262 次 var()（7 次带 fallback，均为 --tx/--ty/--rot）；孤儿 2 个（`--grain-opacity` :532、`--opt-sub` :10/:281/:534 全 0 引用，后者被 check_contrast.js:83,87 校验但页面 :350 实际用 `var(--dim)`）；CSS 未定义即引用 4 个名字全部由 JS setProperty 注入，其中仅 `--layer-bg` :537 无 fallback 且只在 startCombat/showMap 注入 → 条件性真 bug，其余 3 个安全；另记 :root 变量链在 html 处解析、body 级 A 主题覆盖不参与，以及 :6550-6551 内联覆盖 :root 静态值。 |

| 2026-11-06 02:36:52 | `x3_motion.md` | 静态清点 transition 11 处 / animation 21 处 / @keyframes 18 处（17 唯一名，`atkpulse` 在 479、503 重复定义）/ reduce 规则全文件仅 519 行 1 处，覆盖 10 条、遗漏 9 条（其中 5 条 `infinite`：`atkpulse` 三处、`dreampulse`、`mblink`）；reduce 内 `transition:none` 0 处 → 10 条过渡全未禁用，JS 侧 `matchMedia` 0 处无第二条降级路径；523 行对 `#toast`、`#phase-banner.show` 的覆盖无效（二者只有 transition 无 animation）。 |
| 2026-11-06 02:36:52 | `x4_breakpoints.md` | 全文件 `@media` 仅 1 处（519 行 prefers-reduced-motion），宽度断点 0 个、布局属性 0 条；900–1400 段 7 档全落空；<768px 专属规则 0 条 / JS 布局分支 0 处（`innerWidth` 3 处只读度量、resize 1 处）；375px 下手牌扇形溢出 145px 且被 `overflow:hidden` 裁掉、敌人区溢出 133px、`#card-detail` 304px 占屏 81.1%；`--lane` 是 max-width 不是溢出源，真正致命的是 `#hand` 238px 固定高与卡牌 150×210 固定尺寸。 |
| 2026-11-06 02:36:52 | `x5_layers.md` | 浮层 18 个；z-index 声明 22 行（18 静态 + 4 JS），15 个不同取值；风险组合 8 组（倒置/相等 5 组）、失效或层叠上下文隔离 12 项（真正不生效 4 项）；`layoutFan()` :8289 内联 `style.zIndex = i+1` 覆盖 CSS :248/252/254 的 98/99/100 → hover/selected/dragging 声明运行时不生效；`#phase-banner`(z40) 与 `.card.ghost-fly`(z40) 同值、后者 DOM 更晚会盖住横幅；`body.lowsat` filter :472 / `body.shake` :506 让 `#app` 创建层叠上下文，隔离内部 95/55/98–100；与 UI.md 对账 15 条：一致 14 / 不一致 1 / 规范有代码无 1（z=12 vignette 不存在）。 |
| 2026-11-06 02:36:52 | `x6_sfx_wiring.md` | 三方对照 27 wav / SFX_LIST 27 code（19 音效 + 8 氛围）/ `playSfx` 调用点 24 处、唯一字面量 18；孤儿音 1 条 `state.energy_empty`（wav 在、定义在 :31、只进 :7951 预载数组）、缺文件 0、未定义 0；首版「ui.click/ui.page 缺文件」是 `ls \| head -25` 截断误报，两文件实测存在；:7873 注释「28 个」过时（实测 27 = 19+8）；氛围 8 层由 :7927 `load('ambience.depth'+depth)` 动态拼接覆盖，无字面量；24 个调用点的运行时触发全部标「未验证：未开浏览器」。 |

H1–H4 已按序全部完成并逐个交付。**X 批 X1–X6 于 2026-11-06 02:36 全部补齐并交付**（X1 尺寸 / X2 CSS 变量 / X3 动效 / X4 断点 / X5 层级 / X6 音效三方对照），X 批耗尽。按 batch3 任务书要求，先补完上一批再做 Y 批。
