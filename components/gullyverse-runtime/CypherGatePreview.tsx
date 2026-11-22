"use client";

import React, { lazy, Suspense, useCallback, useEffect, useMemo, useRef, useState, useSyncExternalStore } from "react";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { AgXToneMapping, Box3, Color, Euler, MathUtils, PerspectiveCamera, Vector3 } from "three";
import { useImmersiveInput } from "../immersive/input";
import { phoneCamera, ReadinessGate, SceneRenderer } from "../immersive/rendering";
import { ImmersiveRuntime } from "../immersive/runtime";
import { lookAtPose, world } from "../immersive/world";
import { BakedAssetPool, type BakedAsset } from "./baked-assets";
import { createCypherSpace } from "./cypher-space";
import { cypherContact } from "./cypher-contact";
import { CypherContactDialog, type ContactPlacement } from "./CypherContactDialog";
import { CypherEventsDialog } from "./CypherEventsDialog";
import { eventPosterSlots, eventsPerPage, paintEventPage } from "./event-poster-wall";
import type { CypherCatalog, CypherEvent } from "../../lib/events/cypher-catalog";
import { CypherTeamDialog } from "./CypherTeamDialog";
import { defaultTeam, mountTeamCarousel, nextTeam, teamFocus, teamIndex, teamView, type TeamDisplay } from "./team-carousel";
import { mountSponsorDisplay } from "./sponsor-display";
import { mountMarketLamps } from "./market-lamps";
import walkSpace from "./cypher-walk-space.json";

const routeBounds = { start: -29.5, end: 47.6, halfWidth: 16, plaza: true };
const market = createCypherSpace({ ...routeBounds, spawnY: -27.6 });
const approach = createCypherSpace({ ...routeBounds, spawnY: 2.2, spawnPitch: 0.27 });
const plaza = createCypherSpace({ ...routeBounds, spawnY: 19.3, spawnPitch: 0.08 });
const contactStart = createCypherSpace({ ...routeBounds, spawnY: -cypherContact.spawn.z, spawnX: cypherContact.spawn.x,
  spawnYaw: cypherContact.spawn.yaw, spawnPitch: cypherContact.spawn.pitch });
const eventsStart = createCypherSpace({ ...routeBounds, spawnY: 31.05, spawnX: -10.7, spawnYaw: Math.PI / 2 });
const eventsFocus = lookAtPose([-9.7, 8.9, -31.05], [-15.85, 8.15, -31.05]);
const teamStart = createCypherSpace({ ...routeBounds, spawnY: -teamFocus.z, spawnX: teamFocus.x, spawnYaw: teamFocus.yaw });
const assetRoot = "/models/gullyverse/locked-rev15z-";
const QuarryArrivalScene = lazy(() => import("./QuarryArrivalScene"));
type Start = "quarry" | "market" | "approach" | "plaza" | "contact" | "events" | "team";
type WallPanel = "events" | "team";
type WallUI = WallPanel | "active" | null;
const wallFocus = { events: eventsFocus, team: teamFocus };
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
  teamRequest, reportTeam }: {
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
}) {
  const { gl, scene, camera, size } = useThree();
  const [pool] = useState(() => new BakedAssetPool(gl, 1));
  const [assets, setAssets] = useState<BakedAsset[]>();
  const display = useRef<Awaited<ReturnType<typeof mountSponsorDisplay>> | undefined>(undefined);
  const lamps = useRef<ReturnType<typeof mountMarketLamps> | undefined>(undefined);
  const state = useSyncExternalStore(runtime.subscribe, runtime.getSnapshot, runtime.getSnapshot);
  const euler = useRef(new Euler(0, 0, 0, "YXZ"));
  const zone = useRef(zoneAt(runtime.pose.z));
  const zoom = useRef(0);
  const teamZoom = useRef(0);
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
    async function load() {
      const [gateAsset, signAsset, south, north, plazaAsset, audience] = await Promise.all([
        loadChunk(assetRoot + "cypher-gate/"),
        loadChunk(assetRoot + "cypher-approach/"),
        loadChunk(assetRoot + "market-south/"),
        loadChunk(assetRoot + "market-north/"),
        loadChunk(assetRoot + "cypher-plaza/"),
        loadChunk(assetRoot + "cypher-audience/"),
      ]);
      abort.signal.throwIfAborted();
      const led = await mountSponsorDisplay(signAsset.scene, assetRoot + "cypher-approach/sponsor-led.png", abort.signal);
      if (abort.signal.aborted) { led.dispose(); return; }
      display.current = led;
      lamps.current = mountMarketLamps([south.scene, north.scene]);
      const bounds = new Box3();
      plazaAsset.scene.updateMatrixWorld(true);
      plazaAsset.scene.traverse(object => {
        if (object.visible && object.userData.contactPart === "contact heading") bounds.expandByObject(object, true);
      });
      if (bounds.isEmpty()) {
        artwork.current = null;
      } else {
        const extent = bounds.getSize(new Vector3());
        artwork.current = { centre: bounds.getCenter(new Vector3()).toArray(), width: Math.hypot(extent.x, extent.z), height: extent.y };
      }
      setAssets([gateAsset, signAsset, south, north, plazaAsset, audience]);
    }
    void load().catch(() => {
      if (!abort.signal.aborted) runtime.fail("The cypher preview could not load.");
      abort.abort();
      releaseAll();
    });
    return () => { abort.abort(); releaseAll(); };
  }, [pool, runtime]);

  useEffect(() => {
    gl.toneMapping = AgXToneMapping;
    gl.toneMappingExposure = Math.pow(2, 0.25);
    scene.background = new Color("#010303");
    const lost = (event: Event) => { event.preventDefault(); runtime.loseContext(); };
    const restored = () => runtime.restoreContext();
    gl.domElement.addEventListener("webglcontextlost", lost);
    gl.domElement.addEventListener("webglcontextrestored", restored);
    return () => {
      gl.domElement.removeEventListener("webglcontextlost", lost);
      gl.domElement.removeEventListener("webglcontextrestored", restored);
    };
  }, [gl, scene, runtime]);

  const plazaScene = assets?.[4].scene;
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
    const teamTarget = Number(phase === "local" && runtime.interacting && panel === "team");
    teamZoom.current = runtime.reduced ? teamTarget : MathUtils.damp(teamZoom.current, teamTarget, 12, Math.min(delta, 0.2));
    if (teamZoom.current > 0.001) {
      const frame = teamView(aspect, [view.x, view.y, view.z]);
      view.pitch = MathUtils.lerp(view.pitch, frame.pitch, teamZoom.current);
      view.fov = MathUtils.lerp(view.fov, frame.fov, teamZoom.current);
    }
    camera.position.set(view.x, view.y, view.z);
    camera.quaternion.setFromEuler(euler.current.set(view.pitch, view.yaw, 0, "YXZ"));
    if (camera instanceof PerspectiveCamera && camera.fov !== view.fov) {
      camera.fov = view.fov;
      camera.updateProjectionMatrix();
    }
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
      else if (carousel.current && canOpenWall(runtime.pose, teamFocus)) nextWall = "team";
      else if (eventPage && canOpenWall(runtime.pose, eventsFocus)) nextWall = "events";
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
      {assets.map((asset, index) => <primitive key={index} object={asset.scene}
        onClick={index === 4 && panel === "events" ? event => {
          const eventId = event.object.userData.wallEventId;
          if (typeof eventId === "string") chooseEvent(eventId);
        } : undefined} />)}
      <ReadinessGate key={state.serial} runtime={runtime} serial={state.serial} />
    </>}
    <SceneRenderer runtime={runtime} />
  </>;
}

function GateWalk({ start, team, canSendContact, catalog }:
  { start: Start; team?: string; canSendContact: boolean; catalog: CypherCatalog | null }) {
  const curtain = useRef<HTMLDivElement>(null);
  const canvas = useRef<HTMLDivElement>(null);
  const form = useRef<HTMLDivElement>(null);
  const enquiry = useRef<HTMLButtonElement>(null);
  const restoreContactFocus = useRef(false);
  const browse = useRef<HTMLButtonElement>(null);
  const restoreWallFocus = useRef<WallPanel | null>(null);
  const holdCurtain = useRef(false);
  const [contact, setContact] = useState(closedContact);
  const [wallUI, setWallUI] = useState<WallUI>(null);
  const [panel, setPanel] = useState<WallPanel | null>(null);
  const [teamRequest, requestTeam] = useState(() => ({ index: teamIndex(team) }));
  const [teamDisplay, setTeamDisplay] = useState(defaultTeam);
  const [page, setPage] = useState(0);
  const [eventId, chooseEvent] = useState<string | null>(null);
  const pages = Math.ceil((catalog?.data?.length ?? 0) / eventsPerPage);
  const eventPage = useMemo(() => catalog === null ? null :
    catalog.data?.slice(page * eventsPerPage, (page + 1) * eventsPerPage) ?? [], [catalog, page]);
  const [atMarket, setAtMarket] = useState(start !== "quarry");
  const [marketRuntime] = useState(() => new ImmersiveRuntime("hub", undefined, false, undefined,
    (start === "approach" ? approach : start === "plaza" ? plaza : start === "contact" ? contactStart :
      start === "events" ? eventsStart : start === "team" ? teamStart : market).space));
  const [quarry] = useState(() => start === "quarry" ? new ImmersiveRuntime("hub", () => {
    holdCurtain.current = true;
    setAtMarket(true);
  }, true, () => performance.now() / 1000) : null);
  const activeQuarry = atMarket ? null : quarry;
  const runtime = activeQuarry ?? marketRuntime;
  const [zone, setZone] = useState(() => zoneAt(marketRuntime.pose.z));
  const state = useSyncExternalStore(runtime.subscribe, runtime.getSnapshot, runtime.getSnapshot);
  useImmersiveInput(runtime);
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
      setPanel(null);
      chooseEvent(null);
    }
  }, [state, runtime]);
  const walking = atMarket && state.phase === "local";
  const landing = !!activeQuarry && state.phase === "landing";
  return <>
    <div ref={canvas} className="native-canvas" data-world={activeQuarry ? "quarry" : "market"} data-phase={state.phase}
      data-contact-placement={contact.placement ?? undefined}>
      <Canvas dpr={1} gl={{ antialias: true, powerPreference: "high-performance" }}
        camera={start === "quarry" ? world.camera : { near: 0.05, far: 120 }} fallback={<p>3D is unavailable in this browser.</p>}>
        {activeQuarry ? <Suspense fallback={null}>
          <QuarryArrivalScene runtime={activeQuarry} curtain={curtain} holdCurtain={holdCurtain} />
        </Suspense> : <GateScene runtime={marketRuntime} curtain={curtain} reportZone={setZone}
          form={form} reportContact={setContact} panel={panel} eventPage={eventPage}
          reportWall={setWallUI} chooseEvent={chooseEvent} teamRequest={teamRequest} reportTeam={reportTeam} />}
      </Canvas>
      {walking && runtime.interacting && contact.needsHeading &&
        <h2 className="cypher-contact-fallback-heading">Contact us</h2>}
    </div>
    <div className="native-curtain" ref={curtain} aria-hidden="true" />
    {landing && <div className="native-controls"><button onClick={() => runtime.enter()}>Enter Gullyverse</button></div>}
    {walking && !runtime.interacting && <section className="native-controls gate-controls" aria-label="Walk through the cypher gate">
      <div className="gate-toolbar">
        <p aria-live="polite">{zone}</p>
        {contact.available && !state.map && <button ref={enquiry} onClick={() => {
          if (canOpenContact(marketRuntime.pose) && marketRuntime.focusInteraction(cypherContact.focus)) {
            restoreContactFocus.current = true;
          }
        }}>Leave a message</button>}
        {(wallUI === "events" || wallUI === "team") && <button ref={browse} onClick={() => {
          const focus = wallFocus[wallUI];
          if (canOpenWall(marketRuntime.pose, focus) && marketRuntime.focusInteraction(focus)) {
            setPanel(wallUI);
            restoreWallFocus.current = wallUI;
          }
        }}>{wallUI === "team" ? "View team murals" : "Browse event posters"}</button>}
        <button onClick={() => runtime.setMap(!state.map)}>{state.map ? "Close map" : "Map"}</button>
      </div>
      {!state.map && <>
        <small>WASD or arrows to walk. Drag to look.</small>
        <div className="native-touch" aria-label="Movement controls">
          <button data-move="forward" aria-label="Walk forward">↑</button>
          <div>
            <button data-move="left" aria-label="Walk left">←</button>
            <button data-move="back" aria-label="Walk backward">↓</button>
            <button data-move="right" aria-label="Walk right">→</button>
          </div>
        </div>
      </>}
    </section>}
    <CypherContactDialog host={form} placement={walking && runtime.interacting ? contact.placement : null}
      canSend={canSendContact} onClose={closeContact} />
    {panel === "events" && wallUI === "active" && catalog && eventPage && <CypherEventsDialog
      catalog={catalog} visibleEvents={eventPage} page={page} pages={pages}
      event={eventPage.find(item => item.id === eventId)} changePage={setPage} choose={chooseEvent} close={closeWall} />}
    {panel === "team" && wallUI === "active" && <CypherTeamDialog canvas={canvas} display={teamDisplay}
      advance={advanceTeam} retry={() => requestTeam(current => ({ ...current }))} close={closeWall} />}
    {!walking && !landing && state.phase !== "entrance" && <div className="native-loading" role="status">
      <p>{state.error ?? (state.phase === "context-lost" || state.phase === "recovering"
        ? "Restoring 3D…" : activeQuarry ? "Loading the quarry…" : "Loading the market lane…")}</p>
      {state.error && <><a href="/events">Browse events</a><br /><a href="/get-in-touch">Contact us</a></>}
    </div>}
  </>;
}

export default function CypherGatePreview({ start = "market", team, canSendContact = false, catalog = null }:
  { start?: Start; team?: string; canSendContact?: boolean; catalog?: CypherCatalog | null }) {
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
    <header className="native-header"><a href="/">BREEZE <span>2027</span></a></header>
    {status === "ready" && <CanvasBoundary onFailure={() => setStatus("unavailable")}>
      <GateWalk start={start} team={team} canSendContact={canSendContact} catalog={catalog} />
    </CanvasBoundary>}
    {status === "unavailable" && <div className="native-loading" role="status">
      <p>3D is unavailable in this browser.</p>
      <a href="/events">Browse events</a>
      <br /><a href="/get-in-touch">Contact us</a>
    </div>}
  </div>;
}
