# -*- coding: utf-8 -*-
"""统一入口：按顺序重跑 H01-H11 全部模拟。
用法：python tools/sim/run_all.py          # 全部
      python tools/sim/run_all.py 01 04    # 只跑指定编号
结果直接写入各 docs/design/sim_*.md。
"""
import sys, subprocess, time
from pathlib import Path

SCRIPTS = [
 ('01', 'sim_reward.py'), ('02', 'sim_combat.py'), ('03', 'sim_economy.py'),
 ('04', 'sim_build_speed.py'), ('05', 'sim_sensitivity.py'), ('06', 'sim_event_value.py'),
 ('07', 'sim_relic_value.py'), ('08', 'sim_combo_damage.py'), ('09', 'sim_vein_level.py'),
 ('10', 'sim_decision_load.py'), ('11', 'sim_starter_survival.py'), ('14', 'sim_full_run.py'),
]

def main(argv):
    want = set(argv) or {s[0] for s in SCRIPTS}
    here = Path(__file__).resolve().parent
    for num, script in SCRIPTS:
        if num not in want:
            continue
        t0 = time.time()
        print('== run %s ==' % script, flush=True)
        r = subprocess.run([sys.executable, '-I', str(here / script)])
        print('   %.1fs' % (time.time() - t0), flush=True)
        if r.returncode != 0:
            print('!! %s failed' % script)
            sys.exit(1)

if __name__ == '__main__':
    main(sys.argv[1:])
