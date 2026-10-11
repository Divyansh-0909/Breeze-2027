import {chromium} from 'playwright';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
const root='reports/stage-1-final-2026-10-11',mode=process.env.CAPTURE_MODE||'baseline';
const world=JSON.parse(await readFile('public/models/gullyverse/blockout.layout.json','utf8'));
const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true});
const captures=[],errors=[];
const save=()=>writeFile(`${root}/${mode}/captures.json`,JSON.stringify({browser:browser.version(),method:'Current production build. Fixed registry cameras enabled only through browser diagnostics for matched composition review; separate public-controls journey below. Mobile aspect is desktop software GPU emulation.',captures,errors},null,2));
async function snap(p,name,note){let data=await p.evaluate(()=>({pose:window.__gullyverse.runtime.cameraPose(innerWidth/innerHeight),walkingPose:{...window.__gullyverse.runtime.pose},snapshot:window.__gullyverse.runtime.getSnapshot(),stats:{...window.__gullyverse.stats},renderer:window.__gullyverse.renderer,viewport:{width:innerWidth,height:innerHeight,dpr:devicePixelRatio}}));await p.screenshot({path:`${root}/${mode}/${name}.png`,scale:'css'});captures.push({file:`${name}.png`,note,...data});await save();console.log(mode,name);}
const wait=p=>p.waitForFunction(()=>['local','error'].includes(window.__gullyverse?.runtime.getSnapshot().phase),null,{timeout:110000});
try{for(const profile of ['desktop','mobile']){
 const ctx=await browser.newContext({viewport:profile==='desktop'?{width:1366,height:900}:{width:390,height:844},deviceScaleFactor:.25,isMobile:profile==='mobile',hasTouch:profile==='mobile'});
 await ctx.route('**/api/**',r=>['GET','HEAD'].includes(r.request().method())?r.continue():r.abort());
 const p=await ctx.newPage();p.on('pageerror',e=>errors.push(e.message));
 await p.goto('http://127.0.0.1:3000/?diagnostics');await p.waitForSelector('[data-phase="landing"]',{timeout:110000});
 const views=profile==='desktop'?['landing','tunnel-near','tunnel-mid','tunnel-first-exit-reveal','exit','scaffold-front','quarry','left-stalls','right-stalls']:['landing','tunnel-mid','exit','scaffold-front','quarry'];
 for(const id of views){await p.evaluate(id=>{const r=window.__gullyverse.runtime;r.inspectionEnabled=true;r.inspect(id);},id);await p.waitForTimeout(500);await p.locator('aside').evaluateAll(a=>a.forEach(x=>x.style.visibility='hidden'));await snap(p,profile+'-'+id,'Fixed existing registry review camera; no production geometry or config modification.');}
 await p.evaluate(()=>{window.__gullyverse.runtime.inspect(null);});await p.getByRole('button',{name:'Enter Gullyverse',exact:true}).click();await wait(p);
 await p.getByRole('button',{name:/^Map/}).click();await p.waitForFunction(()=>window.__gullyverse.runtime.getSnapshot().mapStage==='open',null,{timeout:30000});await snap(p,profile+'-aerial-map','Public Map control; actual same-world camera.');
 await p.getByRole('button',{name:'Aftermovie',exact:true}).click();await wait(p);
 for(const id of ['stage-front','stage-return']){await p.evaluate(id=>{const r=window.__gullyverse.runtime;r.inspectionEnabled=true;r.inspect(id);},id);await p.waitForTimeout(600);await p.locator('aside').evaluateAll(a=>a.forEach(x=>x.style.visibility='hidden'));await snap(p,profile+'-'+id,'Fixed registered stage camera; original stage assets.');}
 if(profile==='desktop'){await p.evaluate(()=>{const r=window.__gullyverse.runtime;r.inspect('stage-return');});await snap(p,'desktop-stage-ground-transition','Same stage-return camera; locked floor/material transition review.');}
 await p.evaluate(()=>window.__gullyverse.runtime.inspect(null));await p.keyboard.down('KeyS');await p.getByRole('dialog',{name:'Where to next?'}).waitFor({timeout:50000});await p.keyboard.up('KeyS');await snap(p,profile+'-boundary-menu','Public walking into rear boundary.');await ctx.close();
}}catch(e){errors.push(String(e.stack));process.exitCode=1;}finally{await save();await browser.close();}
