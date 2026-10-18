from pathlib import Path
import re
import sys

raiz_proyecto = Path(__file__).resolve().parents[2]
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

with open(raiz_proyecto / 'dapta_widget.js', 'r', encoding='utf-8') as f:
    text = f.read()

# Find POST requests or message sending functions
matches = [m.start() for m in re.finditer(r'method\s*:\s*[\"\']POST[\"\']', text)]
print(f'POST calls count: {len(matches)}')
for pos in matches:
    print('--- POST CALL ---')
    print(text[max(0, pos-100):min(len(text), pos+300)].replace('\n', ' '))
