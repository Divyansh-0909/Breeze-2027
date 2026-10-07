import { spawn } from "node:child_process";
import { mkdtemp, rm } from "node:fs/promises";
import os from "node:os";
import path from "node:path";

const chromePath = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const baseUrl = process.env.PERF_BASE_URL ?? "http://127.0.0.1:3000";
const runs = Number(process.argv[2] ?? process.env.PERF_RUNS ?? 1);
const profileGate = process.env.PERF_PROFILE_GATE === "1";

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function waitForJson(url, timeoutMs = 15_000) {
  const started = Date.now();
  let lastError;
  while (Date.now() - started < timeoutMs) {
    try {
      const response = await fetch(url);
      if (response.ok) return await response.json();
    } catch (error) {
      lastError = error;
    }
    await sleep(100);
  }
  throw lastError ?? new Error(`Timed out waiting for ${url}`);
}

class CdpClient {
  constructor(url) {
    this.url = url;
    this.nextId = 1;
    this.pending = new Map();
    this.listeners = new Map();
  }

  async connect() {
    this.ws = new WebSocket(this.url);
    await new Promise((resolve, reject) => {
      this.ws.addEventListener("open", resolve, { once: true });
      this.ws.addEventListener("error", reject, { once: true });
    });
    this.ws.addEventListener("message", (event) => {
      const message = JSON.parse(event.data);
      if (message.id) {
        const pending = this.pending.get(message.id);
        if (!pending) return;
        this.pending.delete(message.id);
        if (message.error) pending.reject(new Error(message.error.message));
        else pending.resolve(message.result ?? {});
        return;
      }
      const listeners = this.listeners.get(message.method);
      if (listeners) for (const listener of listeners) listener(message.params ?? {});
    });
  }

  send(method, params = {}) {
    const id = this.nextId++;
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
      this.ws.send(JSON.stringify({ id, method, params }));
    });
  }

  on(method, listener) {
    if (!this.listeners.has(method)) this.listeners.set(method, new Set());
    this.listeners.get(method).add(listener);
  }

  close() {
    this.ws?.close();
  }
}

async function evaluate(client, expression) {
  const result = await client.send("Runtime.evaluate", {
    expression,
    awaitPromise: true,
    returnByValue: true,
  });
  if (result.exceptionDetails) {
    throw new Error(result.exceptionDetails.text ?? "Runtime.evaluate failed");
  }
  return result.result?.value;
}

async function waitFor(client, expression, timeoutMs = 20_000, intervalMs = 50) {
  const started = Date.now();
  while (Date.now() - started < timeoutMs) {
    if (await evaluate(client, expression)) return;
    await sleep(intervalMs);
  }
  throw new Error(`Timed out waiting for: ${expression}`);
}

async function clickPoint(client, x, y) {
  await client.send("Input.dispatchMouseEvent", { type: "mousePressed", x, y, button: "left", clickCount: 1 });
  await client.send("Input.dispatchMouseEvent", { type: "mouseReleased", x, y, button: "left", clickCount: 1 });
}

function metricMap(metrics = []) {
  return Object.fromEntries(metrics.map(({ name, value }) => [name, value]));
}

function quantile(values, q) {
  if (!values.length) return 0;
  const sorted = [...values].sort((a, b) => a - b);
  const index = Math.min(sorted.length - 1, Math.floor((sorted.length - 1) * q));
  return sorted[index];
}

function summarizeFrames(intervals) {
  const active = intervals.filter((value) => value < 1000);
  return {
    samples: active.length,
    avgMs: active.reduce((sum, value) => sum + value, 0) / Math.max(active.length, 1),
    p95Ms: quantile(active, 0.95),
    p99Ms: quantile(active, 0.99),
    maxMs: Math.max(0, ...active),
    over34ms: active.filter((value) => value > 34).length,
    over50ms: active.filter((value) => value > 50).length,
  };
}

function summarizeCpuProfile(profile) {
  if (!profile?.nodes?.length || !profile?.samples?.length) return [];
  const nodeById = new Map(profile.nodes.map((node) => [node.id, node]));
  const selfMicros = new Map();
  for (let index = 0; index < profile.samples.length; index += 1) {
    const nodeId = profile.samples[index];
    const delta = profile.timeDeltas?.[index] ?? 0;
    selfMicros.set(nodeId, (selfMicros.get(nodeId) ?? 0) + delta);
  }
  return [...selfMicros.entries()]
    .map(([nodeId, micros]) => {
      const frame = nodeById.get(nodeId)?.callFrame ?? {};
      return {
        functionName: frame.functionName || "(anonymous)",
        url: frame.url || "",
        line: (frame.lineNumber ?? -1) + 1,
        selfMs: micros / 1000,
      };
    })
    .filter((entry) => entry.selfMs > 1)
    .sort((a, b) => b.selfMs - a.selfMs)
    .slice(0, 20);
}

async function runOnce(index) {
  const profileDir = await mkdtemp(path.join(os.tmpdir(), `breeze-perf-${index}-`));
  const port = 9222 + index;
  const chrome = spawn(chromePath, [
    `--remote-debugging-port=${port}`,
    `--user-data-dir=${profileDir}`,
    "--headless=new",
    "--window-size=1440,900",
    "--no-first-run",
    "--no-default-browser-check",
    "--disable-extensions",
    "--disable-background-timer-throttling",
    "--disable-backgrounding-occluded-windows",
    "--disable-renderer-backgrounding",
    "about:blank",
  ], { stdio: "ignore" });

  let browser;
  let page;
  try {
    const version = await waitForJson(`http://127.0.0.1:${port}/json/version`);
    browser = new CdpClient(version.webSocketDebuggerUrl);
    await browser.connect();

    const tabs = await waitForJson(`http://127.0.0.1:${port}/json`);
    const target = tabs.find((tab) => tab.type === "page");
    if (!target) throw new Error("No Chrome page target found");
    page = new CdpClient(target.webSocketDebuggerUrl);
    await page.connect();

    await Promise.all([
      page.send("Page.enable"),
      page.send("Runtime.enable"),
      page.send("Performance.enable"),
      page.send("Network.enable"),
      ...(profileGate ? [page.send("Profiler.enable")] : []),
    ]);

    if (profileGate) {
      await page.send("Profiler.setSamplingInterval", { interval: 100 });
      await page.send("Profiler.start");
    }

    const network = { encodedBytes: 0, resources: 0 };
    page.on("Network.loadingFinished", ({ encodedDataLength = 0 }) => {
      network.encodedBytes += encodedDataLength;
      network.resources += 1;
    });

    await page.send("Page.addScriptToEvaluateOnNewDocument", {
      source: `
        (() => {
          const data = window.__breezePerf = {
            start: performance.now(),
            frames: [],
            longTasks: [],
            events: [],
            phases: [],
            lcp: 0,
          };
          let last = performance.now();
          const tick = (now) => {
            data.frames.push(now - last);
            if (data.frames.length > 5000) data.frames.shift();
            last = now;
            requestAnimationFrame(tick);
          };
          requestAnimationFrame(tick);
          try {
            new PerformanceObserver((list) => {
              for (const entry of list.getEntries()) data.longTasks.push({ start: entry.startTime, duration: entry.duration });
            }).observe({ type: 'longtask', buffered: true });
          } catch {}
          try {
            new PerformanceObserver((list) => {
              for (const entry of list.getEntries()) {
                data.events.push({ name: entry.name, start: entry.startTime, duration: entry.duration, interactionId: entry.interactionId || 0 });
              }
            }).observe({ type: 'event', buffered: true, durationThreshold: 16 });
          } catch {}
          try {
            new PerformanceObserver((list) => {
              const entries = list.getEntries();
              const lastEntry = entries[entries.length - 1];
              if (lastEntry) data.lcp = lastEntry.startTime;
            }).observe({ type: 'largest-contentful-paint', buffered: true });
          } catch {}
          const observePhases = () => {
            const node = document.querySelector('[data-phase]');
            if (!node) return;
            const capture = () => data.phases.push({ phase: node.getAttribute('data-phase'), at: performance.now() });
            capture();
            new MutationObserver(capture).observe(node, { attributes: true, attributeFilter: ['data-phase'] });
          };
          new MutationObserver(() => {
            if (document.querySelector('[data-phase]')) {
              observePhases();
              return;
            }
          }).observe(document, { childList: true, subtree: true });
        })();
      `,
    });

    const cpuBefore = await browser.send("SystemInfo.getProcessInfo");
    const navStartedWall = Date.now();
    await page.send("Page.navigate", { url: baseUrl });
    await waitFor(page, `document.readyState === 'complete'`, 30_000);
    await waitFor(page, `document.querySelector('[data-phase]')?.getAttribute('data-phase') === 'ready'`, 20_000);
    const gateCpuProfile = profileGate ? (await page.send("Profiler.stop")).profile : null;

    const nav = await evaluate(page, `(() => {
      const n = performance.getEntriesByType('navigation')[0];
      const fcp = performance.getEntriesByName('first-contentful-paint')[0];
      return {
        loadMs: n ? n.loadEventEnd - n.startTime : 0,
        domContentLoadedMs: n ? n.domContentLoadedEventEnd - n.startTime : 0,
        ttfbMs: n ? n.responseStart - n.requestStart : 0,
        transferBytes: n ? n.transferSize : 0,
        fcpMs: fcp?.startTime ?? 0,
      };
    })()`);

    const readyAt = await evaluate(page, `window.__breezePerf.phases.find((p) => p.phase === 'ready')?.at ?? performance.now()`);

    const gateCenter = await evaluate(page, `(() => {
      const r = document.querySelector('[data-phase]').getBoundingClientRect();
      return { x: r.left + r.width / 2, y: r.top + r.height / 2 };
    })()`);
    const enterClickAt = await evaluate(page, `performance.now()`);
    await clickPoint(page, gateCenter.x, gateCenter.y);
    await waitFor(page, `document.querySelector('[data-phase]')?.getAttribute('data-phase') === 'arrived'`, 15_000);
    const arrivedAt = await evaluate(page, `window.__breezePerf.phases.find((p) => p.phase === 'arrived')?.at ?? performance.now()`);
    const enteringAt = await evaluate(page, `window.__breezePerf.phases.find((p) => p.phase === 'entering')?.at ?? performance.now()`);

    const aftermovieCenter = await evaluate(page, `(() => {
      const a = [...document.querySelectorAll('a')].find((el) => el.getAttribute('href') === '/aftermovie');
      if (!a) return null;
      const r = a.getBoundingClientRect();
      return { x: r.left + r.width / 2, y: r.top + r.height / 2 };
    })()`);
    if (!aftermovieCenter) throw new Error("Aftermovie link not found after arrival");
    const aftermovieClickAt = await evaluate(page, `performance.now()`);
    await clickPoint(page, aftermovieCenter.x, aftermovieCenter.y);
    await waitFor(page, `location.pathname === '/aftermovie'`, 12_000);
    const aftermovieRouteAt = await evaluate(page, `performance.now()`);
    await waitFor(page, `!document.querySelector('video[src="/travel-crowd.mp4"]')`, 24_000, 100);
    const revealAt = await evaluate(page, `performance.now()`);

    const perf = await evaluate(page, `(() => ({
      data: window.__breezePerf,
      heapUsed: performance.memory?.usedJSHeapSize ?? 0,
      heapTotal: performance.memory?.totalJSHeapSize ?? 0,
      location: location.href,
      canvases: document.querySelectorAll('canvas').length,
      webglRenderer: (() => {
        const c = document.querySelector('canvas');
        const gl = c?.getContext('webgl2') || c?.getContext('webgl');
        if (!gl) return null;
        const ext = gl.getExtension('WEBGL_debug_renderer_info');
        return ext ? gl.getParameter(ext.UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER);
      })(),
    }))()`);
    const pageMetrics = metricMap((await page.send("Performance.getMetrics")).metrics);
    const dom = await page.send("Memory.getDOMCounters");
    const cpuAfter = await browser.send("SystemInfo.getProcessInfo");

    const beforeCpu = Object.fromEntries((cpuBefore.processInfo ?? []).map((p) => [p.id, p.cpuTime]));
    const cpuByType = {};
    for (const process of cpuAfter.processInfo ?? []) {
      const delta = Math.max(0, process.cpuTime - (beforeCpu[process.id] ?? 0));
      cpuByType[process.type] = (cpuByType[process.type] ?? 0) + delta;
    }
    const cpuSeconds = Object.values(cpuByType).reduce((sum, value) => sum + value, 0);
    const wallSeconds = (Date.now() - navStartedWall) / 1000;

    const frames = summarizeFrames(perf.data.frames ?? []);
    const longTasks = perf.data.longTasks ?? [];
    const interactionEvents = (perf.data.events ?? []).filter((event) => event.interactionId);

    return {
      run: index,
      nav,
      timings: {
        gateReadyMs: readyAt,
        enterResponseMs: Math.max(0, enteringAt - enterClickAt),
        tunnelTravelMs: Math.max(0, arrivedAt - enteringAt),
        aftermovieRouteMs: Math.max(0, aftermovieRouteAt - aftermovieClickAt),
        aftermovieRevealMs: Math.max(0, revealAt - aftermovieClickAt),
        flowWallMs: wallSeconds * 1000,
      },
      responsiveness: {
        maxInteractionEventMs: Math.max(0, ...interactionEvents.map((event) => event.duration)),
        p95InteractionEventMs: quantile(interactionEvents.map((event) => event.duration), 0.95),
        interactionEventCount: interactionEvents.length,
      },
      frames,
      longTasks: {
        count: longTasks.length,
        totalMs: longTasks.reduce((sum, task) => sum + task.duration, 0),
        maxMs: Math.max(0, ...longTasks.map((task) => task.duration)),
      },
      cpu: {
        totalCpuSeconds: cpuSeconds,
        averageCpuPercentOfOneCore: wallSeconds ? (cpuSeconds / wallSeconds) * 100 : 0,
        byTypeSeconds: cpuByType,
        rendererTaskSeconds: pageMetrics.TaskDuration ?? 0,
        scriptSeconds: pageMetrics.ScriptDuration ?? 0,
      },
      memory: {
        jsHeapUsedMB: perf.heapUsed / 1024 / 1024,
        jsHeapTotalMB: perf.heapTotal / 1024 / 1024,
        documents: dom.documents,
        nodes: dom.nodes,
        jsEventListeners: dom.jsEventListeners,
      },
      network: {
        encodedMB: network.encodedBytes / 1024 / 1024,
        resources: network.resources,
      },
      render: {
        lcpMs: perf.data.lcp ?? 0,
        canvases: perf.canvases,
        webglRenderer: perf.webglRenderer,
      },
      ...(gateCpuProfile ? { gateCpuHotspots: summarizeCpuProfile(gateCpuProfile) } : {}),
    };
  } finally {
    page?.close();
    browser?.close();
    chrome.kill();
    await sleep(300);
    try {
      await rm(profileDir, { recursive: true, force: true, maxRetries: 3, retryDelay: 200 });
    } catch (error) {
      if (error?.code !== "EBUSY") throw error;
    }
  }
}

const results = [];
for (let index = 0; index < runs; index += 1) {
  const result = await runOnce(index + 1);
  results.push(result);
  process.stdout.write(`${JSON.stringify(result)}\n`);
}

if (results.length > 1) {
  const median = (selector) => quantile(results.map(selector), 0.5);
  process.stdout.write(`${JSON.stringify({
    summary: "median",
    runs: results.length,
    loadMs: median((r) => r.nav.loadMs),
    fcpMs: median((r) => r.nav.fcpMs),
    gateReadyMs: median((r) => r.timings.gateReadyMs),
    enterResponseMs: median((r) => r.timings.enterResponseMs),
    aftermovieRouteMs: median((r) => r.timings.aftermovieRouteMs),
    aftermovieRevealMs: median((r) => r.timings.aftermovieRevealMs),
    flowWallMs: median((r) => r.timings.flowWallMs),
    cpuPercent: median((r) => r.cpu.averageCpuPercentOfOneCore),
    cpuSeconds: median((r) => r.cpu.totalCpuSeconds),
    jsHeapUsedMB: median((r) => r.memory.jsHeapUsedMB),
    frameP95Ms: median((r) => r.frames.p95Ms),
    frameMaxMs: median((r) => r.frames.maxMs),
    framesOver50ms: median((r) => r.frames.over50ms),
    longTaskCount: median((r) => r.longTasks.count),
    longTaskMaxMs: median((r) => r.longTasks.maxMs),
    networkMB: median((r) => r.network.encodedMB),
  })}\n`);
}
