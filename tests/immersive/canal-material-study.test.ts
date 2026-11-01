import test from 'node:test';
import assert from 'node:assert/strict';
import {CanalMaterialSession,canalMaterial,CANAL_CHART_PERIOD_UV,CANAL_TILE_PERIOD_M} from '../../components/immersive/canalMaterialStudy';
import {CaveEntranceSession} from '../../components/immersive/CaveEntranceSession';
import {ImmersiveRuntime} from '../../components/immersive/runtime';
import {naturalCaveReview,carryCaveReview} from '../../components/immersive/caveReview';

test('canal study requires private gate and carries material comparison without changing quarry sampling',()=>{
  assert.equal(naturalCaveReview('?entranceReview=canal-material',false),false);
  assert.equal(naturalCaveReview('?entranceReview=reference-rock',true),false);
  assert.equal(naturalCaveReview('?entranceReview=canal-material',true),true);
  const u=new URL(carryCaveReview('/aftermovie','?entranceReview=canal-material&caveMaterial=cracked_concrete_wall&caveFeatureScale=2',true),'https://test.invalid');
  assert.equal(u.searchParams.get('quarryReview'),'geology-fidelity');
  assert.equal(u.searchParams.get('caveFeatureScale'),'2');
  assert.equal(u.searchParams.get('caveMaterial'),'cracked_concrete_wall');
  const guarded=new URL(carryCaveReview('/aftermovie','?entranceReview=canal-material&caveGeometry=pilot',true),'https://test.invalid');
  assert.equal(guarded.searchParams.has('caveGeometry'),false);
  assert.equal(canalMaterial('../../private'),'control');
});

test('canal selected material owns only three images; failed and superseded loads drain every unpublished image',async()=>{
  const oldFetch=globalThis.fetch,oldBitmap=globalThis.createImageBitmap,oldLoad=CaveEntranceSession.prototype.load;
  let closes=0,made=0,fail=false;
  globalThis.fetch=async input=>({ok:!fail||!String(input).endsWith('/orm.png'),status:fail?503:200,blob:async()=>new Blob(['test'])} as Response);
  globalThis.createImageBitmap=async()=>{made++;return {width:2048,height:2048,close(){closes++;}} as ImageBitmap;};
  CaveEntranceSession.prototype.load=async()=>{};
  try{
    const owner=new CanalMaterialSession(new ImmersiveRuntime('hub',()=>{},false,()=>0),'cracked_concrete_wall');
    await owner.load();const a=owner.studyDiagnostics();assert.equal(a.active,'cracked_concrete_wall');assert.equal(a.studySourceImages,3);assert.equal(a.quarrySamplerScale,3);
    const ids=a.maps!.map(t=>t.uuid);owner.setStudySelection('cracked_concrete_wall',2);
    const b=owner.studyDiagnostics();assert.deepEqual(b.maps!.map(t=>t.uuid),ids);
    b.maps!.forEach((t,i)=>assert.deepEqual(t.repeat,a.maps![i].repeat.map(v=>v/2)));
    assert.equal(b.maps![0].colorSpace,'srgb');assert.equal(b.maps![1].colorSpace,'');
    owner.dispose();assert.equal(closes,made);
    fail=true;const failed=new CanalMaterialSession(new ImmersiveRuntime('hub',()=>{},false,()=>0),'concrete_wall_006');
    await failed.load();assert.ok(failed.studyDiagnostics().error);assert.equal(failed.studyDiagnostics().active,null);failed.dispose();assert.equal(closes,made);
    fail=false;const late=new CanalMaterialSession(new ImmersiveRuntime('hub',()=>{},false,()=>0),'worn_plaster_wall');
    const pending=late.load();late.dispose();await pending;assert.equal(late.studyDiagnostics().active,null);assert.equal(closes,made);
  }finally{globalThis.fetch=oldFetch;globalThis.createImageBitmap=oldBitmap;CaveEntranceSession.prototype.load=oldLoad;}
});

test('canal sampler preserves the existing projection-island phase at both feature sizes',()=>{
  const spec=JSON.parse(require('node:fs').readFileSync('assets-source/gullyverse/recovered-c8-material/material-manifest.json','utf8'));
  assert.ok(Math.abs(CANAL_CHART_PERIOD_UV-8/spec.approvedUVRepeat)<1e-9);
  for(const scale of [1,2])assert.ok(Math.abs((2/CANAL_TILE_PERIOD_M/scale)*CANAL_CHART_PERIOD_UV-128/scale)<1e-9);
});
