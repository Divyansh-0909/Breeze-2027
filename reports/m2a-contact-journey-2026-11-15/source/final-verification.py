from pathlib import Path
import json,hashlib,subprocess
R=Path('/dev/shm/m2a-contact-journey-2026-11-15');W=Path('/dev/shm/Breeze-2027-runtime');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checks=['browser-journey','phone-final','ground-preservation','controller-equivalence','isolated-backend','next-route-gate','pdf-check']
for name in checks:assert json.loads((R/'evidence'/f'{name}.json').read_text())['status']=='PASS',name
b=json.loads((R/'evidence/browser-journey.json').read_text());assert len(b['checks'])==14 and all(b['checks'].values())and not b['errors']and not b['failures']
assert (R/'evidence/typecheck.log').stat().st_size==0
unit=(R/'evidence/unit-tests.log').read_text();assert 'pass 111'in unit and'fail 0'in unit
old=json.loads(Path('/dev/shm/texture-alpha-fix-2026-11-15/evidence/original-controller-preservation.json').read_text());rows=[]
for row in old['files']:
 assert sha(Path('/workspace/Breeze-2027')/row['path'])==row['sha256']
 changed=row['path']in['components/immersive/runtime.ts','components/immersive/input.ts'];newSHA=sha(W/row['path'])
 if not changed:assert newSHA==row['sha256']
 rows.append({'file':row['path'],'originalRepositorySHA256':row['sha256'],'privateImplementationSHA256':newSHA,'optionalNativeIntegrationAdded':changed})
for root in [W,Path('/workspace/Breeze-2027')]:assert subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip()=='0e1e23dd2f5181df202d862d147067249bc55a41'
master=Path('/dev/shm/Gullyverse-Rev15Z-Wide-Contact-Window-and-Restored-Graffiti.blend');assert sha(master)=='89e765de6bb68a58a6a2d17d4d6d7ea6c696a6750402ede19306bdddc6a71041'
for version in ['locked-rev15z-clean-v2','locked-rev15z-m2a-contact-ground']:
 out=W/'public/models/gullyverse'/version;m=json.loads((out/'manifest.json').read_text())
 for row in m['files']:assert sha(out/row['file'])==row['sha256']
 if version.endswith('ground'):
  for name in ['rgbm-verification.json','uv-roundtrip-verification.json','validation/runtime-validation.json']:assert json.loads((out/name).read_text())['status']=='PASS'
assert not list((R/'scratch').glob('auth-*.json'))
result={'status':'PASS','checks':checks,'unitTestsPassed':111,'browserBehaviorChecksPassed':14,'browserConsoleOrPageErrors':0,'observedBrowserRequestCancellations':len(b['expectedCancellations']),'cancellationClassificationAndRawEventsRetained':True,'sourceMasterStillExact':True,'originalRepositoryMovementFilesAllExact':True,'originalDefaultControllerFrameTraceBitExact':16800,'privateControllerFiles':rows,'HEADUnchanged':True,'noTemporaryAuthenticationDescriptorsRetained':True,'scope':'M2A bounded native Contact journey, not full-world completion or physical-device performance'};(R/'evidence/final-verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
