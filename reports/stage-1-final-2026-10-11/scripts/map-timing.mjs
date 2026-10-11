import {launch,instrument,local,snapshot,root,base} from './audit-common.mjs';
import assert from 'node:assert/strict';
import {writeFile} from 'node:fs/promises';
const browser=await launch(),context=await browser.newContext({viewport:{width:1366,height:900},deviceScaleFactor:.25}),page=await context.newPage(),windows=[];
await instrument(context);
const result={method:'Separate public M/Esc event-to-state timing, actual drawn frame intervals, same persistent Canvas; no screenshot/video readbacks in windows; SwiftShader, DPR .25, not hardware certification.',windows};
try {
 await page.goto(base+'/?diagnostics&arrival=hub');await local(page,'hub');const canvas=await page.locator('canvas').evaluateHandle(c=>c);
 for(const location of ['hub','aftermovie']) {
  if(location==='aftermovie'){await page.getByRole('button',{name:/^Map/}).click();await page.waitForFunction(()=>window.__gullyverse.runtime.getSnapshot().mapStage==='open');await page.getByRole('button',{name:'Aftermovie',exact:true}).click();await local(page,'aftermovie');}
  const saved=await page.evaluate(()=>({...window.__gullyverse.runtime.pose}));
  for(const [name,key,done,expected] of [['ascent','KeyM','open',1400],['descent','Escape',null,1100]]) {
   await page.evaluate(()=>{const d=window.__gullyverse;d.frames.length=0;window.__mapStates=[];window.__unsub=d.runtime.subscribe(()=>{const s=d.runtime.getSnapshot();window.__mapStates.push({at:performance.now(),map:s.map,stage:s.mapStage});});});
   await page.keyboard.press(key);await page.waitForFunction(stage=>window.__gullyverse.runtime.getSnapshot().mapStage===stage,done,{timeout:20000});
   const data=await page.evaluate(()=>{window.__unsub();return {states:window.__mapStates,frames:window.__gullyverse.frames,cover:window.__gullyverse.runtime.revealOpacity};});
   const elapsed=data.states.at(-1).at-data.states[0].at,times=data.frames.filter(f=>Number.isFinite(f.cpuRenderMs)).map(f=>f.ms).sort((a,b)=>a-b),q=x=>times[Math.min(times.length-1,Math.floor(times.length*x))];
   windows.push({location,name,eventDurationMs:elapsed,expectedMs:expected,frameCount:times.length,averageFPS:times.length*1000/elapsed,p50Ms:q(.5),p95Ms:q(.95),p99Ms:q(.99),maxMs:times.at(-1),...data,...await snapshot(page)});
   assert.ok(elapsed>=expected-10&&elapsed<=expected+times.at(-1)+150,'Clock endpoint within one measured renderer interval');
  }
  const returned=await page.evaluate(()=>({...window.__gullyverse.runtime.pose}));for(const field of ['x','y','z','yaw','pitch'])assert.ok(Math.abs(saved[field]-returned[field])<1e-6);
 }
 assert.equal(await page.evaluate(c=>document.querySelector('canvas')===c,canvas),true);result.status='PASS';
}catch(e){result.status='FAIL';result.error=String(e.stack);process.exitCode=1;}finally{await writeFile(root+'/raw/map-timing.json',JSON.stringify(result,null,2));await browser.close();}
