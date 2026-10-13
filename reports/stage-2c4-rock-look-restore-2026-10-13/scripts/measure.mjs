import{writeFile}from'node:fs/promises';import{launch,context,view,unfix,details,ready,root}from'./wall-browser-common.mjs';
const label=process.argv[2]||'before',b=await launch(),c=await context(b,{deviceScaleFactor:.5}),p=await c.newPage(),windows=[],errors=[];
async function sample(name){const before=await details(p),start=await p.evaluate(()=>performance.now());await p.waitForTimeout(10000);const end=await p.evaluate(()=>performance.now()),frames=await p.evaluate(({start,end})=>window.__gullyverse.timeline.filter(f=>f.at>=start&&f.at<=end),{start,end}),dt=frames.map(f=>f.ms).sort((a,b)=>a-b),q=k=>dt[Math.floor((dt.length-1)*k)];windows.push({name,start,end,frames,FPS:frames.length*1000/(end-start),p50:q(.5),p95:q(.95),p99:q(.99),max:dt.at(-1),stallsOver100ms:dt.filter(x=>x>100).length,before,after:await details(p)});console.log(name,windows.at(-1).FPS);}
try{
 await p.goto('http://127.0.0.1:3000/?arrival=hub&diagnostics'+'&quarryReview=excavation'+(label==='before'?'&quarryMaterial=limestone':''));
 await p.waitForFunction(()=>window.__gullyverse?.runtime);await p.evaluate(()=>window.__gullyverse.runtime.setQuality(3));await ready(p);
 for(const[name,pos,target]of[['hub',[0,1.72,-51],[0,10,-110]],['left-wall',[-16,1.72,-62],[-42,12,-77]]]){await view(p,pos,target,{fixed:true,quality:3});await sample(name);}
 await unfix(p);await p.evaluate(()=>{const r=window.__gullyverse.runtime;r.pose={x:0,y:1.72,z:-51,yaw:0,pitch:.1};r.setQuality(3);});
 const start=Date.now();await p.getByRole('button',{name:/^Map/}).click();await p.waitForFunction(()=>window.__gullyverse.runtime.getSnapshot().mapStage==='open',null,{timeout:60000});const mapAscentMs=Date.now()-start;
 await sample('aerial-map');
 await p.getByRole('button',{name:'Aftermovie',exact:true}).click();await p.waitForFunction(()=>window.__gullyverse.runtime.getSnapshot().phase==='local'&&window.__gullyverse.runtime.getSnapshot().scene==='aftermovie'&&!window.__wallPreview.state.busy,null,{timeout:90000});
 await view(p,[-10.5,1.72,-108.3],[0,10,-42],{fixed:true,quality:3});await sample('stage-looking-back');
 await writeFile(root+'/raw/'+label+'-performance.json',JSON.stringify({status:'PASS',label,method:'Same production build and software renderer; matched1366x900 cameras, DPR0.5 quality3,10-second windows. No artificial throttling, no recording, no competing authoring/browser workload. Baseline means the explicit previous Grey limestone material on identical connected geometry in this build.',mapAscentMs,windows,errors},null,2));
}catch(e){errors.push(String(e.stack));process.exitCode=1;await writeFile(root+'/raw/'+label+'-performance.json',JSON.stringify({status:'FAIL',windows,errors},null,2));}finally{await c.close();await b.close();}
