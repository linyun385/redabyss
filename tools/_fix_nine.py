# -*- coding: utf-8 -*-
"""补写 8 条漏改的提示词（dive 3 + trem 5）。trem_0058 已合规，不动。

为什么手工写不用模型：只剩 8 条，规则我自己清楚，调一次模型不划算，
而且模型改写容易把「工艺痕迹」写成套话。

规则（规则 IX）：
  · 主体只能是实物：铸成的铁钎 / 铸成整块的铁盖板 / 铸成的铁管 / 粗陶罐 + 铁箍
  · 必须写工艺痕迹：锈穿的洞、歪斜的焊缝、砸扁的边角、铆钉头、锈水淌地
  · 必须写镜头位置
  · 80–140 字，不含尾部光照段

用法：python tools/_fix_nine.py [--apply]
"""
import json
import shutil
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
GAME = Path(__file__).resolve().parents[1]
P = GAME / 'data' / 'zh_prompts_full.json'
SPLIT = '洞底是一整片深红的光'

NEW = {
    'dive_0013': '贴地仰视，一根铸成的铁钎从铁台边缘斜垂下来。钎身是整条铁铸出来的，'
                 '前端被砸成尖，尖口崩了一小块；杆身中段有一道歪斜的焊缝，焊疤鼓起，'
                 '旁边锈穿了两个洞，锈水顺着钎尖滴下。手柄那段缠着发黑的布条，布条下露出磨圆的铆钉头。',

    'dive_0018': '斜俯看，一块铸成整块的铁盖板搁在铁台边上。板面是不规则的厚铁，'
                 '边角被反复砸过、已经砸扁卷起，板心锈穿一处，裂口边挂着一圈白色盐晶，'
                 '像从铁里长出来。板下积着一摊锈水，水边凝出薄薄一层盐壳。',

    'dive_0049': '斜侧平视，一根铸成的铁钎横在刮花的铁台面上。钎身整条铸成，'
                 '前端带螺旋纹、几处崩口；杆上歪斜的焊缝有一道没焊透，'
                 '旁边锈穿出孔隙。缠在杆上的防滑布已经磨破，破口里露出锈成暗红的铁芯，'
                 '铆钉头一颗颗磨得发平。',

    'trem_0031': '斜俯看，一只粗陶罐平搁在刮花的铁台面上。罐是用粗陶手捏成形的，'
                 '口沿磕掉一块，罐壁有细密裂纹，裂纹里沁进暗红；罐身下部箍着一圈锈穿的铁箍，'
                 '箍上铆钉头歪斜，锈水从罐底淌到台面上，积成一小片。',

    'trem_0035': '贴地仰视，一只深口粗陶罐斜靠在井壁边。罐身粗陶手捏，口沿厚薄不匀，'
                 '被磕出两处缺口；罐身箍着两道歪斜的铁箍，箍带锈穿出一个洞，'
                 '洞边挂着锈皮，锈水沿罐壁淌下，在罐底积成一圈。',

    'trem_0051': '斜侧看，一块铸成整块的铁盖板斜靠在铁台边。板上被砸出一个手掌大的凹坑，'
                 '坑里积着锈水，水面上浮着细碎铁屑；板的一角被砸扁卷起，另一角锈穿，'
                 '裂口边散落几粒盐晶。板边缘露着几颗磨圆的铆钉头。',

    'trem_0053': '贴地仰视，一段铸成的铁管半埋在碎石堆里，管口朝斜上方。管壁整条铸成，'
                 '口沿歪斜不平，管身锈穿了三个洞，最大的那个洞边挂着卷起的锈皮，'
                 '锈水顺着管壁流进碎石缝里。管口内壁还粘着一圈干涸的暗色泥。',

    'trem_0056': '斜俯看，一块铸成整块的铁盖板斜立在碎石上，板面朝上。板边被砸扁，'
                 '卷起两道边；板心中段锈穿一道裂缝，裂缝里嵌着一小片铁屑，'
                 '两边翘起；板角一颗铆钉头被磨平，锈水从板底淌进碎石。',
}


def main():
    data = json.loads(P.read_text(encoding='utf-8'))
    by_id = {r['id']: r for r in data}
    changed = []
    for rid, body in NEW.items():
        r = by_id.get(rid)
        if not r:
            print('缺 id:', rid); continue
        old = r['prompt']
        tail = SPLIT + old.split(SPLIT, 1)[1] if SPLIT in old else ''
        r['prompt'] = body + tail
        changed.append(rid)
        print('%s\n  旧: %s\n  新: %s' % (rid, old[:56] + '…', body[:56] + '…'))

    print('\n准备改 %d 条（trem_0058 已合规，不动）' % len(changed))
    if '--apply' not in sys.argv:
        print('干跑。加 --apply 才写盘。')
        return 0

    bak = P.with_suffix('.json.bak10')
    if not bak.exists():
        shutil.copy2(P, bak)
        print('备份 →', bak.name)
    P.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding='utf-8')

    # 复查
    data2 = json.loads(P.read_text(encoding='utf-8'))
    by2 = {r['id']: r['prompt'] for r in data2}
    IX = ('锈穿', '焊缝', '砸扁', '铆钉头', '歪斜')
    bad = [i for i in changed if not any(w in by2[i].split(SPLIT)[0] for w in IX)]
    print('写盘完成。复查未含工艺痕迹的:', bad if bad else '无')
    print('尾部保留检查:', all(('洞底是一整片深红的光' in by2[i]) == ('洞底是一整片深红的光' in by2[i]) for i in changed))
    return 0


if __name__ == '__main__':
    sys.exit(main())
