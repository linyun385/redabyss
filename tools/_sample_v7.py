import os, subprocess, sys, time
from pathlib import Path
G = Path(r'C:\Users\Administrator\Desktop\杂七杂八\红渊\game')
GEN = G/'tools'/'gen_art_diffusers.py'; OUT = G/'art'/'_samples_v7'; OUT.mkdir(parents=True, exist_ok=True)
VAE = G/'models'/'sdxl-vae-fp16-fix.safetensors'

STYLE = ('antique lithograph print on aged yellowed paper, paper texture and foxing visible, '
         'fine stipple shading, deep ink contours, muted ochre and soot palette, '
         'single vermilion accent, one single subject, single view, no pencil sketch, no text')

# A4：跳蛛改写 —— 去掉"八条毛腿两只大眼"这种可对照地球物种的解剖
A = ('a hanging body of pale leathery sacs suspended from a rough rock ceiling, '
     'hooks of hardened chitin gripping the stone, three of the sacs opening downward '
     'with rings of soft lips on their undersides, a deep red glow rising from the floor '
     'and staining the lower sacs crimson, an iron bracket bolted to the wall behind, '
     'no sky, no horizon, the dark cavern interior fills the whole frame, ' + STYLE)

# B4：复现 08 的语言，但换一个对象（悬吊囊群 + 器物），验证这套语言是否稳定
B = ('a cluster of pale sack-like bodies hanging down from a ring-shaped ceiling vent, '
     'each sack parting at the bottom into soft lips, fine threads trailing downward toward the light, '
     'a deep red glow rising from the floor and staining the lower bodies crimson, '
     'dust drifting down, a rusted iron canister standing beneath them, '
     'no sky, no horizon, dark cavern interior fills the frame, ' + STYLE)

NEG = ('pencil sketch, graphite, charcoal, flat poster, vector, silkscreen, cartoon, anime, 3d render, '
       'photograph, landscape, horizon, sky, building, room interior, table, daylight, neutral light, '
       'gray background, spider, insect legs, eight legs, two big eyes, text, letters, labels, '
       'diagram, callouts, inset, multiple views, border, frame')

for name, prompt, seed in [('A4_sacs_spider', A, 704), ('B4_hanging_sacks', B, 705)]:
    out = OUT/(name + '.png')
    cmd = [sys.executable, str(GEN), '--raw','--prompt',prompt,'--neg',NEG,'--out',str(out),
           '--width','512','--height','752','--steps','24','--seed',str(seed)]
    if VAE.exists(): cmd += ['--vae', str(VAE)]
    t0=time.time(); r=subprocess.run(cmd,cwd=str(G),capture_output=True,text=True,encoding='utf-8',errors='replace')
    print(name, 'ok' if out.exists() else 'FAIL', round(time.time()-t0), 's', flush=True)
    if not out.exists(): print((r.stdout or '')[-200:], (r.stderr or '')[-200:])
