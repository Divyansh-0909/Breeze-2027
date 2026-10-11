import {launch,root,base,world,local,map,key,snapshot,instrument} from './audit-common.mjs';
import {writeFile} from 'node:fs/promises';
import os from 'node:os';
const browser=await launch(),windows=[],errors=[],network=[],writes=[];
const dpr=Number(process.env.AUDIT_DPR||'.25');
const context=await browser.newContext({viewport:{width:1366,height:900},deviceScaleFactor:dpr});
// HTTP cache must remain enabled: CDP guards only API writes, no Playwright routing.
await context.addInitScript(()=>{window.__audit={contexts:[],tasks:[],createdVideos:[]};new PerformanceObserver(l=>window.__audit.tasks.push(...l.getEntries().map(e=>({at:e.startTime,ms:e.duration})))).observe({type:'longtask',buffered:true});});
const page=await context.newPage(),cdp=await context.newCDPSession(page);await cdp.send('Network.enable');await cdp.send('Network.setCacheDisabled',{cacheDisabled:false});await cdp.send('Fetch.enable',{patterns:[{urlPattern:'*/api/*',requestStage:'Request'}]});
cdp.on('Fetch.requestPaused',async e=>{if(!['GET','HEAD'].includes(e.request.method)){writes.push({method:e.request.method,url:e.request.url});await cdp.send('Fetch.failRequest',{requestId:e.requestId,errorReason:'Aborted'});}else await cdp.send('Fetch.continueRequest',{requestId:e.requestId});});
cdp.on('Network.responseReceived',e=>network.push({at:e.timestamp,url:e.response.url,status:e.response.status,fromDiskCache:e.response.fromDiskCache,fromServiceWorker:e.response.fromServiceWorker,encodedDataLength:e.response.encodedDataLength}));
page.on('pageerror',e=>errors.push(e.message));
const result={browser:browser.version(),os:`${os.platform()} ${os.release()}`,cpu:os.cpus()[0]?.model,vcpus:os.cpus().length,viewport:{width:1366,height:900,requestedDpr:dpr},windows,errors,network,writes,method:'One browser at a time; no recording/screenshots during benchmark. Actual R3F frame deltas filtered by finite cpuRenderMs. HTTP cache enabled. No CPU throttling. Software GPU; not desktop or mobile hardware certification.'};
async function save(){await writeFile(root+'/raw/'+(process.env.PERF_LABEL||'baseline')+'-performance.json',JSON.stringify(result,null,2));}
function summary(frames,elapsed){const times=frames.filter(f=>Number.isFinite(f.cpuRenderMs)).map(f=>f.ms).sort((a,b)=>a-b),q=x=>times[Math.min(times.length-1,Math.floor(times.length*x))]??null,mean=times.length?times.reduce((s,v)=>s+v,0)/times.length:null;return{loopFrames:frames.length,renderedFrames:times.length,renderedFPS:times.length*1000/elapsed,renderCadenceFPS:mean?1000/mean:null,medianMs:q(.5),p95Ms:q(.95),p99Ms:q(.99),maxMs:times.at(-1)??null,stallsOver50ms:times.filter(v=>v>50).length,stallsOver100ms:times.filter(v=>v>100).length};}
async function measure(name,action){await page.evaluate(()=>{window.__gullyverse.frames.length=0;window.__measureAt=performance.now();});const at=Date.now();await action();const elapsed=Date.now()-at;const raw=await page.evaluate(()=>({frames:window.__gullyverse.frames.map(f=>({...f})),stats:window.__gullyverse.stats,snapshot:window.__gullyverse.runtime.getSnapshot(),preparation:window.__gullyverse.preparations.filter(p=>p.at>=window.__measureAt),phases:window.__gullyverse.phases.filter(p=>p.at>=window.__measureAt),memory:window.__gullyverse.memory.at(-1),renderer:window.__gullyverse.renderer,gpuTimer:window.__gullyverse.gpuTimer,gpu:window.__gullyverse.gpu,resources:performance.getEntriesByType('resource').map(r=>r.toJSON()),tasks:window.__audit.tasks.filter(t=>t.at>=window.__measureAt)}));windows.push({name,elapsedMs:elapsed,...summary(raw.frames,elapsed),...raw});await save();console.log(name,elapsed+'ms',windows.at(-1).renderedFrames+' draws');}
try{
 for(const name of ['cold-landing-load','warm-same-browser-cache-landing-load']){
  const at=Date.now();await page.goto(base+'/?diagnostics',{waitUntil:'domcontentloaded'});await page.waitForSelector('[data-phase="landing"]',{timeout:100000});const elapsed=Date.now()-at;const raw=await page.evaluate(()=>({navigation:performance.getEntriesByType('navigation').map(r=>r.toJSON()),resources:performance.getEntriesByType('resource').map(r=>r.toJSON()),frames:window.__gullyverse.frames,stats:window.__gullyverse.stats,snapshot:window.__gullyverse.runtime.getSnapshot(),renderer:window.__gullyverse.renderer,preparation:window.__gullyverse.preparations,memory:window.__gullyverse.memory.at(-1),tasks:window.__audit.tasks}));windows.push({name,elapsedMs:elapsed,...summary(raw.frames,elapsed),...raw});await save();console.log(name,elapsed+'ms');
 }
 await measure('tunnel-and-first-hub-arrival',async()=>{await page.keyboard.press('Enter');await local(page,'hub');});
 await measure('first-hub-arrival-settling',()=>page.waitForTimeout(3000));
 await measure('hub-local-movement',async()=>{for(const [code,ms] of [['KeyD',800],['KeyA',1600],['KeyD',1600],['KeyA',1600]])await key(page,code,ms);});
 await measure('hub-to-aftermovie-physical-route',async()=>{await page.keyboard.down('KeyS');await page.waitForSelector('[data-phase="departure"]',{timeout:50000});await page.keyboard.up('KeyS');await local(page,'aftermovie');});
 await measure('aftermovie-local-movement',async()=>{for(const [code,ms] of [['KeyD',700],['KeyA',1400],['KeyD',1400],['KeyA',1400]])await key(page,code,ms);});
 await page.keyboard.down('KeyS');await page.getByRole('dialog',{name:'Where to next?'}).waitFor({timeout:40000});await page.keyboard.up('KeyS');
 await measure('aftermovie-boundary-return-to-hub',async()=>{await page.getByRole('button',{name:'Return to Hub',exact:true}).click();await local(page,'hub');});
 await measure('map-to-aftermovie',()=>map(page,'aftermovie'));
 for(let i=0;i<3;i++){
  await measure('repeat-'+(i+1)+'-aftermovie-hub',()=>map(page,'hub'));
  await measure('repeat-'+(i+1)+'-hub-aftermovie',()=>map(page,'aftermovie'));
 }
 const samples=windows.find(w=>w.name==='tunnel-and-first-hub-arrival').frames;
 for(const [label,predicate] of [['tunnel-interior',f=>f.phase==='entrance'&&f.poseZ<-3&&f.poseZ>-38],['quarry-reveal',f=>f.phase==='entrance'&&f.poseZ<=-38]]){const frames=samples.filter(predicate);const elapsed=frames.reduce((s,f)=>s+f.ms,0);windows.push({name:label,elapsedMs:elapsed,...summary(frames,elapsed),frames,note:'Phase/pose subset of the same measured entrance window; not an independent rerun.'});}
}catch(e){result.error=String(e.stack||e);process.exitCode=1;}
finally{await save();await browser.close();console.log(JSON.stringify({...result,windows:windows.map(({frames,resources,preparation,memory,tasks,phases,gpu,...w})=>w),network:network.length},null,2));}
