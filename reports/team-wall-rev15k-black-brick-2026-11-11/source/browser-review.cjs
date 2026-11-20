const {chromium}=require('/workspace/Breeze-2027/node_modules/playwright');
const fs=require('node:fs/promises');
const path=require('node:path');
const root=path.resolve(__dirname,'..');
(async()=>{
 const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});
 try {
  const page=await browser.newPage({viewport:{width:1600,height:900},deviceScaleFactor:1});
  const errors=[],failed=[],checks=[];
  page.on('pageerror',e=>errors.push(String(e)));
  page.on('console',m=>{if(m.type()==='error')errors.push(m.text())});
  page.on('requestfailed',r=>failed.push({url:r.url(),error:r.failure()?.errorText}));
  await page.goto('http://127.0.0.1:8775/',{waitUntil:'networkidle'});
  const settled=async index=>page.waitForFunction(index=>window.teamCarousel?.stats().index===index&&window.teamCarousel.stats().visibleSlides===1&&document.querySelector('#status').hidden,index,{timeout:60000});
  await settled(0);
  const manifest=JSON.parse(await fs.readFile(path.join(root,'viewer/carousel.json'),'utf8'));
  if(manifest.slides[0].headingText!=='ORGANISING COMMITTEE')throw Error('Heading is abbreviated');
  if(manifest.slides.length!==8||manifest.order.includes('Coordinators'))throw Error('Wrong carousel order');
  for(let index=0;index<8;index++){
   if(index)await page.getByRole('button',{name:'Next team',exact:true}).click();
   await settled(index);
   checks.push({check:'next-button',...await page.evaluate(()=>window.teamCarousel.stats())});
   if([0,1,6,7].includes(index))await page.screenshot({path:path.join(root,'renders/browser-'+String(index)+'-laptop.png')});
  }
  await page.keyboard.press('ArrowRight');await settled(0);
  checks.push({check:'keyboard-wrap-to-OC',...await page.evaluate(()=>window.teamCarousel.stats())});
  await page.getByRole('button',{name:'Previous team',exact:true}).click();await settled(7);
  checks.push({check:'previous-button-wrap-to-Web',...await page.evaluate(()=>window.teamCarousel.stats())});
  await page.reload({waitUntil:'networkidle'});await settled(7);
  checks.push({check:'reload-selection',...await page.evaluate(()=>window.teamCarousel.stats())});
  await page.evaluate(()=>window.teamCarousel.show(0));await settled(0);
  const allocations=[];
  for(let i=0;i<3;i++){
   await page.evaluate(()=>window.teamCarousel.show(7));await settled(7);
   await page.evaluate(()=>window.teamCarousel.show(0));await settled(0);
   allocations.push(await page.evaluate(()=>window.teamCarousel.stats()));
  }
  const wall=await page.evaluate(()=>({sourceMaterials:window.sourceWallMaterials.records,brick:window.teamCarousel.stats().brick}));
  await page.setViewportSize({width:390,height:844});
  await page.screenshot({path:path.join(root,'renders/browser-oc-phone.png')});
  const horizontalOverflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth);
  const result={status:errors.length||failed.length||horizontalOverflow?'FAIL':'PASS',defaultTeam:manifest.order[0],slideCount:manifest.slides.length,checks,wallMaterials:wall,allocations,horizontalOverflow,errors,failed,renderer:'Chromium SwiftShader; real-device performance not established'};
  await fs.writeFile(path.join(root,'evidence/browser.json'),JSON.stringify(result,null,2));
  console.log(JSON.stringify(result,null,2));
  if(result.status!=='PASS')throw Error('Browser review failed');
 } finally {await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
