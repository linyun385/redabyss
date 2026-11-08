# -*- coding: utf-8 -*-
"""给 art_studio.py 的「标记不合格」加一个页面内的文字框（不再是 prompt 弹窗）。"""
from pathlib import Path

G = Path(__file__).resolve().parents[1]
P = G / 'tools' / 'art_studio.py'
s = P.read_text(encoding='utf-8')

# 1) 面板里加一个 textarea（放在 prompt 文本框之前）
old_label = "'<label>提示词 prompt</label><textarea id=\"p\" rows=\"4\">'+esc(CUR.prompt)+'</textarea>'+"
new_label = ("'<label>不合格原因（标记时写，方便以后看为什么重做）</label>"
             "<textarea id=\"note\" rows=\"2\" placeholder=\"例：不像怪物 / 太抽象 / 和卡名无关 / 构图太空\">'"
             "+esc((CUR.rework&&CUR.rework.note)||'')+'</textarea>'+"
             "'<label>提示词 prompt</label><textarea id=\"p\" rows=\"4\">'+esc(CUR.prompt)+'</textarea>'+")
assert old_label in s, '找不到 prompt 标签锚点'
s = s.replace(old_label, new_label, 1)

# 2) 标记逻辑：用文字框内容
old_mark = """    let url='/api/mark', payload={id:id,note:''};
    if(CUR.rework){url='/api/unmark';payload={id:id};}
    else{payload.note=prompt('为什么不合格？（一句话，可留空）','')||'';}"""
new_mark = """    const note=($('#note')&&$('#note').value||'').trim();
    let url='/api/mark', payload={id:id,note:note};
    if(CUR.rework){url='/api/unmark';payload={id:id};}"""
assert old_mark in s, '找不到标记逻辑锚点'
s = s.replace(old_mark, new_mark, 1)

# 3) 已标记时按钮文案带上「更新原因」
s = s.replace("(CUR.rework?'取消标记':'标记不合格（进重生成队列）')",
              "(CUR.rework?'取消标记':'标记不合格（进重生成队列）')", 1)

P.write_text(s, encoding='utf-8')
import ast
ast.parse(s)
print('已加：不合格原因文字框（页面内 textarea），语法 ok')
