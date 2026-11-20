import{chromium}from'/workspace/Breeze-2027/node_modules/playwright/index.mjs';
import fs from'node:fs/promises';import path from'node:path';import{fileURLToPath}from'node:url';import{spawn}from'node:child_process';import{once}from'node:events';
const R=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),tour=JSON.parse(await fs.readFile(path.join(R,'tour-path.json'),'utf8')),fps=tour.sourceRenderFPS;
const video=path.join(R,'video/Night-Environment-Tour-Source10fps.mp4'),log=await fs.open(path.join(R,'evidence/source-video-encode.log'),'w');
const encoder=spawn('ffmpeg',['-hide_banner','-loglevel','warning','-y','-f','image2pipe','-vcodec','mjpeg','-framerate',String(fps),'-i','pipe:0','-an','-c:v','libx264','-preset','veryfast','-crf','18','-threads','1','-pix_fmt','yuv420p','-movflags','+faststart',video],{stdio:['pipe','ignore',log.fd]});
const encoderDone=new Promise((resolve,reject)=>{encoder.once('error',reject);encoder.once('close',code=>code===0?resolve():reject(Error('ffmpeg exit '+code)));});
const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-background-timer-throttling']});
const page=await browser.newPage({viewport:{width:1280,height:720},deviceScaleFactor:1});const errors=[];page.on('pageerror',e=>errors.push(String(e)));const begun=Date.now();let frame=0;const shots=[];
try{
 await page.goto('http://127.0.0.1:8771/');await page.waitForFunction(()=>window.tour?.ready()||window.pilotError,null,{timeout:180000});if(await page.evaluate(()=>window.pilotError))throw Error(await page.evaluate(()=>window.pilotError));
 await page.evaluate(r=>{window.pilot.pause(true);window.__comparison.setBenchmarkMode(true);window.tour.pixelRatio(r);},tour.internalRenderPixelRatio);
 for(const shot of tour.shots){
  const count=shot.seconds*fps,startFrame=frame,started=Date.now();let midStats;
  for(let i=0;i<count;i++){
   const u=i/Math.max(1,count-1),ease=u*u*(3-2*u),lerp=(a,b)=>a.map((v,k)=>v+(b[k]-v)*ease),position=lerp(shot.a,shot.b),target=lerp(shot.ta,shot.tb),seconds=shot.start+i/fps;
   const stats=await page.evaluate(({position,target,shot,seconds,total})=>{document.getElementById('chapter').textContent=shot.title;document.getElementById('progress').style.width=(seconds/total*100)+'%';return window.tour.pose(position,target,shot.lens,seconds);},{position,target,shot,seconds,total:tour.duration});
   const buffer=await page.screenshot({type:'jpeg',quality:91});if(!encoder.stdin.write(buffer))await once(encoder.stdin,'drain');
   if(i===Math.floor(count/2)){await fs.writeFile(path.join(R,'renders',shot.id+'.jpg'),buffer);midStats=stats;}
   frame++;
   if(frame%10===0)await fs.writeFile(path.join(R,'evidence/recording-progress.json'),JSON.stringify({phase:'recording',frame,totalFrames:tour.duration*fps,shot:shot.id,filmSeconds:seconds,wallSeconds:(Date.now()-begun)/1000}));
  }
  const result={id:shot.id,title:shot.title,start:shot.start,end:shot.end,sourceFrames:count,startFrame,wallSeconds:(Date.now()-started)/1000,midStats};shots.push(result);console.log('RECORDED',shot.id,frame+'/'+tour.duration*fps,result.wallSeconds.toFixed(1)+'s');
  await fs.writeFile(path.join(R,'evidence/recorded-shots.json'),JSON.stringify(shots,null,2));
 }
 encoder.stdin.end();await encoderDone;
 const info=await page.evaluate(()=>window.tour.stats());if(errors.length)throw Error(errors.join('\n'));
 await fs.writeFile(path.join(R,'evidence/recording.json'),JSON.stringify({status:'PASS',sourceRenderFPS:fps,deliveryFPS:tour.outputFPS,frames:frame,duration:tour.duration,resolution:[1280,720],internalRenderPixelRatio:tour.internalRenderPixelRatio,sourceVideo:path.relative(R,video),wallSeconds:(Date.now()-begun)/1000,renderer:info.renderer,stats:info,errors,shots,scope:'Deterministic camera rendering, static source crowd, LED advanced by film time. Output interpolation is a delivery effect, not website performance evidence.'},null,2));
 console.log('SOURCE_VIDEO_COMPLETE',frame,video);
}catch(e){encoder.stdin.destroy();encoder.kill('SIGTERM');throw e;}finally{await browser.close();await log.close();}
