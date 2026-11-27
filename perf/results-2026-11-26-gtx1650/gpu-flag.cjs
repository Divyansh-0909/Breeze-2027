// Preload (node -r): append --force_high_performance_gpu to every Playwright Chromium launch,
// so Chrome picks the discrete NVIDIA GPU instead of the integrated Intel one. Resolves playwright
// from the current working directory so it patches the same instance the perf scripts import.
const { createRequire } = require("node:module");
const path = require("node:path");
const req = createRequire(path.join(process.cwd(), "package.json"));
const { chromium } = req("playwright");
const launch = chromium.launch.bind(chromium);
// Also use real Chrome (CHROME_PATH) for scripts that do not pass an executablePath themselves (perf-functional.mjs):
// Playwright's bundled headless shell renders this scene at ~1 fps on this machine.
chromium.launch = (options = {}) => launch({
  ...(process.env.CHROME_PATH && !options.executablePath ? { executablePath: process.env.CHROME_PATH } : {}),
  ...options, args: [...(options.args ?? []), "--force_high_performance_gpu"],
});
