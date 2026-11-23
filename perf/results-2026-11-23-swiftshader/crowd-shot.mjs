import { chromium } from "playwright";
const [files, out, w = "1400", h = "700", extra = ""] = process.argv.slice(2);
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: +w, height: +h } });
page.on("pageerror", e => console.log("pageerror", e.message));
await page.goto(`http://127.0.0.1:8765/index.html?files=${files}${extra}`);
await page.waitForFunction(() => document.title === "done", null, { timeout: 600000 });
await page.screenshot({ path: out, timeout: 300000 });
await browser.close();
