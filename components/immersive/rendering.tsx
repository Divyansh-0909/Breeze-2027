"use client";
import { useEffect, useRef } from "react";
import { useFrame, useThree } from "@react-three/fiber";
import * as THREE from "three";
import type { ImmersiveRuntime } from "./runtime";
import { installDiagnostics, recordPreparation, sampleMemory, type FrameSample } from "./diagnostics";
import { world } from "./world";

/** The whole critical scene must instantiate before this gate mounts. */
export function ReadinessGate({ runtime, serial }: { runtime: ImmersiveRuntime; serial: number }) {
  const { gl, scene, camera } = useThree();
  const prepared = useRef(false);
  const rendered = useRef(0);
  const warmStartedAt = useRef(0);
  const warmEuler = useRef(new THREE.Euler(0, 0, 0, "YXZ"));
  const warm = useRef({ count: 0, seconds: 0, done: false });
  useEffect(() => {
    let alive = true;
    prepared.current = false; rendered.current = 0; warmStartedAt.current = 0;
    warm.current = { count: 0, seconds: 0, done: false };
    void (async () => {
      if (gl.getContext().isContextLost()) return;
      const started = performance.now();
      const textures = new Set<THREE.Texture>();
      scene.traverse((object) => {
        if (!(object instanceof THREE.Mesh) && !(object instanceof THREE.Points) && !(object instanceof THREE.Line)) return;
        const materials = Array.isArray(object.material) ? object.material : [object.material];
        for (const material of materials) {
          for (const value of Object.values(material)) if (value instanceof THREE.Texture && !(value instanceof THREE.VideoTexture)) textures.add(value);
          if (material instanceof THREE.ShaderMaterial) for (const uniform of Object.values(material.uniforms)) if (uniform.value instanceof THREE.Texture && !(uniform.value instanceof THREE.VideoTexture)) textures.add(uniform.value);
        }
      });
      textures.forEach((texture) => gl.initTexture(texture));
      recordPreparation(runtime, "texture-initialization", started, performance.now() - started);
      const compileStart = performance.now();
      // KHR_parallel_shader_compile when available; Three falls back to compile.
      await gl.compileAsync(scene, camera);
      recordPreparation(runtime, "shader-compilation", compileStart, performance.now() - compileStart);
      if (alive && serial === runtime.getSnapshot().serial && !gl.getContext().isContextLost()) {
        prepared.current = true; runtime.preparedSerial = serial;
      }
    })().catch((error) => {
      if (alive && serial === runtime.getSnapshot().serial && !gl.getContext().isContextLost()) runtime.fail(`Scene preparation failed: ${String(error)}`);
    });
    return () => { alive = false; };
  }, [gl, scene, camera, runtime, serial]);
  useFrame((_, dt) => {
    if (!prepared.current || warm.current.done || gl.getContext().isContextLost() || runtime.suspended) return;
    // Warm the final viewing composition under the curtain. The approach pose
    // culls more crowd and previously underestimated the cost of the reveal.
    // Recovery warms the exact saved pose; it never relocates the visitor.
    const view = runtime.preparationPose();
    camera.position.set(view.x, view.y, view.z);
    warmEuler.current.set(view.pitch, view.yaw, 0, "YXZ"); camera.quaternion.setFromEuler(warmEuler.current);
    if (!warmStartedAt.current) warmStartedAt.current = performance.now();
    // First flush upload frames, then measure a short real-render window. If
    // the crowd exceeds the budget, lower its cost BEFORE giving input back.
    if (++rendered.current <= 2) return;
    warm.current.seconds += dt; warm.current.count++;
    // Twelve frames resist isolated initialization spikes while still measuring
    // the real scene. Four frames incorrectly selected the lowest tier under CPU throttling.
    if (warm.current.count < 12) return;
    const quality = runtime.getSnapshot().quality;
    if (runtime.getSnapshot().scene === "aftermovie" && warm.current.seconds / warm.current.count > 1 / 55 && quality < 3) {
      runtime.setQuality(quality + 1);
      rendered.current = 0; warm.current.count = warm.current.seconds = 0;
      return;
    }
    // Hidden renders upload geometry and exercise actual programs at the chosen DPR.
    // Animation clocks keep running during compile; actual draws start only after preparation.
    warm.current.done = true;
    recordPreparation(runtime, "readiness-render-window", warmStartedAt.current, performance.now() - warmStartedAt.current);
    runtime.markReady(serial);
  });
  return null;
}

export const QUALITY_DPR = [1.25, 1, 0.75, 0.6];
export function SceneRenderer({ runtime }: { runtime: ImmersiveRuntime }) {
  useFrame(({ gl, scene, camera }) => {
    const state = runtime.getSnapshot();
    // Avoid triggering synchronous shader creation by drawing a partially mounted
    // scene before its gate. This does not stop R3F's animation loop or camera ticks.
    if (["context-lost", "recovering", "boot", "covered"].includes(state.phase) && runtime.preparedSerial !== state.serial) return;
    gl.render(scene, camera);
  }, 1);
  return null;
}
export function FrameController({ runtime, curtain }: { runtime: ImmersiveRuntime; curtain: React.RefObject<HTMLDivElement | null> }) {
  const { gl, scene, setDpr } = useThree();
  const memoryAt = useRef(0);
  const windowStats = useRef({ elapsed: 0, count: 0, fast: 0, cooldown: 0 });
  const poseEuler = useRef(new THREE.Euler(0, 0, 0, "YXZ"));
  useEffect(() => {
    setDpr(Math.min(window.devicePixelRatio, QUALITY_DPR[runtime.getSnapshot().quality]));
    // Opt-in authoring camera: absent from standard production builds and UI.
    const query = new URLSearchParams(window.location.search);
    runtime.inspectionEnabled = (process.env.NODE_ENV === "development" || process.env.NEXT_PUBLIC_GULLYVERSE_INSPECTION === "1") && query.has("diagnostics");
    if (runtime.inspectionEnabled && query.has("inspect")) runtime.inspect(query.get("inspect"));
    return installDiagnostics(gl, runtime);
  }, [runtime, gl, setDpr]);
  useEffect(() => {
    const lost = (event: Event) => {
      event.preventDefault(); runtime.loseContext();
      if (curtain.current) curtain.current.style.opacity = "1";
    };
    const restored = () => runtime.restoreContext();
    gl.domElement.addEventListener("webglcontextlost", lost);
    gl.domElement.addEventListener("webglcontextrestored", restored);
    return () => {
      gl.domElement.removeEventListener("webglcontextlost", lost);
      gl.domElement.removeEventListener("webglcontextrestored", restored);
    };
  }, [runtime, gl, curtain]);
  useFrame(({ camera }, delta) => {
    const updateStart = performance.now();
    runtime.tick(delta);
    const p = runtime.cameraPose(camera instanceof THREE.PerspectiveCamera ? camera.aspect : 16/9);
    camera.position.set(p.x, p.y, p.z);
    if (camera instanceof THREE.PerspectiveCamera && camera.fov !== p.fov) { camera.fov = p.fov; camera.updateProjectionMatrix(); }
    poseEuler.current.set(p.pitch, p.yaw, 0, "YXZ");
    camera.quaternion.setFromEuler(poseEuler.current);
    if (curtain.current) curtain.current.style.opacity = String(runtime.opacity);
    const state = runtime.getSnapshot();
    const diagnostics = window.__gullyverse;
    if (diagnostics && !runtime.suspended) {
      const sample: FrameSample = { at: updateStart, ms: delta * 1000, phase: state.phase, scene: state.scene, poseZ: p.z, cpuUpdateMs: performance.now() - updateStart };
      diagnostics.currentFrame = sample;
      diagnostics.frames.push(sample); diagnostics.timeline.push(sample);
      if (diagnostics.frames.length > 3600) diagnostics.frames.splice(0, 600);
      if (diagnostics.timeline.length > 12000) diagnostics.timeline.splice(0, 600);
      if (updateStart - memoryAt.current > 1000) { memoryAt.current = updateStart; sampleMemory(scene, gl, runtime); }
    }
    // Ignore loading, focus changes, and tab restore in the quality decision.
    if (state.phase !== "local" || runtime.suspended || state.map || state.movie || state.inspection || delta > 0.25) { windowStats.current.elapsed = windowStats.current.count = 0; return; }
    const w = windowStats.current;
    w.elapsed += delta; w.count++;
    if (w.elapsed < 2) return;
    const average = w.elapsed / w.count; w.elapsed = w.count = 0;
    if (w.cooldown > 0) { w.cooldown--; return; }
    let quality = state.quality;
    if (average > 1 / 55 && quality < 3) { quality++; w.fast = 0; w.cooldown = 1; }
    else if (average < 1 / 59 && quality > 0 && ++w.fast >= 10) { quality--; w.fast = 0; w.cooldown = 10; }
    else if (average >= 1 / 59) w.fast = 0;
    if (quality !== state.quality) { setDpr(Math.min(window.devicePixelRatio, QUALITY_DPR[quality])); runtime.setQuality(quality); }
  }, -1);
  return null;
}
