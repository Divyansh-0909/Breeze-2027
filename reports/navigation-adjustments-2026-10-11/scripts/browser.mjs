import { chromium } from 'playwright';
import { readFile, writeFile } from 'node:fs/promises';
import assert from 'node:assert/strict';
const root = 'reports/navigation-adjustments-2026-10-11';
const mode = process.argv[2] || 'baseline';
const base = process.env.GULLYVERSE_BASE_URL || 'http://127.0.0.1:3000';
const world = JSON.parse(await readFile('public/models/gullyverse/blockout.layout.json', 'utf8'));
const browser = await chromium.launch({ executablePath: '/usr/bin/chromium', headless: true, args: ['--no-sandbox', '--enable-unsafe-swiftshader', '--use-gl=angle', '--use-angle=swiftshader'] });
const context = await browser.newContext({ viewport: { width: 1366, height: 900 }, deviceScaleFactor: .25 });
const page = await context.newPage(), errors = [], captures = [], checks = [];
page.on('pageerror', error => errors.push(error.message));
await page.route('**/api/**', route => ['GET', 'HEAD'].includes(route.request().method()) ? route.continue() : route.abort());
const local = id => page.waitForSelector(`[data-phase="local"][data-location="${id}"]`, { timeout: 90000 });
try {
  await page.goto(base + '/?arrival=hub&diagnostics', { waitUntil: 'domcontentloaded' });
  await local('hub');
  await page.evaluate(() => {
    const r = window.__gullyverse.runtime;
    window.__walkTrace = [];
    r.subscribe(() => window.__walkTrace.push({ at: performance.now(), state: r.getSnapshot(), pose: { ...r.pose }, opacity: r.opacity }));
    window.__walkingCanvas = document.querySelector('canvas');
  });
  await page.keyboard.down('KeyW');
  if (mode === 'baseline') {
    await page.waitForFunction(limit => window.__gullyverse.runtime.pose.z < limit, world.hub.bounds[2] + world.playerRadius + .1, { timeout: 60000 });
    await page.waitForTimeout(400);
    await page.keyboard.up('KeyW');
    const blocked = await page.evaluate(() => ({ state: window.__gullyverse.runtime.getSnapshot(), pose: { ...window.__gullyverse.runtime.pose } }));
    assert.equal(blocked.state.phase, 'local');
    assert.equal(blocked.state.scene, 'hub');
    checks.push({ name: 'Reported forward boundary blockage reproduced', ...blocked });
    await page.screenshot({ path: `${root}/baseline/blocked-before-scaffold.png`, scale: 'css' });
  } else {
    await page.waitForFunction(() => window.__gullyverse.runtime.getSnapshot().serial > 0, null, { timeout: 90000 });
    await page.keyboard.up('KeyW');
    await local('aftermovie');
    const trip = await page.evaluate(() => ({ trace: window.__walkTrace, sameCanvas: document.querySelector('canvas') === window.__walkingCanvas }));
    const departure = trip.trace.find(entry => entry.state.phase === 'departure');
    assert.ok(departure && departure.pose.z < world.scaffold.position[2], 'Public forward walking passes beneath the scaffold before travel');
    assert.ok(trip.trace.some(entry => entry.state.phase === 'covered' && entry.opacity === 1), 'Destination preparation is covered');
    assert.ok(trip.trace.some(entry => entry.state.phase === 'arrival'), 'Existing arrival animation runs');
    assert.equal(trip.sameCanvas, true);
    checks.push({ name: 'Forward walking through scaffold fades to Aftermovie on the same Canvas', ...trip });
    await page.screenshot({ path: `${root}/acceptance/forward-aftermovie-arrival.png`, scale: 'css' });
    await page.keyboard.down('KeyS');
    await page.getByRole('dialog', { name: 'Where to next?' }).waitFor({ timeout: 60000 });
    await page.keyboard.up('KeyS');
    await page.getByRole('button', { name: 'Return to Hub', exact: true }).click();
    await local('hub');
    checks.push({ name: 'Existing return path', state: await page.evaluate(() => window.__gullyverse.runtime.getSnapshot()) });
    await page.getByRole('button', { name: /^Map/ }).click();
    await page.waitForSelector('[data-map-stage="open"]', { timeout: 30000 });
    for (const id of ['team', 'contact']) {
      const marker = await page.locator(`[data-map-point="${id}"]`).getAttribute('data-world-position');
      assert.equal(marker, world.destinations.find(destination => destination.id === id).position.join(','));
    }
    assert.equal(await page.locator('svg line').evaluateAll(lines => lines.some(line => ['x1', 'x2', 'y1', 'y2'].some(attribute => !Number.isFinite(Number(line.getAttribute(attribute)))))), false);
    await page.screenshot({ path: `${root}/acceptance/map.png`, scale: 'css' });
    await page.keyboard.press('Escape');
    await page.waitForFunction(() => !window.__gullyverse.runtime.getSnapshot().map, null, { timeout: 30000 });
    checks.push({ name: 'Map markers follow the relocated second stalls and projections stay finite' });
  }
  const views = [
    { id: 'scaffold', position: [0, 1.72, -51], target: [0, 8, -70] },
    { id: 'left-stalls', position: [-10, 1.72, -54], target: [-24, 2.5, -78] },
    { id: 'right-stalls', position: [10, 1.72, -54], target: [24, 2.5, -78] },
    { id: 'quarry', position: [0, 6, -51], target: [0, 4, -92] },
  ];
  for (const view of views) {
    await page.evaluate(view => {
      const r = window.__gullyverse.runtime;
      r.setQuality(3); r.inspectionEnabled = true; r.inspect('quarry');
      const [x, y, z] = view.position, [tx, ty, tz] = view.target;
      r.cameraPose = () => ({ x, y, z, yaw: Math.atan2(-(tx-x), -(tz-z)), pitch: Math.atan2(ty-y, Math.hypot(tx-x,tz-z)), fov: 58 });
    }, view);
    await page.waitForTimeout(600);
    const file = `${view.id}.png`;
    await page.screenshot({ path: `${root}/${mode === 'baseline' ? 'baseline' : 'acceptance'}/${file}`, scale: 'css' });
    captures.push({ ...view, file, fov: 58, viewport: { width: 1366, height: 900 }, requestedDpr: .25, diagnostics: await page.evaluate(() => ({ quality: window.__gullyverse.runtime.getSnapshot().quality, stats: window.__gullyverse.stats })) });
  }
  if (mode !== 'baseline') {
    await context.close();
    const mobile = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: .25, isMobile: true, hasTouch: true });
    const touchPage = await mobile.newPage();
    touchPage.on('pageerror', error => errors.push(error.message));
    await touchPage.route('**/api/**', route => ['GET', 'HEAD'].includes(route.request().method()) ? route.continue() : route.abort());
    await touchPage.goto(base + '/?arrival=hub&diagnostics', { waitUntil: 'domcontentloaded' });
    await touchPage.waitForSelector('[data-phase="local"][data-location="hub"]', { timeout: 90000 });
    await touchPage.screenshot({ path: `${root}/acceptance/mobile-hub.png`, scale: 'css' });
    const pad = await touchPage.getByRole('button', { name: 'Walk forward', exact: true }).boundingBox();
    assert.ok(pad, 'Forward touch control is visible');
    const session = await mobile.newCDPSession(touchPage);
    await session.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x: pad.x + pad.width / 2, y: pad.y + pad.height / 2 }] });
    await touchPage.waitForFunction(() => window.__gullyverse.runtime.getSnapshot().serial > 0, null, { timeout: 90000 });
    await session.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] });
    await touchPage.waitForSelector('[data-phase="local"][data-location="aftermovie"]', { timeout: 90000 });
    checks.push({ name: 'Portrait touch hold through scaffold reaches Aftermovie', device: 'Chromium touch emulation; no physical mobile GPU claim' });
    await touchPage.screenshot({ path: `${root}/acceptance/mobile-aftermovie.png`, scale: 'css' });
    await mobile.close();
  }
  assert.deepEqual(errors, []);
  await writeFile(`${root}/${mode === 'baseline' ? 'baseline' : 'acceptance'}/results.json`, JSON.stringify({ base, mode, checks, captures, pageErrors: errors }, null, 2));
  console.log(JSON.stringify({ mode, checks: checks.map(c => c.name), captures: captures.length, pageErrors: errors }));
} finally { await browser.close(); }
