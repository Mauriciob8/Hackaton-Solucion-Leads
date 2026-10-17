with open('dapta_widget.js', 'r', encoding='utf-8') as f:
    text = f.read()

import re

matches = [m.start() for m in re.finditer(r'method\s*:\s*[\"\']POST[\"\']', text)]
with open('posts.txt', 'w', encoding='utf-8') as out:
    out.write(f'POST calls count: {len(matches)}\n')
    for pos in matches:
        out.write('--- POST CALL ---\n')
        out.write(text[max(0, pos-200):min(len(text), pos+400)] + '\n')
