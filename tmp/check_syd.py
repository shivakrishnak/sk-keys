import os

folder = r'C:\ASK\MyWorkspace\sk-keys\dictionary\tier-5-distributed-architecture\SYD-system-design'
files = sorted([f for f in os.listdir(folder) if f.startswith('SYD-') and f.endswith('.md')])

checks = {
    'TL;DR': 'TL;DR',
    'Problem': 'The Problem This Solves',
    'Textbook': 'Textbook Definition',
    '30Sec': 'Understand It in 30 Seconds',
    'FirstPrinciples': 'First Principles',
    'ThoughtExp': 'Thought Experiment',
    'MentalModel': 'Mental Model',
    'GradualDepth': 'Gradual Depth',
    'Mechanism': 'How It Works',
    'CompletePicture': 'Complete Picture',
    'FailureModes': 'Failure Modes',
    'Related': 'Related Keywords',
    'QuickRef': 'Quick Reference',
    'Wisdom': 'Transferable Wisdom',
    'Surprising': 'Surprising Truth',
    'ThinkAbout': 'Think About This'
}

incomplete = []
for fname in files:
    path = os.path.join(folder, fname)
    with open(path, encoding='utf-8') as f:
        content = f.read()
    lines = content.count('\n')
    missing = [k for k, v in checks.items() if v not in content]
    if not missing:
        status = 'COMPLETE'
    elif lines < 50:
        status = 'STUB'
    else:
        status = 'PARTIAL'
    if status != 'COMPLETE':
        incomplete.append(fname)
    print(f'{fname} | Lines:{lines} | {status} | {", ".join(missing)}')

print(f'\n--- SUMMARY ---')
print(f'Total: {len(files)}')
print(f'Incomplete: {len(incomplete)}')
for f in incomplete:
    print(f'  NEEDS WORK: {f}')

