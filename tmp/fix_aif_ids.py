import re, pathlib

folder = pathlib.Path('dictionary/tier-8-artificial-intelligence/AIF-ai-foundations')
targets = ['AIF-050','AIF-051','AIF-052','AIF-053','AIF-054','AIF-055','AIF-056','AIF-057','AIF-058']

for p in targets:
    files = list(folder.glob(p + ' - *.md'))
    if not files:
        print('NOT FOUND: ' + p)
        continue
    f = files[0]
    txt = f.read_text(encoding='utf-8-sig')
    m = re.search(r'^id: (AIF-\d+)', txt, re.MULTILINE)
    if m and m.group(1) != p:
        old = m.group(1)
        fixed = txt.replace('id: ' + old, 'id: ' + p)
        f.write_text(fixed, encoding='utf-8')
        print('Fixed ' + f.name + ': ' + old + ' -> ' + p)
    else:
        print('OK ' + p)
