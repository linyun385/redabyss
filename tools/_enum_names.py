# -*- coding: utf-8 -*-
"""挖游戏里这些枚举的真实中文叫法，结果写文件（避开 PowerShell 控制台编码坑）。"""
import re, json

s = open('web/index.html', encoding='utf-8').read()
out = {}

# VEIN_CN 表
m = re.search(r'VEIN_CN\s*=\s*\{([^}]*)\}', s)
out['VEIN_CN_raw'] = m.group(1) if m else None

# cost_type switch
i = s.find('switch (card.cost_type)')
out['cost_switch'] = s[i:i+600] if i > 0 else None

# 找 rarity / type 的中文映射表（各种名字）
for name in ['RARITY_CN', 'RARITY', 'RARE_CN', 'TYPE_CN', 'CARD_TYPE', 'COST_CN', 'COST_TYPE_CN']:
    for mm in re.finditer(re.escape(name) + r'\s*=\s*\{([^}]*)\}', s):
        out[name] = mm.group(1)
        break

# 找中文稀有度词出现在哪些映射里
for kw in ['普通', '精良', '稀有', '特殊', '攻击', '技能', '能力']:
    idxs = [mm.start() for mm in re.finditer(kw, s)][:3]
    out['kw_' + kw] = [s[max(0, j-80):j+80].replace('\n', ' ') for j in idxs]

with open('tools/_enum_out.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print('ok', len(s))
