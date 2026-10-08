/** Public input checks for Revision 2. Blocks all API writes during validation. */
import assert from "node:assert/strict";
import { mkdir,readFile,writeFile,unlink } from "node:fs/promises";
import { chromium } from "playwright";
import * as THREE from "three";
const base=process.env.GULLYVERSE_BASE_URL ?? "http://localhost:3000";
const dir=".gullyverse-artifacts/stage-1-revision-2";
const world=JSON.parse(await readFile(new URL("../public/models/gullyverse/blockout.layout.json",import.meta.url),"utf8"));
await mkdir(dir,{recursive:true});
const browser=await chromium.launch({executablePath:process.env.CHROME_PATH ?? "C:/Program Files/Google/Chrome/Application/chrome.exe",headless:true});
const checks=[],errors=[],mutations=[];
const waitLocal=(p,id)=>p.waitForSelector(`[data-phase="local"][data-location="${id}"]`,{timeout:60000});
const pose=p=>p.evaluate(()=>({...window.__gullyverse.runtime.pose}));
const state=p=>p.evaluate(()=>window.__gullyverse.runtime.getSnapshot());
const key=async(p,code,ms)=>{await p.keyboard.down(code);await p.waitForTimeout(ms);await p.keyboard.up(code);};
const menu=p=>p.getByRole("dialog",{name:"Where to next?"});
async function guardedPage(context) {
  const page=await context.newPage();page.on("pageerror",e=>errors.push({url:page.url(),at:new Date().toISOString(),message:e.message}));
  await page.route("**/api/**",route=>{
    if(!["GET","HEAD"].includes(route.request().method())){mutations.push({url:route.request().url(),method:route.request().method()});return route.abort();}
    return route.continue();
  });return page;
}
async function contactBoundary(page,keys) {
  for(const code of keys)await page.keyboard.down(code);
  await menu(page).waitFor({timeout:10000});
  for(const code of keys)await page.keyboard.up(code);
  await page.waitForTimeout(300);
}
async function mapTravel(page,label,id) {
  await page.getByRole("button",{name:/^Map/}).click();
  await page.waitForFunction(()=>window.__gullyverse.runtime.getSnapshot().mapStage==="open",{timeout:10000});
  await page.getByRole("button",{name:label,exact:true}).click();await waitLocal(page,id);
}
async function lookToward(page,target) {
  const current=await pose(page),wanted=Math.atan2(-(target[0]-current.x),-(target[2]-current.z));
  let remaining=Math.atan2(Math.sin(wanted-current.yaw),Math.cos(wanted-current.yaw));
  while(Math.abs(remaining)>.0001) {
    const turn=Math.max(-.6,Math.min(.6,remaining));
    await page.mouse.move(650,340);await page.mouse.down();await page.mouse.move(650-turn/.003,340,{steps:8});await page.mouse.up();remaining-=turn;
  }
  await page.waitForTimeout(100);
}
async function verifyMarkers(page) {
  const evidence=await page.getByRole("region",{name:"Festival aerial map"}).evaluate(el=>({viewport:{width:innerWidth,height:innerHeight},camera:window.__gullyverse.runtime.cameraPose(innerWidth/innerHeight),rect:el.getBoundingClientRect().toJSON(),buttons:[...el.querySelectorAll("button[data-destination]")].map(b=>({name:b.getAttribute("aria-label")??b.textContent,disabled:b.disabled,rect:b.getBoundingClientRect().toJSON(),destination:b.dataset.destination})),dots:[...el.querySelectorAll("[data-map-point]")].map(d=>({id:d.dataset.mapPoint,world:d.dataset.worldPosition,transform:d.style.transform}))}));
  for(const marker of evidence.buttons){const r=marker.rect;assert.ok(r.left>=-.5 && r.top>=-.5 && r.right<=evidence.viewport.width+.5 && r.bottom<=evidence.viewport.height+.5,"Marker clipped: "+marker.name);}
  for(let i=0;i<evidence.buttons.length;i++)for(let j=i+1;j<evidence.buttons.length;j++){
    const a=evidence.buttons[i].rect,b=evidence.buttons[j].rect;
    assert.ok(Math.min(a.right,b.right)-Math.max(a.left,b.left)<=.5 || Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top)<=.5,"Map labels overlap: "+evidence.buttons[i].name+" / "+evidence.buttons[j].name);
  }
  const p=evidence.camera,camera=new THREE.PerspectiveCamera(p.fov,evidence.viewport.width/evidence.viewport.height,world.camera.near,world.camera.far);
  camera.position.set(p.x,p.y,p.z);camera.quaternion.setFromEuler(new THREE.Euler(p.pitch,p.yaw,0,"YXZ"));camera.updateMatrixWorld();
  assert.ok(evidence.dots.length>=10,"All actual world marker dots expose their projection evidence");
  for(const dot of evidence.dots){const point=dot.world.split(",").map(Number),v=new THREE.Vector3(...point).project(camera),expected=[(v.x+1)*evidence.viewport.width/2,(1-v.y)*evidence.viewport.height/2];const actual=dot.transform.match(/translate\(([-.\d]+)px,\s*([-.\d]+)px\)/)?.slice(1).map(Number);assert.ok(actual&&Math.hypot(actual[0]-expected[0],actual[1]-expected[1])<2,"Marker dot disagrees with actual world position: "+dot.id);}
  return evidence;
}
async function catalogState(page) {
  const notice=page.locator('[data-event-catalog="unavailable"]');
  if(process.env.GULLYVERSE_EXPECT_CATALOG_UNAVAILABLE==="1")await notice.waitFor({timeout:30000});
  if(await notice.count()) {assert.equal(await notice.innerText(),"Event listings are currently unavailable. Please try again later.");return "unavailable";}
  return "not asserted against live catalog data";
}
try {
  const context=await browser.newContext({viewport:{width:1366,height:768},deviceScaleFactor:1});
  const page=await guardedPage(context);
  await page.goto(base+"/?diagnostics",{waitUntil:"domcontentloaded"});
  await page.waitForSelector('[data-phase="landing"]',{timeout:60000});
  assert.deepEqual(await pose(page),{x:world.landing.position[0],y:world.landing.position[1],z:world.landing.position[2],yaw:world.landing.yaw,pitch:world.landing.pitch});
  const canvas=await page.locator("canvas").evaluateHandle(c=>c);
  await page.getByRole("button",{name:"Enter Gullyverse",exact:true}).click();
  const entrance=[];
  while((await state(page)).phase==="entrance") {entrance.push(await pose(page));await page.waitForTimeout(150);}
  await waitLocal(page,"hub");
  assert.ok(entrance.length>15);assert.ok(entrance.some(p=>p.z<world.tunnel.endZ+5));
  assert.ok(entrance.some(p=>Math.abs(p.x)>2),"Cinematic path follows the physical bend rather than a straight sightline");
  assert.equal(await page.evaluate(c=>document.querySelector("canvas")===c,canvas),true);
  checks.push({name:"landing and physically connected bent entrance choreography",landing:world.landing,entranceSamples:entrance,persistentCanvas:true,note:"Occlusion and clipping additionally require reviewing real screenshots; coordinate success is not visual acceptance."});
  const hubPose=await pose(page);
  await page.mouse.move(620,320);await page.mouse.down();await page.mouse.move(720,320,{steps:8});await page.mouse.up();await page.waitForTimeout(300);
  assert.equal((await state(page)).phase,"local");assert.equal((await state(page)).destinationMenu,false);
  assert.ok(Math.hypot((await pose(page)).x-hubPose.x,(await pose(page)).z-hubPose.z)<.01,"Turning alone never triggers destination travel");
  checks.push({name:"hub look alone causes no travel or destination-selection menu",before:hubPose,after:await pose(page)});
  const saved=await pose(page);
  await page.keyboard.press("KeyM");
  await page.waitForFunction(()=>window.__gullyverse.runtime.mapProgress>.15,{timeout:10000});
  const ascent=await page.evaluate(()=>({camera:window.__gullyverse.runtime.cameraPose(innerWidth/innerHeight),progress:window.__gullyverse.runtime.mapProgress,stage:window.__gullyverse.runtime.getSnapshot().mapStage}));
  assert.ok(ascent.camera.y>saved.y+1,"Map camera rises from the visitor");
  await key(page,"KeyW",250);assert.deepEqual(await pose(page),saved,"Map freezes exact walking pose");
  await page.waitForFunction(()=>window.__gullyverse.runtime.getSnapshot().mapStage==="open",{timeout:10000});
  const markerEvidence=await verifyMarkers(page);
  assert.ok(markerEvidence.rect.width>=1300 && markerEvidence.rect.height>=700,"Map uses the full viewport");
  for(const label of ["Aftermovie","Team","Contact Us","Accommodation","Past Sponsors","Entrance"]){assert.equal(await page.getByRole("button",{name:label,exact:true}).count(),1);}
  assert.equal(await page.getByRole("button",{name:"Accommodation",exact:true}).isDisabled(),true);
  assert.equal(await page.getByRole("button",{name:"Past Sponsors",exact:true}).isDisabled(),true);
  await page.keyboard.press("Escape");await page.waitForFunction(()=>!window.__gullyverse.runtime.getSnapshot().map,{timeout:10000});assert.deepEqual(await pose(page),saved);
  await page.keyboard.press("KeyM");await page.waitForFunction(()=>window.__gullyverse.runtime.getSnapshot().mapStage==="open");
  await page.keyboard.press("KeyM");await page.waitForFunction(()=>!window.__gullyverse.runtime.getSnapshot().map);assert.deepEqual(await pose(page),saved);
  checks.push({name:"continuous aerial ascent, fullscreen markers, movement ownership, Esc/M exact pose restoration and unavailable markers",saved,ascent,markerEvidence});
  console.log("[browser] connected entrance, looking and aerial-map projection/pose checks passed");
  await mapTravel(page,"Aftermovie","aftermovie");
  assert.equal(await page.evaluate(c=>document.querySelector("canvas")===c,canvas),true);
  const beforePlay=await pose(page);
  await page.getByRole("button",{name:"Play Aftermovie",exact:true}).click();
  await page.waitForFunction(()=>window.__gullyverse.runtime.movieActions.status().currentTime>.1,{timeout:30000});
  await page.getByRole("button",{name:"Enable sound",exact:true}).click();
  assert.equal(await page.evaluate(()=>window.__gullyverse.runtime.movieActions.status().muted),false);
  await page.keyboard.press("Escape");await page.waitForFunction(()=>!window.__gullyverse.runtime.getSnapshot().movie);await page.waitForTimeout(1000);assert.deepEqual(await pose(page),beforePlay);
  assert.equal((await state(page)).destinationMenu,false,"Playback Escape cannot simultaneously navigate/open menu");
  await key(page,"KeyD",150);await page.waitForTimeout(350);assert.equal((await state(page)).destinationMenu,false,"Interior walking is not outer boundary contact");
  await contactBoundary(page,["KeyS"]);
  const edgePose=await pose(page);assert.equal(new URL(page.url()).pathname,"/aftermovie");
  await page.waitForTimeout(300);assert.deepEqual(await pose(page),edgePose);
  const overlay=await menu(page).evaluate(el=>{const s=getComputedStyle(el);return{rect:el.getBoundingClientRect().toJSON(),background:s.backgroundColor,backgroundImage:s.backgroundImage,border:s.borderWidth,children:[...el.children].map(c=>({tag:c.tagName,background:getComputedStyle(c).backgroundColor}))};});
  assert.equal(overlay.backgroundImage,"none");assert.ok(overlay.rect.width>=1300 && overlay.rect.height>=700,"The dimmer spans the scene, not a modal card");
  assert.ok(overlay.children.every(c=>["rgba(0, 0, 0, 0)","transparent"].includes(c.background)),"Typography overlay has no nested rectangular panel");
  assert.equal(await menu(page).getByRole("button",{name:"Aftermovie",exact:true}).count(),0,"No redundant current-location destination");
  await page.keyboard.press("Escape");assert.equal((await state(page)).destinationMenu,false);assert.deepEqual(await pose(page),edgePose);
  await key(page,"KeyS",600);assert.equal((await state(page)).destinationMenu,false,"Outward contact remains latched until moving away");
  await key(page,"KeyW",500);await contactBoundary(page,["KeyS"]);
  await menu(page).getByRole("button",{name:"Stay Here",exact:true}).click();assert.deepEqual(await pose(page),edgePose);
  await key(page,"KeyW",500);await contactBoundary(page,["KeyS"]);
  await menu(page).getByRole("button",{name:"Return to Hub",exact:true}).click();await waitLocal(page,"hub");
  assert.equal(await page.evaluate(c=>document.querySelector("canvas")===c,canvas),true);
  await page.goBack();await waitLocal(page,"aftermovie");await page.goForward();await waitLocal(page,"hub");
  checks.push({name:"playback Escape/unmute, edge clamps without leaving, text-only overlay, Esc/Stay pose preservation, hysteresis, chosen covered return and history",edgePose,overlay,persistentCanvas:true});
  console.log("[browser] playback, text overlay, hysteresis, covered choice and history checks passed");
  await canvas.dispose();
  // Reloading the direct URL isolates each direction from prior edge latch state.
  // Inputs remain public keyboard controls; no test teleportation of the player.
  for(const [name,keys] of [["front",["KeyW"]],["rear",["KeyS"]],["left",["KeyA"]],["right",["KeyD"]],["front-left",["KeyW","KeyA"]],["front-right",["KeyW","KeyD"]],["rear-left",["KeyS","KeyA"]],["rear-right",["KeyS","KeyD"]]]) {
    await page.goto(base+"/aftermovie?diagnostics",{waitUntil:"domcontentloaded"});await waitLocal(page,"aftermovie");
    const initial=await pose(page);await contactBoundary(page,keys);const stopped=await pose(page);
    assert.equal((await state(page)).phase,"local");assert.equal(new URL(page.url()).pathname,"/aftermovie");
    const [xmin,xmax,zmin,zmax]=world.aftermovie.bounds;
    assert.ok(stopped.x>=xmin-1e-5 && stopped.x<=xmax+1e-5 && stopped.z>=zmin-1e-5 && stopped.z<=zmax+1e-5);
    const polygon=world.aftermovie.movementBoundary;
    const clearance=Math.min(...polygon.map((a,i)=>{const b=polygon[(i+1)%polygon.length],dx=b[0]-a[0],dz=b[1]-a[1];return((stopped.x-a[0])*dz-(stopped.z-a[1])*dx)/Math.hypot(dx,dz)-world.playerRadius;}));
    assert.ok(Math.abs(clearance)<.001,"Menu caused by perimeter contact, including capsule radius");
    await page.waitForTimeout(200);assert.deepEqual(await pose(page),stopped);
    await page.keyboard.press("Escape");assert.deepEqual(await pose(page),stopped);
    checks.push({name:"public Aftermovie perimeter "+name,keys,initial,stopped,staysUntilChoice:true});
    console.log("[browser] outer perimeter "+name+" passed");
  }
  for(const edge of [1,3,5,7]) {
    await page.goto(base+"/aftermovie?diagnostics",{waitUntil:"domcontentloaded"});await waitLocal(page,"aftermovie");
    const initial=await pose(page),polygon=world.aftermovie.movementBoundary,a=polygon[edge],b=polygon[(edge+1)%polygon.length],target=[(a[0]+b[0])/2,world.eyeHeight,(a[1]+b[1])/2];
    await lookToward(page,target);await contactBoundary(page,["KeyW"]);const stopped=await pose(page),dx=b[0]-a[0],dz=b[1]-a[1];
    const clearance=((stopped.x-a[0])*dz-(stopped.z-a[1])*dx)/Math.hypot(dx,dz)-world.playerRadius;
    assert.ok(Math.abs(clearance)<.001,"Contact must reach the requested irregular corner segment "+edge);
    assert.equal((await state(page)).phase,"local");assert.equal(new URL(page.url()).pathname,"/aftermovie");
    checks.push({name:"public Aftermovie chamfered corner segment "+edge,initial,target,stopped,staysUntilChoice:true});
    console.log("[browser] chamfered corner "+edge+" passed");
  }
  for(const zone of world.hub.travelZones) {
    await page.goto(base+"/aftermovie?diagnostics",{waitUntil:"domcontentloaded"});await waitLocal(page,"aftermovie");
    await mapTravel(page,"Gullyverse hub","hub");
    const initial=await pose(page),a=world.hub.movementBoundary[zone.edge],b=world.hub.movementBoundary[(zone.edge+1)%world.hub.movementBoundary.length];
    const t=(zone.range[0]+zone.range[1])/2,target=[a[0]+(b[0]-a[0])*t,world.eyeHeight,a[1]+(b[1]-a[1])*t];
    await lookToward(page,target);const started=Date.now();await page.keyboard.down("KeyW");
    if(["accommodation","sponsors"].includes(zone.id)) {
      await page.waitForFunction(id=>window.__gullyverse.runtime.getSnapshot().unavailableDestination===id,zone.id,{timeout:15000});await page.keyboard.up("KeyW");
      const unavailable=await state(page);assert.equal(unavailable.phase,"local");assert.equal(unavailable.scene,"hub");assert.equal(unavailable.destinationMenu,false);
      assert.ok((await page.getByRole("status").allInnerTexts()).some(text=>text.includes("Coming soon")));
      checks.push({name:"deliberate local hub zone "+(zone.sign??zone.id),destination:zone.id,initial,target,approachMs:Date.now()-started,available:false,truthfulNotice:true});
    } else {
      await page.waitForSelector('[data-phase="departure"]',{timeout:15000});await page.keyboard.up("KeyW");
      const approachMs=Date.now()-started;
      if(zone.id==="aftermovie")await waitLocal(page,"aftermovie");
      else await page.waitForURL(base+world.destinations.find(d=>d.id===zone.id).href,{timeout:60000});
      checks.push({name:"deliberate local hub zone "+(zone.sign??zone.id),destination:zone.id,initial,target,approachMs,available:true,finalPath:new URL(page.url()).pathname,...zone.id==="events"?{catalogState:await catalogState(page)}:{}});
    }
    console.log("[browser] local hub travel segment "+(zone.sign??zone.id)+" passed");
  }
  await page.goto(base+"/aftermovie?diagnostics",{waitUntil:"domcontentloaded"});await waitLocal(page,"aftermovie");
  await page.emulateMedia({reducedMotion:"reduce"});
  const reducedSaved=await pose(page);await page.keyboard.press("KeyM");await page.waitForFunction(()=>window.__gullyverse.runtime.getSnapshot().mapStage==="open",{timeout:5000});
  await page.keyboard.press("Escape");await page.waitForFunction(()=>!window.__gullyverse.runtime.getSnapshot().map,{timeout:5000});assert.deepEqual(await pose(page),reducedSaved);
  checks.push({name:"reduced motion map uses shortened transition and restores exact pose",saved:reducedSaved});
  // Existing pages are read only. No form submission or authenticated DB work.
  for(const path of ["/events","/events/cultural","/events/technical","/events/00000000-0000-4000-8000-000000000001","/team","/get-in-touch","/sponsors","/merch","/admin/login"]) {
    const response=await page.goto(base+path,{waitUntil:"domcontentloaded"});await page.waitForTimeout(1000);assert.equal(response.status(),200);
    checks.push({name:"preserved content route",path,finalPath:new URL(page.url()).pathname,status:response.status(),inputs:await page.locator("input").count(),textareas:await page.locator("textarea").count(),...path.startsWith("/events")?{catalogState:await catalogState(page)}:{}});
  }
  await context.close();
  const mobile=await browser.newContext({viewport:{width:390,height:844},deviceScaleFactor:1,isMobile:true,hasTouch:true});
  const touchPage=await guardedPage(mobile);
  await touchPage.goto(base+"/aftermovie?diagnostics",{waitUntil:"domcontentloaded"});await waitLocal(touchPage,"aftermovie");
  await contactBoundary(touchPage,["KeyS"]);const touchEdge=await pose(touchPage);
  await menu(touchPage).getByRole("button",{name:"Stay Here",exact:true}).tap();assert.deepEqual(await pose(touchPage),touchEdge);assert.equal((await state(touchPage)).destinationMenu,false);
  await touchPage.getByRole("button",{name:/^Map/}).tap();await touchPage.waitForFunction(()=>window.__gullyverse.runtime.getSnapshot().mapStage==="open",{timeout:10000});
  assert.ok(await touchPage.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
  const touchMarkers=await verifyMarkers(touchPage);
  await touchPage.getByRole("button",{name:"Gullyverse hub",exact:true}).tap();await waitLocal(touchPage,"hub");
  checks.push({name:"portrait touch Stay Here, fullscreen map without overflow/marker overlap or clipping, actual world projection and marker navigation",touchEdge,touchMarkers});
  await mobile.close();
  assert.deepEqual(errors,[]);assert.deepEqual(mutations,[]);
  await writeFile(dir+"/browser-checks.json",JSON.stringify({checks,errors,mutations,limitations:["Real clipping/occlusion/composition require visual review.","Map projection accuracy also covered by runtime tests and captured camera metadata.","Mobile checks run on desktop Intel GPU."]},null,2));
  await unlink(dir+"/browser-failure.txt").catch(error=>{if(error.code!=="ENOENT")throw error;});
  console.log(JSON.stringify({checks:checks.length,errors,mutations}));
} catch(error) {await writeFile(dir+"/browser-checks.json",JSON.stringify({partial:true,checks,errors,mutations,error:String(error.stack??error)},null,2));await writeFile(dir+"/browser-failure.txt",String(error.stack??error));throw error;}
finally {await browser.close();}
