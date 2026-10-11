// Read-only portability adapter: existing test source remains unchanged.
import { chromium } from 'playwright';
import { pathToFileURL } from 'node:url';
import path from 'node:path';
const originalLaunch=chromium.launch.bind(chromium);
chromium.launch=async(options={})=>{
  const opts={...options,executablePath:'/usr/bin/chromium'};delete opts.channel;
  const browser=await originalLaunch(opts);
  if(process.env.AUDIT_DPR){
    const make=browser.newContext.bind(browser);
    browser.newContext=options=>make({...options,deviceScaleFactor:Number(options?.isMobile||options?.hasTouch?process.env.AUDIT_MOBILE_DPR||process.env.AUDIT_DPR:process.env.AUDIT_DPR)});
  }
  return browser;
};
console.log(JSON.stringify({adapter:'system Chromium in place of Windows Chrome/Edge; source untouched',desktopDPR:process.env.AUDIT_DPR??'as original',mobileDPR:process.env.AUDIT_MOBILE_DPR??'as original',target:process.argv[2]}));
await import(pathToFileURL(path.resolve(process.argv[2])).href);
