import{launch,context,ready,view,details,root}from'./wall-browser-common.mjs';import{writeFile,mkdir}from'node:fs/promises';
const b=await launch();await mkdir(root+'/recordings',{recursive:true});
const c=await context(b,{viewport:{width:1366,height:900},deviceScaleFactor:.5,recordVideo:{dir:root+'/recordings',size:{width:1366,height:900}}}),p=await c.newPage(),events=[],errors=[];
try{
 await p.goto('http://127.0.0.1:3000/?arrival=hub&diagnostics&quarryReview=foundation-refined');await ready(p);
 await p.addStyleTag({content:'[data-quarry-controls],aside[class*="inspection"]{visibility:hidden!important}'});
 await p.evaluate(()=>{const label=document.createElement('div');label.textContent='GEOLOGY INSPECTION · ACTUAL BROWSER · AUTOMATIC LOD · walking bounds unchanged';label.style='position:fixed;z-index:200;top:12px;left:12px;padding:10px;background:#182b24ee;color:#fff;font:14px sans-serif';document.body.append(label);});
 // Close inspection cannot be reached by ordinary walking: existing directional
 // gates intentionally route visitors first. Only this review camera is moved.
 for(let i=0;i<=48;i++){
  const t=i/48,z=-114+55*t,x=-40+7*t;
  await view(p,[x,1.72,z],[-53,10,z-3],{fixed:true,quality:3});
  if(i%6===0)events.push({event:'eye-height inspection traverse',fraction:t,data:await details(p)});
 }
 for(const x of [-35,-28,-18,-5,9,33,43]){await view(p,[x,1.72,-88],[-54,13,-91],{fixed:true,quality:3});await p.waitForTimeout(700);events.push({event:'automatic distance LOD',data:await details(p)});}
}catch(e){errors.push(String(e.stack));process.exitCode=1;}
finally{const video=p.video();await c.close();await video.saveAs(root+'/recordings/near-wall-inspection.webm');await b.close();await writeFile(root+'/raw/near-wall-recording.json',JSON.stringify({status:errors.length?'FAIL':'PASS',method:'Real browser eye-height inspection-camera recording with automatic screen-space LOD. Not a public locomotion path or generated video. Separate visitor recording verifies public movement/map.',events,errors},null,2));}
