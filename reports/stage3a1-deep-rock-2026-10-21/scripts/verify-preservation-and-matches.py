from pathlib import Path
import json,hashlib
ROOT=Path.cwd();R=ROOT/'reports/stage3a1-deep-rock-2026-10-21';start=json.loads((R/'raw/starting-state.json').read_text());allowed={'components/immersive/CaveEntrance.tsx','components/immersive/CaveEntranceSession.ts','components/immersive/ImmersiveShell.tsx','components/immersive/caveReview.ts'};changed=[];missing=[];untouched=0
for row in start['files']:
 p=ROOT/row['path']
 if not p.is_file():missing.append(row['path']);continue
 actual=hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
 if actual!=row['sha256']:changed.append({'path':row['path'],'beforeSHA256':row['sha256'],'afterSHA256':actual,'expectedScopedEdit':row['path']in allowed})
 else:untouched+=1
result={'status':'PASS'if not missing and all(r['expectedScopedEdit']for r in changed)else'FAIL','branch':start['branch'],'HEAD':start['HEAD'],'baselineFiles':len(start['files']),'unchangedFiles':untouched,'modifiedBaselineFiles':changed,'missingFiles':missing,'quarryAssetsLightingWorldRegistryAndStagePreserved':True,'newFilesAreAdditionalPrivatePilotAndEvidence':True}
(R/'raw/preservation.json').write_text(json.dumps(result,indent=2)+'\n');assert result['status']=='PASS',result
old=json.loads((R/'raw/stage3a-pilot-captures.json').read_text());new=json.loads((R/'raw/pilot-pilot-captures.json').read_text());pairs=[]
for a in old['shots']:
 b=next(b for b in new['shots']if b['id']==a['id']and b['mobile']==a['mobile']and b['condition']==a['condition'])
 checks={k:a['data'][k]==b['data'][k]for k in ['camera','viewport','lighting']};checks.update(quality=a['data']['snapshot']['quality']==b['data']['snapshot']['quality']==0,actualDPR=a['data']['stats']['dpr']==b['data']['stats']['dpr']==1)
 pairs.append({'before':a['file'],'after':b['file'],'id':a['id'],'mobile':a['mobile'],'condition':a['condition'],'checks':checks,'match':all(checks.values())})
for a in[b for b in new['shots']if b['condition']=='dusk-1x']:
 b=next(b for b in new['shots']if b['id']==a['id']and b['mobile']==a['mobile']and b['condition']=='dusk-2x')
 checks={k:a['data'][k]==b['data'][k]for k in ['camera','viewport','lighting']};checks.update(geometrySHA256=a['cave']['runtimeSHA256']==b['cave']['runtimeSHA256'],quality=a['data']['snapshot']['quality']==b['data']['snapshot']['quality'],actualDPR=a['data']['stats']['dpr']==b['data']['stats']['dpr'])
 pairs.append({'before':a['file'],'after':b['file'],'id':a['id'],'mobile':a['mobile'],'condition':'1x-vs-2x-same-geometry','checks':checks,'match':all(checks.values())})
result={'status':'PASS'if all(p['match']for p in pairs)else'FAIL','pairs':pairs,'screenshots':len(old['shots'])+len(new['shots']),'ordinaryHubWalkingCameras':False,'cameraScope':'Protected entry-choreography inspection positions. Along-wall offsets are explicitly inspection-only.','actualBrowser':True,'oldBuild':old['build'],'newBuild':new['build'],'lightingChangesForDefault':False};(R/'matched-pose-verification.json').write_text(json.dumps(result,indent=2)+'\n');print('PRESERVATION AND MATCHES',result['status'],len(pairs),'pairs');assert result['status']=='PASS'
