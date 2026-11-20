import {chromium} from '/workspace/Breeze-2027/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';import path from 'node:path';import{fileURLToPath}from'node:url';
const R=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),tour=JSON.parse(await fs.readFile(path.join(R,'tour-path.json'),'utf8'));
const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-background-timer-throttling']});
const page=await browser.newPage({viewport:{width:1280,height:720},deviceScaleFactor:1});const errors=[];page.on('pageerror',e=>errors.push(String(e)));await page.goto('http://127.0.0.1:8771/');await page.waitForFunction(()=>window.tour?.ready()||window.pilotError,{timeout:180000});if(await page.evaluate(()=>window.pilotError))throw Error(await page.evaluate(()=>window.pilotError));await page.evaluate(()=>{window.pilot.pause(true);window.__comparison.setBenchmarkMode(true);});
const frames=[];
for(const shot of tour.shots){const u=.5,lerp=(a,b)=>a.map((v,i)=>v+(b[i]-v)*u),position=lerp(shot.a,shot.b),target=lerp(shot.ta,shot.tb),t=performance.now();
 const stats=await page.evaluate(({position,target,shot,total})=>{document.getElementById('chapter').textContent=shot.title;document.getElementById('progress').style.width=(shot.start+.5*shot.seconds)/total*100+'%';return window.tour.pose(position,target,shot.lens,shot.start+.5*shot.seconds);},{position,target,shot,total:tour.duration});
 const file=path.join(R,'renders',shot.id+'.jpg');await page.screenshot({path:file,type:'jpeg',quality:92});frames.push({id:shot.id,file:path.relative(R,file),seconds:(performance.now()-t)/1000,...stats});console.log('CAMERA',shot.id,frames.at(-1).seconds.toFixed(2));
}
const info=await page.evaluate(()=>window.tour.stats());await fs.writeFile(path.join(R,'evidence/camera-check.json'),JSON.stringify({status:errors.length?'FAIL':'PASS',viewport:[1280,720],pixelRatio:1,renderer:info.renderer,stats:info,errors,frames},null,2));await browser.close();
