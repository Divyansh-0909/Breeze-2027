import{launch,context,ready,details,root}from'./wall-browser-common.mjs';
import{writeFile}from'node:fs/promises';import assert from'node:assert/strict';
const browser=await launch(),runs=[],errors=[];
try{
 for(const look of ['rock','limestone']){
  const c=await context(browser,{deviceScaleFactor:.25}),p=await c.newPage(),requests=[];
  p.on('pageerror',e=>errors.push(e.message));const cdp=await c.newCDPSession(p),responses=new Map();
  await cdp.send('Network.enable');await cdp.send('Network.setCacheDisabled',{cacheDisabled:true});
  cdp.on('Network.responseReceived',e=>responses.set(e.requestId,{url:e.response.url,status:e.response.status,fromDiskCache:e.response.fromDiskCache??false}));
  cdp.on('Network.loadingFinished',e=>{const response=responses.get(e.requestId);if(response)requests.push({...response,encodedBytes:e.encodedDataLength});});
  const started=Date.now();await p.goto('http://127.0.0.1:3000/?arrival=hub&diagnostics&quarryReview=excavation'+(look==='limestone'?'&quarryMaterial=limestone':''));
  await p.waitForFunction(()=>window.__gullyverse?.runtime);await p.evaluate(()=>window.__gullyverse.runtime.setQuality(3));await ready(p);
  const preparationMs=Date.now()-started;
  const material=await p.evaluate(()=>{
   const s=window.__wallPreview,materials=new Set();
   s.asset.scene.traverse(o=>{if(o.isMesh)for(const m of Array.isArray(o.material)?o.material:[o.material])materials.add(m);});
   return{look:s.look,style:s.style,materials:[...materials].map(m=>({name:m.name,metalness:m.metalness,roughnessFactor:m.roughness,normalScale:m.normalScale?.toArray(),side:m.side,
    maps:['map','normalMap','roughnessMap','aoMap'].map(k=>({slot:k,name:m[k]?.name,dimensions:[m[k]?.image?.width,m[k]?.image?.height],colorSpace:m[k]?.colorSpace}))})),trace:s.trace};
  });
  assert.equal(material.look,look);assert.equal(material.style,'detailed');assert.equal(material.materials.length,1);
  assert.equal(material.materials[0].name,look==='rock'?'Quarry_Pilot_Original_Stone_PBR':'Quarry_Pilot_Grey_Limestone_PBR');
  const assetRequests=requests.filter(r=>r.url.endsWith('.glb'));
  assert.equal(assetRequests.filter(r=>r.url.includes('/rock-look-restore/')).length,look==='rock'?1:0);
  assert.equal(assetRequests.filter(r=>r.url.endsWith('/grey-limestone-material.glb')).length,look==='limestone'?1:0);
  assert.equal(assetRequests.filter(r=>r.url.endsWith('/excavation-detailed.glb')).length,1);
  assert.equal(assetRequests.filter(r=>r.url.includes('/quarry-rollout/')).length,0);
  runs.push({look,preparationMs,material,details:await details(p),requests,assetRequests,totalEncodedTransfer:requests.reduce((n,r)=>n+r.encodedBytes,0)});
  await c.close();
 }
 assert.deepEqual(errors,[]);
}catch(e){errors.push(String(e.stack));process.exitCode=1;}
finally{await writeFile(root+'/raw/material-runtime-and-network.json',JSON.stringify({status:errors.length?'FAIL':'PASS',browser:browser.version(),method:'Actual cold browser contexts, CDP disk cache disabled, localhost, DPR0.25/Q3, no CPU/network throttle. Both families use identical connected geometry; encoded network bytes include response overhead. Runtime materials are inspected after covered preparation.',runs,errors},null,2));await browser.close();}
