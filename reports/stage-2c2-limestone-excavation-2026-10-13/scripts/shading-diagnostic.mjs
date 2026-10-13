import{launch,context,ready,view,details,root}from'./wall-browser-common.mjs';import{writeFile,mkdir}from'node:fs/promises';
const b=await launch(),c=await context(b,{deviceScaleFactor:1}),p=await c.newPage(),rows=[];
try{
 await mkdir(root+'/diagnostics',{recursive:true});await p.goto('http://127.0.0.1:3000/?arrival=hub&diagnostics&quarryReview=excavation');await p.waitForFunction(()=>window.__gullyverse?.runtime);await p.evaluate(()=>window.__gullyverse.runtime.setQuality(3));await ready(p);
 await p.addStyleTag({content:'[data-quarry-controls],aside[class*="inspection"]{visibility:hidden!important}'});await view(p,[-36,4,-66],[-48,8,-74],{fixed:true,quality:0});
 for(const mode of['original','normal-map-disabled','actual-geometric-normals']){
  if(mode==='normal-map-disabled')await p.evaluate(()=>{window.__wallPreview.asset.scene.traverse(o=>{if(o.isMesh){o.material.normalMap=null;o.material.needsUpdate=true;}});});
  if(mode==='actual-geometric-normals')await p.evaluate(()=>{window.__wallPreview.asset.scene.traverse(o=>{if(o.isMesh)o.geometry.computeVertexNormals();});});
  await p.waitForTimeout(1000);await p.screenshot({path:root+'/diagnostics/'+mode+'.png'});rows.push({mode,data:await details(p)});
 }
 await writeFile(root+'/raw/shading-diagnostic.json',JSON.stringify({rows,method:'Temporary browser-memory diagnostic only. No source maps, material assets or production settings modified. Same exact camera throughout.'},null,2));
}finally{await c.close();await b.close();}
