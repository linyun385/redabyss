# -*- coding: utf-8 -*-
"""T72 附带修复：tools/_t56_wire.js 的引擎锚点改为 CRLF/LF 兼容（regex）。
用户侧脚本以文本模式写盘后 index.html 变成 CRLF，LF 精确锚点失配。"""
import io

p = 'tools/_t56_wire.js'
s = io.open(p, encoding='utf-8').read()

old = "const anchor = '<script>\\n/* 《红渊：下潜》战斗引擎核心';"
new = "const anchorRe = /<script>\\r?\\n\\/\\* 《红渊：下潜》战斗引擎核心/;   // CRLF/LF 兼容"
if 'anchorRe' in s:
    print('已应用，跳过')
elif old not in s:
    print('锚点行找不到——dump 前后文：')
    i = s.index('const anchor')
    print(repr(s[i - 40:i + 120]))
    sys.exit(1)
else:
    s = s.replace(old, new)
    o2 = "const ai = html.indexOf(anchor);"
    assert o2 in s, 'o2'
    s = s.replace(o2, "const am = html.match(anchorRe);")
    o3 = "if (ai < 0) { console.error('锚点缺失：引擎 <script> 头'); process.exit(1); }"
    n3 = "if (!am) { console.error('锚点缺失：引擎 <script> 头'); process.exit(1); }\nconst ai = am.index;"
    assert o3 in s, 'o3'
    s = s.replace(o3, n3)
    io.open(p, 'w', encoding='utf-8').write(s)
    print('wire anchor CRLF-tolerant')
