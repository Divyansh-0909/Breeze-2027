const {chromium}=require('/workspace/Breeze-2027/node_modules/playwright');
const fs=require('node:fs/promises'),path=require('node:path'),{spawnSync}=require('node:child_process');
const O=path.resolve(__dirname,'..');
(async()=>{
 const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});
 try{
  const context=await browser.newContext({viewport:{width:1600,height:1100},deviceScaleFactor:1,recordVideo:{dir:path.join(O,'review/video'),size:{width:1600,height:1100}}});const epoch=Date.now(),page=await context.newPage();
  await page.goto('http://127.0.0.1:8777/',{waitUntil:'networkidle'});await page.waitForFunction(()=>window.navigationPreview?.stats().ready,null,{timeout:60000});
  await page.evaluate(()=>{const p=window.navigationPreview;p.pause(true);p.view('close');p.setOffset(p.stats().periodCells-60)});
  await page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
  const start=(Date.now()-epoch)/1000;await page.evaluate(()=>window.navigationPreview.pause(false));await page.waitForTimeout(8000);const end=(Date.now()-epoch)/1000;const state=await page.evaluate(()=>window.navigationPreview.stats());const video=page.video();await context.close();const file=await video.path();
  const output=path.join(O,'review/Navigation-Board-LED-Preview.mp4');
  const result=spawnSync('/usr/bin/ffmpeg',['-y','-ss',String(start+.1),'-i',file,'-t',String(Math.min(7.7,end-start-.1)),'-vf','scale=1280:880','-c:v','libx264','-threads','2','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart','-an',output],{encoding:'utf8'});if(result.status!==0)throw Error(result.stderr);
  await fs.writeFile(path.join(O,'evidence/video.json'),JSON.stringify({status:'PASS',file:'review/Navigation-Board-LED-Preview.mp4',method:'Actual 3D browser playback, continuous motion across the last-to-first logo boundary',startOffsetCells:state.periodCells-60,endOffsetCells:state.offsetCells,logos:state.logoCount,captureSeconds:end-start},null,2));console.log('DEMO VIDEO COMPLETE');
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
