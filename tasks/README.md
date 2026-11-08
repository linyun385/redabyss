# 任务总则（每次开工前必读）

## 工作目录
```
C:\Users\Administrator\Desktop\杂七杂八\红渊\game
```

## 必读文件（按顺序）
1. `DESIGN.md` —— 施工图，全部实现依据它
2. `glossary.json` —— 专有名词池，命名只从这里取

## 铁律

| # | 规则 |
|---|---|
| 1 | **只创建/修改当前任务指定的文件**。不许改 `engine/core.js`、`DESIGN.md`、`glossary.json`、`tools/*.js` |
| 2 | **专有名词只能从 `glossary.json` 取**，不许自己发明。允许组合已有名词 |
| 3 | 文风按 `DESIGN.md` §10 执行。**flavor 里出现"造成/获得/点伤害/恭喜/解锁"直接判失败** |
| 4 | 每完成一个任务，**必须跑自检命令并确认通过**，才能写完成标志 |
| 5 | **不许占位**。每个字段都必须是最终内容，不许写 `TODO`、`xxx`、`示例` |
| 6 | 中文全角标点。JSON 里中文引号用「」不用"" |
| 7 | 遇到无法完成的情况，写 `status: blocked` 并说明原因，**不许假装完成** |

## 自检命令
```powershell
cd C:\Users\Administrator\Desktop\杂七杂八\红渊\game
node tools\pack_check.js <cards|enemies|relics|events|all>
```
看到 `全部通过` 才算完。`FAIL` 一律要修到没有。

## 完成标志
每完成一个任务，**追加**写入 `C:\Users\Administrator\Desktop\杂七杂八\红渊\game\TASK_DONE.md`：

```markdown
## T<n> 完成
- status: done
- output: <产出文件路径>
- check: <自检命令最后一行输出>
- notes: <一句话说明，比如"40 张，稀有度分布 16/14/8/2">
```

**不要覆盖已有内容，只追加。**
