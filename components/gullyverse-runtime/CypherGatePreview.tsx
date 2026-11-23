"use client";

import Link from "next/link";
import React, { lazy, Suspense, useCallback, useEffect, useLayoutEffect, useMemo, useRef, useState, useSyncExternalStore } from "react";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { AgXToneMapping, Box3, Color, Euler, MathUtils, Mesh, PerspectiveCamera, Texture, Vector3, VideoTexture,
  type Camera, type Object3D, type Scene, type WebGLRenderer } from "three";
import { useImmersiveInput } from "../immersive/input";
import { phoneCamera, ReadinessGate, SceneRenderer } from "../immersive/rendering";
import { ImmersiveRuntime, sprintSpeed, walkSpeed } from "../immersive/runtime";
import { lookAtPose, world } from "../immersive/world";
import { BakedAssetPool, type BakedAsset } from "./baked-assets";
import { Fidelity } from "./fidelity";
import { GullyAudio, isWet, soundPreference, strideAt } from "./gully-audio";
import { cypherContact } from "./cypher-contact";
import { CypherContactDialog, type ContactPlacement } from "./CypherContactDialog";
import { CypherEventsDialog } from "./CypherEventsDialog";
import { eventPosterSlots, eventsPerPage, paintEventPage } from "./event-poster-wall";
import type { CypherCatalog, CypherEvent } from "../../lib/events/cypher-catalog";
import { CypherTeamDialog } from "./CypherTeamDialog";
import { CypherAftermovieControls } from "./CypherAftermovieControls";
import {
  accommodationApproach, accommodationFocus, accommodationView, isAccommodationArtwork, revealAccommodationHouseWall,
} from "./cypher-accommodation";
import { aftermovieFocus, aftermovieView, bindAftermovie, findAftermoviePanels, isAftermoviePanel } from "./cypher-aftermovie";
import { stageVideoSource } from "../landing-page/stage3d/useStageVideo";
import { useScreenFilm } from "./cypher-screen-film";
import { GullyDiagnostics, markLoad } from "./gully-diagnostics";
import { QualityGovernor } from "./quality-governor";
import { chunkOrder, laneChunks, type Chunk } from "./chunk-order";
import { defaultTeam, mountTeamCarousel, nextTeam, teamFocus, teamIndex, teamView, type TeamDisplay } from "./team-carousel";
import { mountSponsorDisplay } from "./sponsor-display";
import { mountMarketLamps } from "./market-lamps";
import walkSpace from "./cypher-walk-space.json";
import { cypherStarts, startHref, type CypherStart } from "./cypher-map";
import { createCypherMapDOM, CypherMap, CypherMapProjection } from "./CypherMap";

const { plaza } = cypherStarts;
// Review only: `/runtime-preview/cypher?reviewCamera=px,py,pz,qx,qy,qz,qw,fov` pins the camera to an exact
// Three.js pose so browser frames can be compared with renders from the Blender cameras.
const reviewCamera = (() => {
  if (typeof window === "undefined" || !window.location.pathname.startsWith("/runtime-preview")) return null;
  const values = new URLSearchParams(window.location.search).get("reviewCamera")?.split(",").map(Number);
  return values?.length === 8 && values.every(Number.isFinite) ? values : null;
})();
const eventsFocus = lookAtPose([-9.7, 8.9, -31.05], [-15.85, 8.15, -31.05]);
const assetRoot = "/models/gullyverse/locked-rev15z-";
function walkingStarted(runtime: ImmersiveRuntime, signal: AbortSignal) {
  return new Promise<void>((resolve, reject) => {
    const check = () => { if (runtime.getSnapshot().phase === "local") { off(); resolve(); } };
    const off = runtime.subscribe(check);
    signal.addEventListener("abort", () => { off(); reject(signal.reason); }, { once: true });
    check();
  });
}
/**
 * Full speed: one second after walking starts. Data saver or a 2G-class connection: when the visitor
 * comes within about 20 m of the other half (or after three minutes).
 */
function laterAllowed(runtime: ImmersiveRuntime, near: Chunk[], signal: AbortSignal) {
  const connection = (navigator as Navigator & { connection?: { saveData?: boolean; effectiveType?: string } }).connection;
  const constrained = !!connection?.saveData || /(^|-)2g$/.test(connection?.effectiveType ?? "");
  return new Promise<void>((resolve, reject) => {
    const towardsPlaza = near === laneChunks, started = performance.now();
    const timer = window.setInterval(() => {
      const z = runtime.pose.z, close = towardsPlaza ? z < 14 : z > -26;
      if (!constrained ? performance.now() - started > 1000 : close || performance.now() - started > 180000) { window.clearInterval(timer); resolve(); }
    }, 250);
    signal.addEventListener("abort", () => { window.clearInterval(timer); reject(signal.reason); }, { once: true });
  });
}
/** Uploads a late chunk's textures and compiles its programs with the scene's lighting before it is shown. */
async function prepareLate(gl: WebGLRenderer, root: Object3D, camera: Camera, scene: Scene) {
  root.traverse(object => {
    if (!(object instanceof Mesh)) return;
    for (const material of Array.isArray(object.material) ? object.material : [object.material]) {
      for (const value of Object.values(material)) if (value instanceof Texture && !(value instanceof VideoTexture)) gl.initTexture(value);
    }
  });
  await gl.compileAsync(root, camera, scene);
}
const QuarryArrivalScene = lazy(() => import("./QuarryArrivalScene"));
type Start = "quarry" | CypherStart;
type WallPanel = "events" | "team" | "aftermovie" | "accommodation";
type WallUI = WallPanel | "active" | null;
const wallFocus = { events: eventsFocus, team: teamFocus, aftermovie: aftermovieFocus, accommodation: accommodationFocus };
const wallViews = { team: teamView, aftermovie: aftermovieView, accommodation: accommodationView };
const wallLabel = {
  events: "Browse event posters", team: "View team murals", aftermovie: "Watch Aftermovie",
  accommodation: "View accommodation",
};
type ContactUI = { available: boolean; placement: ContactPlacement; needsHeading: boolean };
const closedContact: ContactUI = { available: false, placement: null, needsHeading: false };
const compactContactQuery = "(max-width: 699px), (max-height: 519px), (pointer: coarse)";
const phoneWindowLine = 0.34;
function canOpenContact(pose: { x: number; z: number }) {
  if (!cypherContact.near(pose)) return false;
  const reached = plaza.resolve(pose, cypherContact.focus);
  return Math.hypot(reached.x - cypherContact.focus.x, reached.z - cypherContact.focus.z) < 0.01;
}
function canOpenWall(pose: { x: number; z: number }, focus: { x: number; z: number }) {
  if (Math.hypot(pose.x - focus.x, pose.z - focus.z) > 4) return false;
  const reached = plaza.resolve(pose, focus);
  return Math.hypot(reached.x - focus.x, reached.z - focus.z) < 0.01;
}
const zoneAt = (z: number) => {
  if (z < -22) return "Cypher plaza";
  if (z < -15.65) return "Cypher forecourt";
  if (z < -11.4) return "Cypher gate";
  if (z < -1.5) return "Navigation approach";
  return "Market lane";
};

class CanvasBoundary extends React.Component<{ children: React.ReactNode; onFailure(): void }, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() { return { failed: true }; }
  componentDidCatch() { this.props.onFailure(); }
  render() { return this.state.failed ? null : this.props.children; }
}

function GateScene({ runtime, curtain, reportZone, form, reportContact, panel, eventPage, reportWall, chooseEvent,
  teamRequest, reportTeam, film, openWall, stopAftermovie, audio, ducked, reportStreaming, reportWorld, setDpr }: {
  runtime: ImmersiveRuntime;
  curtain: React.RefObject<HTMLDivElement | null>;
  reportZone(zone: ReturnType<typeof zoneAt>): void;
  form: React.RefObject<HTMLDivElement | null>;
  reportContact(contact: ContactUI): void;
  panel: WallPanel | null;
  eventPage: CypherEvent[] | null;
  reportWall(state: WallUI): void;
  chooseEvent(id: string): void;
  teamRequest: { index: number };
  reportTeam(display: TeamDisplay): void;
  film: VideoTexture | null;
  openWall(panel: WallPanel): void;
  stopAftermovie(): void;
  audio: GullyAudio;
  ducked: boolean;
  reportStreaming(pending: number): void;
  reportWorld(ready: boolean): void;
  setDpr(dpr: number): void;
}) {
  const { gl, scene, camera, size } = useThree();
  const [fidelity] = useState(() => new Fidelity(gl, window.matchMedia("(max-width: 699px)").matches,
    assetRoot + "market-south/transcoders/"));
  // The market chunks hold most of the small static meshes (shops, frontages): merged per material.
  const [pool] = useState(() => new BakedAssetPool(gl, 2, fidelity, /locked-rev15z-market-(south|north)\//));
  useEffect(() => () => pool.dispose(), [pool]);
  useEffect(() => () => fidelity.dispose(), [fidelity]);
  // Chunks stream in: the visitor's half of the gully first, the other half once walking has started.
  const [assets, setAssets] = useState<Partial<Record<Chunk, BakedAsset>>>();
  const display = useRef<Awaited<ReturnType<typeof mountSponsorDisplay>> | undefined>(undefined);
  const lamps = useRef<ReturnType<typeof mountMarketLamps> | undefined>(undefined);
  const state = useSyncExternalStore(runtime.subscribe, runtime.getSnapshot, runtime.getSnapshot);
  const euler = useRef(new Euler(0, 0, 0, "YXZ"));
  const zone = useRef(zoneAt(runtime.pose.z));
  const zoom = useRef(0);
  const wallZoom = useRef(0);
  const framedWall = useRef<keyof typeof wallViews>("team");
  // Walking feel: a stride clock drives a small head bob and the footsteps.
  const stride = useRef({ x: NaN, z: NaN, steps: 0, amplitude: 0 });
  const listenerForward = useRef(new Vector3());
  const contact = useRef(closedContact);
  const wallState = useRef<WallUI>(null);
  const carousel = useRef<ReturnType<typeof mountTeamCarousel>>(null);
  const corners = useRef([new Vector3(), new Vector3()]);
  const artwork = useRef<{ centre: [number, number, number]; width: number; height: number } | null>(null);

  useEffect(() => {
    const abort = new AbortController();
    const releases = new Set<() => void>();
    const releaseAll = () => {
      lamps.current?.dispose();
      lamps.current = undefined;
      display.current?.dispose();
      display.current = undefined;
      releases.forEach(release => release());
      releases.clear();
    };
    const mobile = window.matchMedia("(max-width: 699px)").matches;
    async function loadChunk(base: string) {
      const name = base.slice(assetRoot.length, -1);
      markLoad(name, "start");
      try {
        const asset = await loadChunkAsset(base);
        markLoad(name, "ready");
        return asset;
      } catch (error) { markLoad(name, "failed"); throw error; }
    }
    async function loadChunkAsset(base: string) {
      const response = await fetch(base + "manifest.json", { signal: abort.signal });
      if (!response.ok) throw new Error("The cypher assets are unavailable.");
      const { source, bake } = await response.json();
      if (source?.sha256 !== walkSpace.sourceSHA256 || !Number.isFinite(bake?.range) || bake.range <= 0) {
        throw new Error("The cypher geometry and walking space have different versions.");
      }
      abort.signal.throwIfAborted();
      const lease = pool.acquire(base, mobile, bake);
      releases.add(lease.release);
      try {
        return await lease.promise;
      } catch {
        lease.release();
        releases.delete(lease.release);
        abort.signal.throwIfAborted();
        const fallback = pool.acquire(base, mobile, bake, true);
        releases.add(fallback.release);
        return fallback.promise;
      }
    }
    /** Per-chunk set-up that other systems need (sponsor LEDs, lamps, the accommodation wall, contact). */
    async function mount(name: Chunk, asset: BakedAsset, loaded: Partial<Record<Chunk, BakedAsset>>) {
      if (name === "cypher-approach") {
        const led = await mountSponsorDisplay(asset.scene, assetRoot + "cypher-approach/sponsor-led.png", abort.signal);
        if (abort.signal.aborted) { led.dispose(); return; }
        display.current = led;
      }
      const south = loaded["market-south"], north = loaded["market-north"];
      if ((name === "market-south" || name === "market-north") && south && north && !lamps.current) {
        lamps.current = mountMarketLamps([south.scene, north.scene]);
      }
      if (name === "cypher-plaza") {
        revealAccommodationHouseWall(asset.scene, asset.rgbmRange);
        const bounds = new Box3();
        asset.scene.updateMatrixWorld(true);
        asset.scene.traverse(object => {
          if (object.visible && object.userData.contactPart === "contact heading") bounds.expandByObject(object, true);
        });
        if (bounds.isEmpty()) {
          artwork.current = null;
        } else {
          const extent = bounds.getSize(new Vector3());
          artwork.current = { centre: bounds.getCenter(new Vector3()).toArray(), width: Math.hypot(extent.x, extent.z), height: extent.y };
        }
      }
    }
    async function load() {
      const { near, later } = chunkOrder(runtime.pose.z);
      const loaded: Partial<Record<Chunk, BakedAsset>> = {};
      const first = await Promise.all(near.map(name => loadChunk(assetRoot + name + "/")));
      abort.signal.throwIfAborted();
      near.forEach((name, index) => { loaded[name] = first[index]; });
      for (const name of near) await mount(name, loaded[name]!, loaded);
      abort.signal.throwIfAborted();
      performance.mark("breeze:near-ready");
      setAssets({ ...loaded });
      // The rest streams after walking starts (on slow or data-saving connections, when the visitor
      // heads towards it). Each chunk's textures and shaders are prepared before it joins the scene,
      // so it appears without a compile hitch.
      await walkingStarted(runtime, abort.signal);
      await laterAllowed(runtime, near, abort.signal);
      reportStreaming(later.length);
      let remaining = later.length;
      await Promise.all(later.map(async name => {
        try {
          const asset = await loadChunk(assetRoot + name + "/");
          abort.signal.throwIfAborted();
          loaded[name] = asset;
          await prepareLate(gl, asset.scene, camera, scene);
          abort.signal.throwIfAborted();
          await mount(name, asset, loaded);
          abort.signal.throwIfAborted();
          setAssets(current => ({ ...current, [name]: asset }));
        } catch (error) {
          if (abort.signal.aborted) throw error;
          // The visitor keeps walking the part that loaded; the map and HTML links still reach everything.
          console.warn(`Gully chunk ${name} could not load`, error);
        } finally {
          if (!abort.signal.aborted) reportStreaming(--remaining);
        }
      }));
      performance.mark("breeze:world-ready");
      reportWorld(true);
    }
    void load().catch(() => {
      if (!abort.signal.aborted) runtime.fail("The cypher preview could not load.");
      abort.abort();
      releaseAll();
    });
    return () => { abort.abort(); releaseAll(); };
  }, [pool, runtime, gl, camera, scene, reportStreaming, reportWorld]);

  useEffect(() => {
    gl.toneMapping = AgXToneMapping;
    gl.toneMappingExposure = Math.pow(2, 0.25);
    scene.background = new Color("#010303");
    const lost = (event: Event) => { event.preventDefault(); stopAftermovie(); runtime.loseContext(); };
    const restored = () => runtime.restoreContext();
    gl.domElement.addEventListener("webglcontextlost", lost);
    gl.domElement.addEventListener("webglcontextrestored", restored);
    return () => {
      gl.domElement.removeEventListener("webglcontextlost", lost);
      gl.domElement.removeEventListener("webglcontextrestored", restored);
    };
  }, [gl, scene, runtime, stopAftermovie]);

  const plazaScene = assets?.["cypher-plaza"]?.scene;
  const screenPanels = useMemo(() => plazaScene ? findAftermoviePanels(plazaScene) : null, [plazaScene]);
  useLayoutEffect(() => {
    if (screenPanels && film) return bindAftermovie(screenPanels, film);
  }, [screenPanels, film]);
  useEffect(() => {
    if (!plazaScene || !eventPage) return;
    const slots = eventPosterSlots(plazaScene);
    if (slots.every(slot => slot !== undefined)) return paintEventPage(slots, eventPage);
  }, [plazaScene, eventPage]);
  useEffect(() => {
    if (!plazaScene) return;
    const mounted = mountTeamCarousel(plazaScene);
    carousel.current = mounted;
    return () => {
      mounted?.dispose();
      carousel.current = null;
    };
  }, [plazaScene]);
  useEffect(() => {
    const mounted = carousel.current;
    if (!mounted || mounted.index === teamRequest.index) {
      reportTeam({ index: mounted?.index ?? 0, status: "ready" });
      return;
    }
    const abort = new AbortController();
    reportTeam({ index: mounted.index, status: "loading" });
    void mounted.show(teamRequest.index, abort.signal).then(() => {
      if (!abort.signal.aborted) reportTeam({ index: mounted.index, status: "ready" });
    }, () => {
      if (!abort.signal.aborted) reportTeam({ index: mounted.index, status: "error" });
    });
    return () => abort.abort();
  }, [plazaScene, teamRequest, reportTeam]);

  useFrame((_, delta) => {
    runtime.tick(delta);
    if (!runtime.reduced) display.current?.advance(runtime.activeFrameDelta);
    lamps.current?.advance(runtime.activeFrameDelta, runtime.reduced);
    const aspect = Math.max(size.width / Math.max(1, size.height), 0.01);
    const view = runtime.cameraPose(aspect, panel === null && phoneCamera(size.width));
    const { phase, map } = runtime.getSnapshot();
    const editing = phase === "local" && runtime.interacting && panel === null;
    const sheet = editing && (window.matchMedia(compactContactQuery).matches ||
      !cypherContact.windowFits(window.innerWidth, window.innerHeight));
    const zoomTarget = Number(editing);
    zoom.current = runtime.reduced ? zoomTarget : MathUtils.damp(zoom.current, zoomTarget, 12, Math.min(delta, 0.2));
    if (zoom.current > 0.001) {
      if (sheet) {
        const heading = artwork.current?.centre ?? cypherContact.headingCentre;
        const position = [view.x, view.y, view.z] as const;
        const edge = cypherContact.windowTop;
        const aim = lookAtPose(position, edge);
        const distance = Math.hypot(view.x - edge[0], view.z - edge[2]);
        const headingTop = heading[1] + (artwork.current?.height ?? 0.6) / 2;
        const upperFov = cypherContact.artworkFov(aspect / phoneWindowLine, artwork.current?.width ?? 2.6,
          headingTop - edge[1], Math.max(distance, 1));
        // Keep enough room above the opening for the original graffiti.
        const halfView = Math.tan(MathUtils.degToRad(upperFov / 2)) / phoneWindowLine;
        view.yaw = MathUtils.lerp(view.yaw, aim.yaw, zoom.current);
        view.pitch = MathUtils.lerp(view.pitch, aim.pitch - Math.atan((1 - 2 * phoneWindowLine) * halfView), zoom.current);
        view.fov = MathUtils.lerp(view.fov, MathUtils.radToDeg(2 * Math.atan(halfView)), zoom.current);
      } else {
        view.fov = MathUtils.lerp(view.fov, cypherContact.windowFov(aspect), zoom.current);
      }
    }
    const focusedWall = phase === "local" && runtime.interacting && panel !== "events" ? panel : null;
    const wallTarget = Number(focusedWall !== null);
    if (focusedWall) framedWall.current = focusedWall;
    wallZoom.current = runtime.reduced ? wallTarget : MathUtils.damp(wallZoom.current, wallTarget, 12, Math.min(delta, 0.2));
    let wallOffset = 0;
    if (wallZoom.current > 0.001 && size.width > 0 && size.height > 0) {
      const frame = wallViews[framedWall.current](size.width, size.height, [view.x, view.y, view.z]);
      view.pitch = MathUtils.lerp(view.pitch, wallFocus[framedWall.current].pitch, wallZoom.current);
      view.fov = MathUtils.lerp(view.fov, frame.fov, wallZoom.current);
      wallOffset = frame.offsetY * wallZoom.current;
    }
    camera.position.set(view.x, view.y, view.z);
    camera.quaternion.setFromEuler(euler.current.set(view.pitch, view.yaw, 0, "YXZ"));
    {
      // Stride-driven head bob (sprinting: about 2 cm vertical, 1 cm sway, a quarter-degree roll; walking under half) with a footstep at
      // each footfall. Off in focused views, the map, review captures and for reduced motion.
      const gait = stride.current;
      const dt = Math.min(delta, 0.1);
      const moved = Number.isFinite(gait.x) ? Math.hypot(runtime.pose.x - gait.x, runtime.pose.z - gait.z) : 0;
      gait.x = runtime.pose.x; gait.z = runtime.pose.z;
      const walkingNow = phase === "local" && !map && !runtime.interacting && !reviewCamera;
      // Distance-based, so slow frames on weak devices still step; faster than 7 m/s is a map jump.
      const speed = walkingNow ? moved / Math.max(delta, 1e-3) : 0;
      const stepping = walkingNow && speed <= 7;
      // Walking bobs at under half the sprint's amplitude; sprinting keeps the full 2 cm.
      const intensity = speed <= walkSpeed ? 0.45 * speed / walkSpeed
        : 0.45 + 0.55 * Math.min(1, (speed - walkSpeed) / (sprintSpeed - walkSpeed));
      gait.amplitude = MathUtils.damp(gait.amplitude, stepping ? intensity : 0, 8, dt);
      const before = Math.floor(gait.steps);
      if (stepping) gait.steps += moved / strideAt(speed);
      if (Math.floor(gait.steps) !== before && gait.amplitude > 0.2) {
        audio.footstep(isWet(runtime.pose.x, runtime.pose.z), gait.amplitude, undefined, speed > (walkSpeed + sprintSpeed) / 2);
      }
      if (!runtime.reduced && gait.amplitude > 0.001) {
        const a = gait.amplitude, cycle = gait.steps;
        camera.position.y += 0.011 * a - 0.022 * a * (0.5 + 0.5 * Math.cos(2 * Math.PI * cycle));
        const sway = 0.012 * a * Math.sin(Math.PI * cycle);
        camera.position.x += Math.cos(view.yaw) * sway;
        camera.position.z -= Math.sin(view.yaw) * sway;
        camera.rotateZ(0.0045 * a * Math.sin(Math.PI * cycle));
      }
      camera.getWorldDirection(listenerForward.current);
      const f = listenerForward.current;
      audio.update([camera.position.x, camera.position.y, camera.position.z], [f.x, f.y, f.z], ducked);
    }
    if (reviewCamera) {
      const [px, py, pz, qx, qy, qz, qw, fov] = reviewCamera;
      camera.position.set(px, py, pz);
      camera.quaternion.set(qx, qy, qz, qw);
      view.fov = fov;
      wallOffset = 0;
    }
    if (camera instanceof PerspectiveCamera) {
      const changedFov = camera.fov !== view.fov;
      camera.fov = view.fov;
      const offset = camera.view;
      if (wallOffset !== 0 && (!offset?.enabled || offset.offsetY !== wallOffset ||
          offset.fullWidth !== size.width || offset.fullHeight !== size.height)) {
        camera.setViewOffset(size.width, size.height, 0, wallOffset, size.width, size.height);
      } else if (wallOffset === 0 && offset?.enabled) {
        camera.clearViewOffset();
      } else if (changedFov) {
        camera.updateProjectionMatrix();
      }
    }
    if (assets) fidelity.updateEnvironment(scene, camera);
    if (curtain.current) curtain.current.style.opacity = String(runtime.revealOpacity);
    const current = zoneAt(runtime.pose.z);
    if (current !== zone.current) {
      zone.current = current;
      reportZone(current);
    }
    const settled = phase === "local" && !runtime.focusing && runtime.revealOpacity < 0.02;
    let nextWall: WallUI = null;
    if (settled && !map) {
      if (runtime.interacting) nextWall = panel === null ? null : "active";
      else if (screenPanels && canOpenWall(runtime.pose, aftermovieFocus)) nextWall = "aftermovie";
      else if (carousel.current && canOpenWall(runtime.pose, teamFocus)) nextWall = "team";
      else if (eventPage && canOpenWall(runtime.pose, eventsFocus)) nextWall = "events";
      else if (canOpenWall(runtime.pose, accommodationFocus)) nextWall = "accommodation";
    }
    if (nextWall !== wallState.current) {
      wallState.current = nextWall;
      reportWall(nextWall);
    }
    const available = settled && !map && !runtime.interacting && canOpenContact(runtime.pose);
    let placement: ContactPlacement = settled && editing && sheet ? "sheet" : null;
    if (placement === "sheet" && form.current) {
      camera.updateMatrixWorld();
      const opening = corners.current[0].set(...cypherContact.windowTop).project(camera);
      form.current.style.setProperty("--contact-opening-top", `${(1 - opening.y) * size.height / 2}px`);
    }
    if (settled && editing && !sheet && form.current) {
      camera.updateMatrixWorld();
      const [a, b] = corners.current;
      a.set(...cypherContact.topLeft).project(camera);
      b.set(...cypherContact.bottomRight).project(camera);
      const width = (b.x - a.x) * size.width / 2;
      const height = (a.y - b.y) * size.height / 2;
      placement = "window";
      Object.assign(form.current.style, {
        left: `${(a.x + 1) * size.width / 2}px`, top: `${(1 - a.y) * size.height / 2}px`,
        width: `${width}px`, height: `${height}px`,
      });
    }
    const needsHeading = placement !== null && artwork.current === null;
    if (available !== contact.current.available || placement !== contact.current.placement ||
        needsHeading !== contact.current.needsHeading) {
      contact.current = { available, placement, needsHeading };
      reportContact(contact.current);
    }
  }, -1);

  return <>
    {assets && <>
      {(Object.entries(assets) as [Chunk, BakedAsset][]).map(([name, asset]) => <primitive key={name} object={asset.scene}
        onClick={name === "cypher-plaza" && (panel === "events" || wallState.current === "aftermovie" ||
          wallState.current === "accommodation") ? event => {
          const eventId = event.object.userData.wallEventId;
          if (panel === "events" && typeof eventId === "string") chooseEvent(eventId);
          else if (wallState.current === "aftermovie" && isAftermoviePanel(event.object)) openWall("aftermovie");
          else if (wallState.current === "accommodation" && isAccommodationArtwork(event.object)) openWall("accommodation");
        } : undefined} />)}
      <ReadinessGate key={state.serial} runtime={runtime} serial={state.serial} />
    </>}
    <SceneRenderer runtime={runtime} />
    <GullyDiagnostics runtime={runtime} />
    <QualityGovernor runtime={runtime} setDpr={setDpr} />
  </>;
}

function AccommodationControls({ close }: { close(): void }) {
  const back = useRef<HTMLButtonElement>(null);
  useEffect(() => { back.current?.focus({ preventScroll: true }); }, []);
  return <section className="cypher-accommodation-controls" aria-label="Accommodation" aria-describedby="accommodation-status">
    <p className="sr-only" id="accommodation-status">Coming soon</p>
    <button type="button" ref={back} onClick={close}>Back to walking</button>
  </section>;
}

function AccommodationStatus() {
  return <section className="cypher-accommodation-status" aria-label="Accommodation">
    <h2>Accommodation</h2>
    <p>Coming soon</p>
  </section>;
}

function GateWalk({ start, team, canSendContact, catalog, live }:
  { start: Start; team?: string; canSendContact: boolean; catalog: CypherCatalog | null; live: boolean }) {
  const curtain = useRef<HTMLDivElement>(null);
  const canvas = useRef<HTMLDivElement>(null);
  const form = useRef<HTMLDivElement>(null);
  const enquiry = useRef<HTMLButtonElement>(null);
  const restoreContactFocus = useRef(false);
  const browse = useRef<HTMLButtonElement>(null);
  const restoreWallFocus = useRef<WallPanel | null>(null);
  const watchingMovie = useRef(false);
  const holdCurtain = useRef(false);
  const mapButton = useRef<HTMLButtonElement>(null);
  const [mapDom] = useState(createCypherMapDOM);
  const travelled = useRef(false);
  const [contact, setContact] = useState(closedContact);
  const [wallUI, setWallUI] = useState<WallUI>(null);
  const [panel, setPanel] = useState<WallPanel | null>(null);
  const [audio] = useState(() => new GullyAudio());
  const [sound, setSound] = useState(soundPreference);
  useEffect(() => { audio.arm(); return () => audio.dispose(); }, [audio]);
  const toggleSound = useCallback(() => setSound(on => { audio.setEnabled(!on); return !on; }), [audio]);
  const [movieFailed, setMovieFailed] = useState(false);
  const [streaming, setStreaming] = useState(0);
  const [canvasDpr, setCanvasDpr] = useState(1);
  const [teamRequest, requestTeam] = useState(() => ({ index: teamIndex(team) }));
  const [teamDisplay, setTeamDisplay] = useState(defaultTeam);
  const [page, setPage] = useState(0);
  const [eventId, chooseEvent] = useState<string | null>(null);
  const pages = Math.ceil((catalog?.data?.length ?? 0) / eventsPerPage);
  const eventPage = useMemo(() => catalog === null ? null :
    catalog.data?.slice(page * eventsPerPage, (page + 1) * eventsPerPage) ?? [], [catalog, page]);
  const [atMarket, setAtMarket] = useState(start !== "quarry");
  const [marketRuntime] = useState(() => {
    const runtime = new ImmersiveRuntime("hub", undefined, false, undefined, cypherStarts[start === "quarry" ? "market" : start].space);
    runtime.pace = { walk: walkSpeed, sprint: sprintSpeed };
    return runtime;
  });
  const [quarry] = useState(() => start === "quarry" ? new ImmersiveRuntime("hub", () => {
    holdCurtain.current = true;
    setAtMarket(true);
  }, true, () => performance.now() / 1000) : null);
  const activeQuarry = atMarket ? null : quarry;
  const runtime = activeQuarry ?? marketRuntime;
  const [zone, setZone] = useState(() => zoneAt(marketRuntime.pose.z));
  const state = useSyncExternalStore(runtime.subscribe, runtime.getSnapshot, runtime.getSnapshot);
  useImmersiveInput(runtime);
  // The screen loops the Aftermovie all visit; its sound is the stage and radio music (GullyAudio).
  const [worldReady, setWorldReady] = useState(false);
  const screen = useScreenFilm(useCallback(() => setMovieFailed(true), []), worldReady);
  useEffect(() => { if (screen.film) audio.attachFilm(screen.film.video); }, [audio, screen.film]);
  const stopAftermovie = useCallback(() => {
    if (!watchingMovie.current) return;
    watchingMovie.current = false;
    if (marketRuntime.interacting) marketRuntime.focusInteraction(null);
    setPanel(null);
  }, [marketRuntime]);
  const openWall = useCallback((target: WallPanel) => {
    const focus = wallFocus[target];
    if (!canOpenWall(marketRuntime.pose, focus) || !marketRuntime.focusInteraction(focus)) return;
    setPanel(target);
    restoreWallFocus.current = target;
    if (target === "aftermovie") {
      setMovieFailed(false);
      watchingMovie.current = true;
      screen.restart();
    }
  }, [marketRuntime, screen.restart]);
  const closeContact = useCallback(() => { marketRuntime.focusInteraction(null); }, [marketRuntime]);
  const closeWall = useCallback(() => {
    marketRuntime.focusInteraction(null);
    chooseEvent(null);
    setPanel(null);
  }, [marketRuntime]);
  const advanceTeam = useCallback((direction: -1 | 1) => {
    requestTeam(current => ({ index: nextTeam(current.index, direction) }));
  }, []);
  const reportTeam = useCallback((display: TeamDisplay) => {
    setTeamDisplay(display);
    if (display.status !== "ready" || display.index !== teamRequest.index) return;
    const url = new URL(window.location.href);
    if (display.index === 0) url.searchParams.delete("team");
    else url.searchParams.set("team", String(display.index));
    if (url.href !== window.location.href) window.history.replaceState(null, "", url);
  }, [teamRequest.index]);
  useEffect(() => {
    if (contact.available && restoreContactFocus.current && enquiry.current) {
      restoreContactFocus.current = false;
      enquiry.current.focus();
    }
  }, [contact.available]);
  useEffect(() => {
    if (restoreWallFocus.current && wallUI === restoreWallFocus.current && browse.current) {
      restoreWallFocus.current = null;
      browse.current.focus();
    }
  }, [wallUI]);
  useEffect(() => {
    if (!runtime.interacting) {
      stopAftermovie();
      setPanel(null);
      chooseEvent(null);
    }
  }, [state, runtime, stopAftermovie]);
  const travel = useCallback((stop: CypherStart) => {
    travelled.current = true;
    restoreContactFocus.current = stop === "contact";
    restoreWallFocus.current = stop === "events" || stop === "team" || stop === "aftermovie" || stop === "accommodation"
      ? stop : null;
    const href = startHref(window.location.href, stop);
    if (href !== window.location.href) window.history.replaceState(null, "", href);
  }, []);
  const mapOpen = state.map;
  useEffect(() => {
    if (mapOpen) {
      travelled.current = false;
      return;
    }
    // A plain close returns focus to the Map button; travel hands it to the destination.
    if (!travelled.current && (document.activeElement === null || document.activeElement === document.body)) {
      mapButton.current?.focus({ preventScroll: true });
    }
  }, [mapOpen]);
  const walking = atMarket && state.phase === "local";
  useEffect(() => {
    const keys = (event: KeyboardEvent) => {
      if (event.repeat || event.ctrlKey || event.metaKey || event.altKey) return;
      const target = event.target as HTMLElement | null;
      if (target?.closest("input, textarea, select, [contenteditable=true], form")) return;
      if (event.code === "KeyV") { event.preventDefault(); toggleSound(); return; }
      if (event.code === "KeyE" && walking && !marketRuntime.interacting && !marketRuntime.getSnapshot().map) {
        const action = enquiry.current ?? browse.current;
        if (action) { event.preventDefault(); action.click(); }
      }
    };
    window.addEventListener("keydown", keys);
    return () => window.removeEventListener("keydown", keys);
  }, [walking, marketRuntime, toggleSound]);
  const landing = !!activeQuarry && state.phase === "landing";
  return <>
    <div ref={canvas} className="native-canvas" data-world={activeQuarry ? "quarry" : "market"} data-phase={state.phase}
      data-contact-placement={contact.placement ?? undefined}>
      <Canvas dpr={canvasDpr} gl={{ antialias: true, powerPreference: "high-performance" }}
        camera={start === "quarry" ? world.camera : { near: 0.05, far: 120 }} fallback={<p>3D is unavailable in this browser.</p>}>
        {activeQuarry ? <Suspense fallback={null}>
          <QuarryArrivalScene runtime={activeQuarry} curtain={curtain} holdCurtain={holdCurtain} />
        </Suspense> : <GateScene runtime={marketRuntime} curtain={curtain} reportZone={setZone}
          form={form} reportContact={setContact} panel={panel} eventPage={eventPage}
          reportWall={setWallUI} chooseEvent={chooseEvent} teamRequest={teamRequest} reportTeam={reportTeam}
          film={screen.ready ? screen.film?.texture ?? null : null} openWall={openWall} stopAftermovie={stopAftermovie}
          audio={audio} ducked={panel === "aftermovie" && runtime.interacting} reportStreaming={setStreaming} reportWorld={setWorldReady} setDpr={setCanvasDpr} />}
        {!activeQuarry && <CypherMapProjection runtime={marketRuntime} elements={mapDom} />}
      </Canvas>
      {walking && runtime.interacting && contact.needsHeading &&
        <h2 className="cypher-contact-fallback-heading">Contact us</h2>}
    </div>
    <div className="native-curtain" ref={curtain} aria-hidden="true" />
    {walking && state.map && <CypherMap runtime={marketRuntime} state={state} elements={mapDom} travel={travel} />}
    {landing && <div className="native-controls"><button onClick={() => runtime.enter()}>Enter Gullyverse</button></div>}
    {walking && !state.map && <p className="gully-location" aria-live="polite"><span className="gully-chip">{zone}</span>
      {streaming > 0 && <span className="gully-chip gully-streaming">Loading the rest of the gully…</span>}</p>}
    {walking && !runtime.interacting && <section className="gully-controls" aria-label="Controls">
      <p className="gully-controls-title" aria-hidden="true">Controls</p>
      <ul>
        {!state.map && <>
          <li className="gully-keyboard-only"><span className="gully-keys"><kbd>W</kbd><kbd>A</kbd><kbd>S</kbd><kbd>D</kbd></span>
            <span className="gully-label">Move</span></li>
          <li className="gully-keyboard-only"><span className="gully-keys"><kbd>Shift</kbd></span><span className="gully-label">Hold to sprint</span></li>
          <li className="gully-keyboard-only"><span className="gully-keys"><kbd>Drag</kbd></span><span className="gully-label">Look</span></li>
          {contact.available && <li><button ref={enquiry} aria-keyshortcuts="E" aria-label="Leave a message" onClick={() => {
            if (canOpenContact(marketRuntime.pose) && marketRuntime.focusInteraction(cypherContact.focus)) {
              restoreContactFocus.current = true;
            }
          }}><kbd>E</kbd><span className="gully-label">Leave a message</span></button></li>}
          {!contact.available && wallUI && wallUI !== "active" && <li><button ref={browse} aria-keyshortcuts="E"
            aria-label={wallLabel[wallUI]} onClick={() => openWall(wallUI)}>
            <kbd>E</kbd><span className="gully-label">{wallLabel[wallUI]}</span></button></li>}
        </>}
        <li><button ref={mapButton} aria-keyshortcuts="M"
          aria-label={state.map && state.mapStage !== "descent" ? "Close map" : "Map"}
          onClick={() => runtime.setMap(!state.map || state.mapStage === "descent")}>
          <kbd>M</kbd><span className="gully-label">{state.map && state.mapStage !== "descent" ? "Close map" : "Map"}</span>
        </button></li>
        {!state.map && <li><button aria-keyshortcuts="V" aria-pressed={sound} aria-label="Sound" onClick={toggleSound}>
          <kbd>V</kbd><span className="gully-label">{sound ? "Sound on" : "Sound off"}</span></button></li>}
      </ul>
      {wallUI === "aftermovie" && movieFailed && <p role="status" className="cypher-aftermovie-error">
        The Aftermovie could not play. Try again or <a href={stageVideoSource}>open the video</a>.
      </p>}
    </section>}
    {walking && !runtime.interacting && !state.map && <div className="native-touch gully-touch" aria-label="Movement controls">
      <button data-move="forward" aria-label="Walk forward">↑</button>
      <div>
        <button data-move="left" aria-label="Walk left">←</button>
        <button data-move="back" aria-label="Walk backward">↓</button>
        <button data-move="right" aria-label="Walk right">→</button>
      </div>
    </div>}
    <CypherContactDialog host={form} placement={walking && runtime.interacting ? contact.placement : null}
      canSend={canSendContact} onClose={closeContact} live={live} />
    {panel === "events" && wallUI === "active" && catalog && eventPage && <CypherEventsDialog
      catalog={catalog} visibleEvents={eventPage} page={page} pages={pages}
      event={eventPage.find(item => item.id === eventId)} changePage={setPage} choose={chooseEvent} close={closeWall} />}
    {panel === "team" && wallUI === "active" && <CypherTeamDialog canvas={canvas} display={teamDisplay}
      advance={advanceTeam} retry={() => requestTeam(current => ({ ...current }))} close={closeWall} />}
    {panel === "accommodation" && wallUI === "active" && <AccommodationControls close={closeWall} />}
    {walking && panel === "aftermovie" && runtime.interacting && <CypherAftermovieControls
      loading={!screen.ready} muted={!sound} toggleSound={toggleSound} close={stopAftermovie} />}
    {!walking && !landing && state.phase !== "entrance" && <div className="native-loading" role="status">
      <p>{state.error ?? (state.phase === "context-lost" || state.phase === "recovering"
        ? "Restoring 3D…" : activeQuarry ? "Loading the quarry…" : "Loading the market lane…")}</p>
      {state.error && <>
        {start === "accommodation" && <AccommodationStatus />}
        <Link href="/events">Browse events</Link><br /><a href="/get-in-touch">Contact us</a>
      </>}
    </div>}
  </>;
}

export default function CypherGatePreview({ start = "market", team, canSendContact = false, catalog = null, live = false }:
  { start?: Start; team?: string; canSendContact?: boolean; catalog?: CypherCatalog | null; live?: boolean }) {
  const [status, setStatus] = useState<"checking" | "ready" | "unavailable">("checking");
  useEffect(() => {
    try {
      const context = document.createElement("canvas").getContext("webgl2");
      setStatus(context ? "ready" : "unavailable");
      context?.getExtension("WEBGL_lose_context")?.loseContext();
    } catch {
      setStatus("unavailable");
    }
  }, []);
  return <div className="native-journey">
    <header className="native-header"><Link href="/">BREEZE <span>2027</span></Link></header>
    {status === "ready" && <CanvasBoundary onFailure={() => setStatus("unavailable")}>
      <GateWalk start={start} team={team} canSendContact={canSendContact} catalog={catalog} live={live} />
    </CanvasBoundary>}
    {status === "unavailable" && <div className="native-loading" role="status">
      <p>3D is unavailable in this browser.</p>
      {start === "accommodation" && <AccommodationStatus />}
      <Link href="/events">Browse events</Link>
      <br /><a href="/get-in-touch">Contact us</a>
      {start === "aftermovie" && <><br /><a href={stageVideoSource}>Watch the Aftermovie</a></>}
    </div>}
  </div>;
}
