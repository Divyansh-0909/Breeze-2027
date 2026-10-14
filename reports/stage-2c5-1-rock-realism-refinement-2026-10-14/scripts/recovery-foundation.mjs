import{launch,context,ready,details,root}from'./wall-browser-common.mjs';import assert from'node:assert/strict';import{writeFile}from'node:fs/promises';
const b=await launch(),checks=[];let c,p;
const url='http://127.0.0.1:3000/?arrival=hub&diagnostics&quarryReview=foundation-refined';
async function check(name,fn){try{checks.push({name,status:'PASS',evidence:await fn()});}catch(e){checks.push({name,status:'FAIL',error:String(e.stack)});process.exitCode=1;}console.log(name,checks.at(-1).status);await writeFile(root+'/raw/recovery.json',JSON.stringify({checks},null,2));}
async function open(){c=await context(b,{deviceScaleFactor:.25});p=await c.newPage();}
try{
 await open();await p.goto(url);await ready(p);
 await check('Actual WebGL loss/recovery preserves foundation pose and persistent Canvas',async()=>{
  const canvas=await p.evaluateHandle(()=>document.querySelector('canvas')),saved=await details(p);
  await p.evaluate(()=>{window.__loss=document.querySelector('canvas').getContext('webgl2').getExtension('WEBGL_lose_context');window.__loss.loseContext();});
  await p.waitForSelector('[data-phase="context-lost"]');await p.waitForTimeout(250);await p.evaluate(()=>window.__loss.restoreContext());await ready(p);
  const after=await details(p);assert.equal(after.wall.selectedNodes.length,35);assert.equal(await canvas.evaluate(v=>v===document.querySelector('canvas')),true);
  assert.ok(Math.hypot(after.pose.x-saved.pose.x,after.pose.y-saved.pose.y,after.pose.z-saved.pose.z)<1e-6);return{saved,after};
 });await c.close();
 for(const file of ['foundation-geometry.glb','foundation-materials.glb']){
  await open();await p.route('**/'+file,r=>r.abort());
  await check('Failed '+file+' retains connected dark baseline; explicit retry',async()=>{
   await p.goto(url);await ready(p);const failed=await details(p);assert.equal(await p.evaluate(()=>window.__wallPreview.foundationEnabled),false);assert.equal(failed.wall.selectedNodes.length,18);
   await p.unroute('**/'+file);await p.evaluate(()=>window.__wallPreview.setFoundation(true));await ready(p);
   const retry=await details(p);assert.equal(retry.wall.selectedNodes.length,35);return{failed,retry};
  });await c.close();
 }
 await open();await p.route('**/foundation-geometry.glb',async r=>{await new Promise(resolve=>setTimeout(resolve,5500));await r.continue().catch(()=>{});});
 await check('Delayed load stays covered; fallback unmount disposes unpublished resources',async()=>{
  await p.goto(url);await p.waitForFunction(()=>window.__wallPreview?.trace.some(e=>e.event==='foundation-material-parse'),null,{timeout:90000});
  const handle=await p.evaluateHandle(()=>window.__wallPreview);assert.ok(await p.locator('[data-wall-cover]').count());
  await p.getByRole('button',{name:'Use without 3D',exact:true}).click();await p.waitForFunction(()=>!document.querySelector('canvas'));await p.waitForTimeout(8000);
  const owner=await handle.evaluate(s=>({disposed:s.disposed,asset:!!s.asset,caches:s.assets.size,consumers:s.consumers,trace:s.trace}));
  assert.equal(owner.disposed,true);assert.equal(owner.asset,false);assert.equal(owner.caches,0);assert.equal(owner.consumers,0);assert.ok(owner.trace.some(e=>e.event==='foundation-material-disposal'));return owner;
 });await c.close();
 await open();await p.route('**/foundation-geometry.glb',r=>r.fulfill({path:'public/models/gullyverse/quarry-foundation/foundation-materials.glb',contentType:'model/gltf-binary'}));
 await check('Duplicate embedded texture payload is rejected and owned resources disposed',async()=>{
  await p.goto(url);await ready(p);const d=await details(p);assert.equal(await p.evaluate(()=>window.__wallPreview.foundationEnabled),false);
  assert.ok(d.wall.trace.some(e=>e.event==='foundation-rejected-disposal'&&e.textures===6));return d;
 });await c.close();
 await open();await p.route('**/aftermovie-stage.glb',r=>r.abort());
 await check('Critical original stage failure reaches native video fallback',async()=>{await p.goto('http://127.0.0.1:3000/aftermovie?diagnostics&quarryReview=foundation-refined');await p.waitForFunction(()=>!document.querySelector('canvas')&&document.querySelector('video'),null,{timeout:90000});return{videoCount:await p.locator('video').count()};});await c.close();
 await open();
 await check('Ordinary public URL never requests foundation assets or exposes review controls',async()=>{
  await p.goto('http://127.0.0.1:3000/?arrival=hub&diagnostics');await ready(p);
  const requested=await p.evaluate(()=>performance.getEntriesByType('resource').map(e=>e.name));
  assert.ok(!requested.some(u=>u.includes('/quarry-foundation/')||u.includes('/quarry-foundation-refined/')));assert.equal(await p.locator('[data-quarry-controls]').count(),0);return{requested};
 });
}finally{await c?.close();await b.close();}
