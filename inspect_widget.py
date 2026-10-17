import re

with open('dapta_widget.js', 'r', encoding='utf-8') as f:
    text = f.read()

urls = sorted(set(re.findall(r'https?://[a-zA-Z0-9\.\-_/]+', text)))
for u in urls:
    print('URL:', u)

# Let's search for fetch or endpoints
fetch_matches = [m.start() for m in re.finditer(r'fetch\(', text)]
print(f'fetch calls count: {len(fetch_matches)}')
for pos in fetch_matches[:10]:
    print('--- FETCH ---')
    print(text[max(0, pos-50):min(len(text), pos+250)].replace('\n', ' '))
