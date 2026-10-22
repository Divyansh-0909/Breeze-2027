import test from 'node:test';
import assert from 'node:assert/strict';
import {CaveMaterialStudySession,caveStudyMaterial} from '../../components/immersive/caveMaterialStudy';
import {CaveEntranceSession} from '../../components/immersive/CaveEntranceSession';
import {ImmersiveRuntime} from '../../components/immersive/runtime';
import {naturalCaveReview,carryCaveReview} from '../../components/immersive/caveReview';

test('study requires private gate and carries material comparison without changing quarry sampling',()=>{
  assert.equal(naturalCaveReview('?entranceReview=material-study',false),false);
  assert.equal(naturalCaveReview('?entranceReview=reference-rock',true),false);
  assert.equal(naturalCaveReview('?entranceReview=material-study',true),true);
  const u=new URL(carryCaveReview('/aftermovie','?entranceReview=material-study&caveMaterial=rock_01&caveFeatureScale=2',true),'https://test.invalid');
  assert.equal(u.searchParams.get('quarryReview'),'geology-fidelity');
  assert.equal(u.searchParams.get('caveFeatureScale'),'2');
  assert.equal(u.searchParams.get('caveMaterial'),'rock_01');
  assert.equal(caveStudyMaterial('../../private'),'control');
});

test('selected material owns only three images; failed and superseded loads drain every unpublished image',async()=>{
  const oldFetch=globalThis.fetch,oldBitmap=globalThis.createImageBitmap,oldLoad=CaveEntranceSession.prototype.load;
  let closes=0,made=0,fail=false;
  globalThis.fetch=async input=>({ok:!fail||!String(input).endsWith('/orm.png'),status:fail?503:200,blob:async()=>new Blob(['test'])} as Response);
  globalThis.createImageBitmap=async()=>{made++;return {width:4096,height:4096,close(){closes++;}} as ImageBitmap;};
  CaveEntranceSession.prototype.load=async()=>{};
  try{
    const owner=new CaveMaterialStudySession(new ImmersiveRuntime('hub',()=>{},false,()=>0),'rock_01');
    await owner.load();const a=owner.studyDiagnostics();assert.equal(a.active,'rock_01');assert.equal(a.studySourceImages,3);assert.equal(a.quarrySamplerScale,3);
    const ids=a.maps!.map(t=>t.uuid);owner.setStudySelection('rock_01',2);
    const b=owner.studyDiagnostics();assert.deepEqual(b.maps!.map(t=>t.uuid),ids);
    b.maps!.forEach((t,i)=>assert.deepEqual(t.repeat,a.maps![i].repeat.map(v=>v/2)));
    assert.equal(b.maps![0].colorSpace,'srgb');assert.equal(b.maps![1].colorSpace,'');
    owner.dispose();assert.equal(closes,made);
    fail=true;const failed=new CaveMaterialStudySession(new ImmersiveRuntime('hub',()=>{},false,()=>0),'rock_2');
    await failed.load();assert.ok(failed.studyDiagnostics().error);assert.equal(failed.studyDiagnostics().active,null);failed.dispose();assert.equal(closes,made);
    fail=false;const late=new CaveMaterialStudySession(new ImmersiveRuntime('hub',()=>{},false,()=>0),'rock_3');
    const pending=late.load();late.dispose();await pending;assert.equal(late.studyDiagnostics().active,null);assert.equal(closes,made);
  }finally{globalThis.fetch=oldFetch;globalThis.createImageBitmap=oldBitmap;CaveEntranceSession.prototype.load=oldLoad;}
});
