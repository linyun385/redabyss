# 晚间交接（2026-10-29 21:15）

> 给下一个会话看的。当前会话上下文过长已出现退化（重复工具调用、时间基准错乱），建议换会话。

---

## 一、项目

```
C:\Users\Administrator\Desktop\杂七杂八\红渊\game\
```

卡牌 roguelike《红渊：下潜》。设定源自 `../红渊.md`（590 行，权威）。

## 二、已完成

### 昨晚（GLM 跑的一晚）
T1–T26 全部完成：
- 4 个职业：下潜者 / 震语者 / 疯先知（苍民）/ 维护者（黯民）
- 260 张卡、88 个敌人、90 个遗物、68 个事件、8 层
- 两个 DLC 完整（黯民、苍民），各含设定文档 + 数据 + 引擎 + 验收报告
- `web/index.html` 单文件可玩（当时约 320 KB）

### 今天白天（人工直接改 index.html）
详见 `docs/HANDOFF_D2.md`，共 7 处：
1. flexbox 溢出修复（日志撑爆、点不到结束回合）
2. 统一 1240px 内容梁（三界面同宽同位）
3. HUD 移出战斗屏、常驻所有界面（拆两行：属性 + 遗物）
4. keep_block 遗物：格挡改成保留一半（原来无限累积）
5. 层深度主题色（D1 蓝灰 #39434e → D4 黑 #0d1013 → D8 红 #64101a）
6. 点击目标放大（地图节点 140×80、选项 760 宽、奖励卡 210×210）
7. 内容重心居中（地图/卡牌/敌人/手牌/日志）

### 今天新建的文档
- `docs/art/STYLE_SAMPLES.md` —— 密教模拟器文风样本 + 12 条特征（第一人称、半文半白）
- `docs/art/STYLE_ART.md` —— 美术风格规范（木刻版画）+ SDXL 提示词模板
- `docs/HANDOFF_D2.md` —— 白天改动记录

## 三、今晚的活（任务包已全部写好）

`tasks/T35.md` ~ `tasks/T43.md`，`tasks/queue.json` 已更新为这 9 项：

| 任务 | 内容 | 依赖 |
|---|---|---|
| T35 | 回归验证 + 收尾（读 HANDOFF_D2 先） | 无 |
| T36 | 图标系统 + 卡牌模板（**用户要的核心**） | 无 |
| T37 | 战斗顺滑 + 点击反馈 | T36 |
| T38 | 只修明显坏掉的卡（范围刻意缩小） | 无 |
| T39 | 三条 build + 8 个彩蛋 | 无 |
| T40 | 新手引导 | T36（复用 `?` 面板） |
| T41 | 音效架构（只留钩子） | 无 |
| T42 | 素材接入 + 生图管线 | **ComfyUI 环境** |
| T43 | 最终打包 | 全部 |
| T44 | 材质风格 × 层深度色协调（3 方案 + 开关） | T36 / T42（弱依赖） |

> 2026-10-29 22:55 用户定：密教风整体改造放**最后**（T44），但**不放弃层深度换色**，两者要组合适配、给对比证据，由用户拍板。

## 四、环境：ComfyUI 正在装

```
✅ D:\ComfyUI              代码已 clone（git 直连 GitHub 成功）
🔄 SDXL base               下载中 4.22 GB / 6.9 GB（ModelScope，约 6 MB/s）
🔄 PyTorch CUDA 12.4       安装中（download.pytorch.org，约 2.5GB）
```

**装完后要做的三步**（新会话接手）：
1. `python -c "import torch;print(torch.cuda.is_available())"` → 应为 True
2. `cd D:\ComfyUI; python -m pip install -r requirements.txt`（装剩余依赖）
3. `cd 项目; python tools/gen_art.py --probe` → 应报 ComfyUI 服务运行中

**然后先自己测一张图**（不要直接交给 GLM）：
```powershell
python tools\gen_art.py --prompt "woodcut engraving, an ancient brass lens held in a gloved hand, a thin line of crimson light passing through and splitting into three, sepia ink on aged parchment, heavy cross-hatching, rough hand-carved lines, centered symmetrical composition, dark vignette edges, no text" --out tools/test_lens.png --width 832 --height 1216
```
用 `read_image` 看风格对不对。对味再给 GLM 批量。

**硬件现实**：RTX 4060 Laptop，**8 GB 显存**。Qwen-Image（20B）跑不动，用 SDXL。
832×1216 下预计占 6.5–7 GB，很紧。爆显存就降到 768×1120 或加 `--lowvram`。

## 五、工具

| 工具 | 用途 |
|---|---|
| `tools/pack_check.js` | 数据校验（卡牌/敌人/遗物/事件数量与格式） |
| `tools/test_engine.js` | 引擎单元测试（17 项） |
| `tools/check_web.js` | 前端检查（自包含、无外部资源、核心元素） |
| `tools/sim.js` | 对局模拟（四职业，用于找废卡） |
| `tools/gen_art.py` | 生图管线（`--probe` / `--prompt` / `--batch` / `--check`） |
| `tools/fire_watch.py` | 夜间救火器（详见下） |
| `tools/zwin.py` | **可靠的 ZCode 窗口定位**（按标题 + DPI 感知） |
| `tools/send_now.py` | 用 zwin 坐标给 ZCode 发消息 |
| `tools/grab_zcode.py` | 强制把 ZCode 拉到前台并截图 |

## 六、夜间值守（如果要跑）

`fire_watch.py` 的判据已经过三轮迭代，现在是**检测右下角按钮**：

```
按钮中心 (0.596, 0.955)
方块 ■ = 工作中，亮占比 ~0.45
箭头 ↑ = 已停止，亮占比 < 0.30
```

启动：
```powershell
cd C:\Users\Administrator\Desktop\杂七杂八\红渊\game
python tools\fire_watch.py --start 23:00 --stop 09:00 --idle 180 --hard-idle 1800 --escalate 300 --interval 20
```

`--escape 300` 后自动新建会话并读 `TASK_DONE.md` 找下一个任务。

**教训**（都吃过）：
- 不要用「整窗像素变化」判断——会被右侧桌宠动画骗，4 小时不干预
- 不要用「文件产出」单独判断——GLM 思考时也不写文件
- 「没有完成概念」的任务不能放队列中间（T16 吃掉 4 小时）

## 七、用户的核心诉求（原话要点）

1. **布局统一**——三界面同宽同位，留白可以，但不能一块大一块小
2. **点击目标要显眼、大**——玩家注意力焦点要在中间
3. **背景要有明显色彩变化**——从白到暗到红
4. **图标化**——血量用 ♥ 而不是文字
5. **卡牌长方形**——带图案区，为以后填素材预留
6. **手牌扇形展开**——想做，但要等图片方案定下来（暂缓）
7. **斜向地图**——不是设计方向（以后做特色化）
8. **压迫感**——背景 + 素材 + 声音联动，以后做
9. **卡牌机制以后会大改**——所以今晚不做深度平衡

## 八、下一步（新会话第一件事）

1. 看环境装好没（`gen_art.py --probe`）
2. 装好就先测一张图，给用户看风格
3. 没装好就 23:00 直接开跑 T35，T42 留到环境就绪
4. 用户额度 23:00 开启
