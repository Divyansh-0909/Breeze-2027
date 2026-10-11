import {launch,root,base,local,instrument} from './audit-common.mjs';
import {writeFile} from 'node:fs/promises';
import assert from 'node:assert/strict';
const browser=await launch(),page=await browser.newPage({viewport:{width:1366,height:900},deviceScaleFactor:.25}),result={};
try {
  await instrument(page.context());
  await page.goto(base+'/?diagnostics');await page.waitForSelector('[data-phase="landing"]',{timeout:90000});
  await page.keyboard.press('Enter');
  await page.evaluate(()=>{
    window.__gap=[];let remaining=100;
    function observe(){const r=window.__gullyverse.runtime;window.__gap.push({at:performance.now(),phase:r.getSnapshot().phase,opacity:r.revealOpacity,pose:{...r.pose},domOpacity:document.querySelector('[class*="curtain"]').style.opacity});if(remaining--)requestAnimationFrame(observe);}
    requestAnimationFrame(observe);const until=performance.now()+750;while(performance.now()<until){}
  });
  await local(page,'hub');await page.waitForFunction(()=>window.__gullyverse.runtime.revealOpacity===0);
  result.samples=await page.evaluate(()=>window.__gap);assert.ok(result.samples.some(s=>s.opacity===1&&s.domOpacity==='1'&&s.phase==='entrance'));
  result.phases=await page.evaluate(()=>window.__gullyverse.phases);const start=result.phases.find(s=>s.phase==='entrance'),end=result.phases.find(s=>s.phase==='local');result.activationMs=end.at-start.at;assert.ok(result.activationMs>=7190&&result.activationMs<7800);result.status='PASS';
}catch(e){result.status='FAIL';result.error=String(e.stack);process.exitCode=1;}finally{await writeFile(root+'/raw/gap-browser.json',JSON.stringify(result,null,2));await browser.close();}
