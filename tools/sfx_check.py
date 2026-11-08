# -*- coding: utf-8 -*-
"""音效客观校验：时长、峰值、频段能量分布、主峰频率、循环接缝。

我听不到声音，所以只能验「这个波形长什么样」，不能验「好不好听」。
低频/中频/高频的判定线按人耳感受粗分：
  <300Hz    低频（闷、沉、底噪）
  300-3000  中频（主体、可辨识）
  >3000     高频（脆、亮、金属尖）
"""
import sys
import wave
from pathlib import Path

import numpy as np

sys.stdout.reconfigure(encoding='utf-8')
SFX = Path(__file__).resolve().parents[1] / 'web' / 'sfx'

# 每条音的方向预期（来自 docs/SFX_LIST.md），用来判断频谱是否跑偏
EXPECT = {
    'card.play.attack': ('金属短促', 'mid'),
    'card.play.skill': ('闷响石头', 'lo'),
    'card.play.power': ('低长持续', 'lo'),
    'card.play.cost': ('抽离', 'wide'),
    'combat.start': ('沉底重音', 'lo'),
    'enemy.hit': ('闷击带湿', 'lo'),
    'combat.hurt': ('更钝贴耳', 'lo'),
    'combat.block': ('金属盾震', 'mid'),
    'combat.kill': ('塌落', 'lo'),
    'state.resonance': ('低频轰鸣', 'lo'),
    'state.gaze': ('极短沙沙', 'hi'),
    'state.energy_empty': ('空握', 'lo'),
    'ui.click': ('石子相碰', 'mid'),
    'ui.page': ('纸页翻动', 'hi'),
    'special.boss_phase': ('远钟', 'mid'),
    'special.world_switch': ('水下浮沉', 'wide'),
    'special.egg': ('轻笑规模', 'mid'),
    'special.victory': ('低而长释放', 'lo'),
    'special.death': ('呼尽', 'lo'),
}


def read(p):
    with wave.open(str(p), 'rb') as w:
        n = w.getnframes()
        sr = w.getframerate()
        raw = w.readframes(n)
    x = np.frombuffer(raw, dtype='<i2').astype(float) / 32768.0
    return x, sr


def bands(x, sr):
    X = np.abs(np.fft.rfft(x))
    f = np.fft.rfftfreq(len(x), 1.0 / sr)
    e = X ** 2
    tot = e.sum() or 1.0
    lo = e[f < 300].sum() / tot
    mid = e[(f >= 300) & (f < 3000)].sum() / tot
    hi = e[f >= 3000].sum() / tot
    peak_f = f[int(np.argmax(X))] if len(X) else 0
    return lo, mid, hi, peak_f


print('%-28s %6s %5s %5s %5s %5s  %-12s %s' % ('文件', 'ms', '低频', '中频', '高频', '峰值Hz', '预期', '判定'))
print('-' * 100)

rows = []
for p in sorted(SFX.glob('*.wav')):
    x, sr = read(p)
    lo, mid, hi, pf = bands(x, sr)
    key = p.stem
    dur = len(x) / sr * 1000
    exp = EXPECT.get(key)
    verdict = ''
    if exp:
        tag = exp[1]
        if tag == 'lo' and lo < 0.30:
            verdict = '⚠ 低频不足'
        elif tag == 'hi' and hi < 0.30:
            verdict = '⚠ 高频不足'
        elif tag == 'mid' and mid < 0.30:
            verdict = '⚠ 中频不足'
        else:
            verdict = 'ok'
    print('%-28s %6.0f %5.0f%% %5.0f%% %5.0f%% %5.0f  %-12s %s'
          % (key, dur, lo * 100, mid * 100, hi * 100, pf, exp[0] if exp else '氛围', verdict))
    rows.append((key, dur, lo, mid, hi, pf, verdict))

print('\n--- 氛围循环接缝（首尾样本差，越小越好）---')
for p in sorted(SFX.glob('ambience.*.wav')):
    x, sr = read(p)
    seam = abs(float(x[0] - x[-1]))
    # 也看首尾 50ms 的 RMS 差，判断音量是否跳变
    w = int(sr * 0.05)
    r_head = float(np.sqrt(np.mean(x[:w] ** 2)))
    r_tail = float(np.sqrt(np.mean(x[-w:] ** 2)))
    d = abs(r_head - r_tail)
    flag = '⚠' if (seam > 0.02 or d > 0.02) else 'ok'
    print('%-28s 样本差 %5.3f  首尾RMS差 %5.3f  %s' % (p.stem, seam, d, flag))

print('\n--- 汇总 ---')
bad = [r for r in rows if r[6].startswith('⚠')]
print('总数 %d，频段方向可疑 %d 个' % (len(rows), len(bad)))
for r in bad:
    print('  ', r[0], r[6])
