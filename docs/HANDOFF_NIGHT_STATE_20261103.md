# 夜班值守状态（2026-11-02 23:10 起）

> 给半夜接手的自己、或早班的人。只写「现在是什么状态、怎么接管、哪几个坑踩过」。

## 一、现在在跑什么

| 项 | 状态 |
|---|---|
| ZCode 里的 GLM | 23:00 开跑，已读到 `model-io` 输出持续增长（3 个文件，含 subagent） |
| 任务队列 | `tasks/queue.json`：**T81–T283，共 203 个**，`tasks/T81.md`…`T283.md` 各一份任务书 |
| 开场白 | `tasks/NIGHT_OPENING_1102.txt`（用户已粘进 ZCode） |
| 监控 | `tools/glm_watch.py` v2 后台跑，日志 `tools/_glm_watch.log`，状态 `tools/_glm_watch_state.json` |
| 我的巡检 | 会话级定时提醒，每小时一次，读 state + TASK_DONE 判卡死 |

## 二、监控的三级动作

| 层 | 条件 | 动作 |
|---|---|---|
| L1 | 所有 model-io 文件**总字节** 180 秒无增长 | `send_now.py` 发「继续。按任务清单往下做，不要停，不要问我。」 |
| L2 | 再 300 秒仍无增长 | `notify_done.ps1`：TTS 语音 + 蜂鸣 + 置顶窗，每 25 秒重播、最多 12 次 |
| L3 | 仍未恢复 | 每 600 秒再响，最多 6 次 |

判据用的是**全体 `model-io-sess*.jsonl` 的总字节数**，不是单个文件、也不是 mtime。

## 三、v1 踩的两个坑（别再踩）

1. **锁死单个 jsonl 会让监控自己死掉。** ZCode 一开子代理，文件名就变成
   `model-io-sess_subagent_agent_<uuid>.jsonl`，v1 判「目标文件不见了」直接退出（exit 1，23:09:25）。
   → v2 改成 glob 全体文件求和。
2. **用文件大小变化判产出会被 touch 骗。** v1 日志里出现过连续 9 次「有产出（+0 字节）」：
   文件被 touch、size 没变，被当成模型在吐字。→ v2 只在**总字节**变化时才刷新 idle 计时。

## 四、怎么接管（三条命令）

```powershell
cd C:\Users\Administrator\Desktop\杂七杂八\红渊\game
# 1) 它现在停没停（只看不动作）
python tools\glm_watch.py --dry-run
# 2) 它做到第几号了
python -c "import re;t=open('TASK_DONE.md',encoding='utf-8',errors='replace').read();print(sorted(set(int(n) for n in re.findall(r'##\s*T(\d+)',t))))"
# 3) 给它发话（换做法，不是重复「继续」）
python tools\send_now.py "换个做法：<具体建议>"
```

想重启监控：先 `Get-Process python | Stop-Process` 挑对那个，再 `python tools\glm_watch.py`。

## 五、已知风险

- **`TASK_DONE.md` 在 23:02 时还是 11-01 16:57 的时间戳** —— 说明这份「完成记录」的写法
  GLM 可能没照做（它也许在别的文件里记）。早班第一件事应是确认它到底往哪写记录，
  而不是直接信 `TASK_DONE.md` 判定进度。
- **T283（写夜班交接）依赖它真的走到最后**，走不到就得人工补。
- 队列里 T242–T252 是补做 T27–34/68/79/81，其中有 3 个任务书要它自己先写 ——
  这类「先写任务书再做」的活最容易空转，巡检时优先看这几号。
