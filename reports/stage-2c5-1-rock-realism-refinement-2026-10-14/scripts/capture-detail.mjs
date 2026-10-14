import{writeFile,mkdir}from'node:fs/promises';
import{launch,context,ready,view,details,root}from'./wall-browser-common.mjs';
const label=process.argv[2]||'after',browser=await launch(),c=await context(browser,{deviceScaleFactor:1}),p=await c.newPage(),captures=[],errors=[];
const url='http://127.0.0.1:3000/?arrival=hub&diagnostics&quarryReview='+(label==='before'?'foundation':'foundation-refined');
const frames=[
 ['10-broad-face',[-32,1.72,-97],[-52,14,-100]],
 ['11-corner',[-26,1.72,-58],[-43,13,-69]],
 ['12-joined-regions',[-31,3,-71],[-52,12,-81]],
 ['13-fracture-close',[-47,6,-88],[-56,11,-92]],
 ['14-upper-rim',[-34,1.72,-98],[-56,30,-101]],
 ['15-wall-foot',[-37,1.72,-90],[-51,.3,-92]],
 ['16-along-wall',[-36,1.72,-69],[-53,9,-123]],
 ['17-terrain-map-height',[76,155,-90],[65,25,-103]]
];
async function shot(name,note){const file=label+'/'+name+'.png';await p.screenshot({path:root+'/'+file,scale:'css'});captures.push({file,note,data:await details(p)});console.log(file);await writeFile(root+'/raw/'+label+'-detail-captures.json',JSON.stringify({captures,errors},null,2));}
try{
 await mkdir(root+'/'+label,{recursive:true});await p.goto(url);await ready(p);
 await p.addStyleTag({content:'[data-quarry-controls],aside[class*="inspection"]{visibility:hidden!important}'});
 for(const[name,pos,target]of frames){await view(p,pos,target,{fixed:true,quality:0});await p.waitForTimeout(300);await shot('desktop-'+name,'Matched actual-browser camera; unchanged Hub lighting. Poses outside walking bounds are labeled inspection, not gameplay.');}
 await view(p,[-39,5,-92],[-54,14,-95],{fixed:true,quality:0});
 for(const diagnostic of ['material-only','no-normal','geometric-normal','wireframe']){
  await p.evaluate(diagnostic=>{
   const clone=window.__wallRoots.at(-1).deref();window.__diagnosticRestores=[];
   let template;clone.traverse(o=>{if(o.isMesh&&!template)template=o.material;});
   const Standard=template.constructor,normalProto=Object.getPrototypeOf(Object.getPrototypeOf(template));
   clone.traverse(o=>{if(!o.isMesh)return;const original=o.material,m=original.clone();
    // Standard material emissive/map-only faithfully exposes texture content.
    if(diagnostic==='material-only'){m.normalMap=null;m.roughnessMap=null;m.aoMap=null;m.metalnessMap=null;m.color.setRGB(0,0,0);m.emissive.setRGB(1,1,1);m.emissiveMap=original.map;}
    if(diagnostic==='no-normal')m.normalMap=null;
    if(diagnostic==='geometric-normal'){
     m.map=null;m.normalMap=null;m.roughnessMap=null;m.aoMap=null;m.color.setRGB(0,0,0);m.vertexColors=false;
     m.onBeforeCompile=shader=>{shader.fragmentShader=shader.fragmentShader.replace('#include <opaque_fragment>','outgoingLight = normalize(normal) * 0.5 + 0.5;\n#include <opaque_fragment>');};m.customProgramCacheKey=()=> 'foundation-geometric-normal-diagnostic';
    }
    if(diagnostic==='wireframe'){m.map=null;m.normalMap=null;m.aoMap=null;m.color.setRGB(.02,.02,.02);m.emissive.setRGB(.6,.8,.6);m.wireframe=true;}
    m.needsUpdate=true;o.material=m;window.__diagnosticRestores.push([o,original,m]);
   });
  },diagnostic);
  await p.waitForTimeout(800);await shot('diagnostic-'+diagnostic,'Actual renderer, temporary clone-owned diagnostic material; source maps and global lights unchanged.');
  await p.evaluate(()=>{for(const[o,original,m]of window.__diagnosticRestores){o.material=original;m.dispose();}delete window.__diagnosticRestores;});
 }
 if(label==='after'){
  for(const[level,pos,target]of [[0,[-39,5,-92],[-54,14,-95]],[1,[-25,2,-89],[-54,14,-95]],[2,[0,2,-89],[-54,14,-95]]]){
   await view(p,pos,target,{fixed:true,quality:0});
   await p.evaluate(level=>{const s=window.__wallPreview;s.state.mode='off';const clone=window.__wallRoots.at(-1).deref();for(const part of s.partsForRendering())part.nodes.forEach((name,i)=>{clone.getObjectByName(name).visible=i===level;});},level);
   await p.waitForTimeout(350);await shot('inspection-lod'+level,'Forced single LOD for visual comparison; actual browser. Normal automatic LOD/hysteresis separately tested in walkthrough.');
   await p.evaluate(()=>window.__wallPreview.state.mode='authored');
  }
 }
}catch(e){errors.push(String(e.stack));process.exitCode=1;}
finally{await c.close();await browser.close();await writeFile(root+'/raw/'+label+'-detail-captures.json',JSON.stringify({status:errors.length?'FAIL':'PASS',captures,errors},null,2));}
