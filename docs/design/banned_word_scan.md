# T445 · 卡面文案禁词扫描

> 范围：`cards/*.json` 全部 219 张卡的 `flavor` + `cost_text`（含 `upgrade.flavor_add`，一并查）。禁词表（任务书原文）：造成 / 获得 / 点伤害 / 恭喜 / 解锁 / 恭喜获得。
> 复算：`python data/audit/gen_t445.py`（脚本本体见 data/audit/ 目录，或按下方复算片段）。

**零命中**：扫描 219 张卡 × flavor/cost_text/flavor_add 共 475 个字段，禁词表 6 个词全部零命中。

### 复算片段

```python
import json, glob, os
BANNED = ['造成', '获得', '点伤害', '恭喜', '解锁', '恭喜获得']
for f in glob.glob('cards/*.json'):
    if os.path.basename(f).startswith('_'): continue
    for c in json.load(open(f, encoding='utf-8')):
        fa = (c.get('upgrade') or {}).get('flavor_add')
        for field in ('flavor', 'cost_text', 'flavor_add'):
            v = c.get(field) if field != 'flavor_add' else fa
            if v:
                for w in BANNED:
                    if w in v: print(c['id'], field, w, v)
```
