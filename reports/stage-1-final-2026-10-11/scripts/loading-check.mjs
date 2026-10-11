import {launch,root,base} from './audit-common.mjs';
import {writeFile} from 'node:fs/promises';
import assert from 'node:assert/strict';
const results={},browser=await launch();
try {
  for(const path of ['/', '/_vercel/insights/script.js','/_vercel/speed-insights/script.js']) {
    const response=await fetch(base+path);
    results[path]={status:response.status,link:response.headers.get('link')};
    assert.ok(!results[path].link?.includes('404-image.png'));
  }
  const page=await browser.newPage({viewport:{width:1366,height:900}});
  const response=await page.goto(base+'/__stage1_verify_missing_page__');
  assert.equal(response.status(),404);
  await page.getByRole('img',{name:'404 Illustration',exact:true}).waitFor();
  await page.waitForFunction(()=>{const img=document.querySelector('img[alt="404 Illustration"]');return img?.complete&&img.naturalWidth>0;});
  results.real404=await page.getByRole('img',{name:'404 Illustration',exact:true}).evaluate(img=>({loaded:img.complete,naturalWidth:img.naturalWidth,naturalHeight:img.naturalHeight,loading:img.loading}));
  await page.getByRole('link',{name:'Return to Home',exact:true}).waitFor();
  await page.screenshot({path:root+'/screenshots/real-404-preserved.png'});
}catch(e){results.error=String(e.stack);process.exitCode=1;}finally{await writeFile(root+'/raw/after-loading-check.json',JSON.stringify(results,null,2));await browser.close();}
