import assert from 'node:assert/strict';
import {mkdir,writeFile} from 'node:fs/promises';
import {launch,context,ready,details} from '../../stage-2c5-1-rock-realism-refinement-2026-10-14/scripts/wall-browser-common.mjs';
const R='reports/cave-material-study-2026-10-22',browser=await launch(),checks=[];let ctx,p;
const url='http://127.0.0.1:3000/?arrival=hub&diagnostics&quarryReview=geology-fidelity&entranceReview=material-study&caveMaterial=rock_01';
async function open(){await ctx?.close();ctx=await context(browser,{deviceScaleFactor:.25});await ctx.addInitScript(()=>{const closed=new WeakSet(),close=ImageBitmap.prototype.close;window.__studyCloses={total:0,duplicate:0};ImageBitmap.prototype.close=function(){window.__studyCloses.total++;if(closed.has(this))window.__studyCloses.duplicate++;closed.add(this);return close.call(this);};});p=await ctx.newPage();}
async function active(){await ready(p);await p.waitForFunction(()=>window.__wallPreview.studyDiagnostics().ready&&!window.__wallPreview.state.busy);return p.evaluate(()=>({study:window.__wallPreview.studyDiagnostics(),quarry:window.__wallPreview.materialDiagnostics(),composition:window.__wallPreview.compositionDiagnostics(),closes:window.__studyCloses}));}
async function check(name,fn){try{checks.push({name,status:'PASS',evidence:await fn()});}catch(e){checks.push({name,status:'FAIL',error:String(e.stack)});process.exitCode=1;}console.log(name,checks.at(-1).status);await writeFile(R+'/raw/study-lifecycle.json',JSON.stringify({checks,physicalHardware:false},null,2));}
try{
 await open();await p.goto(url);await p.waitForFunction(()=>window.__gullyverse?.runtime);await p.evaluate(()=>window.__gullyverse.runtime.setQuality(3));
 await check('Material switching preserves C9 sampler/source IDs and plateaus after family retirement',async()=>{
  const first=await active(),samples=[];assert.equal(first.study.studySourceImages,3);assert.equal(first.study.geometryMode,'baseline');
  const ids=first.quarry.textures.map(t=>[t.uuid,t.source,t.repeat]);
  for(let i=0;i<6;i++){
   await p.evaluate(i=>window.__wallPreview.setStudySelection(i%2?'rock_01':'rock_05',i%2?2:1),i);const next=await active();assert.equal(next.study.retiredFamilies,0);assert.equal(next.study.studySourceImages,3);assert.deepEqual(next.quarry.textures.map(t=>[t.uuid,t.source,t.repeat]),ids);assert.equal(next.study.quarrySamplerScale,3);assert.equal(next.closes.duplicate,0);samples.push({next,data:await details(p)});
  }
  assert.ok(samples.at(-1).data.stats.textures<=samples[1].data.stats.textures);return{first,samples};
 });
 await check('Pilot A/B adds one local GLB and reuses its cached geometry across switches',async()=>{
  const samples=[];for(let i=0;i<4;i++){await p.evaluate(i=>window.__wallPreview.setStudyGeometry(i%2===0),i);await active();samples.push(await p.evaluate(()=>window.__wallPreview.studyDiagnostics()));}
  assert.deepEqual(samples.map(s=>s.geometryMode),['pilot','baseline','pilot','baseline']);const resources=await p.evaluate(()=>performance.getEntriesByType('resource').map(r=>r.name));assert.equal(resources.filter(u=>u.endsWith('/emboss-pilot.glb')).length,1);assert.equal(resources.filter(u=>u.endsWith('/foundation-geometry.glb')).length,1);return{samples,resources};
 });
 await check('WebGL loss/recovery preserves selected material, C9 and persistent Canvas',async()=>{
  const before=await active(),canvas=await p.evaluateHandle(()=>document.querySelector('canvas'));
  await p.evaluate(()=>{window.__studyLoss=document.querySelector('canvas').getContext('webgl2').getExtension('WEBGL_lose_context');window.__studyLoss.loseContext();});await p.waitForSelector('[data-phase="context-lost"]');await p.evaluate(()=>window.__studyLoss.restoreContext());const after=await active();assert.equal(await canvas.evaluate(c=>c===document.querySelector('canvas')),true);assert.equal(after.study.selected,before.study.selected);assert.deepEqual(after.quarry.textures.map(t=>t.source),before.quarry.textures.map(t=>t.source));assert.equal(after.closes.duplicate,0);return{before,after};
 });
 await check('Inactive retirement releases study ownership and allows a fresh covered reload',async()=>{
  const before=await active();await p.evaluate(()=>window.__wallPreview.setMode('off'));await ready(p);await p.evaluate(()=>window.__wallPreview.retire());const retired=await p.evaluate(()=>window.__wallPreview.studyDiagnostics());assert.equal(retired.studySourceImages,0);assert.equal(retired.pilot.ready,false);await p.evaluate(()=>window.__wallPreview.setComposition(true));const after=await active();assert.equal(after.study.studySourceImages,3);assert.equal(after.closes.duplicate,0);return{before,retired,after};
 });
 await check('Native fallback unmount closes selected images once',async()=>{const owner=await p.evaluateHandle(()=>window.__wallPreview);await p.getByRole('button',{name:'Use without 3D',exact:true}).click();await p.waitForFunction(()=>!document.querySelector('canvas'));const d=await owner.evaluate(o=>({disposed:o.disposed,study:o.studyDiagnostics()}));assert.equal(d.disposed,true);assert.equal(d.study.studySourceImages,0);assert.equal((await p.evaluate(()=>window.__studyCloses)).duplicate,0);return d;});
 await open();await p.route('**/cave-material-study/rock_01/normal.png',r=>r.abort());
 await check('Failed material channel retains functional cave/C9 and retry recovers',async()=>{await p.goto(url);await p.waitForFunction(()=>window.__gullyverse?.runtime);await p.evaluate(()=>window.__gullyverse.runtime.setQuality(3));const failed=await active();assert.ok(failed.study.error);assert.equal(failed.study.studySourceImages,0);assert.equal(failed.composition.ready,true);await p.unroute('**/cave-material-study/rock_01/normal.png');await p.evaluate(()=>window.__wallPreview.setStudySelection('rock_01',1));const after=await active();assert.equal(after.study.active,'rock_01');assert.equal(after.study.error,null);assert.equal(after.closes.duplicate,0);return{failed,after};});
 await open();await p.route('**/cave-material-study/rock_01/normal.png',async r=>{await new Promise(resolve=>setTimeout(resolve,3000));await r.continue().catch(()=>{});});
 await check('Unmount during delayed material decoding does not adopt images or double-close',async()=>{const requested=p.waitForRequest('**/cave-material-study/rock_01/normal.png');await p.goto(url);await requested;const owner=await p.evaluateHandle(()=>window.__wallPreview);await p.getByRole('button',{name:'Use without 3D',exact:true}).click();await p.waitForFunction(()=>!document.querySelector('canvas'));await p.waitForTimeout(5000);const d=await owner.evaluate(o=>({disposed:o.disposed,study:o.studyDiagnostics()}));assert.equal(d.disposed,true);assert.equal(d.study.studySourceImages,0);assert.equal((await p.evaluate(()=>window.__studyCloses)).duplicate,0);return d;});
}finally{await ctx?.close();await browser.close();await writeFile(R+'/raw/study-lifecycle.json',JSON.stringify({checks,physicalHardware:false},null,2));}
