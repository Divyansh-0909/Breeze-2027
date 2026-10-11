from pathlib import Path

def edit(path,old,new):
 p=Path(path);s=p.read_text();assert old in s,(path,old[:80]);p.write_text(s.replace(old,new))
p='components/landing-page/stage3d/useStageVideo.ts'
edit(p,'import * as THREE from "three";','import * as THREE from "three";\nimport { ownVideoTexture, retireVideoTexture } from "./videoTextureOwnership";')
edit(p,'export function useStageVideo() {','export function useStageVideo(onActiveChange?: (active: boolean) => void) {\n  const activeCallback = useRef(onActiveChange);\n  activeCallback.current = onActiveChange;\n  const listeners = useRef<(() => void) | null>(null);')
edit(p,'  const disposalTimers = useRef(new Map<THREE.VideoTexture, ReturnType<typeof setTimeout>>());','')
edit(p,'    const video = videoRef.current;','    listeners.current?.(); listeners.current = null;\n    const video = videoRef.current;',)
edit(p,'    if (tex) disposalTimers.current.set(tex, setTimeout(() => { tex.dispose(); disposalTimers.current.delete(tex); }, 600));','    if (tex) retireVideoTexture(tex);')
edit(p,'videoRef.current = null; textureRef.current = null; setPhase("idle");','videoRef.current = null; textureRef.current = null; activeCallback.current?.(false); setPhase("idle");')
a=Path(p).read_text();start=a.index('    // Unmount owns every outstanding texture');end=a.index('  }, [stopMovie]);',start);a=a[:start]+a[end:];Path(p).write_text(a)
edit(p,'    const tex = new THREE.VideoTexture(video);','    const tex = new THREE.VideoTexture(video);\n    ownVideoTexture(tex);')
s=Path(p).read_text();a=s.index('    video.addEventListener("playing"');b=s.index('    setPhase("loading");',a)
s=s[:a]+'''    const playing = () => {
      if (videoRef.current !== video) return;
      setPhase("playing"); setPyroKey((key) => key + 1);
    };
    const ended = () => { if (videoRef.current === video) stopMovie(); };
    video.addEventListener("playing", playing, { once: true });
    video.addEventListener("ended", ended); video.addEventListener("error", ended);
    listeners.current = () => {
      video.removeEventListener("playing", playing); video.removeEventListener("ended", ended); video.removeEventListener("error", ended);
    };
    activeCallback.current?.(true);
'''+s[b:];Path(p).write_text(s)
edit(p,'void video.play().catch(stopMovie);','void video.play().catch(() => { if (videoRef.current === video) stopMovie(); });')
edit(p,'if (e.key === "Escape") stopMovie();','if (e.key === "Escape" && !(e.target instanceof Element && e.target.closest("form, input, textarea, select, [contenteditable]:not([contenteditable=false])"))) stopMovie();')
p='components/immersive/AftermovieScene.tsx'
edit(p,'  const video = useStageVideo();','  const playbackOwnership = useCallback((active: boolean) => runtime.setMovie(active), [runtime]);\n  const video = useStageVideo(playbackOwnership);')
edit(p,'  useEffect(() => { runtime.setMovie(video.phase !== "idle"); }, [runtime, video.phase]);','')
p='components/landing-page/stage3d/LEDScreens.tsx'
edit(p,'useEffect, useMemo, useRef','useCallback, useEffect, useLayoutEffect, useMemo, useRef')
edit(p,'import { PALETTE, STAGE }','import { retainVideoTexture } from "./videoTextureOwnership";\nimport { PALETTE, STAGE }')
s=Path(p).read_text();a=s.index('  useEffect(() => {\n    if (videoTexture)');b=s.index('\n  // fade timing:',a)
s=s[:a]+'''  const binding = useRef<{ texture: THREE.VideoTexture; release: () => void } | null>(null);
  const detachVideo = useCallback(() => {
    for (const material of materials) material.uniforms.uVideo.value = blankVideo;
    const old = binding.current; binding.current = null;
    old?.release(); // detach ALL sampler references before disposal is permitted
  }, [materials, blankVideo]);
  useLayoutEffect(() => {
    if (!videoTexture) return; // retain during the existing render-driven exit fade
    detachVideo();
    binding.current = { texture: videoTexture, release: retainVideoTexture(videoTexture) };
    for (const material of materials) material.uniforms.uVideo.value = videoTexture;
    // Materials/binding stay stable until replacement or unmount, not a null prop.
  }, [videoTexture, materials, blankVideo, detachVideo]);
  useLayoutEffect(() => () => detachVideo(), [detachVideo]);
'''+s[b:];Path(p).write_text(s)
edit(p,'      fade.current = Math.max(0, fade.current - delta / FADE_OUT);','      fade.current = Math.max(0, fade.current - delta / FADE_OUT);\n      if (fade.current === 0 && binding.current) detachVideo();')
# Finite projection. Existing map layout algorithm and actual 3D camera are preserved.
p='components/immersive/WorldOverlays.tsx'
edit(p,'import styles from','import { projectMapPoint } from "./mapProjection";\nimport styles from')
edit(p,'const vector = useRef(new THREE.Vector3());\n  const previousFrame = useRef("");','const clip = useRef(new THREE.Vector4());')
edit(p,'if (!runtime.getSnapshot().map || !elements.container) { previousFrame.current = ""; return; }','if (!runtime.getSnapshot().map || !elements.container) return;')
s=Path(p).read_text();a=s.index('    const signature =');b=s.index('    camera.updateMatrixWorld();',a);s=s[:a]+s[b:];Path(p).write_text(s)
a=Path(p).read_text();start=a.index('    const projected = points.map');end=a.index('    for (const { point, x, y } of projected)',start)
a=a[:start]+'''    const projected = points.flatMap(point => {
      const projection = projectMapPoint(point.position, camera, size.width, size.height, clip.current);
      const node = elements.nodes.get(point.id), dot = elements.dots.get(point.id), line = elements.lines.get(point.id);
      for (const element of [node, dot, line]) if (element) element.style.visibility = projection ? "visible" : "hidden";
      return projection ? [{ point, ...projection }] : [];
    }).sort((a, b) => a.y - b.y);
'''+a[end:];Path(p).write_text(a)
edit(p,'const controls = [...node.querySelectorAll<HTMLButtonElement>("button:not(:disabled)")];','const controls = [...node.querySelectorAll<HTMLButtonElement>("button:not(:disabled)")].filter(control => getComputedStyle(control).visibility !== "hidden");')
