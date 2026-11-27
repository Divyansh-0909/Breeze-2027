"use client";
/**
 * Opt-in performance instrumentation for the gully (`?diagnostics`, or `?perf=overlay` for the on-screen
 * developer overlay). Ordinary visits install nothing. It records:
 * - presentation intervals from requestAnimationFrame timestamps (not GPU execution time);
 * - CPU time spent submitting each render, and GPU time from EXT_disjoint_timer_query_webgl2 when the
 *   browser exposes it (sampled every sixth frame, never waited on; disjoint results are discarded);
 * - renderer counters after each render (draw calls, triangles, points, lines, programs, geometries,
 *   textures), drawing-buffer size, DPR and quality tier;
 * - load marks (`breeze:*` performance marks) and the number of pending chunk loads.
 * `window.__breezePerf.snapshot()` returns everything as JSON; the overlay can download it. No visitor
 * data is collected.
 */
import { useEffect } from "react";
import { useThree } from "@react-three/fiber";
import * as THREE from "three";
import type { ImmersiveRuntime } from "../immersive/runtime";
import { deviceBudget } from "./device-tier";

type Frame = { at: number; ms: number; cpuRenderMs: number; calls: number; triangles: number; z: number };
type TimerExtension = { TIME_ELAPSED_EXT: number; GPU_DISJOINT_EXT: number };

/** Shared, mutation-only load state (no React updates). */
export const gullyLoads = { pending: 0, chunks: {} as Record<string, { started: number; ready?: number; failed?: boolean }> };
export const tier = { name: "fixed", dpr: 1, changes: [] as { at: number; from: string; to: string; dpr: number; reason: string }[] };

export function markLoad(name: string, phase: "start" | "ready" | "failed") {
  const now = performance.now();
  if (phase === "start") { gullyLoads.pending++; gullyLoads.chunks[name] = { started: now }; }
  else { gullyLoads.pending = Math.max(0, gullyLoads.pending - 1); const chunk = gullyLoads.chunks[name]; if (chunk) { chunk.ready = now; chunk.failed = phase === "failed"; } }
  performance.mark(`breeze:chunk-${phase}:${name}`);
}

const quantile = (sorted: number[], q: number) => sorted.length ? sorted[Math.min(sorted.length - 1, Math.floor(sorted.length * q))] : 0;
export function summarise(ms: number[]) {
  const sorted = [...ms].sort((a, b) => a - b), mean = ms.reduce((a, b) => a + b, 0) / Math.max(1, ms.length);
  return {
    frames: ms.length, meanMs: mean, effectiveFps: mean ? 1000 / mean : 0, p50Ms: quantile(sorted, 0.5), p95Ms: quantile(sorted, 0.95),
    p99Ms: quantile(sorted, 0.99), maxMs: sorted.at(-1) ?? 0,
    over16_7: ms.filter(v => v > 16.7).length, over33_3: ms.filter(v => v > 33.3).length, over50: ms.filter(v => v > 50).length,
  };
}

function textureBytes(scene: THREE.Object3D) {
  const textures = new Set<THREE.Texture>(), buffers = new Set<ArrayBufferLike>();
  let geometryBytes = 0, textureBytes = 0, meshes = 0, nodes = 0;
  scene.traverse(object => {
    nodes++;
    if (!(object instanceof THREE.Mesh)) return;
    meshes++;
    const geometry = object.geometry as THREE.BufferGeometry;
    for (const attribute of [...Object.values(geometry.attributes), geometry.index].filter(Boolean) as (THREE.BufferAttribute | THREE.InterleavedBufferAttribute)[]) {
      const array = attribute instanceof THREE.InterleavedBufferAttribute ? attribute.data.array : attribute.array;
      if (!buffers.has(array.buffer)) { buffers.add(array.buffer); geometryBytes += array.buffer.byteLength; }
    }
    for (const material of Array.isArray(object.material) ? object.material : [object.material]) {
      for (const value of Object.values(material)) if (value instanceof THREE.Texture) textures.add(value);
    }
  });
  const sources = new Set<unknown>();
  textures.forEach(texture => {
    if (sources.has(texture.source)) return; // clones share one upload
    sources.add(texture.source);
    if (texture instanceof THREE.CompressedTexture) textureBytes += texture.mipmaps.reduce((sum, mip) => sum + (mip.data as ArrayBufferView).byteLength, 0);
    else {
      const image = texture.image as { width?: number; height?: number; videoWidth?: number; videoHeight?: number } | undefined;
      const bytesPerTexel = texture.type === THREE.HalfFloatType ? 8 : texture.type === THREE.FloatType ? 16 : 4;
      textureBytes += (image?.videoWidth || image?.width || 0) * (image?.videoHeight || image?.height || 0) * bytesPerTexel * (texture.generateMipmaps ? 4 / 3 : 1);
    }
  });
  return { nodes, meshes, uniqueTextureSources: sources.size, textureBytesEstimate: Math.round(textureBytes), geometryBytes };
}

/**
 * Estimated draw calls in the camera's frustum, per chunk (the scene child that holds the mesh) and per
 * material, plus shadow casters and lights. One per visible mesh-and-material group; a BatchedMesh is one
 * multi-draw. Matches gl.info.render.calls closely for this scene (no shadow or post-processing passes).
 */
export function drawBreakdown(scene: THREE.Scene, camera: THREE.Camera) {
  camera.updateMatrixWorld();
  const frustum = new THREE.Frustum().setFromProjectionMatrix(
    new THREE.Matrix4().multiplyMatrices(camera.projectionMatrix, camera.matrixWorldInverse));
  const byChunk: Record<string, number> = {}, byMaterial: Record<string, number> = {};
  let shadowCasters = 0, lights = 0, total = 0;
  const sphere = new THREE.Sphere();
  const visit = (object: THREE.Object3D, chunk: string) => {
    if (!object.visible) return;
    if ((object as THREE.Light).isLight) {
      const light = object as THREE.Light;
      if (light.intensity > 0) { lights++; if (light.castShadow) shadowCasters++; }
    }
    const mesh = object as THREE.Mesh;
    if (mesh.isMesh || (object as THREE.Points).isPoints || (object as THREE.Line).isLine) {
      // A BatchedMesh culls its instances itself and is one multi-draw (its geometry bounds are not the batch's).
      let inView = !object.frustumCulled || (object as THREE.BatchedMesh).isBatchedMesh === true;
      if (!inView) {
        const geometry = mesh.geometry as THREE.BufferGeometry;
        if (!geometry.boundingSphere) geometry.computeBoundingSphere();
        inView = frustum.intersectsSphere(sphere.copy(geometry.boundingSphere!).applyMatrix4(object.matrixWorld));
      }
      if (inView) {
        const materials = Array.isArray(mesh.material) ? mesh.material : [mesh.material];
        const groups = Array.isArray(mesh.material) ? Math.max(1, mesh.geometry.groups.length) : 1;
        total += groups; byChunk[chunk] = (byChunk[chunk] ?? 0) + groups;
        for (const material of materials) byMaterial[material.name || material.type] = (byMaterial[material.name || material.type] ?? 0) + 1;
      }
    }
    for (const child of object.children) visit(child, chunk);
  };
  const chunks: Record<string, unknown> = {};
  for (const child of scene.children) {
    visit(child, String(child.userData.breezeChunk ?? (child.name || child.type)));
    if (child.userData.breezeChunk) chunks[child.userData.breezeChunk] = { collapse: child.userData.collapse, batching: child.userData.batching };
  }
  const top = Object.entries(byMaterial).sort((a, b) => b[1] - a[1]).slice(0, 25);
  return { total, byChunk, topMaterials: Object.fromEntries(top), lights, shadowCasters, chunks };
}

export function GullyDiagnostics({ runtime }: { runtime: ImmersiveRuntime }) {
  const { gl, scene, camera } = useThree();
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const overlayRequested = params.get("perf") === "overlay" || params.get("perf") === "1";
    if (!params.has("diagnostics") && !overlayRequested) return;
    const context = gl.getContext() as WebGL2RenderingContext;
    const debug = context.getExtension("WEBGL_debug_renderer_info");
    const renderer = String(context.getParameter(debug ? debug.UNMASKED_RENDERER_WEBGL : context.RENDERER));
    let timer = context.getExtension("EXT_disjoint_timer_query_webgl2") as TimerExtension | null;
    const frames: Frame[] = [], gpu: { at: number; ms: number }[] = [];
    let discardedGpu = 0, last = 0, frame = 0, cpuRenderMs = 0, raf = 0;
    const pending: { query: WebGLQuery; at: number }[] = [];
    const original = gl.render;
    gl.render = function (s, camera) {
      const start = performance.now();
      const sample = timer && ++frame % 6 === 0;
      if (sample) {
        const disjoint = context.getParameter(timer!.GPU_DISJOINT_EXT);
        for (let i = pending.length - 1; i >= 0; i--) {
          const item = pending[i];
          if (disjoint || context.getQueryParameter(item.query, context.QUERY_RESULT_AVAILABLE)) {
            if (disjoint) discardedGpu++;
            else gpu.push({ at: item.at, ms: Number(context.getQueryParameter(item.query, context.QUERY_RESULT)) / 1e6 });
            context.deleteQuery(item.query); pending.splice(i, 1);
          }
        }
      }
      const query = sample && pending.length < 8 ? context.createQuery() : null;
      if (query) context.beginQuery(timer!.TIME_ELAPSED_EXT, query);
      try { original.call(gl, s, camera); } finally {
        if (query) { context.endQuery(timer!.TIME_ELAPSED_EXT); pending.push({ query, at: start }); }
        cpuRenderMs = performance.now() - start;
        if (gpu.length > 20000) gpu.splice(0, 2000);
      }
    };
    const tick = (now: number) => {
      raf = requestAnimationFrame(tick);
      if (last && !document.hidden) {
        frames.push({ at: now, ms: now - last, cpuRenderMs, calls: gl.info.render.calls, triangles: gl.info.render.triangles, z: runtime.pose.z });
        if (frames.length > 40000) frames.splice(0, 4000);
      }
      last = now;
    };
    raf = requestAnimationFrame(tick);
    let phase = "";
    const phaseMark = () => { const next = runtime.getSnapshot().phase; if (next !== phase) { phase = next; performance.mark(`breeze:phase:${next}`); } };
    phaseMark();
    const unsubscribe = runtime.subscribe(phaseMark);
    const lost = () => { pending.length = 0; timer = null; };
    gl.domElement.addEventListener("webglcontextlost", lost);
    const stats = () => {
      const size = gl.getDrawingBufferSize(new THREE.Vector2());
      return {
        calls: gl.info.render.calls, triangles: gl.info.render.triangles, points: gl.info.render.points, lines: gl.info.render.lines,
        programs: gl.info.programs?.length ?? 0, geometries: gl.info.memory.geometries, textures: gl.info.memory.textures,
        drawingBuffer: [size.x, size.y], dpr: gl.getPixelRatio(), devicePixelRatio: window.devicePixelRatio, tier: tier.name,
        device: deviceBudget().tier,
      };
    };
    const api = {
      renderer, gpuTimer: timer ? "available" : "unavailable",
      frames, gpu,
      stats,
      breakdown: () => drawBreakdown(scene, camera),
      /** Review only: the live scene and camera, for inspection from automation. */
      scene, camera,
      reset() { frames.length = 0; gpu.length = 0; discardedGpu = 0; },
      summary(sinceMs = 0) {
        const recent = frames.filter(f => f.at >= sinceMs);
        return { presentation: summarise(recent.map(f => f.ms)), cpuRender: summarise(recent.map(f => f.cpuRenderMs)),
          gpu: summarise(gpu.filter(g => g.at >= sinceMs).map(g => g.ms)), discardedGpu };
      },
      snapshot() {
        const memory = (performance as Performance & { memory?: { usedJSHeapSize: number; totalJSHeapSize: number } }).memory;
        return {
          at: performance.now(), renderer, gpuTimer: timer ? "available" : "unavailable", userAgent: navigator.userAgent,
          viewport: [window.innerWidth, window.innerHeight], stats: stats(), scene: textureBytes(scene),
          jsHeap: memory ? { used: memory.usedJSHeapSize, total: memory.totalJSHeapSize } : null,
          loads: gullyLoads, tier, pose: { ...runtime.pose }, phase: runtime.getSnapshot().phase,
          marks: performance.getEntriesByType("mark").filter(m => m.name.startsWith("breeze:")).map(m => ({ name: m.name, at: m.startTime })),
          summary: api.summary(),
        };
      },
    };
    (window as unknown as { __breezePerf?: typeof api }).__breezePerf = api;

    let overlay: HTMLElement | null = null, interval = 0;
    if (overlayRequested) {
      overlay = document.createElement("aside");
      overlay.setAttribute("aria-hidden", "true");
      Object.assign(overlay.style, { position: "fixed", top: "8px", right: "8px", zIndex: "9999", padding: "8px 10px", background: "rgba(0,0,0,.75)",
        color: "#cfc", font: "11px/1.35 ui-monospace, monospace", whiteSpace: "pre", borderRadius: "6px", pointerEvents: "auto" });
      const text = document.createElement("div"), save = document.createElement("button");
      save.textContent = "Download JSON"; save.style.marginTop = "6px";
      save.onclick = () => {
        const blob = new Blob([JSON.stringify({ snapshot: api.snapshot(), frames, gpu }, null, 1)], { type: "application/json" });
        const link = document.createElement("a"); link.href = URL.createObjectURL(blob); link.download = `breeze-perf-${Date.now()}.json`; link.click();
        setTimeout(() => URL.revokeObjectURL(link.href), 1000);
      };
      overlay.append(text, save); document.body.append(overlay);
      interval = window.setInterval(() => {
        const since = performance.now() - 5000, s = stats(), m = api.summary(since), p = m.presentation, b = drawBreakdown(scene, camera);
        text.textContent = [`${renderer.slice(0, 48)}`, `FPS ${p.effectiveFps.toFixed(1)}  p50 ${p.p50Ms.toFixed(1)}  p95 ${p.p95Ms.toFixed(1)} ms`,
          `GPU p50 ${m.gpu.frames ? m.gpu.p50Ms.toFixed(1) + " ms" : "n/a"}  CPU render p50 ${m.cpuRender.p50Ms.toFixed(1)} ms`,
          `device ${s.device}  tier ${s.tier}  dpr ${s.dpr.toFixed(2)}  buffer ${s.drawingBuffer.join("x")}`,
          `calls ${s.calls}  tris ${(s.triangles / 1000).toFixed(0)}k  programs ${s.programs}`,
          `lights ${b.lights}  shadow casters ${b.shadowCasters}  in view ${Object.entries(b.byChunk).map(([k, v]) => `${k.replace(/^cypher-|^market-/, "")} ${v}`).join(" ")}`,
          `textures ${s.textures}  geometries ${s.geometries}  loads pending ${gullyLoads.pending}`,
          `z ${runtime.pose.z.toFixed(1)}  phase ${runtime.getSnapshot().phase}`].join("\n");
      }, 500);
    }
    return () => {
      cancelAnimationFrame(raf); clearInterval(interval); overlay?.remove(); unsubscribe();
      gl.render = original; gl.domElement.removeEventListener("webglcontextlost", lost);
      pending.forEach(item => context.deleteQuery(item.query));
      delete (window as unknown as { __breezePerf?: unknown }).__breezePerf;
    };
  }, [gl, scene, camera, runtime]);
  return null;
}
