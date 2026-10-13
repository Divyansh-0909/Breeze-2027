import{launch,context,ready,details,root}from'./wall-browser-common.mjs';
import{writeFile}from'node:fs/promises';import assert from'node:assert/strict';
const b=await launch(),c=await context(b,{deviceScaleFactor:.25}),p=await c.newPage(),cycles=[],errors=[];
const counts=d=>({textures:d.stats.textures,geometries:d.stats.geometries,
 ...Object.fromEntries(['Texture','Buffer','Program'].map(k=>[k,d.contexts[0].stats[k].active]))});
async function style(s){await p.evaluate(v=>window.__wallPreview.setExcavation(v),s);await p.waitForFunction(v=>window.__wallPreview.style===v&&!window.__wallPreview.state.busy,s,{timeout:100000});await p.waitForTimeout(700);}
let result={cycles,errors};
try{
 await p.goto('http://127.0.0.1:3000/?arrival=hub&diagnostics&quarryReview=excavation');
 await p.waitForFunction(()=>window.__gullyverse?.runtime);await p.evaluate(()=>window.__gullyverse.runtime.setQuality(3));await ready(p);
 result.initial=await details(p);
 for(let i=1;i<=10;i++){
  const row={cycle:i};
  for(const s of['baseline','detailed']){
   await style(s);const d=await details(p);
   assert.equal(d.wall.selectedNodes.length,s==='baseline'?27:18);
   const uniqueness=await p.evaluate(()=>{const clone=window.__wallRoots.at(-1)?.deref(),byPart={},materials=new Set();clone.traverseVisible(o=>{if(o.isMesh&&o.name!=='Wall_Collision'){const part=o.name.replace(/_LOD[012]$/,'');byPart[part]=(byPart[part]||0)+1;materials.add(o.material);}});return{byPart,materials:materials.size};});
   assert.ok(Object.values(uniqueness.byPart).every(n=>n===1));assert.equal(uniqueness.materials,1);
   row[s]={counts:counts(d),details:d,uniqueness};
  }
  cycles.push(row);await writeFile(root+'/raw/lifecycle.json',JSON.stringify(result,null,2));console.log('Cycle',i);
 }
 for(const s of['baseline','detailed'])for(const row of cycles.slice(2))assert.deepEqual(row[s].counts,cycles[2][s].counts);
 await style('baseline');result.beforeRetirement=await details(p);
 await p.evaluate(()=>window.__wallPreview.retireExcavation());await p.waitForTimeout(900);result.afterRetirement=await details(p);
 assert.equal(result.afterRetirement.stats.textures,result.beforeRetirement.stats.textures);
 assert.ok(result.afterRetirement.stats.geometries<result.beforeRetirement.stats.geometries);
 result.status='PASS';result.method='Ten explicit Stage2C/detailed-preview cycles, one selected LOD per partition, settled GL/Three counters after warm-up; inactive geometry retirement preserves cached shared maps. Not driver VRAM evidence.';
}catch(e){errors.push(String(e.stack));result.status='FAIL';process.exitCode=1;}
finally{await writeFile(root+'/raw/lifecycle.json',JSON.stringify(result,null,2));await c.close();await b.close();}
