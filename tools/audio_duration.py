# -*- coding: utf-8 -*-
"""量 ogg 音频时长（Vorbis，不依赖任何第三方库）。

原理：
  · 第一页里 \x01vorbis 之后的第 12 字节是采样率（4 字节小端）
  · 最后一页 "OggS" 之后偏移 6 处是 granule position（8 字节小端）= 总采样数
  · 时长 = granule / sample_rate

用法：
  python tools/audio_duration.py <文件或目录或 jar>
"""
import sys
import zipfile
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')


def ogg_seconds(data):
    i = data.find(b'\x01vorbis')
    if i < 0:
        return None
    rate = int.from_bytes(data[i + 12:i + 16], 'little')
    if not rate:
        return None
    j = data.rfind(b'OggS')
    if j < 0:
        return None
    gran = int.from_bytes(data[j + 6:j + 14], 'little')
    return gran / float(rate)


def human(sec):
    m, s = divmod(int(round(sec)), 60)
    return '%d:%02d' % (m, s)


def main():
    tgt = Path(sys.argv[1])
    rows = []

    if tgt.is_file() and zipfile.is_zipfile(tgt):
        with zipfile.ZipFile(tgt) as z:
            for n in z.namelist():
                if n.lower().endswith('.ogg'):
                    with z.open(n) as f:
                        d = f.read()
                    s = ogg_seconds(d)
                    if s:
                        rows.append((n, s, len(d)))
    elif tgt.is_dir():
        for p in tgt.rglob('*.ogg'):
            s = ogg_seconds(p.read_bytes())
            if s:
                rows.append((p.name, s, p.stat().st_size))
    else:
        print('不识别的目标：%s' % tgt)
        return 2

    if not rows:
        print('没找到 .ogg')
        return 1

    rows.sort(key=lambda x: -x[1])
    total = sum(r[1] for r in rows)
    print('| 文件 | 时长 | 体积 |')
    print('|---|---|---|')
    for n, s, sz in rows:
        print('| %s | %s | %.1f MB |' % (n.split('/')[-1], human(s), sz / 1048576.0))
    print()
    print('**共 %d 个，合计 %s（%d 分钟）**，平均 %s'
          % (len(rows), human(total), round(total / 60), human(total / len(rows))))
    return 0


if __name__ == '__main__':
    sys.exit(main())
