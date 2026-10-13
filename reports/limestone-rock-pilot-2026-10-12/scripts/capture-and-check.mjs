import {chromium} from 'playwright';import {writeFile} from 'node:fs/promises';import assert from 'node:assert/strict';import {instrument} from './audit-common.mjs';
const root='reports/limestone-rock-pilot-2026-10-12',browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true}),captures=[],windows=[],cycles=[],errors=[],requests=[];let ownership={};
async function open(viewport,dpr){const ctx=await browser.newContext({viewport,deviceScaleFactor:dpr});await instrument(ctx);const p=await ctx.newPage();p.on('pageerror',e=>errors.push(String(e)));p.on('response',r=>{if(r.status()>=400&&!r.url().endsWith('favicon.ico'))errors.push('HTTP '+r.status()+' '+r.url());});p.on('request',r=>requests.push({url:r.url(),at:Date.now()}));await p.goto('http://127.0.0.1:3002');await p.waitForFunction(()=>window.__pilot?.diagnostic.ready,{},{timeout:60000});return{ctx,p};}
async function cfg(p,o){await p.evaluate(o=>window.__pilot.configure(o),o);await p.waitForFunction(o=>window.__pilot.diagnostic.ready&&(!o.mode||window.__pilot.snapshot().mode===o.mode)&&(!Object.hasOwn(o,'lod')||window.__pilot.snapshot().lod===o.lod)&&(!Object.hasOwn(o,'context')||window.__pilot.snapshot().context===o.context),o,{timeout:60000});await p.waitForTimeout(200);}
async function snap(p){return await p.evaluate(()=>{const d=window.__pilot.diagnostic,g=d.renderer;return{current:d.current,collision:d.collision,assetBounds:d.assetBounds,renderer:g.getContext().getParameter(g.getContext().getExtension('WEBGL_debug_renderer_info').UNMASKED_RENDERER_WEBGL),settings:{toneMapping:g.toneMapping,exposure:g.toneMappingExposure,outputColorSpace:g.outputColorSpace,shadowMapEnabled:g.shadowMap.enabled},contexts:window.__audit.contexts.map(c=>({stats:c.stats,renderer:c.renderer}))};});}
async function shot(p,name,o){await cfg(p,o);const before=await snap(p);const file='screenshots/'+name+'.png';await p.screenshot({path:root+'/'+file,scale:'css'});captures.push({file,method:'Actual Chromium capture; isolated comparison; current Hub global lights; no production change',before,after:await snap(p)});await writeFile(root+'/raw/captures.json',JSON.stringify({browser:browser.version(),physicalDevice:false,captures,errors},null,2));console.log('Captured',name);}
async function sample(p,name,o){await cfg(p,o);const start=await p.evaluate(()=>performance.now());await p.waitForTimeout(8000);const end=await p.evaluate(()=>performance.now());const frames=await p.evaluate(t=>window.__pilot.diagnostic.frames.filter(f=>f.at>=t),start),dt=frames.map(f=>f.ms).sort((a,b)=>a-b),q=t=>dt[Math.floor((dt.length-1)*t)];windows.push({name,elapsedMs:end-start,FPS:frames.length*1000/(end-start),p50:q(.5),p95:q(.95),p99:q(.99),max:dt.at(-1),state:await snap(p),frames});console.log(name,windows.at(-1).FPS);}
try{
 let {ctx,p}=await open({width:1366,height:900},1);
 await shot(p,'01-original-pilot-medium',{mode:'original',lod:0,view:'medium',context:false});
 await shot(p,'02-limestone-medium',{mode:'pilot',lod:0,view:'medium',context:false});
 await shot(p,'03-limestone-material-close',{view:'close'});
 await shot(p,'04-limestone-angle-left',{view:'left'});
 await shot(p,'05-limestone-angle-right',{view:'right'});
 await shot(p,'06-limestone-long-lod2',{view:'long',lod:2});
 await shot(p,'07-original-pilot-quarry-context',{mode:'original',lod:0,view:'medium',context:true});
 await shot(p,'08-limestone-quarry-context',{mode:'pilot',lod:0,view:'medium',context:true});
 await ctx.close();({ctx,p}=await open({width:390,height:844},1));
 await shot(p,'09-limestone-mobile-aspect',{mode:'pilot',lod:1,view:'mobile',context:false});
 await shot(p,'10-limestone-mobile-close',{lod:0,view:'close'});
 await ctx.close();({ctx,p}=await open({width:1366,height:900},.5));
 await sample(p,'original-stone-medium',{mode:'original',lod:0,view:'medium',context:false});
 await sample(p,'limestone-medium',{mode:'pilot',lod:0,view:'medium',context:false});
 // Warm all six visual meshes. Shared caches persist intentionally until explicit retirement.
 for(const mode of ['original','pilot'])for(const lod of [0,1,2])await cfg(p,{mode,lod});
 for(let i=0;i<10;i++){await cfg(p,{mode:'blank'});await cfg(p,{mode:'pilot',lod:i%3});const s=await snap(p);assert.equal(s.current.stats.triangles,[43880,21704,14084][i%3]);assert.ok(s.collision.hit);cycles.push({cycle:i+1,settled:s});}
 const sig=cycles.map(c=>JSON.stringify([c.settled.current.stats.textures,c.settled.current.stats.geometries,c.settled.current.stats.programs]));assert.equal(new Set(sig).size,1,'Settled caches must plateau');
 await cfg(p,{mode:'blank'});const before=await snap(p);await p.evaluate(()=>window.__pilot.disposePilotCache());await p.waitForTimeout(600);const after=await snap(p);assert.equal(after.current.stats.textures,1);assert.equal(after.current.stats.geometries,1);
 const detail=await p.evaluate(()=>({preparation:window.__pilot.diagnostic.preparation,parse:window.__pilot.diagnostic.parse,cacheRetired:window.__pilot.diagnostic.cacheRetired,resources:performance.getEntriesByType('resource').map(r=>({name:r.name,duration:r.duration,transferSize:r.transferSize,decodedBodySize:r.decodedBodySize}))}));ownership={before,after,detail,status:'PASS'};assert.equal(errors.length,0);await ctx.close();
}catch(e){errors.push(String(e.stack));process.exitCode=1;}finally{await writeFile(root+'/raw/preview-verification.json',JSON.stringify({browser:browser.version(),physicalGPU:false,method:'October12 SwiftShader, sequential actual browser captures at DPR1; two eight-second matched-camera diagnostic windows at DPR0.5, no throttling; ten repeated limestone mounts after both isolated caches warm; no production benchmark claim',windows,cycles,ownership,errors,requests,status:errors.length?'FAIL':'PASS'},null,2));await browser.close();console.log('Verification',errors.length?'FAIL':'PASS');}
