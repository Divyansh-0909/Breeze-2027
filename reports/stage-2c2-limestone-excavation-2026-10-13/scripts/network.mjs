import{launch,context,details,root}from'./wall-browser-common.mjs';import{writeFile}from'node:fs/promises';import assert from'node:assert/strict';
const b=await launch(),runs=[];
try{for(const[label,query]of[['stage2c-default',''],['macro-preview','&quarryReview=excavation&excavation=macro'],['detailed-preview','&quarryReview=excavation']]){
 const c=await context(b,{deviceScaleFactor:.25}),p=await c.newPage(),cdp=await c.newCDPSession(p),requests=new Map();
 await cdp.send('Network.enable');await cdp.send('Network.setCacheDisabled',{cacheDisabled:true});
 cdp.on('Network.requestWillBeSent',e=>requests.set(e.requestId,{url:e.request.url}));cdp.on('Network.responseReceived',e=>Object.assign(requests.get(e.requestId)||{},{status:e.response.status,mimeType:e.response.mimeType,fromDiskCache:!!e.response.fromDiskCache}));cdp.on('Network.loadingFinished',e=>Object.assign(requests.get(e.requestId)||{},{encodedBytes:e.encodedDataLength}));
 await p.goto('http://127.0.0.1:3000/?diagnostics'+query);await p.waitForFunction(()=>window.__gullyverse?.runtime);await p.evaluate(()=>window.__gullyverse.runtime.setQuality(3));
 await p.waitForFunction(()=>window.__gullyverse.runtime.getSnapshot().phase==='landing'&&!window.__wallPreview.state.busy,null,{timeout:90000});
 const data=await p.evaluate(()=>({navigation:performance.getEntriesByType('navigation').map(e=>e.toJSON()),resources:performance.getEntriesByType('resource').map(e=>e.toJSON()),readyAtMs:performance.now()})),entries=[...requests.values()].filter(e=>e.url.startsWith('http://127.0.0.1:3000'));
 if(label==='stage2c-default')assert.ok(!entries.some(e=>e.url.includes('/limestone-excavation/')));
 else assert.ok(!entries.some(e=>e.url.includes('/quarry-rollout/')));
 runs.push({label,CDPLocalEncodedBytes:entries.reduce((n,e)=>n+(e.encodedBytes||0),0),requests:entries,...data,details:await details(p)});
 console.log(label,runs.at(-1).CDPLocalEncodedBytes,runs.at(-1).readyAtMs);await c.close();
 }await writeFile(root+'/raw/network.json',JSON.stringify({status:'PASS',method:'Fresh contexts; CDP disk cache disabled; localhost production; no network/CPU throttle; DPR0.25 and Q3. Includes response overhead, not an internet benchmark. Default has no new asset requests; preview does not load the 18.6MB Stage2C comparison unless requested.',runs},null,2));
}finally{await b.close();}
