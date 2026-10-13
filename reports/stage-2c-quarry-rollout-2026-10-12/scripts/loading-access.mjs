import {launch,context,root} from './wall-browser-common.mjs';
import {writeFile} from 'node:fs/promises';
import assert from 'node:assert/strict';
const label=process.argv[2]||'after',browser=await launch(),c=await context(browser,{deviceScaleFactor:.25}),p=await c.newPage();
try {
 await p.route('**/quarry-limestone.glb',async route=>{await new Promise(r=>setTimeout(r,6000));await route.continue().catch(()=>{});});
 await p.goto('http://127.0.0.1:3000/?diagnostics');await p.waitForFunction(()=>window.__wallPreview?.state.busy&&document.querySelector('[data-wall-cover]'));
 const evidence=await p.getByRole('button',{name:'Use without 3D',exact:true}).evaluate(el=>{
  const parent=el.closest('div'),cover=document.querySelector('[data-wall-cover]'),r=el.getBoundingClientRect();
  return{footerZ:Number(getComputedStyle(parent).zIndex),coverZ:Number(getComputedStyle(cover).zIndex),coverOpacity:getComputedStyle(cover).opacity,buttonRect:{x:r.x,y:r.y,width:r.width,height:r.height},canvasCount:document.querySelectorAll('canvas').length};
 });
 await p.screenshot({path:root+'/raw/loading-access-'+label+'.png',scale:'css'});
 if(label==='after')assert.ok(evidence.footerZ>evidence.coverZ,'Fallback must draw above opaque preparation cover');
 else assert.ok(evidence.footerZ<evidence.coverZ,'Before capture should reproduce hidden fallback');
 await p.getByRole('button',{name:'Use without 3D',exact:true}).click();await p.waitForFunction(()=>!document.querySelector('canvas'));
 await writeFile(root+'/raw/loading-access-'+label+'.json',JSON.stringify({status:'PASS',method:'Production browser, intentionally delayed optional quarry GLB, actual screenshot and stacking-order assertion, then public fallback action.',...evidence},null,2));
 console.log(label,evidence.footerZ,evidence.coverZ,'fallback exit PASS');
}finally{await c.close();await browser.close();}
