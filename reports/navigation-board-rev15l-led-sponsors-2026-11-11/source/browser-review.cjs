const {chromium}=require('/workspace/Breeze-2027/node_modules/playwright');
const fs=require('node:fs/promises'),path=require('node:path');
const O=path.resolve(__dirname,'..');
(async()=>{
 const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});
 try{
  const context=await browser.newContext({viewport:{width:1600,height:1100},deviceScaleFactor:1,recordVideo:{dir:path.join(O,'review/video'),size:{width:1600,height:1100}}});
  const page=await context.newPage(),errors=[],failed=[];page.on('pageerror',e=>errors.push(String(e)));page.on('console',m=>{if(m.type()==='error')errors.push(m.text())});page.on('requestfailed',r=>failed.push(r.url()));
  await page.goto('http://127.0.0.1:8776/',{waitUntil:'networkidle'});await page.waitForFunction(()=>window.navigationPreview?.stats().ready,null,{timeout:60000});
  await page.evaluate(()=>{window.navigationPreview.pause(true);window.navigationPreview.setOffset(0)});
  const draw=()=>page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));await draw();
  await page.screenshot({path:path.join(O,'renders/browser-whole-board.png')});
  await page.getByRole('button',{name:'LED close-up',exact:true}).click();await draw();await page.screenshot({path:path.join(O,'renders/browser-led-close.png')});
  const start=await page.locator('canvas').screenshot();
  const stats=await page.evaluate(()=>window.navigationPreview.stats());
  if(stats.modelSceneCount!==1)throw Error('Export contains historical scenes');
  if(!(stats.layout.GULLYVERSE.minY>stats.layout.AFTERMOVIE.maxY && stats.layout.AFTERMOVIE.minY>stats.layout['EVENTS  <'].maxY && stats.layout['SCHEDULE'].minY>stats.layout['PAST SPONSORS'].maxY))throw Error('Live sign order differs from Blender layout');
  await page.evaluate(p=>window.navigationPreview.setOffset(p),stats.periodCells);await draw();const wrapped=await page.locator('canvas').screenshot();
  if(!start.equals(wrapped))throw Error('Loop start/end render mismatch');
  await page.evaluate(p=>{window.navigationPreview.setOffset(p-1);window.navigationPreview.advance(1/30)},stats.periodCells);await draw();
  const boundary=await page.evaluate(()=>window.navigationPreview.stats());if(Math.abs(boundary.offsetCells)>1e-5)throw Error('Loop boundary has a gap');
  const count=await page.locator('#sponsor option').count();if(count!==62)throw Error('Missing sponsor options');
  await page.locator('#sponsor').selectOption({index:61});await draw();await page.evaluate(()=>window.navigationPreview.pause(false));const before=await page.evaluate(()=>window.navigationPreview.stats().offsetCells);await page.waitForFunction(v=>window.navigationPreview.stats().offsetCells!==v,before,{timeout:10000});
  await page.waitForTimeout(7000);await page.locator('#sponsor').selectOption({index:0});await page.waitForTimeout(7000);await page.getByRole('button',{name:'Whole board',exact:true}).click();await page.waitForTimeout(2500);
  await page.setViewportSize({width:390,height:844});await draw();await page.screenshot({path:path.join(O,'renders/browser-mobile.png')});
  const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth);const video=page.video();await context.close();
  const videoPath=await video.path();await fs.copyFile(videoPath,path.join(O,'review/Navigation-Board-LED-Preview.webm'));
  const result={status:errors.length||failed.length||overflow?'FAIL':'PASS',logos:count,loopStartEndPixelIdentical:true,boundaryOffsetCells:boundary.offsetCells,scrollAdvances:true,wholeAndCloseViews:true,mobileOverflow:overflow,errors,failed,renderer:'Chromium SwiftShader; private board review'};
  await fs.writeFile(path.join(O,'evidence/browser.json'),JSON.stringify(result,null,2));console.log(JSON.stringify(result));if(result.status!=='PASS')throw Error('Browser checks failed');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1});
