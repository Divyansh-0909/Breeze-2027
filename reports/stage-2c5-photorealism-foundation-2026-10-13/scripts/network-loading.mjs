import{writeFile}from'node:fs/promises';import{launch,context,ready,details,root}from'./wall-browser-common.mjs';
const b=await launch(),runs=[],errors=[];let c,p;
async function cachedContext(){
 c=await context(b,{deviceScaleFactor:.5});await c.unrouteAll();p=await c.newPage();
 const cdp=await c.newCDPSession(p);await cdp.send('Network.enable');
 // Playwright routing disables HTTP cache. CDP URL blocking keeps the API/
 // analytics guard without altering browser cache policy for static assets.
 await cdp.send('Network.setBlockedURLs',{urls:['*/api/*','*vercel-insights.com/*','*google-analytics.com/*','*googletagmanager.com/*']});
 await cdp.send('Network.setCacheDisabled',{cacheDisabled:false});await cdp.send('Network.clearBrowserCache');
 return cdp;
}
try{
 for(const variant of ['excavation','foundation']){
  const cdp=await cachedContext(),responses=[];
  cdp.on('Network.responseReceived',e=>responses.push({url:e.response.url,status:e.response.status,fromDiskCache:!!e.response.fromDiskCache,fromServiceWorker:!!e.response.fromServiceWorker,cacheControl:e.response.headers['Cache-Control']??e.response.headers['cache-control']}));
  const url='http://127.0.0.1:3000/?arrival=hub&diagnostics&quarryReview='+variant;
  for(const cache of ['cold','warm']){
   responses.length=0;const start=Date.now();await p.goto(url);await p.waitForFunction(()=>window.__gullyverse?.runtime);await p.evaluate(()=>window.__gullyverse.runtime.setQuality(3));await ready(p);
   const d=await details(p),resources=await p.evaluate(()=>performance.getEntriesByType('resource').map(e=>({name:e.name,transferSize:e.transferSize,encodedBodySize:e.encodedBodySize,decodedBodySize:e.decodedBodySize,startTime:e.startTime,duration:e.duration,responseEnd:e.responseEnd})));
   const navigation=await p.evaluate(()=>performance.getEntriesByType('navigation')[0]?.toJSON());
   runs.push({label:variant+'-'+cache,route:'direct hub',readyMs:Date.now()-start,
    totalTransferBytes:resources.reduce((s,r)=>s+r.transferSize,0)+(navigation?.transferSize??0),
    encodedBytes:resources.reduce((s,r)=>s+r.encodedBodySize,0)+(navigation?.encodedBodySize??0),
    newAssetBytes:resources.filter(r=>r.name.includes('/quarry-foundation/')).reduce((s,r)=>s+r.encodedBodySize,0),
    resources,navigation,responses:[...responses],data:d});console.log(runs.at(-1).label,runs.at(-1).readyMs,runs.at(-1).totalTransferBytes);
  }await c.close();
 }
 await cachedContext();
 await p.goto('http://127.0.0.1:3000/?diagnostics&quarryReview=foundation');await p.waitForSelector('[data-phase="landing"]',{timeout:90000});
 await p.waitForFunction(()=>window.__wallPreview&&!window.__wallPreview.state.busy,null,{timeout:90000});
 const start=Date.now();await p.getByRole('button',{name:'Enter Gullyverse',exact:true}).click();await ready(p);
 const phases=await p.evaluate(()=>window.__gullyverse.phases),activated=phases.find(x=>x.phase==='entrance'),arrived=phases.find(x=>x.phase==='local'&&x.at>activated?.at);
 const entrance={actionAndSequenceMs:Date.now()-start,entrancePhaseMs:arrived&&activated?arrived.at-activated.at:null,data:await details(p),phases,
  method:'Authored progression timed from actual phase activation, separately from Playwright click/actionability scheduling overhead.'};
 await writeFile(root+'/raw/entrance-timing.json',JSON.stringify(entrance,null,2));
}catch(e){errors.push(String(e.stack));process.exitCode=1;}
finally{await c?.close();await b.close();await writeFile(root+'/raw/network-loading.json',JSON.stringify({status:errors.length?'FAIL':'PASS',method:'HTTP cache enabled explicitly; no Playwright routing. CDP blocks API/analytics URLs. Cold cache cleared once per variant, same-context warm revisit. Production1366x900,DPR0.5,Q3. Localhost transfer excludes blocked analytics; decoded/encoded size distinguished from cached transfer; response cache flags recorded.',runs,errors},null,2));}
