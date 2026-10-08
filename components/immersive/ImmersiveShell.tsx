"use client";
import React, { Component, lazy, Suspense, useEffect, useRef, useState, useSyncExternalStore } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Canvas } from "@react-three/fiber";
import HubScene from "./HubScene";
import { FrameController, SceneRenderer, QUALITY_DPR } from "./rendering";
import { ImmersiveRuntime } from "./runtime";
import { locationFromPath, locations, mapLabels } from "./navigation";
import { useImmersiveInput } from "./input";
import styles from "./immersive.module.css";

const AftermovieScene = lazy(() => import("./AftermovieScene"));
const infoLinks = [["Events", "/events"], ["Team", "/team"], ["Contact us", "/get-in-touch"], ["Past sponsors", "/sponsors"], ["Merch", "/merch"]];

function InformationLinks() {
  return <nav aria-label="Festival information" className={styles.infoLinks}>{infoLinks.map(([label, href]) => <Link key={href} href={href}>{label}</Link>)}</nav>;
}
function Fallback({ error }: { error?: string }) {
  return <section className={styles.fallback} aria-label="Festival without 3D">
    <p>BREEZE 2027 / GULLYVERSE</p><h1>The festival is still here.</h1>
    <p>{error ? "The immersive view could not load. You can watch the Aftermovie and access festival information here." : "Watch the Aftermovie and explore festival information."}</p>
    <video controls playsInline preload="none" src="/after-movie.mp4" aria-label="Breeze Aftermovie" />
    <InformationLinks /><button onClick={() => window.location.reload()}>Reload immersive experience</button>
  </section>;
}
class SceneBoundary extends Component<{ children: React.ReactNode; onError: (message: string) => void }, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() { return { failed: true }; }
  componentDidCatch(error: Error) { this.props.onError(error.message); }
  render() { return this.state.failed ? null : this.props.children; }
}

function FestivalMap({ runtime }: { runtime: ImmersiveRuntime }) {
  const dialog = useRef<HTMLDialogElement>(null);
  useEffect(() => {
    const previous = document.activeElement as HTMLElement | null;
    const node = dialog.current;
    node?.showModal();
    return () => { node?.close(); previous?.focus(); };
  }, []);
  return <dialog ref={dialog} className={styles.map} aria-labelledby="map-title" onCancel={() => runtime.setMap(false)}>
    <div className={styles.mapHeader}><h2 id="map-title">Find your way</h2><button onClick={() => runtime.setMap(false)} aria-label="Close map">×</button></div>
    <p>One festival. Follow the music.</p>
    <div className={styles.mapDrawing} aria-hidden="true"><span className={styles.mapTunnel}>Entrance</span><span className={styles.mapHub}>Gullyverse</span><span className={styles.mapStage}>Aftermovie</span><i /></div>
    <button className={styles.destination} onClick={() => { runtime.request("hub", "map"); runtime.setMap(false); }}>Gullyverse hub</button>
    {mapLabels.map((label) => <button key={label} className={styles.destination} disabled={label !== "Aftermovie"} onClick={() => { runtime.request("aftermovie", "map"); runtime.setMap(false); }}>
      <span>{label}</span><small>{label === "Aftermovie" ? "Travel →" : "Coming soon"}</small>
    </button>)}
  </dialog>;
}

export default function ImmersiveShell() {
  const pathname = usePathname();
  const [runtime] = useState(() => new ImmersiveRuntime(locationFromPath(pathname) ?? "hub", (id, source) => {
    // Next's supported native history integration updates usePathname without
    // fetching/remounting a second renderer. Popstate enters the same request path.
    if (source !== "url" && locationFromPath(window.location.pathname) !== id) {
      const query = new URLSearchParams(window.location.search);
      window.history.pushState(null, "", locations[id].href + (query.has("diagnostics") ? "?diagnostics" : ""));
    }
  }));
  const state = useSyncExternalStore(runtime.subscribe, runtime.getSnapshot, runtime.getSnapshot);
  const curtain = useRef<HTMLDivElement>(null);
  const [flat, setFlat] = useState(false);
  useImmersiveInput(runtime);
  useEffect(() => {
    const destination = locationFromPath(pathname);
    if (destination && destination !== runtime.getSnapshot().destination) runtime.request(destination, "url");
  }, [pathname, runtime]);
  useEffect(() => {
    // Native popstate can supersede an in-flight journey even before Next rerenders.
    const onPop = () => { const id = locationFromPath(window.location.pathname); if (id) runtime.request(id, "url"); };
    window.addEventListener("popstate", onPop);
    return () => window.removeEventListener("popstate", onPop);
  }, [runtime]);
  useEffect(() => {
    if (!["boot", "covered", "context-lost", "recovering"].includes(state.phase)) return;
    // A timeout never reveals unfinished content; it offers the 2D fallback.
    const timer = setTimeout(() => runtime.fail("Critical scene preparation exceeded 45 seconds."), 45000);
    return () => clearTimeout(timer);
  }, [state.phase, state.serial, runtime]);
  useEffect(() => {
    if (window.matchMedia("(pointer: coarse)").matches) runtime.setQuality(1);
  }, [runtime]);
  const local = state.phase === "local";
  if (flat || state.phase === "error") return <div className={styles.shell} data-phase={state.phase}><Fallback error={state.error ?? undefined} /></div>;
  return <section className={styles.shell} data-phase={state.phase} data-location={state.scene} aria-label="Gullyverse immersive experience">
    <SceneBoundary onError={(message) => runtime.fail(message)}>
      <Canvas dpr={Math.min(window.devicePixelRatio, QUALITY_DPR[state.quality])} camera={{ fov: 58, near: 0.1, far: 250, position: [0, 1.72, 8] }} gl={{ antialias: false, powerPreference: "high-performance" }} fallback={<Fallback error="WebGL2 unavailable" />}>
        <FrameController runtime={runtime} curtain={curtain} />
        <SceneRenderer runtime={runtime} />
        <Suspense fallback={null}>
          {state.scene === "hub" ? <HubScene runtime={runtime} serial={state.serial} quality={state.quality} /> : <AftermovieScene runtime={runtime} serial={state.serial} quality={state.quality} />}
        </Suspense>
      </Canvas>
    </SceneBoundary>
    <div ref={curtain} className={styles.curtain} style={{ opacity: 1 }} aria-hidden="true"><div className={styles.occluder} /></div>
    <header className={styles.header}><Link href="/" onClick={(e) => { if (!e.ctrlKey && !e.metaKey && !e.shiftKey && !e.altKey) { e.preventDefault(); if (state.phase === "landing") return; runtime.request("hub", "map"); } }}>BREEZE <span>2027</span></Link><span>GULLYVERSE</span></header>
    {state.phase === "landing" && <div className={styles.landing}><p>FOLLOW THE MUSIC</p><h1>A world<br />beyond the walls.</h1><button onClick={() => runtime.enter()}>Enter Gullyverse <span>→</span></button><small>Click, tap, or press Enter</small></div>}
    <p className={styles.status} role="status" aria-live="polite">{["context-lost", "recovering"].includes(state.phase) ? "Restoring your view…" : state.phase === "boot" ? "Preparing your view…" : state.phase === "covered" ? `On the way to ${locations[state.destination].label}…` : state.phase === "entrance" ? "Welcome to Gullyverse" : local ? locations[state.scene].label : "Follow the music"}</p>
    {local && <div className={styles.controls}>
      <p>{state.movie ? "Esc exits the Aftermovie" : state.scene === "hub" ? "WASD / arrows to walk · drag to look · follow AFTERMOVIE" : "WASD / arrows to walk · return path behind you"}</p>
      <div className={styles.actions}>
        <button onClick={() => runtime.setMap(true)} disabled={state.movie}>Map <kbd>M</kbd></button>
        {state.scene === "aftermovie" && <>
          <button onClick={() => state.movie ? runtime.movieActions?.stop() : runtime.movieActions?.play()}>{state.movie ? "Exit Aftermovie" : "Play Aftermovie"}</button>
          {state.movie && <button onClick={() => runtime.movieActions?.sound()}>Enable sound</button>}
        </>}
      </div>
      {!state.movie && <div className={styles.touchPad} aria-label="Movement controls"><button data-move="forward" aria-label="Walk forward">↑</button><div><button data-move="left" aria-label="Walk left">←</button><button data-move="back" aria-label="Walk backward">↓</button><button data-move="right" aria-label="Walk right">→</button></div><small>Drag the scene to look</small></div>}
    </div>}
    <div className={styles.access}><button onClick={() => { runtime.movieActions?.stop(); runtime.clearInput(); setFlat(true); }}>Use without 3D</button><details onToggle={(e) => { if (e.currentTarget.open) runtime.clearInput(); }}><summary>Festival information</summary><InformationLinks /></details></div>
    {state.map && <FestivalMap runtime={runtime} />}
  </section>;
}
