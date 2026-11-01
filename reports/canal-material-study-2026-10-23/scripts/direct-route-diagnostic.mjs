import {chromium} from 'playwright';
import {writeFile} from 'node:fs/promises';
const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true}),rows=[];
for(const [label,query] of [['unchanged-default',''],['private-control','&entranceReview=canal-material&caveMaterial=control'],['private-cracked','&entranceReview=canal-material&caveMaterial=cracked_concrete_wall']]){
 const ctx=await browser.newContext({viewport:{width:1366,height:900},deviceScaleFactor:.25});const p=await ctx.newPage();
 const errors=[];p.on('pageerror',e=>errors.push(e.message));
 try{for(const route of ['/?arrival=hub&diagnostics&quarryReview=geology-fidelity'+query,'/aftermovie?diagnostics&quarryReview=geology-fidelity'+query]){
 const t=Date.now();await p.goto('http://127.0.0.1:3000'+route);await p.waitForSelector('[data-phase="local"],[data-phase="error"]',{timeout:100000});
 const d=await p.evaluate(()=>({state:window.__gullyverse?.runtime.getSnapshot()??{phase:document.querySelector("[data-phase]")?.getAttribute("data-phase"),error:document.querySelector("[data-phase=error]")?.innerText},phases:window.__gullyverse?.phases,stats:window.__gullyverse?.stats,trace:window.__wallPreview?.trace?.slice(-15),study:window.__wallPreview?.studyDiagnostics?.(),resources:performance.getEntriesByType('resource').filter(r=>/models\/|canal-material/.test(r.name)).map(r=>({name:r.name.split('3000')[1],duration:r.duration,bytes:r.transferSize}))}));
 rows.push({label,route,ms:Date.now()-t,...d,errors});console.log(label,route.startsWith('/aftermovie')?'direct-stage':'direct-hub',d.state.phase,d.state.error);await writeFile('reports/canal-material-study-2026-10-23/raw/direct-route-diagnostic.json',JSON.stringify({rows,settings:'Unchanged automatic quality/deadline; DPR0.25 software diagnostic; no deadline bypass.'},null,2));
 }}catch(e){rows.push({label,error:String(e.stack),errors});}finally{await ctx.close();}
}
await browser.close();await writeFile('reports/canal-material-study-2026-10-23/raw/direct-route-diagnostic.json',JSON.stringify({rows,settings:'Unchanged automatic quality/deadline; DPR0.25 software diagnostic; no deadline bypass.'},null,2));
