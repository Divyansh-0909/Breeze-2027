import {writeFile,mkdir} from 'node:fs/promises';
import {launch,context,ready,view,details,root} from './wall-browser-common.mjs';
const label=process.argv[2]||'after',b=await launch(),c=await context(b,{deviceScaleFactor:1}),p=await c.newPage(),captures=[],errors=[];
try {
 await mkdir(root+'/diagnostics/'+label,{recursive:true});
 await p.goto('http://127.0.0.1:3000/?arrival=hub&diagnostics&quarryReview='+(label==='before'?'foundation':'foundation-refined'));
 await p.waitForFunction(()=>window.__gullyverse?.runtime);await p.evaluate(()=>window.__gullyverse.runtime.setQuality(3));await ready(p);
 await p.addStyleTag({content:'[data-quarry-controls],aside[class*="inspection"]{visibility:hidden!important}'});
 await view(p,[-39,5,-92],[-54,14,-95],{fixed:true,quality:0});
 async function shot(name,note){await p.waitForTimeout(500);const file='diagnostics/'+label+'/'+name+'.png';await p.screenshot({path:root+'/'+file,scale:'css'});captures.push({file,note,data:await details(p)});console.log(file);}
 await shot('approved-lighting','Unchanged approved lighting, normal PBR material.');
 // Actual THREE lights from existing constructors, scoped solely to this
 // instrumented browser. No production source/light/exposure changes.
 await p.evaluate(()=>{
  let scene=window.__wallRoots.at(-1).deref();while(scene.parent)scene=scene.parent;
  const lights=[];scene.traverse(o=>{if(o.isLight)lights.push([o,o.visible]);});
  const hemi=lights.find(([o])=>o.isHemisphereLight)[0],dir=lights.find(([o])=>o.isDirectionalLight)[0];
  const h=new hemi.constructor(0xffffff,0x757575,1.5),d=new dir.constructor(0xffffff,1.1);
  d.position.set(-35,30,-82);d.target.position.set(-54,12,-95);
  lights.forEach(([o])=>o.visible=false);scene.add(h,d,d.target);window.__neutral={scene,lights,h,d};
 });
 await shot('neutral-lighting','Temporary neutral hemisphere/directional lights in browser only; same albedo, exposure, camera, PBR maps. Diagnostic, not the proposed normal scene.');
 await p.evaluate(()=>{const {scene,lights,h,d}=window.__neutral;scene.remove(h,d,d.target);h.dispose();d.dispose();lights.forEach(([o,v])=>o.visible=v);delete window.__neutral;});
 await p.evaluate(()=>{
  window.__aoRestore=[];const materials=new Set();window.__wallRoots.at(-1).deref().traverse(o=>{if(o.isMesh)materials.add(o.material);});
  for(const m of materials){window.__aoRestore.push([m,m.aoMap,m.normalMap]);m.aoMap=null;m.normalMap=null;m.needsUpdate=true;}
 });
 await shot('no-ao-or-normal','Unchanged approved lighting with only AO and normal maps temporarily disabled; diagnoses geometry/orientation versus map attenuation.');
 await p.evaluate(()=>{for(const[m,ao,nm]of window.__aoRestore){m.aoMap=ao;m.normalMap=nm;m.needsUpdate=true;}delete window.__aoRestore;});
}catch(e){errors.push(String(e.stack));process.exitCode=1;}
finally{await c.close();await b.close();await writeFile(root+'/raw/'+label+'-lighting-diagnostics.json',JSON.stringify({status:errors.length?'FAIL':'PASS',captures,errors},null,2));}
