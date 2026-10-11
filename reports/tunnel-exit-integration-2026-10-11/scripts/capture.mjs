import { chromium } from 'playwright';
import { readFile, writeFile } from 'node:fs/promises';
import assert from 'node:assert/strict';
const mode = process.argv[2] || 'baseline';
const root = 'reports/tunnel-exit-integration-2026-10-11';
const world = JSON.parse(await readFile('public/models/gullyverse/blockout.layout.json', 'utf8'));
const browser = await chromium.launch({ executablePath: '/usr/bin/chromium', headless: true, args: ['--no-sandbox', '--disable-dev-shm-usage', '--enable-unsafe-swiftshader', '--use-gl=angle', '--use-angle=swiftshader'] });
const errors = [], captures = [];
const views = [
  { id: 'stage-looking-back', scene: 'aftermovie', position: world.aftermovie.spawn, target: [0,5,-42] },
  { id: 'tunnel-mouth-from-quarry', scene: 'hub', position: [0,1.72,-54], target: [0,8,-42] },
  { id: 'tunnel-exit-forward', scene: 'hub', position: [-1.3,1.72,-38], target: [0,7.4,-70] },
  { id: 'stage-front', scene: 'aftermovie', position: world.aftermovie.spawn, target: [-12,5.9,-128.3] },
];
try {
  for (const viewport of [{width:1366,height:900}, {width:390,height:844}]) {
    const context = await browser.newContext({ viewport, deviceScaleFactor: .25 });
    const page = await context.newPage();
    page.on('pageerror', error => errors.push(error.message));
    await page.route('**/api/**', route => ['GET','HEAD'].includes(route.request().method()) ? route.continue() : route.abort());
    await page.goto('http://127.0.0.1:3000/?arrival=hub&diagnostics', {waitUntil:'domcontentloaded'});
    await page.waitForSelector('[data-phase="local"][data-location="hub"]', {timeout:90000});
    await page.evaluate(()=>{window.__reviewCameraPose=window.__gullyverse.runtime.cameraPose.bind(window.__gullyverse.runtime);});
    let scene='hub';
    for (const view of views) {
      if (scene !== view.scene) {
        await page.evaluate(scene=>{
          const r=window.__gullyverse.runtime;r.cameraPose=window.__reviewCameraPose;r.inspect(null);r.request(scene,'navbar');
        },view.scene);
        await page.waitForSelector(`[data-phase="local"][data-location="${view.scene}"]`, {timeout:90000});
        scene = view.scene;
      }
      await page.evaluate(view => {
        const r=window.__gullyverse.runtime;
        r.setQuality(3);r.inspectionEnabled=true;r.inspect('quarry');
        const [x,y,z]=view.position,[tx,ty,tz]=view.target;
        r.cameraPose=()=>({x,y,z,yaw:Math.atan2(-(tx-x),-(tz-z)),pitch:Math.atan2(ty-y,Math.hypot(tx-x,tz-z)),fov:58});
      }, view);
      await page.waitForTimeout(900);
      const filename=`${viewport.width===390?'mobile':'desktop'}-${view.id}.png`;
      await page.screenshot({ path:`${root}/${mode}/${filename}`,scale:'css' });
      captures.push({...view,viewport,dpr:.25,fov:58,filename,diagnostics:await page.evaluate(()=>({stats:window.__gullyverse.stats,quality:window.__gullyverse.runtime.getSnapshot().quality}))});
      console.log(filename);
    }
    await context.close();
  }
  assert.deepEqual(errors,[]);
  await writeFile(`${root}/${mode}/captures.json`,JSON.stringify({mode,browser:browser.version(),renderer:'SwiftShader software rendering',cameraMethod:'Matched diagnostic camera poses; these captures are visual evidence, not public-control journey tests.',captures,pageErrors:errors},null,2));
  console.log(JSON.stringify({mode,captures:captures.length,pageErrors:errors}));
} finally { await browser.close(); }
