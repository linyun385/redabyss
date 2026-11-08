# -*- coding: utf-8 -*-
"""BASE_ENERGY 3 -> 4（备份 + 演练 + 应用 + 验证）

用法：
  python tools/fix_energy4.py           # 演练，只报不改
  python tools/fix_energy4.py --apply   # 真改
"""
import sys, os, shutil, datetime, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

P = r'C:\Users\Administrator\Desktop\杂七杂八\红渊\game\web\index.html'
OLD = b'const BASE_ENERGY = 3;'
NEW = b'const BASE_ENERGY = 4;'

raw = open(P, 'rb').read()
n_old = raw.count(OLD)
n_new = raw.count(NEW)

print('file size :', len(raw))
print('OLD hits  :', n_old)
print('NEW hits  :', n_new)

# 顺便确认没有别处硬编码 3 作为能量上限
for probe in [b'energyMax: 3', b'energyMax = 3', b'BASE_ENERGY = 3']:
    print(f'probe {probe.decode()}: {raw.count(probe)}')

if n_new == 1 and n_old == 0:
    print('already applied. nothing to do.')
    sys.exit(0)

if n_old != 1:
    print('ABORT: 期望 OLD 恰好出现 1 次，实际', n_old)
    sys.exit(1)

if '--apply' not in sys.argv:
    print()
    print('DRY RUN —— 改动内容：')
    i = raw.find(OLD)
    print('  上下文:', raw[max(0, i-90):i+70].decode('utf-8', 'replace').replace('\n', ' '))
    print()
    print('要真改，加 --apply')
    sys.exit(0)

# 备份
stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
bak = P + '.bak-' + stamp + '-energy4'
shutil.copy2(P, bak)
print('backup   :', bak)

# 替换（纯字节替换，不碰编码和换行）
out = raw.replace(OLD, NEW)
with open(P, 'wb') as f:
    f.write(out)

# 验证
chk = open(P, 'rb').read()
print('verify size :', len(chk), '(diff', len(chk) - len(raw), ')')
print('verify NEW  :', chk.count(NEW))
print('verify OLD  :', chk.count(OLD))
print('OK' if chk.count(NEW) == 1 and chk.count(OLD) == 0 else 'FAILED')
