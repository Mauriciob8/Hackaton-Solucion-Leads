with open('dapta_widget.js', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('/execute')
with open('execute_func.txt', 'w', encoding='utf-8') as out:
    out.write(text[max(0, pos-600):min(len(text), pos+400)])
