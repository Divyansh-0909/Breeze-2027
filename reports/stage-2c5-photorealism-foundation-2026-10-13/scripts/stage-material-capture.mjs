import{writeFile}from'node:fs/promises';import{launch,context,ready,view,details,root}from'./wall-browser-common.mjs';
const b=await launch(),c=await context(b,{deviceScaleFactor:1}),p=await c.newPage(),captures=[];
try{
 await p.goto('http://127.0.0.1:3000/aftermovie?diagnostics&quarryReview=foundation');
 await p.waitForFunction(()=>window.__gullyverse?.runtime);await p.evaluate(()=>window.__gullyverse.runtime.setQuality(3));await ready(p);
 await p.addStyleTag({content:'[data-quarry-controls],aside[class*="inspection"]{visibility:hidden!important}'});
 for(const [label,enabled]of[['after',true],['before',false]]){
  if(!enabled){await p.evaluate(()=>window.__wallPreview.setFoundation(false));await ready(p);}
  await view(p,[-10.5,1.72,-110.8],[-51,14,-90],{fixed:true,quality:0});await p.waitForTimeout(500);
  const file=label+'/desktop-20-regions-under-stage-lighting.png';await p.screenshot({path:root+'/'+file,scale:'css'});
  captures.push({file,note:'Matched original Aftermovie walking spawn with view rotation toward detailed regions; original stage light/fog mode. Inspection holds the same player pose, FOV58, no global light edits.',data:await details(p)});
 }
}finally{await c.close();await b.close();await writeFile(root+'/raw/stage-material-captures.json',JSON.stringify({captures},null,2));}
