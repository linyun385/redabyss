# -*- coding: utf-8 -*-
"""红渊音效合成器 · v2（2026-11-05 23:45 按用户反馈重做）

v1 → v2 改了什么（用户原话在括号里）：
  1. 「声音太小了、基本听不见」
     原因是两个技术问题叠在一起：
       a) 基频太低。victory 44Hz / combat.start 27Hz，笔记本扬声器放不出 150Hz 以下，
          等于静音。→ 全部提基频 + 加饱和（tanh 生成谐波，耳朵听不到基频但听得到谐波）
       b) 峰值归一化（peak 0.85）对人耳是错的，人感知的是平均能量。
          → 峰值提到 0.95 + 饱和提升 RMS
  2. 「界面切换只做一个（书页翻动）」→ ui.open + ui.close 合并成 ui.page
  3. 「入梦应该是惊醒、快速入梦，现在太长了」→ world_switch 从 1100ms 重做成 420ms
  4. 「通关结算太低沉，基本听不见」→ victory 基频 44 → 80Hz + 强谐波

设计依据：docs/SFX_LIST.md
用法：python tools/sfx_synth_full.py
"""
import sys
import wave
from pathlib import Path

import numpy as np

sys.stdout.reconfigure(encoding='utf-8')
SR = 44100
OUT = Path(__file__).resolve().parents[1] / 'web' / 'sfx'
OUT.mkdir(parents=True, exist_ok=True)
RNG = np.random.default_rng(20261105)


# ---------------- 基础工具 ----------------
def t_of(n):
    return np.arange(n) / SR


def env(n, attack=0.002, decay=0.08, power=2.2):
    t = t_of(n)
    a = np.clip(t / max(attack, 1e-5), 0, 1)
    d = np.exp(-t / max(decay, 1e-5))
    return (a * d) ** (1.0 / power)


def noise(n):
    return RNG.standard_normal(n)


def filt(x, lo=None, hi=None):
    """零相位 FFT 频域滤波。lo=下限 Hz，hi=上限 Hz，都不给=原样。"""
    n = len(x)
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1.0 / SR)
    m = np.ones_like(f)
    if lo:
        m = m * (1.0 / (1.0 + (lo / np.maximum(f, 1e-9)) ** 4))
    if hi:
        m = m * (1.0 / (1.0 + (f / hi) ** 4))
    return np.fft.irfft(X * m, n)


def metal(n, f0, ratios, amps, seed=None):
    """不谐和分音叠加——「敲金属」的关键。"""
    t = t_of(n)
    out = np.zeros(n)
    r = np.random.default_rng(seed) if seed is not None else RNG
    for ratio, amp in zip(ratios, amps):
        out += amp * np.sin(2 * np.pi * f0 * ratio * t + r.uniform(0, 2 * np.pi))
    return out / max(1e-9, np.sum(amps))


def sweep(n, f_start, f_end, curve=1.0):
    """频率扫描正弦（相位累加）。"""
    t = t_of(n)
    u = (t / max(float(t[-1]), 1e-9)) ** curve
    f = f_start + (f_end - f_start) * u
    return np.sin(2 * np.pi * np.cumsum(f) / SR)


def normalize(x, peak=0.85):
    x = np.asarray(x, dtype=float)
    m = np.max(np.abs(x)) or 1.0
    return x / m * peak


def save(name, x, peak=0.95, drive=1.0):
    """写 wav。

    drive > 1 = 轻度饱和（tanh waveshaping）。这不是效果器，是**可闻性**手段：
    笔记本扬声器放不出 150Hz 以下，纯低频音效等于静音。
    tanh 把低频分量变成「低频 + 谐波」，耳朵听不到基频但听得到谐波，
    于是仍然「觉得低」，实际是听得到的（音频里叫 bass exciter / 缺失基频）。
    """
    x = normalize(np.asarray(x, dtype=float), 0.9)
    if drive > 1.0:
        x = np.tanh(x * drive) / np.tanh(drive)
    x = normalize(x, peak)
    data = (x * 32767).astype('<i2')
    p = OUT / name
    with wave.open(str(p), 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())
    rms = float(np.sqrt(np.mean(x ** 2)))
    print('  %-28s %6.0f ms  %7.1f KB  peak=%.2f rms=%.3f drive=%.1f'
          % (name, len(x) / SR * 1000, p.stat().st_size / 1024, peak, rms, drive))


def loopify(x, fade_sec=1.0):
    """把尾巴交叉淡化叠到开头，循环接缝听不出来。"""
    f = int(SR * fade_sec)
    if len(x) <= f * 2:
        return x
    head = x[:f].copy()
    tail = x[-f:].copy()
    ramp = np.linspace(0.0, 1.0, f)
    mixed = tail * (1 - ramp) + head * ramp
    out = x[:-f].copy()
    out[:f] = mixed
    return out


def ticks(n, period, jitter=0.0, width=0.004, seed=None):
    """时间轴上撒短脉冲（滴水 / 盖革计数器 / 心跳）。"""
    r = np.random.default_rng(seed)
    out = np.zeros(n)
    w = int(SR * width)
    tt = 0.0
    while True:
        pos = int(tt * SR)
        if pos >= n:
            break
        amp = r.uniform(0.4, 1.0)
        seg = min(w, n - pos)
        out[pos:pos + seg] += amp * env(seg, 0.0005, width * 0.35, 1.5)
        tt += period * (1.0 + r.uniform(-jitter, jitter))
        if period <= 0:
            break
    return out


print('输出目录:', OUT)
print('\n--- 卡牌 ---')

# 1) card.play.attack —— 短促金属（中频，不需要饱和）
n = int(SR * 0.20)
t = t_of(n)
strike = metal(n, 820, [1.0, 2.13, 3.37, 4.71], [1.0, 0.7, 0.45, 0.25]) * env(n, 0.001, 0.030)
air = filt(noise(n), None, 3600) * env(n, 0.002, 0.045) * 0.30
ring = metal(n, 620, [1.0, 1.47, 2.09], [1.0, 0.5, 0.28]) * np.exp(-t / 0.11) * 0.45
save('card.play.attack.wav', strike * 0.75 + air + ring, drive=1.0)

# 2) card.play.skill —— 闷响石头（基频 38→56，加饱和）
n = int(SR * 0.18)
t = t_of(n)
thump = np.sin(2 * np.pi * (90 * np.exp(-t / 0.04) + 56) * t) * env(n, 0.0015, 0.045, 1.8)
stone = metal(n, 260, [1.0, 2.71, 4.33], [1.0, 0.35, 0.16], seed=7) * env(n, 0.001, 0.026)
air = filt(noise(n), 300, 1500) * env(n, 0.002, 0.030) * 0.40
save('card.play.skill.wav', thump * 0.85 + stone * 0.55 + air, drive=2.2)

# 3) card.play.power —— 低而长的持续感（58/29 → 78/39，加饱和）
n = int(SR * 0.75)
t = t_of(n)
base = np.sin(2 * np.pi * 78 * t) * env(n, 0.060, 0.45, 1.4)
hum = np.sin(2 * np.pi * 156 * t + 0.4) * env(n, 0.080, 0.40, 1.5) * 0.40
sub = np.sin(2 * np.pi * 39 * t) * env(n, 0.100, 0.50, 1.2) * 0.50
save('card.play.power.wav', base + hum + sub, drive=2.0)

# 4) card.play.cost —— 「东西被拿走」的抽离声
n = int(SR * 0.22)
t = t_of(n)
hi = filt(noise(n), 1800, 6000) * env(n, 0.004, 0.035) * 0.70
lo = filt(noise(n), 200, 900) * env(n, 0.010, 0.090) * 0.80
suck = sweep(n, 320, 120, curve=1.6) * env(n, 0.020, 0.080) * 0.50
save('card.play.cost.wav', hi + lo + suck, drive=1.8)

print('\n--- 战斗 ---')

# 5) combat.start —— 一下沉底的重音（33 → 45 基频，饱和）
n = int(SR * 0.55)
t = t_of(n)
boom = np.sin(2 * np.pi * (85 * np.exp(-t / 0.12) + 45) * t) * env(n, 0.004, 0.20, 1.3)
sub = np.sin(2 * np.pi * 38 * t) * env(n, 0.008, 0.28, 1.1) * 0.55
dust = filt(noise(n), 60, 380) * env(n, 0.010, 0.12) * 0.35
save('combat.start.wav', boom + sub + dust, drive=2.4)

# 6) enemy.hit —— 闷击带湿（42 → 50 基频，饱和）
n = int(SR * 0.22)
t = t_of(n)
thump = np.sin(2 * np.pi * (105 * np.exp(-t / 0.05) + 50) * t) * env(n, 0.002, 0.055, 1.8)
wet = filt(noise(n), None, 900) * env(n, 0.004, 0.070) * 0.55
tail = filt(noise(n), None, 260) * np.exp(-t / 0.10) * 0.25
save('enemy.hit.wav', thump * 0.9 + wet + tail, drive=2.2)

# 7) combat.hurt —— 比 enemy.hit 更钝、更贴耳（34 → 46 基频）
n = int(SR * 0.26)
t = t_of(n)
body = np.sin(2 * np.pi * (95 * np.exp(-t / 0.06) + 46) * t) * env(n, 0.003, 0.075, 1.6)
close = filt(noise(n), None, 420) * env(n, 0.006, 0.085) * 0.70
rumble = np.sin(2 * np.pi * 40 * t) * np.exp(-t / 0.14) * 0.30
save('combat.hurt.wav', body + close + rumble, drive=2.2)

# 8) combat.block —— 金属盾面轻震（中频，不饱和）
n = int(SR * 0.30)
t = t_of(n)
shield = metal(n, 540, [1.0, 1.73, 2.91, 4.17], [1.0, 0.6, 0.35, 0.2], seed=11) * np.exp(-t / 0.09)
tick = filt(noise(n), 2200, 7000) * env(n, 0.001, 0.012) * 0.45
save('combat.block.wav', shield * 0.8 + tick, drive=1.0)

# 9) combat.kill —— 塌落声，短（40 → 52 基频，饱和）
n = int(SR * 0.42)
t = t_of(n)
fall = np.sin(2 * np.pi * (150 * np.exp(-t / 0.16) + 52) * t) * env(n, 0.004, 0.18, 1.3)
debris = filt(noise(n), 120, 1500) * env(n, 0.006, 0.16, 1.6) * 0.55
thud = np.sin(2 * np.pi * 44 * t) * np.exp(-t / 0.10) * 0.5
save('combat.kill.wav', fall + debris + thud, drive=2.2)

print('\n--- 状态 ---')

# 10) state.resonance —— 低频轰鸣，一拍（46/49 → 58/61）
n = int(SR * 0.55)
t = t_of(n)
drone = np.sin(2 * np.pi * 58 * t) * env(n, 0.030, 0.26, 1.2)
beat = np.sin(2 * np.pi * 61 * t) * env(n, 0.030, 0.24, 1.2) * 0.6
low = filt(noise(n), None, 130) * env(n, 0.040, 0.20) * 0.5
save('state.resonance.wav', drone + beat + low, drive=2.0)

# 11) state.gaze —— 极短的沙沙声
n = int(SR * 0.12)
t = t_of(n)
grain = filt(noise(n), 3000, 11000) * env(n, 0.004, 0.022, 1.4) * 0.9
whisper = filt(noise(n), 1400, 4000) * env(n, 0.008, 0.040) * 0.35
save('state.gaze.wav', grain + whisper, drive=1.0)

# 12) state.energy_empty —— 空握的一声（中频被挖掉）
n = int(SR * 0.16)
t = t_of(n)
low = filt(noise(n), None, 320) * env(n, 0.004, 0.045) * 0.8
mid = filt(noise(n), 500, 700) * env(n, 0.006, 0.030) * 0.18
knock = np.sin(2 * np.pi * 130 * t) * env(n, 0.002, 0.030) * 0.35
save('state.energy_empty.wav', low + mid + knock, drive=2.0)

print('\n--- 界面 ---')

# 13) ui.click —— 轻石子相碰（中频）
n = int(SR * 0.07)
body = metal(n, 1450, [1.0, 1.62, 2.41], [1.0, 0.55, 0.3], seed=3) * env(n, 0.0015, 0.018)
hiss = filt(noise(n), None, 5200) * env(n, 0.001, 0.010) * 0.35
click = body * 0.7 + hiss
shift = int(SR * 0.02)
click[shift:] += 0.45 * (metal(n - shift, 2100, [1.0, 1.51], [1.0, 0.4], seed=5)
                         * env(n - shift, 0.001, 0.012))
save('ui.click.wav', click, drive=1.0)

# 14) ui.page —— 纸页翻动（2026-11-05 v3）
# 用户说 v2「不像书页翻动」，给了一个参考 mp3。
# v2 的问题是**本质是一段连续带通噪声**，听起来只能是「嘶——」。
# 纸的声音是碎的：几十个 4-15ms 的摩擦颗粒叠在一起。
# 做法：整段噪声过一次带通，再乘一个「颗粒包络」（一串随机宽度的短脉冲）。
# 这是合成摩擦类音效的标准手法——颗粒包络决定「碎」，带通决定「纸」。
n = int(SR * 0.34)
t = t_of(n)
_r = np.random.default_rng(77)

mask = np.zeros(n)          # 颗粒包络
pos = 0
while pos < n:
    w = int(SR * _r.uniform(0.0035, 0.015))
    seg = min(w, n - pos)
    if seg <= 1:
        break
    mask[pos:pos + seg] = _r.uniform(0.22, 1.0) * env(seg, 0.0004, seg / SR * 0.55, 1.0)
    pos += seg + int(SR * _r.uniform(0.0012, 0.0075))

overall = np.clip(t / 0.010, 0, 1) * np.where(
    t < 0.255, 1.0, np.exp(-(t - 0.255) / 0.032))

crack = filt(noise(n), 2400, 13000) * mask * overall * 0.95   # 碎的摩擦
body = filt(noise(n), 220, 950) * overall * 0.34 * (1.0 - 0.55 * np.clip(t / 0.34, 0, 1))
settle = filt(noise(n), 500, 2400) * env(n, 0.020, 0.048) * 0.26   # 纸落下的软着陆
save('ui.page.wav', crack + body + settle, drive=1.0)

print('\n--- 特殊 ---')

# 15) special.boss_phase —— 一声很远的钟（中频为主）
n = int(SR * 2.4)
t = t_of(n)
bell = metal(n, 196, [1.0, 2.76, 5.40, 8.93], [1.0, 0.55, 0.30, 0.16], seed=17) * np.exp(-t / 0.85)
far = metal(n, 392, [1.0, 2.02, 3.01], [1.0, 0.4, 0.2], seed=19) * np.exp(-t / 1.05) * 0.28
body = metal(n, 784, [1.0, 1.58], [1.0, 0.4], seed=21) * np.exp(-t / 0.55) * 0.14
air = filt(noise(n), 300, 2600) * np.exp(-t / 0.40) * 0.10
save('special.boss_phase.wav', bell + far + body + air, drive=1.0)

# 16) special.world_switch —— 惊醒 / 快速入梦（2026-11-05 重做）
# 用户：「入梦应该是那种惊醒、快速入梦的状态，现在声音太长了」
# 原版 1100ms 的「水下浮沉」→ 现在 420ms：一下睁眼（高频瞬态）+ 快速沉下去。
n = int(SR * 0.42)
t = t_of(n)
wake = filt(noise(n), 1200, 8000) * env(n, 0.001, 0.020, 1.5) * 0.90
snap = sweep(n, 1800, 320, curve=0.35) * env(n, 0.002, 0.048, 1.3) * 0.45
sink = filt(noise(n), None, 620) * env(n, 0.030, 0.150) * 0.55
pulse = np.sin(2 * np.pi * (130 * np.exp(-t / 0.05) + 62) * t) * env(n, 0.004, 0.085, 1.6) * 0.50
save('special.world_switch.wav', wake + snap + sink + pulse, drive=1.8)

# 17) special.egg —— 一声轻笑规模的短音（三粒上行）
n = int(SR * 0.34)
t = t_of(n)
glint = np.zeros(n)
for i, (freq, pos) in enumerate([(880, 0.00), (1046, 0.055), (1318, 0.115)]):
    pos_n = int(SR * pos)
    seg = n - pos_n
    tone = np.sin(2 * np.pi * freq * t_of(seg)) * env(seg, 0.003, 0.045, 1.4) * (0.8 - i * 0.18)
    glint[pos_n:] += tone
bell_tail = metal(n, 1318, [1.0, 2.01, 3.02], [1.0, 0.3, 0.12], seed=29) * np.exp(-t / 0.10) * 0.22
save('special.egg.wav', glint + bell_tail, drive=1.0)

# 18) special.victory —— 长而低的释放（2026-11-05 重做）
# 用户：「太低沉了，基本听不见」。原来基频 44Hz，笔记本放不出来。
# 现在 80Hz + 三个谐波（160/240/320），低但可闻，仍然不是凯旋号角。
n = int(SR * 1.80)
t = t_of(n)
rise = np.clip(t / 0.50, 0, 1) ** 2.0
fall = np.exp(-np.maximum(t - 0.70, 0) / 0.45)
body = np.sin(2 * np.pi * 80 * t) * rise * fall
h2 = np.sin(2 * np.pi * 160 * t + 0.6) * rise * fall * 0.45
h3 = np.sin(2 * np.pi * 240 * t + 1.2) * rise * fall * 0.24
h4 = np.sin(2 * np.pi * 320 * t + 0.2) * rise * fall * 0.12
save('special.victory.wav', body + h2 + h3 + h4, drive=2.0)

# 19) special.death —— 一口气呼尽（120-520Hz，加饱和）
n = int(SR * 2.00)
t = t_of(n)
breath = filt(noise(n), 120, 520) * np.exp(-t / 0.70) * (1.0 - 0.60 * np.clip(t / 2.0, 0, 1))
chest = filt(noise(n), None, 180) * np.exp(-t / 1.10) * 0.45
save('special.death.wav', breath + chest, drive=2.0)

print('\n--- 氛围（8 层，循环）---')

SEC = 8.0
NB = int(SR * SEC)
AMB_PEAK = 0.72   # v1 是 0.55，太轻了


def lfo(n, hz, depth, phase=0.0):
    t = t_of(n)
    return 1.0 - depth + depth * (0.5 + 0.5 * np.sin(2 * np.pi * hz * t + phase))


# depth1 地表死寂区：远处风 + 地表电台残响
n = NB
t = t_of(n)
wind = filt(noise(n), 40, 420) * lfo(n, 0.07, 0.55) * 0.9
radio = filt(noise(n), 900, 2200) * lfo(n, 0.31, 0.9) * 0.10
save('ambience.depth1.wav', loopify(wind + radio, 1.0), peak=AMB_PEAK, drive=1.6)

# depth2 外层冷洞：滴水 + 金属冷缩咔声
n = NB
drop = ticks(n, 1.35, jitter=0.45, width=0.006, seed=31)
drop = filt(drop, 1800, 6500) * 0.85
creak = ticks(n, 3.10, jitter=0.5, width=0.020, seed=37)
creak = metal(n, 320, [1.0, 2.4, 3.9], [1.0, 0.4, 0.2], seed=41) * creak
bed = filt(noise(n), None, 260) * 0.25
save('ambience.depth2.wav', loopify(drop + creak + bed, 1.0), peak=AMB_PEAK, drive=1.6)

# depth3 干旱空洞区：沙粒摩擦 + 岩层空腔回声
n = NB
sand = filt(noise(n), 2500, 9000) * lfo(n, 0.17, 0.85) * 0.55
cavity = filt(noise(n), 120, 700) * lfo(n, 0.05, 0.4) * 0.45
save('ambience.depth3.wav', loopify(sand + cavity, 1.0), peak=AMB_PEAK, drive=1.6)

# depth4 稳定空洞海：极低频嗡鸣 + 几乎听不见的合唱
n = NB
t = t_of(n)
drone = np.sin(2 * np.pi * 31 * t) * 0.7 + np.sin(2 * np.pi * 37 * t) * 0.5
choir = (np.sin(2 * np.pi * 62 * t) + 0.7 * np.sin(2 * np.pi * 93 * t)
         + 0.5 * np.sin(2 * np.pi * 124 * t)) * 0.10 * lfo(n, 0.04, 0.6)
save('ambience.depth4.wav', loopify(drone * 0.35 + choir, 1.5), peak=AMB_PEAK, drive=2.4)

# depth5 热泉裂带：蒸汽 + 金属呻吟 + 远处泵机
n = NB
t = t_of(n)
steam = filt(noise(n), 1200, 5200) * lfo(n, 0.23, 0.75) * 0.30
groan = np.sin(2 * np.pi * (68 + 7 * np.sin(2 * np.pi * 0.06 * t)) * t) * lfo(n, 0.09, 0.7) * 0.55
pump = ticks(n, 1.60, jitter=0.02, width=0.05, seed=43)
pump = filt(pump, None, 200) * 0.45
save('ambience.depth5.wav', loopify(steam + groan + pump, 1.0), peak=AMB_PEAK, drive=1.8)

# depth6 辐射矿石区：电流嘶嘶 + 盖革计数器哒声
n = NB
hiss = filt(noise(n), 3500, 11000) * 0.16
clicks = ticks(n, 0.42, jitter=0.85, width=0.0035, seed=47) * 0.85
clicks = filt(clicks, 2000, 9000)
save('ambience.depth6.wav', loopify(hiss + clicks, 0.8), peak=AMB_PEAK, drive=1.0)

# depth7 核心高热区：心跳般低频脉冲 + 烧灼声
n = NB
beat = ticks(n, 0.92, jitter=0.008, width=0.090, seed=53)
t = t_of(n)
beat = filt(beat, None, 110) * 0.95
pulse = np.sin(2 * np.pi * 52 * t) * lfo(n, 1.09, 0.55) * 0.45
sear = filt(noise(n), 900, 3800) * 0.12
save('ambience.depth7.wav', loopify(beat + pulse + sear, 1.0), peak=AMB_PEAK, drive=2.0)

# depth8 红渊核心：血声 + 所有层的回声叠在一起
n = NB
t = t_of(n)
blood = ticks(n, 0.70, jitter=0.03, width=0.070, seed=59)
blood = filt(blood, None, 140) * 0.9
echo = filt(noise(n), 60, 900) * lfo(n, 0.03, 0.5) * 0.30
deep = np.sin(2 * np.pi * 28 * t) * 0.45
save('ambience.depth8.wav', loopify(blood + echo + deep, 1.2), peak=AMB_PEAK, drive=2.2)

print('\n完成。文件数:', len(list(OUT.glob('*.wav'))))
