# 夜班验收手册（指挥席自己用）

> 目的：**不信 GLM 自述**。它写完 TASK_DONE.md 后，我用自己的通道复验一遍。
> 2026-10-29 22:40 建立。

## 一、三级验收

| 级 | 手段 | 判据 |
|---|---|---|
| L1 机械 | `node tools/pack_check.js all` / `node tools/test_engine.js` / `node tools/check_web.js` | 必须全绿，**我自己跑**，不看它贴的输出 |
| L2 页面 | 本地 http 服务 + 我的浏览器工具点进去截图 | 看布局/图标/卡牌形状，不看它描述 |
| L3 自查 | 读 TASK_DONE.md 的「边界声明」 | 有没有把没验证的写成已验证 |

## 二、L2 怎么跑（固化成 3 步）

```powershell
# 1) 起预览服务（每夜起一次即可，后台跑）
cd C:\Users\Administrator\Desktop\杂七杂八\红渊\game
python -m http.server 8808 --bind 127.0.0.1 --directory web
```
2) `pilot_navigate http://127.0.0.1:8808/index.html`
3) `pilot_snapshot` 拿 refs → `pilot_act click` 进地图/战斗 → `pilot_screenshot` → `read_image` 看画面

**注意**
- 服务用 `-c-1` 等价的 no-cache（python http.server 默认无长缓存，够用；发现问题先清缓存）
- 每次改完 `web/index.html` 必须 `pilot_navigate reload`，否则看的是旧页
- 截图存 `tools\_acc_<TaskId>.png`，别覆盖

## 三、每任务的最低证据（写进给用户的话里）

- 检查器：三个的**最后一行输出**
- 截图：改动前后的对比（T36 之后卡牌形状、HUD 图标；T37 之后动画）
- 已知风险：它说"未验证"的项，我**要么补测要么明确告诉用户没测**

## 五、夜班值守规则（2026-10-30 00:07 用户定）

1. **判据用后端，不用前端**：`python tools/fire_watch.py --judge log --notify-only --interval 15 --idle 240`
   只看 `~/.zcode/cli/log/zcode-<日期>.jsonl` 有没有长——不碰窗口、不抢焦点、不读像素。
2. **脚本只检测，不输入**。静默 >240s → 打印现场 + 写 `tools/_fire_stop.json` + `exit 3`。
   后台作业退出会通知 DSH 会话，由人接管：截图 → 判断停在哪 → 再决定发什么。
3. **降噪**：`--user-idle`（默认 20s）保证用户还在敲键鼠时脚本不做任何动作。
4. **用户醒着（到 00:30）**：检测到停 → 先报用户，等点头再发。
   **用户睡了（00:30 之后）**：直接发「常驻指令」`tools/STANDING_ORDER.txt`（按 queue.json 顺序做完）。
5. 旧的自动输入路子已弃用：`pyautogui` 在 150% 缩放下点偏、输入框坐标随布局漂移，
   脚本盲打字 4 次全部静默失败。别再回去。

## 六、红线

| # | 红线 |
|---|---|
| 1 | 它说"全绿"但 L1 我自己跑不绿 → **整批退回** |
| 2 | 改了 `engine/core.js` 而任务书说不要动 → 退回 |
| 3 | 把白天人工改的 7 处（HANDOFF_D2）改回去了 → 退回 |
| 4 | TASK_DONE 里没有「边界声明」→ 退回重写，不验收 |
| 5 | 单任务超过 90 分钟没产出 → 换会话，不要等 |
