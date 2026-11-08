import os, subprocess, sys, time
from pathlib import Path
G = Path(r'C:\Users\Administrator\Desktop\杂七杂八\红渊\game')
GEN = G/'tools'/'gen_art_diffusers.py'; OUT = G/'art'/'_samples_v6'; OUT.mkdir(parents=True, exist_ok=True)
VAE = G/'models'/'sdxl-vae-fp16-fix.safetensors'

STYLE = ('antique lithograph plate on aged yellowed paper, visible paper grain and foxing, fine stipple shading, '
         'deep ink contours, muted ochre and soot palette, single vermilion accent, '
         'the stone ceiling fills the whole background, one single subject, single view, '
         'no pencil sketch, no text')
NEG = ('pencil sketch, graphite, charcoal, flat poster, vector, silkscreen, cartoon, anime, 3d render, '
       'photograph, landscape, horizon, sky, building, room interior, table, pot, vase, mushroom, '
       'daylight, neutral light, gray background, text, letters, labels, diagram, callouts, '
       'inset, multiple views, border, frame')

items = [
 ('A3_inverted_spider', 'a heavy jumping spider clinging upside down beneath a rough stone ceiling, '
   'its body hanging below the rock, eight thick hairy legs hooked into the stone, '
   'a deep red glow rising from below and staining the underside of its abdomen, '
   'six small eyes ringed around two large ones, a single silk thread hanging straight down, ' + STYLE),
 ('B3_hanging_moss', 'a pale moss colony growing downward from a rough stone ceiling, '
   'each cap opening toward the floor, fine tendrils trailing down toward the red light, '
   'spore dust drifting downward, the stone surface filling the entire background, ' + STYLE),
]
for name, prompt in items:
    out = OUT/(name + '.png')
    cmd = [sys.executable, str(GEN), '--raw','--prompt',prompt,'--neg',NEG,'--out',str(out),
           '--width','512','--height','752','--steps','24','--seed','703']
    if VAE.exists(): cmd += ['--vae', str(VAE)]
    t0=time.time(); r=subprocess.run(cmd,cwd=str(G),capture_output=True,text=True,encoding='utf-8',errors='replace')
    print(name, 'ok' if out.exists() else 'FAIL', round(time.time()-t0), 's', flush=True)
