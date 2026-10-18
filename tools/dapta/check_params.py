from pathlib import Path
import re

raiz_proyecto = Path(__file__).resolve().parents[2]
carpeta_herramientas = Path(__file__).resolve().parent

with open(raiz_proyecto / 'dapta_widget.js', 'r', encoding='utf-8') as f:
    text = f.read()

matches = [m.start() for m in re.finditer(r'conversation_params', text)]
with open(carpeta_herramientas / 'conv_params.txt', 'w', encoding='utf-8') as out:
    for pos in matches:
        out.write('--- MATCH ---\n')
        out.write(text[max(0, pos-150):min(len(text), pos+250)] + '\n')
