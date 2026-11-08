import re
from pathlib import Path
p = Path('tools/check_prompts.js'); s = p.read_text(encoding='utf-8')
s = s.replace("'copper wire|chains threaded|ring of \\\\w+ eyes|six small eyes|ringed around',",
              "'copper wire|chains threaded|ring of \\\\w+ eyes|six small eyes|ringed around',\n  'glass gauge|heart-like|nails driven|tapped into|wired into',")
s = s.replace("'scratched|carved|cut into|nailed|bolted|laminated|moss|spore|tally|gauge|faceplate'",
              "'scratched|carved|cut into|nailed|bolted|laminated|moss|spore|tally|gauge|faceplate',\n  'wax|still water|layer of water|condensation|metal plate|seam|dust|crack'")
s = s.replace("'rubble|mark|scratch|tally|cloth|suit|faceplate|corridor|gear|fork|hook|tube|coil|stub'",
              "'rubble|mark|scratch|tally|cloth|suit|faceplate|corridor|gear|fork|hook|tube|coil|stub',\n  'metal|plate|dust|edge|groove|iris|draft|condensation|wax|markings'")
p.write_text(s, encoding='utf-8')
print('checker 词表已扩')
