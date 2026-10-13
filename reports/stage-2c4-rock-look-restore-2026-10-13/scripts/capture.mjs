import {writeFile,mkdir} from 'node:fs/promises';
import {launch,context,ready,view,unfix,details,root} from './wall-browser-common.mjs';
const label=process.argv[2]||'before',b=await launch(),captures=[],errors=[];
let c,p;
const frames=[
 ['01-hub-center',[0,1.72,-51],[0,10,-110]],
 ['02-stage-facing',[8,1.72,-93],[-12,10,-146]],
 ['03-left-wall',[-16,1.72,-62],[-42,12,-77]],
 ['04-right-wall',[16,1.72,-65],[44,12,-88]],
 ['05-close-wall',[-36,4,-66],[-48,8,-74]],
 ['06-scaffold',[0,1.72,-46],[0,8,-70]],
 ['08-tunnel-exit',[-1.3,1.72,-38],[0,7.4,-70]]
];
async function material(){return p.evaluate(()=>{
 const s=window.__wallPreview,names=new Set(),maps=new Set();
 s.asset.scene.traverse(o=>{if(o.isMesh)for(const m of Array.isArray(o.material)?o.material:[o.material]){
   names.add(m.name);for(const t of [m.map,m.normalMap,m.roughnessMap,m.aoMap])if(t)maps.add(t);
 }});
 return {look:s.look??'limestone (starting implementation)',materialNames:[...names],mapCount:maps.size};
});}
async function shot(file,method){await p.screenshot({path:root+'/'+file,scale:'css'});
 captures.push({file,method,data:await details(p),material:await material()});
 await writeFile(root+'/raw/'+label+'-captures.json',JSON.stringify({captures,errors},null,2));
 console.log(file);
}
async function open(mobile){
 c=await context(b,{viewport:mobile?{width:390,height:844}:{width:1366,height:900},deviceScaleFactor:1,isMobile:mobile,hasTouch:mobile});
 p=await c.newPage();p.on('pageerror',e=>errors.push(e.message));
 await p.goto('http://127.0.0.1:3000/?arrival=hub&diagnostics&quarryReview=excavation');
 await p.waitForFunction(()=>window.__gullyverse?.runtime);await p.evaluate(()=>window.__gullyverse.runtime.setQuality(3));await ready(p);
 await p.addStyleTag({content:'[data-quarry-controls],aside[class*="inspection"]{visibility:hidden!important}'});
}
try{
 await mkdir(root+'/'+label,{recursive:true});
 for(const mobile of [false,true]){
  await open(mobile);
  for(const[name,pos,target]of(mobile?[frames[0],frames[6]]:frames)){
   await view(p,pos,target,{fixed:true,quality:0});await p.waitForTimeout(400);
   await shot(label+'/'+(mobile?'mobile-':'desktop-')+name+'.png','Actual browser; matched pose, FOV, Q0/DPR1; unchanged scene lighting. Close-up is a diagnostic inspection pose.');
  }
  await unfix(p);await p.evaluate(()=>{const r=window.__gullyverse.runtime;r.clearInput();r.pose={x:0,y:1.72,z:-51,yaw:0,pitch:.1};r.setQuality(3);});
  await p.getByRole('button',{name:/^Map/}).click();
  await p.waitForFunction(()=>window.__gullyverse.runtime.getSnapshot().mapStage==='open',null,{timeout:60000});
  await shot(label+'/'+(mobile?'mobile-':'desktop-')+'07-aerial-map.png','Actual public aerial map from the same saved player pose, unchanged adaptive quality/DPR and map framing.');
  if(!mobile){
   await p.getByRole('button',{name:'Aftermovie',exact:true}).click();
   await p.waitForFunction(()=>window.__gullyverse.runtime.getSnapshot().phase==='local'&&window.__gullyverse.runtime.getSnapshot().scene==='aftermovie'&&!window.__wallPreview.state.busy,null,{timeout:90000});
   await view(p,[-10.5,1.72,-108.3],[0,10,-42],{fixed:true,quality:0});await p.waitForTimeout(400);
   await shot(label+'/desktop-09-stage-looking-back.png','Material under unchanged Aftermovie lighting; matched camera and geometry.');
  }
  await c.close();
 }
}catch(e){errors.push(String(e.stack));process.exitCode=1;}
finally{await c?.close();await b.close();await writeFile(root+'/raw/'+label+'-captures.json',JSON.stringify({status:errors.length?'FAIL':'PASS',browser:b.version(),captures,errors},null,2));}
