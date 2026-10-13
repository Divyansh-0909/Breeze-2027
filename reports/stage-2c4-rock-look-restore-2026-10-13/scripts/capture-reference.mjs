import {chromium} from 'playwright';import{writeFile}from'node:fs/promises';
const root='reports/stage-2c4-rock-look-restore-2026-10-13',browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true});
const page=await browser.newPage({viewport:{width:1280,height:843},deviceScaleFactor:1}),errors=[];
page.on('pageerror',e=>errors.push(e.message));
try{
 await page.goto('http://127.0.0.1:3001');
 await page.waitForFunction(()=>window.__pilot?.diagnostic.ready,null,{timeout:60000});
 await page.evaluate(()=>window.__pilot.configure({mode:'pilot',lod:0,view:'medium',context:false}));
 await page.waitForFunction(()=>window.__pilot.diagnostic.ready&&window.__pilot.snapshot().mode==='pilot',null,{timeout:60000});
 await page.waitForTimeout(600);
 await page.screenshot({path:root+'/reference/original-stage2a-rock-pilot.png'});
 const details=await page.evaluate(()=>({current:window.__pilot.diagnostic.current,exposure:window.__pilot.diagnostic.renderer.toneMappingExposure,toneMapping:window.__pilot.diagnostic.renderer.toneMapping}));
 await writeFile(root+'/raw/reference-capture.json',JSON.stringify({status:errors.length?'FAIL':'PASS',browser:browser.version(),viewport:{width:1280,height:843,dpr:1},details,errors,method:'Fresh actual browser rendering of the retained original Stage2A preview bundle and original unmodified GLB, LOD0/medium/FOV58. Not generated art.'},null,2));
 if(errors.length)process.exitCode=1;
}finally{await browser.close();}
