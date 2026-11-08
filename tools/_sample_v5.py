import os, subprocess, sys, time
from pathlib import Path
G = Path(r'C:\Users\Administrator\Desktop\杂七杂八\红渊\game')
GEN = G/'tools'/'gen_art_diffusers.py'; OUT = G/'art'/'_samples_v5'; OUT.mkdir(parents=True, exist_ok=True)
VAE = G/'models'/'sdxl-vae-fp16-fix.safetensors'

# 风格段 v4：保住纸纹与印刷感；红光提到对象段后面立刻出现
STYLE = ('antique lithograph print on aged yellowed paper, paper texture and foxing visible, '
         'fine stipple shading, deep ink contours, muted ochre and soot palette, '
         'one single vermilion accent, one single subject, single view, no pencil sketch, no text')
NEG = ('pencil sketch, graphite, charcoal, flat poster, vector, silkscreen, cartoon, anime, '
       '3d render, photograph, earth animal, daylight, neutral light, gray background, '
       'text, letters, glyphs, labels, diagram, callouts, inset, multiple views, border, frame')

items = [
 ('A2_inverted_spider', 'a heavy jumping spider clinging upside down to a wet ceiling, '
   'its body hanging below the pipe, eight thick hairy legs hooked into stone, '
   'the floor glows deep red beneath it, red light on the underside of its abdomen, '
   'six small eyes ringed around two large ones, silk line hanging straight down, '
   'feeding organs on the underside, ' + STYLE),
 ('B2_hanging_moss', 'a dense pale moss colony hanging down from a ring-shaped ceiling vent, '
   'feeding mouths clustered on the undersides of its caps, tendrils trailing downward toward the light, '
   'a deep red glow rising from the floor and staining the lower caps crimson, spore dust drifting down, '
   + STYLE),
]
for name, prompt in items:
    out = OUT/(name + '.png')
    cmd = [sys.executable, str(GEN), '--raw','--prompt',prompt,'--neg',NEG,'--out',str(out),
           '--width','512','--height','752','--steps','22','--seed','702']
    if VAE.exists(): cmd += ['--vae', str(VAE)]
    t0=time.time(); r=subprocess.run(cmd,cwd=str(G),capture_output=True,text=True,encoding='utf-8',errors='replace')
    print(name, 'ok' if out.exists() else 'FAIL', round(time.time()-t0), 's', flush=True)
    if not out.exists(): print((r.stdout or '')[-200:], (r.stderr or '')[-200:])
