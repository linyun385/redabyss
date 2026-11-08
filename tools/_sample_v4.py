import os, subprocess, sys, time
from pathlib import Path
G = Path(r'C:\Users\Administrator\Desktop\杂七杂八\红渊\game')
GEN = G/'tools'/'gen_art_diffusers.py'; OUT = G/'art'/'_samples_v4'; OUT.mkdir(parents=True, exist_ok=True)
VAE = G/'models'/'sdxl-vae-fp16-fix.safetensors'
STYLE = ('antique lithograph print, flat blocks of ochre yellow and soot grey, fine stipple shading, '
         'deep ink contours, aged yellowed paper, single vermilion accent, red glow rising from below, '
         'one single subject, single view, no pencil sketch, no text')
NEG = ('pencil sketch, graphite, charcoal, cartoon, anime, 3d render, photograph, earth animal, '
       'text, letters, glyphs, labels, diagram, callouts, inset, multiple views, border, frame')
items = [
 ('A_inverted_spider', 'a heavy jumping spider clinging upside down to a wet ceiling, eight thick hairy legs hooked into stone, six small eyes ringed around two large ones, abdomen marked with a pale skull-like mottle, silk line hanging straight down, feeding organs on the underside, lit from below by a deep red glow, ' + STYLE),
 ('B_hanging_moss', 'a dense pale moss colony hanging down from a ceiling pipe, feeding mouths clustered on its underside, tendrils trailing downward toward the light, spore dust drifting down, lit from below by a deep red glow, ' + STYLE),
]
for name, prompt in items:
    out = OUT/(name + '.png')
    cmd = [sys.executable, str(GEN), '--raw','--prompt',prompt,'--neg',NEG,'--out',str(out),
           '--width','512','--height','752','--steps','20','--seed','701']
    if VAE.exists(): cmd += ['--vae', str(VAE)]
    t0=time.time(); r=subprocess.run(cmd,cwd=str(G),capture_output=True,text=True,encoding='utf-8',errors='replace')
    print(name, 'ok' if out.exists() else 'FAIL', round(time.time()-t0), 's', flush=True)
