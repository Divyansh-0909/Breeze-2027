import {mkdir,writeFile} from "node:fs/promises";
import {launch,context,ready,view,unfix,details} from "../../stage-2c5-1-rock-realism-refinement-2026-10-14/scripts/wall-browser-common.mjs";
const root="reports/recovery-phase3-c9-2026-10-19",browser=await launch(),captures=[],errors=[];let current;
await mkdir(root+"/screenshots/diagnostics",{recursive:true});
async function shot(page,name,title,note) {
 const file=`screenshots/diagnostics/${name}.png`;await page.waitForTimeout(400);
 const data=await details(page);await page.screenshot({path:root+"/"+file,scale:"css"});
 captures.push({file,title,note,data,composition:await page.evaluate(()=>window.__wallPreview.compositionDiagnostics())});console.log(name);
}
try {
 current=await context(browser,{deviceScaleFactor:1});const page=await current.newPage();
 await page.goto("http://127.0.0.1:3000/?arrival=hub&diagnostics&quarryReview=scanned-composition");
 await page.waitForFunction(()=>window.__gullyverse?.runtime);await page.evaluate(()=>window.__gullyverse.runtime.setQuality(3));await ready(page);
 await page.addStyleTag({content:"[data-quarry-controls],aside[class*=inspection]{visibility:hidden!important}"});
 await view(page,[-31,4,-58],[-44,5,-65],{fixed:true,quality:0});
 await page.evaluate(()=>{
  window.__diagnosticMaterials=[];window.__diagnosticClones=[];
  window.__wallRoots.at(-1).deref().traverse(o=>{if(!o.isMesh)return;const m=(Array.isArray(o.material)?o.material[0]:o.material).clone();
   for(const key of ["map","normalMap","roughnessMap","metalnessMap","aoMap"])m[key]=null;m.vertexColors=false;
   m.onBeforeCompile=shader=>{shader.fragmentShader=shader.fragmentShader.replace("#include <dithering_fragment>","gl_FragColor = vec4(normalize(normal)*0.5+0.5, 1.0);\n#include <dithering_fragment>");};
   m.customProgramCacheKey=()=>"c9-view-space-geometric-normal-diagnostic";window.__diagnosticMaterials.push([o,o.material]);window.__diagnosticClones.push(m);o.material=m;
  });
 });
 await shot(page,"geometric-normals","Geometric normals / view-space RGB","Browser-only diagnostic, fine normals and PBR maps disabled; no production shader change.");
 await page.evaluate(()=>{window.__diagnosticMaterials.forEach(([o,m])=>o.material=m);window.__diagnosticClones.forEach(m=>m.dispose());});
 await page.evaluate(()=>{
  window.__wire=[];window.__wallRoots.at(-1).deref().traverse(o=>{if(!o.isMesh)return;const m=(Array.isArray(o.material)?o.material[0]:o.material).clone();
   for(const key of ["map","normalMap","roughnessMap","metalnessMap","aoMap"])m[key]=null;m.vertexColors=false;m.color.set(0xafffc8);m.wireframe=true;window.__wire.push([o,o.material,m]);o.material=m;});
 });
 await shot(page,"wireframe","Runtime wireframe inspection","Non-public close inspection of actual selected LOD geometry; diagnostic only.");
 await page.evaluate(()=>window.__wire.forEach(([o,old,m])=>{o.material=old;m.dispose();}));
 await view(page,[-18,1.72,-55],[-46,8,-65],{fixed:true,quality:0});
 for(const level of [0,1,2]) {
  await page.evaluate(level=>{
   const clone=window.__wallRoots.at(-1).deref();window.__forcedOriginal??=[];
   for(let i=0;i<3;i++){const o=clone.getObjectByName(`Foundation_Wall_15_LOD${i}`);if(!window.__forcedOriginal.some(([v])=>v===o))window.__forcedOriginal.push([o,o.visible]);Object.defineProperty(o,"visible",{configurable:true,enumerable:true,get:()=>i===level,set:()=>{}});}
  },level);
  await shot(page,"forced-lod-"+level,"Forced LOD"+level+" / identical visitor pose","Diagnostic override of only the local visual LOD. Normal experience retains automatic screen-space selection.");
 }
 await page.evaluate(()=>window.__forcedOriginal.forEach(([o,visible])=>Object.defineProperty(o,"visible",{configurable:true,enumerable:true,writable:true,value:visible})));
 await unfix(page);await page.evaluate(()=>window.__gullyverse.runtime.setQuality(3));await page.getByRole("button",{name:/^Map/}).click();await page.waitForFunction(()=>window.__gullyverse.runtime.getSnapshot().mapStage==="open");
 await page.getByRole("button",{name:"Aftermovie",exact:true}).click();await page.waitForFunction(()=>window.__gullyverse.runtime.getSnapshot().phase==="local"&&window.__gullyverse.runtime.getSnapshot().scene==="aftermovie",null,{timeout:90000});await ready(page);
 await view(page,[-10.5,1.72,-110.8],[-12,5.9,-128.3],{fixed:true,quality:0});
 await shot(page,"original-stage-context","Original Aftermovie stage / C9 retained","Actual original stage, crowd and approved lighting. Full-resolution context, not a new stage asset.");
}catch(error){errors.push(String(error.stack));process.exitCode=1;}
finally{await current?.close();await browser.close();await writeFile(root+"/raw/inspection-captures.json",JSON.stringify({status:errors.length?"FAIL":"PASS",captures,errors,physicalHardware:false},null,2));}
