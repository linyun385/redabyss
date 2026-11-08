# -*- coding: utf-8 -*-
"""今晚交付清单核对（2026-11-06 · 第三轮任务 3）。
只读。跑法：python -I tools/_delivery_check_1106.py
输出存在性 + 行数到 stdout，由人写成 _DELIVERY_1106.md（人工归类批次）。
"""
import io, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = [
    # (路径, 归属)
    ('docs/design/anmin_minions/00_README.md', '主任务'),
    ('docs/design/anmin_minions/01_audit.md', '主任务'),
    ('docs/design/anmin_minions/02_cards_A_growth.md', '主任务'),
    ('docs/design/anmin_minions/03_cards_B_buffs.md', '主任务'),
    ('docs/design/anmin_minions/04_cards_C_parts.md', '主任务'),
    ('docs/design/anmin_minions/05_curves.md', '主任务'),
    ('docs/design/anmin_minions/06_needs.md', '主任务'),
    ('docs/design/anmin_minions/cards_draft.json', '主任务'),
    ('docs/design/anmin_minions/07_paper_test.md', '第二批4'),
    ('docs/design/enemies/L1_L3_rework.md', '方向1+第二批1'),
    ('docs/design/enemies/L4_L8.md', '方向2+第二批1'),
    ('docs/design/enemies/battle_lines.md', '第二轮R1'),
    ('docs/design/enemies/_roster_full.tmp.md', '第二轮R1(素材)'),
    ('docs/design/events/new_events_20.md', '方向3'),
    ('docs/design/relics/new_relics_24.md', '方向4'),
    ('docs/design/layers/scene_depth1.md', '方向5'),
    ('docs/design/layers/scene_depth2.md', '方向5'),
    ('docs/design/layers/scene_depth3.md', '方向5'),
    ('docs/design/layers/scene_depth4.md', '方向5'),
    ('docs/design/layers/scene_depth5.md', '方向5'),
    ('docs/design/layers/scene_depth6.md', '方向5'),
    ('docs/design/layers/scene_depth7.md', '方向5'),
    ('docs/design/layers/scene_depth8.md', '方向5'),
    ('docs/design/layers/sound_design.md', '第二轮R4'),
    ('docs/design/copy/flavor_audit.md', '方向6'),
    ('docs/design/copy/name_audit.md', '第二轮R2'),
    ('docs/design/copy/_flavor_dump.tmp.md', '方向6(素材)'),
    ('docs/design/glossary_audit.md', '方向7'),
    ('docs/design/endings/ten_endings.md', '方向8'),
    ('docs/design/tutorial/first_3_battles.md', '方向9'),
    ('docs/design/shops/shop_and_recycle.md', '方向10'),
    ('docs/design/classes/opening.md', '方向11'),
    ('docs/design/curves/curve_report_auto.md', '方向12(脚本产出)'),
    ('docs/design/curves/curve_report.md', '方向12(分析)'),
    ('docs/design/curves/_triage.tmp.md', '方向12(素材)'),
    ('docs/design/curves/parts_economy_auto.md', '第二轮R3(脚本产出)'),
    ('docs/design/curves/parts_economy.md', '第二轮R3(分析)'),
    ('docs/design/_CONFLICTS_1106.md', '兜底1'),
    ('docs/design/_TASKDONE_AUDIT_1106.md', '兜底2'),
    ('docs/design/_INDEX_1106.md', '兜底3'),
    ('docs/design/_NEWCOMER_PATH.md', '兜底4'),
    ('docs/design/_STALE_NUMBERS_1106.md', '第二批2'),
    ('docs/design/_CROSSCHECK_1106.md', '第二批3'),
    ('docs/design/_SELFAUDIT_1106.md', '第三轮1'),
    ('docs/design/_DECISIONS_1106.md', '第三轮2'),
    ('tools/_curve_audit_1106.py', '方向12脚本'),
    ('tools/_parts_economy_1106.py', '第二轮R3脚本'),
    ('tools/_taskdone_audit_1106.py', '兜底2脚本'),
    ('tools/_design_index_1106.py', '兜底3脚本'),
]

def main():
    missing = []
    for path, batch in FILES:
        full = os.path.join(ROOT, path)
        if not os.path.exists(full):
            missing.append((path, batch))
            print('MISSING\t%s\t%s' % (batch, path))
            continue
        try:
            n = sum(1 for _ in io.open(full, encoding='utf-8'))
        except Exception:
            n = -1
        print('OK\t%5d\t%s\t%s' % (n, batch, path))
    print('---')
    print('total=%d missing=%d' % (len(FILES), len(missing)))

if __name__ == '__main__':
    main()
