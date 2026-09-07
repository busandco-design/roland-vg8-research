#!/usr/bin/env python3
from pathlib import Path
import re,sys
root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
blocked_ext={'.bin','.rom','.mid','.syx','.exe','.dll','.zip','.rar','.7z','.lzh','.lha','.pdf','.doc','.docx','.jpg','.jpeg','.png'}
blocked_terms=['service_manual','service-notes','service_notes','firmware_dump','rom_dump','private_email','gmail','correspondence']
patterns=[re.compile(r'BEGIN PRIVATE KEY',re.I),re.compile(r'\bpassword\s*[:=]',re.I),re.compile(r'\bapi[_ -]?key\s*[:=]',re.I)]
problems=[]
for p in root.rglob('*'):
    if not p.is_file() or '.git' in p.parts: continue
    if p.name == 'publication_lint.py': continue
    rel=p.relative_to(root); low=str(rel).lower()
    if p.suffix.lower() in blocked_ext: problems.append((rel,'binary/source artifact requires explicit rights review'))
    if any(t in low for t in blocked_terms): problems.append((rel,'filename suggests restricted/private source material'))
    if p.suffix.lower() in {'.md','.txt','.csv','.py','.json','.yml','.yaml'}:
        txt=p.read_text(encoding='utf-8',errors='ignore')
        for pat in patterns:
            if pat.search(txt): problems.append((rel,'sensitive text pattern'))
if problems:
    print('PUBLICATION LINT: FAIL')
    [print(f'- {r}: {w}') for r,w in problems]
    raise SystemExit(1)
print('PUBLICATION LINT: PASS')
print('Reminder: automated lint cannot determine copyright/license permission.')
