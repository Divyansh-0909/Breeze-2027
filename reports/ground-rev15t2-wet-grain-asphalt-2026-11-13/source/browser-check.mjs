import { chromium } from 'playwright';
import fs from 'node:fs';
import path from 'node:path';
import {spawn} from 'node:child_process';
const server=spawn('python',['-m','http.server','8808','--bind','127.0.0.1'],{cwd:process.cwd(),stdio:'ignore'});
for(let i=0;i<80;i++){try{const r=await fetch('http://127.0.0.1:8808/');if(r.ok)break;}catch{}await new Promise(resolve=>setTimeout(resolve,125));}
try {
const root=path.resolve('reports/ground-rev15t2-wet-grain-asphalt-2026-11-13');const browser=await chromium.launch({headless:true,executablePath:'/usr/bin/chromium',args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader']});const page=await browser.newPage({viewport:{width:1280,height:800},deviceScaleFactor:1});const errors=[];page.on('pageerror',e=>errors.push(String(e)));page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
await page.goto('http://127.0.0.1:8808/reports/ground-rev15t2-wet-grain-asphalt-2026-11-13/viewer/',{waitUntil:'networkidle',timeout:90000});await page.waitForFunction(()=>window.roadReady,{timeout:90000});const views=[];
for(const name of ['lane','cypher','overview']){const result=await page.evaluate(n=>window.roadReview.show(n),name);if(result.glError!==0||result.normalChannels.length!==8||result.normalChannels.some(n=>n!==1))throw new Error('Browser validation failed');await page.screenshot({path:path.join(root,'renders','browser-'+name+'.jpg'),type:'jpeg',quality:88});views.push(result);}
if(errors.length)throw new Error(errors.join('\n'));const result={status:'PASS',scope:'Separate ground asset viewer; no full-world production integration or performance claim',views,consoleErrors:errors,canvasCount:await page.locator('canvas').count(),viewport:[1280,800],movementRouteRaySamples:views[0].raySamples.length};if(result.canvasCount!==1)throw new Error('Expected one canvas');fs.writeFileSync(path.join(root,'evidence/browser-check.json'),JSON.stringify(result,null,2)+'\n');await browser.close();console.log(JSON.stringify({status:result.status,views:views.length,consoleErrors:0,triangles:views[0].triangles,drawCalls:views[0].drawCalls}));

} finally { server.kill('SIGTERM'); }
