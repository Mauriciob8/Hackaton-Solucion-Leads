with open('dapta_widget.js', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'conversation_params', text)]
with open('conv_params.txt', 'w', encoding='utf-8') as out:
    for pos in matches:
        out.write('--- MATCH ---\n')
        out.write(text[max(0, pos-150):min(len(text), pos+250)] + '\n')
