# -*- coding: utf-8 -*-
"""_tone_stats.py — T266 色调分布统计（只读 web/assets/art，产出 data/stat_tone.json）

做法：
  1. 扫描 web/assets/art 下前缀为 enemy/dive/trem/event/anm/cng 的 .webp
     （排除 *.old.webp），共 461 张，与 data/qa_auto.json 的 items 一一对账。
  2. 每张图 convert('RGB') 后降采样到最长边 256px（thumbnail, BICUBIC，
     与 tools/art_qa.py 的 im.thumbnail((256,256)) 同口径），
     用 ImageStat 取 R/G/B 三通道均值 [0-255]。
  3. red_ratio 双轨：a) 直接复用 data/qa_auto.json 按图 id 对上的 red_ratio；
     b) 本脚本按 tools/art_qa.py 的【代码】口径复算
     （r>60 且 r>=1.4g 且 r>=1.4b 的像素占比；注意 art_qa 的 meta 注释写的是
     r≥60，与其代码 r>60 不一致，此处以代码为准），输出最大偏差供「可复算」验收。
  4. 按卡组（前缀）分段与全量，各通道均值与 red_ratio 出 P10/P50/P90
     （线性插值分位，与 numpy 默认一致，不依赖 numpy）。
  5. 写 data/stat_tone.json（meta + 分段统计 + 分位表 + qa 对账）。

可重跑：python tools/_tone_stats.py
"""
import json
import os
import sys
from datetime import datetime

from PIL import Image, ImageStat

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ART_DIR = os.path.join(ROOT, 'web', 'assets', 'art')
QA_PATH = os.path.join(ROOT, 'data', 'qa_auto.json')
OUT_PATH = os.path.join(ROOT, 'data', 'stat_tone.json')

SEGS = ['enemy', 'dive', 'trem', 'event', 'anm', 'cng']
SIZE = 256          # 降采样最长边
KEYS = ('r', 'g', 'b', 'red_ratio', 'red_ratio_recalc')


def percentile(sorted_vals, q):
    """线性插值分位（numpy 'linear' 口径）。sorted_vals 必须已升序。"""
    if not sorted_vals:
        return None
    if len(sorted_vals) == 1:
        return sorted_vals[0]
    pos = (len(sorted_vals) - 1) * q / 100.0
    lo = int(pos)
    hi = min(lo + 1, len(sorted_vals) - 1)
    frac = pos - lo
    return sorted_vals[lo] * (1.0 - frac) + sorted_vals[hi] * frac


def pct_block(vals):
    s = sorted(vals)
    return {
        'p10': round(percentile(s, 10), 4),
        'p50': round(percentile(s, 50), 4),
        'p90': round(percentile(s, 90), 4),
    }


def load_files():
    """返回 {seg: [绝对路径, ...]}，排除 .old.webp，文件名排序保证确定性。"""
    out = {seg: [] for seg in SEGS}
    for name in sorted(os.listdir(ART_DIR)):
        if not name.lower().endswith('.webp') or name.endswith('.old.webp'):
            continue
        seg = name.split('_')[0]
        if seg in out:
            out[seg].append(os.path.join(ART_DIR, name))
    return out


def red_ratio_of(im):
    """tools/art_qa.py 代码口径：r>60 且 r>=1.4g 且 r>=1.4b 的像素占比。"""
    data = im.tobytes()          # RGB 三字节一像素
    n = len(data) // 3
    hit = 0
    for i in range(0, len(data), 3):
        r = data[i]
        if r > 60 and r >= 1.4 * data[i + 1] and r >= 1.4 * data[i + 2]:
            hit += 1
    return hit / n if n else 0.0


def sample(path):
    im = Image.open(path).convert('RGB')
    im.thumbnail((SIZE, SIZE), Image.Resampling.BICUBIC)
    means = ImageStat.Stat(im).mean  # [R, G, B]
    return means, red_ratio_of(im)


def mean(vals):
    return sum(vals) / len(vals)


def seg_report(vals):
    return {
        'count': len(vals['r']),
        'r_mean': pct_block(vals['r']),
        'g_mean': pct_block(vals['g']),
        'b_mean': pct_block(vals['b']),
        'red_ratio': pct_block(vals['red_ratio']),
        'red_ratio_recalc': pct_block(vals['red_ratio_recalc']),
    }


def main():
    files = load_files()
    total = sum(len(v) for v in files.values())

    qa = json.load(open(QA_PATH, encoding='utf-8'))
    qa_map = {it['id']: it.get('red_ratio') for it in qa['items']}

    seg_vals = {seg: {k: [] for k in KEYS} for seg in SEGS}
    qa_checked = 0
    qa_max_diff = 0.0
    errors = []

    for seg in SEGS:
        for path in files[seg]:
            stem = os.path.splitext(os.path.basename(path))[0]
            try:
                means, rr = sample(path)
            except Exception as e:  # 单张坏图不拖垮整体，落账后跳过
                errors.append({'file': os.path.basename(path), 'error': str(e)})
                continue
            seg_vals[seg]['r'].append(means[0])
            seg_vals[seg]['g'].append(means[1])
            seg_vals[seg]['b'].append(means[2])
            seg_vals[seg]['red_ratio_recalc'].append(rr)
            if stem in qa_map and qa_map[stem] is not None:
                seg_vals[seg]['red_ratio'].append(qa_map[stem])
                qa_checked += 1
                qa_max_diff = max(qa_max_diff, abs(qa_map[stem] - rr))

    all_vals = {k: [] for k in KEYS}
    for seg in SEGS:
        for k in KEYS:
            all_vals[k].extend(seg_vals[seg][k])
    overall = seg_report(all_vals)

    # —— 结论（≤5 行；每一句都由表内数字算出，重跑不变）——
    def seg_p50(seg, k):
        return pct_block(seg_vals[seg][k])['p50']

    def seg_mean(seg, k):
        return mean(seg_vals[seg][k])

    red_rank = sorted(SEGS, key=lambda s: seg_p50(s, 'red_ratio'))
    luma_rank = sorted(SEGS, key=lambda s: seg_mean(s, 'r') + seg_mean(s, 'g') + seg_mean(s, 'b'))
    warm_rank = sorted(SEGS, key=lambda s: seg_mean(s, 'r') - seg_mean(s, 'b'))
    spread = overall['red_ratio']['p90'] - overall['red_ratio']['p10']
    summary_lines = [
        '红占比(red_ratio) P50 排序（低→高）：%s；最高 %s P50=%.4f，最低 %s P50=%.4f，全量 P10-P90 跨度 %.4f。'
        % (' < '.join('%s %.4f' % (s, seg_p50(s, 'red_ratio')) for s in red_rank),
           red_rank[-1], seg_p50(red_rank[-1], 'red_ratio'),
           red_rank[0], seg_p50(red_rank[0], 'red_ratio'), spread),
        '亮度(R+G+B 均值) 排序（暗→亮）：最暗 %s（%.1f），最亮 %s（%.1f）；全量 R/G/B 均值 %.1f/%.1f/%.1f，暖偏(R-B)全量 %+.1f。'
        % (luma_rank[0], seg_mean(luma_rank[0], 'r') + seg_mean(luma_rank[0], 'g') + seg_mean(luma_rank[0], 'b'),
           luma_rank[-1], seg_mean(luma_rank[-1], 'r') + seg_mean(luma_rank[-1], 'g') + seg_mean(luma_rank[-1], 'b'),
           mean(all_vals['r']), mean(all_vals['g']), mean(all_vals['b']),
           mean(all_vals['r']) - mean(all_vals['b'])),
        '暖偏(R-B 均值差) 排序（低→高）：%s。'
        % ' < '.join('%s %+.1f' % (s, seg_mean(s, 'r') - seg_mean(s, 'b')) for s in warm_rank),
        'red_ratio 双轨对账（qa_auto 原值 vs 本脚本复算）：%d/%d 张，最大绝对偏差 %.5f（同 256px 降采样、同谓词口径）。'
        % (qa_checked, total, qa_max_diff),
        '样本 %d 张（%s），坏图 %d 张；分位=线性插值 P10/P50/P90；脚本 tools/_tone_stats.py 可重跑复算。'
        % (total, '/'.join('%s %d' % (s, len(files[s])) for s in SEGS), len(errors)),
    ]

    out = {
        'meta': {
            'tool': 'tools/_tone_stats.py',
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'art_dir': os.path.relpath(ART_DIR, ROOT),
            'downsample': "convert RGB -> thumbnail((%d,%d), BICUBIC)（与 tools/art_qa.py 同口径）" % (SIZE, SIZE),
            'percentile': 'linear interpolation (numpy-linear style), P10/P50/P90',
            'red_ratio_def': 'r>60 且 r>=1.4g 且 r>=1.4b 的像素占比——以 tools/art_qa.py 代码为准'
                             '（其 meta 注释写 r≥60，代码是 r>60，两处不一致已记入）',
            'qa_source': os.path.relpath(QA_PATH, ROOT),
            'segments': SEGS,
            'summary': summary_lines,
        },
        'overall': overall,
        'segments': {s: seg_report(seg_vals[s]) for s in SEGS},
        'qa_check': {'checked': qa_checked, 'total_expected': 461,
                     'max_abs_diff_red_ratio': round(qa_max_diff, 6)},
        'errors': errors,
    }
    with open(OUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2, sort_keys=True)

    print('written:', os.path.relpath(OUT_PATH, ROOT))
    print('count per seg:', {s: len(files[s]) for s in SEGS}, 'total', total)
    print('qa checked %d, max diff %.5f' % (qa_checked, qa_max_diff))
    for line in summary_lines:
        print(line)
    return 0


if __name__ == '__main__':
    sys.exit(main())
