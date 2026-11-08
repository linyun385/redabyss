# -*- coding: utf-8 -*-
"""去掉提示词里残留的现实物种名（规则 VIII）。

扫描出来真正需要改的只有「管虫/热泉管虫」（现实里有对应物：巨型管虫 Riftia）。
「鱼钩一样的爪」是隐喻不是物种，保留；「手指」是骨架/手套的部位，保留。

改法：整段重写，不字符串替换（替换会造病句，见交接文档第二节）。
"""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
GAME = Path(__file__).resolve().parents[1]
P = GAME / 'data' / 'zh_prompts_full.json'
MARK = '洞底是一整片深红的光'

NEW = {
    'enemy_d5_01':
        '地底洞窟里，一条没有再分出肢体的长躯体倒挂在岩壁上，上端扎进一条岩缝，下端垂下来。'
        '这条躯体是画面的主体，占满画面中部，体表是暗红色的软皮质，纵向有几道深深的褶皱，'
        '褶皱里渗出黏亮的液；躯体末端散开成一圈细长的丝状触须，触须卷曲、正在向外张开，'
        '一圈触须之间露出一圈细密的孔。岩壁上方是一条细细的黑缝。',
    'enemy_d5_10':
        '地底洞穴中，一条管状的软躯体倒挂在岩壁上，只连着上端一点，整条垂在暗处。'
        '这条躯体是画面的主体，占满画面中部，体表覆着一层厚的角质环纹，环纹上密布细小的裂纹，'
        '裂纹里渗出暗色的液；躯体下侧的一排圆形吸盘鼓起来，吸盘边缘挂着黏液丝，正往下滴。'
        '岩壁只是画面上方一条细细的边。',
    'event_d5_10':
        '绿洲城邦的汤锅架在温泉支流上，锅是厚铸铁的深锅，锅沿豁了几个口。'
        '这个汤锅是画面的主体，占满画面中部，锅体表面覆着一层厚厚的锈迹和水垢，'
        '锅里的汤翻着稠泡，汤面上浮着几段切开的细管状躯体。汤锅下方散落着碎石和啃过的骨头。'
        '锅边的横杆上挂着一块木牌，牌面只有模糊的墨痕。',
}


def main():
    rows = json.loads(P.read_text(encoding='utf-8'))
    bak = P.with_suffix('.bak4.json')
    if not bak.exists():
        bak.write_text(P.read_text(encoding='utf-8'), encoding='utf-8')
    hit = 0
    for r in rows:
        if r['id'] not in NEW:
            continue
        old = r['prompt']
        i = old.find(MARK)
        if i < 0:
            print('!! %s 找不到标记' % r['id'])
            continue
        r['prompt'] = NEW[r['id']] + old[i:]
        hit += 1
        print('%-14s 主体 %d → %d 字' % (r['id'], i, len(NEW[r['id']])))
    P.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding='utf-8')
    print('改 %d 条' % hit)
    return 0


if __name__ == '__main__':
    sys.exit(main())
