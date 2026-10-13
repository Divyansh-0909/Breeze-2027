import{chromium}from'playwright';import{writeFile,mkdir}from'node:fs/promises';
const root='reports/stage-2c2-limestone-excavation-2026-10-13',b=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true});
const p=await b.newPage({viewport:{width:1366,height:900},deviceScaleFactor:1}),errors=[];p.on('pageerror',e=>errors.push(e.message));
try{
 await mkdir(root+'/reference',{recursive:true});await p.goto('http://127.0.0.1:3003');
 await p.waitForFunction(()=>window.__pilot?.diagnostic.ready,null,{timeout:60000});
 await p.evaluate(()=>window.__pilot.configure({mode:'pilot',lod:0,view:'medium',context:false}));
 await p.waitForFunction(()=>window.__pilot.diagnostic.ready&&window.__pilot.snapshot().mode==='pilot',null,{timeout:60000});
 await p.screenshot({path:root+'/reference/approved-grey-limestone-lod0.png'});
 const details=await p.evaluate(()=>({current:window.__pilot.diagnostic.current,exposure:window.__pilot.diagnostic.renderer.toneMappingExposure,toneMapping:window.__pilot.diagnostic.renderer.toneMapping}));
 await writeFile(root+'/raw/reference-capture.json',JSON.stringify({status:errors.length?'FAIL':'PASS',browser:b.version(),details,errors,method:'Fresh actual browser capture of unchanged Grey limestone pilot bundle and exact original GLB; not synthetic art.'},null,2));
}finally{await b.close();}
