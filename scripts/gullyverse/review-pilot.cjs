const { chromium } = require("playwright"),
  fs = require("node:fs/promises");
const R = "/workspace/Breeze-2027/reports/art-lock-implementation-2026-11-14";
(async () => {
  const browser = await chromium.launch({
    executablePath: "/usr/bin/chromium",
    headless: true,
    args: [
      "--no-sandbox",
      "--enable-unsafe-swiftshader",
      "--use-gl=angle",
      "--use-angle=swiftshader",
      "--disable-crash-reporter",
      "--disable-breakpad",
    ],
  });
  try {
    const page = await browser.newPage({
        viewport: { width: 1440, height: 900 },
        deviceScaleFactor: 1,
      }),
      errors = [],
      failures = [];
    page.on("pageerror", (e) => errors.push(String(e)));
    page.on("console", (m) => {
      if (m.type() === "error") errors.push(m.text());
    });
    page.on("requestfailed", (r) => failures.push(r.url()));
    await page.goto("http://127.0.0.1:8893/", { waitUntil: "networkidle" });
    await page.waitForFunction(() => window.__lockedPilot?.ready(), null, {
      timeout: 90000,
    });
    await page.waitForTimeout(1000);
    await page.screenshot({
      path: R + "/renders/m1-png-laptop.jpg",
      type: "jpeg",
      quality: 94,
    });
    const baseline = await page.evaluate(() => __lockedPilot.stats());
    await fs.writeFile(
      R + "/scratch/browser-baseline.json",
      JSON.stringify({ baseline, errors, failures }, null, 2),
    );
    console.log(JSON.stringify({ baseline, errors, failures }));
  } finally {
    await browser.close();
  }
})().catch((e) => {
  console.error(e);
  process.exitCode = 1;
});
