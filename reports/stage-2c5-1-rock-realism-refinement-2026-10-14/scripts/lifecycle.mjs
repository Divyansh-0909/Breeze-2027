import{launch,context,ready,details,root}from'./wall-browser-common.mjs';
import{writeFile}from'node:fs/promises';import assert from'node:assert/strict';
const browser=await launch(),c=await context(browser,{deviceScaleFactor:.25}),p=await c.newPage(),rows=[],errors=[];
async function swap(enabled){await p.evaluate(enabled=>window.__wallPreview.setFoundation(enabled),enabled);await ready(p);await p.waitForTimeout(350);}
async function record(label){const d=await details(p);rows.push({label,...d});await writeFile(root+'/raw/lifecycle.json',JSON.stringify({rows,errors},null,2));console.log(label,d.stats,d.wall.assetTextures);}
try{
 await p.goto('http://127.0.0.1:3000/?arrival=hub&diagnostics&quarryReview=foundation-refined');await ready(p);
 await record('initial-foundation');await swap(false);await record('baseline-warmed');
 for(let i=0;i<10;i++){
  await swap(true);assert.equal((await details(p)).wall.selectedNodes.length,35);await record('foundation-'+i);
  await swap(false);assert.equal((await details(p)).wall.selectedNodes.length,18);await record('baseline-'+i);
 }
 const settled=rows.filter(r=>r.label.startsWith('foundation-')||r.label.startsWith('baseline-')).slice(2);
 const memory=settled.map(r=>r.stats);
 assert.ok(memory.every(Boolean),'Renderer counters must actually be measured');
 const first=memory[0],last=memory.at(-2);
 assert.ok(last.textures<=first.textures&&last.geometries<=first.geometries,'Settled repeated caches must not grow');
 await p.evaluate(()=>window.__wallPreview.retireFoundation());await p.waitForTimeout(500);await record('foundation-retired');
 assert.ok(rows.at(-1).wall.trace.some(e=>e.event==='foundation-material-disposal'&&e.textures===6));
 await swap(true);await record('foundation-reloaded-after-retirement');
 const canvas=await p.evaluateHandle(()=>document.querySelector('canvas')),owner=await p.evaluateHandle(()=>window.__wallPreview);
 await p.getByRole('button',{name:'Use without 3D',exact:true}).click();await p.waitForFunction(()=>!document.querySelector('canvas'));
 const disposed=await owner.evaluate(s=>({disposed:s.disposed,consumers:s.consumers,asset:!!s.asset,trace:s.trace}));
 assert.equal(disposed.disposed,true);assert.equal(disposed.consumers,0);assert.equal(disposed.asset,false);
 rows.push({label:'owner-unmounted',disposed,canvasConnected:await canvas.evaluate(c=>c.isConnected)});
}catch(e){errors.push(String(e.stack));process.exitCode=1;}
finally{await c.close();await browser.close();await writeFile(root+'/raw/lifecycle.json',JSON.stringify({status:errors.length?'FAIL':'PASS',method:'Ten covered enable/disable cycles, bounded shared caches, explicit retirement/reload, full fallback unmount. GL counters are allocation proxies, not VRAM.',rows,errors},null,2));}
