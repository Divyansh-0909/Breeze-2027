import{writeFile,mkdir}from'node:fs/promises';
import{launch,context,ready,view,unfix,details,root}from'./wall-browser-common.mjs';
const label=process.argv[2]||'before',candidate=label!=='before',captures=[],errors=[],b=await launch();let c,p;
const frames=[
 ['01-tunnel-exit',[-1.3,1.72,-38],[0,7.4,-70]],
 ['02-hub-center',[0,1.72,-51],[0,10,-110]],
 ['03-navigation-scaffold',[0,1.72,-46],[0,8,-70]],
 ['04-stage-facing',[8,1.72,-93],[-12,10,-146]],
 ['05-left-wall',[-16,1.72,-62],[-42,12,-77]],
 ['06-right-wall',[16,1.72,-65],[44,12,-88]],
 ['07-detail-navigation',[-36,4,-66],[-48,8,-74]],
 ['08-detail-corner',[-33,5,-136],[-47,12,-144]],
 ['09-detail-stage-return',[22,4,-72],[40,10,-57]],
 ['10-ground-contact',[-39,2.1,-69],[-46,.5,-71]],
 ['11-upper-rim',[0,1.72,-93],[47,35,-113]],
 ['12-close-bedding',[-42,8,-73],[-48,9,-76]],
 ['13-along-wall',[-36,3,-65],[-46,9,-103]],
 ];
async function open(mobile){
 c=await context(b,{viewport:mobile?{width:390,height:844}:{width:1366,height:900},deviceScaleFactor:1,isMobile:mobile,hasTouch:mobile});p=await c.newPage();
 p.on('pageerror',e=>errors.push(String(e)));
 await p.goto('http://127.0.0.1:3000/?arrival=hub&diagnostics'+(candidate?'&quarryReview=excavation'+(label==='macro'?'&excavation=macro':''):''));
 await p.waitForFunction(()=>window.__gullyverse?.runtime);await p.evaluate(()=>window.__gullyverse.runtime.setQuality(3));await ready(p);
 await p.addStyleTag({content:'[data-quarry-controls],aside[class*="inspection"]{visibility:hidden!important}'});
}
async function shot(name,position,target){
 await view(p,position,target,{fixed:true,quality:0});await p.waitForTimeout(400);
 const file=label+'/'+name+'.png';await p.screenshot({path:root+'/'+file,scale:'css'});
 captures.push({file,method:'Actual browser, matched camera/FOV/quality/DPR and unchanged lighting. Fixed inspection positions do not replace player cameras.',data:await details(p)});
 await writeFile(root+'/raw/'+label+'-captures.json',JSON.stringify({captures,errors},null,2));console.log(file);
}
try{
 await mkdir(root+'/'+label,{recursive:true});
 for(const mobile of[false,true]){
  await open(mobile);
  for(const[name,position,target]of(mobile?[frames[0],frames[1],frames[4]]:frames))await shot((mobile?'mobile-':'desktop-')+name,position,target);
  await unfix(p);await p.evaluate(()=>{const r=window.__gullyverse.runtime;r.clearInput();r.pose={x:0,y:1.72,z:-51,yaw:0,pitch:.1};r.setQuality(3);});
  await p.getByRole('button',{name:/^Map/}).click();await p.waitForFunction(()=>window.__gullyverse.runtime.getSnapshot().mapStage==='open',null,{timeout:60000});
  const file=label+'/'+(mobile?'mobile-':'desktop-')+'14-aerial-map.png';await p.screenshot({path:root+'/'+file,scale:'css'});
  captures.push({file,method:'Public aerial map from the exact same saved Hub pose; framing and markers unchanged.',data:await details(p)});
  if(!mobile){
   await p.getByRole('button',{name:'Aftermovie',exact:true}).click();await p.waitForFunction(()=>window.__gullyverse.runtime.getSnapshot().phase==='local'&&window.__gullyverse.runtime.getSnapshot().scene==='aftermovie'&&!window.__wallPreview.state.busy,null,{timeout:90000});
   await shot('desktop-15-stage-looking-back',[-10.5,1.72,-108.3],[0,10,-42]);
   await shot('desktop-16-stage-front',[-10.5,1.72,-110.8],[-12,5.9,-128.3]);
  }
  await c.close();
 }
}catch(e){errors.push(String(e.stack));process.exitCode=1;}
finally{await c?.close();await b.close();await writeFile(root+'/raw/'+label+'-captures.json',JSON.stringify({browser:b.version(),status:errors.length?'FAIL':'PASS',captures,errors},null,2));}
