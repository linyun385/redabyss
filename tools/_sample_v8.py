import os, subprocess, sys, time
from pathlib import Path
G = Path(r'C:\Users\Administrator\Desktop\杂七杂八\红渊\game')
GEN = G/'tools'/'gen_art_diffusers.py'; OUT = G/'art'/'_samples_v8'; OUT.mkdir(parents=True, exist_ok=True)
VAE = G/'models'/'sdxl-vae-fp16-fix.safetensors'
STYLE = ('antique lithograph print on aged yellowed paper, paper texture and foxing visible, '
         'fine stipple shading, deep ink contours, muted ochre and soot palette, '
         'single vermilion accent, one single subject, single view, no pencil sketch, no text')
# 形态改用"模型认识的实物类比"；光改成"地底上穿"的构图
P = ('three fist-sized leathery egg-pods hanging from a rock ceiling on short cords, '
     'round mouths at their lower ends like the ends of cut hoses, '
     'thick curved claws like fishhooks gripping the rock above them, '
     'a single light source below the frame out of sight, the floor the brightest area, '
     'the lower edges of the pods rimmed with red, their upper parts lost in shadow, '
     'shadows thrown upward onto the ceiling, no sky, no horizon, ' + STYLE)
NEG = ('pencil sketch, graphite, charcoal, flat studio lighting, front light, daylight, softbox, '
       'even illumination, light from above, photograph, landscape, horizon, sky, curtain, cloth, '
       'fabric, drapery, text, letters, labels, diagram, callouts, inset, multiple views, border, frame')
out = OUT/'A5_lit_from_below.png'
cmd=[sys.executable,str(GEN),'--raw','--prompt',P,'--neg',NEG,'--out',str(out),
     '--width','512','--height','752','--steps','24','--seed','706']
if VAE.exists(): cmd += ['--vae', str(VAE)]
t0=time.time(); r=subprocess.run(cmd,cwd=str(G),capture_output=True,text=True,encoding='utf-8',errors='replace')
print('A5', 'ok' if out.exists() else 'FAIL', round(time.time()-t0),'s', flush=True)
if not out.exists(): print((r.stdout or '')[-200:], (r.stderr or '')[-200:])
