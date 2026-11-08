# -*- coding: utf-8 -*-
"""零件跨战斗累积：startCombat 里 C.parts 从 run.parts 带入，而不是从 0 开始

现状：parts: 0            → 每场战斗从零开始，结束时 run.parts = C.parts 覆盖库存
改后：parts: run.parts    → 战斗带入库存，结束时写回 = 跨战斗累积

用法：
  python tools/fix_parts_accum.py           # 演练
  python tools/fix_parts_accum.py --apply   # 真改
"""
import sys, shutil, datetime, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

P = r'C:\Users\Administrator\Desktop\杂七杂八\红渊\game\web\index.html'
OLD = b'parts: 0,'
NEW = b'parts: run.parts,'

raw = open(P, 'rb').read()
print('file size  :', len(raw))
print('OLD hits   :', raw.count(OLD))
print('NEW hits   :', raw.count(NEW))

if raw.count(NEW) == 1 and raw.count(OLD) == 0:
    print('already applied.')
    sys.exit(0)

if raw.count(OLD) != 1:
    print('ABORT: 期望 OLD 恰好 1 次')
    sys.exit(1)

# 确认上下文正确（必须出现在 startCombat 的 C 对象里，旁边有 enemies 或 activeProtocol）
i = raw.find(OLD)
before = raw[max(0, i-160):i]
if b'enemies: []' not in before and b'activeProtocol' not in raw[i:i+120]:
    print('ABORT: 上下文不像 startCombat 的 C 对象')
    print(repr(raw[max(0, i-200):i+150]))
    sys.exit(1)

if '--apply' not in sys.argv:
    print()
    print('DRY RUN ——')
    print('  改前:', repr(raw[max(0, i-150):i+80]))
    print('  改后:', repr(raw[max(0, i-150):i+80].replace(OLD, NEW)))
    print()
    print('加 --apply 真改')
    sys.exit(0)

stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
bak = P + '.bak-' + stamp + '-partsaccum'
shutil.copy2(P, bak)
print('backup    :', bak)

out = raw.replace(OLD, NEW)
open(P, 'wb').write(out)

chk = open(P, 'rb').read()
print('verify NEW:', chk.count(NEW))
print('verify OLD:', chk.count(OLD))
print('OK' if chk.count(NEW) == 1 and chk.count(OLD) == 0 else 'FAILED')
