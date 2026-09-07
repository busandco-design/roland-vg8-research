#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,sys
root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
m=json.loads((root/'MANIFEST_SHA256.json').read_text())
bad=[]
for r in m['files']:
    p=root/r['path']
    if not p.exists(): bad.append((r['path'],'missing')); continue
    h=hashlib.sha256(p.read_bytes()).hexdigest()
    if h!=r['sha256']: bad.append((r['path'],'hash mismatch'))
if bad:
    print('MANIFEST VERIFY: FAIL'); [print(*x) for x in bad]; raise SystemExit(1)
print(f"MANIFEST VERIFY: PASS ({len(m['files'])} files)")
