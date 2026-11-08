# -*- coding: utf-8 -*-
"""素材盘点：数量、体积、按类型/子目录分布。

对任意目录或 .jar/.zip/.apk 跑 —— 用来量「别的游戏素材做到什么规模」，
以及量红渊自己的基线。

★ 只读文件大小与数量，不解包、不导出、不复制任何内容。
  目的是对比规模，不是拿别人的素材。

用法：
  python tools/asset_inventory.py <目录或压缩包> [--top 12]
  python tools/asset_inventory.py web/assets --top 8
  python tools/asset_inventory.py "D:\\Steam\\steamapps\\common\\SlayTheSpire"
"""
import argparse
import sys
import zipfile
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

KIND = {
    'image': {'.png', '.jpg', '.jpeg', '.webp', '.gif', '.bmp', '.tga', '.psd', '.aseprite'},
    'audio': {'.ogg', '.wav', '.mp3', '.flac', '.m4a', '.aiff'},
    'font': {'.ttf', '.otf', '.fnt', '.woff', '.woff2'},
    'data': {'.json', '.xml', '.yaml', '.yml', '.csv', '.txt', '.atlas', '.properties'},
    'video': {'.mp4', '.webm', '.mov', '.avi'},
    'code': {'.java', '.class', '.jar', '.js', '.py', '.cs', '.dll', '.exe'},
}


def kind_of(name):
    ext = Path(name).suffix.lower()
    for k, s in KIND.items():
        if ext in s:
            return k
    return 'other'


def human(n):
    for u in ('B', 'KB', 'MB', 'GB'):
        if n < 1024:
            return '%.1f %s' % (n, u)
        n /= 1024.0
    return '%.1f TB' % n


def scan_dir(root):
    """→ [(relpath, name, size)]"""
    out = []
    for p in root.rglob('*'):
        if p.is_file():
            try:
                out.append((p.relative_to(root).as_posix(), p.name, p.stat().st_size))
            except OSError:
                pass
    return out


def scan_zip(path):
    """压缩包（jar/apk/zip）不解压，只读目录表。"""
    out = []
    with zipfile.ZipFile(path) as z:
        for i in z.infolist():
            if not i.is_dir():
                out.append((i.filename, i.filename.rsplit('/', 1)[-1], i.file_size))
    return out


def report(entries, label, top):
    by_kind = defaultdict(lambda: [0, 0])
    by_ext = defaultdict(lambda: [0, 0])
    by_dir = defaultdict(lambda: [0, 0])
    for relpath, name, size in entries:
        k = kind_of(name)
        by_kind[k][0] += 1
        by_kind[k][1] += size
        ext = Path(name).suffix.lower() or '(无后缀)'
        by_ext[ext][0] += 1
        by_ext[ext][1] += size
        # 顶层目录（最多两级），用来找「素材在哪个包/目录」
        parts = relpath.split('/')
        key = '/'.join(parts[:2]) if len(parts) > 2 else ('/'.join(parts[:-1]) or '.')
        by_dir[key][0] += 1
        by_dir[key][1] += size

    total_n = len(entries)
    total_s = sum(e[2] for e in entries)
    print('# 素材盘点：%s' % label)
    print()
    print('文件总数 **%s**，合计 **%s**' % (format(total_n, ','), human(total_s)))
    print()

    print('## 按类型')
    print()
    print('| 类型 | 文件数 | 体积 | 占比 |')
    print('|---|---|---|---|')
    for k in ('image', 'audio', 'font', 'data', 'video', 'code', 'other'):
        if k in by_kind:
            n, s = by_kind[k]
            print('| %s | %s | %s | %.1f%% |' % (k, format(n, ','), human(s), 100.0 * s / max(1, total_s)))
    print()

    print('## 按扩展名（前 %d）' % top)
    print()
    print('| 扩展名 | 文件数 | 体积 |')
    print('|---|---|---|')
    for ext, (n, s) in sorted(by_ext.items(), key=lambda x: -x[1][0])[:top]:
        print('| %s | %s | %s |' % (ext, format(n, ','), human(s)))
    print()

    print('## 占体积最多的目录（前 %d）' % top)
    print()
    print('| 目录 | 文件数 | 体积 |')
    print('|---|---|---|')
    for d, (n, s) in sorted(by_dir.items(), key=lambda x: -x[1][1])[:top]:
        print('| %s | %s | %s |' % (d, format(n, ','), human(s)))
    print()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('target')
    ap.add_argument('--top', type=int, default=12)
    a = ap.parse_args()

    p = Path(a.target)
    if not p.exists():
        print('路径不存在：%s' % p)
        return 2

    if p.is_file() and zipfile.is_zipfile(p):
        entries = scan_zip(p)
        report(entries, '%s（压缩包内目录表，未解压）' % p.name, a.top)
    elif p.is_dir():
        # 目录里如果有 jar/zip，一并算进去（很多游戏把资源打包在 jar 里）
        entries = scan_dir(p)
        zips = [x for x in entries if x[1].lower().endswith(('.jar', '.zip', '.apk'))]
        report(entries, '%s（磁盘文件）' % p, a.top)
        for _, name, _ in zips[:4]:
            for relpath, _, _ in entries:
                if Path(relpath).name == name:
                    try:
                        inner = scan_zip(p / relpath)
                    except Exception:
                        continue
                    report(inner, '%s 内部' % relpath, a.top)
                    break
    else:
        print('既不是目录也不是压缩包：%s' % p)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
