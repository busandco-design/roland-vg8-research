#!/usr/bin/env python3
"""Screen IRAM offset sensitivity using locally supplied CP41 assets.

Uses the plain frozen CspExecutor, full byte-swap decoding, zero runtime
memory, static authentic D62 preload arrays and a synthetic control lane.
Does not run the full CP41 admitted path, live host coefficient updates,
ALX9797's harness, or any physical device. All-zero results are inconclusive.
Dependencies are those of the retained CP41 package. Emits JSON lines.
"""
from pathlib import Path
import sys,hashlib,json,types,math,time,importlib.util
sys.stdout.reconfigure(encoding='utf-8')
# This script changes methods only inside this process; source files remain untouched.
sys.dont_write_bytecode=True
import argparse
ap=argparse.ArgumentParser(description='Inconclusive bounded sensitivity screen, not an issue #1 replication or hardware oracle.')
ap.add_argument('--cp41-root',type=Path,required=True)
p=ap.parse_args().cp41_root
r=p/'Library'/'frozen_cp33_executor'
sys.path[:0]=[str(r/'src'),str(r/'scripts'),str(p/'reproduction')]
from analyze_authentic_d62_reachability import make_bundle
from vg8csp.native_pipeline import _new_executor,DecoderMode
from vg8csp.csa_phase_link import CsaPhaseCandidate,SynchronousCsaExecutor
from vg8csp.model import sign_extend
from vg8csp.executor import CspExecutor,DATA_BITS,IRAM_MASK
original_read=CspExecutor.read_iram
original_write=CspExecutor.write_iram
from vg8csp.host_config import HostConfigState
bundle=make_bundle(r,p/'binaries')
import checkpoint27_effect_probe as cp27
print('ACTIVE',str(cp27.ACTIVE),flush=True)
def setup(shift):
 cs=[_new_executor(bundle[i],DecoderMode.FULL) for i in range(2)]
 for c in cs:
  c.host_config=cp27.ACTIVE
  CspExecutor.read_iram=original_read
  CspExecutor.write_iram=original_write
  if shift:
   def rd(self,off): return self.iram[(self.iram_position+(off>>1))&IRAM_MASK]
   def wr(self,off,v): self.iram[(self.iram_position+(off>>1))&IRAM_MASK]=sign_extend(v,DATA_BITS)
   CspExecutor.read_iram=rd;CspExecutor.write_iram=wr
 return cs,SynchronousCsaExecutor(*cs,CsaPhaseCandidate.SYCSP_LOCKSTEP_CSP0_FIRST)
rows=[]
for shift in [0,1]:
 for stimulus in ['silence','sine220','sine330','pluck220']:
  cs,pair=setup(shift); h=hashlib.sha256();sum_sq=[0]*32;peak=[0]*32;nonzero=[0]*32;stable=True
  t=time.perf_counter()
  for n in range(512):
   cs[0].sio_input[:]=[0]*32
   if stimulus!='silence':
    freq=330 if stimulus=='sine330' else 220
    env=math.exp(-n/128) if stimulus=='pluck220' else 1.0
    cs[0].sio_input[22]=int(1_000_000*env*math.sin(2*math.pi*freq*n/32000))
    cs[0].sio_input[18]=int(2_000_000*env)
   a,b=pair.run_sample(n);stable=stable and a.terminated and b.terminated
   for i,v in enumerate(cs[1].sio_output):
    sum_sq[i]+=int(v)**2;peak[i]=max(peak[i],abs(int(v)));nonzero[i]+=int(v!=0);h.update(int(v).to_bytes(8,'little',signed=True))
  row={'shift':shift,'stimulus':stimulus,'frames':512,'stable':stable,'output_sha256_s64le':h.hexdigest(),'slot17_sum_squares':str(sum_sq[17]),'slot17_peak':peak[17],'active_slots':[i for i in range(32) if nonzero[i]],'seconds':round(time.perf_counter()-t,3)}
  rows.append(row); print(json.dumps(row),flush=True)
print('INPUT_HASHES',json.dumps({f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted((p/'binaries').glob('*MAIN_LOAD_PRELOAD*.bin'))}),flush=True)
print('CORE_HASHES',json.dumps({str(f.relative_to(r)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted((r/'src'/'vg8csp').glob('*.py'))}),flush=True)

CspExecutor.read_iram=original_read
CspExecutor.write_iram=original_write

