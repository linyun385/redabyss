# -*- coding: utf-8 -*-
"""红渊音效合成器 · 样品版

为什么合成而不是找采样：
  · SFX_LIST 的审美目标是「干、闷、纸、金属、地底」——这一类用参数描述比找文件准
  · 20 多个音来源统一的采样库很难凑，拼起来会杂；合成能保证同一套音色
  · 零成本、可反复调参

这里只做三个样品，验证音色方向；方向对了再批量做全 24 个。
"""
import sys
import wave
from pathlib import Path

import numpy as np

sys.stdout.reconfigure(encoding='utf-8')
SR = 44100
OUT = Path(__file__).resolve().parents[1] / 'web' / 'sfx'
OUT.mkdir(parents=True, exist_ok=True)


def env(n, attack=0.002, decay=0.08, power=2.2):
    """指数衰减包络：起音极短、尾巴按 power 收。"""
    t = np.arange(n) / SR
    a = np.clip(t / max(attack, 1e-5), 0, 1)
    d = np.exp(-t / max(decay, 1e-5))
    return (a * d) ** (1.0 / power)


def lowpass(x, cutoff):
    """一阶 IIR 低通，手写（不依赖 scipy）。"""
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc = (1 - a) * v + a * acc
        y[i] = acc
    return y


def noise(n, rng):
    return rng.standard_normal(n)


def metal_partial(n, f0, ratios, amps, rng):
    """金属泛音：不谐和分音叠加，这是「敲金属」的关键。"""
    t = np.arange(n) / SR
    out = np.zeros(n)
    for r, a in zip(ratios, amps):
        out += a * np.sin(2 * np.pi * f0 * r * t + rng.uniform(0, 2 * np.pi))
    return out / max(1e-9, np.sum(amps))


def normalize(x, peak=0.85):
    m = np.max(np.abs(x)) or 1.0
    return x / m * peak


def save(name, x):
    data = (normalize(x) * 32767).astype('<i2')
    p = OUT / name
    with wave.open(str(p), 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())
    print('%-26s %5.0f ms  %6.1f KB' % (name, len(x) / SR * 1000, p.stat().st_size / 1024))


rng = np.random.default_rng(20261105)

# 1) ui.click —— 轻石子相碰：极短、两粒、高频衰减
n = int(SR * 0.07)
body = metal_partial(n, 1450, [1.0, 1.62, 2.41], [1.0, 0.55, 0.3], rng) * env(n, 0.0015, 0.018)
hiss = lowpass(noise(n, rng), 5200) * env(n, 0.001, 0.010) * 0.35
click = body * 0.7 + hiss
# 第二粒（20ms 后）
shift = int(SR * 0.02)
click[shift:] += 0.45 * (metal_partial(n - shift, 2100, [1.0, 1.51], [1.0, 0.4], rng)
                         * env(n - shift, 0.001, 0.012))
save('ui.click.wav', click)

# 2) card.play.attack —— 短促金属：起手一记锐音，后半带金属鸣
n = int(SR * 0.20)
t = np.arange(n) / SR
strike = metal_partial(n, 820, [1.0, 2.13, 3.37, 4.71], [1.0, 0.7, 0.45, 0.25], rng) * env(n, 0.001, 0.030)
air = lowpass(noise(n, rng), 3600) * env(n, 0.002, 0.045) * 0.30
ring = metal_partial(n, 620, [1.0, 1.47, 2.09], [1.0, 0.5, 0.28], rng) * np.exp(-t / 0.11) * 0.45
save('card.play.attack.wav', strike * 0.75 + air + ring)

# 3) enemy.hit —— 闷击带湿：低频冲击 + 带通噪声尾
n = int(SR * 0.22)
t = np.arange(n) / SR
thump = np.sin(2 * np.pi * (95 * np.exp(-t / 0.05) + 42) * t) * env(n, 0.002, 0.055, 1.8)
wet = lowpass(noise(n, rng), 900) * env(n, 0.004, 0.070) * 0.55
tail = lowpass(noise(n, rng), 260) * np.exp(-t / 0.10) * 0.25
save('enemy.hit.wav', thump * 0.9 + wet + tail)

print('\n输出目录:', OUT)
