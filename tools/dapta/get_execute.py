from pathlib import Path

raiz_proyecto = Path(__file__).resolve().parents[2]
carpeta_herramientas = Path(__file__).resolve().parent

with open(raiz_proyecto / 'dapta_widget.js', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('/execute')
with open(carpeta_herramientas / 'execute_func.txt', 'w', encoding='utf-8') as out:
    out.write(text[max(0, pos-600):min(len(text), pos+400)])
