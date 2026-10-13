import {launch,context,details,root} from './wall-browser-common.mjs';
import {writeFile} from 'node:fs/promises';
const browser=await launch(),runs=[];
try {
  for (const [label,query] of [['approved-single-pilot','&wallPreview=limestone'],['full-rollout','']]) {
    const c=await context(browser,{deviceScaleFactor:.25}),page=await c.newPage();
    const cdp=await c.newCDPSession(page),requests=new Map();
    await cdp.send('Network.enable');await cdp.send('Network.setCacheDisabled',{cacheDisabled:true});
    cdp.on('Network.requestWillBeSent',e=>requests.set(e.requestId,{url:e.request.url}));
    cdp.on('Network.responseReceived',e=>Object.assign(requests.get(e.requestId)||{}, {status:e.response.status,fromDiskCache:!!e.response.fromDiskCache,mimeType:e.response.mimeType}));
    cdp.on('Network.loadingFinished',e=>Object.assign(requests.get(e.requestId)||{}, {encodedBytes:e.encodedDataLength}));
    await page.goto('http://127.0.0.1:3000/?diagnostics'+query);
    await page.waitForFunction(()=>window.__gullyverse?.runtime);
    await page.evaluate(()=>window.__gullyverse.runtime.setQuality(3));
    await page.waitForFunction(()=>window.__gullyverse.runtime.getSnapshot().phase==='landing'&&!window.__wallPreview.state.busy,null,{timeout:90000});
    const data=await page.evaluate(()=>({navigation:performance.getEntriesByType('navigation').map(x=>x.toJSON()),resources:performance.getEntriesByType('resource').map(x=>x.toJSON()),at:performance.now()}));
    const entries=[...requests.values()].filter(x=>x.url.startsWith('http://127.0.0.1:3000'));
    const row={label,method:'New production browser context, CDP disk cache disabled, no artificial network or CPU throttling. Localhost SwiftShader, DPR0.25 quality3; fresh intentional-entry landing, before any entry activation. API mutation requests blocked.',CDPLocalEncodedBytes:entries.reduce((n,e)=>n+(e.encodedBytes||0),0),requests:entries,...data,details:await details(page)};
    runs.push(row);console.log(label,row.CDPLocalEncodedBytes,row.at);await c.close();
  }
  await writeFile(root+'/raw/network.json',JSON.stringify({status:'PASS',runs,caution:'CDP encoded counts include response overhead. Localhost transfer/readiness is not an internet or physical-device benchmark.'},null,2));
} finally {await browser.close();}
