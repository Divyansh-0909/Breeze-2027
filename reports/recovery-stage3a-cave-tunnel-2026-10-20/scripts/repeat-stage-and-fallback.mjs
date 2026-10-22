// Continue lifecycle assertions independently after the documented flaky
// cold direct-stage gate. No deadline is changed or original failure removed.
import assert from 'node:assert/strict';
import {writeFile} from 'node:fs/promises';
import {launch,context,ready} from '../../stage-2c5-1-rock-realism-refinement-2026-10-14/scripts/wall-browser-common.mjs';
const root='reports/recovery-stage3a-cave-tunnel-2026-10-20';
const browser=await launch(),checks=[],errors=[];let current;
try{
 current=await context(browser,{deviceScaleFactor:.25});const page=await current.newPage();
 await page.goto('http://127.0.0.1:3000/?arrival=hub&diagnostics&quarryReview=geology-fidelity&entranceReview=natural-cave');
 await page.waitForFunction(()=>window.__gullyverse?.runtime);await page.evaluate(()=>window.__gullyverse.runtime.setQuality(3));await ready(page);
 const canvas=await page.evaluateHandle(()=>document.querySelector('canvas'));
 const baseline=await page.evaluate(()=>window.__wallPreview.materialDiagnostics().textures.map(t=>t.source));
 async function record(label){
  const data=await page.evaluate(()=>({cave:window.__wallPreview.entranceDiagnostics(),composition:window.__wallPreview.compositionDiagnostics(),material:window.__wallPreview.materialDiagnostics(),state:window.__gullyverse.runtime.getSnapshot(),url:location.href,memory:window.__gullyverse.stats}));
  assert.equal(data.cave.ready,true);assert.equal(data.material.scale,3);assert.equal(data.composition.sourceUniformScale,.9);assert.equal(new URL(data.url).searchParams.get('entranceReview'),'natural-cave');assert.deepEqual(data.material.textures.map(t=>t.source),baseline);assert.equal(await canvas.evaluate(c=>c===document.querySelector('canvas')),true);
  checks.push({name:label,status:'PASS',data});console.log(label);
 }
 async function go(scene){await page.getByRole('button',{name:/^Map/}).click();await page.waitForFunction(()=>window.__gullyverse?.runtime?.getSnapshot().mapStage==='open');await page.getByRole('button',{name:scene==='hub'?'Gullyverse hub':'Aftermovie',exact:true}).click();await page.waitForFunction(id=>window.__gullyverse?.runtime?.getSnapshot().scene===id&&window.__gullyverse?.runtime?.getSnapshot().phase==='local',scene,{timeout:90000});await ready(page);}
 for(let i=0;i<3;i++){
  await go('aftermovie');await record('repeat stage arrival '+i);
  await page.getByRole('button',{name:'Play Aftermovie',exact:true}).click();await page.waitForFunction(()=>window.__gullyverse.runtime.movieActions.status().currentTime>.2,null,{timeout:30000});await record('repeat playback '+i);
  await page.getByRole('button',{name:'Exit Aftermovie',exact:true}).click();await page.waitForFunction(()=>!window.__gullyverse.runtime.getSnapshot().movie);
  await go('hub');await record('repeat return to C9 hub '+i);
 }
 await current.close();current=null;
 current=await context(browser,{deviceScaleFactor:.25});const failure=await current.newPage();await failure.route('**/aftermovie-stage.glb',r=>r.abort());
 await failure.goto('http://127.0.0.1:3000/aftermovie?diagnostics&quarryReview=geology-fidelity&entranceReview=natural-cave');
 await failure.waitForFunction(()=>!document.querySelector('canvas')&&document.querySelector('video'),null,{timeout:90000});checks.push({name:'Critical stage GLB failure retains native video fallback',status:'PASS',videos:await failure.locator('video').count()});
}catch(e){errors.push(String(e.stack));process.exitCode=1;}
finally{await current?.close();await browser.close();await writeFile(root+'/raw/repeat-stage-and-fallback.json',JSON.stringify({status:errors.length?'FAIL':'PASS',checks,errors,physicalHardware:false,mode:'Isolated continuation of assertions blocked by the recorded cold-stage failure. Q3 requested after runtime start under existing cover; not a default-quality cold-start acceptance.'},null,2));}
