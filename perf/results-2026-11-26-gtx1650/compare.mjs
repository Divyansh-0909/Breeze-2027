// Compare two perf-breeze result files (baseline vs candidate) by medians across runs.
import { readFileSync } from "node:fs";
const [bf, cf] = process.argv.slice(2);
const B = JSON.parse(readFileSync(bf, "utf8")), C = JSON.parse(readFileSync(cf, "utf8"));
const med = v => { const s = v.filter(Number.isFinite).sort((a, b) => a - b); return s.length ? s[Math.floor(s.length / 2)] : NaN; };
const fmt = (v, d = 1) => Number.isFinite(v) ? (+v.toFixed(d)).toLocaleString("en-US") : "n/a";
const pct = (a, b) => Number.isFinite(a) && Number.isFinite(b) && a ? `${b - a > 0 ? "+" : ""}${Math.round((b - a) / a * 100)}%` : "";
const rows = [];
const row = (section, metric, a, b, d = 1) => rows.push([section, metric, fmt(a, d), fmt(b, d), pct(a, b)]);
const renderer = r => r.poses.find(p => p.snapshot)?.snapshot.renderer;
console.log(`baseline: ${B.environment.label} ${B.environment.startedAt} | candidate: ${C.environment.label} ${C.environment.startedAt}`);
console.log(`renderer: ${renderer(B)} | ${renderer(C)}; Chrome ${C.environment.browser}; ${C.environment.cpus}`);
const errs = r => [...r.load, ...r.poses, ...r.journey, ...r.cycles].filter(e => e.error).map(e => `${e.profile} ${e.stop ?? ""} ${e.error.slice(0, 120)}`);
console.log("baseline errors:", errs(B)); console.log("candidate errors:", errs(C));
for (const profile of ["desktop", "mobile-emulated"]) {
  const L = (r, visit, f) => med(r.load.filter(e => e.profile === profile && e[visit]).map(e => f(e[visit])));
  // Run #0 includes the server's first-request warm-up; report medians of all 3 runs.
  row(profile, "cold: MB before walking", L(B, "cold", v => v.bytesAtWalking.total.bytes / 1e6), L(C, "cold", v => v.bytesAtWalking.total.bytes / 1e6));
  row(profile, "cold: walking unlocked (s)", L(B, "cold", v => v.walkingMs / 1000), L(C, "cold", v => v.walkingMs / 1000));
  row(profile, "cold: whole world ready (s)", L(B, "cold", v => v.worldMs / 1000), L(C, "cold", v => v.worldMs / 1000));
  row(profile, "cold: MB after world + 5 s", L(B, "cold", v => v.bytesAfter5s.total.bytes / 1e6), L(C, "cold", v => v.bytesAfter5s.total.bytes / 1e6));
  row(profile, "warm: walking unlocked (s)", L(B, "warm", v => v.walkingMs / 1000), L(C, "warm", v => v.walkingMs / 1000));
  for (const stop of ["market", "approach", "plaza", "events", "team", "aftermovie"]) {
    const P = (r, f) => med(r.poses.filter(e => e.profile === profile && e.stop === stop && e.summary).map(f));
    row(profile, `${stop}: GPU ms p50`, P(B, e => e.summary.gpu?.p50Ms), P(C, e => e.summary.gpu?.p50Ms), 2);
    row(profile, `${stop}: GPU ms p95`, P(B, e => e.summary.gpu?.p95Ms), P(C, e => e.summary.gpu?.p95Ms), 2);
    row(profile, `${stop}: CPU submit ms p50`, P(B, e => e.summary.cpuRender?.p50Ms), P(C, e => e.summary.cpuRender?.p50Ms), 2);
    row(profile, `${stop}: frame ms p95`, P(B, e => e.summary.presentation.p95Ms), P(C, e => e.summary.presentation.p95Ms));
    row(profile, `${stop}: frames >16.7 ms per 30 s`, P(B, e => e.summary.presentation.over16_7), P(C, e => e.summary.presentation.over16_7), 0);
    row(profile, `${stop}: draw calls`, P(B, e => e.snapshot.stats.calls), P(C, e => e.snapshot.stats.calls), 0);
    row(profile, `${stop}: triangles (k)`, P(B, e => e.snapshot.stats.triangles / 1000), P(C, e => e.snapshot.stats.triangles / 1000), 0);
  }
  const prog = r => med(r.poses.filter(e => e.profile === profile && e.snapshot).map(e => e.snapshot.stats.programs));
  row(profile, "shader programs (median over poses)", prog(B), prog(C), 0);
  const tex = r => med(r.poses.filter(e => e.profile === profile && e.snapshot).map(e => e.snapshot.scene.textureBytesEstimate / 1e6));
  row(profile, "texture MB estimate", tex(B), tex(C), 0);
}
const J = (r, f) => med(r.journey.filter(e => e.walk).map(f));
row("desktop", "walk: frame ms p95", J(B, e => e.walk.p95Ms), J(C, e => e.walk.p95Ms));
row("desktop", "sprint: frame ms p95", J(B, e => e.sprint.presentation.p95Ms), J(C, e => e.sprint.presentation.p95Ms));
row("desktop", "sprint: GPU ms p95", J(B, e => e.sprint.gpu?.p95Ms), J(C, e => e.sprint.gpu?.p95Ms), 2);
const cyc = (r, f) => { const s = r.cycles[0]?.snapshots ?? []; return [f(s[1]), f(s.at(-1))]; };
for (const [name, f, d] of [["JS heap MB", s => s?.jsHeap?.used / 1e6, 0], ["geometries", s => s?.stats.geometries, 0], ["textures", s => s?.stats.textures, 0], ["programs", s => s?.stats.programs, 0]]) {
  const [b1, b10] = cyc(B, f), [c1, c10] = cyc(C, f);
  rows.push(["cycles", `${name} after cycle 1 → 10`, `${fmt(b1, d)} → ${fmt(b10, d)}`, `${fmt(c1, d)} → ${fmt(c10, d)}`, ""]);
}
console.log("\n| profile | metric | baseline 66a7f69 | candidate 8a5e36d | change |\n|---|---|---:|---:|---:|");
for (const r of rows) console.log(`| ${r.join(" | ")} |`);
