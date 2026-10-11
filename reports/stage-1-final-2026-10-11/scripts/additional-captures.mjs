import {launch,root,base,local,instrument} from './audit-common.mjs';
import {writeFile} from 'node:fs/promises';
const browser=await launch(),page=await browser.newPage({viewport:{width:1366,height:900},deviceScaleFactor:.25}),captures=[];
try {
  await instrument(page.context());
  await page.goto(base+'/aftermovie?diagnostics');await local(page,'aftermovie');
  await page.evaluate(()=>{const r=window.__gullyverse.runtime;r.clearInput();Object.assign(r.pose,{x:-10.5,y:1.72,z:-112.8,yaw:Math.PI,pitch:-.3});});
  await page.waitForTimeout(800);
  for(const [file,note] of [['stage-ground-detail.png','Acceptance-only fixed browser review pose, looking down toward the preserved stage floor edge; no matching before capture exists.']]) {
    const metadata=await page.evaluate(()=>({camera:window.__gullyverse.runtime.cameraPose(innerWidth/innerHeight),stats:window.__gullyverse.stats,snapshot:window.__gullyverse.runtime.getSnapshot(),viewport:{width:innerWidth,height:innerHeight,dpr:devicePixelRatio}}));
    await page.screenshot({path:root+'/acceptance/'+file,scale:'css'});captures.push({file,note,...metadata});
  }
  await page.getByRole('button',{name:'Play Aftermovie',exact:true}).click();await page.waitForFunction(()=>window.__gullyverse.runtime.movieActions.status().currentTime>.5,null,{timeout:30000});await page.waitForTimeout(2500);
  const metadata=await page.evaluate(()=>({camera:window.__gullyverse.runtime.cameraPose(innerWidth/innerHeight),stats:window.__gullyverse.stats,snapshot:window.__gullyverse.runtime.getSnapshot(),viewport:{width:innerWidth,height:innerHeight,dpr:devicePixelRatio}}));
  await page.screenshot({path:root+'/acceptance/shared-led-playback.png',scale:'css'});captures.push({file:'shared-led-playback.png',note:'Actual current playback across original shared LED wall; public Play control. Acceptance-only, not matched-camera before/after proof.',...metadata});
}finally{await writeFile(root+'/acceptance/additional-captures.json',JSON.stringify(captures,null,2));await browser.close();}
