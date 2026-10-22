import {launch,context,view} from '../../stage-2c5-1-rock-realism-refinement-2026-10-14/scripts/wall-browser-common.mjs';
import {writeFile} from 'node:fs/promises';
const browser=await launch(),c=await context(browser,{viewport:{width:1000,height:750},deviceScaleFactor:1}),p=await c.newPage(),errors=[];
p.on('pageerror',e=>errors.push(String(e.stack)));p.on('console',m=>{if(m.type()==='error')errors.push(m.text().slice(0,200));});
try{
 await p.goto('http://127.0.0.1:3000/?diagnostics&quarryReview=geology-fidelity&entranceReview=material-study&caveMaterial=control');
 await p.waitForFunction(()=>window.__gullyverse?.runtime);await p.evaluate(()=>window.__gullyverse.runtime.setQuality(3));
 await p.waitForFunction(()=>window.__wallPreview?.entranceReady&&!window.__wallPreview.state.busy,null,{timeout:90000});
 await p.waitForSelector('[data-phase="landing"]',{timeout:90000});
 console.log('BASE',await p.evaluate(()=>window.__wallPreview.studyDiagnostics()));
 await view(p,[-6,1.72,-22],[-9.5,2.5,-24],{fixed:true,quality:0});await p.screenshot({path:'reports/cave-material-study-2026-10-22/screenshots/probe-control.png'});
 console.log('RENDER',await p.evaluate(()=>({suspended:window.__gullyverse.runtime.suspended,opacity:window.__gullyverse.runtime.opacity,reveal:window.__gullyverse.runtime.revealOpacity,stats:window.__gullyverse.stats,frame:window.__gullyverse.currentFrame,curtains:[...document.querySelectorAll('div[class*=curtain]')].map(e=>({style:e.getAttribute('style'),css:getComputedStyle(e).opacity})),rootParent:window.__wallPreview.entranceRoot?.deref()?.parent?.name,rootUUID:window.__wallPreview.entranceRoot?.deref()?.uuid,canvases:document.querySelectorAll('canvas').length})));
 await p.locator('canvas').screenshot({path:'reports/cave-material-study-2026-10-22/screenshots/probe-canvas.png'});
 await p.evaluate(()=>{window.__gullyverse.runtime.setQuality(3);window.__wallPreview.setStudySelection('rock_01',1);});
 await p.waitForFunction(()=>window.__wallPreview.studyDiagnostics().active==='rock_01'&&!window.__wallPreview.state.busy,null,{timeout:90000});
 console.log('SELECTED',await p.evaluate(()=>window.__wallPreview.studyDiagnostics()));
 await view(p,[-6,1.72,-22],[-9.5,2.5,-24],{fixed:true,quality:0});await p.screenshot({path:'reports/cave-material-study-2026-10-22/screenshots/probe-rock01.png'});
}catch(e){errors.push(String(e.stack));console.log('STATE',await p.evaluate(()=>({state:window.__wallPreview?.state,study:window.__wallPreview?.studyDiagnostics?.(),cave:window.__wallPreview?.entranceDiagnostics?.(),runtime:window.__gullyverse?.runtime?.getSnapshot(),trace:window.__wallPreview?.trace.slice(-12)})));process.exitCode=1;}
finally{await writeFile('reports/cave-material-study-2026-10-22/raw/probe.json',JSON.stringify({errors},null,2));console.log('ERRORS',errors);await c.close();await browser.close();}
