import {chromium} from 'playwright';
import {writeFile,mkdir} from 'node:fs/promises';
import assert from 'node:assert/strict';
const root='reports/stage-2c5-1-wip-activation-2026-10-15',base=process.env.AUDIT_BASE||'http://127.0.0.1:3000',label=process.env.AUDIT_LABEL||'local-after',expectRock=process.env.EXPECT_ROCK!=='0',full=process.env.AUDIT_FULL==='1';
const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true});
const checks=[],requests=[],errors=[],captures=[];
const mobile=process.env.AUDIT_MOBILE==='1';
const context=await browser.newContext({viewport:mobile?{width:390,height:844}:{width:1366,height:900},deviceScaleFactor:.5,...(mobile?{isMobile:true,hasTouch:true}:{})});
await context.route('**/api/**',r=>r.abort());
const p=await context.newPage();p.setDefaultTimeout(90000);
p.on('pageerror',e=>errors.push(e.message));p.on('request',r=>{if(r.url().includes('.glb'))requests.push(r.url());});
async function local(id){await p.waitForFunction(id=>{const s=window.__wallPreview?.runtime.getSnapshot();return s?.phase==='error'||s?.phase==='local'&&s.scene===id;},id);assert.equal(await p.locator('[data-phase]').getAttribute('data-phase'),'local');await p.waitForFunction(()=>window.__wallPreview&&!window.__wallPreview.state.busy);}
async function information(){return p.evaluate(()=>{const s=window.__wallPreview,r=s.runtime,materials=new Map();s.asset.scene.traverse(o=>{if(o.isMesh)for(const m of Array.isArray(o.material)?o.material:[o.material])materials.set(m.uuid,{name:m.name,roughness:m.roughness,metalness:m.metalness,maps:['map','normalMap','roughnessMap','aoMap'].map(k=>({slot:k,name:m[k]?.name,width:m[k]?.image?.width,height:m[k]?.image?.height}))});});return {style:s.style,look:s.look,refinement:s.refinement,foundationEnabled:s.foundationEnabled,state:s.state,materials:[...materials.values()],pose:{...r.pose},camera:r.cameraPose(innerWidth/innerHeight),quality:r.getSnapshot().quality,viewport:[innerWidth,innerHeight],dpr:document.querySelector('canvas').width/innerWidth,canvases:document.querySelectorAll('canvas').length,reviewControls:document.querySelectorAll('[data-quarry-controls],[data-wall-preview]').length,trace:s.trace};});}
async function capture(name){await p.waitForTimeout(500);const file=(expectRock?'after/':'before/')+label+'-'+name+'.png';await p.screenshot({path:root+'/'+file,scale:'css'});captures.push({file,data:await information()});}
try{
 await p.goto(base+(full?'/':'/?arrival=hub'),{waitUntil:'domcontentloaded'});
 await p.waitForFunction(()=>window.__wallPreview?.runtime);await p.evaluate(()=>window.__wallPreview.runtime.setQuality(3));
 if(full){await p.locator('[data-phase="landing"]').waitFor();assert.equal(await p.getByRole('button',{name:'Enter Gullyverse',exact:true}).count(),1);await p.getByRole('button',{name:'Enter Gullyverse',exact:true}).click();checks.push('Fresh ordinary / requires entry and reaches the hub');}
 await local('hub');const canvas=await p.locator('canvas').elementHandle();
 let data=await information();
 if(expectRock){assert.equal(data.look,'rock');assert.equal(data.style,'detailed');assert.equal(data.refinement,true);assert.equal(data.foundationEnabled,true);assert.deepEqual(data.materials.map(m=>m.name).sort(),['Foundation_Dark_Rock_PBR','Foundation_Dry_Terrain_PBR']);assert.ok(requests.some(u=>u.includes('/quarry-foundation-refined/foundation-geometry.glb')));assert.ok(requests.some(u=>u.includes('/quarry-foundation-refined/foundation-materials.glb')));assert.equal(data.reviewControls,0);assert.ok(!requests.some(u=>u.includes('/quarry-rollout/')||u.includes('grey-limestone-material')||u.includes('/quarry-foundation/')||u.includes('/limestone-excavation/')||u.includes('/rock-look-restore/')));checks.push('Ordinary URL loads actual Stage2C.5.1 geometry and material holder; refinement enabled, no old quarry requests or review controls');}
 await capture('hub');
 await p.getByRole('button',{name:/^Map/}).click();await p.waitForFunction(()=>window.__wallPreview.runtime.getSnapshot().mapStage==='open');await capture('map');
 if(expectRock){const invalid=await p.locator('svg [x],svg [y],svg [x1],svg [y1],svg [x2],svg [y2]').evaluateAll(nodes=>nodes.flatMap(n=>[...n.attributes].filter(a=>/^(x|y|x1|y1|x2|y2)$/.test(a.name)&&/NaN|Infinity/.test(a.value)).map(a=>a.value)));assert.deepEqual(invalid,[]);}
 await p.getByRole('button',{name:'Aftermovie',exact:true}).click();await local('aftermovie');await capture('stage');
 assert.equal(await p.evaluate(c=>document.querySelector('canvas')===c,canvas),true);checks.push('Aerial map to Aftermovie retains the same Canvas; material is inspected separately');
 if(full){
  await p.getByRole('button',{name:'Play Aftermovie',exact:true}).click();await p.waitForFunction(()=>window.__wallPreview.runtime.movieActions.status().currentTime>.2);await p.getByRole('button',{name:'Exit Aftermovie',exact:true}).click();await p.waitForFunction(()=>!window.__wallPreview.runtime.getSnapshot().movie&&window.__wallPreview.runtime.focusFrom===null);checks.push('Original video actually plays and exits');
  await p.keyboard.down('KeyS');await p.getByRole('dialog',{name:'Where to next?'}).waitFor();await p.keyboard.up('KeyS');await p.getByRole('button',{name:'Return to Hub',exact:true}).click();await local('hub');checks.push('Boundary menu returns to hub through existing travel');
  await p.goBack();await local('aftermovie');await p.goForward();await local('hub');checks.push('Browser Back/Forward preserves the dark quarry');
  await p.reload();await local('hub');assert.equal((await information()).refinement,true);assert.equal((await information()).foundationEnabled,true);checks.push('Reload retains Stage2C.5.1 without review URL or preview build flag');
 }
 data=await information();await writeFile(root+'/raw/'+label+'.json',JSON.stringify({status:'PASS',base,browser:browser.version(),physicalHardware:false,checks,data,requests,captures,errors},null,2));assert.deepEqual(errors,[]);console.log(label,'PASS',checks);
}catch(e){process.exitCode=1;errors.push(String(e.stack));await writeFile(root+'/raw/'+label+'.json',JSON.stringify({status:'FAIL',base,checks,requests,captures,errors},null,2));console.error(label,e);}
finally{await context.close();await browser.close();}
