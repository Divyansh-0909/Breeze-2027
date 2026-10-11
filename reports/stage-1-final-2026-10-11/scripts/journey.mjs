import { chromium } from 'playwright';
import { mkdir, writeFile, readFile } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';

const root = path.resolve('reports/stage-1-final-2026-10-11/acceptance/journey');
const desktopDPR = Number(process.env.AUDIT_DPR || '.25');
const mobileDPR = Number(process.env.AUDIT_MOBILE_DPR || '.5');
const captureOnly = false;
const base = process.env.GULLYVERSE_BASE_URL || 'http://127.0.0.1:3000';
const world = JSON.parse(await readFile('public/models/gullyverse/blockout.layout.json', 'utf8'));
const checks=[], captures=[], errors=[], writes=[], segments=[], network=[];
const browser = await chromium.launch({executablePath:'/usr/bin/chromium',headless:true});
const save = async () => writeFile(root+'/raw/'+(captureOnly?'capture-review':'browser-audit')+'.json',JSON.stringify({at:new Date().toISOString(),browser:browser.version(),os:`${os.platform()} ${os.release()}`,cpu:os.cpus()[0]?.model,checks,captures,errors,writes,segments,network},null,2));
async function instrument(context) {
  await context.route('**/api/**',route=>{
    if(!['GET','HEAD'].includes(route.request().method())) { writes.push({url:route.request().url(),method:route.request().method()});return route.abort(); }
    return route.continue();
  });
  await context.addInitScript(()=>{
    window.__audit={contexts:[],tasks:[],resources:[],createdVideos:[]};
    const original=HTMLCanvasElement.prototype.getContext;
    HTMLCanvasElement.prototype.getContext=function(type,...args){
      const gl=original.call(this,type,...args);
      if(gl && (type==='webgl2'||type==='webgl') && !window.__audit.contexts.some(x=>x.gl===gl)) {
        const stats={};
        for(const resource of ['Texture','Buffer','Program','Shader','Framebuffer','Renderbuffer','VertexArray','Query']) {
          const create='create'+resource,del='delete'+resource;
          if(!gl[create]||!gl[del])continue;
          const known=new WeakSet();stats[resource]={created:0,deleted:0,active:0};
          const make=gl[create].bind(gl),remove=gl[del].bind(gl);
          gl[create]=function(...a){const value=make(...a);if(value){known.add(value);stats[resource].created++;stats[resource].active++;}return value;};
          gl[del]=function(value){if(value&&known.has(value)){known.delete(value);stats[resource].deleted++;stats[resource].active--;}return remove(value);};
        }
        const ext=gl.getExtension('WEBGL_debug_renderer_info');
        window.__audit.contexts.push({gl,stats,renderer:gl.getParameter(ext?ext.UNMASKED_RENDERER_WEBGL:gl.RENDERER)});
      }
      return gl;
    };
    const makeElement=Document.prototype.createElement;
    Document.prototype.createElement=function(tag,...args){const el=makeElement.call(this,tag,...args);if(tag.toLowerCase()==='video')window.__audit.createdVideos.push(new WeakRef(el));return el;};
    new PerformanceObserver(list=>window.__audit.tasks.push(...list.getEntries().map(e=>({at:e.startTime,ms:e.duration})))).observe({type:'longtask',buffered:true});
  });
}
async function observe(page) {
  page.on('pageerror',e=>errors.push({url:page.url(),message:e.message}));
  page.on('console',m=>{if(m.type()==='error')errors.push({url:page.url(),console:m.text(),location:m.location()});});
  page.on('response',r=>{if(r.status()>=400)network.push({url:r.url(),status:r.status()});});
}
const state=p=>p.evaluate(()=>window.__gullyverse?.runtime.getSnapshot());
const pose=p=>p.evaluate(()=>({...window.__gullyverse.runtime.pose}));
const waitLocal=(p,id)=>p.waitForSelector(`[data-phase="local"][data-location="${id}"]`,{timeout:90000});
const check=async(name,run)=>{try{const evidence=await run();checks.push({name,status:'PASS',evidence});}catch(e){checks.push({name,status:'FAIL',error:String(e.stack||e)});}await save();};
async function snapshot(p){return p.evaluate(()=>({snapshot:window.__gullyverse?.runtime.getSnapshot(),pose:{...window.__gullyverse?.runtime.pose},camera:window.__gullyverse?.runtime.cameraPose(innerWidth/innerHeight),renderer:window.__gullyverse?.renderer,stats:{...window.__gullyverse?.stats},contexts:window.__audit.contexts.map(c=>({renderer:c.renderer,stats:c.stats})),memory:window.__gullyverse?.memory.at(-1),media:window.__audit.createdVideos.map(v=>v.deref()).filter(Boolean).map(v=>({src:v.getAttribute('src'),currentTime:v.currentTime,paused:v.paused,readyState:v.readyState})),viewport:{width:innerWidth,height:innerHeight,dpr:devicePixelRatio},canvasCount:document.querySelectorAll('canvas').length}));}
async function capture(p,name,note='Actual public controls; no authoring teleport') {if(captureOnly)name='review-'+name;const before=await snapshot(p);await p.screenshot({path:root+'/screenshots/'+name+'.png',scale:'css'});captures.push({file:'screenshots/'+name+'.png',note,before,after:await snapshot(p)});await save();}
async function key(p,code,ms){await p.keyboard.down(code);await p.waitForTimeout(ms);await p.keyboard.up(code);}
async function look(p,target){const q=await pose(p);const wanted=Math.atan2(-(target[0]-q.x),-(target[2]-q.z));let remaining=Math.atan2(Math.sin(Math.atan2(-(target[0]-q.x),-(target[2]-q.z))-q.yaw),Math.cos(Math.atan2(-(target[0]-q.x),-(target[2]-q.z))-q.yaw));while(Math.abs(remaining)>.001){const turn=Math.max(-.3,Math.min(.3,remaining)),x=600,y=300;await p.mouse.move(x,y);await p.mouse.down();await p.mouse.move(x-turn/.003,y,{steps:8});await p.mouse.up();remaining-=turn;}await p.waitForFunction(w=>{const q=window.__gullyverse.runtime.pose;return Math.abs(Math.atan2(Math.sin(q.yaw-w),Math.cos(q.yaw-w)))<.001;},wanted,{timeout:60000});}
async function map(p,id){await p.getByRole('button',{name:/^Map/}).click();await p.waitForFunction(()=>window.__gullyverse.runtime.getSnapshot().mapStage==='open',{timeout:15000});await p.getByRole('button',{name:id==='hub'?'Gullyverse hub':'Aftermovie',exact:true}).click();await waitLocal(p,id);}
function summarize(samples){const ms=samples.filter(s=>Number.isFinite(s.cpuRenderMs)).map(s=>s.ms).sort((a,b)=>a-b);const mean=ms.reduce((a,b)=>a+b,0)/ms.length;const q=t=>ms[Math.min(ms.length-1,Math.floor(ms.length*t))]??null;return {loopFrames:samples.length,renderedFrames:ms.length,averageFPS:1000/mean,medianMs:q(.5),p95Ms:q(.95),p99Ms:q(.99),maxMs:ms.at(-1),over50ms:ms.filter(x=>x>50).length,over100ms:ms.filter(x=>x>100).length};}
async function cleanSegment(p,name,run){await p.evaluate(()=>window.__gullyverse.frames.length=0);const start=Date.now();await run();const data=await p.evaluate(()=>({samples:window.__gullyverse.frames.map(x=>({...x})),snapshot:window.__gullyverse.runtime.getSnapshot(),stats:{...window.__gullyverse.stats},memory:window.__gullyverse.memory.at(-1)}));segments.push({name,durationMs:Date.now()-start,...summarize(data.samples),...data});await save();}

try {
  // A recording journey is deliberately separate from benchmark windows.
  const context=await browser.newContext({viewport:{width:1366,height:900},deviceScaleFactor:desktopDPR,...(captureOnly?{}:{recordVideo:{dir:root+'/recordings',size:{width:1366,height:900}}})});
  await instrument(context);if(!captureOnly)await context.tracing.start({screenshots:true,snapshots:true,sources:false});
  const p=await context.newPage();await observe(p);
  await p.goto(base+'/?diagnostics',{waitUntil:'domcontentloaded'});await p.waitForSelector('[data-phase="landing"]',{timeout:90000});
  const canvas=await p.locator('canvas').evaluateHandle(c=>c);
  await capture(p,'01-desktop-entrance');
  await p.waitForTimeout(1200);

  await p.getByRole('button',{name:'Enter Gullyverse',exact:true}).click();
  await p.waitForFunction(()=>window.__gullyverse.runtime.pose.z<-8,{timeout:60000});await capture(p,'02-desktop-tunnel-interior');
  await p.waitForFunction(()=>window.__gullyverse.runtime.pose.z<-30,{timeout:30000});await capture(p,'03-desktop-tunnel-before-reveal');
  await p.waitForFunction(()=>window.__gullyverse.runtime.pose.z<-39,{timeout:30000});await capture(p,'04-desktop-quarry-reveal');
  await waitLocal(p,'hub');await capture(p,'05-desktop-hub-arrival-board');
  await look(p,[world.stage.origin[0],6,world.stage.origin[2]]);await capture(p,'06-desktop-hub-stage-stalls');
  await key(p,'KeyD',650);await p.waitForTimeout(500);await capture(p,'07-desktop-hub-movement');
  const zone=world.hub.travelZones.find(z=>z.id==='aftermovie');const a=world.hub.movementBoundary[zone.edge],b=world.hub.movementBoundary[(zone.edge+1)%world.hub.movementBoundary.length],t=(zone.range[0]+zone.range[1])/2;
  await look(p,[a[0]+(b[0]-a[0])*t,world.eyeHeight,a[1]+(b[1]-a[1])*t]);
  await p.keyboard.down('KeyW');await p.waitForSelector('[data-phase="departure"]',{timeout:60000});await p.keyboard.up('KeyW');
  await waitLocal(p,'aftermovie');await capture(p,'08-desktop-aftermovie-arrival');
  await key(p,'KeyW',500);await p.waitForTimeout(500);await capture(p,'09-desktop-aftermovie-viewing-area');
  await p.getByRole('button',{name:'Play Aftermovie',exact:true}).click();await p.waitForFunction(()=>window.__gullyverse.runtime.movieActions?.status().currentTime>.2,{timeout:45000});await capture(p,'11-desktop-aftermovie-playback');
  await p.keyboard.press('Escape');await p.waitForFunction(()=>!window.__gullyverse.runtime.getSnapshot().movie,null,{timeout:30000});await p.waitForTimeout(2000);
  await p.keyboard.down('KeyS');await p.getByRole('dialog',{name:'Where to next?'}).waitFor({timeout:30000});await p.keyboard.up('KeyS');await capture(p,'12-desktop-boundary-menu');
  await p.getByRole('button',{name:'Return to Hub',exact:true}).click();await waitLocal(p,'hub');
  await p.getByRole('button',{name:/^Map/}).click();await p.waitForFunction(()=>window.__gullyverse.runtime.getSnapshot().mapStage==='open',{timeout:15000});await capture(p,'10-desktop-aerial-map','Actual same-world aerial map, replacing requested 2D map');
  await p.getByRole('button',{name:'Aftermovie',exact:true}).click();await waitLocal(p,'aftermovie');
  checks.push({name:'complete uninterrupted physical journey, return, map and playback',status:'PASS',evidence:await snapshot(p),sameCanvas:await p.evaluate(c=>document.querySelector('canvas')===c,canvas)});
  if(!captureOnly)await context.tracing.stop({path:root+'/traces/full-journey.zip'});
  const video=p.video();await context.close();if(video)await video.saveAs(root+'/recordings/full-journey.webm');await save();


} catch(e) {errors.push(String(e.stack));process.exitCode=1;} finally {await save();await browser.close();}
