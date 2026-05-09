import os
import re

d = r'C:\ASK\MyWorkspace\sk-keys\dictionary\tier-5-distributed-architecture\SYD-system-design'
drafts = []
for f in sorted(os.listdir(d)):
    if f.endswith('.md') and f != 'index.md':
        path = os.path.join(d, f)
        with open(path, encoding='utf-8') as fp:
            content = fp.read(600)
        m = re.search(r'status:\s*(\S+)', content)
        status = m.group(1) if m else 'unknown'
        lines = len(open(path, encoding='utf-8').readlines())
        if status == 'draft':
            print(f'{f} | {lines} lines | {status}')

print("Done.")

