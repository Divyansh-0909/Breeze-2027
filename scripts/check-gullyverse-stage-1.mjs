/** Live public-control proof for the connected passage, plus read-only content checks. */
import assert from "node:assert/strict";
import { readFile,writeFile } from "node:fs/promises";
import { chromium } from "playwright";
const base=process.env.GULLYVERSE_BASE_URL ?? "http://localhost:3000";
const dir=".gullyverse-artifacts/stage-1";
const world=JSON.parse(await readFile(new URL("../public/models/gullyverse/blockout.layout.json",import.meta.url),"utf8"));
const browser=await chromium.launch({executablePath:process.env.CHROME_PATH ?? "C:/Program Files/Google/Chrome/Application/chrome.exe",headless:true});
const errors=[],mutations=[],checks=[];
try {
  const page=await browser.newPage({viewport:{width:1366,height:768}});
  page.on("pageerror",e=>errors.push(e.message));
  await page.route("**/api/**",route=>{
    if (!["GET","HEAD"].includes(route.request().method())) {mutations.push(route.request().url());return route.abort();}
    return route.continue();
  });
  await page.goto(base+"/?diagnostics",{waitUntil:"domcontentloaded"});
  await page.waitForSelector('[data-phase="landing"]',{timeout:60000});
  const canvas=await page.locator("canvas").evaluateHandle(c=>c);
  await page.getByRole("button",{name:"Enter Gullyverse"}).click();
  await page.waitForSelector('[data-phase="local"][data-location="hub"]',{timeout:60000});
  const pose=()=>page.evaluate(()=>({...window.__gullyverse.runtime.pose}));
  const key=async(code,ms)=>{await page.keyboard.down(code);await page.waitForTimeout(ms);await page.keyboard.up(code);};
  await key("KeyS",7000);
  await page.waitForTimeout(350); // Let normal walking inertia settle before measuring side collision.
  const inside=await pose();
  assert.ok(inside.z>-28 && inside.z<-15,"Walk backwards into the middle of the carved passage");
  await key("KeyD",1500);
  const wall=await pose();
  assert.ok(Math.abs(wall.x-world.tunnel.walkHalfWidth)<.05);
  assert.ok(Math.abs(wall.z-inside.z)<.1,"Side collision stays local: "+JSON.stringify({inside,wall}));
  await key("KeyA",860);
  await page.keyboard.down("KeyS");
  await page.waitForFunction(z=>window.__gullyverse.runtime.pose.z>=z,world.landing.position[2],{timeout:18000});
  await page.keyboard.up("KeyS");
  const front=await pose();assert.equal(front.y,world.eyeHeight);
  await page.keyboard.down("KeyW");
  await page.waitForFunction(z=>window.__gullyverse.runtime.pose.z<z,world.tunnel.endZ-1,{timeout:25000});
  await page.keyboard.up("KeyW");
  assert.equal(await page.evaluate(c=>document.querySelector("canvas")===c,canvas),true);
  assert.equal(await page.locator('[data-phase="local"][data-location="hub"]').count(),1);
  const {saved,inspection}=await page.evaluate(()=>{
    const runtime=window.__gullyverse.runtime,saved={...runtime.pose};
    return {saved,inspection:runtime.inspect("overview")};
  });
  assert.equal(inspection,process.env.GULLYVERSE_CHECK_INSPECTION!=="disabled");
  if (inspection) {await page.evaluate(()=>window.__gullyverse.runtime.inspect(null));assert.deepEqual(await pose(),saved);}
  checks.push({name:"public keyboard reverse tunnel, side-wall collision, front landing and quarry reentry",inside,wall,front,returned:saved,persistentCanvas:true,inspection});
  await page.getByRole("button",{name:/^Map/}).click();
  await page.getByRole("button",{name:"Aftermovie Travel"}).click();
  await page.waitForSelector('[data-phase="local"][data-location="aftermovie"]',{timeout:60000});
  await page.getByRole("button",{name:"Play Aftermovie",exact:true}).click();
  await page.waitForFunction(()=>window.__gullyverse.runtime.movieActions.status().currentTime>.1);
  await page.getByRole("button",{name:"Enable sound",exact:true}).click();
  assert.equal(await page.evaluate(()=>window.__gullyverse.runtime.movieActions.status().muted),false);
  const film=await pose();await page.goBack();
  await page.waitForSelector('[data-phase="local"][data-location="hub"]',{timeout:60000});
  assert.equal(await page.evaluate(()=>window.__gullyverse.runtime.movieActions.status().phase),"idle");
  checks.push({name:"playback unmute control and browser back stop media through the shared world transition",film,unmuted:true,stoppedOnReturn:true});
  for (const path of ["/team","/get-in-touch","/sponsors","/merch","/admin/login"]) {
    const response=await page.goto(base+path,{waitUntil:"domcontentloaded"});await page.waitForTimeout(1200);
    assert.equal(response.status(),200);
    checks.push({name:"preserved content route",path,finalPath:new URL(page.url()).pathname,status:response.status(),inputs:await page.locator("input").count(),textareas:await page.locator("textarea").count()});
  }
  assert.deepEqual(errors,[]);assert.deepEqual(mutations,[]);
  await writeFile(dir+"/walking-content.json",JSON.stringify({checks,errors,mutations},null,2));
  console.log(JSON.stringify({checks:checks.length,errors,mutations}));
  await canvas.dispose();
} finally {await browser.close();}
