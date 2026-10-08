import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import type { ImmersiveRuntime } from "./runtime";

export type FrameSample = { at: number; ms: number; phase: string; scene: string; poseZ: number; cpuRenderMs?: number; cpuUpdateMs?: number };
type TimedSample = { at: number; ms: number; phase: string; scene: string; serial: number; name: string; poseZ: number };
type TimerExtension = { TIME_ELAPSED_EXT: number; GPU_DISJOINT_EXT: number };
type MemorySample = { at: number; scene: string; geometries: number; textures: number; activeGeometryBytes: number; activeTextureBytesEstimate: number; jsHeapBytes: number | null };
export type Diagnostics = {
  runtime: ImmersiveRuntime; renderer: string;
  frames: FrameSample[]; timeline: FrameSample[]; preparations: TimedSample[]; gpu: TimedSample[];
  phases: { at: number; phase: string; scene: string; serial: number }[]; memory: MemorySample[];
  gpuTimer: "available" | "unavailable"; discardedGpuQueries: number;
  currentFrame: FrameSample | null;
  stats: { calls: number; triangles: number; textures: number; geometries: number; dpr: number };
};
declare global { interface Window { __gullyverse?: Diagnostics } }
function append<T>(items: T[], item: T, limit = 12000) {
  items.push(item); if (items.length > limit) items.splice(0, Math.min(600, items.length));
}
export function recordPreparation(runtime: ImmersiveRuntime, name: string, at: number, ms: number) {
  const d = window.__gullyverse;
  if (d?.runtime !== runtime) return;
  const s = runtime.getSnapshot();
  append(d.preparations, { name, at, ms, phase: s.phase, scene: s.scene, serial: s.serial, poseZ: runtime.pose.z }, 1000);
}

/** Source payload estimates only. Driver allocations, padding and VRAM are not exposed by WebGL. */
export function sampleMemory(scene: THREE.Scene, gl: THREE.WebGLRenderer, runtime: ImmersiveRuntime) {
  const d = window.__gullyverse; if (d?.runtime !== runtime) return;
  const buffers = new Set<ArrayBufferLike>(), textures = new Set<THREE.Texture>();
  let activeGeometryBytes = 0, activeTextureBytesEstimate = 0;
  const addAttribute = (attr: THREE.BufferAttribute | THREE.InterleavedBufferAttribute) => {
    const array = attr instanceof THREE.InterleavedBufferAttribute ? attr.data.array : attr.array;
    if (!buffers.has(array.buffer)) { buffers.add(array.buffer); activeGeometryBytes += array.buffer.byteLength; }
  };
  scene.traverse((object) => {
    if (!(object instanceof THREE.Mesh) && !(object instanceof THREE.Points) && !(object instanceof THREE.Line)) return;
    Object.values(object.geometry.attributes).forEach(addAttribute);
    if (object.geometry.index) addAttribute(object.geometry.index);
    if (object instanceof THREE.InstancedMesh) { addAttribute(object.instanceMatrix); if (object.instanceColor) addAttribute(object.instanceColor); }
    for (const material of Array.isArray(object.material) ? object.material : [object.material]) {
      Object.values(material).forEach((v) => { if (v instanceof THREE.Texture) textures.add(v); });
      if (material instanceof THREE.ShaderMaterial) Object.values(material.uniforms).forEach((v) => { if (v.value instanceof THREE.Texture) textures.add(v.value); });
    }
  });
  textures.forEach((texture) => {
    if (texture instanceof THREE.CompressedTexture) {
      activeTextureBytesEstimate += texture.mipmaps.reduce((bytes, mip) => bytes + mip.data.byteLength, 0);
    } else {
      const source = texture.image as { width?: number; height?: number; videoWidth?: number; videoHeight?: number } | undefined;
      activeTextureBytesEstimate += (source?.videoWidth || source?.width || 0) * (source?.videoHeight || source?.height || 0) * 4 * (texture.generateMipmaps ? 4 / 3 : 1);
    }
  });
  const memory = (performance as Performance & { memory?: { usedJSHeapSize: number } }).memory;
  append(d.memory, { at: performance.now(), scene: runtime.getSnapshot().scene, geometries: gl.info.memory.geometries, textures: gl.info.memory.textures, activeGeometryBytes, activeTextureBytesEstimate, jsHeapBytes: memory?.usedJSHeapSize ?? null }, 1000);
}

/** Opt-in instrumentation; never waits synchronously for GPU completion or publishes React state. */
export function installDiagnostics(gl: THREE.WebGLRenderer, runtime: ImmersiveRuntime) {
  if (!new URLSearchParams(window.location.search).has("diagnostics")) return () => {};
  const context = gl.getContext() as WebGL2RenderingContext;
  const debug = context.getExtension("WEBGL_debug_renderer_info");
  let timer = context.getExtension("EXT_disjoint_timer_query_webgl2") as TimerExtension | null;
  const d: Diagnostics = window.__gullyverse = {
    runtime, renderer: String(context.getParameter(debug ? debug.UNMASKED_RENDERER_WEBGL : context.RENDERER)),
    frames: [], timeline: [], preparations: [], gpu: [], phases: [], memory: [], currentFrame: null,
    gpuTimer: timer ? "available" : "unavailable", discardedGpuQueries: 0,
    stats: { calls: 0, triangles: 0, textures: 0, geometries: 0, dpr: gl.getPixelRatio() },
  };
  let lastPhase = "", frame = 0;
  const phase = () => {
    const s = runtime.getSnapshot(), signature = `${s.phase}:${s.scene}:${s.serial}`;
    if (signature !== lastPhase) { lastPhase = signature; append(d.phases, { at: performance.now(), phase: s.phase, scene: s.scene, serial: s.serial }, 1000); }
  };
  phase(); const unsubscribe = runtime.subscribe(phase);
  const pending: { query: WebGLQuery; sample: TimedSample }[] = [];
  const clearQueries = () => { pending.forEach(({ query }) => context.deleteQuery(query)); pending.length = 0; };
  const lost = () => { d.discardedGpuQueries += pending.length; pending.length = 0; timer = null; };
  const restored = () => { timer = context.getExtension("EXT_disjoint_timer_query_webgl2") as TimerExtension | null; d.gpuTimer = timer ? "available" : "unavailable"; };
  gl.domElement.addEventListener("webglcontextlost", lost);
  gl.domElement.addEventListener("webglcontextrestored", restored);
  const originalRender = gl.render;
  gl.render = function (scene, camera) {
    if (runtime.suspended || context.isContextLost()) { originalRender.call(gl, scene, camera); return; }
    const start = performance.now(), s = runtime.getSnapshot();
    // One timer every twelve rendered frames, bounded to eight outstanding queries.
    const sampleGpu = timer && ++frame % 12 === 0;
    if (sampleGpu) {
      const disjoint = context.getParameter(timer!.GPU_DISJOINT_EXT);
      for (let i = pending.length - 1; i >= 0; i--) {
        const item = pending[i];
        if (disjoint || context.getQueryParameter(item.query, context.QUERY_RESULT_AVAILABLE)) {
          if (!disjoint) append(d.gpu, { ...item.sample, ms: Number(context.getQueryParameter(item.query, context.QUERY_RESULT)) / 1e6 });
          else d.discardedGpuQueries++;
          context.deleteQuery(item.query); pending.splice(i, 1);
        }
      }
    }
    const query = sampleGpu && pending.length < 8 ? context.createQuery() : null;
    if (query) context.beginQuery(timer!.TIME_ELAPSED_EXT, query);
    try { originalRender.call(gl, scene, camera); }
    finally {
      if (query) {
        context.endQuery(timer!.TIME_ELAPSED_EXT);
        pending.push({ query, sample: { name: "gpu-render", at: start, ms: 0, phase: s.phase, scene: s.scene, serial: s.serial, poseZ: runtime.pose.z } });
      }
      if (d.currentFrame) d.currentFrame.cpuRenderMs = performance.now() - start;
      Object.assign(d.stats, { calls: gl.info.render.calls, triangles: gl.info.render.triangles, textures: gl.info.memory.textures, geometries: gl.info.memory.geometries, dpr: gl.getPixelRatio() });
    }
  };
  // GLTF parse includes asynchronous image decoding; elapsed wall time is not CPU-only decode time.
  const originalParse = GLTFLoader.prototype.parse;
  const measuredParse: GLTFLoader["parse"] = function (data, path, onLoad, onError) {
    const start = performance.now();
    originalParse.call(this, data, path, (result) => { recordPreparation(runtime, "gltf-parse-to-ready", start, performance.now() - start); onLoad(result); }, onError);
  };
  GLTFLoader.prototype.parse = measuredParse;
  return () => {
    unsubscribe(); clearQueries(); gl.render = originalRender;
    gl.domElement.removeEventListener("webglcontextlost", lost); gl.domElement.removeEventListener("webglcontextrestored", restored);
    if (GLTFLoader.prototype.parse === measuredParse) GLTFLoader.prototype.parse = originalParse;
    if (window.__gullyverse === d) delete window.__gullyverse;
  };
}
