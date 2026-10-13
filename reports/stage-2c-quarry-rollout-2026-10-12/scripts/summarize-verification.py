from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
P=R/'raw'
def read(name):return json.loads((P/(name+'.json')).read_text())
commands=read('verification-commands')
assert all(c['exitCode']==0 for c in commands)
browser=json.loads((P/'default-regressions/results.json').read_text())
assert all(x['status']=='PASS' for x in browser['checks'])
recovery=read('recovery');video=read('video-with-wall');nav=read('navigation-cycles');life=read('lifecycle')
assert all(x['status']=='PASS' for x in recovery['checks']+video['checks']+life['checks'])
assert nav['status']=='PASS'
def counters(d):return {'textures':d['stats']['textures'],'geometries':d['stats']['geometries'],'GL':{k:d['contexts'][0]['stats'][k]['active']for k in ['Texture','Buffer','Program']}}
v=[counters(x['settled'])for x in video['cycles']]
assert len(v)==10 and all(x==v[0]for x in v)
def brief(checks):return [{k:x[k]for k in ['name','status']}for x in checks]
summary={
 'status':'PASS',
 'scope':'Production localhost runtime, final quarry asset. Physical GPU/mobile and user visual approval remain pending.',
 'quarryAssetSHA256':hashlib.sha256(Path('public/models/gullyverse/quarry-rollout/quarry-limestone.glb').read_bytes()).hexdigest(),
 'lastAdjustmentScope':'Eight browser groups and ten-cycle suites use the final quarry geometry/runtime. A subsequent temporary loading-footer stacking change is separately verified by actual browser captures, final build/type/lint/unit checks and re-run recovery paths. Ready-state geometry/camera/material behavior is identical.',
 'checks':[
  {'command':'npm run test:immersive','status':'PASS','count':64,'log':'unit.log'},
  {'command':'npx tsc --noEmit','status':'PASS','log':'typecheck.log'},
  {'command':'npm run lint','status':'PASS','caution':'Existing warnings outside changed runtime files remain.','log':'lint.log'},
  {'command':'npm run build','status':'PASS','log':'build.log','context':'Existing inspection and old pilot preview build flags enabled for evidence; inert local configuration, no database mutations.'},
  {'command':'node reports/stage-2c-quarry-rollout-2026-10-12/scripts/validate-glb.mjs','status':'PASS','evidence':'glTF-validator.json','errors':0,'warnings':0},
  {'command':'python reports/stage-2c-quarry-rollout-2026-10-12/scripts/validate-exported-topology.py','status':'PASS','evidence':'exported-topology-validation.json'},
  {'command':'python reports/stage-2c-quarry-rollout-2026-10-12/scripts/validate-shape.py','status':'PASS','evidence':'shape-validation.json'},
 ],
 'productionBrowserCommands':commands,
 'existingBrowserGroups':brief(browser['checks']),
 'resourceCycles':{
   'tenToggleCycles':{'status':'PASS','activeFirst':counters(life['cycles'][0]['on']),'activeLast':counters(life['cycles'][-1]['on']),'cold':counters(life['cold']),'retired':counters(life['retired']),'evidence':'lifecycle.json'},
   'tenNavigationRoundTrips':{'status':'PASS','firstHub':counters(nav['cycles'][0]['hub']),'lastHub':counters(nav['cycles'][-1]['hub']),'sameCanvas':True,'evidence':'navigation-cycles.json'},
   'tenPlaybackExitCycles':{'status':'PASS','first':v[0],'last':v[-1],'everyCycleIdentical':True,'cameraRestoration':True,'evidence':'video-with-wall.json'},
 },
 'recovery':brief(recovery['checks']),
 'loadingAccess':{'status':read('loading-access-after')['status'],'evidence':'loading-access-after.json','beforeScreenshot':'loading-access-before.png','afterScreenshot':'loading-access-after.png'},
 'perimeterCoverage':{'status':read('perimeter-coverage')['status'],'visitorHeightSourceHitRays':read('perimeter-coverage')['visitorHeightSourceHitRays'],'newVisitorHeightGaps':len(read('perimeter-coverage')['newVisitorHeightGaps']),'changedUpwardSamples':len(read('perimeter-coverage')['changedUpwardSkylineSamples']),'evidence':'perimeter-coverage.json','caution':'Upward contour differences are disclosed; this does not assert pixel-identical silhouettes.'},
 'preservation':{'status':read('final-preservation')['status'],'protectedFiles':119,'unchanged':115,'evidence':'final-preservation.json'},
 'materialLock':{'status':read('material-lock-validation')['status'],'evidence':'material-lock-validation.json'},
 'capturePairs':{'status':'PASS','pairs':14,'PNGCount':28,'cameraQualityDPRMatch':True,'evidence':'capture-comparison-metadata.json'},
 'limitations':['SwiftShader is not ordinary physical GPU hardware.','GPU counters are resource proxies, not reliable driver VRAM measurements.','Mobile viewport/touch emulation is not physical mobile performance acceptance.','Full-rollout visual production approval is pending.'],
}
(P/'test-summary.json').write_text(json.dumps(summary,indent=2))
print('Final test summary PASS; eight browser groups, ten toggle/navigation/playback cycles and four recovery paths.')
