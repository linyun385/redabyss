# -*- coding: utf-8 -*-
"""把 art_studio2.py（带审图/标记功能的版本）覆盖到 art_studio.py，并删掉临时文件。"""
from pathlib import Path

G = Path(__file__).resolve().parents[1]
src = G / 'tools' / 'art_studio2.py'
dst = G / 'tools' / 'art_studio.py'
dst.write_text(src.read_text(encoding='utf-8'), encoding='utf-8')
src.unlink()
import ast
ast.parse(dst.read_text(encoding='utf-8'))
print('art_studio.py 已更新（审图 + 标记回队），语法 ok，大小 %d 行'
      % len(dst.read_text(encoding='utf-8').splitlines()))
