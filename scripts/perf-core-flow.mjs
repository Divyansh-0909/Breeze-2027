// The core flow now lives in one persistent Canvas. Measure rendered R3F frames
// and the complete hub/Aftermovie loop using the production regression runner.
if (!process.env.GULLYVERSE_BASE_URL && process.env.PERF_BASE_URL) process.env.GULLYVERSE_BASE_URL = process.env.PERF_BASE_URL;
const runs = Math.max(1, Number(process.argv[2] ?? process.env.PERF_RUNS ?? 1));
for (let run = 0; run < runs; run++) {
  await import(`./perf-gullyverse.mjs?run=${run}`);
  if (process.exitCode) break;
}
