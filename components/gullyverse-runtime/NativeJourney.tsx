"use client";
import React, { useEffect, useRef, useState, useSyncExternalStore } from "react";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import * as THREE from "three";
import { ImmersiveRuntime, type Snapshot } from "../immersive/runtime";
import { useImmersiveInput } from "../immersive/input";
import { phoneCamera, ReadinessGate } from "../immersive/rendering";
import { BakedAssetPool, type BakedAsset } from "./baked-assets";
import { contactSpace } from "./native-space";
import config from "./contact-space.json";
import { mountContactForm } from "./contact-form.js";

const native = contactSpace(config);
const readJSON = async (url: string, signal: AbortSignal) => {
  const response = await fetch(url, { signal });
  if (!response.ok) throw Error(`Could not load the environment (${response.status}).`);
  return response.json();
};
const enquiryPath = () => location.hash === "#contact/enquiry";
class CanvasBoundary extends React.Component<{children:React.ReactNode;onFailure:()=>void},{failed:boolean}>{
  state={failed:false};
  static getDerivedStateFromError(){return{failed:true};}
  componentDidCatch(){this.props.onFailure();}
  render(){return this.state.failed?null:this.props.children;}
}

function NativeView({ runtime, data, base, groundBase, attempt, baseline, curtain, form, onError, onNear, onFocused }: any) {
  const { gl, scene, camera, size } = useThree();
  const [pool] = useState(() => new BakedAssetPool(gl));
  const [assets, setAssets] = useState<BakedAsset[] | null>(null);
  const state = useSyncExternalStore<Snapshot>(runtime.subscribe, runtime.getSnapshot, runtime.getSnapshot);
  const euler = useRef(new THREE.Euler(0, 0, 0, "YXZ"));
  const near = useRef(false), focused = useRef(false);
  useEffect(() => {
    let live = true;
    setAssets(null);
    const lease = pool.acquire(base, innerWidth < 700, data.manifest.bake, baseline);
    const ground = pool.acquire(groundBase, innerWidth < 700, data.ground.bake, baseline);
    Promise.all([lease.promise, ground.promise]).then(a => {
      // The adjoining source-ground chunk replaces the first pilot's thin strip.
      // Both have identical world coordinates; avoid coplanar duplicate faces.
      a[0].scene.traverse(o=>{if(o.name.includes("Rooftop_slab")||o.name.includes("Rooftop slab"))o.visible=false;});
      if (live) setAssets(a);
    }, e => { if (live) onError(String(e)); });
    return () => { live = false; lease.release(); ground.release(); };
  }, [base, groundBase, attempt, baseline, data, pool, onError]);
  useEffect(() => {
    gl.toneMapping = THREE.AgXToneMapping; gl.toneMappingExposure = Math.pow(2, 0.25);
    scene.background = new THREE.Color("#010303");
    const lost = (event: Event) => { event.preventDefault(); runtime.loseContext(); };
    const restored = () => runtime.restoreContext();
    gl.domElement.addEventListener("webglcontextlost", lost);
    gl.domElement.addEventListener("webglcontextrestored", restored);
    return () => { gl.domElement.removeEventListener("webglcontextlost", lost); gl.domElement.removeEventListener("webglcontextrestored", restored); };
  }, [gl, scene, runtime]);
  useEffect(() => {
    (window as any).__nativeJourney = {
      stats: () => ({ phase: runtime.getSnapshot().phase, pose: { ...runtime.pose }, near: native.near(runtime.pose), interacting: runtime.interacting, focusing: runtime.focusing,
        map: runtime.getSnapshot().map, suspended: runtime.suspended, activeFrameDelta: runtime.activeFrameDelta, preparedSerial: runtime.preparedSerial, clearance: native.clearance(runtime.pose), canvasCount: document.querySelectorAll("canvas").length,
        gpu: { ...gl.info.memory }, drawCalls: gl.info.render.calls, triangles: gl.info.render.triangles, assetLeases: pool.size,
        glError: gl.getContext().getError(), floor: config.floor, eyeHeight: config.eyeHeight,
        floorHit: new THREE.Raycaster(new THREE.Vector3(runtime.pose.x,config.floor+1,runtime.pose.z),new THREE.Vector3(0,-1,0),0,2).intersectObjects(scene.children,true).find(hit=>hit.face && hit.face.normal.clone().transformDirection(hit.object.matrixWorld).y>.5)?.point.y ?? null }),
    };
    return () => { delete (window as any).__nativeJourney; };
  }, [gl, scene, runtime, pool]);
  useEffect(()=>{if(state.error)onError(state.error);},[state.error,onError]);
  useFrame((_, delta) => {
    runtime.tick(delta);
    const view = runtime.cameraPose(size.width / size.height, !runtime.interacting && phoneCamera(size.width));
    camera.position.set(view.x, view.y, view.z);
    euler.current.set(view.pitch, view.yaw, 0, "YXZ"); camera.quaternion.setFromEuler(euler.current);
    if (camera instanceof THREE.PerspectiveCamera && camera.fov !== view.fov) { camera.fov = view.fov; camera.updateProjectionMatrix(); }
    if (curtain.current) curtain.current.style.opacity = String(runtime.revealOpacity);
    const isNear = native.near(runtime.pose);
    if (near.current !== isNear) { near.current = isNear; onNear(isNear); }
    const target = native.focus();
    const isFocused = runtime.interacting && Math.hypot(runtime.pose.x - target.x, runtime.pose.z - target.z) < 0.01;
    if (focused.current !== isFocused) { focused.current = isFocused; onFocused(isFocused); }
    if (!form.current || !isFocused || innerWidth < 700) return;
    const c = data.contact, n = c.normal, t = c.tangent;
    const projected = (u: number, z: number) => new THREE.Vector3(t[0] * u + n[0] * c.messageDepth, z, -(t[1] * u + n[1] * c.messageDepth)).project(camera);
    const a = projected(c.messageBoundsU[0], c.messageBoundsZ[1]), b = projected(c.messageBoundsU[1], c.messageBoundsZ[0]);
    Object.assign(form.current.style, { left: `${(a.x + 1) * size.width / 2}px`, top: `${(1 - a.y) * size.height / 2}px`,
      width: `${(b.x - a.x) * size.width / 2}px`, height: `${(a.y - b.y) * size.height / 2}px` });
  }, -1);
  return assets ? <>{assets.map((asset,i)=><primitive key={i} object={asset.scene}/>)}<ReadinessGate key={state.serial + ":" + attempt + ":" + baseline} runtime={runtime} serial={state.serial} /></> : null;
}

/** One Canvas and the original controller; this subphase covers the real Contact approach. */
export default function NativeJourney({ assetBase = "assets/", groundBase = "ground/" }: { assetBase?: string; groundBase?: string }) {
  const [webglAvailable]=useState(()=>{
    try{
      const probe=document.createElement("canvas"),context=probe.getContext("webgl2");
      if(!context)return false;
      context.getExtension("WEBGL_lose_context")?.loseContext();
      return true;
    }catch{return false;}
  });
  const [runtime] = useState(() => new ImmersiveRuntime("hub", undefined, false, () => performance.now() / 1000, native.space));
  const state = useSyncExternalStore(runtime.subscribe, runtime.getSnapshot, runtime.getSnapshot);
  const [data, setData] = useState<any>(null), [error, setError] = useState("");
  const [near, setNear] = useState(false), [focused, setFocused] = useState(false), [attempt, setAttempt] = useState(0), [baseline, setBaseline] = useState(false);
  const [flat, setFlat] = useState(!webglAvailable), [backend, setBackend] = useState(false);
  const backendRef=useRef(false);backendRef.current=backend;
  const curtain = useRef<HTMLDivElement>(null), form = useRef<HTMLDivElement>(null), openButton = useRef<HTMLButtonElement>(null);
  const formAPI = useRef<ReturnType<typeof mountContactForm> | null>(null);
  const hashPending = useRef(enquiryPath()), initialHashHandled = useRef(false);
  useImmersiveInput(runtime);
  const closeRef = useRef(() => {});
  const accessButton=useRef<HTMLButtonElement>(null);
  closeRef.current = () => {
    if(flat)setFlat(false);
    if (!runtime.interacting) return;
    runtime.focusInteraction(null);
    if (location.hash === "#contact/enquiry") history.pushState({}, "", "#contact/approach");
    requestAnimationFrame(() => openButton.current?.focus());
  };
  useEffect(() => {
    const abort = new AbortController();
    void Promise.all([readJSON(assetBase + "manifest.json", abort.signal), readJSON(assetBase + "contact.json", abort.signal), readJSON(groundBase + "manifest.json", abort.signal)])
      .then(([manifest, contact, ground]) => {
        if (manifest.source.sha256 !== config.sourceSHA256 || ground.source.sha256 !== config.sourceSHA256) throw Error("The environment version does not match its navigation data.");
        setData({ manifest, contact, ground });
      }).catch(e => { if (!abort.signal.aborted) setError(String(e)); });
    void fetch("/api/preview-health", { signal: abort.signal }).then(r => r.ok ? r.json() : null).then(value => { if (!abort.signal.aborted) setBackend(value?.isolated === true); }).catch(() => {});
    return () => abort.abort();
  }, [assetBase, groundBase, attempt]);
  useEffect(() => {
    const applyHash = () => {
      hashPending.current = enquiryPath();
      if (!hashPending.current && runtime.interacting) runtime.focusInteraction(null);
      else if (hashPending.current && runtime.getSnapshot().phase === "local" && !runtime.interacting) runtime.focusInteraction(native.focus());
    };
    window.addEventListener("hashchange", applyHash); window.addEventListener("popstate", applyHash);
    return () => { window.removeEventListener("hashchange", applyHash); window.removeEventListener("popstate", applyHash); };
  }, [runtime]);
  useEffect(() => {
    if (state.phase === "local" && !initialHashHandled.current) {
      initialHashHandled.current = true;
      if (hashPending.current) runtime.focusInteraction(native.focus());
      else if (!location.hash) history.replaceState({}, "", "#contact/approach");
    }
  }, [state.phase, runtime]);
  useEffect(() => {
    if (!form.current) return;
    const api = mountContactForm(form.current, {
      submit: async fields => {
        if (!backendRef.current) throw Error("The private test backend is unavailable. Your message is still here.");
        const response = await fetch("/api/contact", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(fields) });
        const body = await response.json().catch(() => ({}));
        if (!response.ok || body.success !== true) throw Error("Your message could not be saved. Please try again.");
        return body;
      }, onClose: () => closeRef.current(),
    });
    formAPI.current = api;
    return () => { formAPI.current = null; api.dispose(); };
  }, []);
  useEffect(() => {
    if (!focused && !flat) return;
    const previouslyFocused = document.activeElement;
    formAPI.current?.focus();
    const key = (e: KeyboardEvent) => {
      if (e.key === "Escape") { e.preventDefault(); e.stopPropagation(); if (flat) setFlat(false); else closeRef.current(); }
      if (e.key === "Tab" && form.current) {
        const nodes = [...form.current.querySelectorAll<HTMLElement>("input,textarea,button:not(:disabled)")];
        if (e.shiftKey && document.activeElement === nodes[0]) { e.preventDefault(); nodes.at(-1)?.focus(); }
        else if (!e.shiftKey && document.activeElement === nodes.at(-1)) { e.preventDefault(); nodes[0]?.focus(); }
      }
    };
    document.addEventListener("keydown", key);
    if (document.pointerLockElement) void document.exitPointerLock();
    return () => { document.removeEventListener("keydown", key); if (previouslyFocused instanceof HTMLElement && previouslyFocused.isConnected) previouslyFocused.focus(); };
  }, [focused, flat]);
  const wasInteracting=useRef(false);
  useEffect(()=>{
    const closed=wasInteracting.current&&!runtime.interacting;wasInteracting.current=runtime.interacting;
    if(!closed)return;
    let frame=0,live=true;
    const restore=()=>{
      if(!live)return;
      const target=native.near(runtime.pose)?openButton.current:accessButton.current;
      if(runtime.focusing||!target||target.disabled){frame=requestAnimationFrame(restore);return;}
      target.focus();
    };
    frame=requestAnimationFrame(restore);
    return()=>{live=false;cancelAnimationFrame(frame);};
  },[state,runtime]);
  useEffect(() => {
    // Escape can originate on the Canvas through the original input service.
    if (!runtime.interacting && location.hash === "#contact/enquiry" && initialHashHandled.current) history.replaceState({}, "", "#contact/approach");
  }, [state, runtime]);
  const open = () => {
    if (!near || !runtime.focusInteraction(native.focus())) return;
    history.pushState({}, "", "#contact/enquiry");
  };
  const showForm = focused || flat;
  useEffect(() => { runtime.suspended = flat || document.hidden; runtime.clearInput(); return () => { runtime.suspended = document.hidden; }; }, [flat, runtime]);
  return <div className="native-journey">
    <div className="native-canvas">{webglAvailable&&<CanvasBoundary onFailure={()=>setFlat(true)}><Canvas fallback={<span>Use without 3D to continue.</span>} dpr={1} gl={{ antialias: true, powerPreference: "high-performance" }} camera={{ fov: 35.6, near: 0.05, far: 120 }}>
      {data && <NativeView runtime={runtime} data={data} base={assetBase} groundBase={groundBase} attempt={attempt} baseline={baseline} curtain={curtain} form={form} onError={setError} onNear={setNear} onFocused={setFocused} />}
    </Canvas></CanvasBoundary>}</div>
    <div ref={curtain} className="native-curtain" aria-hidden="true" />
    <header className="native-header"><a href="#contact/approach" onClick={e => { if (runtime.interacting) { e.preventDefault(); closeRef.current(); } }}>BREEZE <span>2027</span></a><span>Contact us</span></header>
    <div className="native-form" ref={form} hidden={!showForm} role="dialog" aria-modal="true" aria-label="Contact enquiry" data-flat={flat} />
    {state.phase === "local" && !runtime.interacting && !flat && <section className="native-controls" aria-label="Explore Contact us">
      <p>{near ? "You’re at the enquiry window." : "Walk towards the enquiry window."}</p>
      <div><button ref={openButton} onClick={open} disabled={!near}>Leave a message</button><button onClick={() => runtime.setMap(!state.map)}>{state.map ? "Close map" : "Map"}</button></div>
      {!state.map && <><small>WASD / arrows to walk · drag to look</small><div className="native-touch" aria-label="Movement controls"><button data-move="forward" aria-label="Walk forward">↑</button><div><button data-move="left" aria-label="Walk left">←</button><button data-move="back" aria-label="Walk backward">↓</button><button data-move="right" aria-label="Walk right">→</button></div></div></>}
    </section>}
    <div className="native-access"><button ref={accessButton} onClick={() => { runtime.clearInput(); setFlat(!flat); }}>{flat ? "Return to 3D" : "Use without 3D"}</button><details onToggle={() => runtime.clearInput()}><summary>Festival information</summary><nav>{[["Events","/events"],["Team","/team"],["Main Stage / Aftermovie","/aftermovie"],["Contact us","/get-in-touch"]].map(([label,href])=><a key={href} href={href}>{label}</a>)}</nav></details></div>
    {showForm && <p className="native-test-note">{backend ? "Private test mode · saved only in the isolated test database" : "Private preview · sending is unavailable"}</p>}
    {!flat&&(error || !["local", "arrival"].includes(state.phase)) && <div className="native-loading" role="status"><p>{error || "Preparing your view…"}</p>{error && <button onClick={() => { setError(""); runtime.retryFromError(); setBaseline(true); setAttempt(x => x + 1); }}>Retry with compatible textures</button>}</div>}
  </div>;
}
