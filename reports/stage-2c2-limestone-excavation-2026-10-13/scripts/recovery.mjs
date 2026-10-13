import{launch,context,ready,details,root}from'./wall-browser-common.mjs';import assert from'node:assert/strict';import{writeFile}from'node:fs/promises';
const b=await launch(),checks=[];let c,p;
const url='http://127.0.0.1:3000/?arrival=hub&diagnostics&quarryReview=excavation';
async function check(name,fn){try{checks.push({name,status:'PASS',evidence:await fn()});}catch(e){checks.push({name,status:'FAIL',error:String(e.stack)});process.exitCode=1;}console.log(name,checks.at(-1).status);await writeFile(root+'/raw/recovery.json',JSON.stringify({checks},null,2));}
async function open(){c=await context(b,{deviceScaleFactor:.25});p=await c.newPage();}
async function settle(){await p.waitForFunction(()=>window.__gullyverse?.runtime);await p.evaluate(()=>window.__gullyverse.runtime.setQuality(3));await ready(p);}
try{
 await open();await p.goto(url);await settle();
 await check('Actual WebGL loss/recovery preserves excavation, pose and Canvas',async()=>{
  const canvas=await p.evaluateHandle(()=>document.querySelector('canvas')),saved=await details(p);
  await p.evaluate(()=>{window.__loss=document.querySelector('canvas').getContext('webgl2').getExtension('WEBGL_lose_context');window.__loss.loseContext();});
  await p.waitForSelector('[data-phase="context-lost"]');await p.waitForTimeout(250);await p.evaluate(()=>window.__loss.restoreContext());await ready(p);
  const after=await details(p);assert.equal(after.wall.selectedNodes.length,18);assert.equal(await canvas.evaluate(v=>v===document.querySelector('canvas')),true);
  assert.ok(Math.hypot(after.pose.x-saved.pose.x,after.pose.y-saved.pose.y,after.pose.z-saved.pose.z)<1e-6);return{saved,after};
 });await c.close();
 await open();await p.route('**/excavation-detailed.glb',r=>r.abort());
 await check('Failed optional excavation restores Stage2C; explicit retry succeeds',async()=>{
  await p.goto(url);await settle();const failed=await details(p);assert.equal(await p.evaluate(()=>window.__wallPreview.style),'baseline');assert.equal(failed.wall.selectedNodes.length,27);
  await p.unroute('**/excavation-detailed.glb');await p.evaluate(()=>window.__wallPreview.setExcavation('detailed'));await ready(p);
  const retry=await details(p);assert.equal(retry.wall.selectedNodes.length,18);return{failed,retry};
 });await c.close();
 await open();await p.route('**/excavation-detailed.glb',async r=>{await new Promise(resolve=>setTimeout(resolve,5500));await r.continue().catch(()=>{});});
 await check('Delayed geometry remains covered and unmount disposes abandoned load',async()=>{
  await p.goto(url);await p.waitForFunction(()=>window.__wallPreview?.trace.some(e=>e.event==='approved-material-ready'),null,{timeout:90000});
  const handle=await p.evaluateHandle(()=>window.__wallPreview);assert.ok(await p.locator('[data-wall-cover]').count());
  await p.getByRole('button',{name:'Use without 3D',exact:true}).click();await p.waitForFunction(()=>!document.querySelector('canvas'));await p.waitForTimeout(8000);
  const owner=await handle.evaluate(s=>({disposed:s.disposed,asset:!!s.asset,caches:s.assets.size,consumers:s.consumers,trace:s.trace}));
  assert.equal(owner.disposed,true);assert.equal(owner.asset,false);assert.equal(owner.caches,0);assert.equal(owner.consumers,0);return owner;
 });await c.close();
 await open();await p.route('**/grey-limestone-material.glb',r=>r.abort());
 await check('Failed approved-material load keeps safe Stage2C fallback',async()=>{await p.goto(url);await settle();assert.equal(await p.evaluate(()=>window.__wallPreview.style),'baseline');const d=await details(p);assert.equal(d.wall.selectedNodes.length,27);return d;});await c.close();
 await open();await p.route('**/excavation-detailed.glb',r=>r.fulfill({path:'assets-source/gullyverse/limestone-excavation/unpacked/excavation-detailed.glb',contentType:'model/gltf-binary'}));
 await check('Accidental unpacked geometry payload is rejected and its duplicate maps are disposed',async()=>{await p.goto(url);await settle();assert.equal(await p.evaluate(()=>window.__wallPreview.style),'baseline');const d=await details(p);assert.equal(d.wall.selectedNodes.length,27);assert.ok(d.wall.trace.some(e=>e.event==='excavation-load-failed'&&e.message.includes('duplicate maps')));return d;});await c.close();
 await open();await p.route('**/aftermovie-stage.glb',r=>r.abort());
 await check('Failed critical original stage reaches native video fallback',async()=>{await p.goto('http://127.0.0.1:3000/aftermovie?diagnostics&quarryReview=excavation');await p.waitForFunction(()=>!document.querySelector('canvas')&&document.querySelector('video'),null,{timeout:90000});return{videoCount:await p.locator('video').count()};});
}finally{await c?.close();await b.close();}
