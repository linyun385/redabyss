## card_06：收编 2 组新彩蛋

**改哪个文件**：web/index.html EASTER_EGGS 表（[index.html:6994] 附近）

**具体怎么改**：按现有格式追加两项：
{ id: 'resonance_accounting', pair: ['anm_0006', 'u_0010'], line: '库存盘点遇上谐振垫层。收支平衡。', fx: (C) => { C.resonance += 1; } }
{ id: 'gaze_lending', pair: ['trem_0055', 'u_0009'], line: '借来的凝视还了一半。剩下一半是利息。', fx: (C) => { C.run.gaze = Math.max(0, C.run.gaze - 1); } }

**改完跑什么**：进战斗打出配对的两张卡，弹出彩蛋文案

**失败了怎么退**：删除追加的两项

**这一步做完，游戏会变成**：彩蛋表从 6 项扩到 8 项——组合技的叙事奖励
