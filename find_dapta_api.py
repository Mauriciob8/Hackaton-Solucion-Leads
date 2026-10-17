with open('dapta_widget.js', 'r', encoding='utf-8') as f:
    text = f.read()

import re

# Find initDaptaEmbeddedWidget definition
idx = text.find('initDaptaEmbeddedWidget')
if idx != -1:
    print('initDaptaEmbeddedWidget:')
    print(text[idx-50:idx+600])

# Find how messages are sent / conversations created
idx2 = text.find('/api/v2/agents/')
if idx2 != -1:
    print('\nAgent API calls:')
    print(text[idx2-50:idx2+600])

# Find chat send / conversation endpoints
idx3 = text.find('text-agent-v2')
while idx3 != -1:
    print('\ntext-agent-v2 match:')
    print(text[max(0, idx3-50):min(len(text), idx3+300)])
    idx3 = text.find('text-agent-v2', idx3 + 1)
