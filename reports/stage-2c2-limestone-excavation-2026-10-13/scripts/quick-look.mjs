import {writeFile,mkdir} from 'node:fs/promises';
import {launch,context,ready,view,unfix,details,root} from './wall-browser-common.mjs';
const b=await launch(),c=await context(b,{deviceScaleFactor:1}),p=await c.newPage(),rows=[],errors=[];
p.on('pageerror',e=>errors.push(e.message));
try {
 await mkdir(root+'/quick',{recursive:true});
 await p.goto('http://127.0.0.1:3000/?arrival=hub&diagnostics&quarryReview=excavation&excavation=macro');
 await p.waitForFunction(()=>window.__gullyverse?.runtime);await p.evaluate(()=>window.__gullyverse.runtime.setQuality(3));await ready(p);
 await p.addStyleTag({content:'[data-quarry-controls],aside[class*="inspection"]{visibility:hidden!important}'});
 for(const[name,pos,target]of[['hub',[0,1.72,-51],[0,10,-110]],['left',[-16,1.72,-62],[-42,12,-77]],['exit',[-1.3,1.72,-38],[0,7.4,-70]]]){
  await view(p,pos,target,{fixed:true,quality:0});await p.waitForTimeout(400);
  await p.screenshot({path:root+'/quick/'+name+'.png'});rows.push({name,data:await details(p)});
 }
 await unfix(p);await p.evaluate(()=>{const r=window.__gullyverse.runtime;r.pose={x:0,y:1.72,z:-51,yaw:0,pitch:.1};r.setQuality(3);});
 await p.getByRole('button',{name:/^Map/}).click();await p.waitForFunction(()=>window.__gullyverse.runtime.getSnapshot().mapStage==='open',null,{timeout:60000});
 await p.screenshot({path:root+'/quick/map.png'});rows.push({name:'map',data:await details(p)});
 console.log('PASS quick macro browser views');
}catch(e){errors.push(String(e.stack));process.exitCode=1;}
finally{await writeFile(root+'/raw/quick-look.json',JSON.stringify({rows,errors,status:errors.length?'FAIL':'PASS'},null,2));await c.close();await b.close();}
